import urllib.request
import subprocess
import os
import re

LOGOS_DIR = os.path.abspath("presentation_assets/logos")
os.makedirs(LOGOS_DIR, exist_ok=True)
EDGE_EXE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

def render_svg(name, svg_content, bg_color="transparent"):
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; }}
  html, body {{
    margin: 0; padding: 0; width: 256px; height: 256px;
    background: {bg_color};
    display: flex; align-items: center; justify-content: center;
    overflow: hidden;
  }}
  svg {{
    max-width: 190px; max-height: 190px; width: 100%; height: 100%;
  }}
</style>
</head>
<body>
  {svg_content}
</body>
</html>"""
    temp_html = os.path.join(LOGOS_DIR, f"temp_{name}.html")
    png_path = os.path.join(LOGOS_DIR, f"{name}.png")
    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(html)
    
    cmd = [
        EDGE_EXE, "--headless=new", "--disable-gpu",
        f"--screenshot={png_path}", "--window-size=256,256",
        "--default-background-color=00000000",
        f"file:///{temp_html}"
    ]
    subprocess.run(cmd, check=True)
    if os.path.exists(temp_html):
        os.remove(temp_html)
    print(f"Rendered {name}.png ({os.path.getsize(png_path)} bytes)")

if __name__ == "__main__":
    # 1. CatBoost official SVG
    try:
        cb_req = urllib.request.Request("https://catboost.ai/static/catboost-logo.svg", headers={"User-Agent": "Mozilla/5.0"})
        cb_svg = urllib.request.urlopen(cb_req, timeout=10).read().decode("utf-8")
        render_svg("catboost", cb_svg)
    except Exception as e:
        print("CatBoost failed:", e)

    # 2. Simple Icons with custom fills
    icons = {
        "python": "#3776AB",
        "fastapi": "#009688",
        "react": "#61DAFB",
        "vite": "#646CFF",
        "scikitlearn": "#F7931E",
        "tailwindcss": "#06B6D4",
        "sqlite": "#003B57",
        "github": "#FFFFFF"
    }

    for slug, fill_col in icons.items():
        try:
            u = f"https://cdn.jsdelivr.net/npm/simple-icons@v11/icons/{slug}.svg"
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
            svg = urllib.request.urlopen(req, timeout=10).read().decode("utf-8")
            if fill_col:
                if 'fill="' in svg:
                    svg = re.sub(r'fill="[^"]+"', f'fill="{fill_col}"', svg)
                else:
                    svg = svg.replace("<svg ", f'<svg fill="{fill_col}" ')
            render_svg(slug, svg)
        except Exception as e:
            print(f"Failed {slug}:", e)

    print("All logos processed!")
