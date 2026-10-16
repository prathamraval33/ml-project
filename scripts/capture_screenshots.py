import subprocess
import time
import os

BASE_DIR = r"c:\Users\DC\OneDrive\Desktop\practice\ml project"
ASSETS_DIR = os.path.join(BASE_DIR, "presentation_assets")
STORE_FILE = os.path.join(BASE_DIR, r"frontend\src\store\useUiStore.js")
EDGE_EXE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

def capture_tab(tab_name, filename):
    with open(STORE_FILE, "r", encoding="utf-8") as f:
        code = f.read()
    
    # replace activeTab
    import re
    new_code = re.sub(r"activeTab:\s*['\"][^'\"]+['\"]", f"activeTab: '{tab_name}'", code)
    with open(STORE_FILE, "w", encoding="utf-8") as f:
        f.write(new_code)
    
    time.sleep(2) # wait for Vite HMR
    
    out_path = os.path.join(ASSETS_DIR, filename)
    cmd = [
        EDGE_EXE,
        "--headless=new",
        "--disable-gpu",
        "--virtual-time-budget=6000",
        "--window-size=1600,1000",
        f"--screenshot={out_path}",
        "http://localhost:5173"
    ]
    subprocess.run(cmd)
    print(f"Captured {tab_name} -> {filename}, exists: {os.path.exists(out_path)}, size: {os.path.getsize(out_path) if os.path.exists(out_path) else 0}")

if __name__ == "__main__":
    capture_tab("whatif", "dashboard_whatif.png")
    capture_tab("explorer", "dashboard_explorer.png")
    capture_tab("overview", "dashboard_overview.png")
    print("Screenshots captured successfully!")
