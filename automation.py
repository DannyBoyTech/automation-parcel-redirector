import time
import configparser
import csv
import random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

# Load login credentials from config file
config = configparser.ConfigParser()
config.read('config.ini')

email = config['Login']['email']
password = config['Login']['password']

def load_parcel_data(csv_file):
    """Load parcel data from CSV file"""
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        return list(reader)

def enter_address_with_dropdown(driver, field_id, address):
    """Enter address and select from dropdown"""
    print(f"Entering address: {address}")
    field = driver.find_element(By.ID, field_id)
    field.clear()
    field.send_keys(address)
    time.sleep(2)  # Wait for dropdown to appear
    
    # Press down arrow to select first item
    field.send_keys(Keys.ARROW_DOWN)
    time.sleep(1)
    # Press Enter to confirm selection
    field.send_keys(Keys.RETURN)
    time.sleep(1)

def wait_for_iframe_and_switch(driver, wait, timeout=20):
    """Wait for iframe to be present and switch to it"""
    print("Waiting for payment form iframe...")
    
    # Wait until there's at least one iframe present
    iframes = wait.until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "iframe"))
    )
    
    # Try each iframe until we find the one with the payment form
    for iframe in iframes:
        try:
            driver.switch_to.frame(iframe)
            # Try to find a payment form element to confirm we're in the right iframe
            if driver.find_elements(By.ID, '36864120') or driver.find_elements(By.NAME, 'CardNumber'):
                print("Successfully switched to payment form iframe")
                return True
            driver.switch_to.default_content()
        except:
            driver.switch_to.default_content()
            continue
    
    return False

def fill_payment_form(driver, wait, card_data):
    """Fill in the payment form with credit card details"""
    print("Filling payment form...")
    
    # Wait for iframe and switch to it
    if not wait_for_iframe_and_switch(driver, wait):
        raise Exception("Could not find payment form iframe")
    
    try:
        # Fill in card number
        print("Entering card number...")
        card_number_field = wait.until(
            EC.presence_of_element_located((By.ID, '36864120'))
        )
        card_number_field.send_keys(card_data['card_number'])
        
        # Fill in card holder name
        print("Entering cardholder name...")
        name_field = driver.find_element(By.ID, '36864121')
        name_field.send_keys(card_data['card_name'])
        
        # Select expiry month
        print("Selecting expiry month...")
        month_select = Select(driver.find_element(By.ID, 'DateExpiry_1'))
        month_select.select_by_value(card_data['card_expiry_month'])
        
        # Select expiry year
        print("Selecting expiry year...")
        year_select = Select(driver.find_element(By.ID, 'DateExpiry_2'))
        year_select.select_by_value(card_data['card_expiry_year'])
        
        # Fill in CVC
        print("Entering CVC...")
        cvc_field = driver.find_element(By.ID, '36864125')
        cvc_field.send_keys(card_data['card_cvc'])
        
        # Click Submit button
        print("Clicking submit button...")
        submit_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and contains(@class, 'DpsPxPayOK')]"))
        )
        submit_button.click()
        
    finally:
        # Switch back to default content
        driver.switch_to.default_content()

def process_tracking_number(driver, wait, tracking_data, is_first_tracking=False):
    """Process a single tracking number"""
    print(f"\nProcessing tracking number: {tracking_data['tracking_number']}")
    
    # Navigate to the tracking page
    print("Navigating to tracking page...")
    driver.get(f"https://www.nzpost.co.nz/tools/tracking?trackid={tracking_data['tracking_number']}")
    
    # Wait for and click the redirect button
    print("Looking for redirect button...")
    redirect_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(@class, 'MuiButton-label') and text()='Redirect my parcel']]"))
    )
    redirect_button.click()
    
    # Only perform sign-in for the first tracking number
    if is_first_tracking:
        # Wait for and click the Sign in button in the dialog
        print("Clicking Sign in button in dialog...")
        sign_in_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(@class, 'MuiButton-label') and text()='Sign in']]"))
        )
        sign_in_button.click()
        
        # Wait for and fill in login form
        print("Filling in login form...")
        email_field = wait.until(EC.presence_of_element_located((By.ID, 'username')))
        email_field.send_keys(email)
        
        password_field = driver.find_element(By.ID, 'password')
        password_field.send_keys(password)
        
        # Click Continue button
        print("Clicking Continue button...")
        continue_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and contains(@class, 'ce869b6b0')]"))
        )
        continue_button.click()
    
    # Wait for the address form to load
    print("Waiting for address form...")
    wait.until(EC.presence_of_element_located((By.ID, 'delivery-address-rdr-field')))
    
    # Fill in the form fields
    print("Filling in form fields...")
    fields = {
        'firstname': tracking_data['firstname'],
        'lastname': tracking_data['lastname'],
        'companyname': tracking_data['companyname'],
        'buildingfloor': tracking_data['buildingfloor'],
        'email': tracking_data['email'],
        'phone': tracking_data['phone']
    }
    
    for field_name, value in fields.items():
        if value:  # Only fill in non-empty values
            field = driver.find_element(By.NAME, field_name)
            field.send_keys(value)
    
    # Fill in addresses with dropdown selection
    print("Entering original delivery address...")
    enter_address_with_dropdown(driver, 'delivery-address-rdr-field', tracking_data['original_address'])
    
    print("Entering new delivery address...")
    enter_address_with_dropdown(driver, 'new-delivery-address-field', tracking_data['new_address'])
    
    time.sleep(2)
    
    # Check the terms and conditions checkboxes
    print("Checking terms and conditions...")
    checkboxes = wait.until(
        EC.presence_of_all_elements_located((By.XPATH, "//input[@type='checkbox']"))
    )
    for checkbox in checkboxes:
        checkbox.click()
    
    # Click Proceed to payment button
    print("Clicking Proceed to payment button...")
    payment_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(@class, 'MuiButton-label') and text()='Proceed to payment']]"))
    )
    payment_button.click()
    
    time.sleep(3)
    
    # Fill in payment form
    print("Handling payment form...")
    fill_payment_form(driver, wait, tracking_data)
    
    # Wait for payment processing and return to tracking page
    print("Waiting for payment processing...")
    time.sleep(10)

def main():
    # Load parcel data from CSV
    print("Loading parcel data from CSV...")
    tracking_data_list = load_parcel_data('parcel_data.csv')
    
    # Process each tracking number
    for tracking_data in tracking_data_list:
        # Set up Chrome options for each new session
        chrome_options = Options()
        chrome_options.add_argument('--log-level=3')  # Suppress console logging
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Suppress USB device logging

        # Create a new WebDriver instance for each tracking number
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 20)  # Increase wait time to 20 seconds for elements

        try:
            # Process the tracking number with a fresh session
            process_tracking_number(driver, wait, tracking_data, is_first_tracking=True)
            print(f"Successfully processed tracking number: {tracking_data['tracking_number']}")
        except Exception as e:
            print(f"Error processing tracking number {tracking_data['tracking_number']}: {e}")
        finally:
            # Always close the browser after processing each tracking number
            driver.quit()
            print("Browser session closed.")
            
    print("All tracking numbers processed.")

if __name__ == "__main__":
    main()

