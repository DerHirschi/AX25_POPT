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

File ext in Station Profile Folder (data/usertxt/<USER CALL>):
- *.ctx > C-Text
- *.btx > Bye-Text
- *.itx > Info-Text
- *.popt > Programm Data Files (Don't change !) 


Knowing Issues / TODO (AX25 Protocol):
- FRMR Frame decoding not implemented yet
- RNR State not implemented yet
- Issues with "Smart-Digi" / Managed DIGI Mode Connection UID
- ! Getting Decoding ERROR on some Frames. ( repeated on same Frame so received Frame seems OK)
  - Examples captured from LOG:
  b"\x14\x92\x98\x867\xbc\x0e\x9f&\xdb\xdd\x99\x17\x06']\x16\xady\x07 \xf1\xee\xa8"
  '1492988637bc0e9f26dbdd991706275d16ad790720f1eea8'