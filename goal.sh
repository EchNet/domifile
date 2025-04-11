set -e
source .env
#flask drop_db
#flask create_db
#flask create_installation ech@ech.net $FLORIDA_RENTAL_FOLDER_ID ./service-acct-creds.json
#flask list_installations
#flask apply_installation_pattern patterns/rental.json 1
#flask list_buckets 1
#flask upload_file_to_bucket examples/receipt.pdf 1 INBOX
flask run_bucket_action 1 INBOX
