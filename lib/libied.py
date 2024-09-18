import iec61850
import logging
logging.basicConfig(level=logging.INFO)

def getDataMeteringC264dss(connection, ied_name):
    """
    Fetch metering data from an IED using IEC 61850 protocol.
    """
    addr = [
        "rmsMMXU1.Hz.mag.f",
        "rmsMMXU1.A.phsA.cVal.mag.f",
        "rmsMMXU1.A.phsB.cVal.mag.f",
        "rmsMMXU1.A.phsC.cVal.mag.f",
        "rmsMMXU1.A.neut.cVal.mag.f",
        "rmsMMXU1.PhV.phsA.cVal.mag.f",
        "rmsMMXU1.PhV.phsB.cVal.mag.f",
        "rmsMMXU1.PhV.phsC.cVal.mag.f",
        "rmsMMXU1.PPV.phsAB.cVal.mag.f",
        "rmsMMXU1.PPV.phsBC.cVal.mag.f",
        "rmsMMXU1.PPV.phsCA.cVal.mag.f",
        "powMMXU1.TotVA.mag.f",
        "powMMXU1.TotVAr.mag.f",
        "powMMXU1.TotW.mag.f",
    ]

    dataNames = [
        "freq",
        "currPhsA",
        "currPhsB",
        "currPhsC",
        "currPhsN",
        "voltPhsA",
        "voltPhsB",
        "voltPhsC",
        "voltPhsAB",
        "voltPhsBC",
        "voltPhsCA",
        "VA", 
        "VAR",
        "W"
    ]

    if "CPL2" in ied_name or "TIE" in ied_name:
        addr = [
            "rmsMMXU1.Hz.mag.f",
            "rmsMMXU1.A.phsA.cVal.mag.f",
            "rmsMMXU1.A.phsB.cVal.mag.f",
            "rmsMMXU1.A.phsC.cVal.mag.f",
            "rmsMMXU1.PhV.phsA.cVal.mag.f",
            "rmsMMXU1.PhV.phsB.cVal.mag.f",
            "rmsMMXU1.PhV.phsC.cVal.mag.f",
        ]
        dataNames = [
            "freqTIE",
            "currPhsA",
            "currPhsB",
            "currPhsC",
            "voltPhsA",
            "voltPhsB",
            "voltPhsC",
        ]

    elif "CPL1" in ied_name:
        addr = [
            "rmsMMXU2.Hz.mag.f",
            "rmsMMXU2.A.phsA.cVal.mag.f",
            "rmsMMXU2.A.phsB.cVal.mag.f",
            "rmsMMXU2.A.phsC.cVal.mag.f",
            "rmsMMXU2.PhV.phsA.cVal.mag.f",
            "rmsMMXU2.PhV.phsB.cVal.mag.f",
            "rmsMMXU2.PhV.phsC.cVal.mag.f",
        ]
        dataNames = [
            "freqTIE",
            "currPhsA",
            "currPhsB",
            "currPhsC",
            "voltPhsA",
            "voltPhsB",
            "voltPhsC",
        ]

    dataValue = []
    
    for addr_item, data_name in zip(addr, dataNames):
        try:
            logging.info(f"Reading data for {data_name} at {ied_name}/{addr_item}")
            value, error = iec61850.IedConnection_readObject(
                connection, f"{ied_name}BCUMEASUREMENT1/{addr_item}", iec61850.IEC61850_FC_MX
            )
            
            if value is not None:
                fval = iec61850.MmsValue_toFloat(value)
                dataValue.append(fval)
                iec61850.MmsValue_delete(value)
            else:
                logging.error(f"Failed to read object {addr_item} for IED {ied_name}")
                dataValue.append(None)
        except iec61850.IEDConnectionError as e:
            logging.error(f"Error reading data {addr_item} for IED {ied_name}: {e}")
            dataValue.append(None)  # Append None to maintain order

    return dict(zip(dataNames, dataValue))