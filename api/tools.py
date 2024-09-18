import datetime


def getCurrTime():

    # Dapatkan waktu sekarang
    now = datetime.datetime.now() + datetime.timedelta(hours=6)

    # Format string sesuai kebutuhan, dengan bulan manual
    bulan_dict = {
        1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
        5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
        9: "September", 10: "Oktober", 11: "November", 12: "Desember"
    }

    tanggal = now.strftime("%d")
    bulan = bulan_dict[now.month]
    tahun = now.strftime("%Y")
    jam = now.strftime("%H:%M")

    return f"Tanggal : {tanggal} {bulan} {tahun}, Pukul {jam} WIB"

def format_metering_data(metering: dict, substation: str) -> str:
    """
    Formats the entire metering data into a single string.
    
    Args:
        metering (dict): The metering data fetched from the BCU.
        substation (str): Substation name
    
    Returns:
        str: The formatted metering data string.
    """
    # Header
    results = [
        f"DATA METERING {substation}",
        getCurrTime(),
        "-------------------------------------"
    ]

    # Iterate through the metering data and format each bay's information
    for bay_name, measurements in metering.items():
        curr_phs_b = round(measurements.get('currPhsB', 0.0))
        volt_phs_ca = round(measurements.get('voltPhsCA', 0.0))
        w = round(measurements.get('W', 0.0))
        var = round(measurements.get('VAR', 0.0))

        # Check if curr_phs_b is 404, indicating connection failure
        if curr_phs_b == 404:
            results.append(f"{bay_name}: gagal konek ke IED")

        # Check if bay_name includes "Kopel" or "Bustie"
        if "Kopel" in bay_name or "Bustie" in bay_name:
            # Use a different format if "Kopel" or "Bustie" is in bay_name
            results.append(f"{bay_name}: {curr_phs_b} A")
        else:
            # Default format for other bay names
            results.append(f"{bay_name}: {curr_phs_b} A, {volt_phs_ca} kV, {w} MW, {var} Mvar")

    # Join the list into a final string
    return "\n".join(results)


def format_statuscb_data(status: dict, substation: str) -> str:
    """
    Formats the entire metering data into a single string.
    
    Args:
        metering (dict): The metering data fetched from the BCU.
        substation (str): Substation name
    
    Returns:
        str: The formatted metering data string.
    """
    # Header
    results = [
        f"DATA STATUS CB {substation}",
        getCurrTime(),
        "-------------------------------------"
    ]

    # Iterate through the metering data and format each bay's information
    for bay_name, statusCB in status.items():
        # Get the HV and LV statuses
        status_cb_hv = statusCB.get('statusCBHV')
        status_cb_lv :int = statusCB.get('statusCBLV', None)  # Default to None if LV status doesn't exist
        
        # Handle connection failure
        if status_cb_hv == 404:
            results.append(f"{bay_name}: gagal konek ke IED")
            continue
        
        # Handle when LV status doesn't exist
        if status_cb_lv is None:
            if status_cb_hv == 1:
                results.append(f"{bay_name}: CB 150 kV Open")
            elif status_cb_hv == 2:
                results.append(f"{bay_name}: CB 150 kV Close")
            else:
                results.append(f"{bay_name}: CB 150 kV Invalid")
            continue
        
        # Define valid status mappings for when both HV and LV exist
        status_mapping = {
            (2, 2): "CB 150 kV Close, CB 20 kV Close",
            (1, 1): "CB 150 kV Open, CB 20 kV Open",
            (2, 1): "CB 150 kV Close, CB 20 kV Open",
            (1, 2): "CB 150 kV Open, CB 20 kV Close"
        }
        
        # Handle invalid statuses
        if status_cb_hv not in [1, 2]:
            if status_cb_lv == 1:
                results.append(f"{bay_name}: CB 150 kV Invalid, CB 20 kV Open")
            elif status_cb_lv == 2:
                results.append(f"{bay_name}: CB 150 kV Invalid, CB 20 kV Close")
            else:
                results.append(f"{bay_name}: CB 150 kV Invalid, CB 20 kV Invalid")
        elif status_cb_lv not in [1, 2]:
            if status_cb_hv == 1:
                results.append(f"{bay_name}: CB 150 kV Open, CB 20 kV Invalid")
            elif status_cb_hv == 2:
                results.append(f"{bay_name}: CB 150 kV Close, CB 20 kV Invalid")
        else:
            # Use status mapping for valid combinations
            message = status_mapping.get((status_cb_hv, status_cb_lv), "Invalid CB Status")
            results.append(f"{bay_name}: {message}")

    # Join the list into a final string
    return "\n".join(results)

def format_file_list(bay, ied, file_names):
    """
    Format the file list result into a readable string format for a specific bay and IED.
    
    Args:
        bay (str): The name or ID of the bay.
        ied (str): The name or IP of the IED.
        file_names (list or str): The result of the get_file_names function, either a list of file names or an error message.
        
    Returns:
        str: A formatted string displaying the file list or an error message.
    """
    # Header message with bay and IED info
    result_str = f"Menampilkan data untuk Bay {bay} IED {ied}\n\n"

    # If file_names is a string, it's an error message, so display it
    if isinstance(file_names, str):
        result_str += f"{file_names}\n"
    else:
        # If file_names is a list, display the files as a numbered list
        for i, file_name in enumerate(file_names, start=1):
            result_str += f"{i}. {file_name}\n"

    # Footer message
    result_str += "\nBerikut brader\n"

    return result_str

