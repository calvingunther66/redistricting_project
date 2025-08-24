U.S. State Redistricting Data (2020)

Here is the list of data sources for all 50 states. Due to the unreliability of direct Census Bureau links, we recommend obtaining the shapefiles from the National Historical Geographic Information System (NHGIS).

**Manual Download Instructions (via NHGIS):**
1.  **Go to the IPUMS NHGIS website:** `https://nhgis.org/`
2.  **Register for a free account and log in.** (This is required to download data from NHGIS).
3.  **Navigate to the Data Finder:** Look for a link like "Download or Revise My Data" or "GIS Files" on the main page.
4.  **Select Data Series:** In the data finder, search for "2020 P.L. 94-171 Redistricting Data" or similar. You may need to browse by "Geographic Level" and select "Voting Districts (VTDs)".
5.  **Choose Geographic Levels:** Select "Voting Districts (VTDs)" for all states you need.
6.  **Select GIS Files:** Under the "GIS Files" tab, select the "2020 P.L. 94-171 Voting Districts" shapefiles.
7.  **Review and Request Data:** Add your selections to your data cart. Review your request and submit it. NHGIS will prepare your data and send you an email with a download link.
8.  **Download and Place Files:** Once you receive the email, download the `.zip` file. Each downloaded `.zip` file from NHGIS will likely contain shapefiles for multiple states. You will need to extract the relevant state's shapefiles (e.g., `tl_2020_01_vtd20.zip` for Alabama) and move them into their corresponding state folder within your `data/` directory (e.g., `redistricting_project/data/AL/`).
9.  **Unzip the file:** Unzip the state-specific `.zip` file in its respective `data/STATE_CODE/` directory.

Note on Population Data: The official Census Bureau shapefiles often name the total population column TOTAL_POP or a similar variant. In the next phase, when we generalize the script, we will update it to look for the correct column name. For now, the main goal is to collect the data.

State | Districts | FIPS Code | Expected Filename (from Census Bureau, may vary slightly from NHGIS)
------|-----------|-----------|------------------------------------------------------------------
Alabama | 7 | 01 | tl_2020_01_vtd20.zip
Alaska | 1 | 02 | tl_2020_02_vtd20.zip
Arizona | 9 | 04 | tl_2020_04_vtd20.zip
Arkansas | 4 | 05 | tl_2020_05_vtd20.zip
California | 52 | 06 | tl_2020_06_vtd20.zip
Colorado | 8 | 08 | tl_2020_08_vtd20.zip
Connecticut | 5 | 09 | tl_2020_09_vtd20.zip
Delaware | 1 | 10 | tl_2020_10_vtd20.zip
Florida | 28 | 12 | tl_2020_12_vtd20.zip
Georgia | 14 | 13 | tl_2020_13_vtd20.zip
Hawaii | 2 | 15 | tl_2020_15_vtd20.zip
Idaho | 2 | 16 | tl_2020_16_vtd20.zip
Illinois | 17 | 17 | tl_2020_17_vtd20.zip
Indiana | 9 | 18 | tl_2020_18_vtd20.zip
Iowa | 4 | 19 | tl_2020_19_vtd20.zip
Kansas | 4 | 20 | tl_2020_20_vtd20.zip
Kentucky | 6 | 21 | tl_2020_21_vtd20.zip
Louisiana | 6 | 22 | tl_2020_22_vtd20.zip
Maine | 2 | 23 | tl_2020_23_vtd20.zip
Maryland | 8 | 24 | tl_2020_24_vtd20.zip
Massachusetts | 9 | 25 | tl_2020_25_vtd20.zip
Michigan | 13 | 26 | tl_2020_26_vtd20.zip
Minnesota | 8 | 27 | tl_2020_27_vtd20.zip
Mississippi | 4 | 28 | tl_2020_28_vtd20.zip
Missouri | 8 | 29 | tl_2020_29_vtd20.zip
Montana | 2 | 30 | tl_2020_30_vtd20.zip
Nebraska | 3 | 31 | tl_2020_31_vtd20.zip
Nevada | 4 | 32 | tl_2020_32_vtd20.zip
New Hampshire | 2 | 33 | tl_2020_33_vtd20.zip
New Jersey | 12 | 34 | tl_2020_34_vtd20.zip
New Mexico | 3 | 35 | tl_2020_35_vtd20.zip
New York | 26 | 36 | tl_2020_36_vtd20.zip
North Carolina | 14 | 37 | tl_2020_37_vtd20.zip
North Dakota | 1 | 38 | tl_2020_38_vtd20.zip
Ohio | 15 | 39 | tl_2020_39_vtd20.zip
Oklahoma | 5 | 40 | tl_2020_40_vtd20.zip
Oregon | 6 | 41 | tl_2020_41_vtd20.zip
Pennsylvania | 17 | 42 | tl_2020_42_vtd20.zip
Rhode Island | 2 | 44 | tl_2020_44_vtd20.zip
South Carolina | 7 | 45 | tl_2020_45_vtd20.zip
South Dakota | 1 | 46 | tl_2020_46_vtd20.zip
Tennessee | 9 | 47 | tl_2020_47_vtd20.zip
Texas | 38 | 48 | tl_2020_48_vtd20.zip
Utah | 4 | 49 | tl_2020_49_vtd20.zip
Vermont | 1 | 50 | tl_2020_50_vtd20.zip
Virginia | 11 | 51 | tl_2020_51_vtd20.zip
Washington | 10 | 53 | tl_2020_53_vtd20.zip
West Virginia | 2 | 54 | tl_2020_54_vtd20.zip
Wisconsin | 8 | 55 | tl_2020_55_vtd20.zip
Wyoming | 1 | 56 | tl_2020_56_vtd20.zip
