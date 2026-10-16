"""
CineForecast – Simplified Presentation Generator
Generates a visually rich .pptx deck using plain, simple language.
"""

import os, json, math
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from PIL import Image

# ── paths ──────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE, "presentation_assets")
CHARTS = os.path.join(ASSETS, "charts")
LOGOS  = os.path.join(ASSETS, "logos")
OUT    = os.path.join(BASE, "cineforecast_simple.pptx")

# ── brand colours ──────────────────────────────────────────────────────
BG_DARK    = RGBColor(0x0D, 0x0D, 0x1A)   # deep navy-black
BG_CARD    = RGBColor(0x16, 0x16, 0x2B)   # slightly lighter card
ACCENT     = RGBColor(0x7C, 0x3A, 0xED)   # vivid purple
ACCENT_LT  = RGBColor(0xA7, 0x8B, 0xFA)   # lighter purple
GOLD       = RGBColor(0xFA, 0xCC, 0x15)   # warm gold
TEAL       = RGBColor(0x2D, 0xD4, 0xBF)   # teal green
CORAL      = RGBColor(0xF4, 0x72, 0x5C)   # coral red
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
GRAY       = RGBColor(0x9C, 0xA3, 0xAF)
LIGHT_GRAY = RGBColor(0xD1, 0xD5, 0xDB)

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

# ── helper functions ───────────────────────────────────────────────────

def set_slide_bg(slide, color):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_rounded_rect(slide, left, top, width, height, fill_color, border_color=None):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if border_color:
        shape.line.fill.solid()
        shape.line.fill.fore_color.rgb = border_color
        shape.line.width = Pt(1.5)
    else:
        shape.line.fill.background()
    return shape

def add_text_box(slide, left, top, width, height, text, font_size=18,
                 color=WHITE, bold=False, alignment=PP_ALIGN.LEFT,
                 font_name="Calibri"):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = color
    p.font.bold = bold
    p.font.name = font_name
    p.alignment = alignment
    return txBox

def add_multi_text(slide, left, top, width, height, lines, default_size=16,
                   default_color=LIGHT_GRAY, font_name="Calibri"):
    """lines = list of (text, size, color, bold, alignment)"""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, item in enumerate(lines):
        text = item[0]
        size = item[1] if len(item) > 1 else default_size
        color = item[2] if len(item) > 2 else default_color
        bold = item[3] if len(item) > 3 else False
        align = item[4] if len(item) > 4 else PP_ALIGN.LEFT
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = text
        p.font.size = Pt(size)
        p.font.color.rgb = color
        p.font.bold = bold
        p.font.name = font_name
        p.alignment = align
        p.space_after = Pt(4)
    return txBox

def add_accent_line(slide, left, top, width, color=ACCENT):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, left, top, width, Pt(4)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape

def add_circle_badge(slide, left, top, size, fill_color, text, font_size=12,
                     text_color=WHITE):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.OVAL, left, top, size, size
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    shape.line.fill.background()
    tf = shape.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = text_color
    p.font.bold = True
    p.font.name = "Calibri"
    p.alignment = PP_ALIGN.CENTER
    tf.paragraphs[0].space_before = Pt(0)
    return shape

def safe_add_image(slide, path, left, top, width=None, height=None):
    if os.path.exists(path):
        kwargs = {"image_file": path, "left": left, "top": top}
        if width:
            kwargs["width"] = width
        if height:
            kwargs["height"] = height
        return slide.shapes.add_picture(**kwargs)
    return None

# ── create presentation ───────────────────────────────────────────────
prs = Presentation()
prs.slide_width = SLIDE_W
prs.slide_height = SLIDE_H
blank_layout = prs.slide_layouts[6]  # blank

# ══════════════════════════════════════════════════════════════════════
# SLIDE 1 – TITLE
# ══════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(blank_layout)
set_slide_bg(sl, BG_DARK)

# Gradient-like accent strip at top
add_rounded_rect(sl, Inches(0), Inches(0), SLIDE_W, Inches(0.08), ACCENT)

