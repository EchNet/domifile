# domifile/prompts/base.py

import json
import logging
import re

from abc import ABC, abstractmethod
from domifile.openai_adapter import create_response

logger = logging.getLogger(__name__)


class Prompt(ABC):

  def run(self, **kwargs):
    # Interpolate the prompt string.
    prompt = self.build_prompt(**kwargs)
    prompt = prompt.strip()
    logger.debug(prompt)

    # Query the AI.
    text = create_response(prompt)
    if not text:
      raise ValueError("Empty response")
    text = text.strip()
    logger.debug(text)

    # Remove ```json ... ``` or ``` ... ```
    match = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL)
    if match:
      text = match.group(1).strip()

    # Parse JSON - TODO: handle parse error.
    return json.loads(text)

  @abstractmethod
  def build_prompt(self, **kwargs):
    pass
