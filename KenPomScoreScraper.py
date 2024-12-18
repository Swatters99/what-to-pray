from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup  # Import BeautifulSoup for parsing
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import re  # Import for regular expressions
import time


def authenticate_and_scrape_kenpom_selenium(base_url, username, password, target_date):
    # Set up the Chrome WebDriver
    service = Service('./chromedriver')  # Adjust path if necessary
    driver = webdriver.Chrome(service=service)

    try:
        # Log in to KenPom
        driver.get("https://kenpom.com/")
        driver.implicitly_wait(10)

        # Input credentials and log in
        driver.find_element(By.CSS_SELECTOR, 'input[type="email"]').send_keys(username)
        driver.find_element(By.CSS_SELECTOR, 'input[type="password"]').send_keys(password)
        driver.find_element(By.CSS_SELECTOR, 'input[type="submit"][value="Login!"]').click()
        driver.implicitly_wait(10)

        # Navigate to the target date page
        target_url = f"{base_url}?d={target_date}"
        driver.get(target_url)
        driver.implicitly_wait(10)

        # Locate the data cells
        data_cells = driver.find_elements(By.CSS_SELECTOR, 'td[style="text-align:left;"]')

        data = []
        for cell in data_cells:
            cell_html = cell.get_attribute('innerHTML')
            soup = BeautifulSoup(cell_html, 'html.parser')

            try:
                # Extract rankings
                rankings = [span.text.strip() for span in soup.find_all('span', class_='seed-gray')]
                rank1 = rankings[0] if len(rankings) > 0 else None
                rank2 = rankings[1] if len(rankings) > 1 else None

                # Extract team names
                team_links = soup.find_all("a", href=re.compile(r"team\.php\?team="))
                team1 = team_links[0].get_text(strip=True) if len(team_links) > 0 else None
                team2 = team_links[1].get_text(strip=True) if len(team_links) > 1 else None

                # Extract scores
                scores_text = soup.get_text(separator=" ", strip=True)
                # Regex to specifically target scores after team names
                scores_match = re.findall(rf'{team1}\s(\d+),.*?{team2}\s(\d+)', scores_text)
                if scores_match:
                    score1, score2 = map(int, scores_match[0])
                else:
                    score1, score2 = None, None

                # Calculate spread and total points
                spread = score1 - score2 if score1 is not None and score2 is not None else None
                total_points = score1 + score2 if score1 is not None and score2 is not None else None

                # Append game data
                game_data = [rank1, team1, score1, rank2, team2, score2, spread, total_points]
                data.append(game_data)
            except Exception as e:
                print(f"Skipping row due to parsing error: {e}")

        print(f"Scraped {len(data)} rows of data.")
        return data

    finally:
        driver.quit()

def update_google_sheet(sheet_name, tab_name, data):
    if not data:
        print("No data to update in Google Sheet.")
        return

    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(credentials)

    # Open the existing spreadsheet
    print(f"Opening spreadsheet: {sheet_name}")
    sheet = client.open(sheet_name)

    # Create a new tab with the specified name
    print(f"Creating new tab: {tab_name}")
    try:
        worksheet = sheet.add_worksheet(title=tab_name, rows="100", cols="20")
    except Exception as e:
        print(f"Error creating new tab: {e}")
        return

    # Populate data in the new tab
    print(f"Updating tab with data...")
    header = ["Seed 1", "Team 1", "Score 1", "Seed 2", "Team 2", "Score 2", "Spread", "Total Points", "MVP", "MVP Stats"]
    worksheet.update('A1', [header] + data)
    print(f"Data added to the new tab '{tab_name}' in the spreadsheet '{sheet_name}'")


if __name__ == "__main__":
    # KenPom credentials
    kp_username = "sammywatters09@gmail.com"  # Replace with your KenPom email
    kp_password = "BlueCedarFig1!"  # Replace with your KenPom password

    # Base URL for KenPom
    base_url = "https://kenpom.com/fanmatch.php"

    # Prompt user for date
    target_date = input("Enter a date (YYYY-MM-DD) or press Enter for yesterday: ")
    if not target_date:
        target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    # Google Sheet details
    sheet_name = "BetAnalyzer"
    tab_name = target_date

    print("Starting script...")
    scraped_data = authenticate_and_scrape_kenpom_selenium(base_url, kp_username, kp_password, target_date)
    update_google_sheet(sheet_name, tab_name, scraped_data)
    print("Script completed.")
