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
9: '?'

Thanks to NL1NOD(Patrick) for the Dutch translations.
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
    #  ?
    'default_ctext': (
        # GER
        ('\n'
       '-= Hallo $destName, =-\n' 
       '-= willkommen bei $ownCall ($distance km), =-\n'
       '-= auf Terminal-Kanal $channel <> Port $portNr. =-\n'
       '-= Das ist Connect Nr. $connNr. =-\n'
       '-= $ver - Max-Frame: $parmMaxFrame - Pac-Len: $parmPacLen =-\n'
       '\n'
       ' # Letzer Login am: $lastConnDate um: $lastConnTime\n'
       '\n'),
        # ENG
        ('\n'
       '-= Hello $destName, =-\n' 
       '-= welcome to $ownCall ($distance km), =-\n'
       '-= on Terminal-Channel $channel <> Port $portNr. =-\n'
       "-= That's your connect No. $connNr. =-\n"
       '-= $ver - Max-Frame: $parmMaxFrame - Pac-Len: $parmPacLen =-\n'
       '\n'
       ' # Last Login at: $lastConnDate um: $lastConnTime\n'
       '\n'),
        # NL
        ('\n'
       '-= Hallo $destName, =-\n' 
       '-= willkommen bei $ownCall ($distance km), =-\n'
       '-= auf Terminal-Kanal $channel <> Port $portNr. =-\n'
       '-= Das ist Connect Nr. $connNr. =-\n'
       '-= $ver - Max-Frame: $parmMaxFrame - Pac-Len: $parmPacLen =-\n'
       '\n'
       ' # Letzer Login am: $lastConnDate um: $lastConnTime\n'
       '\n'),
        # FR
        ('\n'
         '-= Bonjour $destName, =-\n'
         '-= bienvenue sur $ownCall ($distance km), =-\n'
         '-= sur le canal du terminal $channel <> Port $portNr. =-\n'
         '-= C\'est votre connexion n° $connNr. =-\n'
         '-= $ver - Max-Frame : $parmMaxFrame - Pac-Len : $parmPacLen =-\n'
         '\n'
         ' # Dernière connexion le : $lastConnDate à : $lastConnTime\n'
         '\n'),
        # FI
        ('\n'
       '-= Hallo $destName, =-\n' 
       '-= willkommen bei $ownCall ($distance km), =-\n'
       '-= auf Terminal-Kanal $channel <> Port $portNr. =-\n'
       '-= Das ist Connect Nr. $connNr. =-\n'
       '-= $ver - Max-Frame: $parmMaxFrame - Pac-Len: $parmPacLen =-\n'
       '\n'
       ' # Letzer Login am: $lastConnDate um: $lastConnTime\n'
       '\n'),
        # PL
        ('\n'
       '-= Hallo $destName, =-\n' 
       '-= willkommen bei $ownCall ($distance km), =-\n'
       '-= auf Terminal-Kanal $channel <> Port $portNr. =-\n'
       '-= Das ist Connect Nr. $connNr. =-\n'
       '-= $ver - Max-Frame: $parmMaxFrame - Pac-Len: $parmPacLen =-\n'
       '\n'
       ' # Letzer Login am: $lastConnDate um: $lastConnTime\n'
       '\n'),
        # PT
        ('\n'
       '-= Hallo $destName, =-\n' 
       '-= willkommen bei $ownCall ($distance km), =-\n'
       '-= auf Terminal-Kanal $channel <> Port $portNr. =-\n'
       '-= Das ist Connect Nr. $connNr. =-\n'
       '-= $ver - Max-Frame: $parmMaxFrame - Pac-Len: $parmPacLen =-\n'
       '\n'
       ' # Letzer Login am: $lastConnDate um: $lastConnTime\n'
       '\n'),
        # IT
        ('\n'
       '-= Hallo $destName, =-\n' 
       '-= willkommen bei $ownCall ($distance km), =-\n'
       '-= auf Terminal-Kanal $channel <> Port $portNr. =-\n'
       '-= Das ist Connect Nr. $connNr. =-\n'
       '-= $ver - Max-Frame: $parmMaxFrame - Pac-Len: $parmPacLen =-\n'
       '\n'
       ' # Letzer Login am: $lastConnDate um: $lastConnTime\n'
       'v'),
        # ??????
        ('\n'
       '-= Hallo $destName, =-\n' 
       '-= willkommen bei $ownCall ($distance km), =-\n'
       '-= auf Terminal-Kanal $channel <> Port $portNr. =-\n'
       '-= Das ist Connect Nr. $connNr. =-\n'
       '-= $ver - Max-Frame: $parmMaxFrame - Pac-Len: $parmPacLen =-\n'
       '\n'
       ' # Letzer Login am: $lastConnDate um: $lastConnTime\n'
       '\n'),
        # ??????
        ('\n'
       '-= Hallo $destName, =-\n' 
       '-= willkommen bei $ownCall ($distance km), =-\n'
       '-= auf Terminal-Kanal $channel <> Port $portNr. =-\n'
       '-= Das ist Connect Nr. $connNr. =-\n'
       '-= $ver - Max-Frame: $parmMaxFrame - Pac-Len: $parmPacLen =-\n'
       '\n'
       ' # Letzer Login am: $lastConnDate um: $lastConnTime\n'
       '\n'),
    ),

    'default_btext': (
        '\n73 de $ownCall ...\n',
        '\n73 de $ownCall ...\n',
        '\n73 de $ownCall ...\n',
        '\n73 de $ownCall ...\n',
        '\n73 de $ownCall ...\n',
        '\n73 de $ownCall ...\n',
        '\n73 de $ownCall ...\n',
        '\n73 de $ownCall ...\n',
        '\n73 de $ownCall ...\n',
        '\n73 de $ownCall ...\n'),

    'language': (
        'Sprache',
        'Language',
        'Taal',
        'Langues',
        '',
        '',
        '',
        '',
        '',
        ''),

    'temperature': (
        'Temperatur',
        'Temperature',
        'Temperatuur',
        'Température',
        '',
        '',
        '',
        '',
        '',
        ''),

    'wx_press': (
        'Luftdruck',
        'Pressure',
        'Luchtdruk',
        'Pression',
        '',
        '',
        '',
        '',
        '',
        ''),

    'wx_hum': (
        'Luftfeuchtigkeit',
        'Humidity',
        'Vochtigheid',
        'Humidité',
        '',
        '',
        '',
        '',
        '',
        ''),

    'userdb_add_sysop_ent1': (
        'Informationen ergänzen?',
        'Add information?',
        'Informatie toevoegen?',
        'Ajouter information?',
        '',
        '',
        '',
        '',
        '',
        ''),

    'userdb_add_sysop_ent2': (
        'Einträge vom Sysop ergänzen ?',
        'Add information from the sysop?',
        'Informatie uit de sysop toevoegen?',
        'Ajouter information sur le sysop?',
        '',
        '',
        '',
        '',
        '',
        ''),

    'userdb_save_hint': (
        'Info: User Daten für {} wurden gespeichert..',
        'Info: User data for {} has been saved.',
        'Info: gebruikersgegevens voor {} zijn opgeslagen.',
        'Données utilisateur {} suvegardées',
        '',
        '',
        '',
        '',
        '',
        ''),

    'userdb_del_hint1': (
        'lösche',
        'delete',
        'verwijderen',
        'effacer',
        '',
        '',
        '',
        '',
        '',
        ''),

    'userdb_del_hint2': (
        'löschen',
        'delete',
        'verwijderen',
        'effacer',
        '',
        '',
        '',
        '',
        '',
        ''),

    'userdb_newUser': (
        'Neuer Eintrag',
        'New entry',
        'Nieuwe invoer',
        'Nouvelle entrée',
        '',
        '',
        '',
        '',
        '',
        ''),

    'prewritewin': (
        'Vorschreibfenster',
        'Prewriting window',
        'Voorschrijfvenster',
        'Fenêtre de préécriture',
        '',
        '',
        '',
        '',
        '',
        ''),

    'call_vali_warning_1': (
        'Call Format!',
        'Call format!',
        '-----------',
        'Format indicatif!',
        '',
        '',
        '',
        '',
        '',
        ''),

    'call_vali_warning_2': (
        'Max 6 Zeichen nur Großbuchstaben und Zahlen.',
        'Max 6 characters only capital letters and numbers.',
        '-----------',
        'Max 6 caractères, lettres majuscules et chiffresuniquement',
        '',
        '',
        '',
        '',
        '',
        ''),

    'del_station_hint': (
        'Hinweis: Station erfolgreich gelöscht.',
        'Note: Station deleted successfully.',
        'Opmerking: Zender is succesvol verwijderd.',
        'Note: station éffacée avec succès',
        '',
        '',
        '',
        '',
        '',
        ''),

    'del_station_warning_1': (
        'Station gelöscht',
        'Station deleted',
        'Zender verwijderd',
        'Station éffacée',
        '',
        '',
        '',
        '',
        '',
        ''),

    'del_station_warning_2': (
        'Laufwerk C: wurde erfolgreich formatiert.',
        'Drive C: was successfully formatted.',
        'Schijf C: is succesvol geformatteerd.',
        'Disque C a été formaté avec succès',
        '',
        '',
        '',
        '',
        '',
        ''),

    'del_station_hint_1': (
        'lösche Station',
        'delete Station',
        '-----------',
        'effacer station',
        '',
        '',
        '',
        '',
        '',
        ''),

    'del_station_hint_2': (
        'Willst du diese Station wirklich löschen? \nAlle Einstellungen sowie Texte gehen verloren !',
        'Do you really want to delete this station? \nAll settings and texts will be lost!',
        'Wilt u deze zender echt verwijderen? \nAlle instellingen en teksten gaan verloren!',
        'Voulez vous vraiment supprimer cette station\n Tous les paramètres et textes seront perdus',
        '',
        '',
        '',
        '',
        '',
        ''),

    'not_all_station_disco_hint_1': (
        'Stationen nicht disconnected',
        'Stations not disconnected',
        '-----------',
        'Stations non déconnectées',
        '',
        '',
        '',
        '',
        '',
        ''),

    'not_all_station_disco_hint_2': (
        'Nicht alle Stationen disconnected!',
        'Not all stations are disconnected!',
        '-----------',
        'Toutes les stations n\'ont pas été déconnectées',
        '',
        '',
        '',
        '',
        '',
        ''),

    'all_station_get_disco_hint_1': (
        'Stationen werden disconnected !',
        'Stations getting disconnected!',
        '-----------',
        'Les stations se déconnectent!',
        '',
        '',
        '',
        '',
        '',
        ''),

    'all_station_get_disco_hint_2': (
        'Es werden alle Stationen disconnected',
        'All stations getting disconnected',
        '-----------',
        'Toutes les stations sont déconnectés',
        '',
        '',
        '',
        '',
        '',
        '',
        ''),

    'close_port': (
'Info: Versuche Port {} zu schließen.',
           'Info: Try to close Port {}.',
           '-----------',
           'Info: Tentative de fermeture du Port {}.',
           '',
           '',
           '',
           '',
           '',
           ''),

    'port_closed': (
'Info: Port {} erfolgreich geschlossen.',
           'Info: Port {} closed successfully.',
           '-----------',
           'Info: Port {} fermé avec succès.',
           '',
           '',
           '',
           '',
           '',
           ''),

    'send_kiss_parm': (
'Hinweis: Kiss-Parameter an TNC auf Port {} gesendet..',
           'Note: Kiss parameters sent to TNC on port {}..',
           '-----------',
            'Note: Paramètres KISS envoyés au TNC port {}...',
           '',
           '',
           '',
           '',
           '',
           ''),

    'port_in_use': ('Error: Port {} konnte nicht initialisiert werden. Port wird bereits benutzt.',
           'Error: Port {} could not be initialized. Port is already in use.',
           '-----------',
           'Erreur: Port {} ne peut être initialisé. Le port est déjà en service',
           '',
           '',
           '',
           '',
           '',
           ''),

    'no_port_typ': (
'Hinweis: Kein Port-Typ ausgewählt. Port {}',
           'Note: No port type selected. port {}',
           '-----------',
           'Note: Aucun type de port séléctionné port {}',
           '',
           '',
           '',
           '',
           '',
           ''),

    'port_not_init': (
        'Error: Port {} konnte nicht initialisiert werden.',
        'Error: Port {} could not be initialized.',
        '-----------',
        'Erreur: Initialisation port {} impossible.',
        '',
        '',
        '',
        '',
        '',
        ''),
    'port_init': (
        'Info: Port {} erfolgreich initialisiert.',
        'Info: Port {} initialized successfully.',
        '-----------',
        'Info: Port {} initialisé avec succès.',
        '',
        '',
        '',
        '',
        '',
        ''),

    'setting_saved': (
        'Info: {}-Einstellungen wurden gespeichert.',
        'Info: {}-Settings saved.',
        '-----------',
        'Info: {}-paramètres sauvegardés',
        '',
        '',
        '',
        '',
        '',
        ''),

    'all_port_reinit': (
        'Info: Ports werden reinitialisiert.',
        'Info: Ports are reinitialized.',
        '-----------',
        'Info: Ports réinitialisés',
        '',
        '',
        '',
        '',
        '',
        ''),

    'port_reinit': (
        'Info: Port {} wird reinitialisiert.',
        'Info: Port {} is reinitialized.',
        '-----------',
        'Info: Port {} réinitialisé.',
        '',
        '',
        '',
        '',
        '',
        ''),

    'all_disco1': (
        'Stationen werden disconnected !',
        'Stations are disconnected!',
        'Stations zijn losgekoppeld!',
        'Les stations sont déconnectées!',
        '',
        '',
        '',
        '',
        '',
        ''),
    'all_disco2': (
        'Es werden alle Stationen disconnected',
        'All stations are disconnected',
        'Alle stations zijn losgekoppeld',
        'Toutes les stations sont déconnectées',
        '',
        '',
        '',
        '',
        '',
        ''),

    'OK': (
        'OK',
        'OK',
        'OK',
        'OK',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cancel': (
        'Abbrechen',
        'Cancel',
        'Onderbreken',
        'Annuler',
        '',
        '',
        '',
        '',
        '',
        ''),

    'aborted': (
        'Abgebrochen',
        'Aborted',
        'Onderbroken',
        'Annulé',
        '',
        '',
        '',
        '',
        '',
        ''),

    'delete': (
        'Löschen',
        'Delete',
        'Verwijder',
        'Effacer',
        '',
        '',
        '',
        '',
        '',
        ''),

    'delete_dx_history': (
        'DX-History Löschen',
        'Delete DX-History',
        'Verwijder DX-History',
        "Effacer l'historique DX",
        '',
        '',
        '',
        '',
        '',
        ''),

    'del_all': (
        'Alles Löschen',
        'Delete all',
        'Verwijder alles',
        'Effacer tout',
        '',
        '',
        '',
        '',
        '',
        ''),

    'go': (
        'Los',
        'Go',
        'Gaan',
        'Go',
        '',
        '',
        '',
        '',
        '',
        ''),

    'close': (
        'Schließen',
        'Close',
        'Sluiten',
        'Fermer',
        '',
        '',
        '',
        '',
        '',
        ''),

    'save': (
        'Speichern',
        'Save',
        'Opslaan',
        'Enregistrer',
        '',
        '',
        '',
        '',
        '',
        ''),

    'forward': (
        'Weiterleiten',
        'Forward',
        'Vooruit',
        'Forward',
        '',
        '',
        '',
        '',
        '',
        ''),

    'answer': (
        'Antworten',
        'Answer',
        'Antwoord',
        'Réponse',
        '',
        '',
        '',
        '',
        '',
        ''),

    'send_file': (
        'Datei senden',
        'Send File',
        'Verstuur bestand',
        'Envoi fichier',
        '',
        '',
        '',
        '',
        '',
        ''),

    'file_1': (
        'Datei',
        'File',
        'Bestand',
        'Fichier',
        '',
        '',
        '',
        '',
        '',
        ''),

    'file_2': (
        'Datei:',
        'File:',
        'Bestand:',
        'Fichier:',
        '',
        '',
        '',
        '',
        '',
        ''),

    'locator_calc': (
        'Locator Rechner',
        'Locator Calculator',
        'Lokatie berekenen',
        '',
        '',
        '',
        '',
        '',
        '',
        ''),

    'aprs_mon': (
        'APRS-Server Monitor',
        'APRS-Server Monitor',
        'APRS-Server Monitor',
        'Moniteur APRS-Server',
        '',
        '',
        '',
        '',
        '',
        ''),

    'protocol': (
        'Protokoll:',
        'Protocol:',
        'Protocol:',
        'Protocole:',
        '',
        '',
        '',
        '',
        '',
        ''),

    'send_if_free': (
        'Senden wenn Band frei für (sek.):',
        'Send when band is free for (sec.):',
        'Zenden wanneer band vrij is',
        'Envoyer quand la bande est libre depuis (sec.):',
        '',
        '',
        '',
        '',
        '',
        ''),

    'size': (
        'Größe:',
        'Size:',
        'Groot:',
        'Taille:',
        '',
        '',
        '',
        '',
        '',
        ''),

    'new': (
        'Neu',
        'New',
        'Nieuw',
        'Nouveau',
        '',
        '',
        '',
        '',
        '',
        ''),

    'new_port': (
        'Neuer Port',
        'New port',
        'Nieuwe Poort',
        'Nouveau Port',
        '',
        '',
        '',
        '',
        '',
        ''),

    'new_conn': (
        'Neu Verbindung',
        'New Connection',
        'Nieuwe verbinding',
        'Nouvelle connexion',
        '',
        '',
        '',
        '',
        '',
        ''),

    'disconnect': (
        'Disconnecten',
        'Disconnect',
        'Verbreken',
        'Deconnecter',
        '',
        '',
        '',
        '',
        '',
        ''),

    'disconnect_all': (
        'ALLE disconnecten',
        'Disconnect ALL',
        'Verbreek alles',
        'Deconnecter tout',
        '',
        '',
        '',
        '',
        '',
        ''),

    'disconnect_all_ask': (
        'Wirklich ALLE Stationen disconnecten ?',
        'Do you want to disconnect ALL stations?',
        'Wilt u ALLE stations verbreken?',
        'Voulez vous déconnecter toutes les sttions?',
        '',
        '',
        '',
        '',
        '',
        ''),

    'wx_window': (
        'Wetterstationen',
        'Weather Stations',
        'Weerstations',
        'Stations météos',
        '',
        '',
        '',
        '',
        '',
        ''),

    'quit': (
        'Quit',
        'Quit',
        'sluiten',
        'Quitter',
        '',
        '',
        '',
        '',
        '',
        ''),

    'connections': (
        'Verbindungen',
        'Connections',
        'Koppelingen',
        'Connexions',
        '',
        '',
        '',
        '',
        '',
        ''),

    'copy': (
        'Kopieren',
        'Copy',
        'Kopiëren',
        'Copier',
        '',
        '',
        '',
        '',
        '',
        ''),

    'past': (
        'Einfügen',
        'Past',
        'Invoegen',
        'Coller',
        '',
        '',
        '',
        '',
        '',
        ''),

    'past_f_file': (
        'Aus Datei einfügen',
        'Past from File',
        'invoegen uit bestand',
        'Coller depuis fichier',
        '',
        '',
        '',
        '',
        '',
        ''),

    'save_to_file': (
        'In Datei speichern',
        'Save to File',
        'Bestand opslaan',
        'Enregistrer dans fichier',
        '',
        '',
        '',
        '',
        '',
        ''),

    'past_qso_f_file': (
        'Aus Datei einfügen',
        'Past from File',
        'Invoegen uit bestand',
        'Coller dans fichier',
        '',
        '',
        '',
        '',
        '',
        ''),

    'save_qso_to_file': (
        'QSO in Datei speichern',
        'Save QSO to File',
        'QSO opslaan',
        'Enregistrer QSO dans fichier',
        '',
        '',
        '',
        '',
        '',
        ''),

    'save_mon_to_file': (
        'Monitor in Datei speichern',
        'Save Monitor to File',
        'Kopieer monitor naar bestand',
        'Enregistrer moniteur dans fichier',
        '',
        '',
        '',
        '',
        '',
        ''),

    'clean_qso_win': (
        'QSO/Vorschreibfenster löschen',
        'Clear QSO/Prescription window',
        'QSO verwijderen',
        'Effacer QSO/fenêtre préredaction',
        '',
        '',
        '',
        '',
        '',
        ''),

    'clean_all_qso_win': (
        'Alle QSO/Vorschreibfenster löschen',
        'Clear all QSO/Prescription window',
        'Alle QSO verwijderen',
        'Effacer tous QSO/fenêtres préredactions',
        '',
        '',
        '',
        '',
        '',
        ''),

    'clean_mon_win': (
        'Monitor löschen',
        'Clear Monitor',
        'Monitor wissen',
        'Effacer moniteur',
        '',
        '',
        '',
        '',
        '',
        ''),

    'edit': (
        'Bearbeiten',
        'Edit',
        'Bewerken',
        'Editer',
        '',
        '',
        '',
        '',
        '',
        ''),

    'statistic': (
        'Statistik',
        'Statistics',
        'Statistieken',
        'Statistiques',
        '',
        '',
        '',
        '',
        '',
        ''),

    'linkholder': (
        'Linkhalter',
        'Link holder',
        'Link houder',
        'Liste liens',
        '',
        '',
        '',
        '',
        '',
        ''),  #
    'clean_qso': (
        'QSO löschen',
        'delete QSO',
        'QSO verwijderen',
        'Effacer QSO',
        '',
        '',
        '',
        '',
        '',
        ''),

    'tools': (
        'Tools',
        'Tools',
        'Hulpmiddelen',
        'Outils',
        '',
        '',
        '',
        '',
        '',
        ''),

    'station': (
        'Station',
        'Station',
        'Station',
        'Station',
        '',
        '',
        '',
        '',
        '',
        ''),

    'stations': (
        'Stationen',
        'Stations',
        'Stations',
        '',
        '',
        '',
        '',
        '',
        '',
        ''),

    'port': (
        'Port',
        'Port',
        'Poort',
        'Port',
        '',
        '',
        '',
        '',
        '',
        ''),

    'channel': (
        'Kanal',
        'Channel',
        'Kanaal',
        'Canal',
        '',
        '',
        '',
        '',
        '',
        ''),

    'beacon': (
        'Baken',
        'Beacons',
        'Baken',
        'Balises',
        '',
        '',
        '',
        '',
        '',
        ''),

    'sprech': (
        'Sprachausgabe',
        'Speech output',
        'Spraakuitvoer',
        'Sortie vocale',
        '',
        '',
        '',
        '',
        '',
        ''),

    'settings': (
        'Einstellungen',
        'Settings',
        'Instellingen',
        'Paramètres',
        '',
        '',
        '',
        '',
        '',
        ''),

    'main_page': (
        'Hauptseite',
        'Main Page',
        'Hoofdpagina',
        'Page principale',
        '',
        '',
        '',
        '',
        '',
        ''),

    'passwords': (
        'Passwörter',
        'Passwords',
        'Wachtwoord',
        'Mots de passe',
        '',
        '',
        '',
        '',
        '',
        ''),

    'syspassword': (
        'Sys-Passwort:',
        'Sys-Password:',
        'Gebruiker-wachtwoord:',
        'Mot de passe Sys',
        '',
        '',
        '',
        '',
        '',
        ''),

    'trys': (
        'Fake-Versuche:',
        'Fake-Attempts:',
        'Valse pogingen:',
        'Fausses tentatives :',
        '',
        '',
        '',
        '',
        '',
        ''),

    'fillchars': (
        'Antwortlänge:',
        'Response length:',
        'Reactie lengte:',
        'Longueur réponse :',
        '',
        '',
        '',
        '',
        '',
        ''),

    'priv': (
        'Login',
        'Login',
        'Inlog',
        'Login',
        '',
        '',
        '',
        '',
        '',
        ''),

    'login_cmd': (
        'Login Kommando:',
        'Login Command:',
        'Inlog commando:',
        'Commande login :',
        '',
        '',
        '',
        '',
        '',
        ''),

    'keybind': (
        'Tastaturbelegung',
        'Keyboard layout',
        'Toetsenbordindeling',
        'Racourcis clavier',
        '',
        '',
        '',
        '',
        '',
        ''),

    'about': (
        'Über',
        'About',
        'Over',
        'A propos',
        '',
        '',
        '',
        '',
        '',
        ''),

    'help': (
        'Hilfe',
        'Help',
        'Hulp',
        'Aide',
        '',
        '',
        '',
        '',
        '',
        ''),

    'number': (
        'Anzahl',
        'Number',
        'Nummer',
        'Nombre',
        '',
        '',
        '',
        '',
        '',
        ''),

    'minutes': (
        'Minuten',
        'Minutes',
        'Minuut',
        'Minutes',
        '',
        '',
        '',
        '',
        '',
        ''),

    'hours': (
        'Stunden',
        'Hours',
        'Uur',
        'Heures',
        '',
        '',
        '',
        '',
        '',
        ''),

    'day': (
        'Tag',
        'Day',
        'Dag',
        'Jour',
        '',
        '',
        '',
        '',
        '',
        ''),

    'month': (
        'Monat',
        'Month',
        'Maand',
        'Mois',
        '',
        '',
        '',
        '',
        '',
        ''),

    'occup': (
        'Auslastung in %',
        'Occupancy in %',
        'Werkdruk in %',
        'Taux d\'occupation (en %)',
        '',
        '',
        '',
        '',
        '',
        ''),

    'call': (
        'Call',
        'Call',
        'Gebruiker',
        'Indicatif',
        '',
        '',
        '',
        '',
        '',
        ''),

    'name': (
        'Name',
        'Name',
        'Naam',
        'Nom',
        '',
        '',
        '',
        '',
        '',
        ''),

    'fwd_list': (
        'Forward Warteschlange',
        'Forward queue',
        'Voorwaartse wachtrij',
        'Forward queue',
        '',
        '',
        '',
        '',
        '',
        ''),

    'fwd_path': (
        'Forward Routen',
        'Forward routes',
        'Voorwaartse routes',
        'Routes forward',
        '',
        '',
        '',
        '',
        '',
        ''),

    'start_fwd': (
        'FWD Starten',
        'FWD start',
        'Start FWD',
        'Début FWD',
        '',
        '',
        '',
        '',
        '',
        ''),

    'start_auto_fwd': (
        'AutoFWD Start',
        'AutoFWD start',
        'Start AutoFWD',
        'Début FWD auto',
        '',
        '',
        '',
        '',
        '',
        ''),

    'msg_center': (
        'Nachrichten Center',
        'Message Center',
        'Berichten Center',
        'Centre des méssages',
        '',
        '',
        '',
        '',
        '',
        ''),

    'qso_win_color': (
        'QSO Fenster Farben',
        'QSO Win Color',
        'QSO Win Kleur',
        'Couleur fenêtre QSO',
        '',
        '',
        '',
        '',
        '',
        ''),

    'text_color': (
        'Text Farben',
        'Text Color',
        'Text kleur',
        'Couleur du texte',
        '',
        '',
        '',
        '',
        '',
        ''),

    'bg_color': (
        'Hintergrund Farben',
        'Backgrund Color',
        'BG kleur',
        'Couleur arrière plan',
        '',
        '',
        '',
        '',
        '',
        ''),

    'mon_color': (
        'Monitor Farben',
        'Monitor Colors',
        'Monitor Kleur',
        'Couleur du moniteur',
        '',
        '',
        '',
        '',
        '',
        ''),

    'c_text': (
        'C Text',
        'C Text',
        'C-Text',
        'C-texte',
        '',
        '',
        '',
        '',
        '',
        ''),

    'q_text': (
        'Quit Text',
        'Quit Text',
        'Quit-Text',
        'Quit-Text',
        '',
        '',
        '',
        '',
        '',
        ''),

    'i_text': (
        'Info Text',
        'Info Text',
        'Info-Text',
        'Info-Text',
        '',
        '',
        '',
        '',
        '',
        ''),

    'li_text': (
        'Lang-Info Text',
        'Long-Info Text',
        'Lange-Info Text',
        'Texte info long',
        '',
        '',
        '',
        '',
        '',
        ''),

    'news_text': (
        'News Text',
        'News Text',
        'Nieuws-Text',
        'texte actualités',
        '',
        '',
        '',
        '',
        '',
        ''),

    'aprs_settings': (
        'APRS-Einstellungen',
        'APRS-Settings',
        'APRS-instellingen',
        'Paramètres APRS',
        '',
        '',
        '',
        '',
        '',
        ''),

    'aprs_pn_msg': (
        'APRS Private Nachrichten',
        'APRS Private Messages',
        'APRS Prive berichten',
        'Message APRS privés',
        '',
        '',
        '',
        '',
        '',
        ''),

    'pn_msg': (
        'Private Nachrichten',
        'Private Messages',
        'Prive berichten',
        'Messages privés',
        '',
        '',
        '',
        '',
        '',
        ''),

    'msg': (
        'Nachricht',
        'Message',
        'Bericht',
        'Message',
        '',
        '',
        '',
        '',
        '',
        ''),

    'new_msg': (
        'Neue Nachricht',
        'New Message',
        'Nieuw bericht',
        'Nouveau Message',
        '',
        '',
        '',
        '',
        '',
        ''),

    'new_pr_mail': (
        'Neue PR-Mail',
        'New PR-Mail',
        'Nieuwe PR-Mail',
        'Nouveau PR-mail',
        '',
        '',
        '',
        '',
        '',
        ''),

    'send_all_now': (
        'Alles sofort senden',
        'Send everything now',
        'Stuur alles onmiddellijk',
        'Envoyer tout maintenant',
        '',
        '',
        '',
        '',
        '',
        ''),

    'mark_all_read': (
        'Alle als gelesen markieren',
        'Mark all as read',
        'Markeer alles als gelezen',
        'Tous marquer comme lu',
        '',
        '',
        '',
        '',
        '',
        ''),

    'stat_settings': (
        'Station',
        'Station',
        'Gebruiker',
        'Station',
        'Station',
        '',
        '',
        '',
        '',
        ''),  #

    'general_settings': (
        'Allgemein',
        'General',
        'Algemeen',
        'Général',
        '',
        '',
        '',
        '',
        '',
        ''),

