# ocr.py
#
# Wrap the Google Cloud Vision services.
#
import io
from google.cloud import vision


class CharacterRecognitionService:

  def __init__(self, context):
    """
    """
    self.vision_client = (vision.ImageAnnotatorClient.from_service_account_info(
        context.service_account_info))

  def __enter__(self):
    return self

  # No-op
  def __exit__(self, exc_type, exc_value, traceback):
    pass

  def extract_text(self, file_path, mime_type):
    """
      Perform OCR on a local image or PDF file using Google Cloud Vision API.
      
      Args:
          file_path (str): Path to the file for OCR.
      
      Returns:
          str: Extracted text from the file.
    """

    # Load file content.
    with io.open(file_path, "rb") as image_file:
      content = image_file.read()

    if mime_type == "application/pdf":
      # Construct the PDF input
      pdf_source = {"content": content, "mime_type": mime_type}

      # Construct the request
      request = {
          "input_config": pdf_source,
          "features": [{
              "type": vision.Feature.Type.DOCUMENT_TEXT_DETECTION
          }]
      }

      # Send the request
      responses = self.vision_client.batch_annotate_files(requests=[request]).responses

      # Process the responses
      text = ""
      for response in responses:
        for page_response in response.responses:
          if page_response.error.message:
            raise Exception(f"Vision API Error: {page_response.error.message}")
          text += page_response.full_text_annotation.text
    else:
      image = vision.Image(content=content)
      response = self.vision_client.text_detection(image=image)

      if response.error.message:
        raise Exception(f"Vision API Error: {response.error.message}")

      # Extract and return text
      text = response.full_text_annotation.text

    return text
