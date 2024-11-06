"""
0: 'de'
1: 'en'
2: 'nl'
3: 'fr'
4: 'fi'
5: 'pl'
6: 'pt'
7: 'it'
8: 'zh'     # Not really ;-)

Thanks to NL5VKL for the Dutch translation.
"""

STR_TABLE = {
    #  GER
    #  ENG
    #  NL
    #  FR
    #  FI
    #  PL
    #  PT
    #  IT
    #  ?
    'OK': ('OK',
           'OK',
           'OK',
           '',
           '',
           '',
           '',
           '',
           ''),

    'cancel': ('Abbrechen',
               'Cancel',
               'Onderbreken',
           '',
           '',
           '',
           '',
           '',
           ''),

    'delete': ('Löschen',
               'Delete',
               'Verwijder',
           '',
           '',
           '',
           '',
           '',
           ''),

    'delete_dx_history': ('DX-History Löschen',
                          'Delete DX-History',
                          'Verwijder DX-History',
           '',
           '',
           '',
           '',
           '',
           ''),

    'del_all': ('Alles Löschen',
                'Delete all',
                'Verwijder alles',
           '',
           '',
           '',
           '',
           '',
           ''),

    'go': ('Los',
           'Go',
           'Gaan',
           '',
           '',
           '',
           '',
           '',
           ''),

    'close': ('Schließen',
              'Close',
              'Sluiten',
           '',
           '',
           '',
           '',
           '',
           ''),

    'save': ('Speichern',
             'Save',
             'Opslaan',
           '',
           '',
           '',
           '',
           '',
           ''),

    'send_file': ('Datei senden',
                  'Send File',
                  'Verstuur bestand',
           '',
           '',
           '',
           '',
           '',
           ''),

    'file_1': ('Datei',
               'File',
               'Bestand',
           '',
           '',
           '',
           '',
           '',
           ''),

    'file_2': ('Datei:',
               'File:',
               'Bestand:',
           '',
           '',
           '',
           '',
           '',
           ''),

    'locator_calc': ('Locator Rechner',
                     'Locator Calculator',
                     'Lokatie berekenen',
           '',
           '',
           '',
           '',
           '',
           ''),

    'aprs_mon': ('APRS-Server Monitor',
                 'APRS-Server Monitor',
                 'APRS-Server Monitor',
           '',
           '',
           '',
           '',
           '',
           ''),

    'protocol': ('Protokoll:',
                 'Protocol:',
                 'Protocol:',
           '',
           '',
           '',
           '',
           '',
           ''),

    'send_if_free': ('Senden wenn Band frei für (sek.):',
                     'Send when band is free for (sec.):',
                     'Zenden wanneer band vrij is',
           '',
           '',
           '',
           '',
           '',
           ''),

    'size': ('Größe:',
             'Size:',
             'Groot:',
           '',
           '',
           '',
           '',
           '',
           ''),

    'new': ('Neu',
            'New',
            'Nieuw',
           '',
           '',
           '',
           '',
           '',
           ''),

    'new_port': ('Neuer Port',
                 'New port',
                 'Nieuwe Poort',
           '',
           '',
           '',
           '',
           '',
           ''),

    'new_conn': ('Neu Verbindung',
                 'New Connection',
                 'Nieuwe verbinding',
           '',
           '',
           '',
           '',
           '',
           ''),

    'disconnect': ('Disconnecten',
                   'Disconnect',
                   'Verbreken',
           '',
           '',
           '',
           '',
           '',
           ''),

    'disconnect_all': ('ALLE disconnecten',
                       'Disconnect ALL',
                       'Verbreek alles',
           '',
           '',
           '',
           '',
           '',
           ''),

    'disconnect_all_ask': ('Wirklich ALLE Stationen disconnecten ?',
                           'Do you want to disconnect ALL stations?',
                           'Wilt u ALLE stations verbreken?',
           '',
           '',
           '',
           '',
           '',
           ''),

    'wx_window': ('Wetterstationen',
                  'Weather Stations',
                  'Weerstations',
           '',
           '',
           '',
           '',
           '',
           ''),

    'quit': ('Quit',
             'Quit',
             'sluiten',
           '',
           '',
           '',
           '',
           '',
           ''),

    'connections': ('Verbindungen',
                    'Connections',
                    'Koppelingen',
           '',
           '',
           '',
           '',
           '',
           ''),

    'copy': ('Kopieren',
             'Copy',
             'Kopiëren',
           '',
           '',
           '',
           '',
           '',
           ''),

    'past': ('Einfügen',
             'Past',
             'Invoegen',
           '',
           '',
           '',
           '',
           '',
           ''),

    'past_f_file': ('Aus Datei einfügen',
                    'Past from File',
                    'invoegen uit bestand',
           '',
           '',
           '',
           '',
           '',
           ''),

    'save_to_file': ('In Datei speichern',
                     'Save to File',
                     'Bestand opslaan',
           '',
           '',
           '',
           '',
           '',
           ''),

    'past_qso_f_file': ('Aus Datei einfügen',
                        'Past from File',
                        'Invoegen uit bestand',
           '',
           '',
           '',
           '',
           '',
           ''),

    'save_qso_to_file': ('QSO in Datei speichern',
                         'Save QSO to File',
                         'QSO opslaan',
           '',
           '',
           '',
           '',
           '',
           ''),

    'save_mon_to_file': ('Monitor in Datei speichern',
                         'Save Monitor to File',
                         'Kopieer monitor naar bestand',
           '',
           '',
           '',
           '',
           '',
           ''),

    'clean_qso_win': ('QSO/Vorschreibfenster löschen',
                      'Clear QSO/Prescription window',
                      'QSO verwijderen',
           '',
           '',
           '',
           '',
           '',
           ''),

    'clean_all_qso_win': ('Alle QSO/Vorschreibfenster löschen',
                          'Clear all QSO/Prescription window',
                          'Alle QSO verwijderen',
           '',
           '',
           '',
           '',
           '',
           ''),

    'clean_mon_win': ('Monitor löschen',
                      'Clear Monitor',
                      'Monitor wissen',
           '',
           '',
           '',
           '',
           '',
           ''),

    'edit': ('Bearbeiten',
             'Edit',
             'Bewerken',
           '',
           '',
           '',
           '',
           '',
           ''),

    'statistic': ('Statistik',
                  'Statistics',
                  'Statistieken',
           '',
           '',
           '',
           '',
           '',
           ''),

    'linkholder': ('Linkhalter',
                   'Link holder',
                   'Link houder',
           '',
           '',
           '',
           '',
           '',
           ''),

    'tools': ('Tools',
              'Tools',
              'Hulpmiddelen',
           '',
           '',
           '',
           '',
           '',
           ''),

    'station': ('Station',
                'Station',
                'Station',
           '',
           '',
           '',
           '',
           '',
           ''),

    'stations': ('Stationen',
                 'Stations',
                 'Stations',
           '',
           '',
           '',
           '',
           '',
           ''),

    'port': ('Port',
             'Port',
             'Poort',
           '',
           '',
           '',
           '',
           '',
           ''),

    'channel': ('Kanal',
                'Channel',
                'Kanaal',
           '',
           '',
           '',
           '',
           '',
           ''),

    'beacon': ('Baken',
               'Beacons',
               'Baken',
           '',
           '',
           '',
           '',
           '',
           ''),

    'settings': ('Einstellungen',
                 'Settings',
                 'Instellingen',
           '',
           '',
           '',
           '',
           '',
           ''),

    'main_page': ('Hauptseite',
                  'Main Page',
                  'Hoofdpagina',
           '',
           '',
           '',
           '',
           '',
           ''),

    'passwords': ('Passwörter',
                  'Passwords',
                  'Wachtwoord',
           '',
           '',
           '',
           '',
           '',
           ''),

    'syspassword': ('Sys-Passwort:',
                    'Sys-Password:',
                    'Gebruiker-wachtwoord:',
           '',
           '',
           '',
           '',
           '',
           ''),

    'trys': ('Fake-Versuche:',
             'Fake-Attempts:',
             'Valse pogingen:',
           '',
           '',
           '',
           '',
           '',
           ''),

    'fillchars': ('Antwortlänge:',
                  'Response length:',
                  'Reactie lengte:',
           '',
           '',
           '',
           '',
           '',
           ''),

    'priv': ('Login',
             'Login',
             'Inlog',
           '',
           '',
           '',
           '',
           '',
           ''),

    'login_cmd': ('Login Kommando:',
                  'Login Command:',
                  'Inlog commando:',
           '',
           '',
           '',
           '',
           '',
           ''),

    'keybind': ('Tastaturbelegung',
                'Keyboard layout',
                'Toetsenbordindeling',
           '',
           '',
           '',
           '',
           '',
           ''),

    'about': ('Über',
              'About',
              'Over',
           '',
           '',
           '',
           '',
           '',
           ''),

    'help': ('Hilfe',
             'Help',
             'Hulp',
           '',
           '',
           '',
           '',
           '',
           ''),

    'number': ('Anzahl',
               'Number',
               'Nummer',
           '',
           '',
           '',
           '',
           '',
           ''),

    'minutes': ('Minuten',
                'Minutes',
                'Minuut',
           '',
           '',
           '',
           '',
           '',
           ''),

    'hours': ('Stunden',
              'Hours',
              'Uur',
           '',
           '',
           '',
           '',
           '',
           ''),

    'day': ('Tag',
            'Day',
            'Dag',
           '',
           '',
           '',
           '',
           '',
           ''),

    'month': ('Monat',
              'Month',
              'Maand',
           '',
           '',
           '',
           '',
           '',
           ''),

    'occup': ('Auslastung in %',
              'Occupancy in %',
              'Werkdruk in %',
           '',
           '',
           '',
           '',
           '',
           ''),

    'call': ('Call',
             'Call',
             'Gebruiker',
           '',
           '',
           '',
           '',
           '',
           ''),

    'name': ('Name',
             'Name',
             'Naam',
           '',
           '',
           '',
           '',
           '',
           ''),

    'fwd_list': ('Forward Warteschlange',
                 'Forward queue',
                 'Voorwaartse wachtrij',
           '',
           '',
           '',
           '',
           '',
           ''),

    'fwd_path': ('Forward Routen',
                 'Forward routes',
                 'Voorwaartse routes',
           '',
           '',
           '',
           '',
           '',
           ''),

    'start_fwd': ('FWD Start',
                  'FWD start',
                  'Start FWD',
           '',
           '',
           '',
           '',
           '',
           ''),

    'start_auto_fwd': ('AutoFWD Start',
                       'AutoFWD start',
                       'Start AutoFWD',
           '',
           '',
           '',
           '',
           '',
           ''),

    'msg_center': ('Nachrichten Center',
                   'Message Center',
                   'Berichten Center',
           '',
           '',
           '',
           '',
           '',
           ''),

    'qso_win_color': ('QSO Fenster Farben',
                      'QSO Win Color',
                      'QSO Win Kleur',
           '',
           '',
           '',
           '',
           '',
           ''),

    'text_color': ('Text Farben',
                   'Text Color',
                   'Text kleur',
           '',
           '',
           '',
           '',
           '',
           ''),

    'bg_color': ('Hintergrund Farben',
                 'Backgrund Color',
                 'BG kleur',
           '',
           '',
           '',
           '',
           '',
           ''),

    'mon_color': ('Monitor Farben',
                  'Monitor Colors',
                  'Monitor Kleur',
           '',
           '',
           '',
           '',
           '',
           ''),

    'c_text': ('C Text',
               'C Text',
               'C-Text',
           '',
           '',
           '',
           '',
           '',
           ''),

    'q_text': ('Quit Text',
               'Quit Text',
               'Quit-Text',
           '',
           '',
           '',
           '',
           '',
           ''),

    'i_text': ('Info Text',
               'Info Text',
               'Info-Text',
           '',
           '',
           '',
           '',
           '',
           ''),

    'li_text': ('Lang-Info Text',
                'Long-Info Text',
                'Lange-Info Text',
           '',
           '',
           '',
           '',
           '',
           ''),

    'news_text': ('News Text',
                  'News Text',
                  'Nieuws-Text',
           '',
           '',
           '',
           '',
           '',
           ''),

    'aprs_settings': ('APRS-Einstellungen',
                      'APRS-Settings',
                      'APRS-instellingen',
           '',
           '',
           '',
           '',
           '',
           ''),

    'aprs_pn_msg': ('APRS Private Nachrichten',
                    'APRS Private Messages',
                    'APRS Prive berichten',
           '',
           '',
           '',
           '',
           '',
           ''),

    'pn_msg': ('Private Nachrichten',
               'Private Messages',
               'Prive berichten',
           '',
           '',
           '',
           '',
           '',
           ''),

    'msg': ('Nachricht',
            'Message',
            'Bericht',
           '',
           '',
           '',
           '',
           '',
           ''),

    'new_msg': ('Neue Nachricht',
                'New Message',
                'Nieuw bericht',
           '',
           '',
           '',
           '',
           '',
           ''),

    'new_pr_mail': ('Neue PR-Mail',
                    'New PR-Mail',
                    'Nieuwe PR-Mail',
           '',
           '',
           '',
           '',
           '',
           ''),

    'stat_settings': ('Station-Einstellungen',
                      'Station-Settings',
                      'Gebruiker-instellingen',
           '',
           '',
           '',
           '',
           '',
           ''),

    'new_stat': ('Neue Station',
                 'New Station',
                 'nieuwe gebruiker',
           '',
           '',
           '',
           '',
           '',
           ''),

    'txt_decoding': ('Umlautumwandlung',
                     'Text decoding',
                     'Text decoding',
           '',
           '',
           '',
           '',
           '',
           ''),

    'suc_save': ('Info: Station Einstellungen erfolgreich gespeichert.',
                 'Info: Station setiings saved.'
                 'Info: Gebruiker instellingen goed opgelsagen.',
           '',
           '',
           '',
           '',
           '',
           ''),

    'lob1': ('Lob: Das hast du sehr gut gemacht !!',
             'Praise: You did very well!!',
             'Dat heb je zeer goed gemaakt',
           '',
           '',
           '',
           '',
           '',
           ''),

    'lob2': ('Lob: Das hast du gut gemacht !!',
             'Praise: You did well!!',
             'Dat heb je goed gemaakt ',
           '',
           '',
           '',
           '',
           '',
           ''),

    'hin1': ('Hinweis: Der OK Button funktioniert noch !!',
             'Note: The OK button still works !!',
             'De OK knop werkt nog ',
           '',
           '',
           '',
           '',
           '',
           ''),

    'from': ('Von',
             'From',
             'van ',
           '',
           '',
           '',
           '',
           '',
           ''),

    'to': ('An',
           'To',
           'Naar ',
           '',
           '',
           '',
           '',
           '',
           ''),

    'versatz': ('Versatz',
                'Offset',
                'Verzet',
           '',
           '',
           '',
           '',
           '',
           ''),

    'intervall': ('Intervall',
                  'Interval',
                  'Interval',
           '',
           '',
           '',
           '',
           '',
           ''),

    'active': ('Aktiviert',
               'Activated',
               'Ingeschakeld',
           '',
           '',
           '',
           '',
           '',
           ''),

    'text_fm_file': ('Text aus Datei',
                     'Text from File',
                     'Tekst uit bestand ',
           '',
           '',
           '',
           '',
           '',
           ''),

    'beacon_settings': ('Baken-Einstellungen',
                        'Beacon-Settings',
                        'Baken Instellingen',
           '',
           '',
           '',
           '',
           '',
           ''),

    'pipetool_settings': ('Pipe-Tool Einstellungen',
                          'Pipe-Tool Settings',
                          'Pipe-Tool Instellingen',
           '',
           '',
           '',
           '',
           '',
           ''),

    'new_pipe': ('Neue Pipe',
                 'New Pipe',
                 'Nieuwe Pipe',
           '',
           '',
           '',
           '',
           '',
           ''),

    'new_pipe_fm_connection': ('Pipe auf Verbindung',
                               'Pipe on Connection',
                               'Pipe op aansluiting',
           '',
           '',
           '',
           '',
           '',
           ''),

    'tx_file': ('TX Datei',
                'TX File',
                'TX-File',
           '',
           '',
           '',
           '',
           '',
           ''),

    'rx_file': ('RX Datei',
                'RX File',
                'RX-File',
           '',
           '',
           '',
           '',
           '',
           ''),

    'port_cfg_std_parm': ('Standard Parameter. Werden genutzt wenn nirgendwo anders (Station/Client) definiert.',
                          'Default parameters. Are used if not defined anywhere else (station/client).',
                          'Standaardparameters. Worden gebruikt als ze nergens anders zijn gedefinieerd (station/client).',
           '',
           '',
           '',
           '',
           '',
           ''),

    'port_cfg_psd_txd': ('Pseudo TX-Delay (Wartezeit zwischen TX und RX). Wird nicht als KISS Parameter am TNC gesetzt.',
                         'Pseudo TX delay (waiting time between TX and RX). Is not set as a KISS parameter on the TNC.',
                         'Pseudo TX-vertraging (wachttijd tussen TX en RX). Is op de TNC niet als KISS-parameter ingesteld.',
           '',
           '',
           '',
           '',
           '',
           ''),

    'port_cfg_pac_len': ('Paket Länge. 1 - 256',
                         'Packet length. 1-256',
                         'Pakket lengte. 1-256',
           '',
           '',
           '',
           '',
           '',
           ''),

    'port_cfg_pac_max': ('Max Paket Anzahl. 1 - 7',
                         'Max Packets. 1 - 7',
                         'Max pakketnummer. 1 - 7',
           '',
           '',
           '',
           '',
           '',
           ''),

    'port_cfg_port_name': ('Port Bezeichnung für MH und Monitor( Max: 4 ):',
                           'Port designation for MH and monitor (Max: 4):',
                           'Poortaanduiding voor MH en monitor (Max: 4):',
           '',
           '',
           '',
           '',
           '',
           ''),

    'port_cfg_not_init': ('!! Port ist nicht Initialisiert !!',
                          '!! Port is not initialized!!',
                          '!! Poort is niet geïnitialiseerd!!',
           '',
           '',
           '',
           '',
           '',
           ''),

    'new_beacon': ('Neue Bake',
                   'New Beacon',
                   'Nieuw baken',
           '',
           '',
           '',
           '',
           '',
           ''),

    'last_packet': ('letztes Paket',
                    'last packet',
                    'laatste pakket',
           '',
           '',
           '',
           '',
           '',
           ''),

    'scrolling': ('Auto Scrollen',
                  'Auto scrolling',
                  'Automatisch scrollen',
           '',
           '',
           '',
           '',
           '',
           ''),

    'msg_box_mh_delete': ('MH-Liste Löschen',
                          'Delete MH list',
                          'Verwijder MH-lijst',
           '',
           '',
           '',
           '',
           '',
           ''),

    'msg_box_mh_delete_msg': ('Komplette MH-Liste löschen?',
                              'Delete entire MH list?',
                            'Volledige MH-lijst verwijderen?',
           '',
           '',
           '',
           '',
           '',
           ''),

    'msg_box_delete_data': ('Daten Löschen',
                            'Delete data',
                            'Verwijder data',
           '',
           '',
           '',
           '',
           '',
           ''),

    'msg_box_delete_data_msg': ('Alle Daten löschen?',
                                'Delete all data?',
                                'Alle gegevens verwijderen?',
           '',
           '',
           '',
           '',
           '',
           ''),

    'data': ('Daten',
             'Data',
             'Gegevens',
           '',
           '',
           '',
           '',
           '',
           ''),

    'multicast_warning': (
        'Vorsicht bei Nodenanbindungen wie TNN. Verlinkungen mehrerer Noden via Multicast kann zu Problemen führen!',
        'Be careful with node connections like TNN. Linking multiple nodes via multicast can lead to problems!',
        'Voorzichtigmet nodeverbinding zoals TNN, verbinden meervoudige nodes via multicast kan leiden naar problemen!',
           '',
           '',
           '',
           '',
           '',
           ''),

    'user_db': (
        'User Datenbank',
        'User Database',
        'Gebruikersdatabase',
           '',
           '',
           '',
           '',
           '',
           ''),

    # CLI
    'cmd_help_bell': ('Sysop Rufen',
                      'Call Sysop',
                      'Gebruiker roepen',
           '',
           '',
           '',
           '',
           '',
           ''),

    'cmd_help_wx': ('Wetterstationen',
                    'Weather stations',
                    'Weerstations',
           '',
           '',
           '',
           '',
           '',
           ''),

    'cmd_help_user_db': ('Call DB Abfrage',
                         'Get Call DB entry',
                         'Ontvang gebruiker DB-invoer',
           '',
           '',
           '',
           '',
           '',
           ''),

    'cmd_help_set_name': ('Namen eintragen',
                          'Enter Name',
                          'naam ingevuld',
           '',
           '',
           '',
           '',
           '',
           ''),

    'cmd_help_set_qth': ('QTH eintragen',
                         'Enter QTH',
                         'Locatie ingevuld',
           '',
           '',
           '',
           '',
           '',
           ''),

    'cmd_help_set_loc': ('Locator eintragen',
                         'Enter Locator',
                         'Locator ingevuld',
           '',
           '',
           '',
           '',
           '',
           ''),

    'cmd_help_set_zip': ('Postleitzahl eintragen',
                         'Enter ZIP',
                         'Postcode ingevuld',
           '',
           '',
           '',
           '',
           '',
           ''),

    'cmd_help_set_prmail': ('PR-MAIL Adresse eintragen',
                            'Enter PR-MAIL Address',
                            'PR-MAIL ingevuld',
           '',
           '',
           '',
           '',
           '',
           ''),

    'cmd_help_set_email': ('E-MAIL Adresse eintragen',
                           'Enter E-MAIL Address',
                           'E-MAIL ingevuld',
           '',
           '',
           '',
           '',
           '',
           ''),

    'cmd_help_set_http': ('HTTP eintragen',
                          'Enter HTTP',
                          'HTTP ingevuld',
           '',
           '',
           '',
           '',
           '',
           ''),

    'cli_no_user_db_ent': (' # Eintag nicht in Benutzer Datenbank vorhanden!',
                           ' # Entry not in user database!',
                           ' # Invoer niet in gebruikersdatabase!',
           '',
           '',
           '',
           '',
           '',
           ''),

    'cli_name_set': (' # Name eingetragen',
                     ' # Username is set',
                     ' # Naam ingevoerd',
           '',
           '',
           '',
           '',
           '',
           ''),

    'cli_qth_set': (' # QTH eingetragen',
                    ' # QTH is set',
                    ' # Locatie ingevoerd',
           '',
           '',
           '',
           '',
           '',
           ''),

    'cli_loc_set': (' # Locator eingetragen',
                    ' # Locator is set',
                    ' # Locator ingevoerd',
           '',
           '',
           '',
           '',
           '',
           ''),

    'cli_zip_set': (' # Postleitzahl eingetragen',
                    ' # ZIP is set',
                    ' # Postcode ingevoerd',
           '',
           '',
           '',
           '',
           '',
           ''),

    'cli_prmail_set': (' # PR-Mail Adresse eingetragen',
                       ' # PR-Mail Address is set',
                       ' # PR-Mail ingevoerd',
           '',
           '',
           '',
           '',
           '',
           ''),

    'cli_email_set': (' # E-Mail Adresse eingetragen',
                      ' # E-Mail Address is set',
                      ' # E-Mail ingevoerd',
           '',
           '',
           '',
           '',
           '',
           ''),

    'cli_http_set': (' # HTTP eingetragen',
                     ' # HTTP is set',
                     ' # HTTP ingevoerd',
           '',
           '',
           '',
           '',
           '',
           ''),

    'cli_text_encoding_no_param': (' # Bitte ein ä senden. Bsp.: UM ä.\r # Derzeitige Einstellung:',
                                   ' # Please send an ä. Example: UM ä.\r # Current setting:',
                                   ' # Stuur een  ä. voorbeeld ä.\r # Huidige instelling:',
           '',
           '',
           '',
           '',
           '',
           ''),

    'cli_text_encoding_error_not_found': (' # Umlaute wurden nicht erkannt !',
                                          " # Couldn't detect right text encoding",
                                          ' # Kan de juiste tekstcodering niet detecteren',
           '',
           '',
           '',
           '',
           '',
           ''),

    'cli_text_encoding_set': (' # Umlaute/Text de/enkodierung erkannt und gesetzt auf:',
                              " # Text de/encoding detected and set to:",
                              ' # Tekstde/codering gedetecteerd en ingesteld op:',
           '',
           '',
           '',
           '',
           '',
           ''),

    'port_overview': ('Port Übersicht',
                      'Port Overview',
                      'Poort overzicht',
           '',
           '',
           '',
           '',
           '',
           ''),

    'cmd_shelp': ('Kurzhilfe',
                  'Short help',
                  'Korte hulp',
           '',
           '',
           '',
           '',
           '',
           ''),

    'time_connected': ('Connect Dauer',
                       'Connect duration',
                       'verbindingsduur',
           '',
           '',
           '',
           '',
           '',
           ''),

    'cmd_not_known': ('Dieses Kommando ist dem System nicht bekannt !',
                      'The system does not know this command !',
                      'Het systeem kent deze opdracht niet !',
           '',
           '',
           '',
           '',
           '',
           ''),

    'auto_text_encoding': ('Automatisch Umlaut Erkennung. ä als Parameter. > UM ä',
                           'Automatic detection of text encoding. ä as a parameter. > UM ä',
                           'Automatische detectie van tekstcodering. ä als parameter. > UM ä',
           '',
           '',
           '',
           '',
           '',
           ''),

    'cmd_help_lcstatus': ('Verbundene Terminalkanäle anzeigen (ausführliche Version)',
                          'Show connected terminal channels (detailed version)',
                          'Toon aangesloten terminalkanalen (gedetailleerde versie)',
           '',
           '',
           '',
           '',
           '',
           ''),

    'cli_no_wx_data': ('Keine Wetterdaten vorhanden.',
                       'No WX data available',
                       'Geen WX beschikbaar.',
           '',
           '',
           '',
           '',
           '',
           ''),

    'cli_no_data': ('Keine Daten vorhanden.',
                    'No data available.',
                    'Geen gegevens beschikbaar.',
           '',
           '',
           '',
           '',
           '',
           ''),

    'cli_no_tracer_data': (
        'Keine Tracerdaten vorhanden.',
        'No Tracer data available',
        'Geen tracergegevens beschikbaar.',
           '',
           '',
           '',
           '',
           '',
           ''),

    'cli_change_language': ('Sprache ändern.',
                            'Change language.',
                            'Taal veranderen',
           '',
           '',
           '',
           '',
           '',
           ''),

    'cli_lang_set': ('Sprache auf Deutsch geändert.',
                     'Language changed to English.',
                     'Taal veranderd naar Nederlands.',
           '',
           '',
           '',
           '',
           '',
           ''),

    'cli_no_lang_param': ('Sprache nicht erkannt! Mögliche Sprachen: ',
                          'Language not recognized! Possible languages: ',
                          'Taal niet herkend! Mogelijke talen: ',
           '',
           '',
           '',
           '',
           '',
           ''),

    'cmd_bell': ('Sysop wird gerufen !!',
                 'Sysop is called!!',
                 'Gebruiker wordt geroepen!!',
           '',
           '',
           '',
           '',
           '',
           ''),

    'cmd_bell_again': ('Sysop wurde bereits gerufen..',
                       'Sysop has already been called..',
                       'Gebruiker is al geroepen..',
           '',
           '',
           '',
           '',
           '',
           ''),

    'cmd_bell_gui_msg': ('verlangt nach dem Sysop !!',
                         'asks for the sysop!!',
                         'vraagt om de gebruiker!!',
           '',
           '',
           '',
           '',
           '',
           ''),

}