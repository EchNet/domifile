#!/bin/bash

# Check if at least one argument is provided
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <command_option>"
    exit 1
fi

echo
echo GOOGLE_SERVICE_ACCT_CREDENTIALS...
echo
echo $GOOGLE_SERVICE_ACCT_CREDENTIALS

export ESCAPED_SAI = `echo $GOOGLE_SERVICE_ACCT_CREDENTIALS | sed 's/\\/\\\\/g; s/\"/\\\"/g; s/\n/ /g'`

echo
echo ESCAPED_SAI...
echo
echo $ESCAPED_SAI

# Get the first argument
option="$1"

# Execute different commands based on the value of the first argument
if [ "$option" = "valid" ]; then
  curl -X POST -H "Content-Type: application/json" \
    -d "{\"creator\": \"james.echmalian@gmail.com\", \"service_account_info\": $ESCAPED_SAI }" \
    http://localhost:8080/installation
elif [ "$option" = "missing-service-account" ]; then
    # Replace the following line with the actual command for option2
    pwd
else
    echo "Valid options are: valid, missing-service-account"
    exit 1
fi


