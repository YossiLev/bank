import sys
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import sys
import glob
import datetime
import pandas as pd

#from datetime import datetime

with open("/Users/yossilev/launchd_python_debug.txt", "a") as f:
    f.write(f"RUN: {datetime.datetime.now()}\n")

load_dotenv("/Users/yossilev/automation/bank/.env")

LOGIN_URL = os.getenv("LOGIN_URL")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
AID = os.getenv("AID")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")


USER_FIELD_ID = "tzId"
PASS_FIELD_ID = "tzPassword"
AID_FIELD_ID = "aidnum"
FORM_ID = "form_id_here"

file_exists = False

import time

import smtplib
from email.mime.text import MIMEText

def send_email_alert(subject, body):
    # Setup SMTP configuration (Example using Gmail)
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = os.getenv("MAIL_USER")
    sender_password = GMAIL_APP_PASSWORD

    # Create message
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = sender_email

    # Connect and send
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls() # Secure the connection
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, sender_email, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")


def wait_for_download(folder):
    while any([filename.endswith(".crdownload") for filename in os.listdir(folder)]):
        time.sleep(1) # Wait 1 second and check again
    print("Download complete!")

try:

    # Define your custom path
    download_path = os.path.join("/Users/yossilev/automation/bank", "bank_data/backup/newfiles/")
    #final_path = os.path.join("/Users/yossilev/automation/bank", "bank_data/backup/newfiles/")
    # Create the folder if it doesn't exist
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    if not file_exists:
        chrome_options = webdriver.ChromeOptions()
        prefs = {
            "download.default_directory": download_path, # Set your path here
            "download.prompt_for_download": False,       # Don't ask 'Where to save?'
            "directory_upgrade": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(options=chrome_options)

        # Navigate to the bank
        print("Welcome to Stokes!\nGoing to bank site ...", end="")
        driver.get(LOGIN_URL)

        # We wait up to 10 seconds for the username field to actually appear
        wait = WebDriverWait(driver, 20)
        user_input = wait.until(EC.presence_of_element_located((By.ID, USER_FIELD_ID)))

        print("At the bank's home page\nLogging in with user data ... ", end="")

        # Fill the data
        user_input.send_keys(USERNAME)
        
        password_input = driver.find_element(By.ID, PASS_FIELD_ID)
        password_input.send_keys(PASSWORD)

        aid_input = driver.find_element(By.ID, AID_FIELD_ID)
        aid_input.send_keys(AID)

        # Submit the form
        login_form = driver.find_element(By.CSS_SELECTOR, "form.login-form")
        login_form.submit()

        balance_element = WebDriverWait(driver, 45).until(
            EC.presence_of_element_located((By.ID, "balancesBox-accountBalance"))
        )
        print("Logged in successfully!")
        # get balance
        balance_html = balance_element.get_attribute("innerHTML")
        print(f"Balance is: {balance_element.text}")

        # Wait for the specific anchor to be clickable
        stock_link_par = wait.until(EC.element_to_be_clickable((By.ID, "top-level-nav-7")))
        #stock_link_par = wait.until(EC.element_to_be_clickable((By.XPATH, "//p[text()='שוק ההון']")))
        # This waits for any <p> tag whose title attribute contains 'שוק ההון'
        #stock_link_par = wait.until(EC.element_to_be_clickable((By.XPATH, "//p[contains(@title, 'שוק ההון')]")))
        print("found top-level-nav-7")
        stock_link_par.click()
        print("clicked top-level-nav-7, waiting for 'text = my file' sleep..")
        time.sleep(3)


        stock_link = driver.find_element(By.XPATH, "//p[text()='התיק שלי']")

        print(f"my file element is {stock_link}, clicking ...")

        stock_link.click()

        print("Go to see portfolio (wait for URL change)... ", end="")
        WebDriverWait(driver, 15).until(EC.url_changes(LOGIN_URL))
        print("URL changed, now waiting for iframe to load ...")

        time.sleep(3)

        # Find print element
        print("Looking for print element outside iframe...")
        print_select = wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'הדפסה')]"))
        )
        print(f"Found print element: {print_select} not in frame")

        # # Find the iframe element
        # iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        # print(f"Found iframe: {iframe} - switching to it ...")
        # # Switch the driver's focus to this iframe
        # driver.switch_to.frame(iframe)
        # print("Switched to iframe, now waiting for body content to load ...")

        # # NOW you can look for your Hebrew text or body content
        # # The driver is now 'trapped' inside the iframe's HTML
        # wait.until(lambda d: d.find_element(By.TAG_NAME, "body").text.strip() != "")
        # print("Body content loaded. waiting for print element to appear (sleep 3) ...")
        # time.sleep(3)
        # print("Sleep done, now looking for print element ...")
        # # Find print element
        # print_select = wait.until(
        #     EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'הדפסה')]"))
        # )
        print(f"Found print element: {print_select}, clicking ...")
        print_select.click()
        print("See protfolio\nExporting to excel")

        print(f"Sleep 3 while waiting for download menue to appear ... ", end="")
        time.sleep(3)
        print_select_excel = wait.until(
            #EC.presence_of_element_located((By.ID, "cc-combo-item-excel")))
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'ייצוא לאקסל')]")))
        print(f"Found export to excel menu")
        print_select_excel.click()
        print(f"Sleep 3 while download excel ... ", end="")
        time.sleep(3)
        wait_for_download(download_path)
        time.sleep(1)

        # Get a list of all files in your download directory
        list_of_files = glob.glob(os.path.join(download_path, '*')) 

        # Find the most recently created file
        latest_file = max(list_of_files, key=os.path.getctime)
        print(f"file downloaded as: {os.sep.join(latest_file.split(os.sep)[-3:])}")
        # Create a clean name like 'Stocks_2024-05-20.xlsx'
        today = datetime.date.today().strftime("%Y-%m-%d")
        new_name = os.path.join(download_path, f"MyStocks_{today}.xlsx")

        # Rename the file
        os.rename(latest_file, new_name)
        print(f"File renamed to: {os.sep.join(new_name.split(os.sep)[-3:])}")

    # Locate the file
    download_path = os.path.join("/Users/yossilev/automation/bank", "bank_data/backup/newfiles/")
    list_of_files = glob.glob(os.path.join(download_path, '*.xlsx'))
    for f in list_of_files:
        print(f"Found file: {os.sep.join(f.split(os.sep)[-3:])} {os.path.getctime(f)}")
    latest_file = max(list_of_files, key=os.path.getctime)
    print(f"Latest file found: {os.sep.join(latest_file.split(os.sep)[-3:])}")

    # Load the Excel file
    # If your Excel has headers in a specific row (e.g., row 3), use header=2
    df = pd.read_excel(latest_file, header=5)

    # Basic Cleaning
    # Banks often have empty rows at the top or bottom. 
    df = df.dropna(how='all')

    # Printing the Data
    print("\n\n\n\n--- Your Current Holdings ---")
    print(df.head()) # Shows the first 5 rows

    # Simple Analysis
    value_name = 'שווי בש"ח'
    asset_name = 'שם נייר'
    df[value_name] = pd.to_numeric(df[value_name], errors='coerce')
    df = df.dropna(subset=[value_name])
    total_value = df[value_name].sum()
    print(f"\n\nTotal Portfolio Value: {total_value:,.2f}")
    
    # Find your biggest holding
    biggest = df.loc[df[value_name].idxmax()]
    print(f"\n\nTop Asset: {biggest[asset_name]} at {biggest[value_name]}")

    user_choice = None
    if len(sys.argv) > 1:
        user_choice = sys.argv[1]
    else:
        print("Done! finally what do you want to do with the data?\n(M - move to main folder, D - delete, K - keep in place) -> ", end="")
        user_choice = input().strip().upper()
    if user_choice == 'M':
        main_folder = os.path.join("/Users/yossilev/automation/bank", "bank_data/backup/")
        if not os.path.exists(main_folder):
            os.makedirs(main_folder)
        new_main_path = os.path.join(main_folder, os.path.basename(new_name))
        os.rename(new_name, new_main_path)
        print(f"File moved to: {new_main_path}")
        send_email_alert(
            subject="Portfolio File saved to backup",
            body=f"The portfolio file {os.path.basename(new_name)} has been saved to backup."
        )
    elif user_choice == 'G':
        main_folder = os.path.join("/Users/yossilev/automation/bank", "bank_data/backupG/")
        if not os.path.exists(main_folder):
            os.makedirs(main_folder)
        new_main_path = os.path.join(main_folder, os.path.basename(new_name))
        os.rename(new_name, new_main_path)
        print(f"File moved to: {new_main_path}")
        send_email_alert(
            subject="Portfolio File saved to backupG",
            body=f"The portfolio file {os.path.basename(new_name)} has been saved to backupG."
        )
    elif user_choice == 'D':
        os.remove(new_name)
        send_email_alert(
            subject="Portfolio File Deleted",
            body=f"The portfolio file {os.path.basename(new_name)} has been deleted."
        )
        print("File deleted.")
    else:
        print("File kept in place.")
except Exception as outer_error:
    send_email_alert(
        subject="Failed to retrieve portfolio data",
        body=f"The get stokes script encountered an error: {outer_error}"
    )
    # This runs if the login itself failed (e.g., wrong password or timeout)
    print(f"failed: {outer_error}")

finally:
    if not file_exists:
        # Close the browser once done
        driver.quit()