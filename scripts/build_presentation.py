import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# --- COLOR PALETTE (Dark Void Design Tokens) ---
COLOR_VOID = RGBColor(11, 13, 23)        # #0B0D17 Canvas
COLOR_PANEL = RGBColor(18, 20, 34)       # #121422 Panel
COLOR_CARD = RGBColor(24, 27, 44)        # #181B2C Card
COLOR_HAIRLINE = RGBColor(38, 43, 68)    # #262B44 Border
COLOR_IRIS = RGBColor(128, 82, 255)      # #8052FF Primary Accent
COLOR_SAFFRON = RGBColor(255, 184, 41)   # #FFB829 Saffron Spark
COLOR_VERDANT = RGBColor(16, 185, 129)   # #10B981 Deep Verdant / Emerald
COLOR_ROSE = RGBColor(255, 92, 122)      # #FF5C7A Signal Rose
COLOR_WHITE = RGBColor(255, 255, 255)    # #FFFFFF Bone White
COLOR_ASH = RGBColor(148, 163, 184)      # #94A3B8 Ash Gray
COLOR_SILVER = RGBColor(203, 213, 225)   # #CBD5E1 Silver Mist

FONT_HEADING = "Arial"
FONT_BODY = "Arial"

ASSETS_DIR = os.path.abspath("presentation_assets")
LOGOS_DIR = os.path.join(ASSETS_DIR, "logos")
CHARTS_DIR = os.path.join(ASSETS_DIR, "charts")

def get_logo_path(name):
    p = os.path.join(LOGOS_DIR, f"{name}.png")
    return p if os.path.exists(p) else None

def get_chart_path(name):
    p = os.path.join(CHARTS_DIR, f"{name}.png")
    return p if os.path.exists(p) else None

def set_slide_background(slide):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = COLOR_VOID

def add_slide_header(slide, eyebrow, title, subtitle=None):
    # Eyebrow Pill
    eyebrow_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.42), Inches(10), Inches(0.35))
    tf_eye = eyebrow_box.text_frame
    tf_eye.word_wrap = True
    tf_eye.margin_left = tf_eye.margin_right = tf_eye.margin_top = tf_eye.margin_bottom = 0
    p_eye = tf_eye.paragraphs[0]
    p_eye.text = eyebrow.upper()
    p_eye.font.size = Pt(11)
    p_eye.font.bold = True
    p_eye.font.color.rgb = COLOR_IRIS
    p_eye.font.name = FONT_HEADING

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.72), Inches(11.7), Inches(0.65))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    tf_title.margin_left = tf_title.margin_right = tf_title.margin_top = tf_title.margin_bottom = 0
    p_title = tf_title.paragraphs[0]
    p_title.text = title
    p_title.font.size = Pt(28)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_WHITE
    p_title.font.name = FONT_HEADING

    # Subtitle
    if subtitle:
        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.38), Inches(11.7), Inches(0.38))
        tf_sub = sub_box.text_frame
        tf_sub.word_wrap = True
        tf_sub.margin_left = tf_sub.margin_right = tf_sub.margin_top = tf_sub.margin_bottom = 0
        p_sub = tf_sub.paragraphs[0]
        p_sub.text = subtitle
        p_sub.font.size = Pt(13)
        p_sub.font.color.rgb = COLOR_ASH
        p_sub.font.name = FONT_BODY

def add_card(slide, left, top, width, height, bg_color=COLOR_CARD, border_color=COLOR_HAIRLINE):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1)
    return shape

def set_notes(slide, notes_text):
    notes_slide = slide.notes_slide
    text_frame = notes_slide.notes_text_frame
    text_frame.text = notes_text

