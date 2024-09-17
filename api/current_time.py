import datetime


def getCurrTime():

    # Dapatkan waktu sekarang
    now = datetime.datetime.now()

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
