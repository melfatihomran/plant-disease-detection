#  AI Plant Disease Detection 
The idea is to develop an application that uses ai power to help farmers in rural areas with plant diseases

Automated detection of **7 plant disease classes** (Tomato + Potato) using classical ML and deep learning models, trained on the [PlantVillage dataset](https://www.kaggle.com/datasets/emmarex/plantdisease).

---

##  Project Structure

```
plant-disease-detection/
├── dataset/                          # PlantVillage class subfolders
│   ├── Tomato___Early_blight/
│   ├── Tomato___Late_blight/
│   ├── Tomato___Tomato_Yellow_Leaf_Curl_Virus/
│   ├── Tomato___Septoria_leaf_spot/
│   ├── Tomato___healthy/
│   ├── Potato___Early_blight/
│   └── Potato___Late_blight/
├── models/                           # Saved model files
├── outputs/                          # Charts & evaluation plots
├── main.py                           # Classical ML (Naive Bayes, Decision Tree, ANN)
├── plant_disease_deep_learning.ipynb # Deep Learning (Custom CNN + ResNet-50) — Kaggle
├── app.py                            # Inference app
├── simulate_scan.py
├── farm_setup.py
├── treatments.py
├── farm_config.json
└── README.md
```

---

##  Models

| Model | Type | Feature Input |
|-------|------|---------------|
| Naive Bayes | Classical ML | HOG + HSV histogram |
| Decision Tree | Classical ML | HOG + HSV histogram |
| ANN (MLP) | Classical ML | HOG + HSV histogram |
| **Custom CNN** | Deep Learning | Raw images (128×128) |
| **ResNet-50** | Transfer Learning | Raw images (128×128) |

---

##  How to Run

### Classical ML models (`main.py`)
```bash
pip install scikit-image scikit-learn matplotlib seaborn joblib
python main.py
```

### Deep Learning models (Kaggle Notebook)
1. Upload `plant_disease_deep_learning.ipynb` to [Kaggle](https://www.kaggle.com)
2. Add the PlantVillage dataset as a Kaggle Dataset input
3. Enable **GPU accelerator** (T4 × 2 recommended)
4. Update `DATASET_PATH` in Cell 2 to match your dataset path
5. Run all cells — training takes ~15–25 min on GPU

---

##  Classes

```
Tomato___Early_blight
Tomato___Late_blight
Tomato___Tomato_Yellow_Leaf_Curl_Virus
Tomato___Septoria_leaf_spot
Tomato___healthy
Potato___Early_blight
Potato___Late_blight
```

---

##  Outputs

Charts saved to `outputs/`:

| File | Description |
|------|-------------|
| `class_distribution.png` | Dataset balance bar + pie chart |
| `accuracy_comparison.png` | Classical ML model accuracy |
| `confusion_matrices.png` | Confusion matrices (Naive Bayes, DT, ANN) |
| `f1_comparison.png` | Per-class F1 (classical models) |
| `custom_cnn_training_curves.png` | CNN loss & accuracy per epoch |
| `resnet50_training_curves.png` | ResNet-50 loss & accuracy per epoch |
| `dl_confusion_matrices.png` | Confusion matrices (CNN + ResNet) |
| `dl_f1_comparison.png` | Per-class F1 (CNN vs ResNet) |
| `all_models_accuracy.png` | All 5 models side-by-side |

---

##  Requirements

**Classical ML (`main.py`):**
```
numpy scikit-image scikit-learn matplotlib seaborn joblib
```

**Deep Learning (Kaggle notebook):**
```
torch torchvision  # pre-installed on Kaggle GPU kernels
```

---

## 📝 Notes

- Dataset is balanced at **300 images per class** (2,100 total) to match classical ML experiments
- ResNet-50 uses a **two-phase training** strategy: frozen backbone for epochs 1–10, then `layer4` + head unfrozen for fine-tuning in epochs 11–20
- Best model checkpoints saved as `.pth` files in `models/`
