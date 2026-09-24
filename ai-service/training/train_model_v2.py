"""
AgriVision AI — Improved Training (v2)

Improvements over v1:
- Unfreeze layer4 + fc (was only fc)
- Differential learning rates
- Class weighting for imbalanced classes
- 20 epochs (was 10)
- Stronger augmentation (RandomErasing)
- Cosine annealing scheduler
- Saves best model by test-set accuracy pattern
"""
import json
import time
import copy
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader, WeightedRandomSampler
import numpy as np


# ============ CONFIG ============
DATA_DIR = Path("../../datasets/processed")
MODEL_SAVE_PATH = Path("../app/models/saved/agrivision_v2.pth")
CLASSES_SAVE_PATH = Path("../app/models/saved/classes.json")
HISTORY_SAVE_PATH = Path("../app/models/saved/training_history_v2.json")

BATCH_SIZE = 32
EPOCHS = 20
LR_FC = 0.001          # head learns fast
LR_BACKBONE = 0.0001   # pretrained layers learn slowly
DEVICE = torch.device("cpu")

print(f"Device: {DEVICE}")
print(f"Torch: {torch.__version__}")
print()


# ============ TRANSFORMS ============
train_tf = transforms.Compose([
    transforms.Resize(256),
    transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(20),
    transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.05),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    transforms.RandomErasing(p=0.25, scale=(0.02, 0.1)),
])

val_tf = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])


# ============ DATA ============
print("Loading datasets...")
train_ds = datasets.ImageFolder(DATA_DIR / "train", transform=train_tf)
val_ds = datasets.ImageFolder(DATA_DIR / "val", transform=val_tf)

# Compute class weights for imbalanced data
class_counts = np.bincount(train_ds.targets)
class_weights = 1.0 / (class_counts + 1e-6)
class_weights = class_weights / class_weights.sum() * len(class_counts)
class_weights = torch.FloatTensor(class_weights).to(DEVICE)

print(f"Classes: {len(train_ds.classes)}")
print(f"Train: {len(train_ds)} | Val: {len(val_ds)}")
print(f"Class counts: min={class_counts.min()}, max={class_counts.max()}")
print()

# Weighted sampler for balanced batches
sample_weights = [class_weights[t].item() for t in train_ds.targets]
sampler = WeightedRandomSampler(sample_weights, len(sample_weights), replacement=True)

train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, sampler=sampler, num_workers=0)
val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

NUM_CLASSES = len(train_ds.classes)

# Save classes list
MODEL_SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(CLASSES_SAVE_PATH, "w") as f:
    json.dump(train_ds.classes, f, indent=2)


# ============ MODEL ============
print("Building ResNet18 (unfreezing layer4)...")
model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)

# Freeze early layers (conv1 through layer3)
for name, param in model.named_parameters():
    if name.startswith("layer4") or name.startswith("fc"):
        param.requires_grad = True
    else:
        param.requires_grad = False

model.fc = nn.Linear(model.fc.in_features, NUM_CLASSES)
model = model.to(DEVICE)

trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
total = sum(p.numel() for p in model.parameters())
print(f"Trainable params: {trainable:,} / {total:,} ({trainable/total*100:.1f}%)")
print()


# ============ OPTIMIZER + LOSS ============
fc_params = list(model.fc.parameters())
backbone_params = [p for n, p in model.named_parameters() if p.requires_grad and not n.startswith("fc")]

optimizer = optim.AdamW([
    {"params": fc_params, "lr": LR_FC},
    {"params": backbone_params, "lr": LR_BACKBONE},
], weight_decay=1e-4)

scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)
criterion = nn.CrossEntropyLoss(weight=class_weights)


# ============ TRAINING ============
best_acc = 0.0
best_state = None
history = {"train_loss": [], "val_loss": [], "val_acc": []}
start_time = time.time()

print("=" * 70)
print("STARTING TRAINING (v2 — improved)")
print("=" * 70)

for epoch in range(EPOCHS):
    epoch_start = time.time()

    # ---- Train ----
    model.train()
    train_loss = 0.0
    for imgs, labels in train_loader:
        imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
        optimizer.zero_grad()
        outputs = model(imgs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        train_loss += loss.item()
    train_loss /= len(train_loader)

    # ---- Validate ----
    model.eval()
    val_loss = 0.0
    correct, total_count = 0, 0
    with torch.no_grad():
        for imgs, labels in val_loader:
            imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
            outputs = model(imgs)
            loss = criterion(outputs, labels)
            val_loss += loss.item()
            _, preds = outputs.max(1)
            correct += (preds == labels).sum().item()
            total_count += labels.size(0)

    val_loss /= len(val_loader)
    val_acc = correct / total_count

    scheduler.step()

    history["train_loss"].append(train_loss)
    history["val_loss"].append(val_loss)
    history["val_acc"].append(val_acc)

    epoch_time = time.time() - epoch_start
    print(f"Epoch {epoch+1:2d}/{EPOCHS} | "
          f"Train Loss: {train_loss:.4f} | "
          f"Val Loss: {val_loss:.4f} | "
          f"Val Acc: {val_acc*100:5.2f}% | "
          f"Time: {epoch_time:5.1f}s")

    if val_acc > best_acc:
        best_acc = val_acc
        best_state = copy.deepcopy(model.state_dict())
        torch.save({
            "model_state_dict": model.state_dict(),
            "num_classes": NUM_CLASSES,
            "classes": train_ds.classes,
            "arch": "resnet18",
            "img_size": 224,
            "val_acc": val_acc,
            "version": "v2",
        }, MODEL_SAVE_PATH)
        print(f"            💾 Saved best model (val_acc={val_acc*100:.2f}%)")

# Save history
with open(HISTORY_SAVE_PATH, "w") as f:
    json.dump(history, f, indent=2)

total_time = time.time() - start_time
print()
print("=" * 70)
print(f"TRAINING COMPLETE in {total_time/60:.1f} minutes")
print(f"Best val accuracy: {best_acc*100:.2f}%")
print(f"Model saved: {MODEL_SAVE_PATH}")
print("=" * 70)
