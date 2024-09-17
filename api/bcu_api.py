import time
import iec61850
import logging
from lib.libied import getDataMeteringC264dss

# Configure logging
logging.basicConfig(level=logging.INFO)

# Constants
TCP_PORT = 102

def getMeteringBCU(ieds):
    """
    Fetch metering data from all IEDs.
    """
    datas = {}

    for bay, ied_info in ieds.items():
        hostname = ied_info["Ied_IP"]
        iedname = ied_info["Ied_Name"]

        connection = iec61850.IedConnection_create()

        try:
            logging.info(f"Attempting to connect to {hostname}:{TCP_PORT}")
            error = iec61850.IedConnection_connect(connection, hostname, TCP_PORT)

            if error == iec61850.IED_ERROR_OK:
                data = getDataMeteringC264dss(connection, iedname)
                datas[bay] = data
            else:
                logging.error(f"Failed to connect to {hostname}:{TCP_PORT}")
                datas[bay] = "Connection failed"
        except iec61850.IEDConnectionError as e:
            logging.error(f"Error connecting to IED {hostname}: {e}")
            datas[bay] = f"Error: {e}"
        finally:
            iec61850.IedConnection_close(connection)
            iec61850.IedConnection_destroy(connection)

    time.sleep(1)  # If necessary, can be made configurable

    return datas