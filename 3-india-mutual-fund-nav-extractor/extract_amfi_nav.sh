#!/bin/bash

# Script Usage:
# Download and extract Scheme Name and NAV from AMFI data

URL="https://portal.amfiindia.com/spages/NAVAll.txt"
OUTPUT_DIR="output"
ASSET_DIR="asset"
OUTPUT_FILE="$OUTPUT_DIR/amfi_nav_data.tsv"
DOWNLOAD_FILE="$ASSET_DIR/NAVAll.txt"

# Create directories if they don't exist
mkdir -p "$OUTPUT_DIR"
mkdir -p "$ASSET_DIR"

echo "Downloading AMFI NAV data..."
curl -s -L "$URL" -o "$DOWNLOAD_FILE"

if [ $? -ne 0 ]; then
    echo "Error: Failed to download data from $URL"
    exit 1
fi

echo "Extracting Scheme Name and Net Asset Value..."

# Create TSV with header e.g. Scheme NAme & Assest Value
echo -e "Scheme Name\tNet Asset Value" > "$OUTPUT_FILE"

# Extract only lines with NAV data (contain semicolons and valid data)
# Field 4 = Scheme Name, Field 5 = Net Asset Value
awk -F';' '
    # Skip header line and empty lines
    NF == 6 && $5 ~ /^[0-9]+\.[0-9]+$/ {
        # Clean up the scheme name
        gsub(/^[[:space:]]+|[[:space:]]+$/, "", $4)
        gsub(/&amp;/, "\\&", $4)
        gsub(/&lt;/, "<", $4)
        gsub(/&gt;/, ">", $4)
        print $4 "\t" $5
    }
' "$DOWNLOAD_FILE" >> "$OUTPUT_FILE"

echo "Extraction complete! Data saved to $OUTPUT_FILE"
echo "Total schemes extracted: $(tail -n +2 "$OUTPUT_FILE" | wc -l)"