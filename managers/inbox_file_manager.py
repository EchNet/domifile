# inbox_manager.py
#
# Manage the processing of files that land in the inbox.
#
from connectors.drive_connector import DriveService
from connectors.ocr_connector import CharacterRecognitionService
from connectors.openai_connector import ChatConnector
import os


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
