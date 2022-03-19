from os import read
import sys
import json
import requests
import time
import csv
import hashlib
import pymongo
from pymongo import MongoClient
import subprocess
import os
import signal
import threading

def readWifiFile(file_name):

    second_half = False
    skip_next_row = False

    data_list = []

    with open(file_name, 'r') as f_wifi:
        lines = csv.reader(f_wifi)
        #Skipping header and first empty rows
        #! TARKKANA, välillä tiedostossa yksi rivi vähemmän alussa....
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



def sendDataToServer(file_name_wifi, file_name_bluetooth, timer, url_to_save_wifi, url_to_save_bt):
    
    wlan_airodump = input('Which wlan interface to use for airodump (monitormode)?: ')
    wlan_sparrow = input("Which wlan interface to use for sparrow (Pi's own)?: ")

    cmd_airodump = ['sudo', 'airodump-ng', '-w', '/home/pi/Desktop/recordings/testi', wlan_airodump]
    cmd_sparrow = ['sudo', 'python3', '/home/pi/sparrow-wifi/sparrowwifiagent.py', '--recordinterface', wlan_sparrow]

    try:
        print('started recording bt')
        process_sparrow = subprocess.Popen(cmd_sparrow, start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        print('started recording wifi')
        process_airodump = subprocess.Popen(cmd_airodump, start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    except:
        print('Opening subprocesses failed')
        os.killpg(os.getpgid(process_airodump.pid), signal.SIGTERM)
        os.killpg(os.getpgid(process_sparrow.pid), signal.SIGTERM)
        sys.exit(1)

    
    
    #Waiting till the recording files are created
    while True:
        if (os.path.exists(file_name_wifi) & os.path.exists(file_name_bluetooth)):
            if((os.stat(file_name_wifi).st_size > 100) & (os.stat(file_name_bluetooth).st_size > 100)):
                print("Sending to web... (ctr + c, to stop)")
                break
            else:
                print("Recording files don't have content yet")
                time.sleep(1)
        else:
            print('Recording files are not yet created')
            time.sleep(2)
    
    while True:
        try:
            data_list_wifi = readWifiFile(file_name_wifi)
            data_list_bluetooth = readBluetoothFile(file_name_bluetooth)

            r_wifi = requests.post(url_to_save_wifi, json={"wifi": data_list_wifi})
            try:
                r_wifi = r_wifi.json()
            except:
                print('No response from server')

            if r_wifi.get('success'):
                print('Server saved wifi to the database.')
            else:
                print('Saving the wifi data on server failed.')

            r_bt = requests.post(url_to_save_bt, json={"bluetooth": data_list_bluetooth})
            try: 
                r_bt = r_bt.json()
            except:
                print('No response from server')
            if r_bt.get('success'):
                print('Server saved bt to the database.')
            else:
                print('Saving the bt data on server failed.')
            
            time.sleep(timer)

        except KeyboardInterrupt:
            print('Shutting down...')
            os.killpg(os.getpgid(process_airodump.pid), signal.SIGTERM)
            os.killpg(os.getpgid(process_sparrow.pid), signal.SIGTERM)
            break
        except:
            print('Something went wrong')
            os.killpg(os.getpgid(process_airodump.pid), signal.SIGTERM)
            os.killpg(os.getpgid(process_sparrow.pid), signal.SIGTERM)
            break
        

def saveDataLocally(cluster_address, file_name_wifi, file_name_bluetooth, timer):
    client = MongoClient(cluster_address)
    db = client['kandiserveri']

    wlan_airodump = input('Which wlan interface to use for airodump (monitormode)?: ')
    wlan_sparrow = input("Which wlan interface to use for sparrow (Pi's own)?: ")

    cmd_airodump = ['sudo', 'airodump-ng', '-w', '/home/pi/Desktop/recordings/testi', wlan_airodump]
    cmd_sparrow = ['sudo', 'python3', '/home/pi/sparrow-wifi/sparrowwifiagent.py', '--recordinterface', wlan_sparrow]

    try:
        print('started recording bt')
        process_sparrow = subprocess.Popen(cmd_sparrow, start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        print('started recording wifi')
        process_airodump = subprocess.Popen(cmd_airodump, start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    except:
        print('Opening subprocesses failed')
        os.killpg(os.getpgid(process_airodump.pid), signal.SIGTERM)
        os.killpg(os.getpgid(process_sparrow.pid), signal.SIGTERM)
        sys.exit(1)
    
    #Waiting till the recording files are created
    while True:
        if (os.path.exists(file_name_wifi) & os.path.exists(file_name_bluetooth)):
            if((os.stat(file_name_wifi).st_size > 100) & (os.stat(file_name_bluetooth).st_size > 100)):
                print("Saving to local database... (ctr + c, to stop)")
                break
            else:
                print("Recording files don't have content yet")
                time.sleep(1)
        else:
            print('Recording files are not yet created')
            time.sleep(2)

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
            os.killpg(os.getpgid(process_airodump.pid), signal.SIGTERM)
            os.killpg(os.getpgid(process_sparrow.pid), signal.SIGTERM)
            break
        except:
            print('Saving to database failed')
            os.killpg(os.getpgid(process_airodump.pid), signal.SIGTERM)
            os.killpg(os.getpgid(process_sparrow.pid), signal.SIGTERM)
            exit(1)


def exportLocalDatabaseToWeb(cluster_address, url_to_save_wifi, url_to_save_bt):
    data_list_wifi = []
    data_list_bluetooth = []
    client = MongoClient(cluster_address)
    db = client['kandiserveri']

    wifi_collection= db['wifis']
    bluetooth_collection = db['bluetooths']



    try:
        data_list_wifi_mongo  = wifi_collection.find({})
        data_list_bluetooth_mongo  = bluetooth_collection.find({})
    except:
        print('Reading local database failed')
        exit(1)

    for data in data_list_wifi_mongo:
        data_wifi = {
            'MAC_Address': data['MAC_Address'],
            'First_Seen': data['First_Seen'],
            'Is_AP': data['Is_AP'],
            'Last_Seen': data['Last_Seen'],
            'Signal_Strength': data['Signal_Strength'],
        }
        if not data['Is_AP']:
            data_wifi.update({'Probed_ESSID': data['Probed_ESSID'],})
            data_wifi.update({'BSSID': data['BSSID'],})
        else:
            data_wifi.update({'ESSID': data['ESSID'],})
        data_list_wifi.append(data_wifi)
    
    for data in data_list_bluetooth_mongo:
        data_bt = {
            'MAC_Address': data['MAC_Address'],
            'Name': data['Name'],
            'Company': data['Company'],
            'RSSI': data['RSSI'],
            'Last_Seen': data['Last_Seen'],
            'First_Seen': data['First_Seen'],
        }
        data_list_bluetooth.append(data_bt)

    r_wifi = requests.post(url_to_save_wifi, json={"wifi": data_list_wifi})
    try:
        r_wifi = r_wifi.json()
    except:
        print('No response from server')

    if r_wifi.get('success'):
        print('Server saved wifi to the database.')
    else:
        print('Saving the wifi data on server failed.')

    r_bt = requests.post(url_to_save_bt, json={"bluetooth": data_list_bluetooth})
    try: 
        r_bt = r_bt.json()
    except:
        print('No response from server')
    if r_bt.get('success'):
        print('Server saved bt to the database.')
    else:
        print('Saving the bt data on server failed.')
    


def main(argv):

    file_name_wifi = "/home/pi/Desktop/recordings/testi-01.csv"                 #../Desktop/recordings/testi-01.csv
    file_name_bluetooth = '/home/pi/Desktop/recordings/Bluetooth_recording.csv'  #../Desktop/recordings/Bluetooth_recording.csv
    timer_for_reading_sending = 5
    cluster_address = 'mongodb://localhost:27017'
    url_to_save_wifi = 'https://sheltered-lake-40542.herokuapp.com/api/save/wifi'  #https://sheltered-lake-40542.herokuapp.com/api/save/wifi
    url_to_save_bt = 'https://sheltered-lake-40542.herokuapp.com/api/save/bt'  #https://sheltered-lake-40542.herokuapp.com/api/save/bt

    #try:
    for arg in argv:
        if arg == "-help":
            print("Apua on tulossa")
            sys.exit(0)
        if arg == "-web":
            sendDataToServer(file_name_wifi, file_name_bluetooth, timer_for_reading_sending, url_to_save_wifi, url_to_save_bt)
            break
        if arg == "-local":       
            saveDataLocally(cluster_address, file_name_wifi, file_name_bluetooth, timer_for_reading_sending)
            break
        if arg == "-export":
            exportLocalDatabaseToWeb(cluster_address, url_to_save_wifi, url_to_save_bt)
            break
    # except:
    #     print('Error has occured in main')


if __name__ == "__main__":
    main(sys.argv)



#############################EOF####################################