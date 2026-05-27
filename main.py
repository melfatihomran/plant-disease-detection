"""
=============================================================
  CAI3101 - Introduction to Artificial Intelligence
  Project: AI Plant Disease Detection
  Crops: Tomato + Potato | 7 Classes
=============================================================
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

warnings.filterwarnings('ignore')

from skimage.feature import hog
from skimage.io import imread
from skimage.transform import resize
from skimage.color import rgb2hsv

from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (accuracy_score, classification_report,
                              confusion_matrix, ConfusionMatrixDisplay)
import joblib

# ─────────────────────────────────────────────
#  CONFIGURATION — update this path only
# ─────────────────────────────────────────────

DATASET_PATH = "dataset"   # folder containing your 7 class subfolders
OUTPUT_PATH  = "outputs"
MODEL_PATH   = "models"
IMG_SIZE     = (128, 128)  # resize all images to this
MAX_PER_CLASS = 300        # use 300 images per class (fast & balanced)

CLASSES = [
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Septoria_leaf_spot",
    "Tomato___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
]

os.makedirs(OUTPUT_PATH, exist_ok=True)
os.makedirs(MODEL_PATH,  exist_ok=True)


# ─────────────────────────────────────────────
#  STEP 1 — FEATURE EXTRACTION
# ─────────────────────────────────────────────

def extract_features(image_path):
    """
    Extract HOG + HSV Color Histogram features from a single image.
    Returns a 1D feature vector.
    """
    img = imread(image_path)

    # Handle RGBA images (4 channels → 3)
    if img.ndim == 2:
        img = np.stack([img, img, img], axis=-1)
    if img.shape[-1] == 4:
        img = img[:, :, :3]

    # Resize
    img = resize(img, IMG_SIZE, anti_aliasing=True)
    img = (img * 255).astype(np.uint8)

    # HOG features (captures shape/texture of lesions)
    hog_features = hog(
        img,
        orientations=9,
        pixels_per_cell=(16, 16),
        cells_per_block=(2, 2),
        channel_axis=-1
    )

    # HSV Color Histogram (captures color of disease spots)
    img_hsv = rgb2hsv(img)
    hist_h, _ = np.histogram(img_hsv[:, :, 0], bins=32, range=(0, 1))
    hist_s, _ = np.histogram(img_hsv[:, :, 1], bins=32, range=(0, 1))
    hist_v, _ = np.histogram(img_hsv[:, :, 2], bins=32, range=(0, 1))
    color_features = np.concatenate([hist_h, hist_s, hist_v])

    # Combine into one feature vector
    return np.concatenate([hog_features, color_features])


# ─────────────────────────────────────────────
#  STEP 2 — LOAD DATASET
# ─────────────────────────────────────────────

print("\n" + "="*55)
print("  Loading & extracting features from dataset...")
print("="*55)

X, y = [], []

for class_name in CLASSES:
    class_folder = os.path.join(DATASET_PATH, class_name)

    if not os.path.exists(class_folder):
        print(f"  [!] Folder not found: {class_folder}")
        continue

    images = [f for f in os.listdir(class_folder)
              if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    images = images[:MAX_PER_CLASS]

    print(f"  Processing {class_name[:45]:<45} ({len(images)} images)")

    for img_file in images:
        img_path = os.path.join(class_folder, img_file)
        try:
            features = extract_features(img_path)
            X.append(features)
            y.append(class_name)
        except Exception as e:
            pass  # skip corrupted images

X = np.array(X)
y = np.array(y)

print(f"\n  Total samples loaded : {len(X)}")
print(f"  Feature vector size  : {X.shape[1]}")
print(f"  Classes found        : {len(np.unique(y))}")

# ── Chart 0: Class Distribution (Data Understanding) ──
short_names = [
    "Tomato\nEarly Blight", "Tomato\nLate Blight",
    "Tomato\nYL Curl Virus", "Tomato\nSeptoria",
    "Tomato\nHealthy", "Potato\nEarly Blight", "Potato\nLate Blight"
]
unique_classes, counts = np.unique(y, return_counts=True)
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

bar_colors = ["#E57373","#EF5350","#FF8A65","#FFA726","#66BB6A","#42A5F5","#26C6DA"]
axes[0].bar(short_names, counts, color=bar_colors, edgecolor="white", linewidth=1.2)
for bar, count in zip(axes[0].patches, counts):
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                 str(count), ha="center", va="bottom", fontsize=10, fontweight="bold")
axes[0].set_title("Sample Count per Disease Class", fontsize=12, fontweight="bold", pad=12)
axes[0].set_ylabel("Number of Images", fontsize=11)
axes[0].set_ylim(0, max(counts) * 1.15)
axes[0].spines[["top","right"]].set_visible(False)
axes[0].set_facecolor("#f9f9f9")

axes[1].pie(counts, labels=short_names, colors=bar_colors,
            autopct="%1.1f%%", startangle=140, textprops={"fontsize": 9})
axes[1].set_title("Class Distribution (%)", fontsize=12, fontweight="bold", pad=12)

fig.patch.set_facecolor("#ffffff")
plt.suptitle("Dataset Summary Statistics — PlantVillage (Tomato + Potato Subset)",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_PATH, "class_distribution.png"),
            dpi=150, bbox_inches="tight")
plt.close()
print("  Saved: class_distribution.png")


# ─────────────────────────────────────────────
#  STEP 3 — PREPROCESSING
# ─────────────────────────────────────────────

print("\n" + "="*55)
print("  Preprocessing...")
print("="*55)

# Encode class labels to numbers
le = LabelEncoder()
y_encoded = le.fit_transform(y)
print(f"  Label encoding: {dict(zip(le.classes_, le.transform(le.classes_)))}")

# Train/test split (80/20, stratified)
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

# Normalize features (zero mean, unit variance)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test  = scaler.transform(X_test)

print(f"  Training samples : {len(X_train)}")
print(f"  Testing samples  : {len(X_test)}")

# Save preprocessor
joblib.dump(scaler, os.path.join(MODEL_PATH, "scaler.pkl"))
joblib.dump(le,     os.path.join(MODEL_PATH, "label_encoder.pkl"))
print("  Scaler and label encoder saved.")


# ─────────────────────────────────────────────
#  STEP 4 — TRAIN 3 MODELS
# ─────────────────────────────────────────────

print("\n" + "="*55)
print("  Training models...")
print("="*55)

models = {
    "Naive Bayes": GaussianNB(),

    "Decision Tree": DecisionTreeClassifier(
        max_depth=15,
        min_samples_split=5,
        class_weight="balanced",
        random_state=42
    ),

    "ANN (MLP)": MLPClassifier(
        hidden_layer_sizes=(256, 128, 64),
        activation="relu",
        max_iter=200,
        random_state=42,
        verbose=False
    )
}

results = {}

for name, model in models.items():
    print(f"\n  Training {name}...")
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc    = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred,
                                   target_names=le.classes_,
                                   output_dict=True)

    results[name] = {
        "model"   : model,
        "accuracy": acc,
        "y_pred"  : y_pred,
        "report"  : report
    }

    # Save model
    safe_name = name.replace(" ", "_").replace("(", "").replace(")", "")
    joblib.dump(model, os.path.join(MODEL_PATH, f"{safe_name}.pkl"))

    print(f"  Accuracy: {acc*100:.2f}%")


# ─────────────────────────────────────────────
#  STEP 5 — EVALUATION & CHARTS
# ─────────────────────────────────────────────

print("\n" + "="*55)
print("  Generating evaluation charts...")
print("="*55)

# Short class labels for display
short_labels = [
    "Tomato\nEarly Blight",
    "Tomato\nLate Blight",
    "Tomato\nYL Curl Virus",
    "Tomato\nSeptoria",
    "Tomato\nHealthy",
    "Potato\nEarly Blight",
    "Potato\nLate Blight",
]

# ── Chart 1: Accuracy Comparison Bar Chart ──
fig, ax = plt.subplots(figsize=(8, 5))
model_names = list(results.keys())
accuracies  = [results[m]["accuracy"] * 100 for m in model_names]
colors      = ["#4CAF50", "#2196F3", "#FF5722"]

bars = ax.bar(model_names, accuracies, color=colors, width=0.5,
              edgecolor="white", linewidth=1.2)

for bar, acc in zip(bars, accuracies):
    ax.text(bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.8,
            f"{acc:.1f}%",
            ha="center", va="bottom", fontsize=12, fontweight="bold")

ax.set_ylim(0, 110)
ax.set_ylabel("Accuracy (%)", fontsize=12)
ax.set_title("Model Accuracy Comparison\nAI Plant Disease Detection (Tomato + Potato)",
             fontsize=13, fontweight="bold", pad=15)
ax.spines[["top", "right"]].set_visible(False)
ax.set_facecolor("#f9f9f9")
fig.patch.set_facecolor("#ffffff")

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_PATH, "accuracy_comparison.png"), dpi=150)
plt.close()
print("  Saved: accuracy_comparison.png")

# ── Chart 2: Confusion Matrices (3 side by side) ──
fig, axes = plt.subplots(1, 3, figsize=(20, 6))

for ax, (name, res) in zip(axes, results.items()):
    cm = confusion_matrix(y_test, res["y_pred"])
    disp = ConfusionMatrixDisplay(confusion_matrix=cm,
                                  display_labels=short_labels)
    disp.plot(ax=ax, colorbar=False, cmap="Greens")
    ax.set_title(f"{name}\nAccuracy: {res['accuracy']*100:.1f}%",
                 fontsize=12, fontweight="bold")
    ax.set_xticklabels(short_labels, rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels(short_labels, rotation=0, fontsize=8)

plt.suptitle("Confusion Matrices — All 3 Models",
             fontsize=14, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_PATH, "confusion_matrices.png"),
            dpi=150, bbox_inches="tight")
plt.close()
print("  Saved: confusion_matrices.png")

# ── Chart 3: Per-class F1 Score Comparison ──
fig, ax = plt.subplots(figsize=(12, 6))
x      = np.arange(len(short_labels))
width  = 0.25

for i, (name, res) in enumerate(results.items()):
    f1_scores = [res["report"][cls]["f1-score"] for cls in le.classes_]
    ax.bar(x + i * width, f1_scores, width,
           label=name, color=colors[i], alpha=0.85, edgecolor="white")

ax.set_xticks(x + width)
ax.set_xticklabels(short_labels, fontsize=9)
ax.set_ylabel("F1 Score", fontsize=12)
ax.set_ylim(0, 1.1)
ax.set_title("Per-Class F1 Score Comparison",
             fontsize=13, fontweight="bold", pad=15)
ax.legend(fontsize=11)
ax.spines[["top", "right"]].set_visible(False)
ax.set_facecolor("#f9f9f9")
fig.patch.set_facecolor("#ffffff")

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_PATH, "f1_comparison.png"), dpi=150)
plt.close()
print("  Saved: f1_comparison.png")


# ─────────────────────────────────────────────
#  FINAL SUMMARY
# ─────────────────────────────────────────────

print("\n" + "="*55)
print("  FINAL RESULTS SUMMARY")
print("="*55)

for name, res in results.items():
    print(f"\n  {name}")
    print(f"    Accuracy : {res['accuracy']*100:.2f}%")
    print(f"    Report:")
    report = classification_report(y_test, res["y_pred"],
                                    target_names=le.classes_)
    for line in report.split("\n"):
        print(f"      {line}")

best_model = max(results, key=lambda m: results[m]["accuracy"])
print(f"\n  Best model: {best_model} "
      f"({results[best_model]['accuracy']*100:.2f}% accuracy)")

print("\n" + "="*55)
print("  All models saved to   -> models/")
print("  All charts saved to   -> outputs/")
print("  Run complete!")
print("="*55 + "\n")