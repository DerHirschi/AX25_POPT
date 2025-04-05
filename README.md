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

## Overview
**PoPT** is a modern terminal program for AX.25 Packet Radio.
It supports versatile connections such as KISS over TCP/Serial and AXIP over UDP.
Currently under development, tested on Python 3.6 and 3.8, it runs on Windows, Linux, and 
Raspberry Pi.

### Requirements
- Python 3.6 or 3.8 (other versions such as 3.11 see below)
- Supported Platforms: Windows, Linux, Raspberry Pi
- 
## Installation
Install all dependencies:
``` sh
$ sudo apt install python3-tk
$ sudo apt install python3-pil python3-pil.imagetk
$ sudo apt install python3-matplotlib
$ pip install -r requirements.txt
```

Install all dependencies for Python 3.11 (Thanks to Lars):
``` sh
$ sudo apt install python3-matplotlib python3-tk python3-crcmod python3-gtts python3-pip python3-networkx python3-minimal
$ pip install --break-system-packages playsound pyserial aprslib
```

**notice:** If problems with playsound on Debian OS:
``` sh
$ sudo apt install python3-gst-1.0
```

## Run
``` sh
$ python3 PoPT.py
```

## Functions

#### Supported AX.25 connection options:
- KISS via TCP (e.g. Direwolf)
- KISS via Serail (e.g. Linux AX.25 Device (kissattach). Not tested on TNCs or Modems yet)
- AXIP via UDP (AXIP Client)
- AX25KERNEL (Linux AX.25 Device)
- TNC-EMU-TCP-SERVER (Pseudo TNC-Emulator Device to connect e.g. DOS-BOX)
- TNC-EMU-TCP-CLIENT (Pseudo TNC-Emulator Device to connect e.g. Amiberry (AMIGA-Emulator))

#### Tools / Functions / Buildins
- APRS
  - Weather data evaluation
  - Beacon Tracer
  - Private Message System
  - APRS-Server Monitor
  - APRS Decoder for Monitor
- Dual Port (for two TNC's on same Frequency e.g. a SDR on a different Antenna)
- RX-Echo (Packet echoing to another Port/Device)
- PMS/BBS (S&F cable) (BIN-Mail cable (compressed Mails))
- UserDB
  - Priv Tool for Baycom login procedure
- Comprehensive statistics for data traffic and AX-25network/BBS-network structures
- NetRom decoder
- Filetransfer
  - YAPP
  - AutoBin
  - Bin
  - Textmode

#### QTH Locator Functions:
- Author: 4X5DM
- Source: https://github.com/4x1md/qth_locator_functions
- License location: doc-other/qth_locator_functions-master/LICENSE

#### Supported languages:
- German
- English
- Dutch  (Thanks to Patrick for the Dutch translation)
- French (Thanks to ClaudeMa)

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


## Community & Support
- **Forum:** [Further Information](http://forum.packetradio-salzwedel.de/index.php?board/10-popt/)
- **Telegram:** [PoPT Support](https://t.me/poptsupport)
```    
    8b   d8 888b. d88b .d88b.    db  Yb        dP  Sysop: Manuel
    8YbmdP8 8   8 " dP YPwww.   dPYb  Yb  db  dP  QTH: Salzwedel - JO52NU
    8  "  8 8   8  dP      d8  dPwwYb  YbdPYbdP  BBS: MD2BBS.#SAW.SAA.DEU.EU
    8     8 888P' d888 `Y88P' dP    Yb  YP  YP  QRV: 27.235 MHz / LoRa 868
                                               Web: packetradio-salzwedel.de
    PR-Mail:  MD2SAW@MD2BBS.#SAW.SAA.DEU.EU
    E-Mail:   cb0saw@e-mail.de
    Terminal: MD2SAW via CB0SAW
    CB0SAW Teamspeak3-/I-Net-/HF-Gateway/I-Gate AXIP: cb0saw-ddnss.de U 8093
```    

## Contribute
PoPT is under active development. 
Feedback, bug reports, and contributions are welcome! 
Check it out on [GitHub](https://github.com/DerHirschi/AX25_POPT).