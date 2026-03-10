from drive import DriveService

DRIVE_FOLDER_ID = "1ZFgdI25w87_nWt0rELtjU51QMTpaBx0o"
service = DriveService()
folder_contents = service.query().children_of(DRIVE_FOLDER_ID).list()
for f in folder_contents:
  if f.trashed:
    raise ValueError("unexpected trashed file")
  print(f.id, f.name, f.mime_type, f.owner)
  if f.properties:
    print(f.properties)

for f in folder_contents:
  if f.mime_type == "image/png":
    print("")
    print("Downloading", f.name)
    service.download_file(f.id, f"./{f.name}")
    break
