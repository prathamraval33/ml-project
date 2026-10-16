import os
import comtypes.client

BASE_DIR = os.path.abspath(".")
PPTX_PATH = os.path.join(BASE_DIR, "cineforecast_presentation.pptx")
OUTPUT_DIR = os.path.join(BASE_DIR, "presentation_assets", "rendered_slides")

os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"Opening {PPTX_PATH} in PowerPoint...")
powerpoint = comtypes.client.CreateObject("PowerPoint.Application")
# Keep PowerPoint background / minimized
try:
    presentation = powerpoint.Presentations.Open(PPTX_PATH, WithWindow=False)
    # Save as PNG: ppSaveAsPNG = 17
    presentation.SaveAs(OUTPUT_DIR, 17)
    presentation.Close()
    print("Exported slides to:", OUTPUT_DIR)
except Exception as e:
    print("Export failed:", e)
finally:
    powerpoint.Quit()

# List exported files
files = os.listdir(OUTPUT_DIR)
print(f"Rendered {len(files)} slide images:")
for f in sorted(files):
    print(" -", f)