# ==========================================================
# SLIDE 1: TITLE SLIDE
# ==========================================================
def build_slide_1(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide)

    # Accent Top Line
    accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.8), Inches(1.5), Inches(0.06))
    accent.fill.solid()
    accent.fill.fore_color.rgb = COLOR_IRIS
    accent.line.fill.background()

    # Category Pill
    pill = add_card(slide, Inches(0.8), Inches(1.1), Inches(3.6), Inches(0.42), bg_color=COLOR_PANEL, border_color=COLOR_IRIS)
    tf = pill.text_frame
    p = tf.paragraphs[0]
    p.text = "PREDICTIVE ANALYTICS & APPLIED ML"
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_IRIS

    # Project Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.75), Inches(11.5), Inches(1.3))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = "CineForecast"
    p.font.size = Pt(54)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.font.name = FONT_HEADING

    # Tagline
    sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(3.05), Inches(11.5), Inches(0.8))
    tf = sub_box.text_frame
    p = tf.paragraphs[0]
    p.text = "Explainable Machine Learning for Pre-Release Film Revenue Forecasting & ROI Underwriting"
    p.font.size = Pt(19)
    p.font.color.rgb = COLOR_SAFFRON
    p.font.name = FONT_BODY

    # 4 Meta Cards
    meta_cards = [
        ("PROJECT LEAD / AUTHOR", "Pratham Raval", "ML Engineering & Architecture"),
        ("EVALUATION DATASET", "3,931 Clean TMDB Films", "Verified Pre-Release Financials"),
        ("CHAMPION ARCHITECTURE", "Optuna-Tuned XGBoost", "TreeExplainer SHAP Attribution"),
        ("PRODUCTION PLATFORM", "FastAPI + React 18", "Interactive What-If Studio")
    ]
    card_w = Inches(2.75)
    card_h = Inches(1.5)
    gap = Inches(0.25)
    start_x = Inches(0.8)
    top_y = Inches(4.15)

    for i, (k, v1, v2) in enumerate(meta_cards):
        cx = start_x + i * (card_w + gap)
        add_card(slide, cx, top_y, card_w, card_h, bg_color=COLOR_PANEL, border_color=COLOR_HAIRLINE)
        tb = slide.shapes.add_textbox(cx + Inches(0.18), top_y + Inches(0.15), card_w - Inches(0.36), card_h - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p0 = tf.paragraphs[0]
        p0.text = k
        p0.font.size = Pt(9.5)
        p0.font.bold = True
        p0.font.color.rgb = COLOR_ASH
        
        p1 = tf.add_paragraph()
        p1.text = v1
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_WHITE
        p1.space_before = Pt(4)
        
        p2 = tf.add_paragraph()
        p2.text = v2
        p2.font.size = Pt(10)
        p2.font.color.rgb = COLOR_IRIS
        p2.space_before = Pt(2)

    # Bottom Tech Stack Badges Bar
    add_card(slide, Inches(0.8), Inches(5.95), Inches(11.75), Inches(1.0), bg_color=COLOR_CARD, border_color=COLOR_HAIRLINE)
    tb_stack = slide.shapes.add_textbox(Inches(1.0), Inches(6.2), Inches(2.8), Inches(0.5))
    tf_s = tb_stack.text_frame
    p_s = tf_s.paragraphs[0]
    p_s.text = "CORE TECHNOLOGIES"
    p_s.font.size = Pt(10.5)
    p_s.font.bold = True
    p_s.font.color.rgb = COLOR_ASH

    # Logos row with proper spacing and centered badges
    logos = ["python", "xgboost", "catboost", "scikitlearn", "fastapi", "react", "vite", "sqlite"]
    logo_x = Inches(4.0)
    for l_name in logos:
        lp = get_logo_path(l_name)
        if lp:
            add_card(slide, logo_x, Inches(6.1), Inches(0.72), Inches(0.72), bg_color=COLOR_PANEL, border_color=COLOR_HAIRLINE)
            slide.shapes.add_picture(lp, logo_x + Inches(0.11), Inches(6.21), width=Inches(0.5))
        logo_x += Inches(0.98)

    set_notes(slide, 
        "Welcome to CineForecast. This project addresses the multi-million dollar challenge of theatrical box office risk underwriting. "
        "By leveraging 3,931 verified historical films from TMDB, we developed a leakage-safe machine learning engine that forecasts worldwide box office revenue "
        "and classifies return on investment tiers before theatrical debut. Today's presentation highlights our data audit, architecture, modeling benchmarks, and interactive analytics platform."
    )

# ==========================================================
# SLIDE 2: PROJECT OUTLINE / ROADMAP
# ==========================================================
def build_slide_2(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide)
    add_slide_header(slide, "ROADMAP & STRUCTURE", "Project Outline & Analytical Progression", "Visual agenda covering our end-to-end machine learning engineering lifecycle")

    steps = [
        ("01", "Problem & Objectives", "Film Financing Risk", "Quantifying box-office volatility, missing financials, and the risk of post-release target leakage.", COLOR_IRIS),
        ("02", "Data Audit & Cleaning", "Quality Funnel", "Resolving 232 duplicates, 47.7% missing budgets, and parsing malformed list features into 3,931 films.", COLOR_SAFFRON),
        ("03", "System Architecture", "End-to-End Pipeline", "Strict chronological cutoffs, rolling director priors, FastAPI REST services, and React dashboard.", COLOR_VERDANT),
        ("04", "Machine Learning Models", "Champion Optimization", "Ridge baseline, CatBoost benchmark, and Optuna-tuned Champion XGBoost with TimeSeriesSplit.", COLOR_IRIS),
        ("05", "Results & Explainability", "Ablation & SHAP", "Held-out test evaluation, proof of popularity inflation, and TreeExplainer feature attributions.", COLOR_SAFFRON),
        ("06", "Application & Future Scope", "What-If Studio", "Real-time pre-production sensitivity simulator, production deployment, and multi-modal roadmap.", COLOR_VERDANT)
    ]

    card_w = Inches(3.65)
    card_h = Inches(2.3)
    start_x = Inches(0.8)
    gap_x = Inches(0.4)
    top_y1 = Inches(2.05)
    top_y2 = Inches(4.65)

    for i, (num, title, badge, desc, accent) in enumerate(steps):
        row = i // 3
        col = i % 3
        cx = start_x + col * (card_w + gap_x)
        cy = top_y1 if row == 0 else top_y2

        add_card(slide, cx, cy, card_w, card_h, bg_color=COLOR_PANEL, border_color=COLOR_HAIRLINE)
        
        tb = slide.shapes.add_textbox(cx + Inches(0.2), cy + Inches(0.18), card_w - Inches(0.4), card_h - Inches(0.36))
        tf = tb.text_frame
        tf.word_wrap = True

        p0 = tf.paragraphs[0]
        p0.text = f"{num} • {badge.upper()}"
        p0.font.size = Pt(11)
        p0.font.bold = True
        p0.font.color.rgb = accent
        
        p1 = tf.add_paragraph()
        p1.text = title
        p1.font.size = Pt(16)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_WHITE
        p1.space_before = Pt(4)

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(11)
        p2.font.color.rgb = COLOR_ASH
        p2.space_before = Pt(6)

    set_notes(slide, 
        "Our presentation follows a structured six-stage roadmap. We begin with the financial problem statement and the necessity of preventing hindsight leakage. "
        "Next, we review the data cleaning audit and system architecture. We then deep-dive into the ML benchmark results, ablation study, and SHAP explainability. "
        "Finally, we showcase the live interactive What-If Studio and our future engineering roadmap."
    )

# ==========================================================
# SLIDE 3: PROBLEM & OBJECTIVE
# ==========================================================
def build_slide_3(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide)
    add_slide_header(slide, "PROBLEM CONTEXT & MANDATE", "Problem Statement & Strategic Objectives", "De-risking capital allocation in theatrical motion pictures through pre-release intelligence")

    # One-line Problem Banner
    add_card(slide, Inches(0.8), Inches(1.95), Inches(11.75), Inches(1.15), bg_color=COLOR_PANEL, border_color=COLOR_ROSE)
    tb = slide.shapes.add_textbox(Inches(1.05), Inches(2.05), Inches(11.25), Inches(0.95))
    tf = tb.text_frame
    tf.word_wrap = True
    p0 = tf.paragraphs[0]
    p0.text = "CORE PROBLEM STATEMENT"
    p0.font.size = Pt(10)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_ROSE

    p1 = tf.add_paragraph()
    p1.text = "Film greenlighting commits $50M–$200M+ under extreme market uncertainty, compounded by 47% missing financial data in public catalogs and widespread post-release target leakage."
    p1.font.size = Pt(14)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_WHITE
    p1.space_before = Pt(3)

    # 4 Objective Cards
    objs = [
        ("01", "Pre-Release Revenue Forecasting", "Predict worldwide box office gross in log USD using strictly pre-release attributes.", COLOR_IRIS),
        ("02", "Four-Tier ROI Classification", "Classify projects into Flop (<0x), Break-even (0-1x), Hit (1-3x), and Blockbuster (≥3x).", COLOR_SAFFRON),
        ("03", "Zero Target Leakage Discipline", "Strict chronological cutoffs to eliminate post-release popularity and vote bias.", COLOR_VERDANT),
        ("04", "Interactive What-If Simulation", "Provide live sensitivity analysis for studio executives to test budgets and release dates.", COLOR_IRIS)
    ]

    card_w = Inches(2.75)
    card_h = Inches(2.35)
    start_x = Inches(0.8)
    gap_x = Inches(0.25)
    top_y = Inches(3.35)

    for i, (num, title, desc, accent) in enumerate(objs):
        cx = start_x + i * (card_w + gap_x)
        add_card(slide, cx, top_y, card_w, card_h, bg_color=COLOR_CARD, border_color=COLOR_HAIRLINE)
        
        tb = slide.shapes.add_textbox(cx + Inches(0.18), top_y + Inches(0.18), card_w - Inches(0.36), card_h - Inches(0.36))
        tf = tb.text_frame
        tf.word_wrap = True

        p0 = tf.paragraphs[0]
        p0.text = f"GOAL {num}"
        p0.font.size = Pt(11)
        p0.font.bold = True
        p0.font.color.rgb = accent

        p1 = tf.add_paragraph()
        p1.text = title
        p1.font.size = Pt(14)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_WHITE
        p1.space_before = Pt(4)

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(11)
        p2.font.color.rgb = COLOR_ASH
        p2.space_before = Pt(6)

    # Bottom Stat Row
    add_card(slide, Inches(0.8), Inches(5.95), Inches(11.75), Inches(0.95), bg_color=COLOR_PANEL, border_color=COLOR_HAIRLINE)
    stats = [
        ("47.74%", "Missing Budget in Raw Data"),
        ("44.32%", "Missing Revenue in Raw Data"),
        ("3,931", "Final Clean Verified Films"),
        ("56.98%", "Historical Hit/Blockbuster Rate")
    ]
    sw = Inches(2.93)
    for i, (val, lbl) in enumerate(stats):
        sx = Inches(0.8) + i * sw
        tb = slide.shapes.add_textbox(sx, Inches(6.05), sw, Inches(0.75))
        tf = tb.text_frame
        tf.word_wrap = True
        p0 = tf.paragraphs[0]
        p0.text = val
        p0.alignment = PP_ALIGN.CENTER
        p0.font.size = Pt(18)
        p0.font.bold = True
        p0.font.color.rgb = COLOR_SAFFRON if i % 2 == 0 else COLOR_IRIS
        
        p1 = tf.add_paragraph()
        p1.text = lbl
        p1.alignment = PP_ALIGN.CENTER
        p1.font.size = Pt(10)
        p1.font.color.rgb = COLOR_ASH

    set_notes(slide, 
        "Every film production decision carries massive financial downside risk. In raw TMDB data, nearly half the entries omit budget or box office earnings. "
        "Furthermore, many published models commit a critical error: they use post-release audience votes to predict revenue, which is impossible before release. "
        "CineForecast sets four strict objectives: pre-release revenue prediction, four-tier ROI risk classification, zero target leakage, and real-time scenario simulation."
    )

# ==========================================================
# SLIDE 4: DATASET & QUALITY AUDIT
# ==========================================================
def build_slide_4(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide)
    add_slide_header(slide, "DATA ENGINEERING & AUDIT", "Dataset Curation & Quality Funnel", "Transforming 9,999 noisy raw records into 3,931 leakage-safe training samples")

    # Left: Audit Funnel Chart
    chart_funnel = get_chart_path("data_audit_funnel")
    if chart_funnel:
        add_card(slide, Inches(0.8), Inches(1.95), Inches(7.4), Inches(3.65), bg_color=COLOR_PANEL, border_color=COLOR_HAIRLINE)
        slide.shapes.add_picture(chart_funnel, Inches(0.9), Inches(2.02), width=Inches(7.2))

    # Right: Tier Distribution Chart
    chart_tier = get_chart_path("tier_distribution")
    if chart_tier:
        add_card(slide, Inches(8.4), Inches(1.95), Inches(4.15), Inches(3.65), bg_color=COLOR_PANEL, border_color=COLOR_HAIRLINE)
        slide.shapes.add_picture(chart_tier, Inches(8.5), Inches(2.02), width=Inches(3.95))

    # Bottom: 3 Audit Takeaway Cards filling the lower space
    audit_takeaways = [
        ("47.7% MISSING FINANCIALS", "Handled Non-Silently", "Raw zeros reflect unrecorded telemetry rather than actual zero spend. Excluded from supervised training without synthetic imputation.", COLOR_ROSE),
        ("232 DUPLICATE SNAPSHOTS", "Completeness-Based Retention", "Multi-attribute scoring retained exactly one most complete record per film ID, preserving 9,767 unique movies.", COLOR_SAFFRON),
        ("TEMPORAL STABILITY", "1990–2025 Release Window", "Historical pre-1990 releases and future releases up to 2031 filtered to maintain modern macroeconomic consistency.", COLOR_VERDANT)
    ]
    card_w = Inches(3.75)
    card_h = Inches(1.3)
    start_x = Inches(0.8)
    gap_x = Inches(0.25)
    top_y = Inches(5.8)

    for i, (tag, title, desc, acc) in enumerate(audit_takeaways):
        cx = start_x + i * (card_w + gap_x)
        add_card(slide, cx, top_y, card_w, card_h, bg_color=COLOR_CARD, border_color=COLOR_HAIRLINE)
        tb = slide.shapes.add_textbox(cx + Inches(0.18), top_y + Inches(0.1), card_w - Inches(0.36), card_h - Inches(0.2))
        tf = tb.text_frame
        tf.word_wrap = True

        p0 = tf.paragraphs[0]
        p0.text = tag
        p0.font.size = Pt(9.5)
        p0.font.bold = True
        p0.font.color.rgb = acc

        p1 = tf.add_paragraph()
        p1.text = title
        p1.font.size = Pt(12)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_WHITE
        p1.space_before = Pt(2)

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(9)
        p2.font.color.rgb = COLOR_ASH
        p2.space_before = Pt(3)

    set_notes(slide, 
        "This slide presents our rigorous data audit findings. Starting from 9,999 raw TMDB entries, we identified 232 duplicates, which we resolved using completeness scoring. "
        "We filtered out zero-budget and zero-revenue records, removed historical pre-1990 films to preserve macroeconomic consistency, and excluded future-dated entries up to 2031. "
        "The resulting 3,931 films show a balanced tier distribution, with 56.9% achieving Break-even or better returns."
    )

# ==========================================================
# SLIDE 5: SYSTEM ARCHITECTURE & WORKFLOW
# ==========================================================
def build_slide_5(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide)
    add_slide_header(slide, "TECHNICAL BLUEPRINT", "End-to-End System Architecture", "Multi-stage pipeline spanning ingestion, leakage-safe feature engineering, REST APIs, and UI")

    stages = [
        ("STAGE 1", "Data Ingestion & Audit", COLOR_ASH, [
            ("Raw TMDB Catalog", "9,999 rows, 15 raw columns"),
            ("Completeness Audit", "Resolved 232 duplicates"),
            ("Type Sanitation", "ast.literal_eval list parser"),
            ("Interim Parquet", "9,767 parsed unique movies")
        ]),
        ("STAGE 2", "Leakage-Safe Features", COLOR_IRIS, [
            ("Chronological Rolling Priors", "Director & studio historic gross"),
            ("Genre Encoders", "17 multi-hot genre flags"),
            ("Temporal Splitting", "Train: 1990-2022 | Test: 2023-2025"),
            ("Feature Manifest", "34 clean pre-release inputs")
        ]),
        ("STAGE 3", "ML Optimization & Registry", COLOR_SAFFRON, [
            ("Baseline Ridge", "L2 regularized benchmark"),
            ("Optuna Tuning", "5-fold TimeSeriesSplit CV"),
            ("TreeExplainer SHAP", "Waterfall cache for 383 test films"),
            ("Model Registry", "Serialized joblib artifacts")
        ]),
        ("STAGE 4", "Application & Serving", COLOR_VERDANT, [
            ("FastAPI Backend", "/api/predict, /api/whatif, /api/shap"),
            ("Relational DB", "SQLite / PostgreSQL catalog"),
            ("React 18 + Vite", "High-density Dark Void UI"),
            ("What-If Studio", "Real-time parameter sensitivity")
        ]),
    ]

    col_w = Inches(2.65)
    col_h = Inches(4.75)
    start_x = Inches(0.8)
    gap_x = Inches(0.38)
    top_y = Inches(2.05)

    for i, (stage_num, stage_title, accent, items) in enumerate(stages):
        cx = start_x + i * (col_w + gap_x)
        add_card(slide, cx, top_y, col_w, col_h, bg_color=COLOR_PANEL, border_color=COLOR_HAIRLINE)
        
        # Header Box
        tb = slide.shapes.add_textbox(cx + Inches(0.15), top_y + Inches(0.15), col_w - Inches(0.3), Inches(0.75))
        tf = tb.text_frame
        tf.word_wrap = True
        p0 = tf.paragraphs[0]
        p0.text = stage_num
        p0.font.size = Pt(10)
        p0.font.bold = True
        p0.font.color.rgb = accent

        p1 = tf.add_paragraph()
        p1.text = stage_title
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_WHITE
        p1.space_before = Pt(3)

        # Content Cards inside column
        item_y = top_y + Inches(0.95)
        for h_text, b_text in items:
            add_card(slide, cx + Inches(0.12), item_y, col_w - Inches(0.24), Inches(0.82), bg_color=COLOR_CARD, border_color=COLOR_HAIRLINE)
            tb_sub = slide.shapes.add_textbox(cx + Inches(0.18), item_y + Inches(0.06), col_w - Inches(0.36), Inches(0.7))
            tf_sub = tb_sub.text_frame
            tf_sub.word_wrap = True
            
            p_h = tf_sub.paragraphs[0]
            p_h.text = h_text
            p_h.font.size = Pt(10.5)
            p_h.font.bold = True
            p_h.font.color.rgb = COLOR_WHITE
            
            p_b = tf_sub.add_paragraph()
            p_b.text = b_text
            p_b.font.size = Pt(9)
            p_b.font.color.rgb = COLOR_ASH
            p_b.space_before = Pt(2)

            item_y += Inches(0.9)

        # Connector Arrow between columns (except last)
        if i < 3:
            arrow_x = cx + col_w + Inches(0.08)
            arrow_box = slide.shapes.add_textbox(arrow_x, top_y + Inches(2.2), Inches(0.25), Inches(0.4))
            tf_a = arrow_box.text_frame
            p_a = tf_a.paragraphs[0]
            p_a.text = "➔"
            p_a.alignment = PP_ALIGN.CENTER
            p_a.font.size = Pt(18)
            p_a.font.bold = True
            p_a.font.color.rgb = COLOR_IRIS

    set_notes(slide, 
        "Our system architecture is designed for production reliability and analytical integrity. In Stage 1, raw catalog data is ingested and sanitized. "
        "In Stage 2, our leakage-safe feature builder computes rolling historical priors with strict temporal cutoffs to eliminate future data contamination. "
        "Stage 3 optimizes gradient boosted trees using Bayesian search via Optuna and serializes models and SHAP cache to the registry. "
        "Stage 4 serves inference through a FastAPI REST engine to an interactive React dashboard."
    )

# ==========================================================
# SLIDE 6: ML MODELS USED & TUNING
# ==========================================================
def build_slide_6(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide)
    add_slide_header(slide, "MODELING & OPTIMIZATION", "Machine Learning Models & Bayesian Tuning", "Comparing linear baselines against gradient boosted decision tree ensembles")

    models = [
        ("BASELINE MODEL", "Ridge Regression", "L2-Regularized Linear", "scikitlearn", [
            ("Feature Count", "34 Pre-Release Features"),
            ("Objective", "Log Worldwide Revenue USD"),
            ("Test R² (Log)", "0.4021"),
            ("Pearson r", "0.6536")
        ], COLOR_ASH),
        ("BENCHMARK MODEL", "CatBoost Regressor", "Oblivious Decision Trees", "catboost", [
            ("Feature Count", "34 Pre-Release Features"),
            ("Ensemble Depth", "6 splits with symmetric trees"),
            ("Test R² (Log)", "0.3943"),
            ("Pearson r", "0.6410")
        ], COLOR_SAFFRON),
        ("CHAMPION MODEL", "XGBoost Regressor", "Optuna Tuned Gradient Boosting", "xgboost", [
            ("Feature Count", "34 Pre-Release Features"),
            ("Cross-Validation", "5-Fold TimeSeriesSplit CV"),
            ("Test R² (Log)", "0.3747 (MdAPE: 68.4%)"),
            ("Pearson r", "0.6267 (Zero Leakage)")
        ], COLOR_IRIS),
    ]

    card_w = Inches(3.75)
    card_h = Inches(4.75)
    start_x = Inches(0.8)
    gap_x = Inches(0.25)
    top_y = Inches(2.05)

    for i, (m_type, m_name, m_sub, logo_name, stats, accent) in enumerate(models):
        cx = start_x + i * (card_w + gap_x)
        add_card(slide, cx, top_y, card_w, card_h, bg_color=COLOR_PANEL, border_color=accent if accent == COLOR_IRIS else COLOR_HAIRLINE)

        # Header Text
        tb = slide.shapes.add_textbox(cx + Inches(0.2), top_y + Inches(0.18), card_w - Inches(1.15), Inches(0.95))
        tf = tb.text_frame
        tf.word_wrap = True
        p0 = tf.paragraphs[0]
        p0.text = m_type
        p0.font.size = Pt(10)
        p0.font.bold = True
        p0.font.color.rgb = accent

        p1 = tf.add_paragraph()
        p1.text = m_name
        p1.font.size = Pt(16)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_WHITE
        p1.space_before = Pt(3)

        p2 = tf.add_paragraph()
        p2.text = m_sub
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = COLOR_ASH
        p2.space_before = Pt(2)

        # Centered Logo inside rounded badge
        lp = get_logo_path(logo_name)
        if lp:
            add_card(slide, cx + card_w - Inches(0.95), top_y + Inches(0.2), Inches(0.75), Inches(0.75), bg_color=COLOR_CARD, border_color=COLOR_HAIRLINE)
            slide.shapes.add_picture(lp, cx + card_w - Inches(0.88), top_y + Inches(0.27), width=Inches(0.6))

        # Divider
        div = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx + Inches(0.2), top_y + Inches(1.22), card_w - Inches(0.4), Inches(0.02))
        div.fill.solid()
        div.fill.fore_color.rgb = COLOR_HAIRLINE
        div.line.fill.background()

        # Metrics rows inside card
        my = top_y + Inches(1.36)
        for lbl, val in stats:
            add_card(slide, cx + Inches(0.2), my, card_w - Inches(0.4), Inches(0.65), bg_color=COLOR_CARD, border_color=COLOR_HAIRLINE)
            tb_s = slide.shapes.add_textbox(cx + Inches(0.3), my + Inches(0.08), card_w - Inches(0.6), Inches(0.5))
            tf_s = tb_s.text_frame
            tf_s.word_wrap = True
            
            p_l = tf_s.paragraphs[0]
            p_l.text = lbl
            p_l.font.size = Pt(9.5)
            p_l.font.color.rgb = COLOR_ASH
            
            p_v = tf_s.add_paragraph()
            p_v.text = val
            p_v.font.size = Pt(12)
            p_v.font.bold = True
            p_v.font.color.rgb = COLOR_WHITE
            p_v.space_before = Pt(2)

            my += Inches(0.72)

        # Champion Specific Hyperparameters Table
        if i == 2:
            add_card(slide, cx + Inches(0.2), top_y + Inches(4.3), card_w - Inches(0.4), Inches(0.88), bg_color=COLOR_VOID, border_color=COLOR_IRIS)
            tb_hp = slide.shapes.add_textbox(cx + Inches(0.25), top_y + Inches(4.33), card_w - Inches(0.5), Inches(0.8))
            tf_hp = tb_hp.text_frame
            tf_hp.word_wrap = True
            p_hp = tf_hp.paragraphs[0]
            p_hp.text = "CHAMPION HYPERPARAMETERS (OPTUNA)"
            p_hp.font.size = Pt(8.5)
            p_hp.font.bold = True
            p_hp.font.color.rgb = COLOR_IRIS
            
            p_hp_vals = tf_hp.add_paragraph()
            p_hp_vals.text = "n_est: 400 • depth: 5 • lr: 0.0134 • sub: 0.77 • col: 0.87 • alpha: 0.49"
            p_hp_vals.font.size = Pt(8.5)
            p_hp_vals.font.color.rgb = COLOR_WHITE
            p_hp_vals.space_before = Pt(2)

    set_notes(slide, 
        "We systematically evaluated multiple model families. Ridge Regression provides a solid linear baseline with an R² of 0.40 on log revenue. "
        "CatBoost demonstrated competitive performance with symmetric trees. Our champion model, XGBoost, was hyperparameter-tuned using Optuna "
        "over 5-fold TimeSeriesSplit cross-validation. XGBoost was chosen as our primary production champion due to its deterministic TreeExplainer SHAP "
        "performance and rapid inference latency in FastAPI."
    )

