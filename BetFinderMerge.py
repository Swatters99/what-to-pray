
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

def fetch_kenpom_data(sheet_name, tab_name):
    """Fetch data from KenPom Tracker."""
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(credentials)

    # Open the KenPom Tracker spreadsheet and the specified tab
    print(f"Fetching data from '{sheet_name}', tab '{tab_name}'...")
    sheet = client.open(sheet_name)
    worksheet = sheet.worksheet(tab_name)

    # Convert the data to a Pandas DataFrame
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    print(f"Fetched {len(df)} rows of data.")
    return df

def match_and_update_kenpom_data(kenpom_df, betfinder_sheet_name, betfinder_tab_name):
    """Match and update KenPom data in BetFinder based on teams."""
    # Authenticate with Google Sheets
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(credentials)

    # Open the BetFinder spreadsheet
    print(f"Opening BetFinder spreadsheet: '{betfinder_sheet_name}'")
    sheet = client.open(betfinder_sheet_name)

    # Access the specified tab
    try:
        worksheet = sheet.worksheet(betfinder_tab_name)
        print(f"Found tab '{betfinder_tab_name}'.")
    except gspread.exceptions.WorksheetNotFound:
        raise ValueError(f"Tab '{betfinder_tab_name}' not found in '{betfinder_sheet_name}'.")

    # Fetch all data from the BetFinder tab
    print("Fetching existing data from BetFinder...")
    existing_data = worksheet.get_all_values()
    headers = existing_data[0]
    betfinder_df = pd.DataFrame(existing_data[1:], columns=headers)

    # Ensure relevant columns exist
    if 'home_team' not in betfinder_df.columns or 'away_team' not in betfinder_df.columns:
        raise ValueError("Missing 'home_team' or 'away_team' columns in BetFinder sheet.")

    # Create a large matrix to hold all updates
    updates_matrix = [row[:] for row in existing_data]  # Copy the existing data

    # Expand updates_matrix rows if needed
    required_rows = len(betfinder_df) + 1
    while len(updates_matrix) < required_rows:
        updates_matrix.append([""] * len(updates_matrix[0]))

    # Expand updates_matrix columns if needed
    required_columns = 16 + len(kenpom_df.columns)  # Column P onward
    for row in updates_matrix:
        while len(row) < required_columns:
            row.append("")

    # Add column headers from KenPom Tracker to updates_matrix
    kenpom_headers = ["Team Name"] + list(kenpom_df.columns[1:])  # Include "Team Name"
    for i, header in enumerate(kenpom_headers):
        updates_matrix[0][15 + i] = header  # 15 = Column P - 1 (0-based indexing)

    # Iterate through KenPom data and match rows
    for _, row in kenpom_df.iterrows():
        team_name = row['Team Name']
        matching_rows = betfinder_df[
            betfinder_df['home_team'].str.contains(team_name, na=False, case=False) |
            betfinder_df['away_team'].str.contains(team_name, na=False, case=False)
        ]

        for match_index in matching_rows.index:
            # Determine the starting column (P corresponds to column index 16)
            start_column = 16  # Column P
            row_index = match_index + 1  # Adjust for 1-based indexing
            data_values = row.values.tolist()  # Include "Team Name"

            # Update the corresponding cells in the matrix
            for i, value in enumerate(data_values):
                updates_matrix[row_index][start_column + i - 1] = value

    # Perform a single batch update
    print(f"Performing batch update for {len(updates_matrix) - 1} rows...")
    worksheet.update(updates_matrix)
    print("Data successfully matched and batch updated.")


if __name__ == "__main__":
    # Google Sheet details
    kenpom_sheet_name = "KenPom Tracker"
    kenpom_tab_name = "2024-12-12"  # Replace dynamically with today's date if needed
    betfinder_sheet_name = "BetFinder"
    betfinder_tab_name = "2024-12-12"

    # Step 1: Fetch data from KenPom Tracker
    kenpom_data = fetch_kenpom_data(kenpom_sheet_name, kenpom_tab_name)

    # Step 2: Match and update KenPom data in BetFinder
    match_and_update_kenpom_data(kenpom_data, betfinder_sheet_name, betfinder_tab_name)
