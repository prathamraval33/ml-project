import os
import subprocess
import urllib.request
import sqlite3
import json
import matplotlib.pyplot as plt
import numpy as np
import qrcode
from PIL import Image

BASE_DIR = os.path.abspath(".")
ASSETS_DIR = os.path.join(BASE_DIR, "presentation_assets")
LOGOS_DIR = os.path.join(ASSETS_DIR, "logos")
CHARTS_DIR = os.path.join(ASSETS_DIR, "charts")

os.makedirs(LOGOS_DIR, exist_ok=True)
os.makedirs(CHARTS_DIR, exist_ok=True)

EDGE_EXE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# --- 1. DOWNLOAD & RENDER OFFICIAL LOGOS ---
def fetch_logo_png(name, url, is_svg=False, fill_color="white", bg_color=None):
    png_path = os.path.join(LOGOS_DIR, f"{name}.png")
    if os.path.exists(png_path) and os.path.getsize(png_path) > 1000:
        print(f"[Logo] {name} already exists.")
        return png_path

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()

        if not is_svg:
            with open(png_path, "wb") as f:
                f.write(data)
            print(f"[Logo] Downloaded direct PNG: {name}")
            return png_path
        else:
            svg_text = data.decode("utf-8")
            # Replace fill if specified
            if fill_color:
                if 'fill="' in svg_text:
                    import re
                    svg_text = re.sub(r'fill="[^"]+"', f'fill="{fill_color}"', svg_text)
                else:
                    svg_text = svg_text.replace("<svg ", f'<svg fill="{fill_color}" ')

            temp_html = os.path.join(LOGOS_DIR, f"temp_{name}.html")
            bg_css = f"background:{bg_color};" if bg_color else "background:transparent;"
            html_content = f"""<!DOCTYPE html>
<html>
<head>
<style>
  body {{ margin: 0; {bg_css} display: flex; align-items: center; justify-content: center; height: 100vh; overflow: hidden; }}
  svg {{ width: 200px; height: 200px; }}
</style>
</head>
<body>
{svg_text}
</body>
</html>"""
            with open(temp_html, "w", encoding="utf-8") as f:
                f.write(html_content)

            cmd = [
                EDGE_EXE,
                "--headless",
                f"--screenshot={png_path}",
                "--window-size=256,256",
                "--default-background-color=00000000",
                f"file:///{os.path.abspath(temp_html)}"
            ]
            subprocess.run(cmd, check=True)
            if os.path.exists(temp_html):
                os.remove(temp_html)
            print(f"[Logo] Rendered SVG to PNG: {name}")
            return png_path
    except Exception as e:
        print(f"[Logo] Error fetching {name}: {e}")
        return None

# Brand assets
fetch_logo_png("python", "https://cdn.jsdelivr.net/npm/simple-icons@v11/icons/python.svg", is_svg=True, fill_color="#3776AB")
fetch_logo_png("fastapi", "https://cdn.jsdelivr.net/npm/simple-icons@v11/icons/fastapi.svg", is_svg=True, fill_color="#009688")
fetch_logo_png("react", "https://cdn.jsdelivr.net/npm/simple-icons@v11/icons/react.svg", is_svg=True, fill_color="#61DAFB")
fetch_logo_png("vite", "https://cdn.jsdelivr.net/npm/simple-icons@v11/icons/vite.svg", is_svg=True, fill_color="#646CFF")
fetch_logo_png("scikitlearn", "https://cdn.jsdelivr.net/npm/simple-icons@v11/icons/scikitlearn.svg", is_svg=True, fill_color="#F7931E")
fetch_logo_png("tailwindcss", "https://cdn.jsdelivr.net/npm/simple-icons@v11/icons/tailwindcss.svg", is_svg=True, fill_color="#06B6D4")
fetch_logo_png("sqlite", "https://cdn.jsdelivr.net/npm/simple-icons@v11/icons/sqlite.svg", is_svg=True, fill_color="#003B57")
fetch_logo_png("github", "https://cdn.jsdelivr.net/npm/simple-icons@v11/icons/github.svg", is_svg=True, fill_color="#FFFFFF")

