import base64
import json
import logging
import mimetypes
import os
import tempfile
from flask import current_app as app
from pprint import pp

from connectors.openai_connector import openai_api
from connectors.ocr_connector import CharacterRecognitionService
from errors import ApplicationError
from managers.InstallationBucketManager import InstallationBucketManager
from pdf_to_image import pdf_to_image
from utils import strip_json_markers

logger = logging.getLogger(__name__)


class Classifier:
  """ Classify a file that has been deposited into an INBOX bucket """

  def __init__(self, bucket_context):
    self.bucket_context = bucket_context

  def classify_drive_file(self, file):
    DriveFileClassifier(self.bucket_context, file).classify()


class DriveFileClassifier:

  def __init__(self, bucket_context, file):
    self.bucket_context = bucket_context
    self.file = file

  @property
  def drive_connector(self):
    return self.bucket_context.drive_connector

  def classify(self):
    file = self.file
    if file.mime_type == "application/pdf" or file.name.endswith(".pdf"):
      self.download_and_classify_pdf(file)
    elif file.mime_type.startswith("image/"):
      self.download_and_classify_image(file)
    else:
      raise ApplicationError("Sorry, I can only deal with images at this point.")

  def download_and_classify_pdf(self, file):
    logger.info(f"File to be classified - {file.name} - is a PDF.")

    # Create a temporary file.
    with tempfile.NamedTemporaryFile(delete=False, suffix="pdf") as tmp_file:
      pdf_path = tmp_file.name

    try:
      # Download from Drive
      self.bucket_context.drive_connector.download_file(file, pdf_path)
      logger.info(f"Downloaded PDF file to {pdf_path}...")

      # Convert to PNG.
      png_path = pdf_to_image(pdf_path)
      logger.info(f"Converted to PNG {png_path}.")

    finally:
      os.remove(pdf_path)

    # Go to work on the PNG.
    try:
      self.classify_local_image(png_path, "image/png")
    finally:
      os.remove(png_path)

  def download_and_classify_image(self, file):
    logger.info(f"File {file.name} is an image (mime type {file.mime_type}).")

    # Create a temporary file.
    suffix = os.splitext(file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
      image_path = tmp_file.name

    try:
      # Download from Drive
      self.bucket_context.drive_connector.download_file(file, image_path)
      logger.info(f"Downloaded image file to {image_path}.")
      self.classify_local_image(image_path, file.mime_type)
    finally:
      os.remove(image_path)

  def classify_local_image(self, image_path, image_mime_type):
    extracted_text = self.run_character_recognition(image_path, image_mime_type)
    file_properties = self.run_ai(image_path, image_mime_type, extracted_text)
    pp(file_properties)
    destination_bucket_name = file_properties.get("bucket")
    if destination_bucket_name is not None and destination_bucket_name != "None":
      logger.info(f"Classified file {self.file.id} into bucket {destination_bucket_name}")
      destination_bucket_context = app.create_bucket_context(
          installation=self.bucket_context.installation, bucket_name=destination_bucket_name)
      print(f"Moving file {self.file.id} into bucket {destination_bucket_name}")
      self.drive_connector.move_file(self.file, new_parent=destination_bucket_context.bucket)

  @staticmethod
  def image_to_openai_base64(image_path, mime_type):
    with open(image_path, "rb") as f:
      encoded = base64.b64encode(f.read()).decode("utf-8")
      return f"data:{mime_type};base64,{encoded}"

  def run_ai(self, image_path, image_mime_type, text):
    buckets = InstallationBucketManager(self.bucket_context).list_buckets()
    bucket_names = [b.name for b in buckets]

    image_url = self.image_to_openai_base64(image_path, image_mime_type)

    response = openai_api.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{
            "role":
            "system",
            "content":
            f"You are a document classifier. "
            f"When asked to classify a document, you will respond with a JSON object. "
            f"The JSON will include at least one property with key 'bucket' and one of "
            f"the following values, depending on your categorization of the document: "
            f"{', '.join(bucket_names)}, or None. "
            f"Property 'date' should be included, if available. Dates must be formatted YYYY-MM-DD or YYYY-MM."
            f"Property 'type' should be included.  This is the general categorization of the document, like "
            "the bucket property, but unfettered by a pick list. "
            f"Property 'sender' should be included, if available.  This is the name of the vendor or source "
            f"organization. "
            f"Include whatever additional properties seem called for."
        }, {
            "role":
            "user",
            "content": [{
                "type":
                "text",
                "text":
                f"Classify this document. "
                f"Here is also some text extracted by OCR, in case it helps: {text}"
            }, {
                "type": "image_url",
                "image_url": {
                    "url": image_url,
                }
            }]
        }])

    try:
      json_reply = strip_json_markers(response.choices[0].message.content)
      return json.loads(json_reply)
    except:
      logger.exception()
      return {}

  # Do we need this, or will OpenAI do just fine by itself?
  def run_character_recognition(self, image_path, mime_type):
    character_recognition_service = CharacterRecognitionService(self.bucket_context)
    extracted_text = character_recognition_service.extract_text(image_path, mime_type)
    logger.info("Extracted text...")
    logger.info(extracted_text)
