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
       
def sendDataToServer(file_name, url_to_save, timer):
    
    while True:
        try:
            data_list = readWifiFile(file_name)
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
    file_name = "testi-01.csv"
    timer_for_reading_sending = 5

    #TODO Lisää ohjelmien käynnistys!!!

    for arg in argv:
        if arg == "-help":
            print("Apua on tulossa")
            sys.exit(0)
        if arg == "-web":
            print("Sending to web")
            sendDataToServer(file_name, url_to_save, timer_for_reading_sending)


if __name__ == "__main__":
    main(sys.argv)