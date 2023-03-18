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

Packages Required:
- tkinter
- playsound
- crcmod
- pyserial

Install all dependencies:
  ``` sh
  $ pip install tkinter
  $ pip install playsound
  $ pip install crcmod
  $ pip install pyserial
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