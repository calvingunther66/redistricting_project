import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from gerrychain import Graph, Partition
from gerrychain.updaters import Tally, cut_edges
from gerrychain import MarkovChain
from gerrychain.proposals import recom
from gerrychain.accept import always_accept
from gerrychain.constraints import within_percent_of_ideal_population
from gerrychain.tree import recursive_tree_part
from gerrychain.metrics import polsby_popper
import numpy as np
from functools import partial
import networkx as nx
import argparse
import os

# ---\
# This is a generalized version of the redistricting analysis script.\
# It now automatically detects population columns, repairs geometries,\
# correctly reprojects data, and handles geographic islands and single-district states.\
# Example Usage:\
# python3 analyze_maps.py --state CA --districts 52\
# ---\

# --- 1. Set up Command-Line Argument Parsing ---\

parser = argparse.ArgumentParser(description="Generate and analyze congressional district maps for a given state.")
parser.add_argument("--state", required=True, type=str, help="The two-letter abbreviation for the state (e.g., 'CA', 'TX').")
parser.add_argument("--districts", required=True, type=int, help="The number of congressional districts for the state.")
parser.add_argument("--steps", default=1000, type=int, help="The number of steps to run the MCMC simulation.")
parser.add_argument("--output_dir", default=".", type=str, help="The directory to save output files.")

args = parser.parse_args()

# --- 2. Define Configuration from Arguments ---\

STATE_ABBR = args.state.upper()
NUM_DISTRICTS = args.districts
TOTAL_STEPS = args.steps
OUTPUT_DIR = args.output_dir

# Construct the path to the shapefile
SHAPEFILE_PATH = os.path.join("data", STATE_ABBR, f"{STATE_ABBR.lower()}_2020.shp")

print(f"--- Starting Analysis for {STATE_ABBR} ---")
print(f"Shapefile: {SHAPEFILE_PATH}")
print(f"Districts: {NUM_DISTRICTS}")
print(f"Simulation Steps: {TOTAL_STEPS}\n")


# --- 3. Load the Shapefile and Identify Population Column ---

print("Loading shapefile...")
try:
    df = gpd.read_file(SHAPEFILE_PATH)
except Exception as e:
    print(f"Initial geopandas read failed: {e}. Trying with pyogrio engine.")
    import pyogrio
    df = pyogrio.read_dataframe(SHAPEFILE_PATH)

# A list of potential column names for total population.
POTENTIAL_POP_COLUMNS = ["P0010001", "TOTPOP", "POP20", "POP100", "U7B001", "TOTAL_POP"]

def find_population_column(dataframe, potential_columns):
    """
    Searches the dataframe's columns for the first valid population column.
    Returns the column name if found, otherwise returns None.
    """
    for col in potential_columns:
        if col in dataframe.columns:
            print(f"Found standard population column: '{col}'")
            return col
    return None

POPULATION_COLUMN = find_population_column(df, POTENTIAL_POP_COLUMNS)

# If no standard population column is found, create a proxy from voting data
if POPULATION_COLUMN is None:
    print("\nWARNING: Could not find a standard population column.")
    print("Attempting to create a proxy population by summing vote columns...")

    vote_columns = [
        col for col in df.columns
        if col.upper().startswith(('G20', 'C20', 'R21', 'S20', 'USS', 'PRE'))
        and pd.api.types.is_numeric_dtype(df[col])
    ]

    if not vote_columns:
        available_cols_str = ", ".join(df.columns)
        raise KeyError(
            f"FATAL: Could not find a valid population column for {STATE_ABBR} and could not find "
            f"any vote data columns to create a proxy.\n"
            f"Searched for standard columns: {POTENTIAL_POP_COLUMNS}\n"
            f"Available columns are: [{available_cols_str}]"
        )

    print(f"Found {len(vote_columns)} potential vote columns to create a proxy.")
    df['PROXY_POP'] = df[vote_columns].sum(axis=1)
    POPULATION_COLUMN = 'PROXY_POP'

    total_proxy_pop = df[POPULATION_COLUMN].sum()
    if total_proxy_pop == 0:
        raise ValueError(
            f"FATAL: Proxy population for {STATE_ABBR} summed to zero. "
            f"The voting data columns may be empty or invalid.\n"
            f"Columns used for proxy calculation: {vote_columns}"
        )
    print(f"Successfully created '{POPULATION_COLUMN}' column with a total proxy population of {total_proxy_pop:,.0f}.\n")

# Ensure the final population column is numeric and has no missing values.
df[POPULATION_COLUMN] = pd.to_numeric(df[POPULATION_COLUMN], errors='coerce').fillna(0)


# --- 4. Prepare Geometries and Build the Graph ---

print("Cleaning geometries and building geographic dual graph...")

# Reproject to a projected CRS (like Web Mercator) for accurate calculations
df = df.to_crs("epsg:3857")

# Repair any invalid geometries before creating the graph
df.geometry = df.geometry.buffer(0)

# Add area and perimeter columns to the dataframe BEFORE creating the graph
df['area'] = df.geometry.area
df['perimeter'] = df.geometry.length

# Create the graph from the cleaned GeoDataFrame.
graph = Graph.from_geodataframe(df, ignore_errors=True)

