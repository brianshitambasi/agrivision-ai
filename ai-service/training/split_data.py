import shutil
import random
from pathlib import Path

SOURCE_DIR = Path("../../datasets/raw/PlantVillage")
TARGET_DIR = Path("../../datasets/processed")
SPLIT = {"train": 0.70, "val": 0.15, "test": 0.15}
SEED = 42

random.seed(SEED)

for split in SPLIT:
    (TARGET_DIR / split).mkdir(parents=True, exist_ok=True)

totals = {"train": 0, "val": 0, "test": 0}

for class_dir in sorted(SOURCE_DIR.iterdir()):
    if not class_dir.is_dir():
        continue

    images = [
        f for f in class_dir.iterdir()
        if f.suffix.lower() in {".jpg", ".jpeg", ".png"}
    ]
    if not images:
        continue

    random.shuffle(images)
    n = len(images)
    n_train = int(n * SPLIT["train"])
    n_val = int(n * SPLIT["val"])

    buckets = {
        "train": images[:n_train],
        "val": images[n_train:n_train + n_val],
        "test": images[n_train + n_val:],
    }

    for split_name, files in buckets.items():
        out_dir = TARGET_DIR / split_name / class_dir.name
        out_dir.mkdir(parents=True, exist_ok=True)
        for img in files:
            shutil.copy2(img, out_dir / img.name)
        totals[split_name] += len(files)

    print(f"OK {class_dir.name}: "
          f"{len(buckets['train'])}/{len(buckets['val'])}/{len(buckets['test'])}")

print(f"\nTOTAL: {totals['train']} train | {totals['val']} val | {totals['test']} test")
print(f"Location: {TARGET_DIR.resolve()}")
