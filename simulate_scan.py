"""
simulate_scan.py
---------------------------------------------------------
Simulates the irrigation car moving across the farm,
taking photos at each GPS checkpoint and detecting disease.

Outputs:
  - outputs/scan_results_map.html  -> interactive disease map
  - outputs/scan_report.csv        -> full detection report
---------------------------------------------------------
"""

import os
import json
import random
import csv
from datetime import datetime

try:
    import folium
except ImportError:
    os.system("pip install folium")
    import folium

import joblib
import numpy as np
from skimage.io import imread
from skimage.transform import resize
from skimage.color import rgb2hsv
from skimage.feature import hog

from treatments import TREATMENTS, get_treatment

# ---------------------------------------------
#  CONFIG
# ---------------------------------------------

DATASET_PATH = "dataset"
MODEL_PATH   = "models"
OUTPUT_PATH  = "outputs"
CONFIG_PATH  = "farm_config.json"
IMG_SIZE     = (128, 128)
LANGUAGE     = "ar"   # "en" for English, "ar" for Arabic

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


# ---------------------------------------------
#  FEATURE EXTRACTION (same as main.py)
# ---------------------------------------------

def extract_features(image_path):
    img = imread(image_path)
    if img.ndim == 2:
        img = np.stack([img, img, img], axis=-1)
    if img.shape[-1] == 4:
        img = img[:, :, :3]
    img = resize(img, IMG_SIZE, anti_aliasing=True)
    img = (img * 255).astype(np.uint8)

    hog_features = hog(img, orientations=9,
                       pixels_per_cell=(16, 16),
                       cells_per_block=(2, 2),
                       channel_axis=-1)

    img_hsv = rgb2hsv(img)
    hist_h, _ = np.histogram(img_hsv[:, :, 0], bins=32, range=(0, 1))
    hist_s, _ = np.histogram(img_hsv[:, :, 1], bins=32, range=(0, 1))
    hist_v, _ = np.histogram(img_hsv[:, :, 2], bins=32, range=(0, 1))
    color_features = np.concatenate([hist_h, hist_s, hist_v])

    return np.concatenate([hog_features, color_features])


# ---------------------------------------------
#  LOAD MODEL
# ---------------------------------------------

def load_best_model():
    """Loads the ANN model (best performer)"""
    model_file  = os.path.join(MODEL_PATH, "ANN_MLP.pkl")
    scaler_file = os.path.join(MODEL_PATH, "scaler.pkl")
    le_file     = os.path.join(MODEL_PATH, "label_encoder.pkl")

    if not os.path.exists(model_file):
        print("  [!] Model not found. Please run main.py first.")
        return None, None, None

    model  = joblib.load(model_file)
    scaler = joblib.load(scaler_file)
    le     = joblib.load(le_file)
    print("  [OK] ANN model loaded successfully.")
    return model, scaler, le


# ---------------------------------------------
#  GET RANDOM SAMPLE IMAGE FROM DATASET
# ---------------------------------------------

def get_random_image(class_name=None):
    """Gets a random image from the dataset to simulate camera capture."""
    if class_name is None:
        class_name = random.choice(CLASSES)

    class_folder = os.path.join(DATASET_PATH, class_name)
    if not os.path.exists(class_folder):
        return None, None

    images = [f for f in os.listdir(class_folder)
              if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if not images:
        return None, None

    img_file = random.choice(images)
    return os.path.join(class_folder, img_file), class_name


# ---------------------------------------------
#  SCAN THE FARM
# ---------------------------------------------

def scan_farm():
    print("\n" + "="*55)
    print("  IRRIGATION CAR SCAN SIMULATION")
    print("="*55)

    # Load farm config
    if not os.path.exists(CONFIG_PATH):
        print(f"  [!] farm_config.json not found. Run farm_setup.py first.")
        return

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    grid = config.get("scan_grid", [])
    if not grid:
        print("  [!] No scan grid found. Run farm_setup.py first.")
        return

    print(f"  Farm        : {config['farm_name']}")
    print(f"  Location    : {config['location_name']}")
    print(f"  Checkpoints : {len(grid)}")
    print(f"  Scanning...\n")

    # Load model
    model, scaler, le = load_best_model()
    if model is None:
        return

    # Scan each checkpoint
    detections = []
    disease_count = 0
    healthy_count = 0

    # Limit to 50 checkpoints for demo speed
    scan_points = grid[:50] if len(grid) > 50 else grid

    for i, point in enumerate(scan_points):
        lat, lng = point

        # Simulate camera capture (get random image from dataset)
        img_path, true_class = get_random_image()
        if img_path is None:
            continue

        # Extract features & predict
        try:
            features = extract_features(img_path)
            features_scaled = scaler.transform([features])
            pred_index = model.predict(features_scaled)[0]
            pred_class = le.inverse_transform([pred_index])[0]
            confidence = max(model.predict_proba(features_scaled)[0]) * 100
        except Exception as e:
            continue

        # Get treatment
        treatment = get_treatment(pred_class, language=LANGUAGE)
        is_healthy = pred_class == "Tomato___healthy"

        if is_healthy:
            healthy_count += 1
        else:
            disease_count += 1

        detection = {
            "checkpoint"  : i + 1,
            "latitude"    : lat,
            "longitude"   : lng,
            "disease"     : pred_class,
            "confidence"  : round(confidence, 1),
            "severity"    : treatment["severity"] if treatment else "Unknown",
            "spread_risk" : treatment["spread_risk"] if treatment else "Unknown",
            "description" : treatment["description"] if treatment else "",
            "treatment"   : " | ".join(treatment["steps"][:2]) if treatment else "",
            "timestamp"   : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "color"       : treatment["color"] if treatment else "gray"
        }
        detections.append(detection)

        status = "[OK] Healthy" if is_healthy else f"[!]  {pred_class.split('___')[1]}"
        print(f"  Point {i+1:02d} | {lat:.6f}, {lng:.6f} | {status} ({confidence:.0f}%)")

    print(f"\n  Scan complete!")
    print(f"  Healthy crops  : {healthy_count}")
    print(f"  Diseased crops : {disease_count}")
    print(f"  Disease rate   : {disease_count/(healthy_count+disease_count)*100:.1f}%")

    # Save outputs
    save_csv_report(detections, config)
    save_disease_map(detections, config)


# ---------------------------------------------
#  SAVE CSV REPORT
# ---------------------------------------------

def save_csv_report(detections, config):
    report_path = os.path.join(OUTPUT_PATH, "scan_report.csv")

    with open(report_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "checkpoint", "latitude", "longitude", "disease",
            "confidence", "severity", "spread_risk",
            "description", "treatment", "timestamp"
        ])
        writer.writeheader()
        for d in detections:
            writer.writerow({k: v for k, v in d.items() if k != "color"})

    print(f"\n  [OK] CSV report saved -> {report_path}")