'GPIO': (
        'GPIO',
        'GPIO',
        'GPIO',
        'GPIO',
        '',
        '',
        '',
        '',
        '',
        ''),

'Digipeater': (
        'Digipeater',
        'Digipeater',
        'Digipeater',
        'Digipeater',
        '',
        '',
        '',
        '',
        '',
        ''),

'F-Text': (
        'F-Text',
        'F-Text',
        'F-Text',
        'F-Text',
        '',
        '',
        '',
        '',
        '',
        ''),

    'MCast': (
        'MCast',
        'MCast',
        'MCast',
        'MCast',
        '',
        '',
        '',
        '',
        '',
        ''),

    'RX-Echo': (
        'RX-Echo',
        'RX-Echo',
        'RX-Echo',
        'RX-Echo',
        '',
        '',
        '',
        '',
        '',
        ''),

    'new_stat': (
        'Neue Station',
        'New Station',
        'nieuwe gebruiker',
        'Nouvelle station',
        '',
        '',
        '',
        '',
        '',
        ''),


    'txt_decoding': (
        'Umlautumwandlung',
        'Text decoding',
        'Text decoding',
        'Decodage texte',
        '',
        '',
        '',
        '',
        '',
        ''),

    'suc_save': (
        'Info: Station Einstellungen erfolgreich gespeichert.',
        'Info: Station setiings saved.'
        'Info: Gebruiker instellingen goed opgelsagen.',
        'Infos : paramètres station enregistrés',
        '',
        '',
        '',
        '',
        '',
        ''),

    'lob1': (
        'Lob: Das hast du sehr gut gemacht !!',
        'Praise: You did very well!!',
        'Dat heb je zeer goed gemaakt',
        'Éloge : Vous vous êtes très bien débrouillés !',
        '',
        '',
        '',
        '',
        '',
        ''),

    'lob2': (
        'Lob: Das hast du gut gemacht !!',
        'Praise: You did well!!',
        'Dat heb je goed gemaakt ',
        'Éloge : Vous avez bien travaillé !',
        '',
        '',
        '',
        '',
        '',
        ''),

    'lob3': (
        'Lob: Das war eine gute Entscheidung. Mach weiter so. Das hast du gut gemacht.',
        'Praise: That was a good decision. Keep it up. You did well.',
        'Dat was een goede beslissing. Ga zo door. Dat heb je goed gemaakt.',
        'Éloge : C\'était une bonne décision. Continuez. Vous avez bien travaillé,',
        '',
        '',
        '',
        '',
        '',
        ''),  #

    'lob4': (
        'Lob: Du hast dir heute noch kein Lob verdient.',
        "Praise: You haven't earned any praise today.",
        'Je hebt vandaag geen lof verdiend.',
        'Éloges : Vous n\'avez pas mérité d\'être félicité aujourd\'hui.',
        '',
        '',
        '',
        '',
        '',
        ''),

    'lob5': (
        'Es tut mir leid, Dave. Ich fürchte, das kann ich nicht.',
        "I'm sorry, Dave. I'm afraid I can't do that.",
        'Het spijt me, Dave. Ik ben bang dat ik dat niet kan.',
        'Je suis désolé, Dave. J\'ai bien peur de ne pas pouvoir le faire ',
        '',
        '',
        '',
        '',
        '',
        ''),

    'hin1': (
        'Hinweis: Der OK Button funktioniert noch !!',
        'Note: The OK button still works !!',
        'De OK knop werkt nog !!',
        'Note le bouton OK fonctionne',
        '',
        '',
        '',
        '',
        '',
        ''),

    'hin2': (
        'Hinweis: Knack!! Abgebrochen..',
        'Note: Canceled !!',
        'geannuleerd!',
        'Note : Annulé',
        '',
        '',
        '',
        '',
        '',
        ''),

    'date_time': (
        'Datum/Zeit',
        'Date/Time',
        'Datum/tijd',
        'Date/heure',
        '',
        '',
        '',
        '',
        '',
        ''),

    'date': (
        'Datum',
        'Date',
        'Datum',
        'Date',
        '',
        '',
        '',
        '',
        '',
        ''),

    'message': (
        'Nachricht',
        'Message',
        'Nieuws',
        'Messages',
        '',
        '',
        '',
        '',
        '',
        ''),

    'titel': (
        'Titel',
        'Title',
        'Titel',
        'Titre',
        '',
        '',
        '',
        '',
        '',
        ''),

    'from': (
        'Von',
        'From',
        'van ',
        'De',
        '',
        '',
        '',
        '',
        '',
        ''),

    'to': (
        'An',
        'To',
        'Naar ',
        'Pour',
        '',
        '',
        '',
        '',
        '',
        ''),

    'subject': (
        'Betreff',
        'Subject',
        'Onderwerp ',
        'Sujet',
        '',
        '',
        '',
        '',
        '',
        ''),

    'versatz': (
        'Versatz',
        'Offset',
        'Verzet',
        'Offset',
        '',
        '',
        '',
        '',
        '',
        ''),

    'intervall': (
        'Intervall',
        'Interval',
        'Interval',
        'Intervalle',
        '',
        '',
        '',
        '',
        '',
        ''),

    'active': (
        'Aktiviert',
        'Activated',
        'Ingeschakeld',
        'Activé',
        '',
        '',
        '',
        '',
        '',
        ''),

    'text_fm_file': (
        'Text aus Datei',
        'Text from File',
        'Tekst uit bestand ',
        'Texte depuis fichier',
        '',
        '',
        '',
        '',
        '',
        ''),

    'beacon_settings': (
        'Baken',
        'Beacon',
        'Baken',
        'Balise',
        '',
        '',
        '',
        '',
        '',
        ''),

    'pipetool_settings': (
        'Pipe-Tool Einstellungen',
        'Pipe-Tool Settings',
        'Pipe-Tool Instellingen',
        'paramètres Pipe-tools',
        '',
        '',
        '',
        '',
        '',
        ''),

    'new_pipe': (
        'Neue Pipe',
        'New Pipe',
        'Nieuwe Pipe',
        'Nouveau Pipe',
        '',
        '',
        '',
        '',
        '',
        ''),

    'new_pipe_fm_connection': (
        'Pipe auf Verbindung',
        'Pipe on Connection',
        'Pipe op aansluiting',
        'Pipe à la connexion',
        '',
        '',
        '',
        '',
        '',
        ''),

    'tx_file': (
        'TX Datei',
        'TX File',
        'TX-File',
        'TX fichier',
        '',
        '',
        '',
        '',
        '',
        ''),

    'rx_file': (
        'RX Datei',
        'RX File',
        'RX-File',
        'RX fichier',
        '',
        '',
        '',
        '',
        '',
        ''),

    'port_cfg_std_parm': (
        'Standard Parameter. Werden genutzt wenn nirgendwo anders (Station/Client) definiert.',
        'Default parameters. Are used if not defined anywhere else (station/client).',
        'Standaardparameters. Worden gebruikt als ze nergens anders zijn gedefinieerd (station/client).',
        'Paramètres par défaut. Utilisés si non définis (station/client)',
        '',
        '',
        '',
        '',
        '',
        ''),

    'port_cfg_psd_txd': (
        'Pseudo TX-Delay (Wartezeit zwischen TX und RX). Wird nicht als KISS Parameter am TNC gesetzt.',
        'Pseudo TX delay (waiting time between TX and RX). Is not set as a KISS parameter on the TNC.',
        'Pseudo TX-vertraging (wachttijd tussen TX en RX). Is op de TNC niet als KISS-parameter ingesteld.',
        'Pseudo TX delay (attente entre TX et RX si non défini dans les paramètres KISS du TNC',
        '',
        '',
        '',
        '',
        '',
        ''),

    'port_cfg_pac_len': (
        'Paket Länge. 1 - 256',
        'Packet length. 1-256',
        'Pakket lengte. 1-256',
        'Longueur trame. 1-256',
        '',
        '',
        '',
        '',
        '',
        ''),

    'port_cfg_pac_max': (
        'Max Paket Anzahl. 1 - 7',
        'Max Packets. 1 - 7',
        'Max pakketnummer. 1 - 7',
        'Max trame. 1-7',
        '',
        '',
        '',
        '',
        '',
        ''),

    'port_cfg_port_name': (
        'Port Bezeichnung für MH und Monitor( Max: 4 ):',
        'Port designation for MH and monitor (Max: 4):',
        'Poortaanduiding voor MH en monitor (Max: 4):',
        'Port pour MH dns le moniteur (Max: 4)',
        '',
        '',
        '',
        '',
        '',
        ''),

    'port_cfg_not_init': (
        '!! Port ist nicht Initialisiert !!',
        '!! Port is not initialized!!',
        '!! Poort is niet geïnitialiseerd!!',
        '!! Port non initialisé',
        '',
        '',
        '',
        '',
        '',
        ''),

    'new_beacon': (
        'Neue Bake',
        'New Beacon',
        'Nieuw baken',
        'Nouvelle balise',
        '',
        '',
        '',
        '',
        '',
        ''),

    'last_packet': (
        'letztes Paket',
        'last packet',
        'laatste pakket',
        'Dernière trame',
        '',
        '',
        '',
        '',
        '',
        ''),

    'scrolling': (
        'Auto Scrollen',
        'Auto scrolling',
        'Automatisch scrollen',
        'Défilement auto',
        '',
        '',
        '',
        '',
        '',
        ''),

    'msg_box_mh_delete': (
        'MH-Liste Löschen',
        'Delete MH list',
        'Verwijder MH-lijst',
        'Effacer liste MH',
        '',
        '',
        '',
        '',
        '',
        ''),

    'msg_box_mh_delete_msg': (
        'Komplette MH-Liste löschen?',
        'Delete entire MH list?',
        'Volledige MH-lijst verwijderen?',
        'Supprimer la liste MH complète',
        '',
        '',
        '',
        '',
        '',
        ''),

    'msg_box_delete_data': (
        'Daten Löschen',
        'Delete data',
        'Verwijder data',
        'Effacer données',
        '',
        '',
        '',
        '',
        '',
        ''),

    'msg_box_delete_data_msg': (
        'Alle Daten löschen?',
        'Delete all data?',
        'Alle gegevens verwijderen?',
        'Effacer toutes les données',
        '',
        '',
        '',
        '',
        '',
        ''),

    'data': (
        'Daten',
        'Data',
        'Gegevens',
        'Données',
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
        'Soyez prudent avec les connexions de node comme TNN. La liaison de plusieurs nodes via la multidiffusion peut entraîner des problèmes »,',
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
        'Base de données utilisateur',
        '',
        '',
        '',
        '',
        '',
        ''),

    # CLI
    'cmd_help_bell': (
        'Sysop Rufen',
        'Call Sysop',
        'Gebruiker roepen',
        'Appel Sysop',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cmd_help_wx': (
        'Wetterstationen',
        'Weather stations',
        'Weerstations',
        'Stations météo',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cmd_help_user_db': (
        'Call DB Abfrage',
        'Get Call DB entry',
        'Ontvang gebruiker DB-invoer',
        'Obtenir l\'entrée dans la bdd des appels',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cmd_help_set_name': (
        'Namen eintragen',
        'Enter Name',
        'naam ingevuld',
        'Entrez Nom',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cmd_help_set_qth': (
        'QTH eintragen',
        'Enter QTH',
        'Locatie ingevuld',
        'Entrez QTH',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cmd_help_set_loc': (
        'Locator eintragen',
        'Enter Locator',
        'Locator ingevuld',
        'Entrez Locator',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cmd_help_set_zip': (
        'Postleitzahl eintragen',
        'Enter ZIP',
        'Postcode ingevuld',
        'Entrez CP',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cmd_help_set_prmail': (
        'PR-MAIL Adresse eintragen',
        'Enter PR-MAIL Address',
        'PR-MAIL ingevuld',
        'Entrez adresse PR-MAIL',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cmd_help_set_email': (
        'E-MAIL Adresse eintragen',
        'Enter E-MAIL Address',
        'E-MAIL ingevuld',
        'Entrez adresse E-mail',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cmd_help_set_http': (
        'HTTP eintragen',
        'Enter HTTP',
        'HTTP ingevuld',
        'Entrez http',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cli_no_user_db_ent': (
        ' # Eintag nicht in Benutzer Datenbank vorhanden!',
        ' # Entry not in user database!',
        ' # Invoer niet in gebruikersdatabase!',
        ' # Entrée non trouvé dans la BDD utilisateur!!',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cli_name_set': (
        ' # Name eingetragen',
        ' # Username is set',
        ' # Naam ingevoerd',
        ' # Nom utilisateur défini',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cli_qth_set': (
        ' # QTH eingetragen',
        ' # QTH is set',
        ' # Locatie ingevoerd',
        ' # QTH défini',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cli_loc_set': (
        ' # Locator eingetragen',
        ' # Locator is set',
        ' # Locator ingevoerd',
        ' # Locator défini',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cli_zip_set': (
        ' # Postleitzahl eingetragen',
        ' # ZIP is set',
        ' # Postcode ingevoerd',
        ' # CP défini',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cli_prmail_set': (
        ' # PR-Mail Adresse eingetragen',
        ' # PR-Mail Address is set',
        ' # PR-Mail ingevoerd',
        ' # Adresse PR-Mail définie',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cli_email_set': (
        ' # E-Mail Adresse eingetragen',
        ' # E-Mail Address is set',
        ' # E-Mail ingevoerd',
        ' # Adresse E-mail définie',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cli_http_set': (
        ' # HTTP eingetragen',
        ' # HTTP is set',
        ' # HTTP ingevoerd',
        ' # HTTP défini',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cli_text_encoding_no_param': (
        ' # Bitte ein ä senden. Bsp.: UM ä.\r # Derzeitige Einstellung:',
        ' # Please send an ä. Example: UM ä.\r # Current setting:',
        ' # Stuur een  ä. voorbeeld ä.\r # Huidige instelling:',
        ' # Veuillez envoyer un ä. Exemple : UM ä.\r # Réglage actuel :',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cli_text_encoding_error_not_found': (
        ' # Umlaute wurden nicht erkannt !',
        " # Couldn't detect right text encoding",
        ' # Kan de juiste tekstcodering niet detecteren',
        ' # Ne peut detecter le bon encodage',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cli_text_encoding_set': (
        ' # Umlaute/Text de/enkodierung erkannt und gesetzt auf:',
        " # Text de/encoding detected and set to:",
        ' # Tekstde/codering gedetecteerd en ingesteld op:',
        'Encodage/decodage du texte détecté et paramétré à :',
        '',
        '',
        '',
        '',
        '',
        ''),

    'port_overview': (
        'Port Übersicht',
        'Port Overview',
        'Poort overzicht',
        'Vue d\'ensemble Ports',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cmd_shelp': (
        'Kurzhilfe',
        'Short help',
        'Korte hulp',
        'Aide courte',
        '',
        '',
        '',
        '',
        '',
        ''),

    'time_connected': (
        'Connect Dauer',
        'Connect duration',
        'verbindingsduur',
        'Durée connexion',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cmd_not_known': (
        'Dieses Kommando ist dem System nicht bekannt !',
        'The system does not know this command !',
        'Het systeem kent deze opdracht niet !',
        '',
        '',
        '',
        '',
        '',
        '',
        ''),

    'auto_text_encoding': (
        'Automatisch Umlaut Erkennung. ä als Parameter. > UM ä',
        'Automatic detection of text encoding. ä as a parameter. > UM ä',
        'Automatische detectie van tekstcodering. ä als parameter. > UM ä',
        'Détection automatique de l\'encodage du texte. ä comme paramètre. > UM ä',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cmd_help_lcstatus': (
        'Verbundene Terminalkanäle anzeigen (ausführliche Version)',
        'Show connected terminal channels (detailed version)',
        'Toon aangesloten terminalkanalen (gedetailleerde versie)',
        'Afficher les terminal connectés (version détaillée)',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cli_no_wx_data': (
        'Keine Wetterdaten vorhanden.',
        'No WX data available',
        'Geen WX beschikbaar.',
        'Aucune données météos disponnible',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cli_no_data': (
        'Keine Daten vorhanden.',
        'No data available.',
        'Geen gegevens beschikbaar.',
        '',
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
        'Pas de données Tracer disponnibles',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cli_change_language': (
        'Sprache ändern.',
        'Change language.',
        'Taal veranderen',
        'Modifier langue',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cli_lang_set': (
        'Sprache auf Deutsch geändert.',
        'Language changed to English.',
        'Taal veranderd naar Nederlands.',
        'Lange changé pour Français',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cli_no_lang_param': (
        'Sprache nicht erkannt! Mögliche Sprachen: ',
        'Language not recognized! Possible languages: ',
        'Taal niet herkend! Mogelijke talen: ',
        'Langue non reconnue! Langues possibles',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cmd_bell': (
        'Sysop wird gerufen !!',
        'Sysop is called!!',
        'Gebruiker wordt geroepen!!',
        'Sysop appelé',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cmd_bell_again': (
        'Sysop wurde bereits gerufen..',
        'Sysop has already been called..',
        'Gebruiker is al geroepen..',
        'Le Sysop a déjà ete appelé',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cmd_bell_gui_msg': (
        'verlangt nach dem Sysop !!',
        'asks for the sysop!!',
        'vraagt om de gebruiker!!',
        'Appel du Sysop!!',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cmd_c_noCall': (
        '# Bitte Call eingeben..',
        '# Please enter call..',
        '# Voer een oproep in..',
        '# Entrez indicaif SVP',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cmd_c_badCall': (
        '# Ungültiger Ziel Call..',
        '# Invalid destination call..',
        '# Ongeldige bestemmingsoproep..',
        '# indicatif de destinantion invalide..',
        '',
        '',
        '',
        '',
        '',
        ''),
    'cmd_c_badPort': (
        '# Ungültige Port Angabe..',
        '# Invalid port specification..',
        '# Ongeldige poortspecificatie..',
        '',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cmd_c_noPort': (
        '# Ungültiger Port..',
        '# Invalid port..',
        '# Ongeldige poort..',
        '# Port invalide..',
        '',
        '',
        '',
        '',
        '',
        ''),

    #####################################################
    # MCast

    'cmd_help_mcast_move_ch': (
        'MCast Kanal wechseln',
        'Change MCast channel',
        'MCast kanaal wijzigen',
        'Changer canal MCAST',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cmd_help_mcast_ch_info': (
        'MCast Kanal Info',
        'MCast channel info',
        'MCast kanaalinformatie',
        'Info canal MCAST',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cmd_help_mcast_channels': (
        'MCast Kanal Übersicht',
        'MCast channel overview',
        'MCast kanaaloverzicht',
        '',
        '',
        '',
        '',
        '',
        '',
        ''),  #

    'cmd_help_mcast_set_axip': (
        'Eigene AXIP Adresse eintragen / anzeigen lassen',
        'Enter/display your own AXIP address',
        'Voer/toon uw eigen AXIP-adres in',
        'Entrez/afficher votre adresse AXIP',
        '',
        '',
        '',
        '',
        '',
        ''),

    'mcast_new_user_beacon': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '-= Willkommen auf dem AXIP-MCast Server. Registriere dich auf {} =-',
        '-= Welcome to the AXIP-MCast Server. Please connect {} to register =-',
        '-= Welcome to the AXIP-MCast Server. Please connect {} to register =-',
        '-= Bienvenue sur le serveur AXIP-MCast. Veuillez vous connecter {} pour vous enregistrer =-',
        '',
        '',
        '',
        '',
        '',
        ''),

    'mcast_new_user_reg_beacon': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars) per Line
        # Max 256
        ('-= Du wurdest erfolgreich auf dem MCast-Server registriert =-\r'
         '-= Du befindest dich auf Kanal {} ({}) =-'),
        ('-= You have been successfully registered on the MCast server =-\r'
         '-= You are on channel {} ({}) =-'),
        ('-= U bent succesvol geregistreerd op de MCast-server. =-\r'
         '-= Je bevindt je op kanaal {} ({}) =-'),
        ('-= Vous avez été enregistré avec succès sur le serveur MCast =-\r'
         '-= Vous êtes sur le canal {} ({}) =-'),
        ('\r'
         ''),
        ('\r'
         ''),
        ('\r'
         ''),
        ('\r'
         ''),
        ('\r'
         ''),
        ''),

    'mcast_user_enters_channel_beacon': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '-= {} hat den Kanal betreten =-',
        '-= {} has entered the channel =-',
        '-= {} is het kanaal binnengekomen =-',
        '-= {} est arrivé sur le canal =-',
        '',
        '',
        '',
        '',
        '',
        ''),

    'mcast_user_left_channel_beacon': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '-= {} hat den Kanal verlassen =-',
        '-= {} has left the channel =-',
        '-= {} het kanaal verlaten =-',
        '-= {} a quité le canal',
        '',
        '',
        '',
        '',
        '',
        ''),

    #####################################################
    # BOX CLI
    'cmd_r': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '<MSG#> Liest die Nachricht mit der entspr. Nummer aus.',
        '<MSG#> Reads the message with the corresponding number.',
        '<MSG#> Leest het bericht met het bijbehorende nummer.',
        '<MSG#> lecture du message correspondant au numéro de message.',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cmd_sp': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        'SP <Call> @ <BBS> : Sendet eine persoenliche Nachricht an Rufzeichen',
        'SP <Call> @ <BBS> : Sends a personal message to call sign',
        'SP <Call> @ <BBS>: Stuurt een persoonlijk bericht naar roepnamen',
        'SP <Call> @ <BBS> : Envoie un message personnel à l\'indicatid',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cmd_sb': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        ('SB <Rubrik> @ <Verteiler> Sendet ein Bulletin in eine Rubrik \r'
         '              fuer mehrere Boxen in einer Region.'),
        ('SB <Category> @ <Distribution> Sends a bulletin to a category \r'
         '              for multiple boxes in a region.'),
        ('SB <categorie> @ <distributie> Stuurt een bulletin naar een categorie \r'
         '              voor meerdere dozen in een regio.'),
        ('SB <Catégorie> @ <Distribution> Envoie un bulletin a la categorie \r'
         '              pour plusieurs boites dans une région.'),
        '',
        '',
        '',
        '',
        '',
        ''),

    'cmd_ln': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        'Listet alle eigenen neuen Nachrichten auf.',
        'Lists all of your own new messages.',
        'Geeft al uw eigen nieuwe berichten weer.',
        'Liste tous vos nouveaux messages',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cmd_lm': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        'Listet alle eigenen Nachrichten.',
        'Lists all of your own messages.',
        'Geeft al uw eigen berichten weer.',
        'Liste tous vos messages',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cmd_ll': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '<Anzahl> Listet die neuesten Nachrichten in der ang. Zahl.',
        '<Number> Lists the latest news in the specified number.',
        '<nummer> Geeft de laatste berichten in het opgegeven nummer weer.',
        '<number> Répertorie les derniers messages dans le numéro spécifié.',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cmd_lb': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        'Listet alle Bulletin Nachrichten.',
        'Lists all bulletin messages.',
        'Geeft een overzicht van alle bulletinberichten.',
        'Liste tous les messages bulletins',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cmd_km': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        'Loescht alle pers. Nachrichten, die man bereits gelesen hat.',
        'Deletes all personal messages that you have already read.',
        'Verwijdert alle persoonlijke berichten die u al hebt gelezen.',
        'Supprime tous les messages personnels que vous avez déjà lus »,',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cmd_k': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '<MSG#> Loescht die Nachricht mit der entspr. Nummer.',
        '<MSG#> Deletes the message with the corresponding number.',
        '<MSG#> Verwijdert het bericht met het bijbehorende nummer.',
        '<MSG#> Supprime le message portant ce numéro',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cmd_op': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        'Anzahl der Zeilen pro Seite. Nur OP aus.',
        'Number of lines per page. Just OP = off.',
        'Aantal regels per pagina. OP alleen = uit',
        'Nombre de lignes par page. Juste OP = off.',
        '',
        '',
        '',
        '',
        '',
        ''),

    'op_prompt_0': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # (A)=Abbruch, (O)=weiter ohne Stop, (Return)=weiter -->',
        '\r # (A)=Cancel, (O)=continue without stopping, (Return)=continue -->',
        '\r # (A)=Annuleren, (O)=doorgaan zonder te stoppen, (Terug)=doorgaan -->',
        '\r # (A)=Annuler, (O)=continuer sans arrêt, (Return)=continuer -->',
        '',
        '',
        '',
        '',
        '',
        ''),

    'op_prompt_1': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # (A)=Abbruch, (R)=Lesen, (Return)=weiter -->',
        '\r # (A)=Cancel, (R)=Read, (Return)=continue -->',
        '\r # (A)=Annuleren, (R)=Lezen, (Terug)=doorgaan -->',
        '\r # (A)=Annuler, (R)=Lire, (Return)=continuer -->',
        '',
        '',
        '',
        '',
        '',
        ''),

    'box_new_mail_ctext': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r\r # BOX: Du hast {} neu Mails.\r\r',
        '\r\r # BOX : You have {} new mails.\r\r',
        '\r\r # BOX: Je hebt {} nieuwe mails.\r\r',
        '\r\r # BOX : Vous avez {} nouveaux mails.\r\r',
        '',
        '',
        '',
        '',
        '',
        ''),

    'box_cmd_op2': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # OP: Fehler, ungültiger Parameter.\r',
        '\r # OP : Error, Invalid Parameter.\r',
        '\r # OP: Fout, ongeldige parameter.\r',
        '\r # OP : Erreur, Paramètre Invalide.\r',
        '',
        '',
        '',
        '',
        '',
        ''),

    'box_cmd_op1': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # OP : Kein Seitenstop.\r',
        '\r # OP : No side stop.\r',
        '\r # OP: Geen zijstop.\r',
        '\r # OP :Pas de pagination.\r',
        '',
        '',
        '',
        '',
        '',
        ''),

    'box_cmd_op3': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # OP : Seitenstop auf {} Zeilen eingestellt.\r',
        '\r # OP : Page stop set to {} lines.\r',
        '\r # OP: Paginastop ingesteld op {} regels.\r',
        '\r # OP : Pagination de {} lignes.\r',
        '',
        '',
        '',
        '',
        '',
        ''),

    'box_lm_header': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        'Msg#  TSLD Byte   An    @ BBS   Von    Dat./Zeit Titel\r',
        'Msg#  TSLD Byte   To    @ BBS   From   Dat./Time Head\r',
        'Msg#  TSLD Byte   Naar  @ BBS   Van    Dat./Tijd Titel\r',
        'Msg#  TSLD Byte   Pour  @ BBS   De     Dat./Heure Titre\r',
        '',
        '',
        '',
        '',
        '',
        ''),

    'box_r_no_msg_found': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r\r # Nachricht {} nicht gefunden ! \r\r',
        '\r\r # Message {} not found! \r\r',
        '\r\r # Bericht {} niet gevonden! \r\r',
        '\r\r # Message {} non trouvé! \r\r',
        '',
        '',
        '',
        '',
        '',
        ''),

    'box_parameter_error': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # Fehler, ungültiger Parameter.\r',
        '\r # Error, Invalid Parameter.\r',
        '\r # Fout, ongeldige parameter.\r',
        '\r # Erreur, Paramètre invalide.\r',
        '',
        '',
        '',
        '',
        '',
        ''),

    'box_msg_error': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # Interner Fehler, kann Nachricht nicht lesen.\r',
        '\r # Internal error, cannot read message.\r',
        '\r # Interne fout, kan bericht niet lezen.\r',
        '\r # Erreur interne, impossible lire message.\r',
        '',
        '',
        '',
        '',
        '',
        ''),

    'box_msg_foter': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r\r--- Ende der Nachricht #{} an {} von {} BID:{} ---\r\r',
        '\r\r--- End of message #{} to {} from {} BID:{} ---\r\r',
        '\r\r--- Einde van bericht #{} tot {} van {} BID:{} ---\r\r',
        '\r\r--- Fin des messages #{} por {} de {} BID:{} ---\r\r',
        '',
        '',
        '',
        '',
        '',
        ''),

    'box_msg_del': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # Es wurden {} Nachrichten gelöscht.\r',
        '\r # {} messages have been deleted.\r',
        '\r # {} berichten zijn verwijderd.\r',
        '\r # {} messages ont été supprimés.\r',
        '',
        '',
        '',
        '',
        '',
        ''),

    'box_msg_del_k': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # Nachrichte(n) {} wurde(n) gelöscht.\r',
        '\r # Message(s) {} have been deleted.\r',
        '\r # Berichte(n) {} zijn verwijderd.\r',
        '\r # {} Message(s) supprimés.\r',
        '',
        '',
        '',
        '',
        '',
        ''),

    'box_error_no_address': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # Kein Empfänger angegeben. SP XX0XX oder SP XX0XX@XBBS0\r',
        '\r # No recipient specified. SP XX0XX or SP XX0XX@XBBS0.\r',
        '\r # Geen ontvanger opgegeven. SP XX0XX of SP XX0XX@XBBS0.\r',
        '\r # Pas de recipient specifié. SP XX0XX or SP XX0XX@XBBS0.\r',
        '',
        '',
        '',
        '',
        '',
        ''),

    'box_error_invalid_dist': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # Kein Verteiler in BBS-Adresse {}\r',
        '\r # No distribution list in BBS address {}\r',
        '\r # Geen distributeur in BBS-adres {}\r',
        '\r # Pas de liste de distribution dans l\'adresse BBS address {}\r',
        '',
        '',
        '',
        '',
        '',
        ''),

    'box_cmd_sp_routing_to': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        ('\r # Routing: {}\r'
         'Titel der Nachricht an {}:\r'),
        ('\r # Routing: {}\r'
         'Title of message to {}:\r'),
        ('\r # Routing: {}\r'
         'Berichttitel aan {}:\r'),
        ('\r # Routage : {}\r'
         'Title du message pour {}:\r'),
        '',
        '',
        '',
        '',
        '',
        ''),

    'box_cmd_sp_local': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        ('\r # Lokale Nachricht.\r'
         'Titel der Nachricht an {}:\r'),
        ('\r # Local message.\r'
         'Title of message to {}:\r'),
        ('\r # Lokaal bericht.\r'
         'Berichttitel aan {}:\r'),
        ('\r # Message local.\r'
         'Titre du message pour {}:\r')
        ,
        '',
        '',
        '',
        '',
        '',
        ''),

    'box_cmd_sp_enter_msg': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        'Text eingeben ... (Ende mit /EX oder Strg-Z):\r',
        'Enter text ... (End with /EX or Ctrl-Z):\r',
        'Tekst invoeren... (eindigen met /EX of Ctrl-Z):\r',
        'Entrez texte ... (Fin avec /EX ou Ctrl+z) : \r',
        '',
        '',
        '',
        '',
        '',
        ''),

    'box_cmd_sp_abort_msg': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # Nachricht fuer {} anulliert\r',
        '\r # Message for {} canceled\r',
        '\r # Bericht voor {} geannuleerd\r',
        '\r # Message pour {} annulé\r',
        '',
        '',
        '',
        '',
        '',
        ''),

    'box_cmd_sp_msg_accepted': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        ('\r # Ok. Nachricht an Adresse {} @ {} wird geforwardet.\r'
         '   via: {} MID: {} Bytes: {}\r\r'),
        ('\r # Ok. Message to address {} @ {} is being forwarded\r'
         '   via: {} Mid: {} Bytes: {}\r\r'),
        ('\r # Ok. Bericht wordt doorgestuurd naar adres {} @ {}\r'
         '   via: {} MID: {} Bytes: {}\r\r'),
        ('\r # Ok. Message à l\'adresse {} @ {} est en cours de forward\r'
         '   via: {} Mid: {} Bytes: {}\r\r')
        ,
        '',
        '',
        '',
        '',
        '',
        ''),

    'box_cmd_sp_msg_accepted_local': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        ('\r # Ok. Nachricht an Adresse {} bleibt lokal.\r'
         '   MID: {} Bytes: {}\r\r'),
        ('\r # Ok. Message to address {} remains local.\r'
         '   MID: {} Bytes: {}\r\r'),
        ('\r# Oké. Bericht aan adres {} blijft lokaal.\r'
         '   Mid: {} Bytes: {}\r\r'),
        ('\r# Ok. message à l\'adresse {} reste local.\r'
         '   Mid: {} Bytes: {}\r\r')
        ,
        '',
        '',
        '',
        '',
        '',
        ''),

    #####################################################
    # BOX GUI
    'own_station': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        'Eigene Station',
        'Own station',
        'Eigen station',
        'Ma station',
        '',
        '',
        '',
        '',
        '',
        ''),

    'region': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        'Region',
        'Region',
        'Regio',
        'Région',
        '',
        '',
        '',
        '',
        '',
        ''),

    'fwd_settings': (
        'Forward',
        'Forward',
        'Forward',
        'Forward',
        '',
        '',
        '',
        '',
        '',
        ''), #

    'fwd_port_settings': (
        'FWD-Port',
        'FWD-Port',
        'FWD-Port',
        'FWD-Port',
        '',
        '',
        '',
        '',
        '',
        ''),  # fwd_port_settings

    'routing_settings': (
        'Routing',
        'Routing',
        'Routing',
        'Routage',
        '',
        '',
        '',
        '',
        '',
        ''),

    'reject_settings': (
        'Reject/Hold',
        'Reject/Hold',
        'Reject/Hold',
        'Reject/Hold',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cc_settings': (
        'CC',
        'CC',
        'CC',
        'CC',
        '',
        '',
        '',
        '',
        '',
        ''),

    'swap_settings': (
        'SWAP',
        'SWAP',
        'SWAP',
        'SWAP',
        '',
        '',
        '',
        '',
        '',
        ''),

    'allowRevFWD': (
        'Erlaube Reverse-FWD',
        'Allow Reverse-FWD',
        'Sta Reverse-FWD toe',
        'Autoriser reverse FWD',
        '',
        '',
        '',
        '',
        '',
        ''),

    'allowPN_AutoPath': (
        'Erlaube PN AutoPath',
        'Allow PN AutoPath',
        'PN AutoPath toestaan',
        'Autorise PN-route auto',
        '',
        '',
        '',
        '',
        '',
        ''),

    'allowPN_AlterPath': (
        'PN-Alternativroute zulassen',
        'Allow PN alternative route',
        'Alternatieve PN-route toestaan',
        'Autoriser PN-route alternative',
        '',
        '',
        '',
        '',
        '',
        ''),

    'allow_PN_FWD': (
        'Privat Mail FWD zulassen',
        'Allow private mail FWD',
        'Sta het doorsturen van privémail toe',
        'Autoriser FWD mails privés',
        '',
        '',
        '',
        '',
        '',
        ''),

    'allow_BL_FWD': (
        'Bulletin Mail FWD zulassen',
        'Allow Bulletin mail FWD',
        'Doorsturen van bulletinmail toestaan',
        'Autoriser FWD mails bulletins',
        '',
        '',
        '',
        '',
        '',
        ''), #

    'conn_intervall': (
        'Abstände zwischen Connects (Minuten): ',
        'Intervals between connects (minutes): ',
        'Intervallen tussen verbindingen (minuten): ',
        'Intervalles entre les connexions (minutes): ',
        '',
        '',
        '',
        '',
        '',
        ''),  #

    'fwd_autoPath_help': (
        ('0  = deaktiviert\n'
         '1  = am aktuellsten\n'
         '2  = am besten (geringe Sprünge)'),
        ('0 = disabled\n'
         '1 = most recent\n'
         '2 = best (lowes hops)'),
        ('0 = uitgeschakeld\n'
         '1 = meest recente\n'
         '2 = beste (kleine sprongen)'),
        ('0 = désactivé\n'
         '1 = plus recent\n'
         '2 = Meilleurs (lowes hops)'),
        '',
        '',
        '',
        '',
        '',
        ''),

    'bbs_sett_fwd_global': (
        'Forwarding Global',
        'Forwarding Global',
        'Forwarding globaal',
        'Forward Global',
        '',
        '',
        '',
        '',
        '',
        ''),

    'bbs_sett_local_dist': (
        'Lokale Verteiler',
        'Local distributors',
        'Lokale distributeurs',
        'Distributeurs locaux',
        '',
        '',
        '',
        '',
        '',
        ''),

    'bbs_sett_local_theme': (
        'Lokale Bulletin Themen',
        'Local Bulletin Themes',
        'Lokale Bulletin thema s',
        'Théme bulletin local',
        '',
        '',
        '',
        '',
        '',
        ''),

    'bbs_sett_block_bbs': (
        'BBS blockieren',
        'Block BBS',
        'BBS blokkeren',
        'Bloquer BBS',
        '',
        '',
        '',
        '',
        '',
        ''),

    'bbs_sett_block_call': (
        'CALL blockieren',
        'Block CALL',
        'CALL blokkeren',
        'Bloquer CALL',
        '',
        '',
        '',
        '',
        '',
        ''),

    'bbs_sett_pn_bbs_out': (
        'Privat Mail > ausgehend',
        'Private mail > outgoing',
        'Privémail > uitgaand',
        'Mail Privé > sortant',
        '',
        '',
        '',
        '',
        '',
        ''),

    'bbs_sett_pn_bbs_in': (
        'Privat Mail > eingehend',
        'Private mail > incoming',
        'Privémail > inkomend',
        'Mail Privé > entrant',
        '',
        '',
        '',
        '',
        '',
        ''),

    'bbs_sett_bl_bbs_in': (
        'Bulletin Mail > eingehend',
        'Bulletin mail > incoming',
        'Bulletin mail > inkomend',
        'Mail Bulletin > entrant',
        '',
        '',
        '',
        '',
        '',
        ''),

    'bbs_sett_bl_bbs_out': (
        'Bulletin Mail > ausgehend',
        'Bulletin mail > outgoing',
        'Bulletin mail > uitgaand',
        'Mail Bulletin > sortant',
        '',
        '',
        '',
        '',
        '',
        ''),

    'read_ed': (
        'gelesen',
        'read',
        'lezen',
        'Lu',
        '',
        '',
        '',
        '',
        '',
        ''),

    'msgC_sendet_msg': (
        'Gesendet',
        'Sendet',
        'Verstuurd',
        'Envoyé',
        '',
        '',
        '',
        '',
        '',
        ''),

    'msgC_trash_bin': (
        'Papierkorb',
        'Trash',
        'Afval',
        'Poubelle',
        '',
        '',
        '',
        '',
        '',
        ''),

    'saved': (
        'Gespeichert',
        'Saved',
        'Opgeslagen',
        'Enregistré',
        '',
        '',
        '',
        '',
        '',
        ''),

    'private': (
        'Privat',
        'Private',
        'Privaat',
        'Privé',
        '',
        '',
        '',
        '',
        '',
        ''),

    #####################################################
    # guiHelpKeybinds.py
    'key_title': (
        'Tastaturbelegung',
        'Keyboard layout',
        'Toetsenbordindeling',
        'Racourcis clavier',
        '',
        '',
        '',
        '',
        '',
        '',
        ''),

    'key_esc': (
        'ESC > Neue Verbindung',
        'ESC > New connection',
        'ESC > Nieuwe verbinding',
        'ESC > Nouvelle connexion',
        '',
        '',
        '',
        '',
        '',
        '',
        ''),

    'key_altc': (
        'ALT + C > Neue Verbindung',
        'ALT + C > New connection',
        'ALT + C > Nieuwe verbinding',
        'ALT + C > Nouvelle connexion',
        '',
        '',
        '',
        '',
        '',
        '',
        ''),

    'key_altd': (
        'ALT + D > Disconnect',
        'ALT + D > Disconnect',
        'ALT + D > Ontkoppelen',
        'ALT + D > Déconnecter',
        '',
        '',
        '',
        '',
        '',
        '',
        ''),

    'key_f': (
        'F1 - F10 > Kanal 1 - 10',
        'F1 - F10 > Channel 1 - 10',
        'F1 - F10 > Kanal 1 - 10',
        'F1 - F10 > Canal 1 - 10',
        '',
        '',
        '',
        '',
        '',
        '',
        ''),

    'key_f12': (
        'F12 > Monitor',
        'F12 > Monitor',
        'F12 > Monitor',
        'F12 > Moniteur',
        '',
        '',
        '',
        '',
        '',
        '',
        ''),

    'key_strgplus': (
        'STRG + plus > Textgröße vergrößern',
        'CTRL + plus > Increase text size',
        'CTRL + plus > Tekst vergroten',
        'CTRL + plus > Augmente taille du texte',
        '',
        '',
        '',
        '',
        '',
        '',
        ''),

    'key_strgminus': (
        'STRG + minus > Textgröße verkleinern',
        'CTRL + minus > Reduce text size',
        'CTRL + min > Tekst verkleinen',
        'CTRL + plus > Réduit taille du texte',
        '',
        '',
        '',
        '',
        '',
        '',
        ''),

    'key_shiftf': (
        'SHIFT + F1 - F12 > Macro-Texte',
        'SHIFT + F1 - F12 > Macro texts',
        'SHIFT + F1 - F12 > Macro texts',
        'SHIFT + F1 - F12 > Texte Macro',
        '',
        '',
        '',
        '',
        '',
        '',
        ''),

    #####################################################
    # guiNewConnWin.py

    'newcon_title': (
        'Neue Verbindung',
        'New Connection',
        'Nieuwe verbinding',
        'Nouvelle connexion',
        '',
        '',
        '',
        '',
        '',
        '',
        ''),

    'newcon_ziel': (
        'Ziel:',
        'Target:',
        'streefcijfer:',
        'Cible :',
        '',
        '',
        '',
        '',
        '',
        '',
        ''),

    'newcon_history': (
        'Geschichte',
        'History:',
        'Geschiedenis:',
        'Historique',
        '',
        '',
        '',
        '',
        '',
        '',
        ''),
    #####################################################
    # guiBeaconSettings.py

    'scheduler': (
        'Scheduler',
        'Scheduler',
        'Scheduler',
        'Planificateur',
        '',
        '',
        '',
        '',
        '',
        '',
        ''),

    'type': (
        'Typ:',
        'Type:',
        'Typ:',
        'Type : ',
        '',
        '',
        '',
        '',
        '',
        '',
        ''),

    #####################################################
    # guiPoPT_Scheduler.py

    'week_day': (
        'Wochen tage',
        'Week days',
        'Week dagen:',
        'Jour de la semaine',
        '',
        '',
        '',
        '',
        '',
        '',
        ''),

    'month_day': (
        'Monats Tage',
        'Month days',
        'Maand dagen:',
        'Jour du mois',
        '',
        '',
        '',
        '',
        '',
        '',
        ''),
    'intervall_mn': (
        'Interval (mn): ',
        'Intervall (mn): ',
        'Interval (mn): ',
        'Intervalle (mn) : ',
        '',
        '',
        '',
        '',
        '',
        '',
        ''),

    'offset_sec': (
        'Versatz (sek): ',
        'Offset (sec): ',
        'Offset (sec): ',
        'Décalage (sec) : ',
        '',
        '',
        '',
        '',
        '',
        '',
        ''),

    'reset': (
        'Reset',
        'Reset',
        'Reset',
        'Reset',
        '',
        '',
        '',
        '',
        '',
        '',
        ''),

    'scheduler_set': (
        'Scheduler-Set',
        'Scheduler set',
        'Scheduler ingesteld',
        'Planificateur',
        '',
        '',
        '',
        '',
        '',
        '',
        ''),

    #####################################################
    # guiRxEchoSettings.py

    'echo_warning': (
        'Achtung! Diese Funktion ersetzt kein Digipeater!',
        'Attention! This function does not replace a digipeater!',
        'Let op! Deze functie vervangt geen digipeater!',
        'Attention ! Cette fonction ne remplace pas un digipeater !',
        '',
        '',
        '',
        '',
        '',
        '',
        ''),

}
