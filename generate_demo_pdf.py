import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

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
            self.draw_page_number(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 11 * 72 - 36, "Diabetes Readmission Prediction — System Functionality & Video Demo Guide")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(54, 11 * 72 - 42, 8.5 * 72 - 54, 11 * 72 - 42)

        # Footer
        text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * 72 - 54, 36, text)
        self.drawString(54, 36, "IT3051 Data Mining Project · Academic Decision Support System")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 48, 8.5 * 72 - 54, 48)
        self.restoreState()


def build_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom palette
    PRIMARY = colors.HexColor("#087F5B")      # Emerald primary
    PRIMARY_DARK = colors.HexColor("#065F46") # Dark forest
    SECONDARY = colors.HexColor("#0F172A")    # Dark slate title
    BODY_COLOR = colors.HexColor("#334155")   # Slate body
    ACCENT_BG = colors.HexColor("#F0FDF4")    # Light green tint
    BORDER_COLOR = colors.HexColor("#CBD5E1") # Soft border
    MUTED = colors.HexColor("#64748B")

    # Custom typography styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=PRIMARY_DARK,
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=MUTED,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=PRIMARY_DARK,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=SECONDARY,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=BODY_COLOR,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=4
    )

    callout_style = ParagraphStyle(
        'Callout',
        parent=body_style,
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#064E3B")
    )

    script_actor_style = ParagraphStyle(
        'ScriptActor',
        parent=body_style,
        fontName='Helvetica-Bold',
        fontSize=9.5,
        textColor=PRIMARY_DARK,
        spaceAfter=2
    )

    script_action_style = ParagraphStyle(
        'ScriptAction',
        parent=body_style,
        fontName='Helvetica-Oblique',
        fontSize=9,
        textColor=colors.HexColor("#475569"),
        spaceAfter=3
    )

    script_dialogue_style = ParagraphStyle(
        'ScriptDialogue',
        parent=body_style,
        fontSize=9.5,
        leftIndent=10,
        spaceAfter=6
    )

    story = []

    # ----------------------------------------------------
    # COVER / HEADER SECTION
    # ----------------------------------------------------
    story.append(Paragraph("Diabetes Hospital Readmission Prediction System", title_style))
    story.append(Paragraph("Comprehensive System Functionality Overview & Demonstration Video Script", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceBefore=0, spaceAfter=12))

    # Meta table
    meta_data = [
        [
            Paragraph("<b>Project:</b> IT3051 Data Mining", body_style),
            Paragraph("<b>Core Model:</b> LightGBM (Selected Classifier)", body_style)
        ],
        [
            Paragraph("<b>Stack:</b> React 18 + Vite + Tailwind · FastAPI", body_style),
            Paragraph("<b>Dataset:</b> UCI Diabetes 130-US Hospitals (100k+ Encounters)", body_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[250, 250])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # Executive Summary Box
    exec_summary = [
        [Paragraph("<b>Executive Summary:</b> This document provides an end-to-end breakdown of the Diabetes Readmission Prediction Decision-Support System. It includes the architectural workflow, machine learning pipeline, frontend user interface functionality, and a complete scene-by-scene demonstration video script to guide live recordings or presentations.", callout_style)]
    ]
    exec_table = Table(exec_summary, colWidths=[504])
    exec_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), ACCENT_BG),
        ('BOX', (0,0), (-1,-1), 1, PRIMARY),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(exec_table)
    story.append(Spacer(1, 12))

    # ----------------------------------------------------
    # SECTION 1: SYSTEM ARCHITECTURE & PIPELINE
    # ----------------------------------------------------
    story.append(Paragraph("1. System Architecture & Machine Learning Pipeline", h1_style))
    story.append(Paragraph(
        "The system operates as an integrated full-stack machine learning application comprising three core layers:",
        body_style
    ))
    story.append(Paragraph("• <b>Machine Learning Core (Scikit-Learn & LightGBM):</b> Trained on historical hospital encounters to predict 3 distinct multiclass outcomes: <b>&lt;30</b> (readmitted within 30 days), <b>&gt;30</b> (readmitted after 30 days), and <b>NO</b> (not readmitted). Evaluated via 5-fold patient-grouped cross-validation to prevent data leakage.", bullet_style))
    story.append(Paragraph("• <b>Backend API Service (FastAPI & Uvicorn):</b> Serves production endpoints (<code>/api/health</code>, <code>/api/model-info</code>, <code>/api/predict</code>). It validates incoming clinical features via Pydantic, applies engineered feature transformations on-the-fly, and invokes the saved LightGBM model bundle.", bullet_style))
    story.append(Paragraph("• <b>Clinical Frontend UI (React, Vite, Tailwind, Recharts):</b> Modern, responsive, healthcare-grade UI delivering real-time predictions, intuitive probability charts, descriptive dataset analytics, and model transparency tools.", bullet_style))
    story.append(Spacer(1, 8))

    # Architecture Overview Table
    arch_data = [
        [Paragraph("<b>Component</b>", body_style), Paragraph("<b>Technology</b>", body_style), Paragraph("<b>Key Responsibilities</b>", body_style)],
        [Paragraph("<b>Frontend UI</b>", body_style), Paragraph("React, Vite, Tailwind CSS, Recharts, Lucide Icons", body_style), Paragraph("Interactive clinician forms, real-time probability visualization, EDA dashboard, model benchmarks.", body_style)],
        [Paragraph("<b>Backend API</b>", body_style), Paragraph("FastAPI, Pydantic v2, Uvicorn", body_style), Paragraph("REST API gateway, request payload validation, real-time feature derivation, error handling.", body_style)],
        [Paragraph("<b>ML Pipeline</b>", body_style), Paragraph("LightGBM, Scikit-Learn 1.9.1, NumPy, Pandas", body_style), Paragraph("Missing value handling, feature engineering, multi-class tree inference, calibrated probabilities.", body_style)]
    ]
    arch_table = Table(arch_data, colWidths=[90, 150, 264])
    arch_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(arch_table)
    story.append(Spacer(1, 14))

    # ----------------------------------------------------
    # SECTION 2: APPLICATION PAGES & CAPABILITIES
    # ----------------------------------------------------
    story.append(Paragraph("2. Detailed Module & Page Breakdown", h1_style))
    story.append(Paragraph(
        "The web interface is organized into 6 dedicated views, each serving a critical role in data discovery, prediction, and transparency:",
        body_style
    ))

    pages_info = [
        ("Dashboard (/) — Clinical Command Center",
         "Presents high-level system health, connected API status, model summary, total encounter volume (101.8k records), and interactive donut charts showing overall readmission distribution (<30: ~11.2%, >30: ~34.9%, NO: ~53.9%)."),
        ("Predict Readmission (/predict) — Live Decision Support",
         "The central interactive tool. Clinicians input encounter data (demographics, admission types, discharge disposition, previous visits, medications, lab counts, diagnosis categories, and medication changes). Upon submission, the system displays predicted class and calibrated percentage probabilities for all three outcomes."),
        ("Data Insights (/insights) — Exploratory Dataset Analytics",
         "Displays interactive charts exploring patient demographics (10-year age groups), length of hospital stay curves, distribution of prior inpatient/emergency visits, and average service utilization (lab procedures, medications)."),
        ("Model Performance (/performance) — Rigorous ML Evaluation",
         "Direct comparison of evaluated classifiers (LightGBM, XGBoost, Random Forest, Decision Tree, Logistic Regression). Highlights Cross-Validation Macro-F1 (0.4572) and Held-Out Test Macro-F1 (0.4581) with detailed rationale on why Macro-F1 was chosen for class imbalance."),
        ("Risk Factors (/risk-factors) — Model Interpretability & Feature Importance",
         "Visualizes gain-based feature importance from the fitted LightGBM model. Key drivers include previous inpatient visits, number of medications, number of diagnoses, time in hospital, and lab procedures."),
        ("About Project (/about) — Clinical Context & Disclaimers",
         "Documents project methodology, dataset provenance (UCI 130-US Hospitals), known technical limitations, and explicit academic/clinical decision support disclaimers.")
    ]

    for title, desc in pages_info:
        story.append(Paragraph(f"<b>• {title}:</b> {desc}", bullet_style))
    story.append(Spacer(1, 10))

    story.append(PageBreak())

    # ----------------------------------------------------
    # SECTION 3: DEMONSTRATION VIDEO GUIDE & SCRIPT
    # ----------------------------------------------------
    story.append(Paragraph("3. Demonstration Video Script & Recording Walkthrough", h1_style))
    story.append(Paragraph(
        "<b>Target Video Duration:</b> 3 to 4.5 minutes | <b>Audience:</b> Evaluators, Clinicians, Technical Reviewers",
        subtitle_style
    ))
    story.append(Paragraph(
        "Follow this timed step-by-step recording plan. Before starting, ensure both the backend (<code>port 8000</code>) and frontend (<code>port 5173</code>) are running with the status indicator showing <b>API connected</b>.",
        body_style
    ))
    story.append(Spacer(1, 6))

    scenes = [
        {
            "num": "Scene 1",
            "time": "0:00 - 0:35",
            "title": "Introduction & Clinical Problem Statement",
            "action": "Start screen on Dashboard. Mouse pointer hovers over the header and system title.",
            "speech": "\"Hello everyone. Today I'm demonstrating our Diabetes Readmission Prediction System—an interactive clinical decision-support application built for IT3051 Data Mining. Hospital readmissions within 30 days pose significant risks to diabetic patients and increase healthcare costs. Our system leverages advanced machine learning on over 100,000 hospital encounters to identify patient readmission risk in real-time, helping care teams plan timely post-discharge interventions.\""
        },
        {
            "num": "Scene 2",
            "time": "0:35 - 1:10",
            "title": "System Dashboard & Dataset Overview",
            "action": "Scroll through Dashboard. Highlight the API status badge, key stat cards, and the interactive readmission donut chart.",
            "speech": "\"Starting on the Dashboard, we immediately see our system status is live and connected to our FastAPI backend. The dashboard gives clinicians a high-level overview: our multiclass prediction task estimates three distinct outcomes: readmitted in under 30 days, after 30 days, or not readmitted. The dataset summary visualizes the baseline distribution across historical hospital stays.\""
        },
        {
            "num": "Scene 3",
            "time": "1:10 - 2:15",
            "title": "Live Interactive Prediction Walkthrough",
            "action": "Click 'Predict readmission' in sidebar or banner. Fill out encounter details (or show sample patient), then click 'Calculate Readmission Risk'. Show the animated loading and resulting probability card.",
            "speech": "\"Now let's head to the core feature: the Live Prediction module. Here, clinicians enter encounter-level details—such as patient age group, admission type, prior inpatient visits, length of stay, and diabetes medications. Let's enter a sample encounter for a patient with 2 previous inpatient visits and 18 medications. When we click 'Calculate Readmission Risk', the frontend securely calls our backend API. Within milliseconds, the trained LightGBM model returns both the predicted outcome class and a calibrated probability distribution across all three categories, giving transparent risk context.\""
        },
        {
            "num": "Scene 4",
            "time": "2:15 - 2:50",
            "title": "Data Insights & Clinical Exploration",
            "action": "Navigate to 'Data insights' page. Hover over the interactive age distribution, hospital stay curves, and prior visit charts.",
            "speech": "\"Next, under 'Data insights', clinicians and researchers can explore historical patient patterns. We provide responsive charts showing the breakdown of age demographics, length of hospital stays, prior utilization, and medication counts. This enables data-driven exploration of hospital utilization trends.\""
        },
        {
            "num": "Scene 5",
            "time": "2:50 - 3:30",
            "title": "Model Performance & Benchmark Comparison",
            "action": "Navigate to 'Model performance' page. Point to the benchmark bar chart comparing LightGBM, XGBoost, Random Forest, Decision Tree, and Logistic Regression.",
            "speech": "\"On the 'Model performance' page, we provide full transparency into our machine learning experiments. We evaluated multiple model families using 5-fold patient-grouped cross-validation. LightGBM achieved the highest cross-validation Macro-F1 score of 0.4572 and a held-out test Macro-F1 of 0.4581, demonstrating robust generalization without data leakage across patient encounters.\""
        },
        {
            "num": "Scene 6",
            "time": "3:30 - 4:05",
            "title": "Risk Factors (Explainability) & About Page",
            "action": "Navigate to 'Risk factors' page, scroll through feature importance chart, then briefly click 'About this project'.",
            "speech": "\"On the 'Risk factors' page, we break down feature importance based on tree gain. Prior inpatient visits, number of medications, and diagnoses emerge as leading contributors. Finally, our 'About' page details project methodology, dataset provenance, and clinical decision support disclaimers.\""
        },
        {
            "num": "Scene 7",
            "time": "4:05 - 4:25",
            "title": "Conclusion & Summary",
            "action": "Return to Dashboard or keep showing the connected application. Add concluding remarks.",
            "speech": "\"In summary, our system unites a validated LightGBM machine learning pipeline with an intuitive, modern clinical dashboard to assist healthcare providers in proactive patient care. Thank you for watching!\""
        }
    ]

    for scene in scenes:
        scene_box = [
            [
                Paragraph(f"<b>{scene['num']}: {scene['title']}</b> ({scene['time']})", script_actor_style),
            ],
            [
                Paragraph(f"<b>Visual / Screen Action:</b> {scene['action']}", script_action_style),
            ],
            [
                Paragraph(f"<b>Narrator Script:</b> {scene['speech']}", script_dialogue_style),
            ]
        ]
        scene_table = Table(scene_box, colWidths=[504])
        scene_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
            ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('LINEBELOW', (0,0), (-1,0), 0.5, colors.HexColor("#E2E8F0")),
            ('LINEBELOW', (0,1), (-1,1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(scene_table)
        story.append(Spacer(1, 6))

    story.append(PageBreak())

    # ----------------------------------------------------
    # SECTION 4: DEMO PRESENTATION & VIVA PREPARATION (Q&A)
    # ----------------------------------------------------
    story.append(Paragraph("4. Technical Demonstration & Q&A Cheat Sheet", h1_style))
    story.append(Paragraph(
        "Key questions evaluators often ask during project demonstrations and how to answer them confidently:",
        subtitle_style
    ))

    qa_items = [
        ("Why did you choose LightGBM as the final model?",
         "LightGBM achieved the top validation performance (CV Macro-F1 = 0.4572), outperforming Logistic Regression, Decision Trees, Random Forest, and XGBoost. It handles categorical features efficiently, trains rapidly, and provides fast, low-latency inference suitable for interactive clinical web tools."),
        ("Why is Macro-F1 used as the primary evaluation metric instead of Accuracy?",
         "Hospital readmission datasets exhibit severe class imbalance (over 53% 'NO' readmission, while '<30' is only ~11%). Accuracy would be misleading as a naive majority-class model would score >53%. Macro-F1 computes the unweighted mean of F1 scores across all 3 classes, ensuring equal importance is placed on minority classes like early readmission (<30)."),
        ("How did you prevent data leakage during training?",
         "We implemented GroupKFold / patient-grouped stratified cross-validation based on patient identifiers (patient_nbr). This guarantees that multiple hospital encounters for the same patient never appear simultaneously across training and validation folds."),
        ("How does the frontend communicate with the machine learning model?",
         "The React frontend makes asynchronous REST API calls via Axios to the FastAPI backend at <code>/api/predict</code>. The backend passes data into the preprocessing pipeline, constructs engineered features, runs inference on the saved LightGBM model bundle, and returns the probabilities as JSON.")
    ]

    for question, answer in qa_items:
        story.append(Paragraph(f"<b>Q: {question}</b>", h2_style))
        story.append(Paragraph(f"<b>A:</b> {answer}", body_style))
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 10))

    # ----------------------------------------------------
    # SECTION 5: DEMO SETUP CHECKLIST
    # ----------------------------------------------------
    story.append(Paragraph("5. Pre-Recording / Live Demo Checklist", h1_style))
    
    checklist = [
        "1. <b>Start Backend:</b> Run <code>python -m uvicorn app.main:app --app-dir backend --reload --port 8000</code> in terminal 1.",
        "2. <b>Start Frontend:</b> Run <code>npm run dev</code> inside <code>frontend/</code> directory in terminal 2.",
        "3. <b>Check Connection:</b> Open <code>http://localhost:5173</code> and verify the green <b>API connected</b> pill in the top bar.",
        "4. <b>Browser Zoom & Resolution:</b> Set browser window to 1080p (1920x1080) or full screen with 100% zoom for crisp video capture.",
        "5. <b>Microphone & Audio:</b> Test recording levels to ensure clean voice narration without background hiss."
    ]
    for chk in checklist:
        story.append(Paragraph(chk, bullet_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF generated successfully at: {filename}")

if __name__ == "__main__":
    output_path = os.path.abspath("Diabetes_Readmission_System_Demonstration_Guide.pdf")
    build_pdf(output_path)
