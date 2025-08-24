#!/bin/bash

# ==============================================================================
# Fair Maps: Master Script for Nationwide Analysis
# ==============================================================================
# This script automates the process of running the redistricting analysis for
# states whose data has been MANUALLY downloaded and prepared according to the
# manual download guide.
#
# USAGE:
# 1. Manually download and unzip state data into the 'data/STATE_ABBR/' folders.
# 2. Make sure your virtual environment is active: source venv/bin/activate
# 3. Make this script executable (only need to do this once): chmod +x run_all_states.sh
# 4. Run the script: ./run_all_states.sh
# ==============================================================================

# Activate the Python virtual environment
source venv/bin/activate

# --- CONFIGURATION ---

# Define a directory to store all output maps
OUTPUT_DIR="output_maps"

# Create the output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# State configurations: "STATE_ABBR;NUM_DISTRICTS"
# The Python script will automatically find the population column.
STATES_TO_RUN=(
    "AL;7"
    "AK;1"
    "AZ;9"
    "AR;4"
    "CA;52"
    "CO;8"
    "CT;5"
    "DE;1"
    "FL;28"
    "GA;14"
    "HI;2"
    "ID;2"
    "IL;17"
    "IN;9"
    "IA;4"
    "KS;4"
    "KY;6"
    "LA;6"
    "ME;2"
    "MD;8"
    "MA;9"
    "MI;13"
    "MN;8"
    "MS;4"
    "MO;8"
    "MT;2"
    "NE;3"
    "NV;4"
    "NH;2"
    "NJ;12"
    "NM;3"
    "NY;26"
    "NC;14"
    "ND;1"
    "OH;15"
    "OK;5"
    "OR;6"
    "PA;17"
    "RI;2"
    "SC;7"
    "SD;1"
    "TN;9"
    "TX;38"
    "UT;4"
    "VT;1"
    "VA;11"
    "WA;10"
    "WV;2"
    "WI;8"
    "WY;1"
)

# --- SCRIPT LOGIC ---

START_TIME=$(date +%s)
PROCESSED_COUNT=0
TOTAL_STATES=${#STATES_TO_RUN[@]}

echo "Starting nationwide redistricting analysis..."
echo "=================================================================="

for state_config in "${STATES_TO_RUN[@]}"; do
    IFS=';' read -r STATE_ABBR NUM_DISTRICTS <<< "$state_config"
    PROCESSED_COUNT=$((PROCESSED_COUNT + 1))

    echo ""
    echo "($PROCESSED_COUNT/$TOTAL_STATES) --- Checking for: $STATE_ABBR ---"

    # Check if the data directory for the state exists
    if [ ! -d "data/$STATE_ABBR" ]; then
        echo "Data directory 'data/$STATE_ABBR' not found. Skipping."
        continue
    fi
    
    # Check if a shapefile exists in the directory
    if ! ls data/$STATE_ABBR/*.shp 1> /dev/null 2>&1; then
        echo "Shapefile not found in 'data/$STATE_ABBR'. Skipping."
        continue
    fi

    echo "Data found. Starting analysis for $STATE_ABBR..."
    
    # --- Run Analysis ---
    python3 analyze_maps.py \
        --state "$STATE_ABBR" \
        --districts "$NUM_DISTRICTS" \
        --output_dir "$OUTPUT_DIR"

    if [ $? -eq 0 ]; then
        echo "--- Successfully completed analysis for: $STATE_ABBR ---"
    else
        echo "--- ERROR: Analysis failed for: $STATE_ABBR ---"
    fi
done

# --- Merge all generated maps into a single image ---

echo ""
echo "=================================================================="
echo "Attempting to merge all state maps into a single image..."

if ! command -v montage &> /dev/null; then
    echo "WARNING: ImageMagick 'montage' command not found. Skipping merge."
    echo "Please install it to enable this feature (e.g., 'sudo apt-get install imagemagick')."
else
    montage "$OUTPUT_DIR"/*.png -geometry +5+5 -tile 10x "USA_master_map.png"
    if [ $? -eq 0 ]; then
        echo "Successfully created 'USA_master_map.png'!"
    else
        echo "ERROR: Failed to merge maps. There might have been an issue with the montage command."
    fi
fi

END_TIME=$(date +%s)
ELAPSED_TIME=$((END_TIME - START_TIME))

echo ""
echo "=================================================================="
echo "Nationwide analysis complete!"
echo "Total time elapsed: $ELAPSED_TIME seconds."
