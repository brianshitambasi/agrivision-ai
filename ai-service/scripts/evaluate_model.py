"""
Evaluate the AgriVision AI model on the independent test set.

This script:
- Loads the EXACT checkpoint used by FastAPI
- Runs inference on all test images
- Reports accuracy, precision, recall, F1, confusion matrix
- Does NOT fabricate any numbers
"""
import sys
import json
from pathlib import Path
from collections import defaultdict

import torch
import torch.nn as nn
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
import numpy as np


# ============ CONFIG ============
CHECKPOINT_PATH = Path(__file__).parent.parent / "app/models/saved/agrivision_v1.pth"
TEST_DIR = Path(__file__).parent.parent.parent / "datasets/processed/test"
DEVICE = torch.device("cpu")
BATCH_SIZE = 64


# ============ TRANSFORMS (must match training) ============
test_tf = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])


def load_model():
    """Load checkpoint and rebuild ResNet18."""
    if not CHECKPOINT_PATH.exists():
        print(f"❌ Checkpoint not found: {CHECKPOINT_PATH}")
        sys.exit(1)

    ckpt = torch.load(CHECKPOINT_PATH, map_location=DEVICE, weights_only=False)
    num_classes = ckpt["num_classes"]
    classes = ckpt["classes"]
    arch = ckpt["arch"]

    print(f"📦 Checkpoint: {CHECKPOINT_PATH.name}")
    print(f"   Architecture: {arch}")
    print(f"   Classes: {num_classes}")
    print(f"   Saved val_acc: {ckpt.get('val_acc', 0):.4f}")
    print()

    if arch == "resnet18":
        model = models.resnet18(weights=None)
        model.fc = nn.Linear(model.fc.in_features, num_classes)
    else:
        print(f"❌ Unsupported architecture: {arch}")
        sys.exit(1)

    model.load_state_dict(ckpt["model_state_dict"])
    model.eval().to(DEVICE)
    return model, classes