# ==========================================================
# SLIDE 7: TRAINING & IMPLEMENTATION TECH STACK
# ==========================================================
def build_slide_7(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide)
    add_slide_header(slide, "INFRASTRUCTURE & CODEBASE", "Training Pipeline & Official Technology Stack", "Modular architecture built strictly with enterprise open-source libraries")

    # Left: Official Tech Stack Logo Grid
    add_card(slide, Inches(0.8), Inches(2.05), Inches(6.0), Inches(4.75), bg_color=COLOR_PANEL, border_color=COLOR_HAIRLINE)
    tb = slide.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.6), Inches(0.4))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = "ENTERPRISE ML & SERVING STACK"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_IRIS

    techs = [
        ("python", "Python 3.11", "Runtime & ML"),
        ("xgboost", "XGBoost 2.0+", "Champion Regressor"),
        ("catboost", "CatBoost", "Benchmark Ensemble"),
        ("scikitlearn", "Scikit-Learn", "Preprocessing & Metrics"),
        ("optuna", "Optuna 3.5+", "Bayesian HPO Search"),
        ("shap", "SHAP", "TreeExplainer Attribution"),
        ("fastapi", "FastAPI", "High-Performance REST"),
        ("sqlite", "SQLite / PG", "Relational Catalog DB"),
        ("react", "React 18", "Component UI Engine"),
        ("vite", "Vite 5", "Lightning Build System"),
        ("tailwindcss", "Tailwind CSS", "Dark Void Design"),
        ("github", "GitHub Actions", "Automated CI / Pytest")
    ]

    grid_x = Inches(1.0)
    grid_y = Inches(2.7)
    item_w = Inches(1.8)
    item_h = Inches(0.92)
    gap_gx = Inches(0.15)
    gap_gy = Inches(0.14)

    for i, (l_name, t_title, t_role) in enumerate(techs):
        row = i // 3
        col = i % 3
        ix = grid_x + col * (item_w + gap_gx)
        iy = grid_y + row * (item_h + gap_gy)

        add_card(slide, ix, iy, item_w, item_h, bg_color=COLOR_CARD, border_color=COLOR_HAIRLINE)
        lp = get_logo_path(l_name)
        if lp:
            slide.shapes.add_picture(lp, ix + Inches(0.12), iy + Inches(0.22), width=Inches(0.46))
        
        tb_t = slide.shapes.add_textbox(ix + Inches(0.64), iy + Inches(0.15), item_w - Inches(0.68), Inches(0.68))
        tf_t = tb_t.text_frame
        tf_t.word_wrap = True
        p_tt = tf_t.paragraphs[0]
        p_tt.text = t_title
        p_tt.font.size = Pt(10)
        p_tt.font.bold = True
        p_tt.font.color.rgb = COLOR_WHITE
        
        p_tr = tf_t.add_paragraph()
        p_tr.text = t_role
        p_tr.font.size = Pt(8.5)
        p_tr.font.color.rgb = COLOR_ASH

    # Right: Pipeline Engineering Pillars
    add_card(slide, Inches(7.05), Inches(2.05), Inches(5.5), Inches(4.75), bg_color=COLOR_PANEL, border_color=COLOR_HAIRLINE)
    tb_p = slide.shapes.add_textbox(Inches(7.25), Inches(2.2), Inches(5.1), Inches(0.4))
    tf_p = tb_p.text_frame
    p_p = tf_p.paragraphs[0]
    p_p.text = "ENGINEERING DISCIPLINE & PIPELINE PILLARS"
    p_p.font.size = Pt(12)
    p_p.font.bold = True
    p_p.font.color.rgb = COLOR_SAFFRON

    pillars = [
        ("Strict Temporal Split", "Train: 1990–2022 ($N=3,548$) held out against test: 2023–2025 ($N=383$) to mirror true chronological deployment conditions.", COLOR_IRIS),
        ("Defensive Preprocessing", "Stringified Python list parsing via ast.literal_eval, eliminating malformed genres and null runtime anomalies.", COLOR_SAFFRON),
        ("Sub-2-Minute Training", "Bayesian hyperparameter optimization and XGBoost training finish in under 120 seconds on standard CPU hardware.", COLOR_VERDANT),
        ("Comprehensive Testing Suite", "Automated Pytest coverage verifying leakage prevention, schema integrity, and REST endpoint response schemas.", COLOR_IRIS)
    ]

    py = Inches(2.7)
    for p_title, p_desc, p_acc in pillars:
        add_card(slide, Inches(7.25), py, Inches(5.1), Inches(0.92), bg_color=COLOR_CARD, border_color=COLOR_HAIRLINE)
        tb_card = slide.shapes.add_textbox(Inches(7.4), py + Inches(0.08), Inches(4.8), Inches(0.76))
        tf_c = tb_card.text_frame
        tf_c.word_wrap = True
        
        pt = tf_c.paragraphs[0]
        pt.text = p_title
        pt.font.size = Pt(11)
        pt.font.bold = True
        pt.font.color.rgb = p_acc

        pd = tf_c.add_paragraph()
        pd.text = p_desc
        pd.font.size = Pt(9.5)
        pd.font.color.rgb = COLOR_SILVER
        pd.space_before = Pt(2)

        py += Inches(1.04)

    set_notes(slide, 
        "Our technical implementation adheres to strict software engineering standards. The entire stack is built on Python 3.11, FastAPI, and React 18. "
        "We maintain full reproducibility through frozen requirements and Docker specs. Model tuning executes in under 2 minutes on CPU, "
        "and our automated Pytest test suite validates zero-leakage constraints before any model artifact is accepted into the registry."
    )

