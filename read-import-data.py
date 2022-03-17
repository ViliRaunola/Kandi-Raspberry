from os import read
import sys
import json
import requests
import time


def readWifiFile(file_name):
    #Open the file for reading
    f_wifi = open(file_name, 'r')
    
    #Reading the header & first line off
    next(f_wifi)
    next(f_wifi)

    data_list = []

    #First half of the file, containing APs   
    for line in f_wifi:
        line = line.replace('\n', '').replace('\t', '')
        if line == '':
            break
        line_array = line.split(',')
        #Station MAC 0, First time seen 1, Last time seen 2, Power 3, # packets 4, BSSID 5, Probed ESSIDs 6
        data = {
            "MAC_Address": line_array[0],
            "First_Seen": line_array[1],
            "Last_Seen": line_array[2],
            "Signal_Strength": line_array[8],
            "ESSID": line_array[13],
        }
        #BSSID 0, First time seen 1, Last time seen 2, channel 3, Speed 4, Privacy 5, Cipher 6, Authentication 7, Power 8, # beacons 9, # IV 10, LAN IP 11, ID-length 12, ESSID 13, Key 14 
        data_list.append(data)
    
    #Reading the header off
    next(f_wifi)

    #Second half of the file, containing clients
    for line in f_wifi: 
        line = line.replace('\n', '').replace('\t', '')
        if line == '':
            break
        line_array = line.split(',')
        data = {
            "MAC_Address": line_array[0],
            "First_Seen": line_array[1],
            "Last_Seen": line_array[2],
            "Signal_Strength": line_array[3],
            "BSSID": line_array[5],
            "Probed_ESSID": line_array[6]
        }
        data_list.append(data)
    
    return data_list

def readBluetoothFile(file_name):
    #Open the file for reading
    f_bluetooth = open(file_name, 'r')

    #Reading the header off
    next(f_bluetooth)

    data_list = []

    #uuid 0,Address 1,Name 2,Company 3,Manufacturer 4,Type 5,RSSI 6,TX Power 7,Strongest RSSI 8,Est Range (m) 9,Last Seen 10,GPS Valid 11,Latitude,Longitude,Altitude,Speed,Strongest GPS Valid,Strongest Latitude,Strongest Longitude,Strongest Altitude,Strongest Speed

    for line in f_bluetooth:
        if line == '':
            break
        line_array = line.split(',')
        data = {
            "MAC_address": line_array[1],
            "Name": line_array[2],
            "Company": line_array[3],
            "RSSI": line_array[6],
            "Last_Seen": line_array[10]
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