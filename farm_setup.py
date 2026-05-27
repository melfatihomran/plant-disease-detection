"""
farm_setup.py
---------------------------------------------------------
Step 1: User opens a map in the browser
Step 2: User draws the farm border by clicking points
Step 3: AI generates a GPS grid of scan checkpoints
Step 4: Grid is saved to farm_config.json
---------------------------------------------------------
"""

import json
import math
import os

# -- Install folium if not already installed --
try:
    import folium
    from folium.plugins import Draw
except ImportError:
    os.system("pip install folium")
    import folium
    from folium.plugins import Draw

OUTPUT_PATH = "outputs"
os.makedirs(OUTPUT_PATH, exist_ok=True)


# ---------------------------------------------
#  STEP 1 — BUILD THE FARM DRAWING MAP
# ---------------------------------------------

def build_farm_map():
    """
    Opens an interactive map centered on Egypt.
    User draws their farm polygon and saves the coordinates.
    """

    # Center map on Egypt
    m = folium.Map(
        location=[26.8206, 30.8025],
        zoom_start=7,
        tiles="Esri.WorldImagery",  # satellite view
        attr="Esri"
    )

    # Add drawing tools
    draw = Draw(
        draw_options={
            "polygon"   : True,
            "rectangle" : True,
            "circle"    : False,
            "marker"    : False,
            "polyline"  : False,
            "circlemarker": False
        },
        edit_options={"edit": True}
    )
    draw.add_to(m)

    # Instructions overlay
    instructions_html = """
    <div style="
        position: fixed;
        top: 15px; left: 60px;
        z-index: 9999;
        background: white;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        font-family: Arial, sans-serif;
        max-width: 340px;
    ">
        <h3 style="margin:0 0 8px 0; color:#2C7A3F;"> Farm Setup</h3>
        <p style="margin:0 0 6px 0; font-size:13px; color:#333;">
            <b>Step 1:</b> Navigate to your farm location on the map.
        </p>
        <p style="margin:0 0 6px 0; font-size:13px; color:#333;">
            <b>Step 2:</b> Click the <b>polygon tool</b> (left toolbar) and draw your farm borders.
        </p>
        <p style="margin:0 0 6px 0; font-size:13px; color:#333;">
            <b>Step 3:</b> When done, right-click to close the shape.
        </p>
        <p style="margin:0 0 10px 0; font-size:13px; color:#333;">
            <b>Step 4:</b> Copy the coordinates below into <b>farm_config.json</b>
        </p>
        <hr style="border:1px solid #eee; margin:8px 0;">
        <p style="margin:0; font-size:11px; color:#888;">
            💡 Tip: Use satellite view to clearly see your farm boundaries.
        </p>
    </div>
    """
    m.get_root().html.add_child(folium.Element(instructions_html))

    # Coordinate capture script
    capture_html = """
    <div style="
        position: fixed;
        bottom: 30px; left: 50%;
        transform: translateX(-50%);
        z-index: 9999;
        background: white;
        padding: 12px 20px;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        font-family: Arial, sans-serif;
        text-align: center;
        min-width: 400px;
    ">
        <p style="margin:0 0 8px 0; font-size:13px; color:#333; font-weight:bold;">
            📋 Your farm coordinates will appear here after drawing:
        </p>
        <textarea id="coords_output" rows="4" style="
            width:100%; font-size:11px;
            border:1px solid #ddd; border-radius:6px;
            padding:6px; resize:none; font-family:monospace;
        " placeholder='Draw your farm on the map above...'></textarea>
        <p style="margin:6px 0 0 0; font-size:11px; color:#888;">
            Copy these coordinates and paste into farm_config.json -> "coordinates" field
        </p>
    </div>

    <script>
    function updateCoords() {
        setTimeout(function() {
            var layers = [];
            document.querySelectorAll('.leaflet-interactive').forEach(function(el) {
            });

            // Listen for draw events
            document.addEventListener('DOMContentLoaded', function() {
                if (window._map) {
                    window._map.on('draw:created', function(e) {
                        var coords = e.layer.getLatLngs()[0].map(function(p) {
                            return [parseFloat(p.lat.toFixed(6)), parseFloat(p.lng.toFixed(6))];
                        });
                        document.getElementById('coords_output').value =
                            JSON.stringify(coords, null, 2);
                    });
                }
            });
        }, 1000);
    }
    updateCoords();
    </script>
    """
    m.get_root().html.add_child(folium.Element(capture_html))

    # Save map
    map_path = os.path.join(OUTPUT_PATH, "farm_setup_map.html")
    m.save(map_path)
    print(f"\n  [OK] Farm setup map saved -> {map_path}")
    print(f"  Open this file in your browser to draw your farm.\n")
    return map_path


# ---------------------------------------------
#  STEP 2 — GENERATE GPS GRID FROM FARM POLYGON
# ---------------------------------------------

