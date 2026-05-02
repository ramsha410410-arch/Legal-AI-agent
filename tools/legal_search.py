# ============================================================
# tools/draft_generator.py — Legal Document Templates
# ============================================================
#
# This file provides helper functions for common legal document
# templates. These are used by the agent when users ask to
# "draft a contract" or "create an NDA" etc.
# ============================================================


# Common legal document templates
# These are basic templates — always recommend professional review

NDA_TEMPLATE_PROMPT = """
Create a Non-Disclosure Agreement (NDA) with these details:

Disclosing Party: [DISCLOSING_PARTY_NAME]
Receiving Party: [RECEIVING_PARTY_NAME]  
Purpose: [PURPOSE_OF_DISCLOSURE]
Duration: [DURATION_YEARS] years
Governing Law: [STATE/JURISDICTION]

Include standard clauses for:
1. Definition of Confidential Information
2. Obligations of Receiving Party
3. Exclusions from Confidentiality
4. Return/Destruction of Information
5. Remedies for Breach
6. Term and Termination

Use professional legal language but make it clear and readable.
Mark all customizable fields with [BRACKETS].
"""

EMPLOYMENT_CONTRACT_PROMPT = """
Create an Employment Agreement with these elements:

Employer: [EMPLOYER_NAME]
Employee: [EMPLOYEE_NAME]
Position: [JOB_TITLE]
Start Date: [START_DATE]
Compensation: [SALARY/HOURLY_RATE]
Work Location: [LOCATION/REMOTE]

Include clauses for:
1. Job Duties and Responsibilities
2. Compensation and Benefits
3. Working Hours
4. Confidentiality
5. Intellectual Property Assignment
6. Termination Conditions
7. Dispute Resolution

Mark customizable fields with [BRACKETS].
"""

SERVICE_AGREEMENT_PROMPT = """
Create a Service Agreement (Independent Contractor) with:

Client: [CLIENT_NAME]
Service Provider: [PROVIDER_NAME]
Services: [DESCRIPTION_OF_SERVICES]
Payment: [PAYMENT_TERMS]
Timeline: [PROJECT_TIMELINE]

Include clauses for:
1. Scope of Services
2. Payment Terms
3. Independent Contractor Status (vs Employee)
4. Intellectual Property Ownership
5. Confidentiality
6. Limitation of Liability
7. Termination

Mark customizable fields with [BRACKETS].
"""


def get_template_prompt(document_type: str) -> str:
    """
    Get the appropriate prompt template for a document type.
    
    Args:
        document_type: Type of document ("nda", "employment", "service")
    
    Returns:
        Template prompt string
    """
    
    templates = {
        "nda": NDA_TEMPLATE_PROMPT,
        "non-disclosure": NDA_TEMPLATE_PROMPT,
        "employment": EMPLOYMENT_CONTRACT_PROMPT,
        "service": SERVICE_AGREEMENT_PROMPT,
        "contractor": SERVICE_AGREEMENT_PROMPT,
    }
    
    # Find best match
    doc_lower = document_type.lower()
    for key, template in templates.items():
        if key in doc_lower:
            return template
    
    # Return generic if no match
    return f"Create a professional {document_type} with all standard clauses. Mark fields with [BRACKETS]."
