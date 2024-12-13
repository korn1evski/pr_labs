import time
import requests
import os
from ftplib import FTP

FTP_HOST = os.environ.get('FTP_HOST', 'ftp_server')
LAB2_HOST = os.environ.get('LAB2_HOST', 'lab2_webserver')

def fetch_and_send_file_periodically(stop_flag):
    while not stop_flag['stop']:
        time.sleep(30)
        filename = "data_from_ftp.txt"
        try:
            ftp = FTP(FTP_HOST)
            ftp.login('ftpuser', 'ftppass')
            with open(filename, 'wb') as f:
                ftp.retrbinary(f'RETR {filename}', f.write)
            ftp.quit()

            files = {'file': open(filename, 'rb')}
            data = {"name": "FTP_File_Based_Book", "author": "FTP_Author", "price": "0"}
            response = requests.post(f"http://{LAB2_HOST}:5000/books", files=files, data=data)
            print("FTP file sent:", response.text)
            os.remove(filename)
        except Exception as e:
            print("Error in FTP fetch thread:", e)