def generate_grid_from_polygon(coordinates, spacing_meters=10):
    """
    Given a list of [lat, lng] points forming a farm polygon,
    generates a grid of GPS checkpoints spaced ~spacing_meters apart.

    coordinates: list of [lat, lng] pairs
    spacing_meters: distance between scan points (default 10m)
    Returns: list of [lat, lng] checkpoint pairs
    """

    # Find bounding box of the polygon
    lats = [c[0] for c in coordinates]
    lngs = [c[1] for c in coordinates]
    min_lat, max_lat = min(lats), max(lats)
    min_lng, max_lng = min(lngs), max(lngs)

    # Convert meters to degrees (approximate)
    # 1 degree latitude ≈ 111,000 meters
    # 1 degree longitude ≈ 111,000 * cos(lat) meters
    avg_lat = (min_lat + max_lat) / 2
    lat_step = spacing_meters / 111000
    lng_step = spacing_meters / (111000 * math.cos(math.radians(avg_lat)))

    # Generate grid points inside bounding box
    grid_points = []
    lat = min_lat
    row = 0
    while lat <= max_lat:
        lng = min_lng
        # Zigzag pattern (like irrigation car movement)
        if row % 2 == 1:
            lng_range = []
            l = min_lng
            while l <= max_lng:
                lng_range.append(l)
                l += lng_step
            lng_range = list(reversed(lng_range))
        else:
            lng_range = []
            l = min_lng
            while l <= max_lng:
                lng_range.append(l)
                l += lng_step

        for lng in lng_range:
            if point_in_polygon(lat, lng, coordinates):
                grid_points.append([round(lat, 6), round(lng, 6)])

        lat += lat_step
        row += 1

    return grid_points


def point_in_polygon(lat, lng, polygon):
    """
    Ray casting algorithm to check if a point is inside a polygon.
    """
    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i][1], polygon[i][0]
        xj, yj = polygon[j][1], polygon[j][0]
        if ((yi > lat) != (yj > lat)) and \
           (lng < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


# ---------------------------------------------
#  STEP 3 — CREATE DEFAULT farm_config.json
# ---------------------------------------------

def create_default_config():
    """Creates a default farm_config.json for the user to fill in."""

    # Example farm near Fayoum, Egypt
    example_config = {
  "farm_name": "My Farm",
  "owner": "Owner",
  "location_name": "Fayoum, Egypt",
  "spacing_meters": 10,
  "coordinates": [
    [29.4285, 30.8360],
    [29.4285, 30.8385],
    [29.4270, 30.8385],
    [29.4270, 30.8360],
    [29.4285, 30.8360]
  ]
}

    config_path = "farm_config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(example_config, f, indent=2, ensure_ascii=False)

    print(f"  [OK] Default farm config saved -> {config_path}")
    print(f"  Edit this file with your real farm coordinates from the map.\n")
    return config_path


# ---------------------------------------------
#  STEP 4 — GENERATE GRID & SAVE
# ---------------------------------------------

def setup_farm():
    print("\n" + "="*55)
    print("  FARM SETUP")
    print("="*55)

    # Build the drawing map
    map_path = build_farm_map()

    # Create default config
    config_path = create_default_config()

    # Load config
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Generate GPS grid
    print(f"  Generating GPS scan grid for: {config['farm_name']}")
    print(f"  Spacing between checkpoints : {config['spacing_meters']} meters")

    grid = generate_grid_from_polygon(
        config["coordinates"],
        spacing_meters=config["spacing_meters"]
    )

    # Save grid to config
    config["scan_grid"] = grid
    config["total_checkpoints"] = len(grid)

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"  Total scan checkpoints generated: {len(grid)}")
    print(f"  Grid saved to farm_config.json [OK]")

    # Visualize grid on map
    visualize_grid(config, grid)

    print("\n" + "="*55)
    print("  NEXT STEPS:")
    print("  1. Open outputs/farm_setup_map.html in your browser")
    print("  2. Draw your real farm borders")
    print("  3. Copy coordinates into farm_config.json")
    print("  4. Re-run this file to regenerate the grid")
    print("  5. Then run simulate_scan.py to simulate detection")
    print("="*55 + "\n")


def visualize_grid(config, grid):
    """Shows the generated scan grid on a map."""

    if not grid:
        print("  No grid points generated.")
        return

    center_lat = sum(p[0] for p in grid) / len(grid)
    center_lng = sum(p[1] for p in grid) / len(grid)

    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=17,
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
        weight=3,
        tooltip=f"Farm: {config['farm_name']}"
    ).add_to(m)

    # Draw grid points
    for i, point in enumerate(grid):
        folium.CircleMarker(
            location=point,
            radius=3,
            color="#1565C0",
            fill=True,
            fill_color="#1565C0",
            fill_opacity=0.7,
            tooltip=f"Checkpoint {i+1}: {point[0]:.6f}, {point[1]:.6f}"
        ).add_to(m)

    # Connect grid with lines (irrigation car path)
    if len(grid) > 1:
        folium.PolyLine(
            locations=grid,
            color="#FF8F00",
            weight=1.5,
            opacity=0.6,
            tooltip="Irrigation car path"
        ).add_to(m)

    # Info box
    info_html = f"""
    <div style="
        position:fixed; top:15px; right:15px; z-index:9999;
        background:white; padding:12px 16px; border-radius:10px;
        box-shadow:0 4px 15px rgba(0,0,0,0.2); font-family:Arial;
    ">
        <h4 style="margin:0 0 8px 0; color:#2C7A3F;"> {config['farm_name']}</h4>
        <p style="margin:0; font-size:12px;">📌 Location: {config['location_name']}</p>
        <p style="margin:0; font-size:12px;"> Spacing: {config['spacing_meters']}m</p>
        <p style="margin:0; font-size:12px;"> Checkpoints: {len(grid)}</p>
        <p style="margin:0; font-size:12px; color:#FF8F00;"> Orange line = car path</p>
    </div>
    """
    m.get_root().html.add_child(folium.Element(info_html))

    grid_map_path = os.path.join(OUTPUT_PATH, "farm_grid_map.html")
    m.save(grid_map_path)
    print(f"  [OK] Grid map saved -> {grid_map_path}")


if __name__ == "__main__":
    setup_farm()
