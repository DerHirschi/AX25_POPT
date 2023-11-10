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
    'del_all': ('Alles Löschen', 'Delete all', 'Lekker Delete all'),
    'go': ('Los', 'Go', 'Lekker'),
    'close': ('Schließen', 'Close', 'Lekker'),
    'save': ('Speichern', 'Save', 'Lekker'),
    'send_file': ('Datei senden', 'Send File', 'Lekker'),
    'file_1': ('Datei', 'File', 'Lekker'),
    'file_2': ('Datei:', 'File:', 'Lekker'),
    'locator_calc': ('Locator Rechner', 'Locator Calculator', 'Lekker Locator Calculator'),
    'aprs_mon': ('APRS-Server Monitor', 'APRS-Server Monitor', 'Lekker APRS-Server Monitor'),
    'protocol': ('Protokoll:', 'Protocol:', 'Lekker Protocol:'),
    'send_if_free': ('Senden wenn Band frei für (sek.):', 'Send when band is free for (sec.):', ''),
    'size': ('Größe:', 'Size:', 'Lekker groot:'),
    'new': ('Neu', 'New', 'Lekker Nieuw'),
    'disconnect': ('Disconnect', 'Disconnect', 'Lekker'),
    'wx_window': ('Wetterstationen', 'Weather Stations', 'Lekker WX-Stations'),
    'quit': ('Quit', 'Quit', 'niet Lekker'),
    'connections': ('Verbindungen', 'Connections', 'Lekker'),
    'copy': ('Kopieren', 'Copy', 'Lekker Kopiëren'),
    'past': ('Einfügen', 'Past', 'Lekker Invoegen'),
    'past_f_file': ('Aus Datei einfügen', 'Past from File', 'Lekker'),
    'save_to_file': ('QSO in Datei speichern', 'Save QSO to File', 'Lekker'),
    'save_mon_to_file': ('Monitor in Datei speichern', 'Save Monitor to File', 'Lekker'),
    'clean_qso_win': ('QSO/Vorschreibfenster löschen', 'Clear QSO/Prescription window', 'Lekker'),
    'clean_mon_win': ('Monitor löschen', 'Clear Monitor', 'Lekker'),
    'bw_plot_enable': ('Plot (!frisst RAM auf!)', 'Plot (!eating up Memory!', 'Plot (!eating up Memory!'),
    'edit': ('Bearbeiten', 'Edit', 'Lekker bewerking'),
    'statistic': ('Statistik', 'Statistics', 'Lekker statistic'),
    'linkholder': ('Linkhalter', 'Link holder', 'Lekker'),
    'tools': ('Tools', 'Tools', 'Lekker hulpmiddelen'),
    'station': ('Station', 'Station', 'Lekker'),
    'stations': ('Stationen', 'Stations', 'Lekker'),
    'port': ('Port', 'Port', 'Lekker Port'),
    'channel': ('Kanal', 'Channel', 'Lekker Kanaal'),
    'beacon': ('Baken', 'Beacons', 'Lekker Bakken'),
    'settings': ('Einstellungen', 'Settings', 'Lekker Ideeën'),
    'main_page': ('Hauptseite', 'Main Page', 'Lekker hoofdpagina'),
    'passwords': ('Passwörter', 'Passwords', 'Lekker wachtwoord'),
    'syspassword': ('Sys-Passwort:', 'Sys-Password:', 'Lekker Sys-wachtwoord:'),
    'trys': ('Fake-Versuche:', 'Fake-Attempts:', 'Valse pogingen:'),
    'fillchars': ('Antwortlänge:', 'Response length:', 'Reactie lengte:'),
    'priv': ('Login', 'Login', 'Lekker Login'),
    'login_cmd': ('Login Kommando:', 'Login Command:', 'Login commando:'),
    'keybind': ('Tastaturbelegung', 'Keyboard layout', 'Lekker toetsenbordindeling'),
    'about': ('Über', 'About', 'Lekker'),
    'help': ('Hilfe', 'Help', 'Lekker Hulp'),
    'minutes': ('Minuten', 'Minutes', 'Lekker Minuut'),
    'hours': ('Stunden', 'Hours', 'Lekker Uur'),
    'day': ('Tag', 'Day', 'Lekker Dag'),
    'month': ('Monat', 'Month', 'Maand'),
    'occup': ('Auslastung in %', 'Occupancy in %', 'Lekker in %'),
    'call': ('Call', 'Call', 'Lekker Call'),
    'name': ('Name', 'Name', 'Lekker Name'),
    'fwd_list': ('Forward Warteschlange', 'Forward queue', 'Lekker Voorwaartse wachtrij'),
    'start_fwd': ('FWD Start', 'FWD start', 'Start Lekker FWD'),
    'msg_center': ('Nachrichten Center', 'Message Center', 'Lekker Message Center'),
    'qso_win_color': ('QSO Fenster Farben', 'QSO Win Color', 'Lekker QSO Win Color'),
    'text_color': ('Text Farben', 'Text Color', 'Lekker Text Color'),
    'bg_color': ('Hintergrund Farben', 'Backgrund Color', 'Lekker BG Color'),
    'mon_color': ('Monitor Farben', 'Monitor Colors', 'Lekker Monitor Colors'),
    'c_text': ('C Text', 'C Text', 'Lekker C-Text'),
    'q_text': ('Quit Text', 'Quit Text', 'Lekker Quit-Text'),
    'i_text': ('Info Text', 'Info Text', 'Lekker Info-Text'),
    'li_text': ('Lang-Info Text', 'Long-Info Text', 'Lekker Long-Info Text'),
    'news_text': ('News Text', 'News Text', 'Lekker News-Text'),
    'aprs_settings': ('APRS-Einstellungen', 'APRS-Settings', 'Lekker APRS-Settings'),
    'aprs_pn_msg': ('APRS Private Nachrichten', 'APRS Private Messages', 'Lekker APRS Private Messages'),
    'pn_msg': ('Private Nachrichten', 'Private Messages', 'Lekker Private Messages'),
    'msg': ('Nachricht', 'Message', 'Lekker Message'),
    'new_msg': ('Neue Nachricht', 'New Message', 'Lekker new Message'),
    'stat_settings': ('Station-Einstellungen', 'Station-Settings', 'Lekker Station-Settings'),
    'new_stat': ('Neue Station', 'New Station', 'Lekker nieuw station'),
    'txt_decoding': ('Umlautumwandlung', 'Text decoding', 'Lekker Text decoding'),
    'suc_save': ('Info: Station Einstellungen erfolgreich gespeichert.', 'Info: Station settings saved successfully.',
                 'alles Lekker'),
    'lob1': ('Lob: Das hast du sehr gut gemacht !!', 'Praise: You did very well!!', 'Lekker '),
    'lob2': ('Lob: Das hast du gut gemacht !!', 'Praise: You did well!!', 'Lekker '),
    'hin1': ('Hinweis: Der OK Button funktioniert noch !!', 'Note: The OK button still works !!', 'Lekker '),
    'from': ('Von', 'From', 'Lekker '),
    'to': ('An', 'To', 'Lekker '),
    'versatz': ('Versatz', 'Offset', 'Lekker compenseren'),
    'intervall': ('Intervall', 'Interval', 'Lekker Intervall'),
    'active': ('Aktiviert', 'Activated', 'Lekker An'),
    'text_fm_file': ('Text aus Datei', 'Text from File', 'Lekker '),
    'beacon_settings': ('Baken-Einstellungen', 'Beacon-Settings', 'Lekker '),
    'pipetool_settings': ('Pipe-Tool Einstellungen', 'Pipe-Tool Settings', 'Lekker Pipe-Tool'),
    'new_pipe': ('Neue Pipe', 'New Pipe', 'Lekker New Pipe'),
    'new_pipe_fm_connection': ('Pipe auf Verbindung', 'Pipe on Connection', 'Lekker Pipe'),
    'tx_file': ('TX Datei', 'TX File', 'Lekker TX-File'),
    'rx_file': ('RX Datei', 'RX File', 'Lekker RX-File'),
    'new_beacon': ('Neue Bake', 'New Beacon', 'Lekker Nieuw baken'),
    'last_packet': ('letztes Paket', 'Last Seen', 'Lekker'),
    'scrolling': ('Auto Scrollen', 'Auto scrolling', 'Lekker Auto scrolling'),
    'multicast_warning': (
        'Vorsicht bei Nodenanbindungen wie TNN. Verlinkungen mehrerer Noden via Multicast kann zu Problemen führen!',
        'Be careful with node connections like TNN. Linking multiple nodes via multicast can lead to problems!',
        'Lekker probleem !'
    ),
    'user_db': (
        'User Datenbank',
        'User Database',
        'Lekker Gebruikersdatabase'
    ),

    # CLI
    'cmd_help_user_db': ('Call DB Abfrage',
                         'Get Call DB entry',
                         'Ontvang Lekker Call DB-invoer',
                         ),
    'cmd_help_set_name': ('Namen eintragen',
                          'Enter Name',
                          'Leeker naam ingevuld',
                          ),

    'cmd_help_set_qth': ('QTH eintragen',
                         'Enter QTH',
                         'Leeker QTH ingevuld',
                         ),

    'cmd_help_set_loc': ('Locator eintragen',
                         'Enter Locator',
                         'Leeker Locator ingevuld',
                         ),
    'cmd_help_set_zip': ('Postleitzahl eintragen',
                         'Enter ZIP',
                         'Leeker Postcode ingevuld',
                         ),
    'cmd_help_set_prmail': ('PR-MAIL Adresse eintragen',
                            'Enter PR-MAIL Address',
                            'Leeker PR-MAIL ingevuld',
                            ),
    'cmd_help_set_email': ('E-MAIL Adresse eintragen',
                           'Enter E-MAIL Address',
                           'Leeker E-MAIL ingevuld',
                           ),
    'cmd_help_set_http': ('HTTP eintragen',
                          'Enter HTTP',
                          'Leeker HTTP ingevuld',
                          ),

    'cli_no_user_db_ent': (' # Eintag nicht in Benutzer Datenbank vorhanden!',
                           ' # Entry not in user database!',
                           ' # Invoer niet in Lekker gebruikersdatabase!',
                           ),

    'cli_name_set': (' # Name eingetragen',
                     ' # Username is set',
                     ' # Lekker Naam ingevoerd',
                     ),

    'cli_qth_set': (' # QTH eingetragen',
                    ' # QTH is set',
                    ' # Lekker QTH ingevoerd',
                    ),
    'cli_loc_set': (' # Locator eingetragen',
                    ' # Locator is set',
                    ' # Lekker Locator ingevoerd',
                    ),
    'cli_zip_set': (' # Postleitzahl eingetragen',
                    ' # ZIP is set',
                    ' # Lekker Postcode ingevoerd',
                    ),
    'cli_prmail_set': (' # PR-Mail Adresse eingetragen',
                       ' # PR-Mail Address is set',
                       ' # Lekker PR-Mail ingevoerd',
                       ),
    'cli_email_set': (' # E-Mail Adresse eingetragen',
                      ' # E-Mail Address is set',
                      ' # Lekker E-Mail ingevoerd',
                      ),
    'cli_http_set': (' # HTTP eingetragen',
                     ' # HTTP is set',
                     ' # Lekker HTTP ingevoerd',
                     ),
    'cli_text_encoding_no_param': (' # Bitte ein ä senden. Bsp.: UM ä.\r # Derzeitige Einstellung:',
                                   ' # Please send an ä. Example: UM ä.\r # Current setting:',
                                   ' # Stuur een Lekker ä. Dus UM ä.\r # Huidige lekker instelling:',
                                   ),
    'cli_text_encoding_error_not_found': (' # Umlaute wurden nicht erkannt !',
                                          " # Couldn't detect right text encoding",
                                          ' # Kan de juiste lekker tekstcodering niet detecteren',
                                          ),
    'cli_text_encoding_set': (' # Umlaute/Text de/enkodierung erkannt und gesetzt auf:',
                              " # Text de/encoding detected and set to:",
                              ' # Lekker Tekstde/codering gedetecteerd en ingesteld op:',
                              ),

    'port_overview': ('Port Übersicht',
                      'Port Overview',
                      'Lekker Ports'),
    'cmd_shelp': ('Kurzhilfe',
                  'Short help',
                  'Lekker Korte hulp'),

    'time_connected': ('Connect Dauer',
                       'Connect duration',
                       'Lekker verbindingsduur'),

    'cmd_not_known': ('Dieses Kommando ist dem System nicht bekannt !',
                      'The system does not know this command !',
                      'Het systeem kent deze lekker opdracht niet !'),

    'auto_text_encoding': ('Automatisch Umlaut Erkennung. ä als Parameter. > UM ä',
                           'Automatic detection of text encoding. ä as a parameter. > UM ä',
                           'Automatische detectie van lekker tekstcodering. ä als parameter. > UM ä'),
    'cmd_help_lcstatus': ('Verbundene Terminalkanäle anzeigen (ausführliche Version)',
                          'Show connected terminal channels (detailed version)',
                          'Toon lekker aangesloten terminalkanalen (gedetailleerde versie)'),
    'cli_no_wx_data': ('Keine Wetterdaten vorhanden.', 'No WX data available', 'Geen lekker WX beschikbaar.'),
    'cli_no_data': ('Keine Daten vorhanden.', 'No data available.', 'Geen gegevens beschikbaar.'),
    'cli_no_tracer_data': ('Keine Tracerdaten vorhanden.', 'No Tracer data available', 'Geen tracergegevens beschikbaar.'),
    'cli_change_language': ('Sprache ändern.', 'Change language.', 'Lekker taal veranderen'),
    'cli_lang_set': ('Sprache auf Deutsch geändert.',
                     'Language changed to English.',
                     'Taal veranderd naar lekker Nederlands.'),
    'cli_no_lang_param': ('Sprache nicht erkannt! Mögliche Sprachen: ',
                          'Language not recognized! Possible languages: ',
                          'Taal niet herkend! Mogelijke talen: '),

}
