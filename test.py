# appfiles/test.py
import logging
import json
from api import bcu_api, tools

# Configure logging
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    try:
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
        logging.error(f"Unexpected error: {e}")
    
    #print(current_time.getCurrTime())

