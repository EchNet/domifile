# domifile/prompts/planner_prompt.py

from domifile.domains import PropertyManagementDomain, DocType
from domifile.prompts.base import Prompt


class QueryPlannerPrompt(Prompt):

  def build_prompt(self, **kwargs):
    domain = PropertyManagementDomain()
    question = kwargs['question']

    return f"""
Generate up to 4 distinct search queries for retrieval in a {domain.name} document system.

Goal:
Maximize recall across different document types and wording styles.

Rules:
- 2-6 words each
- no punctuation
- no full sentences
- each query must use meaningfully different terminology
- include likely document vocabulary when useful
- prefer noun phrases over questions
- avoid repeating the same key terms unless necessary
- format results as a JSON array, for example ```["sprinkler maintenance", "irrigation planning"]```
- emit ONLY correct JSON

Possible document types:
{"\n".join(domain.get_doc_type_names())}

Question:
{question}
"""
