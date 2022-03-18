from os import read
import sys
import json
import requests
import time
import csv
import hashlib
import pymongo
from pymongo import MongoClient

def readWifiFile(file_name):

    second_half = False
    skip_next_row = False

    data_list = []

    with open(file_name, 'r') as f_wifi:
        lines = csv.reader(f_wifi)
        #Skipping header and first empty rows
        #! TARKKANA, välillä tiedostossa yksi rivi vähemmän alussa....
        #next(lines)
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
                if line[5] == ' (not associated) ':
                    BSSID = 0
                else:
                    BSSID =  hashlib.md5(line[5].encode()).hexdigest()
                data = {
                    "MAC_Address": hashlib.md5(line[0].encode()).hexdigest(),
                    "First_Seen": line[1],
                    "Last_Seen": line[2],
                    "Signal_Strength": line[3],
                    "BSSID": BSSID,
                    "Probed_ESSID": line[6],
                    "Is_AP": False
                }
            else:
                data = {
                    "MAC_Address": hashlib.md5(line[0].encode()).hexdigest(),
                    "First_Seen": line[1],
                    "Last_Seen": line[2],
                    "Signal_Strength": line[8],
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
                "MAC_Address": hashlib.md5(line[1].encode()).hexdigest(),
                "Name": line[2],
                "Company": line[3],
                "RSSI": line[6],
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
                print('Server saved the data.')
            else:
                print('Saving the data on server failed.')
            time.sleep(timer)
        except KeyboardInterrupt:
            print('Shutting down...')
            break
        

def saveDataLocally(cluster_address, file_name_wifi, file_name_bluetooth, timer):
    client = MongoClient(cluster_address)
    db = client['kandiserveri']

    wifi_collection = db['wifis']
    bluetooth_collection = db['bluetooths']

    while True:
        try:
            data_list_wifi = readWifiFile(file_name_wifi)
            data_list_bluetooth = readBluetoothFile(file_name_bluetooth)

            for data in data_list_wifi:
                wifi_collection.find_one_and_update({'MAC_Address': data.get('MAC_Address')}, {'$set': data}, upsert=True)
            
            for data in data_list_bluetooth:
                found = bluetooth_collection.find_one({'MAC_Address': data.get('MAC_Address')})
                if found != None:
                    bluetooth_collection.update_one({'MAC_Address': data.get('MAC_Address')}, {'$set': {'Last_Seen': data.get('Last_Seen'), 'RSSI': data.get('RSSI')}})
                else:
                    bluetooth_collection.insert_one({
                        "MAC_Address": data.get('MAC_Address'),
                        "Name": data.get('Name'),
                        "Company": data.get('Company'),
                        "RSSI": data.get('RSSI'),
                        "Last_Seen": data.get('Last_Seen'),
                        "First_Seen": data.get('Last_Seen'),
                    })

            
            time.sleep(timer)
        except KeyboardInterrupt:
            print('Shutting down...')
            break


def main(argv):

    url_to_save = 'http://localhost:1234/api/save'
    file_name_wifi = "testi-01.csv"
    file_name_bluetooth = 'raspberrypi_bt_2022-03-16_14_16_45.csv'
    timer_for_reading_sending = 5
    cluster_address = 'mongodb://localhost:27017'


    #TODO Lisää ohjelmien käynnistys!!!

    for arg in argv:
        if arg == "-help":
            print("Apua on tulossa")
            sys.exit(0)
        if arg == "-web":
            print("Sending to web... (ctr + c, to stop)")
            sendDataToServer(file_name_wifi, file_name_bluetooth, url_to_save, timer_for_reading_sending)
        if arg == "-local":
            print("Saving to local database... (ctr + c, to stop)")
            saveDataLocally(cluster_address, file_name_wifi, file_name_bluetooth, timer_for_reading_sending)


if __name__ == "__main__":
    main(sys.argv)



#############################EOF####################################