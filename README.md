# Fair Maps: A Congressional Redistricting Analysis Tool

## Overview

This project is a Python-based tool designed to explore and analyze congressional redistricting. It uses an algorithmic approach to generate thousands of possible, non-partisan districting plans for a given state. By analyzing this large collection (or "ensemble") of maps, the tool identifies a single, representative map that serves as a baseline for fairness.

The goal is to create maps that are unbiased, non-partisan, and racially blind, adhering only to the core principles of equal population and geographic contiguity. This allows for a data-driven comparison against existing or proposed congressional maps to identify potential gerrymandering.

## Core Concepts

This tool is built on a powerful computational method called **Ensemble Analysis** using a **Markov Chain Monte Carlo (MCMC)** algorithm.

> **What does that mean?**
> Instead of trying to find one "perfect" map, we create a "sea" of thousands of valid maps. The algorithm starts with one map and then makes a series of small, random changes—like swapping a few neighborhoods between adjacent districts—to create the next map in the chain.

> **Why do this?**
> By generating a massive, diverse sample of possible maps, we can understand what a "typical" districting plan for a state looks like when only geography and population are considered. The final map produced by this script is the single plan from our simulation that is the most similar to the statistical average of all the plans we generated.

## Requirements

* A Linux environment (tested on Crostini)
* Python 3 (e.g., 3.9+)
* `pip` (Python package installer)
* `venv` (for creating virtual environments)

## Setup Instructions

These steps will guide you through setting up the project environment from scratch.

1.  **Create a Project Directory**

    First, create a folder for the project and navigate into it.
    ```bash
    mkdir redistricting_project
    cd redistricting_project
    ```

2.  **Create and Activate a Virtual Environment**

    Using a virtual environment is crucial to keep the project's dependencies separate from your system's Python packages.
    ```bash
    # Create the virtual environment (creates a 'venv' folder)
    python3 -m venv venv

    # Activate the environment. You must do this every time you start a new terminal session.
    source venv/bin/activate
    ```
    Your terminal prompt should now start with `(venv)`, indicating the environment is active.

3.  **Install Required Python Libraries**

    With the virtual environment active, install the necessary libraries using `pip`.
    ```bash
    pip install gerrychain geopandas pandas matplotlib networkx
    ```

## Data Acquisition

The program requires geographic shapefiles (`.shp`) that contain the boundaries and population counts for a state's Voting Tabulation Districts (VTDs).

1.  **Directory Structure**

    It is recommended to create a `data` directory to store the shapefiles for each state.
    ```bash
    mkdir data
    cd data
    mkdir AL AZ CA # etc. for each state
    ```

2.  **Downloading the Data**

    Please refer to `datalinks.md` for detailed instructions on how to download and prepare the necessary shapefiles for each state.

## Usage

1.  Ensure your virtual environment is active (`source venv/bin/activate`).

2.  Make sure the `analyze_maps.py` script is in your main `redistricting_project` directory.

3.  Run the script from the terminal:
    ```bash
    python3 analyze_maps.py
    ```
    > **Note:** The script is currently configured to run on the Texas data. To adapt it for other states, you will need to modify the configuration variables at the top of the `analyze_maps.py` file.

## Output

The script will perform the following steps:

* Load the shapefile data.
* Run the MCMC simulation for the configured number of steps, printing progress to the terminal.
* Analyze the results to find the single most representative map from the simulation.
* Save the final map as an image file named `summary_map.png` in the project directory.

## Future Work

* **Generalize the Script:** Modify `analyze_maps.py` to accept command-line arguments for the state, number of districts, and population column, eliminating the need to edit the code for each run.
* **Automate Nationwide Analysis:** Create a master script (`run_all_states.sh`) to automatically download data and run the analysis for all 50 states sequentially.