# ---------------------------------------------
#  SAVE INTERACTIVE DISEASE MAP
# ---------------------------------------------

def save_disease_map(detections, config):
    if not detections:
        return

    center_lat = sum(d["latitude"] for d in detections) / len(detections)
    center_lng = sum(d["longitude"] for d in detections) / len(detections)

    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=18,
        tiles="Esri.WorldImagery",
        attr="Esri"
    )

    # Draw farm boundary
    folium.Polygon(
        locations=config["coordinates"],
        color="#2C7A3F",
        fill=True,
        fill_color="#2C7A3F",
        fill_opacity=0.1,
        weight=3
    ).add_to(m)

    # Color map for severity
    color_map = {
        "green"   : "#4CAF50",
        "orange"  : "#FF9800",
        "red"     : "#F44336",
        "darkred" : "#B71C1C",
        "gray"    : "#9E9E9E"
    }

    # Add detection pins
    for d in detections:
        color   = color_map.get(d["color"], "#9E9E9E")
        disease_short = d["disease"].replace("Tomato___", "").replace("Potato___", "").replace("_", " ")

        popup_html = f"""
        <div style="font-family:Arial; min-width:220px; max-width:280px;">
            <h4 style="margin:0 0 6px 0; color:{color};">
                {'[OK]' if d['color']=='green' else '[!]'} {disease_short}
            </h4>
            <p style="margin:0; font-size:12px;"><b> Location:</b> {d['latitude']:.6f}, {d['longitude']:.6f}</p>
            <p style="margin:0; font-size:12px;"><b>🎯 Confidence:</b> {d['confidence']}%</p>
            <p style="margin:0; font-size:12px;"><b> Severity:</b> {d['severity']}</p>
            <p style="margin:0; font-size:12px;"><b> Spread Risk:</b> {d['spread_risk']}</p>
            <hr style="border:1px solid #eee; margin:6px 0;">
            <p style="margin:0; font-size:11px; color:#555;">{d['description'][:120]}...</p>
            <hr style="border:1px solid #eee; margin:6px 0;">
            <p style="margin:0; font-size:11px;"><b> Treatment:</b></p>
            <p style="margin:0; font-size:11px; color:#333;">{d['treatment'][:150]}</p>
            <p style="margin:4px 0 0 0; font-size:10px; color:#aaa;"> {d['timestamp']}</p>
        </div>
        """

        folium.CircleMarker(
            location=[d["latitude"], d["longitude"]],
            radius=8,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.85,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"Point {d['checkpoint']}: {disease_short} ({d['confidence']}%)"
        ).add_to(m)

    # Summary box
    total     = len(detections)
    diseased  = sum(1 for d in detections if d["color"] != "green")
    healthy   = total - diseased
    rate      = diseased / total * 100 if total > 0 else 0

    summary_html = f"""
    <div style="
        position:fixed; top:15px; right:15px; z-index:9999;
        background:white; padding:14px 18px; border-radius:12px;
        box-shadow:0 4px 20px rgba(0,0,0,0.2); font-family:Arial;
        min-width:220px;
    ">
        <h4 style="margin:0 0 10px 0; color:#2C7A3F;"> {config['farm_name']}</h4>
        <p style="margin:0 0 4px 0; font-size:12px;"> {config['location_name']}</p>
        <p style="margin:0 0 4px 0; font-size:12px;"> Points scanned: <b>{total}</b></p>
        <p style="margin:0 0 4px 0; font-size:12px; color:#4CAF50;">[OK] Healthy: <b>{healthy}</b></p>
        <p style="margin:0 0 4px 0; font-size:12px; color:#F44336;">[!] Diseased: <b>{diseased}</b></p>
        <p style="margin:0 0 8px 0; font-size:12px;"> Disease rate: <b>{rate:.1f}%</b></p>
        <hr style="border:1px solid #eee; margin:8px 0;">
        <p style="margin:0; font-size:11px; color:#888;">
             Healthy &nbsp;  Medium &nbsp;  High &nbsp;  Critical
        </p>
        <p style="margin:4px 0 0 0; font-size:10px; color:#aaa;">Click any pin for details</p>
    </div>
    """
    m.get_root().html.add_child(folium.Element(summary_html))

    map_path = os.path.join(OUTPUT_PATH, "scan_results_map.html")
    m.save(map_path)
    print(f"  [OK] Disease map saved -> {map_path}")
    print(f"  Open this file in your browser to see the results!\n")


if __name__ == "__main__":
    scan_farm()
