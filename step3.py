import os
from domifile.drive import DriveService
from domifile.ingest.extractor import TextExtractor

DRIVE_FOLDER_ID = "1ZFgdI25w87_nWt0rELtjU51QMTpaBx0o"
service = DriveService()
folder_contents = service.query().children_of(DRIVE_FOLDER_ID).list()
for f in folder_contents:
  assert not f.trashed
  if f.mime_type in ("image/png", "application/pdf"):
    print(f"\nDownloading {f.name}...")
    service.download_file(f.id, f"./{f.name}")
    text = TextExtractor.extract(f.name, f.mime_type)
    print("")
    print(text[:1000])
    print("")
    os.remove(f.name)