# ==========================================================
# SLIDE 8: RESULTS & LEAKAGE ABLATION
# ==========================================================
def build_slide_8(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide)
    add_slide_header(slide, "BENCHMARK & EMPIRICAL FINDINGS", "Results, Leakage Ablation & Explainability", "Quantitative proof of post-release target leakage and global SHAP value drivers")

    # Left: Model Benchmark Chart
    chart_bm = get_chart_path("model_benchmark")
    if chart_bm:
        add_card(slide, Inches(0.8), Inches(1.95), Inches(5.8), Inches(3.65), bg_color=COLOR_PANEL, border_color=COLOR_HAIRLINE)
        slide.shapes.add_picture(chart_bm, Inches(0.85), Inches(2.0), width=Inches(5.7))

    # Right: Ablation Chart
    chart_abl = get_chart_path("ablation_comparison")
    if chart_abl:
        add_card(slide, Inches(6.8), Inches(1.95), Inches(5.75), Inches(3.65), bg_color=COLOR_PANEL, border_color=COLOR_HAIRLINE)
        slide.shapes.add_picture(chart_abl, Inches(6.85), Inches(2.0), width=Inches(5.65))

    # Bottom Row: 4 Big-Number Callout Cards
    kpis = [
        ("0.375", "Champion Test R²", "Log USD worldwide box office", COLOR_IRIS),
        ("0.627", "Pearson Correlation (r)", "Clean pre-release features", COLOR_SAFFRON),
        ("+0.07", "Leakage Inflation Lift", "Post-release vote distortion", COLOR_ROSE),
        ("#1 DRIVER", "Budget ($0.84 SHAP)", "Dominant pre-release signal", COLOR_VERDANT)
    ]
    card_w = Inches(2.75)
    start_x = Inches(0.8)
    gap_x = Inches(0.25)
    by = Inches(5.8)

    for i, (b_val, b_title, b_sub, accent) in enumerate(kpis):
        cx = start_x + i * (card_w + gap_x)
        add_card(slide, cx, by, card_w, Inches(1.15), bg_color=COLOR_PANEL, border_color=COLOR_HAIRLINE)
        tb = slide.shapes.add_textbox(cx + Inches(0.1), by + Inches(0.1), card_w - Inches(0.2), Inches(0.95))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p0 = tf.paragraphs[0]
        p0.text = b_val
        p0.alignment = PP_ALIGN.CENTER
        p0.font.size = Pt(20)
        p0.font.bold = True
        p0.font.color.rgb = accent

        p1 = tf.add_paragraph()
        p1.text = b_title
        p1.alignment = PP_ALIGN.CENTER
        p1.font.size = Pt(11)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_WHITE
        p1.space_before = Pt(2)

        p2 = tf.add_paragraph()
        p2.text = b_sub
        p2.alignment = PP_ALIGN.CENTER
        p2.font.size = Pt(9)
        p2.font.color.rgb = COLOR_ASH

    set_notes(slide, 
        "Slide 8 presents our core empirical findings. On the left, our held-out test benchmarks on 2023–2025 releases demonstrate strong predictive correlation "
        "exceeding 0.62 across models. On the right, our Leakage Ablation Study proves the deceptive inflation caused by early audience signals: incorporating post-release "
        "popularity artificially increases Pearson r to 0.6939. CineForecast exclusively deploys the clean pre-release model to maintain operational truth."
    )