# Big title
add_text_box(sl, Inches(1), Inches(1.5), Inches(11), Inches(1.2),
             "🎬 CineForecast", font_size=52, color=WHITE, bold=True,
             alignment=PP_ALIGN.CENTER, font_name="Calibri")

# Tagline – SIMPLE language
add_text_box(sl, Inches(1.5), Inches(2.9), Inches(10), Inches(0.8),
             "Predicting How Much Money a Movie Will Make — Before It Even Releases",
             font_size=24, color=ACCENT_LT, bold=False,
             alignment=PP_ALIGN.CENTER)

# Divider
add_accent_line(sl, Inches(5), Inches(4.0), Inches(3.3), ACCENT)

# Author & course info
add_multi_text(sl, Inches(2), Inches(4.4), Inches(9), Inches(2.2), [
    ("A Machine Learning Project", 20, GOLD, True, PP_ALIGN.CENTER),
    ("", 8, GRAY, False, PP_ALIGN.CENTER),
    ("Built with Python · XGBoost · FastAPI · React", 16, GRAY, False, PP_ALIGN.CENTER),
    ("Data Source: TMDB Movie Database  ·  3,931 Movies  ·  1990 – 2025", 14, GRAY, False, PP_ALIGN.CENTER),
])

# ══════════════════════════════════════════════════════════════════════
# SLIDE 2 – WHAT THIS PROJECT IS ABOUT (Agenda / Outline)
# ══════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(blank_layout)
set_slide_bg(sl, BG_DARK)

add_text_box(sl, Inches(0.6), Inches(0.4), Inches(12), Inches(0.8),
             "What This Project Covers", font_size=36, color=WHITE, bold=True)
add_accent_line(sl, Inches(0.6), Inches(1.15), Inches(3), ACCENT)

# Roadmap items as numbered cards
items = [
    ("1", "The Problem",     "Why is predicting movie earnings hard?", ACCENT),
    ("2", "The Data",        "Where our movie data comes from & how we cleaned it", TEAL),
    ("3", "The Models",      "Three ML models we tried and compared", CORAL),
    ("4", "How It Works",    "Step-by-step flow from raw data to prediction", GOLD),
    ("5", "Results",         "How well our models performed on unseen movies", ACCENT_LT),
    ("6", "The Dashboard",   "Interactive web app to explore predictions", TEAL),
    ("7", "Key Takeaways",   "What we learned & what comes next", CORAL),
]

card_w = Inches(1.55)
card_h = Inches(4.5)
start_x = Inches(0.5)
gap = Inches(0.28)

