# domifile/domains.py

import json
from enum import Enum


class DocType(Enum):
  OTHER = (
      "other",
      "Document of a recognizable type that does not appear in the domain's list of types.",
  )
  UNKNOWN = (
      "unknown",
      "Document of no known type.",
  )
  MEETING_AGENDA = (
      "meeting_agenda",
      """
        Document outlining the planned topics, order of discussion, and time allocations
        for a board or association meeting. Typically prepared in advance and may include
        references to supporting materials.
      """,
      {
          "event_date": "date"
      },
      {
          "meeting_type": "board | annual | special | budget | committee",
          "status": "draft | final",
          "location": "string",
      },
  )
  MEETING_MINUTES = (
      "meeting_minutes",
      """
        Official record of a meeting, capturing attendees, motions, decisions, votes, and
        key discussions. Serves as the authoritative historical record of board actions.
      """,
      {
          "event_date": "date",
          "document_date": "date",
      },
      {
          "meeting_type": "board | annual | special | budget | committee",
          "approval_status": "draft | approved",
          "location": "string",
      },
  )
  PROPOSAL = (
      "proposal",
      """
        Estimate or offer from a vendor describing proposed work, scope, materials,
        timeline, and cost. May precede contract execution and is often used for bid
        comparison.
      """,
      {
          "document_date": "date",
          "total_amount": "money",
      },
      {
          "vendor": "string",
          "category":
          "landscaping | snow_removal | plumbing | electrical | roofing | paving | painting | cleaning | security | other",
          "status": "draft | submitted | accepted | rejected",
          "project_name": "string",
      },
  )
  INVOICE = (
      "invoice",
      """
      Request for payment issued by a vendor for goods or services provided. Includes
      line items, service dates, amounts due, and payment terms.
    """,
      {
          "document_date": "date",
          "due_date": "date",
          "service_date": "date",
          "total_amount": "money",
      },
      {
          "vendor": "string",
          "invoice_number": "string",
          "category":
          "maintenance | utilities | insurance | legal | management | supplies | other",
          "status": "open | paid | overdue | partial",
      },
  )
  RECEIPT = (
      "receipt",
      """
        Proof of payment for a completed transaction. Typically includes
        amount paid, payment method, date, and payee.
      """,
      {
          "document_date": "date",
          "total_amount": "money",
      },
      {
          "payee": "string",
          "payment_method": "check | ach | wire | credit_card | cash | other",
          "category":
          "maintenance | utilities | insurance | legal | management | supplies | other",
      },
  )
  VENDOR_CONTRACT = (
      "vendor_contract",
      """
        Executed agreement between the association and a vendor defining scope of work,
        pricing, duration, responsibilities, and legal terms.
      """,
      {
          "document_date": "date",
          "effective_date": "date",
          "expiration_date": "date",
          "total_amount": "money",
      },
      {
          "vendor": "string",
          "category":
          "landscaping | snow_removal | plumbing | electrical | roofing | paving | painting | cleaning | security | management | other",
          "renewal_type": "fixed_term | auto_renew | month_to_month",
          "status": "draft | executed | expired | terminated",
      },
  )
  VENDOR_INSURANCE = (
      "vendor_insurance",
      """
        Certificate of insurance or related documentation provided by a
        vendor, demonstrating coverage (e.g., liability, workers’ comp)
        during the term of work performed for the association.
      """,
      {
          "effective_date": "date",
          "expiration_date": "date",
      },
      {
          "vendor": "string",
          "coverage_type": "general_liability | workers_comp | auto | umbrella | other",
          "carrier": "string",
          "status": "active | expired | cancelled",
      },
  )
  UTILITY_BILL = (
      "utility_bill",
      """
        Statement from a utility provider (e.g., water, electricity, gas, sewer)
        showing usage, billing period, and amount due.
      """,
      {
          "document_date": "date",
          "date_range_start": "date",
          "date_range_end": "date",
          "due_date": "date",
          "total_amount": "money",
      },
      {
          "provider": "string",
          "utility_type": "water | sewer | electric | gas | trash | internet | other",
          "account_number": "string",
          "status": "open | paid | overdue",
      },
  )
  INSURANCE_POLICY = (
      "insurance_policy",
      """
        Formal insurance document describing coverage terms, limits, deductibles,
        effective dates, and insured parties for the property or association.
      """,
      {
          "effective_date": "date",
          "expiration_date": "date",
          "premium_amount": "money",
      },
      {
          "carrier": "string",
          "policy_number": "string",
          "policy_type": "master | liability | property | flood | umbrella | d_and_o | other",
          "status": "active | expired | cancelled | superseded",
      },
  )
  ASSESSMENT_NOTICE = (
      "assessment_notice",
      """
        Notice to owners regarding required payments (regular dues or
        special assessments), including amount, due date, and purpose.
      """,
      {
          "document_date": "date",
          "due_date": "date",
          "total_amount": "money",
      },
      {
          "assessment_type": "regular | special",
          "target": "all_owners | unit_specific",
          "reason": "operations | reserves | repair | emergency | other",
          "status": "issued | revised | rescinded",
      },
  )
  VIOLATION_NOTICE = (
      "violation_notice",
      """
        Notification to an owner or occupant identifying a violation of bylaws, rules, or
        regulations, often including required corrective action and deadline.
      """,
      {
          "notice_date": "date",
          "cure_deadline": "date",
      },
      {
          "violation_type":
          "noise | pets | parking | architectural | maintenance | trash | occupancy | other",
          "recipient": "owner | tenant | occupant | unit",
          "severity": "warning | fine | legal",
          "status": "open | cured | escalated | closed",
      },
  )
  BANK_STATEMENT = (
      "bank_statement",
      "Bank statement.",
      {
          "document_date": "date",
          "date_range_start": "date",
          "date_range_end": "date",
          "ending_balance": "money",
          "transactions": "list of (money, description)"
      },
      {
          "bank": "string",
          "account_type": "operating | reserve | escrow | other",
          "account_last4": "string"
      },
  )
  RESERVE_STUDY = (
      "reserve_study",
      """
        Long-term financial planning document analyzing capital components (e.g., roofs,
        paving) and forecasting funding requirements to maintain reserves and avoid
        special assessments.
      """,
      {
          "document_date": "date",
      },
      {
          "prepared_by": "string",
          "study_type": "full | update | with_site_visit | without_site_visit",
          "funding_level": "full | threshold | baseline | other",
      },
  )
  MUNICIPAL_NOTICE = (
      "municipal_notice",
      """
        Notice from the city or town regarding safety, infrastructure, utilities,
        regulations, inspections, or public works affecting the property.
      """,
      {
          "document_date": "date",
          "effective_date": "date",
          "deadline": "date",
      },
      {
          "issuing_authority": "string",
          "notice_type":
          "inspection | utility | code | water_quality | public_works | tax | safety | other",
          "severity": "info | warning | required_action | emergency",
      },
  )
  NEWSLETTER = (
      "newsletter",
      """
        Periodical communication from board of trustees / management company to the
        residents and property owners, including updates, reminders, and community
        information.
      """,
      {
          "document_date": "date",
      },
      {
          "periodicity": "monthly | quarterly | annual | ad_hoc",
          "publisher": "board | management_company | committee",
          "audience": "owners | residents | both",
      },
  )
  OWNER_COMMUNICATION = (
      "owner_communication",
      """
        Written statements from owners expressing complaints, requests, questions, or
        other information.
      """,
      {
          "document_date": "date",
      },
      {
          "channel": "email | letter | portal",
          "category": "complaint | request | question | info",
          "sender": "owner name | unit number",
          "urgency": "low | normal | high",
      },
  )
  CONTACT_INFO = (
      "contact_info",
      """
        Homeowner lists, resident/tenant lists, contact information for vendors and
        services, emergency phone numbers, ...
      """,
      {
          "document_date": "date"
      },
      {},
  )

  def __init__(self, code, description, facts={}, attributes={}):
    self.code = code
    self.description = description
    self.facts = facts
    self.attributes = attributes

  def to_dict(self):
    return {
        "code": self.code,
        "description": self.description,
        "facts": self.facts,
        "attributes": self.attributes,
    }

  def to_json(self):
    return json.dumps(self.to_dict(), indent=2)