def evaluate():
    """Run full evaluation on test set."""
    print("=" * 70)
    print("AgriVision AI — Model Evaluation")
    print("=" * 70)
    print()

    if not TEST_DIR.exists():
        print(f"❌ No independent test set at {TEST_DIR}")
        print("   Cannot report test accuracy.")
        sys.exit(1)

    model, classes = load_model()

    # Load test set
    test_ds = datasets.ImageFolder(TEST_DIR, transform=test_tf)
    test_loader = DataLoader(test_ds, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    # Verify class order matches
    if test_ds.classes != classes:
        print("⚠️  WARNING: Test set class order differs from checkpoint!")
        print(f"   Checkpoint: {classes[:3]}...")
        print(f"   Test set:   {test_ds.classes[:3]}...")
        print("   Using checkpoint class order.")
        print()

    print(f"📊 Test set: {len(test_ds)} images")
    print(f"   Classes: {len(classes)}")
    print(f"   Class distribution:")
    for cls, count in zip(test_ds.classes, np.bincount(test_ds.targets)):
        print(f"     {cls:50s} {count:5d}")
    print()

    # Run inference
    print("🔍 Running inference...")
    all_preds = []
    all_labels = []
    all_confs = []

    with torch.no_grad():
        for imgs, labels in test_loader:
            imgs = imgs.to(DEVICE)
            outputs = model(imgs)
            probs = torch.softmax(outputs, dim=1)
            confs, preds = probs.max(dim=1)

            all_preds.extend(preds.cpu().tolist())
            all_labels.extend(labels.tolist())
            all_confs.extend(confs.cpu().tolist())

    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)
    all_confs = np.array(all_confs)

    # Overall accuracy
    correct = (all_preds == all_labels).sum()
    total = len(all_labels)
    accuracy = correct / total

    print()
    print("=" * 70)
    print("📈 OVERALL METRICS (on independent test set)")
    print("=" * 70)
    print(f"Total images:     {total}")
    print(f"Correct:          {correct}")
    print(f"Incorrect:        {total - correct}")
    print(f"Accuracy:         {accuracy*100:.2f}%")
    print(f"Mean confidence:  {all_confs.mean()*100:.2f}%")
    print()

    # Per-class metrics
    print("=" * 70)
    print("📊 PER-CLASS METRICS")
    print("=" * 70)
    print(f"{'Class':<45} {'Prec':>8} {'Rec':>8} {'F1':>8} {'Support':>8}")
    print("-" * 70)

    per_class_stats = {}
    for i, cls in enumerate(classes):
        tp = ((all_preds == i) & (all_labels == i)).sum()
        fp = ((all_preds == i) & (all_labels != i)).sum()
        fn = ((all_preds != i) & (all_labels == i)).sum()
        support = (all_labels == i).sum()

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        per_class_stats[cls] = {
            "precision": round(float(precision), 4),
            "recall": round(float(recall), 4),
            "f1": round(float(f1), 4),
            "support": int(support),
            "correct": int(tp),
            "incorrect": int(fn),
        }

        print(f"{cls:<45} {precision:>8.3f} {recall:>8.3f} {f1:>8.3f} {support:>8d}")

    # Macro averages
    macro_prec = np.mean([s["precision"] for s in per_class_stats.values()])
    macro_rec = np.mean([s["recall"] for s in per_class_stats.values()])
    macro_f1 = np.mean([s["f1"] for s in per_class_stats.values()])

    print("-" * 70)
    print(f"{'MACRO AVERAGE':<45} {macro_prec:>8.3f} {macro_rec:>8.3f} {macro_f1:>8.3f}")
    print()

    # Confusion matrix
    print("=" * 70)
    print("🔢 CONFUSION MATRIX (rows = true, cols = predicted)")
    print("=" * 70)

    num_classes = len(classes)
    cm = np.zeros((num_classes, num_classes), dtype=int)
    for true, pred in zip(all_labels, all_preds):
        cm[true, pred] += 1

    # Short labels for matrix
    short = [c.split("_")[0][:3] + "_" + c.split("_")[-1][:6] for c in classes]
    header = "        " + "".join(f"{s:>10s}" for s in short)
    print(header)
    for i, cls in enumerate(classes):
        row = f"{short[i]:<8s}"
        for j in range(num_classes):
            row += f"{cm[i][j]:>10d}"
        print(row)

    # Top misclassifications
    print()
    print("=" * 70)
    print("❌ TOP 10 MISCLASSIFICATIONS (true → predicted)")
    print("=" * 70)
    misclass = []
    for i in range(num_classes):
        for j in range(num_classes):
            if i != j and cm[i][j] > 0:
                misclass.append((cm[i][j], classes[i], classes[j]))
    misclass.sort(reverse=True)

    for count, true_cls, pred_cls in misclass[:10]:
        print(f"  {count:4d} × {true_cls:<42s} → {pred_cls}")

    # Low-confidence analysis
    print()
    print("=" * 70)
    print("⚠️  CONFIDENCE ANALYSIS")
    print("=" * 70)
    for threshold in [0.5, 0.6, 0.7, 0.8, 0.9]:
        below = (all_confs < threshold).sum()
        acc_below = (all_preds[all_confs < threshold] == all_labels[all_confs < threshold]).mean() if below > 0 else 0.0
        acc_above = (all_preds[all_confs >= threshold] == all_labels[all_confs >= threshold]).mean() if (total - below) > 0 else 0.0
        print(f"  Threshold {threshold:.2f}: {below:5d} below ({below/total*100:5.1f}%) | "
              f"Acc when below: {acc_below*100:5.1f}% | Acc when above: {acc_above*100:5.1f}%")
    print()

    # Save results
    results = {
        "checkpoint": str(CHECKPOINT_PATH),
        "test_set": str(TEST_DIR),
        "total_images": int(total),
        "correct": int(correct),
        "accuracy": round(float(accuracy), 4),
        "macro_precision": round(float(macro_prec), 4),
        "macro_recall": round(float(macro_rec), 4),
        "macro_f1": round(float(macro_f1), 4),
        "per_class": per_class_stats,
        "confusion_matrix": cm.tolist(),
        "classes": classes,
    }

    output_path = Path(__file__).parent.parent / "app/models/saved/test_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"💾 Results saved to: {output_path}")
    print()
    print("=" * 70)
    print(f"✅ DONE — Test accuracy: {accuracy*100:.2f}%")
    print("=" * 70)


if __name__ == "__main__":
    evaluate()
