"""Generates a professional multi-page PDF presentation guide with embedded screenshots."""

import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY


def build_pdf(output_pdf_path="/Volumes/T7/SIH/SkyGuard_AI_Dashboard_Guide.pdf"):
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom Palette
    c_primary = colors.HexColor("#0284c7")
    c_dark = colors.HexColor("#0f172a")
    c_card = colors.HexColor("#f8fafc")
    c_border = colors.HexColor("#cbd5e1")
    c_green = colors.HexColor("#16a34a")
    c_amber = colors.HexColor("#d97706")
    c_red = colors.HexColor("#dc2626")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=c_dark,
        alignment=TA_CENTER
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569"),
        alignment=TA_CENTER
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=c_primary,
        spaceBefore=12,
        spaceAfter=6
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_dark,
        spaceBefore=8,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1e293b"),
        alignment=TA_LEFT
    )

    bold_body_style = ParagraphStyle(
        'BoldBody',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#0f172a")
    )

    jury_box_style = ParagraphStyle(
        'JuryBox',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#0f172a")
    )

    img_dir = '/Users/pradumnpatidar/.gemini/antigravity-ide/brain/4bb672e2-a789-4e4d-9749-a8480abf69e8/.user_uploaded'
    img1 = os.path.join(img_dir, 'media_1789147381567.png')
    img2 = os.path.join(img_dir, 'media_1789147381574.png')
    img3 = os.path.join(img_dir, 'media_1789147381584.png')
    img4 = os.path.join(img_dir, 'media_1789147381594.png')
    img5 = os.path.join(img_dir, 'media_1789147381614.png')

    story = []

    # ------------------- HEADER & COVER SUMMARY -------------------
    story.append(Paragraph("🛡️ SkyGuard AI - Dashboard & Presentation Jury Guide", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Smart India Hackathon (SIH26073) | MoES / India Meteorological Department (IMD)<br/><b>Strict Raw Input Constraint:</b> Temperature (°C), Atmospheric Pressure (hPa), Relative Humidity (%) ONLY", subtitle_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceBefore=4, spaceAfter=10))

    # Executive Pitch Box
    pitch_text = """<b>🎤 30-Second Elevator Pitch:</b><br/>
    <i>"SkyGuard AI is India’s first physics-informed, multivariate, self-healing anomaly detection system for Automatic Weather Stations (AWS). Operating strictly on Temperature, Pressure, and Relative Humidity, SkyGuard combines atmospheric thermodynamics with LightGBM, TreeSHAP explainability, and recursive Kalman self-healing to eliminate false alarms during severe weather (<1.5% vs 48.5% in baseline QC) and maintain uninterrupted weather records—both in the cloud and directly on edge microcontrollers."</i>"""
    
    pitch_table = Table([[Paragraph(pitch_text, callout_style)]], colWidths=[540])
    pitch_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f0f9ff")),
        ('BOX', (0,0), (-1,-1), 1, c_primary),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(pitch_table)
    story.append(Spacer(1, 12))

    # ------------------- SECTION 1: DATASET PROVENANCE -------------------
    story.append(Paragraph("1. Dataset Lineage & Provenance Governance", h1_style))
    if os.path.exists(img1):
        story.append(Image(img1, width=540, height=190))
        story.append(Spacer(1, 6))

    p1_desc = """<b>❓ Yeh Page Kya Hai aur Iska Kaam Kya Hai?</b><br/>
    Is page par data ki complete <b>Governance, Lineage aur Provenance (source tracking)</b> dikhai gayi hai. Weather AI systems me sabse bada issue hota hai ki training data aur real-world ground truth mix ho jata hai. SkyGuard AI har record ka source label retain karta hai.<br/><br/>
    <b>⚙️ 4 Data Sources Ka Exact Role:</b><br/>
    • <b>IMD_AWS (Primary Production Ingest):</b> Official IMD AWS portal (<code>dsp.imdpune.gov.in</code>) ka standard adapter. Real Indian stations (Safdarjung, Palam, etc.) ka 15-min feed.<br/>
    • <b>NOAA_ISD (Secondary Benchmark):</b> Global station archive for heavy benchmark pre-training.<br/>
    • <b>ERA5 (Climatological Reference Only):</b> <i>Yeh direct AWS sensor ground truth nahi hai!</i> Isko strictly seasonal normal baseline aur diurnal prior ke liye use kiya jata hai.<br/>
    • <b>SYNTHETIC (High-Fidelity Physics Generator):</b> 26 realistic hardware faults (spikes, drift, stuck ADC, packet drop) aur authentic extreme events generate karta hai.<br/><br/>
    <b>🎤 Likely Jury Question & Winning Answer:</b><br/>
    <b>Q: 'Aapne ERA5 reanalysis ko sensor ground truth ki tarah kyu nahi use kiya?'</b><br/>
    <i><b>Ans:</b> 'Sir, ERA5 ek global 0.25° reanalysis model hai, direct ground sensor truth nahi. Humne Section 4 guidelines follow karte hue ERA5 ko strictly baseline prior rakha hai aur ground observation IMD AWS adapter se preserve ki hai.'</i>"""

    story.append(Paragraph(p1_desc, body_style))
    story.append(PageBreak())

    # ------------------- SECTION 2: MODEL BENCHMARK & ABLATION -------------------
    story.append(Paragraph("2. Model Benchmark & Comprehensive Ablation Study", h1_style))
    if os.path.exists(img2):
        story.append(Image(img2, width=540, height=190))
        story.append(Spacer(1, 6))

    p2_desc = """<b>❓ Yeh Page Kya Hai aur Iska Kaam Kya Hai?</b><br/>
    Yeh page SIH Technical Defense ka sabse strong proof hai. Yeh scientifically prove karta hai ki conventional rules ya simple ML kyu fail hoti hai aur <b>Full SkyGuard Hybrid System</b> kyu superior hai.<br/><br/>
    <b>⚙️ Table Ka Point-by-Point Breakdown:</b><br/>
    • <b>A. Conventional Rule-Based QC (WMO-8):</b> F1=0.742, <b>Extreme Weather False Alarms = 48.5%</b>. Traditional static threshold (±5°C) severe heatwave ya toofan ko fault samajhkar reject kar deta hai.<br/>
    • <b>B. Raw LightGBM (T/P/RH only):</b> F1=0.835, False Alarms = 32.0%. Bina atmospheric thermodynamics ke ML black-box ki tarah confuse hota hai.<br/>
    • <b>C. Physics + LightGBM:</b> F1=0.912. Magnus-Tetens Dew Point ($T_d \le T$) aur VPD add karne se precision boost hoti hai.<br/>
    • <b>D. Temporal + LightGBM:</b> F1=0.895. 24-hour diurnal solar cycle aur EWMA rolling dynamics capture hote hain.<br/>
    • <b>G. Full SkyGuard Hybrid (Proposed):</b> <b>F1 = 0.982, False Alarms &lt; 1.5%</b>. Extreme weather ko scientifically accept karta hai aur sirf genuine sensor faults ko flag karta hai!<br/><br/>
    <b>🎤 Likely Jury Question & Winning Answer:</b><br/>
    <b>Q: 'Ablation study se kya prove hota hai?'</b><br/>
    <i><b>Ans:</b> 'Sir, ablation study prove karti hai ki machine learning akele kafi nahi hai. Jab hum atmospheric thermodynamics (Magnus-Tetens) aur diurnal harmonics ko LightGBM ke sath fuse karte hain, tabhi extreme weather false alarm rate 48.5% se girkar <1.5% hota hai.'</i>"""

    story.append(Paragraph(p2_desc, body_style))
    story.append(PageBreak())

    # ------------------- SECTION 3: FAULT INJECTION SANDBOX -------------------
    story.append(Paragraph("3. Fault Injection Sandbox (Live Interactive Testing)", h1_style))
    if os.path.exists(img3):
        story.append(Image(img3, width=540, height=190))
        story.append(Spacer(1, 6))

    p3_desc = """<b>❓ Yeh Page Kya Hai aur Iska Kaam Kya Hai?</b><br/>
    Yeh evaluators ke liye ek <b>Live Interactive Control Room</b> hai jahan jury ke samne live anomaly inject karke SkyGuard AI ka instant response test kiya ja sakta hai.<br/><br/>
    <b>⚙️ Kaise Work Karta Hai?</b><br/>
    1. <b>Target Station Select karein:</b> Safdarjung AWS, Palam Airport AWS, Lodhi Road AWS.<br/>
    2. <b>Anomaly / Scenario Mode Choose karein:</b><br/>
       • <i>Mode 1: Transient Temperature Spike (+14°C)</i> (Hardware glitch)<br/>
       • <i>Mode 5: Stuck / Frozen ADC Value</i> (Sensor freeze / repeated decimal)<br/>
       • <i>Mode 8: Sensor Calibration Drift (+0.4°C/h)</i> (Transducer aging)<br/>
       • <i>Event 1: Genuine Severe Heatwave</i> (True meteorological heating with RH drop)<br/>
       • <i>Event 2: Severe Convective Squall Line</i> (True cold pool with pressure jump)<br/>
       • <i>Mode 20: Telemetry Bit Flip Sentinel (-999.0)</i> (Corrupted packet)<br/>
    3. <b>'Inject Live Observation' par click karein:</b> Backend 12ms me process karke output, TreeSHAP feature attribution, aur Kalman self-healing preview dikhata hai.<br/><br/>
    <b>🎤 Live Demo Presentation Pitch (Jury ke samne bolne ke liye):</b><br/>
    <i>'Respected Jury, let's inject a +14°C hardware spike on Palam station. Within 12 ms, SkyGuard classifies it as SPIKE with 99.1% confidence. TreeSHAP proves that pressure & humidity stayed flat, confirming it is an isolated sensor glitch. Kalman filter then immediately heals the telemetry stream!'</i>"""

    story.append(Paragraph(p3_desc, body_style))
    story.append(PageBreak())

    # ------------------- SECTION 4: SELF-HEALING RECOVERY -------------------
    story.append(Paragraph("4. Self-Healing Recovery (State-Space Kalman Filter)", h1_style))
    if os.path.exists(img4):
        story.append(Image(img4, width=540, height=190))
        story.append(Spacer(1, 6))

    p4_desc = """<b>❓ Yeh Page Kya Hai aur Iska Kaam Kya Hai?</b><br/>
    Yeh AWS network ki sabse critical operational problem solve karta hai: <b>'Sensor faulty hone par synoptic weather stream me time-series gaps ban jate hain.'</b><br/><br/>
    <b>⚙️ Do Streams Ka Concept (Raw vs Healed):</b><br/>
    • <b>Red Line (Raw Sensor Telemetry):</b> Original uncorrupted raw reading. <i>CRITICAL RULE: Hum raw data ko kabhi overwrite ya delete nahi karte (meteorological audit trail ke liye).</i><br/>
    • <b>Green Dashed Line (Kalman Self-Healed Imputation):</b> Continuous <b>Recursive Bayesian State-Space Filter</b> jo diurnal physics trajectory ke hisab se smooth, physically valid estimate ($32.6^\circ\text{C}$) supply karta hai.<br/><br/>
    <b>⚙️ Mathematical Formulation:</b><br/>
    • <i>Predict Step:</i> $\hat{x}_{k|k-1} = F \hat{x}_{k-1}, \quad P_{k|k-1} = F P_{k-1} F^T + Q$<br/>
    • <i>Measurement Gating:</i> Agar anomaly detect hoti hai, measurement update skip hota hai aur Kalman state estimate automatically time-series continuity maintain karta hai.<br/><br/>
    <b>🎤 Likely Jury Question & Winning Answer:</b><br/>
    <b>Q: 'Kya aap original sensor reading ko replace kar dete ho?'</b><br/>
    <i><b>Ans:</b> 'No Sir! Rule 18 ke mutabiq raw observations cold storage me unaltered save hoti hain. Kalman filter validated stream me self-healed estimate propagate karta hai taaki downstream NWP models ko continuous data mile.'</i>"""

    story.append(Paragraph(p4_desc, body_style))
    story.append(PageBreak())

    # ------------------- SECTION 5: TREESHAP & XAI -------------------
    story.append(Paragraph("5. TreeSHAP & Physics-Informed Explainability (XAI)", h1_style))
    if os.path.exists(img5):
        story.append(Image(img5, width=540, height=190))
        story.append(Spacer(1, 6))

    p5_desc = """<b>❓ Yeh Page Kya Hai aur Iska Kaam Kya Hai?</b><br/>
    AI models par meteorological scientists aur disaster management tabhi trust karenge jab AI apna **Faisla Explain** kare. Yeh page har alert ka exact mathematical aur physical justification deta hai.<br/><br/>
    <b>⚙️ Do Coordinated Explainability Layers:</b><br/>
    1. <b>TreeSHAP Feature Attributions (Upper Panel):</b><br/>
       • Polynomial-time exact Shapley values jo dikhate hain ki kis feature ne risk badhaya (e.g., <code>d_temp_dt: +0.52</code>, <code>thermo_incoherence: +0.38</code>).<br/>
    2. <b>Diagnostic Rule & Physical Evidence (Lower Panel):</b><br/>
       • Mathematical SHAP ko Plain-English Meteorological Alert me convert karta hai:<br/>
       - <i>Headline:</i> 'Transient Hardware Sensor Spike'<br/>
       - <i>Physical Evidence:</i> 'Temperature jumped +14°C in 15 mins while Pressure remained 1004.2 hPa and RH remained 52%. Psychrometric consistency check failed.'<br/>
       - <i>Action Recommendation:</i> 'Reject raw observation. Forward Kalman self-healed estimate. Flag sensor for on-site calibration check.'<br/><br/>
    <b>🎤 Likely Jury Question & Winning Answer:</b><br/>
    <b>Q: 'TreeSHAP kya atmospheric causality prove karta hai?'</b><br/>
    <i><b>Ans:</b> 'Sir, TreeSHAP mathematical model attribution deta hai. Hum usko deterministic thermodynamic laws (Magnus-Tetens Dew Point $T_d \le T$, VPD $\ge 0$) ke sath combine karke physical causality establish karte hain.'</i>"""

    story.append(Paragraph(p5_desc, body_style))
    story.append(PageBreak())

    # ------------------- SECTION 6: REMAINING VIEWS & EDGE DEPLOYMENT -------------------
    story.append(Paragraph("6. Remaining Operational Views & Edge AI Architecture", h1_style))

    p6_desc = """<b>🌐 Baki 5 Dashboard Views Ka Quick Reference:</b><br/>
    • <b>Network Overview (View 1):</b> Regional AWS network health (Safdarjung, Palam, Lodhi, Ayanagar, Ridge), total stations online, active fault counters.<br/>
    • <b>Live AWS Monitor (View 2):</b> 4 simultaneous 15-minute live stream charts (Temp vs Dew Point, Barometric Pressure, RH vs VPD, Anomaly Probability).<br/>
    • <b>Station Detail (View 3):</b> Individual station 48-hour deep dive profile aur Physics Invariant audit ($T_d \le T$, $VPD \ge 0$, Poisson Potential Temp $\theta$).<br/>
    • <b>Alerts & Events (View 4):</b> Incident log with Severity (LOW, MEDIUM, HIGH, CRITICAL), Confidence %, aur CSV Export.<br/>
    • <b>Sensor Health (0-100) (View 5):</b> Har transducer (Temperature, Barometer, Humidity) ka individual 0-100 score aur <b>Predictive Maintenance Risk</b> (HEALTHY, WATCH, DEGRADED, CRITICAL).<br/><br/>
    <b>⚡ Edge AI Microcontroller Deployment (ESP32 / ARM Cortex-M):</b><br/>
    • Standalone C99 Header/Source: <code>skyguard_edge.h</code> aur <code>skyguard_edge.c</code>.<br/>
    • <b>Zero External Dependencies</b>, Zero Heap Allocation.<br/>
    • <b>Inference Latency:</b> <b>42.5 µs</b> per observation.<br/>
    • <b>Memory Footprint:</b> Flash &lt; 8 KB (0.18% of ESP32 4MB), Static SRAM = 128 bytes.<br/><br/>
    <b>🏆 Top 3 Golden Rules for Final Presentation:</b><br/>
    1. <b>Strict 3-Sensor Constraint:</b> 'Sir, humne strictly Temperature, Pressure aur Relative Humidity use kiya hai (no wind/rain dependence).' <br/>
    2. <b>Extreme Weather Disentanglement:</b> 'Heatwave me T badhta hai aur RH ghati hai (psychrometric coupling). Fault me sirf T badhta hai aur baki flat rehte hain.'<br/>
    3. <b>Edge Portability:</b> 'Pura logic ESP32 par bina internet ke sensor head par bhi run ho sakta hai!'"""

    story.append(Paragraph(p6_desc, body_style))

    # Build Document
    doc.build(story)
    print(f"PDF Successfully Generated: {output_pdf_path}")
    return output_pdf_path


if __name__ == "__main__":
    build_pdf()
