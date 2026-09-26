#!/usr/bin/env python3
"""
SkyGuard AI - Complete Operational Dashboard Guide PDF Generator
Creates a comprehensive, high-quality, professional presentation & study PDF.
"""

import os
import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

PDF_OUTPUT_PATH = "/Volumes/T7/SIH/SkyGuard_AI_Complete_Dashboard_Explanation_Guide.pdf"

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#0284c7"))

        # Top Header (Only on pages > 1)
        if self._pageNumber > 1:
            self.drawString(40, 760, "🛡️ SkyGuard AI | MoES / IMD AWS Sentinel (SIH26073)")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748b"))
            self.drawRightString(572, 760, "Complete 10-View Dashboard Master Explanation Guide")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.75)
            self.line(40, 752, 572, 752)

        # Bottom Footer
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(40, 30, "Strict Input Constraint: T, P, RH Only | LightGBM + Kalman EKF + TreeSHAP XAI + C99 Edge")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(572, 30, page_str)
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.75)
        self.line(40, 42, 572, 42)

        self.restoreState()


def create_guide_pdf():
    doc = SimpleDocTemplate(
        PDF_OUTPUT_PATH,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    PRIMARY = colors.HexColor("#0f172a") # Dark Slate
    ACCENT = colors.HexColor("#0284c7")  # Deep Sky Blue
    ACCENT_LIGHT = colors.HexColor("#e0f2fe")
    SUCCESS = colors.HexColor("#059669") # Emerald Green
    SUCCESS_LIGHT = colors.HexColor("#d1fae5")
    WARNING = colors.HexColor("#d97706") # Amber
    WARNING_LIGHT = colors.HexColor("#fef3c7")
    DANGER = colors.HexColor("#dc2626")  # Red
    DANGER_LIGHT = colors.HexColor("#fee2e2")
    PURPLE = colors.HexColor("#7c3aed")
    PURPLE_LIGHT = colors.HexColor("#ede9fe")
    BG_CARD = colors.HexColor("#f8fafc")
    BORDER_COLOR = colors.HexColor("#cbd5e1")
    TEXT_MAIN = colors.HexColor("#1e293b")
    TEXT_MUTED = colors.HexColor("#475569")

    # Typography Styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=PRIMARY,
        alignment=1, # Center
        spaceAfter=8
    )

    subtitle_style = ParagraphStyle(
        'CoverSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=ACCENT,
        alignment=1,
        spaceAfter=18
    )

    h1_style = ParagraphStyle(
        'ChapterH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=ACCENT,
        spaceBefore=10,
        spaceAfter=6
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=PRIMARY,
        spaceBefore=8,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=TEXT_MAIN,
        spaceAfter=6
    )

    body_bold = ParagraphStyle(
        'BodyDarkBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=TEXT_MAIN
    )

    jury_style = ParagraphStyle(
        'JuryPitch',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.2,
        leading=13.2,
        textColor=colors.HexColor("#065f46")
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#0f172a")
    )

    story = []

    # ==================== COVER / EXECUTIVE SUMMARY ====================
    story.append(Spacer(1, 10))
    story.append(Paragraph("🛡️ SkyGuard AI - Operational Dashboard Guide", title_style))
    story.append(Paragraph("India Meteorological Department (IMD) & MoES Automatic Weather Station (AWS) Sentinel<br/><b>Problem Statement ID: SIH26073 | Disaster Management Theme</b>", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceBefore=0, spaceAfter=12))

    summary_data = [
        [Paragraph("<b>Key Technical Pillar</b>", body_bold), Paragraph("<b>Operational Implementation in SkyGuard AI</b>", body_bold)],
        [Paragraph("<b>Strict Input Constraint</b>", body_style), Paragraph("Accepts ONLY 3 raw meteorological observations: <b>Temperature (°C), Pressure (hPa), Relative Humidity (%)</b>.", body_style)],
        [Paragraph("<b>Machine Learning Core</b>", body_style), Paragraph("LightGBM Multi-Class Classifier with <b>99.79% Test Accuracy</b> across 8 discrete operational categories.", body_style)],
        [Paragraph("<b>Deterministic Physics Invariants</b>", body_style), Paragraph("Enforces Clausius-Clapeyron, Magnus-Tetens dew point (<i>T_d &le; T</i>), Vapor Pressure Deficit (<i>VPD &ge; 0</i>), & Potential Temp (<i>&theta;</i>).", body_style)],
        [Paragraph("<b>Severe Weather vs Fault</b>", body_style), Paragraph("Disentangles genuine convective squalls / severe heatwaves from sensor hardware bugs using joint dynamics.", body_style)],
        [Paragraph("<b>Self-Healing & Imputation</b>", body_style), Paragraph("Real-time State-Space <b>Kalman Filter (EKF/UKF)</b> stream with 100% raw data preserved in WMO cold storage.", body_style)],
        [Paragraph("<b>Explainable AI (XAI)</b>", body_style), Paragraph("Exact polynomial <b>TreeSHAP</b> feature attributions + English meteorological diagnostic explanation rules.", body_style)],
        [Paragraph("<b>Edge Deployment</b>", body_style), Paragraph("Pure C99 standalone library (<b>42.5 &micro;s execution</b>, 3.2 KB RAM) for ESP32 / STM32 datalogger boards.", body_style)],
        [Paragraph("<b>Docker Containerization</b>", body_style), Paragraph("Instant one-click production container (<b>Port 8000</b>) bundling REST API, WebSockets, & UI Dashboard.", body_style)]
    ]
    summary_table = Table(summary_data, colWidths=[160, 372])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), ACCENT_LIGHT),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 14))

    # Architecture Overview Callout
    arch_box = [
        [Paragraph("<b>📌 Dashboard Quick Access & Live Operation:</b><br/>"
                   "• <b>Live URL:</b> <code>http://localhost:8000/</code> (Docker container <code>skyguard_ai_server</code>)<br/>"
                   "• <b>10 Interactive Views:</b> Sidebar se kisi bhi view par click karke real-time monitoring aur evaluation dekha ja sakta hai.<br/>"
                   "• <b>Real-Time Telemetry:</b> WebSocket <code>/ws/live</code> stream ke through har second telemetry tick aati hai.", body_style)]
    ]
    arch_table = Table(arch_box, colWidths=[532])
    arch_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_CARD),
        ('BOX', (0,0), (-1,-1), 1, ACCENT),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(arch_table)
    story.append(PageBreak())

    # ==================== VIEW 1: NETWORK OVERVIEW ====================
    story.append(Paragraph("1. 🌐 Network Overview (Regional AWS Sentinel Master)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceBefore=0, spaceAfter=8))

    story.append(Paragraph("<b>Maksad (Primary Purpose):</b> Pure region (e.g. Delhi NCR / State AWS Network) ke sabhi Automatic Weather Stations ki overall synoptic health, active faults, aur regional alerts ko single glance me monitor karna.", body_style))
    
    story.append(Paragraph("<b>UI Components & Elements (Kya Kya Dikhta Hai):</b>", h2_style))
    v1_items = [
        [Paragraph("• <b>4 Top KPI Cards:</b><br/>"
                   "  1. <b>Active Stations (5):</b> 100% online telemetry status.<br/>"
                   "  2. <b>Network Health Index (96.4%):</b> Regional aggregate sensor reliability.<br/>"
                   "  3. <b>Extreme Weather Events (0):</b> Coherent atmospheric heatwave/squall warnings.<br/>"
                   "  4. <b>Active Sensor Faults (0):</b> Hardware faults under active self-healing.", body_style)],
        [Paragraph("• <b>Regional Automatic Weather Station Table:</b><br/>"
                   "  Displays <i>Station ID, Location Name, Temperature (°C), Pressure (hPa), Humidity (%), Magnus-Tetens Dew Point ($T_d$ in °C), Health Score (%), Status (HEALTHY/FAULT)</i>.", body_style)],
        [Paragraph("• <b>Recent Critical Sentinel Alerts Stream:</b><br/>"
                   "  Live scrollable event feed with color-coded severity badges (Green: Normal, Blue: Extreme Weather, Yellow/Red: Sensor Faults).", body_style)]
    ]
    t_v1 = Table(v1_items, colWidths=[532])
    t_v1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_CARD),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 6)
    ]))
    story.append(t_v1)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Background AI & Physics Engine:</b>", h2_style))
    story.append(Paragraph("Har station se aane wale raw $T, P, RH$ par instantly <b>Magnus-Tetens Dew Point formula</b> compute hota hai: "
                           "$$T_d = \\frac{243.04 \\cdot \\left(\\ln(\\frac{RH}{100}) + \\frac{17.625 \\cdot T}{243.04 + T}\\right)}{17.625 - \\left(\\ln(\\frac{RH}{100}) + \\frac{17.625 \\cdot T}{243.04 + T}\\right)}$$ "
                           "Agar kisi station ka $T_d > T$ nikalta hai, toh yeh thermodynamics ka physical violation hai aur system instantly health index penalize karta hai.", body_style))

    story.append(Paragraph("<b>🎯 Jury / Evaluator ke Samne Kya Bolein (Pitch):</b>", h2_style))
    j1 = [[Paragraph("<i>'Sir, yeh Network Overview IMD ke central control room ka master landing page hai. Yahan single screen par pata chal jata hai ki pure Delhi NCR me kitne AWS active hain, unki health kya hai, aur kisi station par physical invariant violate toh nahi ho raha. Single click me kisi bhi anomalous station ko isolate kiya ja sakta hai.'</i>", jury_style)]]
    tj1 = Table(j1, colWidths=[532])
    tj1.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), SUCCESS_LIGHT), ('BOX', (0,0), (-1,-1), 1, SUCCESS), ('PADDING', (0,0), (-1,-1), 8)]))
    story.append(tj1)
    story.append(PageBreak())

    # ==================== VIEW 2: LIVE AWS MONITOR ====================
    story.append(Paragraph("2. 📈 Live AWS Stream Monitor (Real-Time Waveforms)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceBefore=0, spaceAfter=8))

    story.append(Paragraph("<b>Maksad (Primary Purpose):</b> Real-time continuous 15-minute telemetry streams ko high-resolution interactive waveforms me render karna aur simultaneous multivariate correlations ko visually track karna.", body_style))
    
    story.append(Paragraph("<b>UI Components & Elements (Charo Live Graphs):</b>", h2_style))
    v2_items = [
        [Paragraph("<b>Graph 1: Temperature (°C) vs Magnus-Tetens Dew Point ($T_d$)</b><br/>"
                   "• <b>Solid Blue Line:</b> Ambient Temperature (range: 18°C - 42°C).<br/>"
                   "• <b>Dashed Green Line:</b> Physical Dew Point ($T_d$). WMO standard ke mutabik green line hamesha blue line ke niche honi chahiye ($T_d \\le T$).", body_style)],
        [Paragraph("<b>Graph 2: Atmospheric Pressure (hPa) - Barometric Tide</b><br/>"
                   "• <b>Vibrant Purple Waveform:</b> High-precision barometric pressure (range: 1002 - 1018 hPa).<br/>"
                   "• Shows 12-hour atmospheric thermal tidal oscillations cleanly without flatlining.", body_style)],
        [Paragraph("<b>Graph 3: Relative Humidity (%) & Vapor Pressure Deficit (VPD in hPa)</b><br/>"
                   "• <b>Dual-Axis Coupling:</b> Left Axis me Relative Humidity (0% - 100%) aur Right Axis me Vapor Pressure Deficit (0 - 35 hPa).<br/>"
                   "• Inverse thermodynamic relationship ($RH \\uparrow \\implies VPD \\downarrow$) ko live monitor karta hai.", body_style)],
        [Paragraph("<b>Graph 4: AI Anomaly Probability Score (0.0 to 1.0)</b><br/>"
                   "• <b>Red Calibrated Anomaly Risk:</b> Normal state me score &lt; 0.05 rehta hai. Sensor spike, drift, ya fault aane par curve 0.90+ spike karti hai.", body_style)]
    ]
    t_v2 = Table(v2_items, colWidths=[532])
    t_v2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_CARD),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 6)
    ]))
    story.append(t_v2)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Background AI & Physics Engine:</b>", h2_style))
    story.append(Paragraph("Client side par WebSocket connection (<code>ws://localhost:8000/ws/live</code>) real-time streaming data push karta hai. Backend me LightGBM inference model har 15-minute tick par <b>24 temporal & physical derived features</b> calculate karke probability score nikalta hai.", body_style))

    story.append(Paragraph("<b>🎯 Jury / Evaluator ke Samne Kya Bolein (Pitch):</b>", h2_style))
    j2 = [[Paragraph("<i>'Sir, Live Monitor me hum teeno coupled meteorological variables ko simultaneously track karte hain. Notice kijiye ki jab temperature badhta hai toh Relative Humidity natural physics ke tahat drop hoti hai aur VPD badhta hai. Agar koi sensor corrupt data bhejta hai, toh yeh multi-variate coherence toot jaati hai aur AI Anomaly Score immediately spike ho jaata hai.'</i>", jury_style)]]
    tj2 = Table(j2, colWidths=[532])
    tj2.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), SUCCESS_LIGHT), ('BOX', (0,0), (-1,-1), 1, SUCCESS), ('PADDING', (0,0), (-1,-1), 8)]))
    story.append(tj2)
    story.append(PageBreak())

    # ==================== VIEW 3: STATION DETAIL ====================
    story.append(Paragraph("3. 📡 Station Detail Analysis & Thermodynamic Audit", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceBefore=0, spaceAfter=8))

    story.append(Paragraph("<b>Maksad (Primary Purpose):</b> Kisi specific AWS (jaise Safdarjung, Palam, Lodhi Road) ka 48-hour historical synoptic profile analyze karna aur physical invariants ka rigorous thermodynamic audit perform karna.", body_style))
    
    story.append(Paragraph("<b>UI Components & Elements (Kya Kya Dikhta Hai):</b>", h2_style))
    v3_items = [
        [Paragraph("• <b>Station Meta Banner:</b> Station Name, Latitude, Longitude, Elevation (MSL), Station ID, aur Overall Health Badge (e.g. HEALTH: 98/100).", body_style)],
        [Paragraph("• <b>48-Hour Historical Observation Profile (Large Canvas):</b><br/>"
                   "  - <b>Left Axis (Blue):</b> 48-hour Diurnal Temperature Swing (Night: ~24°C, Afternoon Peak: ~36°C).<br/>"
                   "  - <b>Right Axis (Purple):</b> Semi-diurnal Barometric Pressure Tide (1008 - 1014 hPa).", body_style)],
        [Paragraph("• <b>Physics Invariant Audit Panel:</b><br/>"
                   "  1. <b>Dew Point Condition ($T_d \\le T$):</b> PASS (Checks if dew point depression $T - T_d > 0$).<br/>"
                   "  2. <b>Vapor Pressure Deficit ($VPD \\ge 0$):</b> PASS (Ensures atmospheric saturation bounds).<br/>"
                   "  3. <b>Potential Temperature ($\\theta$):</b> $\\theta = T \\cdot (1000/P)^{0.286}$ in Kelvin (measures atmospheric stability).<br/>"
                   "  4. <b>Spatial Neighbor Consistency:</b> Compares target AWS with neighboring stations using standard elevation lapse rate ($0.0065 \\text{ K/m}$).", body_style)]
    ]
    t_v3 = Table(v3_items, colWidths=[532])
    t_v3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_CARD),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 6)
    ]))
    story.append(t_v3)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>🎯 Jury / Evaluator ke Samne Kya Bolein (Pitch):</b>", h2_style))
    j3 = [[Paragraph("<i>'Sir, yeh view kisi bhi individual station ka deep forensic audit karta hai. 48-ghante ki synoptic curve standard diurnal solar cycle ko demonstrate karti hai. Sath hi, right side me hum WMO aur atmospheric thermodynamics ke 4 strictly deterministic laws ko live audit karte hain — ensuring complete physical validity.'</i>", jury_style)]]
    tj3 = Table(j3, colWidths=[532])
    tj3.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), SUCCESS_LIGHT), ('BOX', (0,0), (-1,-1), 1, SUCCESS), ('PADDING', (0,0), (-1,-1), 8)]))
    story.append(tj3)
    story.append(PageBreak())

    # ==================== VIEW 4: ALERTS & EVENTS ====================
    story.append(Paragraph("4. 🚨 Alerts & Incident Log (Operational Audit Trail)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceBefore=0, spaceAfter=8))

    story.append(Paragraph("<b>Maksad (Primary Purpose):</b> IMD duty meteorologists aur maintenance engineers ke liye sabhi classified anomaly incidents aur severe weather warnings ka persistent, searchable, aur exportable audit log maintain karna.", body_style))
    
    story.append(Paragraph("<b>UI Components & Elements (Kya Kya Dikhta Hai):</b>", h2_style))
    v4_items = [
        [Paragraph("• <b>Incident Log Table:</b><br/>"
                   "  - <b>Alert ID:</b> Unique sequential identifier (e.g. ALT_1042).<br/>"
                   "  - <b>Timestamp (UTC):</b> Exact time of anomaly detection.<br/>"
                   "  - <b>Station ID:</b> Originating Automatic Weather Station.<br/>"
                   "  - <b>Classification:</b> AI Predicted category (e.g. SPIKE, FROZEN, DRIFT, GENUINE_EXTREME_WEATHER).<br/>"
                   "  - <b>Severity:</b> Color-coded tag (LOW, MEDIUM, HIGH, CRITICAL).<br/>"
                   "  - <b>Confidence:</b> Multi-class probabilistic model certainty (e.g. 98.4%).<br/>"
                   "  - <b>Diagnostic Summary:</b> Actionable English diagnosis of the failure mode.", body_style)],
        [Paragraph("• <b>Export CSV Button:</b> Allows instant export of incident logs for shift-duty reporting and IMD compliance.", body_style)]
    ]
    t_v4 = Table(v4_items, colWidths=[532])
    t_v4.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), BG_CARD), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 6)]))
    story.append(t_v4)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>🎯 Jury / Evaluator ke Samne Kya Bolein (Pitch):</b>", h2_style))
    j4 = [[Paragraph("<i>'Sir, alert fatigue ko khatam karne ke liye humara system raw thresholding ki jagah calibrated multi-class AI use karta hai. Alerts table me aap dekh sakte hain ki false alarms eliminate ho gaye hain, aur severe meteorological events (jaise Squall lines) ko sensor fault se alag highlight kiya gaya hai.'</i>", jury_style)]]
    tj4 = Table(j4, colWidths=[532])
    tj4.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), SUCCESS_LIGHT), ('BOX', (0,0), (-1,-1), 1, SUCCESS), ('PADDING', (0,0), (-1,-1), 8)]))
    story.append(tj4)
    story.append(PageBreak())

    # ==================== VIEW 5: SENSOR HEALTH ====================
    story.append(Paragraph("5. 🩺 Sensor Health Index (0-100) & Predictive Maintenance", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceBefore=0, spaceAfter=8))

    story.append(Paragraph("<b>Maksad (Primary Purpose):</b> Har individual sensor transducer (Thermistor, Barometer, Capacitive Hygrometer) ki health ko continuous 0-100 scale par track karna aur catastrophic failure se pehle predictive maintenance schedule karna.", body_style))
    
    story.append(Paragraph("<b>UI Components & Elements (Kya Kya Dikhta Hai):</b>", h2_style))
    v5_items = [
        [Paragraph("• <b>Temperature Sensor Health:</b> 0-100% Index (Monitors thermal response time & ADC noise).", body_style)],
        [Paragraph("• <b>Pressure Sensor Health:</b> 0-100% Index (Tracks barometer hysteresis & diurnal harmonic alignment).", body_style)],
        [Paragraph("• <b>Humidity Sensor Health:</b> 0-100% Index (Detects capacitive fouling, saturation lockup, & drift).", body_style)],
        [Paragraph("• <b>Maintenance Risk Level:</b> Dynamic risk category (LOW / MEDIUM / HIGH / URGENT) + Next scheduled calibration countdown.", body_style)],
        [Paragraph("• <b>Diagnostic Recommendations Box:</b> Natural language action recommendations (e.g., <i>'All transducers operating within calibrated tolerances. No hysteresis observed in the last 24 hours.'</i>).", body_style)]
    ]
    t_v5 = Table(v5_items, colWidths=[532])
    t_v5.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), BG_CARD), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 6)]))
    story.append(t_v5)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Background Health Tracking Equation:</b>", h2_style))
    story.append(Paragraph("$$H_t = 100 - \\left( w_f \\cdot \\sum_{k=1}^N f_k + w_d \\cdot |\\Delta_{drift}| + w_n \\cdot (1 - SNR) \\right)$$ "
                           "Agar kisi sensor me continuous small drift ya intermittent spikes aate hain, toh health score gradually 98% -> 75% -> 50% degrade hota hai, triggering preventive field dispatch.", body_style))

    story.append(Paragraph("<b>🎯 Jury / Evaluator ke Samne Kya Bolein (Pitch):</b>", h2_style))
    j5 = [[Paragraph("<i>'Sir, yeh module reactive maintenance ko predictive maintenance me convert karta hai. Agar humidity sensor dhire-dhire foul ho raha hai, toh pura station fail hone ka wait karne ki jagah humara system health score ko degrade karke pehle hi alert bhej deta hai.'</i>", jury_style)]]
    tj5 = Table(j5, colWidths=[532])
    tj5.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), SUCCESS_LIGHT), ('BOX', (0,0), (-1,-1), 1, SUCCESS), ('PADDING', (0,0), (-1,-1), 8)]))
    story.append(tj5)
    story.append(PageBreak())

    # ==================== VIEW 6: TREESHAP & XAI ====================
    story.append(Paragraph("6. 🧠 TreeSHAP & Physics Explainable AI (XAI)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceBefore=0, spaceAfter=8))

    story.append(Paragraph("<b>Maksad (Primary Purpose):</b> Black-box ML predictions ko transparent banana. Har decision ke piche ka exact mathematical feature contribution aur physical atmospheric justification show karna.", body_style))
    
    story.append(Paragraph("<b>UI Components & Elements (Kya Kya Dikhta Hai):</b>", h2_style))
    v6_items = [
        [Paragraph("• <b>TreeSHAP Feature Attribution Bars:</b><br/>"
                   "  - Exact local SHAP values ($\phi_i$) for top features (e.g. <code>dT_dt: +0.4281</code>, <code>vpd_deviation: +0.2190</code>, <code>spatial_consensus_delta: -0.1140</code>).<br/>"
                   "  - Positive bars (Blue/Purple) indicate evidence pushing towards anomaly; Negative bars (Green) indicate evidence supporting normal state.", body_style)],
        [Paragraph("• <b>Diagnostic Rule & Physical Evidence Card:</b><br/>"
                   "  Translates mathematical SHAP weights into human-readable meteorological proof (e.g., <i>'Temperature rate of change +14.2°C/15min exceeds physical dry adiabatic limit without corresponding pressure drop.'</i>).", body_style)]
    ]
    t_v6 = Table(v6_items, colWidths=[532])
    t_v6.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), BG_CARD), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 6)]))
    story.append(t_v6)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>🎯 Jury / Evaluator ke Samne Kya Bolein (Pitch):</b>", h2_style))
    j6 = [[Paragraph("<i>'Sir, meteorologists aur operational scientists black-box AI models par blind trust nahi kar sakte. TreeSHAP exact game-theoretic mathematical proof deta hai ki model ne yeh decision kyun liya. Sath hi physical evidence card batata hai ki kaunsa atmospheric thermodynamic law violate hua.'</i>", jury_style)]]
    tj6 = Table(j6, colWidths=[532])
    tj6.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), SUCCESS_LIGHT), ('BOX', (0,0), (-1,-1), 1, SUCCESS), ('PADDING', (0,0), (-1,-1), 8)]))
    story.append(tj6)
    story.append(PageBreak())

    # ==================== VIEW 7: SELF-HEALING RECOVERY ====================
    story.append(Paragraph("7. 🔄 Real-Time State-Space Kalman Self-Healing", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceBefore=0, spaceAfter=8))

    story.append(Paragraph("<b>Maksad (Primary Purpose):</b> Sensor fault hone par Numerical Weather Prediction (NWP) models ke stream ko uninterrupted rakhna by computing continuous state-space Kalman estimates — bina raw telemetry ko overwrite kiye.", body_style))
    
    story.append(Paragraph("<b>UI Components & Elements (Kya Kya Dikhta Hai):</b>", h2_style))
    v7_items = [
        [Paragraph("• <b>4 Top KPI Cards:</b><br/>"
                   "  1. <b>State-Space Model:</b> Extended Kalman Filter (EKF) / Unscented Kalman Filter.<br/>"
                   "  2. <b>Imputation Accuracy:</b> 99.4% (RMSE: 0.14°C / 0.18 hPa).<br/>"
                   "  3. <b>Telemetry Preservation:</b> 100% Raw Data Preserved in Cold Storage.<br/>"
                   "  4. <b>Fallback Redundancy:</b> Spatial Kriging / Inverse Distance Weighting (IDW).", body_style)],
        [Paragraph("• <b>Raw vs Healed Comparison Waveform (Large 360px Canvas):</b><br/>"
                   "  - <b>Red Dots:</b> Corrupted Raw Sensor Telemetry (e.g. severe +15°C hardware transient spike reaching 48°C).<br/>"
                   "  - <b>Green Dashed Line:</b> Continuous State-Space Kalman Self-Healed Imputation (smoothly tracking true atmospheric state at ~33°C).<br/>"
                   "  - <b>WMO Cold Storage Compliance:</b> Demonstrates that raw erroneous observation is never lost, while operational models receive clean imputed data.", body_style)]
    ]
    t_v7 = Table(v7_items, colWidths=[532])
    t_v7.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), BG_CARD), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 6)]))
    story.append(t_v7)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>State-Space Kalman Filter Equations:</b>", h2_style))
    story.append(Paragraph("$$\\hat{x}_{k|k-1} = F_k \\hat{x}_{k-1|k-1} + B_k u_k, \\quad P_{k|k-1} = F_k P_{k-1|k-1} F_k^T + Q_k$$ "
                           "$$K_k = P_{k|k-1} H_k^T (H_k P_{k|k-1} H_k^T + R_k)^{-1}, \\quad \\hat{x}_{k|k} = \\hat{x}_{k|k-1} + K_k (z_k - H_k \\hat{x}_{k|k-1})$$ "
                           "Fault detection par measurement covariance $R_k \\to \\infty$, jisse filter purely state transition physics par predict karta hai.", body_style))

    story.append(Paragraph("<b>🎯 Jury / Evaluator ke Samne Kya Bolein (Pitch):</b>", h2_style))
    j7 = [[Paragraph("<i>'Sir, IMD me data loss synoptic forecasting ke liye bohot bada threat hota hai. Humara Self-Healing module Dual-Pipeline architecture use karta hai: Raw corrupted data WMO standard cold storage me audit ke liye safe rehta hai, jabki downstream NWP weather models ko Kalman filter ka continuous, physically coherent imputed stream milta hai.'</i>", jury_style)]]
    tj7 = Table(j7, colWidths=[532])
    tj7.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), SUCCESS_LIGHT), ('BOX', (0,0), (-1,-1), 1, SUCCESS), ('PADDING', (0,0), (-1,-1), 8)]))
    story.append(tj7)
    story.append(PageBreak())

    # ==================== VIEW 8: MODEL PERFORMANCE & ABLATION ====================
    story.append(Paragraph("8. 📊 Model Benchmark & Comprehensive Ablation Study", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceBefore=0, spaceAfter=8))

    story.append(Paragraph("<b>Maksad (Primary Purpose):</b> SIH Jury ke technical defense ke liye scientific proof provide karna ki hamari proposed hybrid architecture existing conventional methods se superior kyun hai.", body_style))
    
    story.append(Paragraph("<b>Scientific Ablation Study Benchmark Table:</b>", h2_style))
    ablation_data = [
        [Paragraph("<b>Architecture Configuration</b>", body_bold), Paragraph("<b>F1-Score</b>", body_bold), Paragraph("<b>Severe Weather False Alarm</b>", body_bold), Paragraph("<b>Explainability</b>", body_bold), Paragraph("<b>Edge Deploy</b>", body_bold)],
        [Paragraph("A. Conventional Rule QC (WMO-8)", body_style), Paragraph("0.742", body_style), Paragraph("<font color='#dc2626'>48.5% (Very High)</font>", body_style), Paragraph("Fixed Bounds", body_style), Paragraph("Yes", body_style)],
        [Paragraph("B. Raw LightGBM (T/P/RH only)", body_style), Paragraph("0.835", body_style), Paragraph("<font color='#dc2626'>32.0% (High)</font>", body_style), Paragraph("Black-Box", body_style), Paragraph("Yes", body_style)],
        [Paragraph("C. Physics Features + LightGBM", body_style), Paragraph("0.912", body_style), Paragraph("12.5%", body_style), Paragraph("Thermodynamics", body_style), Paragraph("Yes", body_style)],
        [Paragraph("D. Temporal Features + LightGBM", body_style), Paragraph("0.895", body_style), Paragraph("18.0%", body_style), Paragraph("Harmonics", body_style), Paragraph("Yes", body_style)],
        [Paragraph("<b>G. Full SkyGuard Hybrid (Ours)</b>", body_bold), Paragraph("<b><font color='#059669'>0.982</font></b>", body_bold), Paragraph("<b><font color='#059669'>&lt; 1.5% (Minimal)</font></b>", body_bold), Paragraph("<b>TreeSHAP + Physics</b>", body_bold), Paragraph("<b>ESP32 (42&micro;s)</b>", body_bold)]
    ]
    t_abl = Table(ablation_data, colWidths=[150, 70, 140, 100, 72])
    t_abl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), ACCENT_LIGHT),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,5), (-1,5), SUCCESS_LIGHT),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(t_abl)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>🎯 Jury / Evaluator ke Samne Kya Bolein (Pitch):</b>", h2_style))
    j8 = [[Paragraph("<i>'Sir, conventional WMO-8 quality control rules 48.5% genuine extreme weather events (jaise heatwaves aur thunderstorms) ko galti se sensor fault declare kar dete the. Hamare ablation study se prove hota hai ki jab hum Physics Features + Temporal Diurnal Harmonics + LightGBM combine karte hain, toh False Alarm Rate 48.5% se girkar sirf 1.5% reh jata hai.'</i>", jury_style)]]
    tj8 = Table(j8, colWidths=[532])
    tj8.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), SUCCESS_LIGHT), ('BOX', (0,0), (-1,-1), 1, SUCCESS), ('PADDING', (0,0), (-1,-1), 8)]))
    story.append(tj8)
    story.append(PageBreak())

    # ==================== VIEW 9: FAULT INJECTION SANDBOX ====================
    story.append(Paragraph("9. ⚡ Fault Injection Sandbox (Interactive Live Harness)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceBefore=0, spaceAfter=8))

    story.append(Paragraph("<b>Maksad (Primary Purpose):</b> Jury ke samne live, interactive evaluation demonstrate karna jahan kisi bhi station par 26 hardware fault modes ya genuine extreme weather events ko on-the-fly inject kiya ja sake.", body_style))
    
    story.append(Paragraph("<b>UI Components & Elements (Kya Kya Dikhta Hai):</b>", h2_style))
    v9_items = [
        [Paragraph("• <b>Target Station Dropdown:</b> Choose from Safdarjung, Palam Airport, Lodhi Road, Ayanagar, or Delhi Ridge.", body_style)],
        [Paragraph("• <b>Scenario / Anomaly Mode Dropdown (26 Fault Modes + Events):</b><br/>"
                   "  - <i>Mode 1:</i> Transient Temperature Spike (+14°C)<br/>"
                   "  - <i>Mode 5:</i> Stuck / Frozen ADC Transducer Value<br/>"
                   "  - <i>Mode 8:</i> Calibration Drift (+0.4°C/hr gradual drift)<br/>"
                   "  - <i>Event 1:</i> Genuine Severe Heatwave (T > 45°C, coherent atmospheric response)<br/>"
                   "  - <i>Event 2:</i> Severe Convective Squall Line (Rapid pressure surge + temp drop)<br/>"
                   "  - <i>Mode 20:</i> Telemetry Bit Flip Sentinel (-999.0 / corrupted bits)", body_style)],
        [Paragraph("• <b>'Inject Live Observation' Button:</b> Triggers instant live inference via FastAPI endpoint <code>/simulate-anomaly</code>.", body_style)],
        [Paragraph("• <b>Live AI Sentinel Real-Time Response Box:</b> Outputs complete JSON telemetry response, classification, confidence, TreeSHAP bar updates, and physical evidence.", body_style)]
    ]
    t_v9 = Table(v9_items, colWidths=[532])
    t_v9.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), BG_CARD), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 6)]))
    story.append(t_v9)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>🎯 Jury / Evaluator ke Samne Kya Bolein (Pitch):</b>", h2_style))
    j9 = [[Paragraph("<i>'Sir, hamare system ki reliability test karne ke liye humne Sandbox build kiya hai. Aap koi bhi station aur koi bhi anomaly mode select karke inject karein — AI Sentinel 1 millisecond ke andar decision, confidence percentage, aur exact physical explanation ke sath live response dega.'</i>", jury_style)]]
    tj9 = Table(j9, colWidths=[532])
    tj9.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), SUCCESS_LIGHT), ('BOX', (0,0), (-1,-1), 1, SUCCESS), ('PADDING', (0,0), (-1,-1), 8)]))
    story.append(tj9)
    story.append(PageBreak())

    # ==================== VIEW 10: DATASET & PROVENANCE ====================
    story.append(Paragraph("10. 📋 Dataset Lineage & Governance Provenance", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceBefore=0, spaceAfter=8))

    story.append(Paragraph("<b>Maksad (Primary Purpose):</b> Training, validation, aur benchmarking datasets ka complete scientific lineage aur governance traceability maintain karna.", body_style))
    
    story.append(Paragraph("<b>Dataset Sources Matrix:</b>", h2_style))
    prov_data = [
        [Paragraph("<b>Provenance Tag</b>", body_bold), Paragraph("<b>Data Source Name</b>", body_bold), Paragraph("<b>Provider Portal</b>", body_bold), Paragraph("<b>Role in SkyGuard AI</b>", body_bold), Paragraph("<b>Variables</b>", body_bold)],
        [Paragraph("IMD_AWS", body_style), Paragraph("India Meteorological Dept AWS", body_style), Paragraph("dsp.imdpune.gov.in", body_style), Paragraph("Primary Production Telemetry Ingest", body_style), Paragraph("T, P, RH Only", body_style)],
        [Paragraph("NOAA_ISD", body_style), Paragraph("Integrated Surface Database", body_style), Paragraph("ncei.noaa.gov", body_style), Paragraph("Multi-Station Global Benchmark", body_style), Paragraph("Air Temp, SLP, RH", body_style)],
        [Paragraph("ERA5", body_style), Paragraph("Copernicus Climate Service Reanalysis", body_style), Paragraph("cds.climate.copernicus.eu", body_style), Paragraph("Climatological Baseline & Reference", body_style), Paragraph("t2m, sp, r (Ref only)", body_style)],
        [Paragraph("SYNTHETIC", body_style), Paragraph("SkyGuard Physics Simulation Engine", body_style), Paragraph("Internal Diurnal Engine", body_style), Paragraph("26 Fault Modes & Extreme Weather Gen", body_style), Paragraph("T, P, RH Coupled", body_style)]
    ]
    t_prov = Table(prov_data, colWidths=[80, 130, 110, 132, 80])
    t_prov.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), ACCENT_LIGHT),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    story.append(t_prov)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>🎯 Jury / Evaluator ke Samne Kya Bolein (Pitch):</b>", h2_style))
    j10 = [[Paragraph("<i>'Sir, data integrity ke liye hum WMO standard data provenance follow karte hain. Humara system real IMD AWS datasets, NOAA global benchmarks, aur physics-based synthetic generators se train kiya gaya hai — ensuring 100% auditable lineage.'</i>", jury_style)]]
    tj10 = Table(j10, colWidths=[532])
    tj10.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), SUCCESS_LIGHT), ('BOX', (0,0), (-1,-1), 1, SUCCESS), ('PADDING', (0,0), (-1,-1), 8)]))
    story.append(tj10)
    story.append(PageBreak())

    # ==================== DOCKER & ARCHITECTURE CHEATSHEET ====================
    story.append(Paragraph("11. 🐳 Docker & Architecture Master Cheatsheet", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceBefore=0, spaceAfter=8))

    story.append(Paragraph("<b>Docker Ka Role & Explanation (Jab Jury Pooche):</b>", h2_style))
    docker_points = [
        [Paragraph("• <b>Zero-Setup Production Deployment:</b> Docker humare pure stack (Python 3.11, LightGBM, FastAPI, WebSocket Server, C99 Edge Compiler, aur Dashboard) ko ek isolated container me pack kar deta hai.", body_style)],
        [Paragraph("• <b>Cloud & Edge Agnostic:</b> Chahe IMD ka central Linux server ho, state disaster management center ka server ho, ya AWS/Azure cloud — <code>docker compose up -d</code> run karte hi pura system without any dependency conflict live ho jata hai.", body_style)],
        [Paragraph("• <b>High-Availability & Health Monitoring:</b> Container me healthcheck endpoint (<code>/health</code>) configured hai jo har 10 seconds me engine status monitor karta hai.", body_style)],
        [Paragraph("• <b>Live Volume Mounts:</b> <code>./dashboard:/app/dashboard</code> mount kiya gaya hai taaki frontend live sync rahe.", body_style)]
    ]
    t_dk = Table(docker_points, colWidths=[532])
    t_dk.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), BG_CARD), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 6)]))
    story.append(t_dk)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>⚡ 3-Minute SIH Winning Pitch Script:</b>", h2_style))
    pitch_box = [
        [Paragraph("<b>Opening (0:00 - 0:45):</b> <i>'Respected Jury, Automatic Weather Stations are the backbone of early disaster warnings in India. But today, IMD AWS networks face two huge challenges: high sensor failure rates due to extreme weather, and up to 48% false alarms where genuine heatwaves or squalls are misclassified as sensor bugs.'</i><br/><br/>"
                   "<b>Solution (0:45 - 1:45):</b> <i>'Introducing <b>SkyGuard AI</b> — a physics-infused operational sentinel that works under strict real-world constraints: using <b>Temperature, Pressure, and Relative Humidity ONLY</b>. We combine deterministic thermodynamic laws (Magnus-Tetens Dew Point, Vapor Pressure Deficit), diurnal harmonics, and LightGBM machine learning to achieve <b>99.79% accuracy with under 1.5% false alarms</b>.'</i><br/><br/>"
                   "<b>Self-Healing & Edge (1:45 - 2:30):</b> <i>'We dont just detect faults — we heal them. Our real-time <b>State-Space Kalman Filter</b> provides uninterrupted NWP streams while strictly preserving 100% of raw data in cold storage. Plus, our pure C99 inference engine runs in just <b>42.5 microseconds</b> directly on low-cost ESP32 datalogger microcontrollers at the edge.'</i><br/><br/>"
                   "<b>Closing (2:30 - 3:00):</b> <i>'SkyGuard AI is fully containerized with Docker, explainable with TreeSHAP, and ready for immediate deployment across all 1,000+ IMD Automatic Weather Stations. Thank you!'</i>", jury_style)]
    ]
    t_pitch = Table(pitch_box, colWidths=[532])
    t_pitch.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), SUCCESS_LIGHT), ('BOX', (0,0), (-1,-1), 1.5, SUCCESS), ('PADDING', (0,0), (-1,-1), 8)]))
    story.append(t_pitch)

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated Master PDF: {PDF_OUTPUT_PATH}")

if __name__ == "__main__":
    create_guide_pdf()
