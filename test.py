# appfiles/test.py
import logging
import os
from api import bcu_api, tools, downIED_api

# Configure logging
logging.basicConfig(level=logging.INFO)

# Get the current directory of the script
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_FOLDER = os.path.join(CURRENT_DIR, 'tmp')
record_dir = os.path.join(CURRENT_DIR, 'record.zip')

if __name__ == '__main__':
    """try:
        with open('databaseBCU.json', 'r') as file:
            ieds = json.load(file)

        fetch = bcu_api.getStatusCB(ieds, type="C264dss")
        result = tools.format_statuscb_data(fetch, "GID BEKASI") 
        logging.info(f"Metering data received: {fetch}")
        logging.info(f"Metering data received: {result}")
    except FileNotFoundError:
        logging.error("databaseBCU.json file not found.")
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing JSON: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")"""
    
    ied_info = {'Ied_IP': '192.16.1.134', 'Ied_Dir': '/COMTRADE'}
    file_names = downIED_api.get_file_names(ied_info, 6)
    logging.info(f"Retrieved files: {file_names}")
    downloaded_files = downIED_api.get_file(ied_info, file_names, TMP_FOLDER)
    logging.info(f"Downloaded files: {downloaded_files}")
    tools.zip_tmp_files("tmp", record_dir)
