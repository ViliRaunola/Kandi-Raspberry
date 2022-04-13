# Kandi-Raspberry

Kandidaatin työssäni kehitetty ohjelma, mikä käynnistää WLAN ja Bluetooth laitteiden havainnoinnin Raspberry Pi:llä. 
Havainnointi tehdään sparrow-wifi ja airodump-ng ohjelmistoja käyttäen.
Tallennuksessa saatavan datan voi tallentaa lokaaliin tai netissä olevaan tietokantaan.
Lokaalin tietokannan voi myös lähettää nettiin, jossa tiedot päivittyvät.
Tarkemmat ohjeet Rasperryn konfiguroimiseen löytyvät kandidaatin työstäni.

Komennot, joilla aloittaa kuuntelu
```
python3 read-import-data.py -web
```
tai
```
python3 read-import-data.py -local
```

Komento, jolla lähettää lokaalin tietokannan tiedot netissä olevaan tietokantaan
```
python3 read-import-data.py -export
```