fetch_logo_png("xgboost", "https://raw.githubusercontent.com/dmlc/dmlc.github.io/master/img/logo-m/xgboost.png", is_svg=False)
fetch_logo_png("optuna", "https://raw.githubusercontent.com/optuna/optuna/master/docs/image/optuna-logo.png", is_svg=False)
fetch_logo_png("shap", "https://raw.githubusercontent.com/shap/shap/master/docs/artwork/shap_logo.png", is_svg=False)
fetch_logo_png("catboost", "https://avatars.githubusercontent.com/u/29729868?s=400&v=4", is_svg=False)

# --- 2. GENERATE DARK VOID MATPLOTLIB CHARTS ---

# Style tokens
VOID_BG = "#0B0D17"
PANEL_BG = "#121422"
IRIS = "#8052FF"
SAFFRON = "#FFB829"
VERDANT = "#10B981"
ROSE = "#FF5C7A"
WHITE = "#FFFFFF"
ASH = "#94A3B8"
HAIRLINE = "#1F2338"

plt.rcParams.update({
    "font.sans-serif": "Arial",
    "font.family": "sans-serif",
    "figure.facecolor": VOID_BG,
    "axes.facecolor": PANEL_BG,
    "axes.edgecolor": HAIRLINE,
    "axes.labelcolor": ASH,
    "xtick.color": ASH,
    "ytick.color": ASH,
    "text.color": WHITE,
    "grid.color": HAIRLINE,
    "grid.linestyle": "--",
    "grid.alpha": 0.6,
})

# CHART 1: Data Audit Funnel & Completeness Breakdown
def generate_audit_chart():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5), dpi=300)
    fig.patch.set_facecolor(VOID_BG)

    # Left: Audit Funnel
    stages = ["Raw Ingested", "Deduplicated", "Pre-Release Eligible", "Train Set (1990-2022)", "Held-Out Test (2023-2025)"]
    counts = [9999, 9767, 3931, 3548, 383]
    colors = [ASH, HAIRLINE, IRIS, VERDANT, SAFFRON]

    y_pos = np.arange(len(stages))
    bars = ax1.barh(y_pos, counts, color=colors, height=0.55, edgecolor=HAIRLINE)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(stages, fontsize=11, fontweight="bold", color=WHITE)
    ax1.invert_yaxis()
    ax1.set_xlabel("Number of Film Records", fontsize=10, color=ASH)
    ax1.set_title("Data Cleaning & Audit Funnel", fontsize=13, fontweight="bold", pad=12, color=WHITE)
    ax1.grid(axis="x", alpha=0.3)

    for bar, count in zip(bars, counts):
        ax1.text(bar.get_width() + 150, bar.get_y() + bar.get_height()/2, f"{count:,}",
                 va='center', ha='left', fontsize=10, fontweight="bold", color=WHITE)
    ax1.set_xlim(0, 11800)

    # Right: Financial Completeness in Raw Data
    labels = ["Usable Both > 0\n(4,696)", "Missing Budget\n(4,774)", "Missing Revenue\n(4,432)", "Missing Both\n(3,903)"]
    vals = [4696, 4774, 4432, 3903]
    colors_pie = [VERDANT, ROSE, SAFFRON, "#E11D48"]
    
    x = np.arange(len(labels))
    bars2 = ax2.bar(x, vals, color=colors_pie, width=0.5, edgecolor=HAIRLINE)
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=9, color=ASH)
    ax2.set_ylabel("Records (Raw N=9,999)", fontsize=10, color=ASH)
    ax2.set_title("Raw Financial Data Anomalies", fontsize=13, fontweight="bold", pad=12, color=WHITE)
    ax2.grid(axis="y", alpha=0.3)

    for bar, val in zip(bars2, vals):
        pct = (val / 9999) * 100
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100, f"{pct:.1f}%",
                 ha='center', va='bottom', fontsize=10, fontweight="bold", color=WHITE)
    ax2.set_ylim(0, 5600)

    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, "data_audit_funnel.png")
    fig.savefig(path, bbox_inches="tight", facecolor=VOID_BG)
    plt.close(fig)
    print("[Chart] Generated:", path)

