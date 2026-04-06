# domifile/ingest/doctypes.py

PROPERTY_MANAGEMENT = "property_management"
DOMAIN = PROPERTY_MANAGEMENT

DOC_TYPES = {
    PROPERTY_MANAGEMENT: {
        "meeting_agenda": {
            "description": """
        Document outlining the planned topics, order of discussion, and time
        allocations for a board or association meeting. Typically prepared
        in advance and may include references to supporting materials.
      """,
            "facts": {
                "meeting_date": "date"
            },
            "attributes": {
                "meeting_type": "board | annual | special | budget | committee",
                "status": "draft | final",
                "location": "string"
            }
        },
        "meeting_minutes": {
            "description": """
        Official record of a meeting, capturing attendees, motions,
        decisions, votes, and key discussions. Serves as the authoritative
        historical record of board actions.
      """,
            "facts": {
                "meeting_date": "date"
            },
            "attributes": {
                "meeting_type": "board | annual | special | budget | committee",
                "approval_status": "draft | approved",
                "location": "string"
            }
        },
        "proposal": {
            "description": """
        Estimate or offer from a vendor describing proposed work, scope,
        materials, timeline, and cost. May precede contract execution and
        is often used for bid comparison.
      """,
            "facts": {
                "proposal_date": "date",
                "total_amount": "money"
            },
            "attributes": {
                "vendor": "string",
                "category":
                "landscaping | snow_removal | plumbing | electrical | roofing | paving | painting | cleaning | security | other",
                "status": "draft | submitted | accepted | rejected",
                "project_name": "string"
            }
        },
        "invoice": {
            "description": """
        Request for payment issued by a vendor for goods or services
        provided. Includes line items, service dates, amounts due,
        and payment terms.
      """,
            "facts": {
                "invoice_date": "date",
                "due_date": "date",
                "service_date": "date",
                "total_amount": "money"
            },
            "attributes": {
                "vendor": "string",
                "invoice_number": "string",
                "category":
                "maintenance | utilities | insurance | legal | management | supplies | other",
                "status": "open | paid | overdue | partial"
            }
        },
        "receipt": {
            "description": """
        Proof of payment for a completed transaction. Typically includes
        amount paid, payment method, date, and payee.
      """,
            "facts": {
                "payment_date": "date",
                "total_amount": "money"
            },
            "attributes": {
                "payee":
                "string",
                "payment_method":
                "check | ach | wire | credit_card | cash | other",
                "category":
                "maintenance | utilities | insurance | legal | management | supplies | other"
            }
        },
        "vendor_contract": {
            "description": """
        Executed agreement between the association and a vendor defining
        scope of work, pricing, duration, responsibilities, and legal terms.
      """,
            "facts": {
                "contract_date": "date",
                "effective_date": "date",
                "expiration_date": "date",
                "total_amount": "money"
            },
            "attributes": {
                "vendor": "string",
                "category":
                "landscaping | snow_removal | plumbing | electrical | roofing | paving | painting | cleaning | security | management | other",
                "renewal_type": "fixed_term | auto_renew | month_to_month",
                "status": "draft | executed | expired | terminated"
            }
        },
        "vendor_insurance": {
            "description": """
        Certificate of insurance or related documentation provided by a
        vendor, demonstrating coverage (e.g., liability, workers’ comp)
        during the term of work performed for the association.
      """,
            "facts": {
                "effective_date": "date",
                "expiration_date": "date"
            },
            "attributes": {
                "vendor": "string",
                "coverage_type": "general_liability | workers_comp | auto | umbrella | other",
                "carrier": "string",
                "status": "active | expired | cancelled"
            }
        },
        "utility_bill": {
            "description": """
        Statement from a utility provider (e.g., water, electricity, gas,
        sewer) showing usage, billing period, and amount due.
      """,
            "facts": {
                "statement_date": "date",
                "coverage_start": "date",
                "coverage_end": "date",
                "due_date": "date",
                "total_amount": "money"
            },
            "attributes": {
                "provider": "string",
                "utility_type": "water | sewer | electric | gas | trash | internet | other",
                "account_number": "string",
                "status": "open | paid | overdue"
            }
        },
        "insurance_policy": {
            "description": """
        Formal insurance document describing coverage terms, limits,
        deductibles, effective dates, and insured parties for the property
        or association.
      """,
            "facts": {
                "effective_date": "date",
                "expiration_date": "date",
                "premium_amount": "money"
            },
            "attributes": {
                "carrier": "string",
                "policy_number": "string",
                "policy_type":
                "master | liability | property | flood | umbrella | d_and_o | other",
                "status": "active | expired | cancelled | superseded"
            }
        },
        "assessment_notice": {
            "description": """
        Notice to owners regarding required payments (regular dues or
        special assessments), including amount, due date, and purpose.
      """,
            "facts": {
                "notice_date": "date",
                "due_date": "date",
                "total_amount": "money"
            },
            "attributes": {
                "assessment_type": "regular | special",
                "target": "all_owners | unit_specific",
                "reason": "operations | reserves | repair | emergency | other",
                "status": "issued | revised | rescinded"
            }
        },
        "violation_notice": {
            "description": """
        Notification to an owner or occupant identifying a violation of
        bylaws, rules, or regulations, often including required corrective
        action and deadline.
      """,
            "facts": {
                "notice_date": "date",
                "cure_deadline": "date"
            },
            "attributes": {
                "violation_type":
                "noise | pets | parking | architectural | maintenance | trash | occupancy | other",
                "recipient": "owner | tenant | occupant | unit",
                "severity": "warning | fine | legal",
                "status": "open | cured | escalated | closed"
            }
        },
        "bank_statement": {
            "description": """
        Bank statement.
      """,
            "facts": {
                "statement_date": "date",
                "coverage_start": "date",
                "coverage_end": "date",
                "ending_balance": "money"
            },
            "attributes": {
                "bank": "string",
                "account_type": "operating | reserve | escrow | other",
                "account_last4": "string"
            }
        },
        "reserve_study": {
            "description": """
        Long-term financial planning document analyzing capital components
        (e.g., roofs, paving) and forecasting funding requirements to
        maintain reserves and avoid special assessments.
      """,
            "facts": {
                "study_date": "date"
            },
            "attributes": {
                "prepared_by": "string",
                "study_type": "full | update | with_site_visit | without_site_visit",
                "funding_level": "full | threshold | baseline | other"
            }
        },
        "municipal_notice": {
            "description": """
        Notice from the city or town regarding safety, infrastructure, utilities,
        regulations, inspections, or public works affecting the property.
      """,
            "facts": {
                "notice_date": "date",
                "effective_date": "date",
                "deadline": "date"
            },
            "attributes": {
                "issuing_authority": "string",
                "notice_type":
                "inspection | utility | code | water_quality | public_works | tax | safety | other",
                "severity": "info | warning | required_action | emergency"
            }
        },
        "newsletter": {
            "description": """
        Periodical communication from board of trustees / management company
        to the occupants and property owners, including updates, reminders,
        and community information.
      """,
            "facts": {
                "publication_date": "date"
            },
            "attributes": {
                "periodicity": "monthly | quarterly | annual | ad_hoc",
                "publisher": "board | management_company | committee",
                "audience": "owners | residents | both"
            }
        },
        "owner_communication": {
            "description": """
        E.g., emails from owners, letters, contact form submissions,
        complaints, requests, ...
      """,
            "facts": {
                "communication_date": "date"
            },
            "attributes": {
                "channel": "email | letter | portal",
                "category": "complaint | request | question | info",
                "sender": "owner name | unit number",
                "urgency": "low | normal | high"
            }
        },
    }
}

DOC_TYPE_OTHER = "other"
DOC_TYPE_UNKNOWN = "unknown"
