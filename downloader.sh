#!/bin/bash

# Set your S3 bucket and file details
S3_BUCKET="alatau-tr"
S3_PREFIX="md/binance/futures/"
LOCAL_DIR="cups_data"

# Set the start and end dates in "YYYY_MM_DD" format
START_DATE="2024_01_25"
END_DATE="2024_01_28"

# Create the local directory if it doesn't exist
mkdir -p "$LOCAL_DIR"

# Iterate through the date range
current_date="$START_DATE"

while [[ "$current_date" <= "$END_DATE" ]]; do
    # Formulate the S3 key for the current date
    echo "Processing for date: $current_date"
    S3_KEY="$S3_PREFIX$current_date/ETHUSDT_snapshot_md_$current_date.csv.gz"

    # Download the file from S3 using s3cmd
    s3cmd get "s3://$S3_BUCKET/$S3_KEY" "$LOCAL_DIR/"

    # Add additional processing steps here, if needed

    # Optionally, you can clean up the downloaded files after processing
    # rm "$LOCAL_DIR/ETHUSDT_snapshot_md_$current_date.csv.gz"

    # Move to the next date
    current_date=$(date -d "$current_date +1 day" +%Y_%m_%d)
done