# CHART 2: Success Tier ROI Distribution
def generate_tier_distribution():
    fig, ax = plt.subplots(figsize=(6.5, 4.2), dpi=300)
    fig.patch.set_facecolor(VOID_BG)

    tiers = ["Flop\n(ROI < 0)", "Break-even\n(0 ≤ ROI < 1)", "Hit\n(1 ≤ ROI < 3)", "Blockbuster\n(ROI ≥ 3)"]
    counts = [884, 807, 1130, 1110]
    percentages = [22.49, 20.53, 28.75, 28.24]
    colors = [ROSE, ASH, SAFFRON, IRIS]

    x = np.arange(len(tiers))
    bars = ax.bar(x, counts, color=colors, width=0.52, edgecolor=HAIRLINE)
    ax.set_xticks(x)
    ax.set_xticklabels(tiers, fontsize=10, fontweight="bold", color=WHITE)
    ax.set_ylabel("Clean Catalog Count (N=3,931)", fontsize=10, color=ASH)
    ax.set_title("Financial Success Tier Breakdown", fontsize=13, fontweight="bold", pad=12, color=WHITE)
    ax.grid(axis="y", alpha=0.3)

    for bar, count, pct in zip(bars, counts, percentages):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 25, f"{count}\n({pct:.1f}%)",
                 ha='center', va='bottom', fontsize=9.5, fontweight="bold", color=WHITE)
    ax.set_ylim(0, 1350)

    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, "tier_distribution.png")
    fig.savefig(path, bbox_inches="tight", facecolor=VOID_BG)
    plt.close(fig)
    print("[Chart] Generated:", path)

# CHART 3: Model Benchmark Comparison (R² & Pearson r)
def generate_model_benchmark():
    fig, ax = plt.subplots(figsize=(8.2, 4.2), dpi=300)
    fig.patch.set_facecolor(VOID_BG)

    models = ["Ridge (Baseline)", "XGBoost (Baseline)", "XGBoost (Champion Tuned)", "CatBoost (Benchmark)"]
    r2_scores = [0.4021, 0.3332, 0.3747, 0.3943]
    pearson_r = [0.6536, 0.6070, 0.6267, 0.6410]

    x = np.arange(len(models))
    width = 0.35

    rects1 = ax.bar(x - width/2, r2_scores, width, label='Test R² (Log USD)', color=IRIS, edgecolor=HAIRLINE)
    rects2 = ax.bar(x + width/2, pearson_r, width, label='Pearson Correlation (r)', color=SAFFRON, edgecolor=HAIRLINE)

    ax.set_ylabel('Score Metric', fontsize=11, color=ASH)
    ax.set_title('Test Set Benchmark: Clean Pre-Release Features (N=383)', fontsize=13, fontweight="bold", pad=12, color=WHITE)
    ax.set_xticks(x)
    ax.set_xticklabels(models, fontsize=10, fontweight="bold", color=WHITE)
    ax.legend(facecolor=PANEL_BG, edgecolor=HAIRLINE, labelcolor=WHITE, fontsize=10)
    ax.grid(axis="y", alpha=0.3)

    for r in rects1:
        h = r.get_height()
        ax.text(r.get_x() + r.get_width()/2, h + 0.015, f"{h:.3f}", ha='center', va='bottom', fontsize=9, fontweight="bold", color=WHITE)
    for r in rects2:
        h = r.get_height()
        ax.text(r.get_x() + r.get_width()/2, h + 0.015, f"{h:.3f}", ha='center', va='bottom', fontsize=9, fontweight="bold", color=WHITE)

    ax.set_ylim(0, 0.78)

    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, "model_benchmark.png")
    fig.savefig(path, bbox_inches="tight", facecolor=VOID_BG)
    plt.close(fig)
    print("[Chart] Generated:", path)

