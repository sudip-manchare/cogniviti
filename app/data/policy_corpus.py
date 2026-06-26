from typing import List, Dict

POLICY_EXCERPTS: List[Dict[str, str]] = [
    {
        "source_citation": "CMS NCD 100-2, Chapter 15, Section 50.1 – Reasonable and Necessary",
        "text": (
            "For Medicare to cover a service, it must be reasonable and necessary for the "
            "diagnosis or treatment of illness or injury, or to improve the functioning of a "
            "malformed body member. Services that are not reasonable and necessary, including "
            "those that exceed the frequency, duration, or scope of generally accepted medical "
            "practice standards, shall be denied."
        ),
    },
    {
        "source_citation": "CMS NCD 100-4, Chapter 1, Section 10.2 – Medical Necessity",
        "text": (
            "Medical necessity is determined by the local Medicare Administrative Contractor "
            "(MAC) based on accepted standards of medical practice. The documentation submitted "
            "must support that the service was medically necessary and appropriate for the "
            "diagnosis and treatment of the patient's condition."
        ),
    },
    {
        "source_citation": "CMS NCD 220.6 – Routine Costs in Clinical Trials",
        "text": (
            "Medicare covers routine costs associated with qualifying clinical trials. Routine "
            "costs include items and services that are typically covered absent a clinical trial, "
            "such as standard chemotherapy, hospital stays, and physician visits. Investigational "
            "items and services that are not typically covered are excluded."
        ),
    },
    {
        "source_citation": "CMS NCD 100-2, Chapter 15, Section 290 – Evaluation and Management Services",
        "text": (
            "Evaluation and Management (E/M) services are covered when provided to evaluate a "
            "patient's condition, establish a diagnosis, and develop a treatment plan. The level "
            "of E/M service billed must be supported by the documentation in the medical record. "
            "Upcoding or billing for a higher level of service than documented is prohibited."
        ),
    },
    {
        "source_citation": "CMS Publication 100-03, NCD 150.3 – Cardiac Rehabilitation",
        "text": (
            "Cardiac rehabilitation programs are covered when ordered by a physician and "
            "provided in a hospital outpatient setting. Services must include physician-prescribed "
            "exercise, cardiac risk factor modification, and psychosocial assessment. Programs "
            "exceeding 36 sessions in 36 weeks require additional medical necessity justification."
        ),
    },
    {
        "source_citation": "CMS NCD 100-2, Chapter 15, Section 80 – Surgical Services",
        "text": (
            "Surgical services must be performed by a qualified provider and must be medically "
            "necessary for the treatment of the patient's condition. Billed amounts for surgical "
            "services should reflect reasonable and customary charges consistent with the "
            "complexity of the procedure and geographic region."
        ),
    },
    {
        "source_citation": "CMS NCD 100-04, Chapter 12, Section 30 – Payment for Radiological Services",
        "text": (
            "Payment for diagnostic radiology services is based on the technical and professional "
            "components. Services must be ordered by a treating physician and be appropriate for "
            "the patient's signs, symptoms, or diagnosis. Repeat imaging studies within a short "
            "timeframe without documented clinical change require justification."
        ),
    },
    {
        "source_citation": "CMS NCD 280.1 – Durable Medical Equipment Reference List",
        "text": (
            "Durable Medical Equipment (DME) must: (1) be able to withstand repeated use, "
            "(2) be primarily and customarily used for medical purposes, (3) generally not be "
            "useful to a person in the absence of illness or injury, and (4) be appropriate for "
            "use in the home. Claims for DME must include proof of medical necessity and delivery."
        ),
    },
    {
        "source_citation": "CMS NCD 190.2 – Chiropractic Services",
        "text": (
            "Medicare covers manual manipulation of the spine for correction of a subluxation "
            "demonstrated by X-ray. Maintenance therapy (services provided to maintain function "
            "rather than correct a specific condition) is not covered. Documentation must include "
            "the specific spinal level manipulated and evidence of subluxation."
        ),
    },
    {
        "source_citation": "CMS NCD 100-4, Chapter 23, Section 20 – Reporting of Unlisted Codes",
        "text": (
            "When a service is billed using an unlisted procedure code, the provider must submit "
            "supporting documentation including a description of the service, the amount of time "
            "spent, and a comparison to similar covered services. Failure to submit adequate "
            "documentation may result in denial of the claim."
        ),
    },
    {
        "source_citation": "CMS Publication 100-02, Medicare Benefit Policy Manual, Chapter 10 – Ambulance Services",
        "text": (
            "Ambulance services are covered only when the transportation is medically necessary "
            "and the patient's condition requires transport by ambulance. Non-emergency ambulance "
            "transport must be documented with a written order from the treating physician and "
            "a description of why other means of transportation are contraindicated."
        ),
    },
    {
        "source_citation": "CMS NCD 100-2, Chapter 15, Section 100 – Preventive Services",
        "text": (
            "Medicare covers a range of preventive services including annual wellness visits, "
            "mammography, colorectal cancer screening, and cardiovascular disease screening. "
            "Services must be provided within the recommended frequency limits. Services billed "
            "more frequently than allowed will be denied as not medically necessary."
        ),
    },
    {
        "source_citation": "CMS NCD 100-03, Section 20.8 – Electrocardiographic (EKG) Services",
        "text": (
            "Screening EKG services are covered once within a 12-month period as part of a "
            "one-time initial preventive physical examination. Diagnostic EKG services are "
            "covered for patients presenting with signs or symptoms of cardiac disease. Routine "
            "screening EKGs for asymptomatic patients beyond the initial benefit are not covered."
        ),
    },
    {
        "source_citation": "42 CFR §411.351 – Anti-Kickback Statute Implications",
        "text": (
            "Remuneration offered or paid to induce or reward the referral of Medicare or "
            "Medicaid patients is prohibited. This includes financial arrangements that result "
            "in excessive utilization or inflated billing amounts. Providers must ensure that "
            "financial relationships are structured in compliance with safe harbor provisions."
        ),
    },
    {
        "source_citation": "CMS NCD 100-4, Chapter 1, Section 80 – Claims Processing Requirements",
        "text": (
            "All claims must be submitted with accurate coding and complete supporting "
            "documentation. Duplicate billing for the same service, unbundling of services "
            "that should be billed as a single procedure, and billing for services not actually "
            "furnished are all grounds for claim denial and potential fraud investigation."
        ),
    },
]


def get_policy_excerpts() -> List[Dict[str, str]]:
    return POLICY_EXCERPTS