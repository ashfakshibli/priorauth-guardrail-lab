"""
Seeds synthetic demo data.  All IDs and clinical content are fictional.
No PHI/PII is present.

Policy clause text is adapted from public-domain CMS coverage documents:
  • NCD 220.2   – MRI coverage criteria
  • NCD 220.6.17 – FDG PET scan coverage
  • NCD 150.9   – Lumbar vertebral body fusion (knee surgical guidance)
  • LCD L33626  – Psychiatric partial hospitalization (Novitas Solutions)
  • CMS Article A52423 – Infliximab/adalimumab site-of-care & step-therapy
Source: https://www.cms.gov/medicare-coverage-database/
"""
from app.models import PolicyDocument, PolicyClause, Case, CaseStatusEnum
from app.database import SessionLocal, engine, Base


POLICY_DOCUMENTS = [
    {
        "id": "POL-MED-001",
        "title": "Medical Necessity Criteria – Biologics",
        "payer_code": "SYNTH-PLAN-A",
        "effective_date": "2025-01-01",
        "description": (
            "Coverage criteria for biologic and specialty medications. "
            "Clause language adapted from CMS Article A52423 (Infliximab/"
            "adalimumab prior-authorization requirements) and Medicare biologic "
            "step-therapy guidelines. "
            "Source: https://www.cms.gov/medicare-coverage-database/"
        ),
        "clauses": [
            {
                "id": "CL-001-A",
                "section": "Section 3.1 – Adalimumab (J0885) Coverage Criteria",
                "clause_text": (
                    "Adalimumab (HCPCS J0885) is covered for members with a confirmed "
                    "diagnosis of moderate-to-severe rheumatoid arthritis (ICD-10 M05.x, M06.x) "
                    "who have documented failure of at least two conventional disease-modifying "
                    "anti-rheumatic drugs (DMARDs), one of which must be methotrexate, each "
                    "trialed for a minimum of 90 days at therapeutic dose. Inadequate response "
                    "is defined as fewer than 20% improvement in tender joint count (TJC) or "
                    "swollen joint count (SJC) from baseline, consistent with ACR response criteria. "
                    "Prescribing rheumatologist attestation is required."
                ),
                "tags": ["biologics", "rheumatoid-arthritis", "J0885", "DMARD"],
                "determination_hint": "approve",
            },
            {
                "id": "CL-001-B",
                "section": "Section 3.2 – Non-Coverage: Missing DMARD Documentation",
                "clause_text": (
                    "Biologic therapy is NOT covered when the submitted clinical documentation "
                    "does not include: (a) chart notes or laboratory results confirming a prior "
                    "adequate trial of methotrexate and at least one additional DMARD; (b) "
                    "objective evidence of inadequate response using a validated disease-activity "
                    "score (DAS28, CDAI, or TJC/SJC counts); or (c) a diagnosis code mapping to "
                    "an approved indication listed in the plan formulary. Absence of any one of "
                    "these elements constitutes insufficient documentation and results in denial "
                    "pending resubmission with complete records."
                ),
                "tags": ["biologics", "denial", "documentation-missing"],
                "determination_hint": "deny",
            },
            {
                "id": "CL-001-C",
                "section": "Section 3.5 – Step Therapy Exception Pathway",
                "clause_text": (
                    "Step therapy is required prior to biologic approval. Members must have "
                    "failed methotrexate and at least one other conventional DMARD at therapeutic "
                    "doses. Exception to step therapy may be granted when the treating specialist "
                    "provides written attestation of a contraindication to conventional DMARDs "
                    "(e.g., hepatotoxicity risk, renal impairment, intolerance) supported by "
                    "lab values or prior adverse event documentation. Exception requests require "
                    "concurrent medical review and are not subject to automatic approval."
                ),
                "tags": ["biologics", "step-therapy", "DMARD"],
                "determination_hint": "human_review",
            },
        ],
    },
    {
        "id": "POL-IMG-002",
        "title": "Imaging Authorization Policy – Advanced Imaging",
        "payer_code": "SYNTH-PLAN-A",
        "effective_date": "2025-01-01",
        "description": (
            "Prior authorization requirements for MRI and PET imaging. "
            "Clause language adapted from CMS NCD 220.2 (Magnetic Resonance Imaging) "
            "and NCD 220.6.17 (FDG PET Scans for Solid Tumors). "
            "Sources: "
            "https://www.cms.gov/medicare-coverage-database/view/ncd.aspx?NCDId=282 "
            "(NCD 220.2); "
            "https://www.cms.gov/medicare-coverage-database/view/ncd.aspx?NCDId=229 "
            "(NCD 220.6.17)."
        ),
        "clauses": [
            {
                "id": "CL-002-A",
                "section": "Section 2.1 – MRI Lumbar Spine (CPT 72148) Coverage",
                "clause_text": (
                    "MRI of the lumbar spine (CPT 72148) is covered when the member has "
                    "low back pain with a duration exceeding six (6) weeks AND documented "
                    "failure of conservative treatment, defined as physician-directed physical "
                    "therapy, activity modification, or analgesic therapy. Coverage is also "
                    "approved without the six-week waiting period when red-flag indicators "
                    "are present, including: new neurological deficit (radiculopathy, bowel "
                    "or bladder dysfunction), history of malignancy with suspected metastatic "
                    "disease, fever with suspected spinal infection, or acute trauma. "
                    "Per CMS NCD 220.2, MRI is a covered service when clinically indicated "
                    "and ordered by the treating physician."
                ),
                "tags": ["imaging", "MRI", "lumbar", "72148", "low-back-pain"],
                "determination_hint": "approve",
            },
            {
                "id": "CL-002-B",
                "section": "Section 2.2 – MRI Lumbar Spine: Non-Coverage",
                "clause_text": (
                    "MRI of the lumbar spine is NOT covered within the first six (6) weeks "
                    "of acute low back pain onset in the absence of red-flag indicators. "
                    "Acute onset is defined as symptom duration of less than six weeks with "
                    "no prior documented episode. Per CMS guidance and consistent with LCD "
                    "L34220 (MRI spine), routine imaging for uncomplicated acute low back "
                    "pain does not meet medical necessity criteria. Claims submitted without "
                    "documentation of conservative treatment failure or a qualifying red-flag "
                    "condition will be denied."
                ),
                "tags": ["imaging", "MRI", "lumbar", "denial", "acute", "no-prior-treatment"],
                "determination_hint": "deny",
            },
            {
                "id": "CL-002-C",
                "section": "Section 5.1 – FDG PET Scan (CPT 78816) Coverage",
                "clause_text": (
                    "Whole-body FDG PET scanning (CPT 78816) is covered as an initial "
                    "anti-tumor treatment strategy when: (a) the ordering physician is an "
                    "oncology specialist; (b) a histologically or cytologically confirmed "
                    "malignancy is documented; and (c) the PET findings are expected to "
                    "influence the management of the treated malignancy. Per CMS NCD 220.6.17, "
                    "coverage extends to initial staging, restaging after treatment, and "
                    "monitoring of treatment response for approved solid tumor types including "
                    "non-small cell lung carcinoma, colorectal cancer, lymphoma, and melanoma. "
                    "Treatment response monitoring is covered for up to three (3) scans per "
                    "treatment course."
                ),
                "tags": ["imaging", "PET", "78816", "oncology"],
                "determination_hint": "approve",
            },
        ],
    },
    {
        "id": "POL-BH-003",
        "title": "Behavioral Health Coverage Policy",
        "payer_code": "SYNTH-PLAN-A",
        "effective_date": "2025-01-01",
        "description": (
            "Coverage criteria for inpatient and residential behavioral health services. "
            "Clause language adapted from CMS LCD L33626 (Psychiatric Partial "
            "Hospitalization Programs, Novitas Solutions) and CMS Benefit Policy Manual "
            "Chapter 4 (Inpatient Psychiatric Facility Services). "
            "Source: https://www.cms.gov/medicare-coverage-database/view/lcd.aspx?LCDId=33626"
        ),
        "clauses": [
            {
                "id": "CL-003-A",
                "section": "Section 1.1 – Inpatient Psychiatric Admission",
                "clause_text": (
                    "Inpatient psychiatric admission is covered when the member presents with "
                    "an acute psychiatric crisis requiring 24-hour supervised care that cannot "
                    "be safely managed in a less restrictive setting. Qualifying presentations "
                    "include: active suicidal ideation with plan and intent, homicidal ideation, "
                    "acute psychotic episode with severe functional impairment, or a documented "
                    "acute exacerbation of a major psychiatric disorder (DSM-5 criteria). "
                    "Admission must be ordered by a licensed psychiatrist or clinical psychologist "
                    "with prescriptive authority. Continued stay requires daily documentation "
                    "of medical necessity by the attending psychiatrist."
                ),
                "tags": ["behavioral-health", "inpatient", "psychiatric", "crisis"],
                "determination_hint": "approve",
            },
            {
                "id": "CL-003-B",
                "section": "Section 1.3 – Residential Treatment: Escalation from IOP",
                "clause_text": (
                    "Transition from outpatient care to residential behavioral health treatment "
                    "(H0018) is covered when the member has completed a structured intensive "
                    "outpatient program (IOP) of at least eight (8) weeks providing a minimum "
                    "of nine (9) hours of therapeutic services per week, and the treating "
                    "psychiatrist documents continued clinical necessity for a higher level of "
                    "care. Per LCD L33626, the clinical record must demonstrate that the member's "
                    "psychiatric condition has not responded adequately to less intensive "
                    "outpatient treatment and that residential-level services are the least "
                    "restrictive appropriate level of care. Concurrent utilization review is "
                    "required; authorization is not automatically granted at the time of "
                    "IOP discharge."
                ),
                "tags": ["behavioral-health", "residential", "IOP", "escalation"],
                "determination_hint": "human_review",
            },
        ],
    },
    {
        "id": "POL-SURG-004",
        "title": "Surgical Procedures Authorization",
        "payer_code": "SYNTH-PLAN-B",
        "effective_date": "2024-07-01",
        "description": (
            "Prior authorization requirements for elective and semi-elective surgical "
            "procedures. Clause language for knee arthroscopy adapted from CMS NCD 150.9 "
            "(Lumbar Vertebral Body Fusion / Orthopedic Surgical Guidance) and CMS "
            "local coverage guidance for knee meniscal procedures. "
            "Source: https://www.cms.gov/medicare-coverage-database/view/ncd.aspx?NCDId=199"
        ),
        "clauses": [
            {
                "id": "CL-004-A",
                "section": "Section 4.1 – Knee Arthroscopy with Meniscectomy (CPT 29881)",
                "clause_text": (
                    "Arthroscopic knee surgery with partial or total meniscectomy (CPT 29881) "
                    "is covered when ALL of the following criteria are met: (a) MRI or "
                    "diagnostic arthroscopy confirms a meniscal tear; (b) the member "
                    "demonstrates mechanical symptoms attributable to the tear, including at "
                    "least one of: joint locking, catching, or giving way; (c) conservative "
                    "treatment including at least eight (8) weeks of supervised physical "
                    "therapy has failed to provide adequate functional improvement; and "
                    "(d) an orthopedic surgeon has evaluated the member and recommends "
                    "surgical intervention as medically necessary. Coverage criteria align "
                    "with CMS guidance that meniscal surgery is appropriate for mechanically "
                    "symptomatic disease rather than incidental imaging findings."
                ),
                "tags": ["surgery", "orthopedic", "knee", "29881", "meniscal"],
                "determination_hint": "approve",
            },
            {
                "id": "CL-004-B",
                "section": "Section 4.4 – Non-Coverage: Degenerative OA Without Mechanical Symptoms",
                "clause_text": (
                    "Knee arthroscopy is NOT covered for members whose primary indication is "
                    "osteoarthritis-related pain in the absence of documented mechanical "
                    "symptoms (locking, catching, or giving way). Per CMS coverage guidance, "
                    "arthroscopic procedures performed solely for the treatment of generalized "
                    "knee pain, degenerative joint disease, or chondromalacia without a "
                    "discrete mechanical derangement do not meet medical necessity criteria. "
                    "Procedures performed solely for quality-of-life improvement without "
                    "functional impairment from mechanical symptoms are categorically excluded. "
                    "When imaging shows incidental degenerative changes only, denial is expected "
                    "absent additional clinical justification."
                ),
                "tags": ["surgery", "exclusion", "cosmetic", "elective", "denial"],
                "determination_hint": "deny",
            },
        ],
    },
    {
        "id": "POL-PHARM-005",
        "title": "Specialty Pharmacy – Infusion Services",
        "payer_code": "SYNTH-PLAN-B",
        "effective_date": "2025-01-01",
        "description": (
            "Authorization criteria for home infusion and infusion center services. "
            "Clause language adapted from CMS Article A52423 (Infliximab Coverage "
            "Requirements and Site-of-Care Policy) and J5 MAC infusion therapy guidance. "
            "Source: https://www.cms.gov/medicare-coverage-database/view/article.aspx?articleId=52423"
        ),
        "clauses": [
            {
                "id": "CL-005-A",
                "section": "Section 2.1 – Home Infusion Eligibility",
                "clause_text": (
                    "Home infusion services are covered when: (a) the member is clinically "
                    "stable and has no documented history of infusion-related adverse reactions "
                    "requiring medical intervention; (b) a trained caregiver is present during "
                    "infusion or the member has demonstrated self-administration competency; "
                    "and (c) the treating physician provides written certification that the "
                    "home setting is medically appropriate. For infliximab (J1745), home "
                    "infusion requires additional documentation per CMS Article A52423: the "
                    "member must have completed at least two (2) uneventful infusion center "
                    "infusions prior to transitioning to home setting, confirming tolerability "
                    "and absence of infusion reaction risk."
                ),
                "tags": ["infusion", "home-infusion", "J1745", "specialty-pharmacy"],
                "determination_hint": "approve",
            },
            {
                "id": "CL-005-B",
                "section": "Section 2.3 – Site-of-Care Review: Infusion Center Required",
                "clause_text": (
                    "When the clinical record indicates the member requires monitoring that "
                    "exceeds home setting capabilities, infusion center care is required and "
                    "home infusion cannot be authorized. Per CMS Article A52423, infliximab "
                    "infusions must be administered in an infusion center or outpatient "
                    "hospital setting when: (a) the member has documented infusion-related "
                    "reactions in prior treatment records; (b) the member requires "
                    "pre-medication (e.g., antihistamines, corticosteroids) prior to each "
                    "infusion; or (c) comorbidities (cardiovascular disease, renal impairment, "
                    "or age ≥ 65 with frailty indicators) elevate the risk profile beyond "
                    "home monitoring capability. Payer site-of-care review is mandatory; "
                    "a home infusion request under these conditions requires medical director "
                    "review before approval."
                ),
                "tags": ["infusion", "site-of-care", "human_review", "monitoring"],
                "determination_hint": "human_review",
            },
        ],
    },
]