# CHART 4: Leakage Ablation Study (Pre-Release vs Early-Signal)
def generate_ablation_chart():
    fig, ax = plt.subplots(figsize=(7.8, 4.2), dpi=300)
    fig.patch.set_facecolor(VOID_BG)

    models = ["Ridge Regression", "XGBoost Regressor", "CatBoost Regressor"]
    clean_r = [0.6536, 0.6070, 0.6410]
    early_signal_r = [0.6514, 0.6595, 0.6939]

    x = np.arange(len(models))
    width = 0.32

    rects1 = ax.bar(x - width/2, clean_r, width, label='Pre-Release Clean (34 feats)', color=VERDANT, edgecolor=HAIRLINE)
    rects2 = ax.bar(x + width/2, early_signal_r, width, label='Early-Signal +Popularity (40 feats)', color=ROSE, edgecolor=HAIRLINE)

    ax.set_ylabel('Pearson Correlation (r)', fontsize=11, color=ASH)
    ax.set_title('Target Leakage Ablation: Inflation via Post-Release Signals', fontsize=13, fontweight="bold", pad=12, color=WHITE)
    ax.set_xticks(x)
    ax.set_xticklabels(models, fontsize=10, fontweight="bold", color=WHITE)
    ax.legend(facecolor=PANEL_BG, edgecolor=HAIRLINE, labelcolor=WHITE, fontsize=9.5)
    ax.grid(axis="y", alpha=0.3)

    for r in rects1:
        h = r.get_height()
        ax.text(r.get_x() + r.get_width()/2, h + 0.015, f"{h:.3f}", ha='center', va='bottom', fontsize=9, fontweight="bold", color=WHITE)
    for r in rects2:
        h = r.get_height()
        ax.text(r.get_x() + r.get_width()/2, h + 0.015, f"{h:.3f}", ha='center', va='bottom', fontsize=9, fontweight="bold", color=WHITE)

    ax.set_ylim(0, 0.82)

    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, "ablation_comparison.png")
    fig.savefig(path, bbox_inches="tight", facecolor=VOID_BG)
    plt.close(fig)
    print("[Chart] Generated:", path)

# CHART 5: SHAP Global Feature Importance
def generate_shap_chart():
    fig, ax = plt.subplots(figsize=(7.5, 4.4), dpi=300)
    fig.patch.set_facecolor(VOID_BG)

    features = [
        "Production Budget",
        "Release Year (Inflation)",
        "Studio Prior Film Count",
        "Release Day of Week",
        "Movie Runtime",
        "Log Production Budget",
        "Genre: Action",
        "Studio Prior Avg Revenue",
        "Genre: Drama",
        "Production Company Count"
    ][::-1]

    shap_vals = [0.8368, 0.7494, 0.1975, 0.1852, 0.1822, 0.1053, 0.0955, 0.0813, 0.0722, 0.0625][::-1]

    y_pos = np.arange(len(features))
    colors = [IRIS if i >= 8 else (SAFFRON if i >= 5 else VERDANT) for i in range(len(features))]

    bars = ax.barh(y_pos, shap_vals, color=colors, height=0.6, edgecolor=HAIRLINE)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(features, fontsize=9.5, fontweight="bold", color=WHITE)
    ax.set_xlabel('Mean |SHAP Value| (Impact on Log USD Revenue)', fontsize=10, color=ASH)
    ax.set_title('Top 10 Pre-Release Value Drivers (TreeExplainer)', fontsize=13, fontweight="bold", pad=12, color=WHITE)
    ax.grid(axis="x", alpha=0.3)

    for bar, val in zip(bars, shap_vals):
        ax.text(bar.get_width() + 0.015, bar.get_y() + bar.get_height()/2, f"+{val:.3f}",
                 va='center', ha='left', fontsize=9, fontweight="bold", color=WHITE)

    ax.set_xlim(0, 0.98)

    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, "shap_importance.png")
    fig.savefig(path, bbox_inches="tight", facecolor=VOID_BG)
    plt.close(fig)
    print("[Chart] Generated:", path)

# --- 3. GENERATE REPO QR CODE ---
def generate_repo_qrcode():
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    repo_url = "https://github.com/prathamraval33/ml-project"
    qr.add_data(repo_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#8052FF", back_color="#0B0D17")
    path = os.path.join(ASSETS_DIR, "repo_qrcode.png")
    img.save(path)
    print("[QR] Generated repository QR code:", path)

if __name__ == "__main__":
    generate_audit_chart()
    generate_tier_distribution()
    generate_model_benchmark()
    generate_ablation_chart()
    generate_shap_chart()
    generate_repo_qrcode()
    print("All presentation assets created successfully!")
