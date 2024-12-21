import base64
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

  def extract_text_from_image(self, file_path):
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

  def extract_text_from_pdf(self, file_path):
    """
      Perform OCR on a PDF file using Google Cloud Vision API.

      Args:
          file_path (str): Path to the PDF file.

      Returns:
          str: Extracted text from the PDF.
    """
    """
      TODO: handle large PDFs
      pdf_source = vision.types.InputConfig(
        gcs_source=vision.types.GcsSource(uri="gs://your-bucket-name/document.pdf"),
        mime_type="application/pdf"
      )
    """

    # Read the PDF file and encode it in base64
    with io.open(file_path, "rb") as pdf_file:
      content = pdf_file.read()

    # Construct the PDF input
    pdf_source = {"content": content, "mime_type": "application/pdf"}

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

    return text
