# NZ Post Parcel Redirector

An automated solution for redirecting NZ Post parcels using Selenium WebDriver. This script automates the process of redirecting parcels through the NZ Post website, handling the entire workflow from tracking to payment.

## Features

- Automated parcel redirection process
- CSV-based data input for multiple parcels
- Handles address selection with dropdowns
- Automated payment processing
- Fresh browser session for each parcel
- Detailed logging and error handling

## Requirements

- Python 3.7+
- Chrome browser installed
- ChromeDriver (matching your Chrome version)
- Required Python packages (install using `pip install -r requirements.txt`):
  - selenium
  - configparser

## Setup

1. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `config.ini` file with your NZ Post login credentials:
   ```ini
   [Login]
   email = your_email@example.com
   password = your_password
   ```

3. Prepare your `parcel_data.csv` file with the following columns:
   - tracking_number
   - firstname
   - lastname
   - companyname
   - buildingfloor
   - email
   - phone
   - original_address
   - new_address
   - card_number
   - card_name
   - card_expiry_month
   - card_expiry_year
   - card_cvc

## Usage

1. Ensure your CSV file is properly formatted with the required data
2. Run the script:
   ```bash
   python automation.py
   ```

The script will:
1. Load parcel data from the CSV file
2. For each tracking number:
   - Create a fresh browser session
   - Navigate to the tracking page
   - Click the redirect button
   - Sign in (if required)
   - Fill in the address form
   - Process payment
   - Close the browser session
3. Continue with the next tracking number

## Notes

- Each tracking number is processed in a fresh browser session
- The script includes appropriate wait times for page loading and form submission
- Error handling is implemented to continue processing even if one tracking number fails
- Console logging is suppressed for cleaner output

## Troubleshooting

If you encounter issues:
1. Ensure ChromeDriver matches your Chrome browser version
2. Verify your login credentials in config.ini
3. Check that your CSV data is properly formatted
4. Make sure all required fields in the CSV are filled out
5. Check the console output for specific error messages 