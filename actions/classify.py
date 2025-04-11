import os
import mimetypes
from googleapiclient.http import MediaFileUpload
import os

from . import Action
from connectors.openai_connector import AiAssistantFactory
from connectors.ocr_connector import CharacterRecognitionService
from managers.InstallationDriveManager import InstallationDriveManager


def classify(file_id, bucket):
  print(f"Classified file {file_id} into bucket: {bucket}")


class ClassifyAction(Action):
  """ Classify a file that has been deposited into the INBOX """

  def execute_action(self):
    if not self.args:
      raise ValueError("File argument is required")
    file = self.args[0]
    if not (hasattr(file, "id") and hasattr(file, "name")):
      raise ValueError("The argument must be a File")

    installation_drive_mgr = InstallationDriveManager(self.context)
    buckets = installation_drive_mgr.get_buckets()
    bucket_names = [b.name for b in buckets]

    if not file.mime_type.startswith("image/"):
      raise ApplicationError("Sorry, I can only deal with images at this point.")

    image_bytes = installation_drive_mgr.

    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[{
            "role":
            "system",
            "content":
            f"You are a document classifier. Choose one of the following categories for the document: {', '.join(bucket_names)}, or None.",
            "role":
            "user",
            "content": [{
                "type": "text",
                "text": "Classify this document."
            }, {
                "type": "image_url",
                "image_url": {
                    "url": "data:image/jpeg;base64," + img.read().encode("base64").decode()
                }
            }]
        }],
        max_tokens=10)
    return response.choices[0].message.content.strip()


def upload_to_drive(file_path, folder_id):
  file_name = os.path.basename(file_path)
  mime_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
  file_metadata = {"name": file_name}
  if folder_id:
    file_metadata["parents"] = [folder_id]

  media = MediaFileUpload(file_path, mimetype=mime_type)
  file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
  return file.get("id")


def process_folder(input_dir):
  for file_name in os.listdir(input_dir):
    if file_name.lower().endswith((".jpg", ".jpeg", ".png")):
      file_path = os.path.join(input_dir, file_name)
      print(f"Classifying: {file_name}...")
      bucket = classify_image(file_path)
      folder_id = BUCKETS.get(bucket, None)
      upload_to_drive(file_path, folder_id)
      print(f"Stored in: {bucket}\n")



class InboxFileManager:
  """
    InboxFileManager is responsible for processing files in the inbox.
  """

  def __init__(self, installation_manager, file):
    self.installation_manager = installation_manager
    self.file = file

  @property
  def drive_service(self):
    return self.installation_manager.drive_service

  def process_inbox_file(self):
    file_id = self.file["id"]
    file_name = self.file["name"]
    print(f"START process inbox file {file_id} {file_name}")
    if self.create_lock_file(file_id):
      extracted_text = self.run_character_recognition()
      file_properties = self.run_ai(extracted_text)
      print(f"DONE process inbox file {file_id} - {file_properties}")
    else:
      print(f"LOCKED inbox file {file_id}")

  def create_lock_file(self, file_id):
    return True

  def run_character_recognition(self):
    file_id = self.file["id"]
    file_mime_type = self.file["mime_type"]

    character_recognition_service = CharacterRecognitionService()
    try:
      # Download the file.
      temp_file_name = f"/tmp/{file_id}.download"
      self.drive_service.download_file(file_id, temp_file_name)
      extracted_text = character_recognition_service.extract_text(temp_file_name, file_mime_type)
      print("Extracted Text:")
      print(extracted_text)
    except Exception as e:
      print(f"ERROR processing file {file_id}: {e}")
    finally:
      if os.path.exists(temp_file_name):
        os.remove(temp_file_name)

  def run_ai(self, extracted_text):
    return "TBD"
