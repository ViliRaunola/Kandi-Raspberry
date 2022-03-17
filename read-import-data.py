from os import read
import sys
import json
import requests
import time
import csv

def readWifiFile(file_name):

    second_half = False
    skip_next_row = False

    data_list = []

    with open(file_name, 'r') as f_wifi:
        lines = csv.reader(f_wifi)
        #Skipping header and first empty rows
        next(lines)
        next(lines)
        for line in lines:
            if skip_next_row:
                skip_next_row = False
                continue
            #After the empty row, clients are listed. Need to skip the header row so skip_next_row is set to True
            if len(line) == 0:
                second_half = True
                skip_next_row = True
                continue
            if second_half:
                data = {
                    "MAC_Address": hash(line[0]),
                    "First_Seen": line[1],
                    "Last_Seen": line[2],
                    "Signal_Strength": int(line[3]),
                    "BSSID": hash(line[5]),
                    "Probed_ESSID": line[6],
                    "Is_AP": False
                }
            else:
                data = {
                    "MAC_Address": hash(line[0]),
                    "First_Seen": line[1],
                    "Last_Seen": line[2],
                    "Signal_Strength": int(line[8]),
                    "ESSID": line[13],
                    "Is_AP": True
                }
            data_list.append(data)

    return data_list


def readBluetoothFile(file_name):

    data_list = []

    with open(file_name, 'r') as f_bluetooth:
        lines = csv.reader(f_bluetooth) 
        next(lines) #Skipping header
        for line in lines:
            data = {
                "MAC_Address": hash(line[1]),
                "Name": line[2],
                "Company": line[3],
                "RSSI_value": line[6],
                "Last_Seen": line[10]
            }
            data_list.append(data)

    return data_list



def sendDataToServer(file_name_wifi, file_name_bluetooth, url_to_save, timer):
    
    while True:
        try:
            data_list_wifi = readWifiFile(file_name_wifi)
            data_list_bluetooth = readBluetoothFile(file_name_bluetooth)
            data_list = {
                "wifi": data_list_wifi,
                "bluetooth": data_list_bluetooth,
            }
            r = requests.post(url_to_save, json=data_list)
            r = r.json()
            if r.get('success'):
                print('Data sent to server.')
            else:
                print('Sending the data failed.')
            time.sleep(timer)
        except KeyboardInterrupt:
            print('Shutting down...')
            break
        



def main(argv):

    url_to_save = 'http://localhost:1234/api/save'
    file_name_wifi = "testi-01.csv"
    file_name_bluetooth = 'raspberrypi_bt_2022-03-16_14_16_45.csv'
    timer_for_reading_sending = 5

    #TODO Lisää ohjelmien käynnistys!!!

    for arg in argv:
        if arg == "-help":
            print("Apua on tulossa")
            sys.exit(0)
        if arg == "-web":
            print("Sending to web")
            sendDataToServer(file_name_wifi, file_name_bluetooth, url_to_save, timer_for_reading_sending)


if __name__ == "__main__":
    main(sys.argv)



#############################EOF####################################