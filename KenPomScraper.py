from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import time

import re  # Import for regular expressions

def authenticate_and_scrape_kenpom_selenium(url, username, password):
    # Set up the Chrome WebDriver
    service = Service('./chromedriver')  # Adjust path if necessary
    driver = webdriver.Chrome(service=service)

    try:
        # Open the KenPom login page
        driver.get("https://kenpom.com/")
        driver.implicitly_wait(10)

        # Locate login fields and button
        login_field = driver.find_element(By.CSS_SELECTOR, 'input[type="email"]')  # Match email field
        password_field = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')  # Match password field
        login_button = driver.find_element(By.CSS_SELECTOR, 'input[type="submit"][value="Login!"]')  # Match login button

        # Enter credentials and log in
        login_field.send_keys(username)
        password_field.send_keys(password)
        login_button.click()

        # Wait for login to complete
        driver.implicitly_wait(10)

        # Navigate to the desired page
        driver.get(url)
        driver.implicitly_wait(10)

        # Locate all <td> elements with the style "text-align:left;"
        cells = driver.find_elements(By.CSS_SELECTOR, 'td[style="text-align:left;"]')

        data = []
        for cell in cells:
            full_text = cell.text.strip()  # Get the text content of the <td>

            # Use regex to find the score pattern
            match = re.search(r'(\d+)-(\d+)', full_text)
            if match:
                score1, score2 = int(match.group(1)), int(match.group(2))  # Extract individual scores
                spread = (score1 - score2) * -1  # Calculate spread as a negative number for the winning team
                point_total = score1 + score2  # Calculate the point total
                score = f"{score1}-{score2}"  # Format the score
                team_name = full_text.split(score)[0].strip()  # Extract everything before the score
                data.append([team_name, score, spread, point_total])  # Add team name, score, spread, and point total

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
    header = ["Team Name", "Score", "Spread", "Point Total"]  # Column headers
    worksheet.update('A1', [header] + data)
    print(f"Data added to the new tab '{tab_name}' in the spreadsheet '{sheet_name}'")


if __name__ == "__main__":
    # KenPom credentials
    kp_username = "sammywatters09@gmail.com"  # Replace with your KenPom email
    kp_password = "BlueCedarFig1!"  # Replace with your KenPom password

    # KenPom URL for FanMatch data
    date = datetime.now().strftime("%Y-%m-%d")  # Use today's date dynamically
    kenpom_url = f"https://kenpom.com/fanmatch.php?d={date}"

    # Google Sheet details
    sheet_name = "KenPom Tracker"
    tab_name = date

    print("Starting script...")
    scraped_data = authenticate_and_scrape_kenpom_selenium(kenpom_url, kp_username, kp_password)
    update_google_sheet(sheet_name, tab_name, scraped_data)
    print("Script completed.")
