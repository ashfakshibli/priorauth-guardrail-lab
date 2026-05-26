"""
Seeds synthetic demo data.  All IDs and clinical content are fictional.
No PHI/PII is present.
"""
from app.models import PolicyDocument, PolicyClause, Case, CaseStatusEnum
from app.database import SessionLocal, engine, Base


POLICY_DOCUMENTS = [
    {
        "id": "POL-MED-001",
        "title": "Medical Necessity Criteria – Biologics",
        "payer_code": "SYNTH-PLAN-A",
        "effective_date": "2025-01-01",
        "description": "Coverage criteria for biologic and specialty medications.",
        "clauses": [
            {
                "id": "CL-001-A",
                "section": "Section 3.1 – Adalimumab",
                "clause_text": (
                    "Adalimumab (J0885) is covered when the member has a confirmed diagnosis "
                    "of moderate-to-severe rheumatoid arthritis (M05.x, M06.x) AND has "
                    "documented inadequate response to at least two conventional DMARDs over 90 days."
                ),
                "tags": ["biologics", "rheumatoid-arthritis", "J0885", "DMARD"],
                "determination_hint": "approve",
            },
            {
                "id": "CL-001-B",
                "section": "Section 3.2 – Denial Criteria",
                "clause_text": (
                    "Biologics are NOT covered when clinical documentation lacks evidence of "
                    "prior DMARD therapy, OR when the diagnosis code does not correspond to "
                    "an approved indication listed in Appendix A."
                ),
                "tags": ["biologics", "denial", "documentation-missing"],
                "determination_hint": "deny",
            },
            {
                "id": "CL-001-C",
                "section": "Section 3.5 – Step Therapy Requirement",
                "clause_text": (
                    "Step therapy is required before any biologic approval. Members must fail "
                    "methotrexate and at least one other DMARD. Exceptions require specialist attestation."
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
        "description": "Prior auth requirements for MRI, CT, and PET imaging.",
        "clauses": [
            {
                "id": "CL-002-A",
                "section": "Section 2.1 – MRI Lumbar Spine",
                "clause_text": (
                    "MRI of the lumbar spine (CPT 72148) is covered when the member has "
                    "low back pain lasting > 6 weeks with documented conservative treatment "
                    "failure, OR red-flag symptoms (e.g., neurological deficits, cancer history)."
                ),
                "tags": ["imaging", "MRI", "lumbar", "72148", "low-back-pain"],
                "determination_hint": "approve",
            },
            {
                "id": "CL-002-B",
                "section": "Section 2.2 – MRI Denial",
                "clause_text": (
                    "MRI lumbar spine is NOT covered within the first 6 weeks of acute low back "
                    "pain onset in the absence of red-flag indicators."
                ),
                "tags": ["imaging", "MRI", "lumbar", "denial", "acute", "no-prior-treatment"],
                "determination_hint": "deny",
            },
            {
                "id": "CL-002-C",
                "section": "Section 5.1 – PET Scan",
                "clause_text": (
                    "PET scans (CPT 78816) require oncology specialist order and documented "
                    "diagnosis of malignancy. Routine staging PET is covered for approved cancer types."
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
        "description": "Coverage criteria for inpatient and outpatient behavioral health services.",
        "clauses": [
            {
                "id": "CL-003-A",
                "section": "Section 1.1 – Inpatient Psychiatric Admission",
                "clause_text": (
                    "Inpatient psychiatric admission is covered when the member presents "
                    "with acute psychiatric crisis, including active suicidal ideation with "
                    "plan, psychotic break, or severe functional impairment requiring 24-hour care."
                ),
                "tags": ["behavioral-health", "inpatient", "psychiatric", "crisis"],
                "determination_hint": "approve",
            },
            {
                "id": "CL-003-B",
                "section": "Section 1.3 – Residential Escalation",
                "clause_text": (
                    "Transition from outpatient to residential treatment requires documented "
                    "failure of intensive outpatient program (IOP) and continued clinical necessity. "
                    "Requires concurrent review."
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
        "description": "Prior authorization requirements for elective and semi-elective surgery.",
        "clauses": [
            {
                "id": "CL-004-A",
                "section": "Section 4.1 – Knee Arthroscopy",
                "clause_text": (
                    "Knee arthroscopy for meniscal repair (CPT 29881) is covered when "
                    "imaging confirms meniscal tear, conservative treatment has failed (>8 weeks), "
                    "and orthopedic surgeon recommends surgical intervention."
                ),
                "tags": ["surgery", "orthopedic", "knee", "29881", "meniscal"],
                "determination_hint": "approve",
            },
            {
                "id": "CL-004-B",
                "section": "Section 4.4 – Exclusions",
                "clause_text": (
                    "Cosmetic and elective procedures without documented medical necessity "
                    "are categorically excluded. Procedures performed solely for quality-of-life "
                    "improvement without functional impairment are not covered."
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
        "description": "Authorization criteria for home infusion and infusion center services.",
        "clauses": [
            {
                "id": "CL-005-A",
                "section": "Section 2.1 – Home Infusion Eligibility",
                "clause_text": (
                    "Home infusion services are covered when the member is clinically stable, "
                    "has a trained caregiver or self-administration capability, and the treating "
                    "physician certifies medical appropriateness of home setting."
                ),
                "tags": ["infusion", "home-infusion", "J1745", "specialty-pharmacy"],
                "determination_hint": "approve",
            },
            {
                "id": "CL-005-B",
                "section": "Section 2.3 – Conflicting Site of Care",
                "clause_text": (
                    "When the clinical record indicates the member requires monitoring that "
                    "exceeds home setting capabilities, infusion center care is required. "
                    "Payer site-of-care review is mandatory."
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
