# appfiles/test.py
import logging
import json
from api import bcu_api

# Configure logging
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    try:
        with open('databaseBCU.json', 'r') as file:
            ieds = json.load(file)

        result = bcu_api.getMeteringBCU(ieds, type="C264dss")
        logging.info(f"Metering data received: {result}")
    except FileNotFoundError:
        logging.error("databaseBCU.json file not found.")
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing JSON: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
