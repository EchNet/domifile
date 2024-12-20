import io
from google.cloud import vision
from environment import get_service_account_info_from_environment


class CharacterRecognitionService:

  def __init__(self):
    # Google Cloud Vision client
    service_account_info = get_service_account_info_from_environment()
    self.vision_client = \
        vision.ImageAnnotatorClient.from_service_account_info(service_account_info)

  def __enter__(self):
    return OcrUtils(self.vision_client)

  # No-op
  def __exit__(self, exc_type, exc_value, traceback):
    pass


class OcrUtils:

  def __init__(self, vision_client):
    self.vision_client = vision_client

  def extract_text(self, file_path):
    """
      Perform OCR on a local image or PDF file using Google Cloud Vision API.
      
      Args:
          file_path (str): Path to the file for OCR.
      
      Returns:
          str: Extracted text from the file.
    """
    with io.open(file_path, "rb") as image_file:
      content = image_file.read()

    image = vision.Image(content=content)
    response = self.vision_client.text_detection(image=image)

    if response.error.message:
      raise Exception(f"Vision API Error: {response.error.message}")

    # Extract and return text
    return response.full_text_annotation.text
