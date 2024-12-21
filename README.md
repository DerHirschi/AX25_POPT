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


Install all dependencies:
``` sh
$ sudo apt install python3-tk
$ sudo apt install python3-pil python3-pil.imagetk
$ sudo apt install python3-matplotlib
$ pip install -r requirements.txt
```

If problems with playsound on Debian OS:
``` sh
$ sudo apt install python3-gst-1.0
```

Run:
``` sh
$ python3 PoPT.py
```

Install all dependencies for Python 3.11 (Thanks to Lars):
``` sh
$ sudo apt install python3-matplotlib python3-tk python3-crcmod python3-gtts python3-pip python3-networkx python3-minimal
$ pip install --break-system-packages playsound pyserial aprslib
```

#### Supported AX.25 connection options:
- KISS via TCP (e.g. Direwolf)
- KISS via Serail (e.g. Linux AX.25 Device (kissattach). Not tested on TNCs or Modems yet)
- AXIP via UDP (AXIP Client)

#### Keybindings:
- ESC > New Connection
- ALT + C > New Connection
- ALT + D > Disconnect
- F1 - F10 > Channel 1 - 10
- F12 > Monitor Mode
- CTRL + plus > increase Text size
- CTRL + minus > decrease Text size
- SHIFT+F1 – SHIFT+F12 > F-Text (Macro Text)


#### File ext in Station Profile Folder (data/usertxt/<USER CALL>):
- *.ctx > C-Text
- *.btx > Bye-Text
- *.atx > News-Text
- *.itx > Info-Text
- *.litx > Long Info-Text
- *.popt > Programm Data Files (Don't change !) 


#### QTH Locator Functions:
- Author: 4X5DM
- Source: https://github.com/4x1md/qth_locator_functions
- License location: doc-other/qth_locator_functions-master/LICENSE

#### Supported languages:
- German
- English
- Dutch (Thanks to Patrick for the Dutch translation)




[Further Information](http://forum.packetradio-salzwedel.de/index.php?board/10-popt/)

[Telegram Group](https://t.me/poptsupport)
