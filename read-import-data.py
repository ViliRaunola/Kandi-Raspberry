import sys
import json
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler



def sendDataToServer(file_name, url_to_save):
    
    #Open the file for reading
    f_wifi = open(file_name, 'r')
    
    #Reading the header line
    next(f_wifi)

    #macAddr 0,vendor 1,SSID 2,Security 3,Privacy 4,Channel 5,Frequency 6,Signal Strength 7,Strongest Signal Strength 8,Bandwidth 9,Last Seen 10,First Seen 11,GPS Valid,Latitude,Longitude,Altitude,Speed,Strongest GPS Valid,Strongest Latitude,Strongest Longitude,Strongest Altitude,Strongest Speed

    #Saving information from listening file to an object called data
    for line in f_wifi:
        line_array = line.split(',')
        data = {
            "MAC_Address": line_array[0],
            "Vendor": line_array[1],
            "SSID": line_array[2],
            "Channel": line_array[5],
            "Freaquency": line_array[6],
            "Signal_Strength": line_array[7],
            "Last_Seen": line_array[10],
            "First_Seen": line_array[11],
        }
    
    r = requests.post(url_to_save, json=data)
        



def main(argv):

    url_to_save = 'http://localhost:1234/api/save'
    file_name = "raspberrypi_wifi_2022-03-16_14_16_45.csv"


    for arg in argv:
        if arg == "-help":
            print("Apua on tulossa")
            sys.exit(0)
        if arg == "-web":
            print("Sending to web")
            sendDataToServer(file_name, url_to_save)


if __name__ == "__main__":
    main(sys.argv)