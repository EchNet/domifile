# domifile/query.py


def answer_question(question):
  return {
      "answer": "I don't know",
      "sources": [],
      "citations": [],
  }


def get_insurance_spend(session, start, end):
  return session.query(func.sum(ExtractedFact.amount)).filter(
      ExtractedFact.fact_type == "transaction", ExtractedFact.category == "insurance",
      ExtractedFact.effective_date >= start, ExtractedFact.effective_date <= end).scalar()