class Domain:

  class Meta:
    NAME = "??"
    DOC_TYPES = []

  @classmethod
  @property
  def name(cls):
    return cls.Meta.NAME

  @classmethod
  def format_doc_types(cls):
    return [doc_type.to_json() for doc_type in cls.Meta.DOC_TYPES]

  @classmethod
  def get_doc_type_names(cls):
    return [doc_type.code for doc_type in cls.Meta.DOC_TYPES]


class PropertyManagementDomain(Domain):

  class Meta:
    NAME = "property management"

    DOC_TYPES = (
        DocType.MEETING_AGENDA,
        DocType.MEETING_MINUTES,
        DocType.PROPOSAL,
        DocType.INVOICE,
        DocType.RECEIPT,
        DocType.VENDOR_CONTRACT,
        DocType.VENDOR_INSURANCE,
        DocType.UTILITY_BILL,
        DocType.INSURANCE_POLICY,
        DocType.ASSESSMENT_NOTICE,
        DocType.VIOLATION_NOTICE,
        DocType.BANK_STATEMENT,
        DocType.RESERVE_STUDY,
        DocType.MUNICIPAL_NOTICE,
        DocType.NEWSLETTER,
        DocType.OWNER_COMMUNICATION,
        DocType.CONTACT_INFO,
    )
