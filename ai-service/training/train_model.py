import json
import time
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
from pathlib import Path

# ============ CONFIG ============
DATA_DIR = Path("../../datasets/processed")
MODEL_SAVE_PATH = Path("../app/models/saved/agrivision_v1.pth")
CLASSES_SAVE_PATH = Path("../app/models/saved/classes.json")
HISTORY_SAVE_PATH = Path("../app/models/saved/training_history.json")

BATCH_SIZE = 32
EPOCHS = 10
LR = 0.001
DEVICE = torch.device("cpu")

print(f"Device: {DEVICE}")
print(f"Torch: {torch.__version__}")
print()

# ============ TRANSFORMS ============
train_tf = transforms.Compose([
    transforms.Resize(256),
    transforms.RandomResizedCrop(224),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
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

train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

NUM_CLASSES = len(train_ds.classes)
print(f"Classes: {NUM_CLASSES}")
print(f"Train: {len(train_ds)} | Val: {len(val_ds)}")
print()

# Save classes list
MODEL_SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(CLASSES_SAVE_PATH, "w") as f:
    json.dump(train_ds.classes, f, indent=2)

# ============ MODEL ============
print("Building ResNet18 model...")
model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
for param in model.parameters():
    param.requires_grad = False

model.fc = nn.Linear(model.fc.in_features, NUM_CLASSES)
model = model.to(DEVICE)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.fc.parameters(), lr=LR)
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.5)

total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"Trainable params: {total_params:,}")
print()

# ============ TRAINING LOOP ============
best_acc = 0.0
history = {"train_loss": [], "val_loss": [], "val_acc": []}
start_time = time.time()

print("=" * 70)
print("STARTING TRAINING")
print("=" * 70)

for epoch in range(EPOCHS):
    epoch_start = time.time()

    # --- Train ---
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

    # --- Validate ---
    model.eval()
    val_loss = 0.0
    correct, total = 0, 0
    with torch.no_grad():
        for imgs, labels in val_loader:
            imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
            outputs = model(imgs)
            loss = criterion(outputs, labels)
            val_loss += loss.item()
            _, preds = outputs.max(1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

    val_loss /= len(val_loader)
    val_acc = correct / total
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
        torch.save({
            "model_state_dict": model.state_dict(),
            "num_classes": NUM_CLASSES,
            "classes": train_ds.classes,
            "arch": "resnet18",
            "img_size": 224,
            "val_acc": val_acc,
        }, MODEL_SAVE_PATH)
        print(f"            Saved best model (val_acc={val_acc*100:.2f}%)")

# Save history
with open(HISTORY_SAVE_PATH, "w") as f:
    json.dump(history, f, indent=2)

total_time = time.time() - start_time
print()
print("=" * 70)
print(f"TRAINING COMPLETE in {total_time/60:.1f} minutes")
print(f"Best val accuracy: {best_acc*100:.2f}%")
print(f"Model saved to: {MODEL_SAVE_PATH}")
print("=" * 70)
