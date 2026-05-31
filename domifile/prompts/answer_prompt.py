# domifile/prompts/answer_prompt.py

from datetime import date

from domifile.prompts.base import Prompt


class AnswerQuestionPrompt(Prompt):

  MIME_TYPE = "text/plain"

  def build_prompt(self, **kwargs):
    question = kwargs['question']
    context_rows = kwargs['context_rows']

    context = "\n\n-----\n\n".join(
        [f"""[{c['chunk_id']}]
{c['text_value']}""" for c in context_rows])

    today = date.today().isoformat()

    return f"""
You are answering questions about property management documents.

Use ONLY the information in the context.
Do not infer schedules, rules, or patterns not stated in the context.

If the answer is not explicitly stated in the context, say "Not stated in the documents", but suggest relevant information stated in the context if it exists.

Include the source IDs of all context items that are cited. Use the format: [ID]
For example: "The septic system was serviced on March 11, 2026 [43]."
When citing multiple sources, use [ID, ID] format.

Today's date is {today}.

Context:
{context}

Question:
{question}
"""