for i, (num, title, desc, color) in enumerate(items):
    x = start_x + i * (card_w + gap)
    y = Inches(1.7)
    card = add_rounded_rect(sl, x, y, card_w, card_h, BG_CARD, color)

    # Number circle
    add_circle_badge(sl, x + Inches(0.45), y + Inches(0.3), Inches(0.6),
                     color, num, 22, WHITE)

    # Title
    add_text_box(sl, x + Inches(0.1), y + Inches(1.15), Inches(1.35), Inches(0.7),
                 title, font_size=16, color=WHITE, bold=True,
                 alignment=PP_ALIGN.CENTER)

    # Description
    add_text_box(sl, x + Inches(0.1), y + Inches(1.9), Inches(1.35), Inches(2.2),
                 desc, font_size=12, color=GRAY,
                 alignment=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════════════════
# SLIDE 3 – THE PROBLEM
# ══════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(blank_layout)
set_slide_bg(sl, BG_DARK)

add_text_box(sl, Inches(0.6), Inches(0.4), Inches(12), Inches(0.8),
             "The Problem: Can We Predict a Movie's Earnings?", font_size=32,
             color=WHITE, bold=True)
add_accent_line(sl, Inches(0.6), Inches(1.1), Inches(4.5), ACCENT)

# Left side – problem explanation
add_multi_text(sl, Inches(0.6), Inches(1.5), Inches(5.8), Inches(5), [
    ("Why is this hard?", 22, GOLD, True),
    ("", 6, GRAY, False),
    ("• Movies can cost millions but still flop at the box office", 16, LIGHT_GRAY, False),
    ("• There are many factors: budget, actors, genre, release date…", 16, LIGHT_GRAY, False),
    ("• No one knows for sure how audiences will react", 16, LIGHT_GRAY, False),
    ("• Studios need better tools to estimate returns early on", 16, LIGHT_GRAY, False),
    ("", 10, GRAY, False),
    ("What we built:", 22, TEAL, True),
    ("", 6, GRAY, False),
    ("A system that uses past movie data to predict:", 16, LIGHT_GRAY, False),
    ("  1. How much revenue a movie will likely earn", 15, WHITE, False),
    ("  2. Whether it will be a Flop, Break-Even, Hit, or Blockbuster", 15, WHITE, False),
    ("  3. Which factors matter most for success", 15, WHITE, False),
])

# Right side – Tier cards
tier_data = [
    ("💔 Flop",       "Lost money\n(Revenue < Budget)", CORAL),
    ("⚖️ Break-Even", "Just covered costs\n(1x – 2x return)", GRAY),
    ("🎯 Hit",        "Good profit\n(2x – 4x return)", TEAL),
    ("🚀 Blockbuster","Massive success\n(4x+ return)", GOLD),
]

right_x = Inches(7.2)
for i, (label, desc, color) in enumerate(tier_data):
    y = Inches(1.6) + i * Inches(1.35)
    card = add_rounded_rect(sl, right_x, y, Inches(5.5), Inches(1.15), BG_CARD, color)
    add_text_box(sl, right_x + Inches(0.3), y + Inches(0.1), Inches(2.2), Inches(0.9),
                 label, font_size=20, color=color, bold=True)
    add_text_box(sl, right_x + Inches(2.5), y + Inches(0.15), Inches(2.8), Inches(0.85),
                 desc, font_size=13, color=LIGHT_GRAY)


# ══════════════════════════════════════════════════════════════════════
# SLIDE 4 – THE DATA
# ══════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(blank_layout)
set_slide_bg(sl, BG_DARK)

add_text_box(sl, Inches(0.6), Inches(0.4), Inches(12), Inches(0.8),
             "The Data: From Messy to Clean", font_size=32,
             color=WHITE, bold=True)
add_accent_line(sl, Inches(0.6), Inches(1.1), Inches(3.5), TEAL)

# Left – explanation
add_multi_text(sl, Inches(0.6), Inches(1.5), Inches(5.5), Inches(5.5), [
    ("Where the data came from", 20, GOLD, True),
    ("", 4, GRAY, False),
    ("• TMDB (The Movie Database) — a public movie database", 15, LIGHT_GRAY, False),
    ("• Started with 9,999 movie records from 1990 to 2025", 15, LIGHT_GRAY, False),
    ("", 8, GRAY, False),
    ("Problems we found", 20, CORAL, True),
    ("", 4, GRAY, False),
    ("• 47.7% of movies had no budget information", 15, LIGHT_GRAY, False),
    ("• 44.3% had no revenue information", 15, LIGHT_GRAY, False),
    ("• 232 duplicate entries", 15, LIGHT_GRAY, False),
    ("• Some dates were in the future (bad data)", 15, LIGHT_GRAY, False),
    ("", 8, GRAY, False),
    ("After cleaning", 20, TEAL, True),
    ("", 4, GRAY, False),
    ("• 3,931 movies with complete, reliable data", 15, WHITE, True),
    ("• Training set: 1990–2022 (3,548 movies)", 14, LIGHT_GRAY, False),
    ("• Test set: 2023–2025 (383 movies, never seen during training)", 14, LIGHT_GRAY, False),
])

# Right – funnel chart
safe_add_image(sl, os.path.join(CHARTS, "data_audit_funnel.png"),
               Inches(6.8), Inches(1.3), width=Inches(6))


# ══════════════════════════════════════════════════════════════════════
# SLIDE 5 – THE FEATURES (What Info We Used)
# ══════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(blank_layout)
set_slide_bg(sl, BG_DARK)

add_text_box(sl, Inches(0.6), Inches(0.4), Inches(12), Inches(0.8),
             "What Information Did We Feed the Model?", font_size=32,
             color=WHITE, bold=True)
add_accent_line(sl, Inches(0.6), Inches(1.1), Inches(4), GOLD)

add_text_box(sl, Inches(0.6), Inches(1.4), Inches(12), Inches(0.6),
             "We only used information available BEFORE a movie releases — no cheating!",
             font_size=17, color=ACCENT_LT, bold=True)

# Feature category cards
feature_cats = [
    ("💰 Money",
     "• Production budget\n• Budget (log scale)\n  → How much was spent making the movie",
     GOLD),
    ("🎭 Genre",
     "• Action, Drama, Comedy, Sci-Fi…\n• 15+ genre flags\n  → What type of movie is it",
     ACCENT),
    ("📅 Timing",
     "• Release month, day, quarter\n• Holiday release? Summer?\n  → When the movie hits theaters",
     TEAL),
    ("🎬 Track Record",
     "• Director's past avg. earnings\n• Studio's past avg. earnings\n• Number of past films\n  → How experienced is the team",
     CORAL),
    ("📊 Other Details",
     "• Runtime (movie length)\n• Cast size\n• Is it a franchise/sequel?\n• International co-production?",
     ACCENT_LT),
    ("🔢 Total Features",
     "34 pre-release features\n\nAll carefully chosen to\navoid data leakage\n(no post-release info)",
     RGBColor(0x60, 0xA5, 0xFA)),
]

card_w = Inches(3.8)
card_h = Inches(2.1)
for i, (title, desc, color) in enumerate(feature_cats):
    col = i % 3
    row = i // 3
    x = Inches(0.6) + col * (card_w + Inches(0.35))
    y = Inches(2.2) + row * (card_h + Inches(0.3))

    card = add_rounded_rect(sl, x, y, card_w, card_h, BG_CARD, color)
    add_text_box(sl, x + Inches(0.2), y + Inches(0.15), card_w - Inches(0.4), Inches(0.5),
                 title, font_size=17, color=color, bold=True)
    add_text_box(sl, x + Inches(0.2), y + Inches(0.6), card_w - Inches(0.4), card_h - Inches(0.8),
                 desc, font_size=12, color=LIGHT_GRAY)


# ══════════════════════════════════════════════════════════════════════
# SLIDE 6 – THE MODELS WE TRIED
# ══════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(blank_layout)
set_slide_bg(sl, BG_DARK)

add_text_box(sl, Inches(0.6), Inches(0.4), Inches(12), Inches(0.8),
             "The Models: Three Approaches Compared", font_size=32,
             color=WHITE, bold=True)
add_accent_line(sl, Inches(0.6), Inches(1.1), Inches(4), ACCENT)

# Three model cards
models = [
    ("Ridge Regression",
     "The Simple One",
     "A basic linear model.\nGood starting point\nto see how a simple\napproach performs.",
     "R² = 0.40  |  r = 0.65",
     TEAL, "🏔️"),
    ("CatBoost",
     "The Smart Competitor",
     "A tree-based model from\nYandex. Good at handling\ndifferent types of data\nautomatically.",
     "R² = 0.39  |  r = 0.64",
     CORAL, "🐱"),
    ("XGBoost ★ Winner",
     "Our Best Model",
     "A powerful tree-based model\nfine-tuned with Optuna.\nBest overall balance of\naccuracy and reliability.",
     "R² = 0.37  |  r = 0.63",
     GOLD, "🏆"),
]

model_w = Inches(3.8)
model_h = Inches(4.8)
for i, (name, subtitle, desc, metrics, color, emoji) in enumerate(models):
    x = Inches(0.6) + i * (model_w + Inches(0.4))
    y = Inches(1.5)

    card = add_rounded_rect(sl, x, y, model_w, model_h, BG_CARD, color)

    # Emoji badge
    add_text_box(sl, x + Inches(1.2), y + Inches(0.2), Inches(1.4), Inches(0.7),
                 emoji, font_size=36, alignment=PP_ALIGN.CENTER)

    # Model name
    add_text_box(sl, x + Inches(0.2), y + Inches(0.9), model_w - Inches(0.4), Inches(0.5),
                 name, font_size=20, color=WHITE, bold=True,
                 alignment=PP_ALIGN.CENTER)

    # Subtitle
    add_text_box(sl, x + Inches(0.2), y + Inches(1.4), model_w - Inches(0.4), Inches(0.4),
                 subtitle, font_size=14, color=color, bold=True,
                 alignment=PP_ALIGN.CENTER)

    # Description
    add_text_box(sl, x + Inches(0.3), y + Inches(2.0), model_w - Inches(0.6), Inches(1.5),
                 desc, font_size=14, color=LIGHT_GRAY,
                 alignment=PP_ALIGN.CENTER)

    # Metrics bar
    bar = add_rounded_rect(sl, x + Inches(0.2), y + Inches(3.7),
                           model_w - Inches(0.4), Inches(0.7), color)
    add_text_box(sl, x + Inches(0.2), y + Inches(3.78),
                 model_w - Inches(0.4), Inches(0.55),
                 metrics, font_size=13, color=BG_DARK, bold=True,
                 alignment=PP_ALIGN.CENTER)

# Footnote
add_text_box(sl, Inches(0.6), Inches(6.7), Inches(12), Inches(0.5),
             "R² = how much of the variation in earnings the model explains  |  r = how closely predictions match actual values  |  Higher = Better",
             font_size=12, color=GRAY, alignment=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════════════════
# SLIDE 7 – HOW IT ALL WORKS (Pipeline)
# ══════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(blank_layout)
set_slide_bg(sl, BG_DARK)

add_text_box(sl, Inches(0.6), Inches(0.4), Inches(12), Inches(0.8),
             "How It All Works: Step by Step", font_size=32,
             color=WHITE, bold=True)
add_accent_line(sl, Inches(0.6), Inches(1.1), Inches(3.5), TEAL)

# Pipeline steps as horizontal flow
steps = [
    ("1", "Get Raw Data",      "Download 9,999\nmovie records\nfrom TMDB",        ACCENT),
    ("2", "Clean & Filter",     "Remove bad data\nkeep 3,931\nreliable movies",   TEAL),
    ("3", "Build Features",     "Create 34 useful\ninputs from the\nraw movie info", GOLD),
    ("4", "Train Models",       "Teach 3 models\nusing movies\nfrom 1990-2022",    CORAL),
    ("5", "Test & Compare",     "Test on 383\nnew movies\nfrom 2023-2025",         ACCENT_LT),
    ("6", "Deploy & Serve",     "Serve predictions\nthrough API &\nweb dashboard",   RGBColor(0x60, 0xA5, 0xFA)),
]

step_w = Inches(1.75)
step_h = Inches(3.4)
start_x = Inches(0.4)
gap = Inches(0.28)

for i, (num, title, desc, color) in enumerate(steps):
    x = start_x + i * (step_w + gap)
    y = Inches(1.6)

    # Card
    card = add_rounded_rect(sl, x, y, step_w, step_h, BG_CARD, color)

    # Step number
    add_circle_badge(sl, x + Inches(0.5), y + Inches(0.2), Inches(0.7),
                     color, num, 24, WHITE)

    # Title
    add_text_box(sl, x + Inches(0.1), y + Inches(1.1), step_w - Inches(0.2), Inches(0.5),
                 title, font_size=15, color=WHITE, bold=True,
                 alignment=PP_ALIGN.CENTER)

    # Description
    add_text_box(sl, x + Inches(0.1), y + Inches(1.7), step_w - Inches(0.2), Inches(1.5),
                 desc, font_size=12, color=GRAY,
                 alignment=PP_ALIGN.CENTER)

    # Arrow between steps
    if i < len(steps) - 1:
        arrow_x = x + step_w + Inches(0.02)
        add_text_box(sl, arrow_x, y + Inches(1.2), Inches(0.25), Inches(0.5),
                     "→", font_size=24, color=color, bold=True,
                     alignment=PP_ALIGN.CENTER)

# Tech stack row at bottom
add_text_box(sl, Inches(0.6), Inches(5.4), Inches(12), Inches(0.5),
             "Tools & Technologies Used", font_size=18, color=WHITE, bold=True)
add_accent_line(sl, Inches(0.6), Inches(5.85), Inches(2.5), GOLD)

tech_items = [
    ("python.png",    "Python"),
    ("xgboost.png",   "XGBoost"),
    ("catboost.png",  "CatBoost"),
    ("scikitlearn.png","Scikit-Learn"),
    ("optuna.png",    "Optuna"),
    ("shap.png",      "SHAP"),
    ("fastapi.png",   "FastAPI"),
    ("react.png",     "React"),
    ("vite.png",      "Vite"),
    ("sqlite.png",    "SQLite"),
]

for i, (logo_file, label) in enumerate(tech_items):
    x = Inches(0.5) + i * Inches(1.25)
    y_logo = Inches(6.1)
    logo_path = os.path.join(LOGOS, logo_file)
    safe_add_image(sl, logo_path, x + Inches(0.15), y_logo, width=Inches(0.55), height=Inches(0.55))
    add_text_box(sl, x, y_logo + Inches(0.6), Inches(0.9), Inches(0.3),
                 label, font_size=9, color=GRAY, alignment=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════════════════
# SLIDE 8 – RESULTS
# ══════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(blank_layout)
set_slide_bg(sl, BG_DARK)

add_text_box(sl, Inches(0.6), Inches(0.4), Inches(12), Inches(0.8),
             "Results: How Good Are Our Predictions?", font_size=32,
             color=WHITE, bold=True)
add_accent_line(sl, Inches(0.6), Inches(1.1), Inches(4), GOLD)

# Left – chart
safe_add_image(sl, os.path.join(CHARTS, "model_benchmark.png"),
               Inches(0.4), Inches(1.5), width=Inches(6.2))

# Right – key findings in simple language
add_multi_text(sl, Inches(7), Inches(1.4), Inches(5.8), Inches(5.5), [
    ("What the numbers mean", 22, GOLD, True),
    ("", 6, GRAY, False),
    ("Our best model (XGBoost) can explain about", 15, LIGHT_GRAY, False),
    ("37% of the variation in movie earnings.", 16, WHITE, True),
    ("", 6, GRAY, False),
    ("That may sound low, but predicting movie", 15, LIGHT_GRAY, False),
    ("revenue is extremely hard — even experts", 15, LIGHT_GRAY, False),
    ("at studios often get it wrong!", 15, LIGHT_GRAY, False),
    ("", 10, GRAY, False),
    ("Key findings:", 20, TEAL, True),
    ("", 4, GRAY, False),
    ("✅ Budget is the #1 predictor of revenue", 15, LIGHT_GRAY, False),
    ("✅ Release year matters a lot (inflation effect)", 15, LIGHT_GRAY, False),
    ("✅ Studio track record is important", 15, LIGHT_GRAY, False),
    ("✅ Action genre movies tend to earn more", 15, LIGHT_GRAY, False),
    ("✅ Ridge Regression actually beat XGBoost on R²!", 15, LIGHT_GRAY, False),
    ("", 10, GRAY, False),
    ("Tested on 383 movies the model never saw", 14, ACCENT_LT, True),
    ("during training (released 2023–2025)", 14, ACCENT_LT, False),
])

# ══════════════════════════════════════════════════════════════════════
# SLIDE 9 – WHAT DRIVES PREDICTIONS (SHAP)
# ══════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(blank_layout)
set_slide_bg(sl, BG_DARK)

add_text_box(sl, Inches(0.6), Inches(0.4), Inches(12), Inches(0.8),
             "What Matters Most? Top Factors That Drive Revenue",
             font_size=30, color=WHITE, bold=True)
add_accent_line(sl, Inches(0.6), Inches(1.1), Inches(4.5), ACCENT)

add_text_box(sl, Inches(0.6), Inches(1.35), Inches(12), Inches(0.5),
             "We used SHAP (a method to explain AI decisions) to find which features push predictions up or down",
             font_size=15, color=GRAY)

# Left – SHAP chart
safe_add_image(sl, os.path.join(CHARTS, "shap_importance.png"),
               Inches(0.4), Inches(2.0), width=Inches(6.3))

# Right – simple explanation of top features
top_features = [
    ("💰 Budget",              "The most important factor. Higher budget → higher expected earnings", GOLD),
    ("📅 Release Year",        "More recent movies tend to earn more (inflation + bigger markets)", ACCENT_LT),
    ("🏢 Studio Experience",   "Studios with more past films tend to produce higher-earning movies", TEAL),
    ("📆 Release Day",         "The day of the week a movie opens affects opening weekend sales", CORAL),
    ("⏱️ Runtime",             "Movie length plays a surprising role in predicting earnings", ACCENT),
]

for i, (feat, explanation, color) in enumerate(top_features):
    y = Inches(2.0) + i * Inches(1.05)
    card = add_rounded_rect(sl, Inches(7), y, Inches(5.8), Inches(0.9), BG_CARD, color)
    add_text_box(sl, Inches(7.2), y + Inches(0.05), Inches(5.4), Inches(0.35),
                 feat, font_size=15, color=color, bold=True)
    add_text_box(sl, Inches(7.2), y + Inches(0.4), Inches(5.4), Inches(0.45),
                 explanation, font_size=12, color=LIGHT_GRAY)

# ══════════════════════════════════════════════════════════════════════
# SLIDE 10 – THE DASHBOARD
# ══════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(blank_layout)
set_slide_bg(sl, BG_DARK)

add_text_box(sl, Inches(0.6), Inches(0.4), Inches(12), Inches(0.8),
             "The Dashboard: Explore Movies Visually", font_size=32,
             color=WHITE, bold=True)
add_accent_line(sl, Inches(0.6), Inches(1.1), Inches(3.5), TEAL)

# Dashboard screenshots
screenshots = [
    ("dashboard_overview.png",  "Overview Page\nSee all movies at a glance"),
    ("dashboard_explorer.png",  "Movie Explorer\nDig into individual predictions"),
    ("dashboard_whatif.png",    "What-If Simulator\nChange inputs & see impact"),
]

for i, (img_file, caption) in enumerate(screenshots):
    x = Inches(0.5) + i * Inches(4.3)
    y = Inches(1.5)
    img_path = os.path.join(ASSETS, img_file)
    safe_add_image(sl, img_path, x, y, width=Inches(3.9))

    add_text_box(sl, x, Inches(5.2), Inches(3.9), Inches(0.9),
                 caption, font_size=14, color=LIGHT_GRAY,
                 alignment=PP_ALIGN.CENTER)

# Feature bullets at bottom
add_multi_text(sl, Inches(0.6), Inches(6.0), Inches(12), Inches(1.2), [
    ("Dashboard Features:", 16, GOLD, True),
    ("📊 Scatter plots showing predicted vs actual earnings  •  🔍 Search & filter any movie  •  🔬 SHAP explanations for every prediction  •  🎮 What-If simulator to test scenarios", 13, GRAY, False),
])


# ══════════════════════════════════════════════════════════════════════
# SLIDE 11 – LIMITATIONS & FUTURE WORK
# ══════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(blank_layout)
set_slide_bg(sl, BG_DARK)

add_text_box(sl, Inches(0.6), Inches(0.4), Inches(12), Inches(0.8),
             "What We Learned & What Comes Next", font_size=32,
             color=WHITE, bold=True)
add_accent_line(sl, Inches(0.6), Inches(1.1), Inches(3.5), ACCENT)

# Left column – Limitations
add_rounded_rect(sl, Inches(0.6), Inches(1.5), Inches(5.8), Inches(5.2), BG_CARD, CORAL)
add_text_box(sl, Inches(0.9), Inches(1.7), Inches(5.2), Inches(0.5),
             "⚠️ Current Limitations", font_size=22, color=CORAL, bold=True)

limitations = [
    "• Almost half the original data had missing budget/revenue info",
    "• Model can't predict viral moments or unexpected events",
    "• Doesn't account for marketing spend (data not available)",
    "• Mostly US-focused; limited international movie data",
    "• Predictions are estimates, not guarantees!",
]
add_multi_text(sl, Inches(0.9), Inches(2.4), Inches(5.2), Inches(3.8),
               [(l, 15, LIGHT_GRAY, False) for l in limitations])

# Right column – Future work
add_rounded_rect(sl, Inches(7), Inches(1.5), Inches(5.8), Inches(5.2), BG_CARD, TEAL)
add_text_box(sl, Inches(7.3), Inches(1.7), Inches(5.2), Inches(0.5),
             "🚀 Future Improvements", font_size=22, color=TEAL, bold=True)

futures = [
    "• Add trailer analysis (use AI to analyze movie trailers)",
    "• Include social media buzz as a predictor",
    "• Break down predictions by country/region",
    "• Try deep learning models for better accuracy",
    "• Add real-time data updates as new movies release",
]
add_multi_text(sl, Inches(7.3), Inches(2.4), Inches(5.2), Inches(3.8),
               [(f, 15, LIGHT_GRAY, False) for f in futures])


# ══════════════════════════════════════════════════════════════════════
# SLIDE 12 – THANK YOU
# ══════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(blank_layout)
set_slide_bg(sl, BG_DARK)

add_rounded_rect(sl, Inches(0), Inches(0), SLIDE_W, Inches(0.08), ACCENT)

add_text_box(sl, Inches(1), Inches(1.8), Inches(11), Inches(1.2),
             "Thank You! 🎬", font_size=52, color=WHITE, bold=True,
             alignment=PP_ALIGN.CENTER)

add_text_box(sl, Inches(2), Inches(3.3), Inches(9), Inches(0.6),
             "CineForecast: Predicting Movie Revenue with Machine Learning",
             font_size=22, color=ACCENT_LT, alignment=PP_ALIGN.CENTER)

add_accent_line(sl, Inches(5), Inches(4.2), Inches(3.3), ACCENT)

# Summary stats
stats = [
    ("3,931", "Movies\nAnalyzed", GOLD),
    ("34", "Features\nUsed", TEAL),
    ("3", "Models\nCompared", CORAL),
    ("383", "Test\nMovies", ACCENT_LT),
]
for i, (num, label, color) in enumerate(stats):
    x = Inches(1.5) + i * Inches(2.8)
    y = Inches(4.6)
    add_circle_badge(sl, x, y, Inches(1.3), color, num, 28, WHITE)
    add_text_box(sl, x - Inches(0.3), y + Inches(1.45), Inches(1.9), Inches(0.7),
                 label, font_size=13, color=GRAY, alignment=PP_ALIGN.CENTER)

# QR code
qr_path = os.path.join(ASSETS, "repo_qrcode.png")
safe_add_image(sl, qr_path, Inches(11), Inches(5.5), width=Inches(1.5))
add_text_box(sl, Inches(10.5), Inches(7.0), Inches(2.5), Inches(0.4),
             "Scan for GitHub Repo", font_size=10, color=GRAY,
             alignment=PP_ALIGN.CENTER)


# ── save ───────────────────────────────────────────────────────────────
prs.save(OUT)
print(f"\n✅ Simplified presentation saved to:\n   {OUT}")
print(f"   Total slides: {len(prs.slides)}")
