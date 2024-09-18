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
