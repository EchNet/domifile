import os
from drive_service import DriveService
from ocr import CharacterRecognitionService


def run_file_worker(file_id):
  print(f"START process inbox file {file_id}")

  temp_file_name = f"/tmp/{file_id}.download"

  with DriveService() as drive_service:
    mime_type = drive_service.get_file_mime_type(file_id)
    print(f"file {file_id} is {mime_type}")
    with CharacterRecognitionService() as character_recognition_service:
      try:
        drive_service.download_file(file_id, temp_file_name)
        if mime_type == "application/pdf":
          extracted_text = character_recognition_service.extract_text_from_pdf(temp_file_name)
        else:
          extracted_text = character_recognition_service.extract_text_from_image(temp_file_name)
        print("Extracted Text:")
        print(extracted_text)
      except Exception as e:
        print(f"file {file_id}: {e}")
      finally:
        if os.path.exists(temp_file_name):
          os.remove(temp_file_name)

  print(f"FINISH process inbox file {file_id}")