# ==========================================================
# SLIDE 9: APPLICATION & FUTURE SCOPE
# ==========================================================
def build_slide_9(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide)
    add_slide_header(slide, "DEPLOYMENT & ROADMAP", "Production Application & Future Scope", "Live interactive analytics dashboard paired with forward-looking multi-modal capabilities")

    # Left: UI Screenshot
    ui_pic = os.path.join(ASSETS_DIR, "dashboard_overview.png")
    if os.path.exists(ui_pic):
        add_card(slide, Inches(0.8), Inches(1.95), Inches(6.8), Inches(4.85), bg_color=COLOR_PANEL, border_color=COLOR_HAIRLINE)
        slide.shapes.add_picture(ui_pic, Inches(0.9), Inches(2.05), width=Inches(6.6))
        
        # Caption pill
        cap = add_card(slide, Inches(1.1), Inches(6.25), Inches(6.2), Inches(0.42), bg_color=COLOR_CARD, border_color=COLOR_HAIRLINE)
        tf_c = cap.text_frame
        p_c = tf_c.paragraphs[0]
        p_c.text = "CineForecast Live Executive Overview • 3,931 Catalog Films • Real-Time Predictions"
        p_c.alignment = PP_ALIGN.CENTER
        p_c.font.size = Pt(9.5)
        p_c.font.bold = True
        p_c.font.color.rgb = COLOR_WHITE

    # Right: Dashboard Features & Future Scope
    add_card(slide, Inches(7.8), Inches(1.95), Inches(4.75), Inches(4.85), bg_color=COLOR_PANEL, border_color=COLOR_HAIRLINE)
    tb_r = slide.shapes.add_textbox(Inches(8.0), Inches(2.1), Inches(4.35), Inches(0.35))
    tf_r = tb_r.text_frame
    p_r = tf_r.paragraphs[0]
    p_r.text = "CORE CAPABILITIES & ROADMAP"
    p_r.font.size = Pt(12)
    p_r.font.bold = True
    p_r.font.color.rgb = COLOR_SAFFRON

    features = [
        ("What-If Scenario Simulator", "Producers dynamically slide budget, adjust release calendar, and view live ROI & tier deltas.", COLOR_IRIS),
        ("SHAP Waterfall Inspection", "Expandable per-movie breakdown detailing positive revenue drivers vs negative drags.", COLOR_VERDANT),
        ("Macro Industry Analytics", "Historical breakdown across genres, decadal inflation, and holiday seasonality.", COLOR_SAFFRON),
        ("Future: Multi-Modal Trailer AI", "Extract video pacing, audio score mood, and trailer YouTube engagement signals.", COLOR_WHITE),
        ("Future: Global Territory Splits", "Decompose box office projections across North America, EMEA, and APAC markets.", COLOR_WHITE)
    ]

    fy = Inches(2.55)
    for f_title, f_desc, f_acc in features:
        add_card(slide, Inches(8.0), fy, Inches(4.35), Inches(0.78), bg_color=COLOR_CARD, border_color=COLOR_HAIRLINE)
        tb_f = slide.shapes.add_textbox(Inches(8.15), fy + Inches(0.06), Inches(4.05), Inches(0.66))
        tf_f = tb_f.text_frame
        tf_f.word_wrap = True
        
        pf_t = tf_f.paragraphs[0]
        pf_t.text = f_title
        pf_t.font.size = Pt(10.5)
        pf_t.font.bold = True
        pf_t.font.color.rgb = f_acc

        pf_d = tf_f.add_paragraph()
        pf_d.text = f_desc
        pf_d.font.size = Pt(9)
        pf_d.font.color.rgb = COLOR_ASH
        pf_d.space_before = Pt(2)

        fy += Inches(0.84)

    set_notes(slide, 
        "Our production application puts predictive power directly in the hands of creative producers and film financiers. "
        "Through the What-If Studio, users can simulate budget adjustments and release shifts to test project sensitivity in real-time. "
        "Per-film SHAP waterfall drawers explain every prediction. Our future engineering roadmap includes multi-modal trailer video analysis "
        "and territory-level box office decomposition."
    )

