import time
import iec61850
import logging
from lib import libied

# Configure logging
logging.basicConfig(level=logging.INFO)

# Constants
TCP_PORT = 102


def getMeteringBCU(ieds, type):
    """
    Fetch metering data from all IEDs using a dynamically selected function 
    based on the type.

    :param ieds: A dictionary containing IED configurations.
    :param type: The type of IED (e.g., "C264dss", "SIEMENS").
    """
    datas = {}

    # Construct the function name dynamically based on the measurement type
    function_name = f"getDataMetering{type}"

    # Use getattr to fetch the correct function from libied
    try:
        get_data_func = getattr(libied, function_name)
    except AttributeError:
        logging.error(f"No function found for measurement type: {type}")
        return {"error": f"No function found for measurement type: {type}"}

    for bay, ied_info in ieds.items():
        hostname = ied_info["Ied_IP"]
        iedname = ied_info["Ied_Name"]

        connection = iec61850.IedConnection_create()

        try:
            logging.info(f"Attempting to connect to {hostname}:{TCP_PORT}")
            error = iec61850.IedConnection_connect(
                connection, hostname, TCP_PORT)

            if error == iec61850.IED_ERROR_OK:
                # Dynamically call the selected function
                data = get_data_func(connection, iedname)
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

    time.sleep(3)  # If necessary, can be made configurable

    return datas