CASES = [
    {
        "id": "CASE-1001",
        "member_id": "MBR-1042",
        "provider_id": "PRV-217",
        "age_band": "45-54",
        "service_code": "J0885",
        "service_description": "Adalimumab injection, 20 mg",
        "diagnosis_codes": ["M05.79", "M06.09"],
        "clinical_notes_summary": (
            "Member has documented RA since 2021. Trialed methotrexate (24 weeks) "
            "and hydroxychloroquine (16 weeks) with inadequate response. "
            "Rheumatologist recommends biologic initiation."
        ),
        "policy_document_ids": ["POL-MED-001"],
        "status": CaseStatusEnum.pending,
        "tags": ["biologics", "rheumatoid-arthritis", "J0885", "DMARD"],
    },
    {
        "id": "CASE-1002",
        "member_id": "MBR-2089",
        "provider_id": "PRV-304",
        "age_band": "35-44",
        "service_code": "72148",
        "service_description": "MRI lumbar spine without contrast",
        "diagnosis_codes": ["M54.5"],
        "clinical_notes_summary": (
            "Member presents with acute low back pain onset 10 days ago. "
            "No prior conservative treatment documented. No red-flag symptoms noted."
        ),
        "policy_document_ids": ["POL-IMG-002"],
        "status": CaseStatusEnum.pending,
        "tags": ["imaging", "MRI", "lumbar", "72148", "acute", "no-prior-treatment"],
    },
    {
        "id": "CASE-1003",
        "member_id": "MBR-3317",
        "provider_id": "PRV-512",
        "age_band": "25-34",
        "service_code": "H0018",
        "service_description": "Behavioral health; short-term residential (non-hospital)",
        "diagnosis_codes": ["F32.2", "F41.1"],
        "clinical_notes_summary": (
            "Member completed 8-week IOP with limited improvement. "
            "Continued significant functional impairment and psychiatrist recommends "
            "step-up to residential level of care."
        ),
        "policy_document_ids": ["POL-BH-003"],
        "status": CaseStatusEnum.pending,
        "tags": ["behavioral-health", "residential", "IOP", "escalation"],
    },
    {
        "id": "CASE-1004",
        "member_id": "MBR-4450",
        "provider_id": "PRV-189",
        "age_band": "55-64",
        "service_code": "29881",
        "service_description": "Arthroscopy, knee, surgical; with meniscectomy",
        "diagnosis_codes": ["M23.20"],
        "clinical_notes_summary": (
            "MRI confirmed medial meniscal tear. Member completed 10 weeks of PT "
            "without functional improvement. Orthopedic surgeon recommends repair."
        ),
        "policy_document_ids": ["POL-SURG-004"],
        "status": CaseStatusEnum.pending,
        "tags": ["surgery", "orthopedic", "knee", "29881", "meniscal"],
    },
    {
        "id": "CASE-1005",
        "member_id": "MBR-5521",
        "provider_id": "PRV-067",
        "age_band": "65+",
        "service_code": "J1745",
        "service_description": "Infliximab injection, 10 mg",
        "diagnosis_codes": ["K50.10", "M05.60"],
        "clinical_notes_summary": (
            "Member requires infliximab infusion. Home setting requested. "
            "Caregiver present and trained. Physician certifies home appropriateness. "
            "However, prior infusion records indicate two adverse reactions requiring "
            "on-site monitoring."
        ),
        "policy_document_ids": ["POL-PHARM-005"],
        "status": CaseStatusEnum.pending,
        "tags": ["infusion", "home-infusion", "J1745", "site-of-care", "monitoring"],
    },
    {
        "id": "CASE-1006",
        "member_id": "MBR-6634",
        "provider_id": "PRV-441",
        "age_band": "35-44",
        "service_code": "J0885",
        "service_description": "Adalimumab injection, 20 mg",
        "diagnosis_codes": ["L40.0"],
        "clinical_notes_summary": "",
        "policy_document_ids": ["POL-MED-001"],
        "status": CaseStatusEnum.pending,
        "tags": ["biologics", "J0885", "documentation-missing"],
    },
    {
        "id": "CASE-1007",
        "member_id": "MBR-7712",
        "provider_id": "PRV-298",
        "age_band": "45-54",
        "service_code": "78816",
        "service_description": "PET scan, whole body",
        "diagnosis_codes": ["C34.10"],
        "clinical_notes_summary": (
            "Oncologist ordered whole-body PET for lung cancer staging (stage IIIA). "
            "Pathology confirms non-small cell lung carcinoma."
        ),
        "policy_document_ids": ["POL-IMG-002"],
        "status": CaseStatusEnum.pending,
        "tags": ["imaging", "PET", "78816", "oncology"],
    },
    {
        "id": "CASE-1008",
        "member_id": "MBR-8891",
        "provider_id": "PRV-554",
        "age_band": "55-64",
        "service_code": "99999",
        "service_description": "Experimental reconstructive procedure (unlisted code)",
        "diagnosis_codes": ["M79.3"],
        "clinical_notes_summary": "Physician requests authorization for novel procedure not on plan formulary.",
        "policy_document_ids": [],
        "status": CaseStatusEnum.pending,
        "tags": ["unlisted", "experimental"],
    },
]


def seed(db=None):
    if db is None:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        close_after = True
    else:
        close_after = False

    # Idempotent: skip if already seeded
    if db.query(PolicyDocument).count() > 0:
        if close_after:
            db.close()
        return

    for doc_data in POLICY_DOCUMENTS:
        doc_copy = {k: v for k, v in doc_data.items() if k != "clauses"}
        clauses_data = doc_data["clauses"]
        doc = PolicyDocument(**doc_copy)
        db.add(doc)
        db.flush()
        for cl_data in clauses_data:
            cl = PolicyClause(document_id=doc.id, **cl_data)
            db.add(cl)

    for case_data in CASES:
        case = Case(**case_data)
        db.add(case)

    db.commit()
    if close_after:
        db.close()