# ==========================================================
# SLIDE 10: THANK YOU & QR CODE
# ==========================================================
def build_slide_10(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide)

    # Left Container: Project Summary & Links
    add_card(slide, Inches(0.8), Inches(1.0), Inches(6.8), Inches(5.5), bg_color=COLOR_PANEL, border_color=COLOR_HAIRLINE)
    
    tb = slide.shapes.add_textbox(Inches(1.2), Inches(1.3), Inches(6.0), Inches(1.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p0 = tf.paragraphs[0]
    p0.text = "CineForecast"
    p0.font.size = Pt(44)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_WHITE
    p0.font.name = FONT_HEADING

    p1 = tf.add_paragraph()
    p1.text = "Predictive Intelligence for Film Box Office & ROI Forecasting"
    p1.font.size = Pt(14)
    p1.font.color.rgb = COLOR_IRIS
    p1.space_before = Pt(4)

    info_rows = [
        ("AUTHOR & LEAD", "Pratham Raval (ML Engineer & Full-Stack Developer)"),
        ("REPOSITORY", "github.com/prathamraval33/ml-project"),
        ("CORE RESULTS", "Test R²: 0.38 • Pearson r: 0.63 • 3,931 Clean Historical Films"),
        ("COMPONENTS", "FastAPI Engine • React 18 UI • Optuna • TreeExplainer SHAP"),
        ("LICENSE", "Open-Source MIT License • Automated Pytest CI Suite")
    ]
    iy = Inches(2.7)
    for k, v in info_rows:
        tb_i = slide.shapes.add_textbox(Inches(1.2), iy, Inches(6.0), Inches(0.55))
        tf_i = tb_i.text_frame
        tf_i.word_wrap = True
        
        pi_k = tf_i.paragraphs[0]
        pi_k.text = k
        pi_k.font.size = Pt(9.5)
        pi_k.font.bold = True
        pi_k.font.color.rgb = COLOR_SAFFRON
        
        pi_v = tf_i.add_paragraph()
        pi_v.text = v
        pi_v.font.size = Pt(11)
        pi_v.font.color.rgb = COLOR_SILVER
        pi_v.space_before = Pt(2)

        iy += Inches(0.65)

    # Right Container: QR Code & Access Card
    add_card(slide, Inches(8.0), Inches(1.0), Inches(4.55), Inches(5.5), bg_color=COLOR_PANEL, border_color=COLOR_IRIS)
    
    tb_r = slide.shapes.add_textbox(Inches(8.2), Inches(1.3), Inches(4.15), Inches(0.8))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True
    pr0 = tf_r.paragraphs[0]
    pr0.text = "SCAN TO ACCESS REPOSITORY"
    pr0.alignment = PP_ALIGN.CENTER
    pr0.font.size = Pt(13)
    pr0.font.bold = True
    pr0.font.color.rgb = COLOR_WHITE

    pr1 = tf_r.add_paragraph()
    pr1.text = "Codebase • Model Registry • Interactive UI"
    pr1.alignment = PP_ALIGN.CENTER
    pr1.font.size = Pt(10)
    pr1.font.color.rgb = COLOR_ASH
    pr1.space_before = Pt(2)

    # QR Code Image
    qr_path = os.path.join(ASSETS_DIR, "repo_qrcode.png")
    if os.path.exists(qr_path):
        slide.shapes.add_picture(qr_path, Inches(9.0), Inches(2.25), width=Inches(2.55))

    # GitHub Logo + Link Pill
    add_card(slide, Inches(8.5), Inches(5.15), Inches(3.55), Inches(0.8), bg_color=COLOR_CARD, border_color=COLOR_HAIRLINE)
    lp = get_logo_path("github")
    if lp:
        slide.shapes.add_picture(lp, Inches(8.75), Inches(5.3), width=Inches(0.5))
    
    tb_gh = slide.shapes.add_textbox(Inches(9.35), Inches(5.25), Inches(2.5), Inches(0.6))
    tf_gh = tb_gh.text_frame
    tf_gh.word_wrap = True
    p_gh = tf_gh.paragraphs[0]
    p_gh.text = "VIEW ON GITHUB"
    p_gh.font.size = Pt(11)
    p_gh.font.bold = True
    p_gh.font.color.rgb = COLOR_WHITE
    
    p_url = tf_gh.add_paragraph()
    p_url.text = "prathamraval33/ml-project"
    p_url.font.size = Pt(9.5)
    p_url.font.color.rgb = COLOR_IRIS

    set_notes(slide, 
        "Thank you for your attention. CineForecast bridges academic machine learning discipline with production full-stack engineering. "
        "The entire codebase, test suites, trained model registry, and interactive dashboard are open-source and documented on GitHub. "
        "Scan the QR code or visit github.com/prathamraval33/ml-project. I welcome your questions and feedback."
    )

# ==========================================================
# MAIN EXECUTION
# ==========================================================
def main():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    print("Building enhanced 10 slides...")
    build_slide_1(prs)
    build_slide_2(prs)
    build_slide_3(prs)
    build_slide_4(prs)
    build_slide_5(prs)
    build_slide_6(prs)
    build_slide_7(prs)
    build_slide_8(prs)
    build_slide_9(prs)
    build_slide_10(prs)

    output_path = os.path.abspath("cineforecast_presentation.pptx")
    prs.save(output_path)
    print("Enhanced presentation saved successfully at:", output_path)

if __name__ == "__main__":
    main()
