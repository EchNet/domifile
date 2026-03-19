import logging
from openai import OpenAI

logger = logging.getLogger(__name__)
openai = OpenAI()

EMBEDDING_MODEL = "text-embedding-3-small"

RESPONSE_MODEL = "gpt-4.1-mini"


def create_embedding(input):
  """ """

  result = openai.embeddings.create(
      model=EMBEDDING_MODEL,
      input=input,
  )

  data = result.data
  logger.debug(f"input={input} embeddings={len(data)}")

  return data[0].embedding


def create_response(input):
  """ """

  result = openai.responses.create(
      model=RESPONSE_MODEL,
      temperature=0,
      input=input,
  )

  return result.output_text
