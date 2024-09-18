import iec61850
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Constants
TCP_PORT = 102

def get_file_names(ied_info, max_files):
    """
    Fetch a list of file names from an IED (Intelligent Electronic Device) using IEC 61850 protocol.
    
    Args:
        ied_info (dict): Dictionary containing the IED information with keys 'Ied_IP' and 'Ied_Dir'.
        max_files (int): Maximum number of file names to return.
        
    Returns:
        list or str: A list of file names from the IED's directory, up to the number specified by max_files.
                     Returns "Failed to connect" if connection fails, or "No files available" if no files are found.
    """
    # Extract IED IP and directory from the dictionary
    ied_ip = ied_info.get('Ied_IP')
    ied_dir = ied_info.get('Ied_Dir')

    if not ied_ip or not ied_dir:
        logging.error("Invalid IED info provided. 'Ied_IP' or 'Ied_Dir' is missing.")
        return []

    # Initialize IEC 61850 connection
    con = iec61850.IedConnection_create()

    try:
        # Attempt to connect to the IED
        logging.info(f"Connecting to IED at {ied_ip}...")
        error = iec61850.IedConnection_connect(con, ied_ip, TCP_PORT)
        if error != iec61850.IED_ERROR_OK:
            logging.error(f"Failed to connect to IED: {ied_ip}. Error code: {error}")
            return "Failed to connect"

        # Get the file directory from the IED
        logging.info(f"Fetching file directory from: {ied_dir}")
        root_dir = iec61850.IedConnection_getFileDirectory(con, ied_dir)
        if not root_dir:
            logging.warning(f"No directory entries found at {ied_dir}.")
            return "No files available"

        # Prepare to collect file names
        file_names = []
        entry = iec61850.LinkedList_getNext(root_dir[0])

        # Collect file names, up to max_files
        while entry and len(file_names) < max_files:
            file_name = iec61850.FileDirectoryEntry_getFileName(iec61850.toFileDirectoryEntry(entry.data))
            logging.info(f"Found file: {file_name}")
            file_names.append(file_name)
            entry = iec61850.LinkedList_getNext(entry)

        # If no files are found, return "No files available"
        if not file_names:
            return "No files available"

        return file_names

    except Exception as e:
        logging.error(f"An exception occurred: {str(e)}")
        return "Failed to connect"

    finally:
        # Ensure that the connection is closed and cleaned up
        iec61850.IedConnection_close(con)
        iec61850.IedConnection_destroy(con)
        logging.info("Connection closed.")