# Handle disconnected "islands" by working with the largest connected component
if not nx.is_connected(graph):
    print("WARNING: Graph is not connected. Using the largest connected component.")
    largest_component = max(nx.connected_components(graph), key=len)
    graph = graph.subgraph(largest_component).copy()
    # After creating the subgraph, we need to re-index the dataframe to match
    df = df.iloc[list(graph.nodes)].copy()
    df.reset_index(drop=True, inplace=True)
    graph = nx.relabel_nodes(graph, {old_label: new_label for new_label, old_label in enumerate(graph.nodes())})


# Manually assign attributes to the graph nodes for compatibility
for node in graph.nodes:
    graph.nodes[node][POPULATION_COLUMN] = df[POPULATION_COLUMN][node]
    graph.nodes[node]["area"] = df["area"][node]
    graph.nodes[node]["perimeter"] = df["perimeter"][node]

print("Graph built successfully.")


# --- 5. Set up the GerryChain Simulation ---

print("\nConfiguring redistricting simulation (Markov Chain)...")

# Define updaters to track data during the simulation
updaters = {
    "cut_edges": cut_edges,
    "population": Tally(POPULATION_COLUMN, alias="population"),
    "area": Tally("area", alias="area"),
    "perimeter": Tally("perimeter", alias="perimeter"),
}

# Calculate the ideal population for each district
total_population = df[POPULATION_COLUMN].sum()
ideal_population = total_population / NUM_DISTRICTS

# Handle single-district states and create a more robust initial partition
if NUM_DISTRICTS == 1:
    print("State has only one district. Skipping simulation.")
    # Assign all nodes to district 0
    assignment = {node: 0 for node in graph.nodes}
    best_partition = Partition(graph, assignment, updaters)
else:
    # For multi-district states, create the initial partition using a recursive method.
    initial_partition = Partition(
        graph,
        assignment=recursive_tree_part(graph, range(NUM_DISTRICTS), ideal_population, POPULATION_COLUMN, 0.02),
        updaters=updaters
    )

    # Define the proposal method (how to change the map at each step)
    proposal = partial(recom,
                       pop_col=POPULATION_COLUMN,
                       pop_target=ideal_population,
                       epsilon=0.02, # The main simulation is still strict
                       node_repeats=1)

    # Define constraints (rules for valid maps)
    constraints = [
        within_percent_of_ideal_population(initial_partition, 0.02)
    ]

    # Create the main Markov Chain object
    chain = MarkovChain(
        proposal=proposal,
        constraints=constraints,
        accept=always_accept,
        initial_state=initial_partition,
        total_steps=TOTAL_STEPS
    )

    # --- 6. Run the Simulation ---

    print(f"\nRunning simulation for {TOTAL_STEPS} steps...")
    partitions = []
    compactness_scores = []

    polsby_popper_updater = polsby_popper

    for i, partition in enumerate(chain):
        partitions.append(partition)
        scores = polsby_popper_updater(partition)
        compactness_scores.append(np.mean(list(scores.values())))
        
        if (i + 1) % 100 == 0:
            print(f"Step {i+1}/{TOTAL_STEPS} complete.")

    print("Simulation finished.")

    # --- 7. Analyze the Results to Find the Best Map ---
    print("\nAnalyzing results to find the most typical and compact map...")

    district_assignments = {node: [] for node in graph.nodes}
    for part in partitions:
        for node, district in part.assignment.items():
            district_assignments[node].append(district)

    summary_assignment = {node: max(set(counts), key=counts.count) for node, counts in district_assignments.items()}

    min_score = float('inf')
    best_partition = None

    for i, partition in enumerate(partitions):
        deviation = 0
        for node, district_id in partition.assignment.items():
            if district_id != summary_assignment[node]:
                deviation += graph.nodes[node][POPULATION_COLUMN]
        
        normalized_deviation = deviation / total_population
        score = normalized_deviation + (1 - compactness_scores[i])

        if score < min_score:
            min_score = score
            best_partition = partition


# --- 8. Assign Final Districts and Save Results ---

# Assign the final district IDs to the GeoDataFrame, adding 1 to make them 1-indexed for the map.
df['best_cd'] = df.index.map(best_partition.assignment) + 1


# --- 9. Visualize and Save the Result ---

print("\nGenerating map visualization and data files...")

districts = df.dissolve(by='best_cd')

output_geojson = os.path.join(OUTPUT_DIR, f"{STATE_ABBR}_best_map.geojson")
districts.to_file(output_geojson, driver="GeoJSON")
print(f"Best map saved to {output_geojson}")

# --- FIX: Improved plotting section for cleaner visuals ---
fig, ax = plt.subplots(1, 1, figsize=(15, 15)) # Use a square figure for better aspect ratio
districts.plot(
    column=districts.index,
    cmap="tab20",  # A good colormap for categorical data
    ax=ax,
    categorical=True,
    edgecolor="black",
    # The legend is removed as it's impractical for states with many districts (like CA's 52)
    # and causes the visual clutter you observed.
    legend=False
)

ax.set_title(f"Most Representative & Compact Map for {STATE_ABBR}", fontsize=20, pad=20)
ax.set_axis_off()
plt.tight_layout()

output_image = os.path.join(OUTPUT_DIR, f"{STATE_ABBR}_summary_map.png")
plt.savefig(output_image, dpi=300, bbox_inches='tight') # Use bbox_inches='tight' to remove extra whitespace
print(f"Map image saved to {output_image}")

print(f"\n--- Analysis for {STATE_ABBR} complete. ---")
