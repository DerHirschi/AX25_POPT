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
"""

STR_TABLE = {
    #  GER   ENG  NL
    'OK': ('OK', 'OK', 'OK'),
    'cancel': ('Abbrechen', 'Cancel', 'Onderbreken'),
    'delete': ('Löschen', 'Delete', 'Lekker'),
    'del_all': ('Alles Löschen', 'Delete all', 'Verwijder alles'),
    'go': ('Los', 'Go', 'Gaan'),
    'close': ('Schließen', 'Close', 'Schließen'),
    'save': ('Speichern', 'Save', 'Redden'),
    'send_file': ('Datei senden', 'Send File', 'Verstuur bestand'),
    'file_1': ('Datei', 'File', 'Bestand'),
    'file_2': ('Datei:', 'File:', 'Bestand:'),
    'locator_calc': ('Locator Rechner', 'Locator Calculator', 'Lekker Locator Calculator'),
    'aprs_mon': ('APRS-Server Monitor', 'APRS-Server Monitor', 'Lekker APRS-Server Monitor'),
    'protocol': ('Protokoll:', 'Protocol:', 'Lekker Protocol:'),
    'send_if_free': ('Senden wenn Band frei für (sek.):', 'Send when band is free for (sec.):', ''),
    'size': ('Größe:', 'Size:', 'Groot:'),
    'new': ('Neu', 'New', 'Nieuw'),
    'new_conn': ('Neu Verbindung', 'New Connection', 'Nieuw Koppelingen'),
    'disconnect': ('Disconnecten', 'Disconnect', 'Loskoppelen'),
    'disconnect_all': ('ALLE disconnecten', 'Disconnect ALL', 'Loskoppelen ALLE'),
    'wx_window': ('Wetterstationen', 'Weather Stations', 'Weerstations'),
    'quit': ('Quit', 'Quit', 'Quit'),
    'connections': ('Verbindungen', 'Connections', 'Koppelingen'),
    'copy': ('Kopieren', 'Copy', 'Lekker Kopiëren'),
    'past': ('Einfügen', 'Past', 'Lekker Invoegen'),
    'past_f_file': ('Aus Datei einfügen', 'Past from File', 'Lekker'),
    'save_to_file': ('In Datei speichern', 'Save to File', 'Lekker'),
    'past_qso_f_file': ('Aus Datei einfügen', 'Past from File', 'Lekker'),
    'save_qso_to_file': ('QSO in Datei speichern', 'Save QSO to File', 'Lekker'),
    'save_mon_to_file': ('Monitor in Datei speichern', 'Save Monitor to File', 'Lekker'),
    'clean_qso_win': ('QSO/Vorschreibfenster löschen', 'Clear QSO/Prescription window', 'Lekker'),
    'clean_all_qso_win': ('Alle QSO/Vorschreibfenster löschen', 'Clear all QSO/Prescription window', 'Lekker'),
    'clean_mon_win': ('Monitor löschen', 'Clear Monitor', 'Lekker'),
    'edit': ('Bearbeiten', 'Edit', 'Lekker bewerking'),
    'statistic': ('Statistik', 'Statistics', 'Statistieken'),
    'linkholder': ('Linkhalter', 'Link holder', 'Link houder'),
    'tools': ('Tools', 'Tools', 'Lekker hulpmiddelen'),
    'station': ('Station', 'Station', 'Station'),
    'stations': ('Stationen', 'Stations', 'Stations'),
    'port': ('Port', 'Port', 'Port'),
    'channel': ('Kanal', 'Channel', 'Kanaal'),
    'beacon': ('Baken', 'Beacons', 'Bakken'),
    'settings': ('Einstellungen', 'Settings', 'Instellingen'),
    'main_page': ('Hauptseite', 'Main Page', 'Hoofdpagina'),
    'passwords': ('Passwörter', 'Passwords', 'Wachtwoord'),
    'syspassword': ('Sys-Passwort:', 'Sys-Password:', 'Sys-wachtwoord:'),
    'trys': ('Fake-Versuche:', 'Fake-Attempts:', 'Valse pogingen:'),
    'fillchars': ('Antwortlänge:', 'Response length:', 'Reactie lengte:'),
    'priv': ('Login', 'Login', 'Login'),
    'login_cmd': ('Login Kommando:', 'Login Command:', 'Login commando:'),
    'keybind': ('Tastaturbelegung', 'Keyboard layout', 'Toetsenbordindeling'),
    'about': ('Über', 'About', 'Lekker'),
    'help': ('Hilfe', 'Help', 'Hulp'),
    'number': ('Anzahl', 'Number', 'Nummer'),
    'minutes': ('Minuten', 'Minutes', 'Minuut'),
    'hours': ('Stunden', 'Hours', 'Uur'),
    'day': ('Tag', 'Day', 'Dag'),
    'month': ('Monat', 'Month', 'Maand'),
    'occup': ('Auslastung in %', 'Occupancy in %', 'Werkdruk in %'),
    'call': ('Call', 'Call', 'Call'),
    'name': ('Name', 'Name', 'Name'),
    'fwd_list': ('Forward Warteschlange', 'Forward queue', 'Voorwaartse wachtrij'),
    'start_fwd': ('FWD Start', 'FWD start', 'Start FWD'),
    'start_auto_fwd': ('AutoFWD Start', 'AutoFWD start', 'Start AutoFWD'),
    'msg_center': ('Nachrichten Center', 'Message Center', 'Message Center'),
    'qso_win_color': ('QSO Fenster Farben', 'QSO Win Color', 'QSO Win Color'),
    'text_color': ('Text Farben', 'Text Color', 'Text Color'),
    'bg_color': ('Hintergrund Farben', 'Backgrund Color', 'BG Color'),
    'mon_color': ('Monitor Farben', 'Monitor Colors', 'Monitor Colors'),
    'c_text': ('C Text', 'C Text', 'C-Text'),
    'q_text': ('Quit Text', 'Quit Text', 'Quit-Text'),
    'i_text': ('Info Text', 'Info Text', 'Info-Text'),
    'li_text': ('Lang-Info Text', 'Long-Info Text', 'Long-Info Text'),
    'news_text': ('News Text', 'News Text', 'News-Text'),
    'aprs_settings': ('APRS-Einstellungen', 'APRS-Settings', 'APRS-Settings'),
    'aprs_pn_msg': ('APRS Private Nachrichten', 'APRS Private Messages', 'APRS Private Messages'),
    'pn_msg': ('Private Nachrichten', 'Private Messages', 'Private Messages'),
    'msg': ('Nachricht', 'Message', 'Message'),
    'new_msg': ('Neue Nachricht', 'New Message', 'new Message'),
    'new_pr_mail': ('Neue PR-Mail', 'New PR-Mail', 'new PR-Mail'),
    'stat_settings': ('Station-Einstellungen', 'Station-Settings', 'Station-Settings'),
    'new_stat': ('Neue Station', 'New Station', 'nieuw station'),
    'txt_decoding': ('Umlautumwandlung', 'Text decoding', 'Text decoding'),
    'suc_save': ('Info: Station Einstellungen erfolgreich gespeichert.', 'Info: Station settings saved successfully.',
                 'alles Lekker'),
    'lob1': ('Lob: Das hast du sehr gut gemacht !!', 'Praise: You did very well!!', 'Lekker '),
    'lob2': ('Lob: Das hast du gut gemacht !!', 'Praise: You did well!!', 'Lekker '),
    'hin1': ('Hinweis: Der OK Button funktioniert noch !!', 'Note: The OK button still works !!', 'Lekker '),
    'from': ('Von', 'From', 'Lekker '),
    'to': ('An', 'To', 'Lekker '),
    'versatz': ('Versatz', 'Offset', 'compenseren'),
    'intervall': ('Intervall', 'Interval', 'Interval'),
    'active': ('Aktiviert', 'Activated', 'Ingeschakeld'),
    'text_fm_file': ('Text aus Datei', 'Text from File', 'Tekst uit bestand '),
    'beacon_settings': ('Baken-Einstellungen', 'Beacon-Settings', 'Beacon Instellingen'),
    'pipetool_settings': ('Pipe-Tool Einstellungen', 'Pipe-Tool Settings', 'Pipe-Tool Instellingen'),
    'new_pipe': ('Neue Pipe', 'New Pipe', 'Nieuwe Pipe'),
    'new_pipe_fm_connection': ('Pipe auf Verbindung', 'Pipe on Connection', 'Pipe op aansluiting'),
    'tx_file': ('TX Datei', 'TX File', 'TX-File'),
    'rx_file': ('RX Datei', 'RX File', 'RX-File'),
    'new_beacon': ('Neue Bake', 'New Beacon', 'Nieuw baken'),
    'last_packet': ('letztes Paket', 'last packet', 'laatste pakket'),
    'scrolling': ('Auto Scrollen', 'Auto scrolling', 'Lekker Auto scrolling'),
    'msg_box_mh_delete': ('MH-Liste Löschen', 'Delete MH list', 'Verwijder MH-lijst'),
    'msg_box_mh_delete_msg': ('Komplette MH-Liste löschen?', 'Delete entire MH list?', 'Volledige MH-lijst verwijderen?'),
    'msg_box_delete_data': ('Daten Löschen', 'Delete data', 'Verwijder data'),
    'msg_box_delete_data_msg': (
    'Alle Daten löschen?', 'Delete all data?', 'Alle gegevens verwijderen?'),

    'data': ('Daten', 'Data', 'Gegevens'),
    'multicast_warning': (
        'Vorsicht bei Nodenanbindungen wie TNN. Verlinkungen mehrerer Noden via Multicast kann zu Problemen führen!',
        'Be careful with node connections like TNN. Linking multiple nodes via multicast can lead to problems!',
        'Lekker probleem !'
    ),
    'user_db': (
        'User Datenbank',
        'User Database',
        'Gebruikersdatabase'
    ),

    # CLI
    'cmd_help_user_db': ('Call DB Abfrage',
                         'Get Call DB entry',
                         'Ontvang Call DB-invoer',
                         ),
    'cmd_help_set_name': ('Namen eintragen',
                          'Enter Name',
                          'naam ingevuld',
                          ),

    'cmd_help_set_qth': ('QTH eintragen',
                         'Enter QTH',
                         'QTH ingevuld',
                         ),

    'cmd_help_set_loc': ('Locator eintragen',
                         'Enter Locator',
                         'Locator ingevuld',
                         ),
    'cmd_help_set_zip': ('Postleitzahl eintragen',
                         'Enter ZIP',
                         'Postcode ingevuld',
                         ),
    'cmd_help_set_prmail': ('PR-MAIL Adresse eintragen',
                            'Enter PR-MAIL Address',
                            'PR-MAIL ingevuld',
                            ),
    'cmd_help_set_email': ('E-MAIL Adresse eintragen',
                           'Enter E-MAIL Address',
                           'E-MAIL ingevuld',
                           ),
    'cmd_help_set_http': ('HTTP eintragen',
                          'Enter HTTP',
                          'HTTP ingevuld',
                          ),

    'cli_no_user_db_ent': (' # Eintag nicht in Benutzer Datenbank vorhanden!',
                           ' # Entry not in user database!',
                           ' # Invoer niet in Lekker gebruikersdatabase!',
                           ),

    'cli_name_set': (' # Name eingetragen',
                     ' # Username is set',
                     ' # Naam ingevoerd',
                     ),

    'cli_qth_set': (' # QTH eingetragen',
                    ' # QTH is set',
                    ' # QTH ingevoerd',
                    ),
    'cli_loc_set': (' # Locator eingetragen',
                    ' # Locator is set',
                    ' # Locator ingevoerd',
                    ),
    'cli_zip_set': (' # Postleitzahl eingetragen',
                    ' # ZIP is set',
                    ' # Postcode ingevoerd',
                    ),
    'cli_prmail_set': (' # PR-Mail Adresse eingetragen',
                       ' # PR-Mail Address is set',
                       ' # PR-Mail ingevoerd',
                       ),
    'cli_email_set': (' # E-Mail Adresse eingetragen',
                      ' # E-Mail Address is set',
                      ' # E-Mail ingevoerd',
                      ),
    'cli_http_set': (' # HTTP eingetragen',
                     ' # HTTP is set',
                     ' # HTTP ingevoerd',
                     ),
    'cli_text_encoding_no_param': (' # Bitte ein ä senden. Bsp.: UM ä.\r # Derzeitige Einstellung:',
                                   ' # Please send an ä. Example: UM ä.\r # Current setting:',
                                   ' # Stuur een Lekker ä. Dus UM ä.\r # Huidige instelling:',
                                   ),
    'cli_text_encoding_error_not_found': (' # Umlaute wurden nicht erkannt !',
                                          " # Couldn't detect right text encoding",
                                          ' # Kan de juiste tekstcodering niet detecteren',
                                          ),
    'cli_text_encoding_set': (' # Umlaute/Text de/enkodierung erkannt und gesetzt auf:',
                              " # Text de/encoding detected and set to:",
                              ' # Tekstde/codering gedetecteerd en ingesteld op:',
                              ),

    'port_overview': ('Port Übersicht',
                      'Port Overview',
                      'Lekker Ports'),
    'cmd_shelp': ('Kurzhilfe',
                  'Short help',
                  'Korte hulp'),

    'time_connected': ('Connect Dauer',
                       'Connect duration',
                       'verbindingsduur'),

    'cmd_not_known': ('Dieses Kommando ist dem System nicht bekannt !',
                      'The system does not know this command !',
                      'Het systeem kent deze opdracht niet !'),

    'auto_text_encoding': ('Automatisch Umlaut Erkennung. ä als Parameter. > UM ä',
                           'Automatic detection of text encoding. ä as a parameter. > UM ä',
                           'Automatische detectie van tekstcodering. ä als parameter. > UM ä'),
    'cmd_help_lcstatus': ('Verbundene Terminalkanäle anzeigen (ausführliche Version)',
                          'Show connected terminal channels (detailed version)',
                          'Toon aangesloten terminalkanalen (gedetailleerde versie)'),
    'cli_no_wx_data': ('Keine Wetterdaten vorhanden.', 'No WX data available', 'Geen WX beschikbaar.'),
    'cli_no_data': ('Keine Daten vorhanden.', 'No data available.', 'Geen gegevens beschikbaar.'),
    'cli_no_tracer_data': ('Keine Tracerdaten vorhanden.', 'No Tracer data available', 'Geen tracergegevens beschikbaar.'),
    'cli_change_language': ('Sprache ändern.', 'Change language.', 'Taal veranderen'),
    'cli_lang_set': ('Sprache auf Deutsch geändert.',
                     'Language changed to English.',
                     'Taal veranderd naar lekker Nederlands.'),
    'cli_no_lang_param': ('Sprache nicht erkannt! Mögliche Sprachen: ',
                          'Language not recognized! Possible languages: ',
                          'Taal niet herkend! Mogelijke talen: '),

}
