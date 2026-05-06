set -e

export DRIVE_ROOT="https://drive.google.com/drive/u/0/folders/1sUY1cB2GThDFRx9D7rIFLZklRssojm7m"
export DRIVE_FOCUS="1H_6EqaVm8qAKNSDOgDvOAgWP98f7q5Ij"

#flask clear-ingest-drive $DRIVE_FOCUS
flask ingest-drive $DRIVE_ROOT
#flask examine-drive-file $DRIVE_FOCUS
