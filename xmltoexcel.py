import xml.etree.ElementTree as ET
import pandas as pd
import argparse
import logging

# Initialize the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the command-line arguments
parser = argparse.ArgumentParser(description="Convert XML test results to Excel and count test statuses.")
parser.add_argument("xml_file", help="Path to the XML file")
parser.add_argument("output_dir", help="Path to the directory where the Excel file will be saved")

# Parse the command-line arguments
args = parser.parse_args()

# Parse the XML file
try:
    tree = ET.parse(args.xml_file)
    root = tree.getroot()
except FileNotFoundError:
    logger.error(f"XML file not found at: {args.xml_file}")
    exit(1)
except Exception as e:
    logger.error(f"Failed to parse the XML file: {str(e)}")
    exit(1)

# Create a list to store test case information as dictionaries
test_cases = []

# Iterate through the XML and extract test case information
for testsuite in root.findall('.//testsuite'):
    for testcase in testsuite.findall('.//testcase'):
        name = testcase.get('name')
        status = testcase.get('status', 'unknown')

        # Extract the failure message if the test case failed
        failure = testcase.find('failure')
        if failure is not None:
            failure_message = failure.text.split(':')[0] if ':' in failure.text else failure.text
        else:
            failure_message = None

        test_cases.append({"name": name, "status": status, "failure_message": failure_message})

# Create a DataFrame from the test case data
df = pd.DataFrame(test_cases)

# Count the number of test cases for each status
num_passed = len(df[df['status'] == 'passed'])
num_failed = len(df[df['status'] == 'failed'])
num_skipped = len(df[df['status'] == 'skipped'])

# Define the Excel file path
excel_file_path = f"{args.output_dir}/test_cases.xlsx"

# Write the DataFrame to an Excel file
try:
    df.to_excel(excel_file_path, index=False)
    logger.info(f"Excel file saved to: {excel_file_path}")
except Exception as e:
    logger.error(f"Failed to save Excel file: {str(e)}")

# Display the counts of test statuses
logger.info(f"Number of Passed Test Cases: {num_passed}")
logger.info(f"Number of Failed Test Cases: {num_failed}")
logger.info(f"Number of Skipped Test Cases: {num_skipped}")
