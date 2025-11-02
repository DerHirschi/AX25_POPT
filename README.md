![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

![Windows](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![Raspberry Pi](https://img.shields.io/badge/-RaspberryPi-C51A4A?style=for-the-badge&logo=Raspberry-Pi)
![MacOS](https://shields.io/badge/MacOS--9cf?logo=Apple&style=for-the-badge)

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
**PoPT** is a modern, multi-platform terminal program for AX.25 Packet Radio.
It supports versatile connections such as KISS over TCP/Serial, AXIP over UDP and Linux AX.25 Devices.
Currently under development, tested on Python 3.11, it runs on Windows, Linux, MacOS, and 
Raspberry Pi.

### Requirements
- Python 3.6 or higher (other versions such as 3.11 see below)
- Supported Platforms: Windows, Linux, Raspberry Pi, MacOS

## Install on Linux (including Raspberry Pi)
#### Option 1: 
Using Install Script:
``` sh
$ wget -O install_popt.sh https://raw.githubusercontent.com/DerHirschi/AX25_POPT/dev/doc/Scripts/install_popt.sh
$ chmod +x install_popt.sh
$ ./install_popt.sh
```
#### Option 2: Manual Installation
Install all dependencies:
``` sh
$ sudo apt install python3-tk
$ sudo apt install python3-pil python3-pil.imagetk
$ sudo apt install python3-matplotlib
$ cd AX25_POPT
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

**notice:** If problems with playsound on Debian OS:
``` sh
$ sudo apt install python3-gst-1.0
```

## Run
``` sh
$ python PoPT.py
```


## Install on MacOS (homebrew required):
``` sh
$ brew install python@3.12
$ brew install python-tk@3.12
$ brew install python-matplotlib
$ cd AX25_POPT
$ python3.12 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ python PoPT.py
```

#### Leave Environment:
``` sh
$ deactivate
```

#### To Start PoPT in Environment:
``` sh
$ cd AX25_POPT
$ source venv/bin/activate
$ python PoPT.py
```

## Optional: Install awthemes

To enhance the visual appearance of PoPT, you can optionally install awthemes. Follow these steps:

1. Download the awthemes-10.4.0 package from:
   https://sourceforge.net/projects/tcl-awthemes/

2. Extract the contents of awthemes-10.4.0.zip into the data/ folder of your PoPT installation.

Note: Ensure the extracted files are placed directly in the data/ directory to be recognized by PoPT.

## Functions

#### Supported AX.25 connection options:
- KISS via TCP (e.g. Direwolf)
- KISS via Serial (e.g. TNC, Linux AX.25 Device (kissattach))
- AXIP via UDP
- AX25KERNEL (Linux AX.25 Device) (root rights needed)
- TNC-EMU-TCP-SERVER (Pseudo TNC-Emulator Device to connect e.g. DOS-BOX (TFPCX).)
- TNC-EMU-TCP-CLIENT (Pseudo TNC-Emulator Device to connect e.g. Amiberry (AMIGA-Emulator) (AmigaTNC))

#### Tools / Functions / Buildins
- APRS
  - Weather data evaluation
  - Beacon Tracer
  - Private Message System
  - APRS Monitor
  - APRS Decoder for Monitor
- Dual Port (for two TNC's on same Frequency e.g. a SDR on a different Antenna)
- RX-Echo (Packet echoing to another Port/Device)
- Environment variablen replacement for:
  - Beacon
  - Scheduled Auto PR-Mail
  - C-Text, Info-Text, ...
  - Additional Vars from:
    - 1-wire Sensors 
- PMS/BBS
  - S&F capable
  - BIN-Mail capable (compressed Mails (lzhuf))
  - Mail import
  - Remote Commands / CLI
  - Generates a network diagram of the forward routes 
  - Scheduled Auto Mail e.g.: Routingmails
    - Optional env-var replacement (e.g.: $uptime) 
- UserDB
  - Priv Tool for Baycom login procedure
- Comprehensive statistics for data traffic and AX-25network/BBS-network structures
- NetRom decoder
- Node/Digi Functions (No NetRom Routing)
- MCast Server (Multicast Server for AXIP)
- Remote Commands / CLI
- GPIO Functions (capable switch GPIO's on PI and other GPIO-Devices) (root rights needed)
- 1-Wirer Temperatur Sensors (Sensor data can be embedded in C-Text/I-Text/Beacon)
- Pipe-Tool (Certain traffic or connections can be redirected to a file)
- Filetransfer
  - YAPP
  - AutoBin
  - Bin
  - Textmode
  - Auto RNR-Mode (File transfer is paused by RNR state when other radio traffic is detected)
- Local Converse-Mode

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
- **X:** [@AX25_PoPT](https://x.com/AX25_PoPT)
```    
    8b   d8 888b. d88b .d88b.    db  Yb        dP  Sysop: Manuel
    8YbmdP8 8   8 " dP YPwww.   dPYb  Yb  db  dP  QTH: Salzwedel - JO52NU
    8  "  8 8   8  dP      d8  dPwwYb  YbdPYbdP  BBS: MD2BBS.#SAW.SAA.DEU.EU
    8     8 888P' d888 `Y88P' dP    Yb  YP  YP  QRV: 27.235 MHz / LoRa 868
                                               Web: packetradio-salzwedel.de
    PR-Mail:  MD2SAW@MD2BBS.#SAW.SAA.DEU.EU
    E-Mail:   cb0saw@e-mail.de
    Terminal: MD2SAW via CB0SAW
    CB0SAW Teamspeak3-/I-Net-/HF-Gateway/I-Gate AXIP: cb0saw.ddnss.de U 8093
```    

## Contribute
PoPT is under active development. 
Feedback, bug reports, and contributions are welcome! 
Check it out on [GitHub](https://github.com/DerHirschi/AX25_POPT).