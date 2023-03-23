![Windows](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![Raspberry Pi](https://img.shields.io/badge/-RaspberryPi-C51A4A?style=for-the-badge&logo=Raspberry-Pi)

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)
# P.ython o.ther P.acket T.erminal
### AX25 Terminal (AX25_POPT)

    $$$$$$$\   $$$$$$\     $$$$$$$\ $$$$$$$$|
    $$  __$$\ $$  __$$\    $$  __$$\|__$$ __|
    $$ |  $$ |$$ /  $$ |   $$ |  $$ |  $$ |
    $$$$$$$  |$$ |  $$ |   $$$$$$$  |  $$ |
    $$  ____/ $$ |  $$ |   $$  ____/   $$ |
    $$ |      $$ |  $$ |   $$ |        $$ |
    $$ |       $$$$$$  |   $$ |        $$ |
    \__|yton   \______/ther\__|acket   \__|erminal

under development...

Tested on Python Version:

[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)

[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)

Packages Required:
- tkinter
- playsound
- crcmod
- pyserial
- matplotlib
- gtts

Install all dependencies:
  ``` sh
  $ pip install tkinter
  $ pip install playsound
  $ pip install crcmod
  $ pip install pyserial
  $ pip install matplotlib
  $ pip install gtts
  ```

Run:
  ``` sh
  $ python3 main.py
  ```

Supported AX.25 connection options:
- KISS via TCP (e.g. Direwolf)
- KISS via Serail (e.g. Linux AX.25 Device (kissattach). Not tested on TNCs or Modems yet)
- AXIP via UDP (AXIP Client)

Keybindings:
- ALT + C > New Connection
- ALT + D > Disconnect
- F1 - F10 > Channel 1 - 10
- CTRL + plus > increase Text size
- CTRL + minus > decrease Text size
- CTRL + Left > decrease Text Window
- CTRL + Right > increase Text Window

File ext in Station Profile Folder (data/usertxt/<USER CALL>):
- *.ctx > C-Text
- *.btx > Bye-Text
- *.atx > News-Text
- *.itx > Info-Text
- *.litx > Long Info-Text
- *.popt > Programm Data Files (Don't change !) 


Knowing Issues / TODO (AX25 Protocol):
- FRMR Frame decoding not implemented yet
- RNR State not implemented yet
- Issues with "Smart-Digi" / Managed DIGI Mode Connection UID

TODO: !! Lot of Testing and Debugging !!

