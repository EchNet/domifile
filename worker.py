import os
from drive_service import DriveService
from ocr import CharacterRecognitionService


def run_file_worker(file_id):
  print(f"START process inbox file {file_id}")

  temp_file_name = f"/tmp/{file_id}.download"

  with DriveService() as drive_service:
    with CharacterRecognitionService() as character_recognition_service:
      try:
        drive_service.download_file(file_id, temp_file_name)
        extracted_text = character_recognition_service.extract_text(temp_file_name)
        print("Extracted Text:")
        print(extracted_text)
      except Exception as e:
        print(f"file {file_id}: {e}")
      finally:
        if os.path.exists(temp_file_name):
          os.remove(temp_file_name)

  print(f"FINISH process inbox file {file_id}")
