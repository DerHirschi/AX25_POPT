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
       '-= Welkom bij $ownCall ($distance km), =-\n'
       '-= Op Terminal-Kanaal $channel <> Poort $portNr. =-\n'
       '-= Dit is Connect Nr. $connNr. =-\n'
       '-= $ver - Max-Frame: $parmMaxFrame - Pac-Len: $parmPacLen =-\n'
       '\n'
       ' # Laatste Login op: $lastConnDate um: $lastConnTime\n'
       '\n'),
        # FR
        ('\n'
         '-= Bonjour $destName, =-\n'
         '-= bienvenue sur $ownCall ($distance km), =-\n'
         '-= sur le canal du terminal $channel <> Port $portNr. =-\n'
         '-= C\'est votre connexion nÂ° $connNr. =-\n'
         '-= $ver - Max-Frame : $parmMaxFrame - Pac-Len : $parmPacLen =-\n'
         '\n'
         ' # DerniÃ¨re connexion le : $lastConnDate Ã  : $lastConnTime\n'
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

    #################
    # BBS First user
    'bbs_new_user_reg0': (
        'Bitte Sprache wÃ¤hlen.\r',
        'Use this BBS as your home BBS? Y/N> ',
        'Deze BBS gebruiken als thuis-BBS? J/N> ',
        'Utiliser ce BBS comme BBS domestique ? O/N> ',
        '',
        '',
        '',
        '',
        '',
        ''),

    'bbs_new_user_reg_confirm': (
        'Mit <Enter> bestÃ¤tigen oder neu eingeben um zu Ã¤ndern.\r> ',
        'Press <Enter> to confirm or re-enter to change.\r>',
        'Druk op <Enter> om te bevestigen of druk nogmaals op enter om te wijzigen.\r>',
        'Appuyez sur <EntrÃ©e> pour confirmer ou appuyez Ã  nouveau pour modifier.\r>',
        '',
        '',
        '',
        '',
        '',
        ''),

    'bbs_new_user_reg1': (
        ('\r'
         'Das ist die 1. Verbindung mit diesem System.\r'
         'Bevor es weitergeht, bitte die Fragen beantworten. DANKE !\r'
         'Tip: Du musst dir das hier nicht antun, es gibt etwas dass\r'
         'nennt sich Internet.\r'
         '\r'
         'Vorname            :'),
        ('\r'
        'This is the first connection to this system.\r'
        'Before we continue, please answer the questions. THANK YOU!\r'
        "Tip: You don't have to put yourself through this, there's something called\r"
        'the Internet.\r'
        '\r'
        'First Name:'),
        ('\r'
         'Dit is de eerste verbinding met dit systeem.\r'
         'Voordat we verdergaan, wilt u alstublieft de vragen beantwoorden? BEDANKT!\r'
         'Tip: Je hoeft dit niet zelf te doen, er is iets dat\r'
         'wordt het internet genoemd.\r'
         '\r'
         'Voornaam :'),
        ('\r'
         "Il s'agit de la premiÃ¨re connexion Ã  ce systÃ¨me.\r"
         "Avant de continuer, veuillez rÃ©pondre aux questions. MERCI!\r"
         "Conseil : vous nâ€Ãªtes pas obligÃ© de vous infliger cela, il y a quelque chose qui\r"
         "s'appelle Internet.\r"
         '\r'
         'PrÃ©nom            :'),
        '',
        '',
        '',
        '',
        '',
        ''),

    'bbs_new_user_reg2_1': (
        'Ist {}\rnoch deine aktuelle Heimat-BBS ? J/N> ',
        'Is {}\rstill your current home BBS? Y/N> ',
        'Is {}\rnog steeds uw huidige thuis-BBS? J/N> ',
        'Est-ce que {}\rest toujours votre BBS personnel actuel? O/N> ',
        '',
        '',
        '',
        '',
        '',
        ''),

    'bbs_new_user_reg2_2': (
        'Dies BBS als Heimat-BBS Nutzen ? J/N> ',
        'Use this BBS as your home BBS? Y/N> ',
        'Deze BBS gebruiken als thuis-BBS? J/N> ',
        'Utiliser ce BBS comme BBS domestique ? O/N> ',
        '',
        '',
        '',
        '',
        '',
        ''),

    'bbs_new_user_reg3': (
        'Heimat-BBS         :',
        'Home-BBS           :',
        'Thuis BBS          :',
        'Accueil BBS        :',
        '',
        '',
        '',
        '',
        '',
        ''),

    'bbs_new_user_reg4': (
        ('\rDas hast du gut gemacht!\r\r'
         'Benutzerdaten von $destCall:\r'
         'Vorname   : {}\r'
         'Heimat-BBS: {}\r'
         'QTH       : {}\r'
         'Locator   : {}\r\r'),
        ('\rYou did well!\r\r'
            'User data of $destCall:\r'
            'First name: {}\r'
            'Home BBS  : {}\r'
            'QTH       : {}\r'
            'Locator   : {}\r\r'),
        ('Je hebt het goed gedaan!'
         'Gebruikersgegevens van $destCall:\r'
         'Voornaam: {}\r'
         'Home BBS: {}\r'
         'QTH     : {}\r'
         'Locator : {}\r\r'),
        ('\rTu as bien fait !\r\r'
         "DonnÃ©es utilisateur de $destCall:\r"
         'PrÃ©nom      : {}\r'
         'Accueil BBS : {}\r'
         'QTH         : {}\r'
         'Localisateur: {}\r\r'),
        '',
        '',
        '',
        '',
        '',
        ''),

    'bbs_new_user_error_hbbs_add': (
        '\r # Error, eingegebener Call ist keine BBS.\r # {} Typ ist als {} bekannt.\r # Bitte nochmal versuchen.\r\r',
        '\r # Error, entered call is not a BBS.\r # {} Type is known as {}.\r # Please try again.\r\r',
        '\r # Fout, ingevoerde oproep is geen BBS.\r # {} Type staat bekend als {}.\r # Probeer het opnieuw.\r\r',
        "\r # Erreur, l'appel saisi n'est pas un BBS.\r # {} Le type est connu comme {}.\r # Veuillez rÃ©essayer.\r\r",
        '',
        '',
        '',
        '',
        '',
        ''),

    'bbs_new_user_sysopMsg_top': (
        'Neue Benutzeranmeldung',
        'New user registration',
        'Registratie nieuwe gebruiker',
        "Inscription d'un nouvel utilisateur",
        '',
        '',
        '',
        '',
        '',
        ''),

    'bbs_new_user_sysopMsg_msg': (
        '{} hat sich soeben zum ersten mal auf {} connected.\nZeit: {}\n',
        '{} has just connected to {} for the first time.\nTime: {}\n',
        '{} heeft zojuist voor de eerste keer verbinding gemaakt met {}.\nTijd: {}\n',
        '{} vient de se connecter Ã  {} pour la premiÃ¨re fois.\nHeure: {}\n',
        '',
        '',
        '',
        '',
        '',
        ''),

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
        'TempÃ©rature',
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
        'HumiditÃ©',
        '',
        '',
        '',
        '',
        '',
        ''),

    'userdb_add_sysop_ent1': (
        'Informationen ergÃ¤nzen?',
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
        'EintrÃ¤ge vom Sysop ergÃ¤nzen ?',
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
        'Info: User Daten fÃ¼r {} wurden gespeichert..',
        'Info: User data for {} has been saved.',
        'Info: gebruikersgegevens voor {} zijn opgeslagen.',
        'DonnÃ©es utilisateur {} suvegardÃ©es',
        '',
        '',
        '',
        '',
        '',
        ''),

    'userdb_del_hint1': (
        'lÃ¶sche',
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
        'lÃ¶schen',
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
        'Nouvelle entrÃ©e',
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
        'FenÃªtre de prÃ©Ã©criture',
        '',
        '',
        '',
        '',
        '',
        ''),

    'call_vali_warning_1': (
        'Call Format!',
        'Call format!',
        'Call Format',
        'Format indicatif!',
        '',
        '',
        '',
        '',
        '',
        ''),

    'call_vali_warning_2': (
        'Max 6 Zeichen nur GroÃbuchstaben und Zahlen.',
        'Max 6 characters only capital letters and numbers.',
        'Max 6 karakters aleen Hoofdletters en nummers',
        'Max 6 caractÃ¨res, lettres majuscules et chiffresuniquement',
        '',
        '',
        '',
        '',
        '',
        ''),

    'del_station_hint': (
        'Hinweis: Station erfolgreich gelÃ¶scht.',
        'Note: Station deleted successfully.',
        'Opmerking: Zender is succesvol verwijderd.',
        'Note: station Ã©ffacÃ©e avec succÃ¨s',
        '',
        '',
        '',
        '',
        '',
        ''),

    'del_station_warning_1': (
        'Station gelÃ¶scht',
        'Station deleted',
        'Zender verwijderd',
        'Station Ã©ffacÃ©e',
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
        'Disque C a Ã©tÃ© formatÃ© avec succÃ¨s',
        '',
        '',
        '',
        '',
        '',
        ''),

    'del_station_hint_1': (
        'lÃ¶sche Station',
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
        'Willst du diese Station wirklich lÃ¶schen? \nAlle Einstellungen sowie Texte gehen verloren !',
        'Do you really want to delete this station? \nAll settings and texts will be lost!',
        'Wilt u deze zender echt verwijderen? \nAlle instellingen en teksten gaan verloren!',
        'Voulez vous vraiment supprimer cette station\n Tous les paramÃ¨tres et textes seront perdus',
        '',
        '',
        '',
        '',
        '',
        ''),

    'not_all_station_disco_hint_1': (
        'Stationen nicht disconnected',
        'Stations not disconnected',
        'Stations niet gedisconnect',
        'Stations non dÃ©connectÃ©es',
        '',
        '',
        '',
        '',
        '',
        ''),

    'not_all_station_disco_hint_2': (
        'Nicht alle Stationen disconnected!',
        'Not all stations are disconnected!',
        'Niet alle stations zijn gedisconnect',
        'Toutes les stations n\'ont pas Ã©tÃ© dÃ©connectÃ©es',
        '',
        '',
        '',
        '',
        '',
        ''),

    'all_station_get_disco_hint_1': (
        'Stationen werden disconnected !',
        'Stations getting disconnected!',
        'Stations worden gedisconnect',
        'Les stations se dÃ©connectent!',
        '',
        '',
        '',
        '',
        '',
        ''),

    'all_station_get_disco_hint_2': (
        'Es werden alle Stationen disconnected',
        'All stations getting disconnected',
        'Alle stations worden gedisconnect',
        'Toutes les stations sont dÃ©connectÃ©s',
        '',
        '',
        '',
        '',
        '',
        '',
        ''),

    'close_port': (
'Info: Versuche Port {} zu schlieÃen.',
           'Info: Try to close Port {}.',
           'info probeer poort te sluiten',
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
           'info: poort goed gesloten',
           'Info: Port {} fermÃ© avec succÃ¨s.',
           '',
           '',
           '',
           '',
           '',
           ''),

    'send_kiss_parm': (
'Hinweis: Kiss-Parameter an TNC auf Port {} gesendet..',
           'Note: Kiss parameters sent to TNC on port {}..',
           'Note: Kiss parameter gezonden naar TNC op poort{}..',
            'Note: ParamÃ¨tres KISS envoyÃ©s au TNC port {}...',
           '',
           '',
           '',
           '',
           '',
           ''),

    'port_in_use': ('Error: Port {} konnte nicht initialisiert werden. Port wird bereits benutzt.',
           'Error: Port {} could not be initialized. Port is already in use.',
           'Fout:Poort {} kan niet initialized. Poort is al in gebruik',
           'Erreur: Port {} ne peut Ãªtre initialisÃ©. Le port est dÃ©jÃ  en service',
           '',
           '',
           '',
           '',
           '',
           ''),

    'no_port_typ': (
'Hinweis: Kein Port-Typ ausgewÃ¤hlt. Port {}',
           'Note: No port type selected. port {}',
           'Note: geen poort type geselecteerd.poort {}',
           'Note: Aucun type de port sÃ©lÃ©ctionnÃ© port {}',
           '',
           '',
           '',
           '',
           '',
           ''),

    'port_not_init': (
        'Error: Port {} konnte nicht initialisiert werden.',
        'Error: Port {} could not be initialized.',
        'Fout: poort {}  kan niet initaliseerd worden',
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
        'Info: Poort{} geinitalezeerd succesvol',
        'Info: Port {} initialisÃ© avec succÃ¨s.',
        '',
        '',
        '',
        '',
        '',
        ''),

    'setting_saved': (
        'Info: {}-Einstellungen wurden gespeichert.',
        'Info: {}-Settings saved.',
        'instellingen opgeslagen',
        'Info: {}-paramÃ¨tres sauvegardÃ©s',
        '',
        '',
        '',
        '',
        '',
        ''),

    'all_port_reinit': (
        'Info: Ports werden reinitialisiert.',
        'Info: Ports are reinitialized.',
        'Info: poort geinitaliseerd',
        'Info: Ports rÃ©initialisÃ©s',
        '',
        '',
        '',
        '',
        '',
        ''),

    'port_reinit': (
        'Info: Port {} wird reinitialisiert.',
        'Info: Port {} is reinitialized.',
        'Info: Poort {}is geinitaliseerd',
        'Info: Port {} rÃ©initialisÃ©.',
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
        'Les stations sont dÃ©connectÃ©es!',
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
        'Toutes les stations sont dÃ©connectÃ©es',
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
        'AnnulÃ©',
        '',
        '',
        '',
        '',
        '',
        ''),

    'delete': (
        'LÃ¶schen',
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
        'DX-History LÃ¶schen',
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
        'Alles LÃ¶schen',
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
        'SchlieÃen',
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
        'RÃ©ponse',
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
        'Senden wenn Band frei fÃ¼r (sek.):',
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
        'GrÃ¶Ãe:',
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
        'Voulez vous dÃ©connecter toutes les sttions?',
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
        'Stations mÃ©tÃ©os',
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
        'KopiÃ«ren',
        'Copier',
        '',
        '',
        '',
        '',
        '',
        ''),

    'past': (
        'EinfÃ¼gen',
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
        'Aus Datei einfÃ¼gen',
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
        'Aus Datei einfÃ¼gen',
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
        'QSO/Vorschreibfenster lÃ¶schen',
        'Clear QSO/Prescription window',
        'QSO verwijderen',
        'Effacer QSO/fenÃªtre prÃ©redaction',
        '',
        '',
        '',
        '',
        '',
        ''),

    'clean_all_qso_win': (
        'Alle QSO/Vorschreibfenster lÃ¶schen',
        'Clear all QSO/Prescription window',
        'Alle QSO verwijderen',
        'Effacer tous QSO/fenÃªtres prÃ©redactions',
        '',
        '',
        '',
        '',
        '',
        ''),

    'clean_mon_win': (
        'Monitor lÃ¶schen',
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
        'QSO lÃ¶schen',
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
        'ParamÃ¨tres',
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
        'PasswÃ¶rter',
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
        'AntwortlÃ¤nge:',
        'Response length:',
        'Reactie lengte:',
        'Longueur rÃ©ponse :',
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
        'Ãber',
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
        'DÃ©but FWD',
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
        'DÃ©but FWD auto',
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
        'Centre des mÃ©ssages',
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
        'Couleur fenÃªtre QSO',
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
        'Couleur arriÃ¨re plan',
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
        'texte actualitÃ©s',
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
        'ParamÃ¨tres APRS',
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
        'Message APRS privÃ©s',
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
        'Messages privÃ©s',
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
        'GÃ©nÃ©ral',
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
        'Infos : paramÃ¨tres station enregistrÃ©s',
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
        'Ãloge : Vous vous Ãªtes trÃ¨s bien dÃ©brouillÃ©s !',
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
        'Ãloge : Vous avez bien travaillÃ© !',
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
        'Ãloge : C\'Ã©tait une bonne dÃ©cision. Continuez. Vous avez bien travaillÃ©,',
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
        'Ãloges : Vous n\'avez pas mÃ©ritÃ© d\'Ãªtre fÃ©licitÃ© aujourd\'hui.',
        '',
        '',
        '',
        '',
        '',
        ''),

    'lob5': (
        'Es tut mir leid, Dave. Ich fÃ¼rchte, das kann ich nicht.',
        "I'm sorry, Dave. I'm afraid I can't do that.",
        'Het spijt me, Dave. Ik ben bang dat ik dat niet kan.',
        'Je suis dÃ©solÃ©, Dave. J\'ai bien peur de ne pas pouvoir le faire ',
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
        'Geannuleerd!',
        'Note : AnnulÃ©',
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
        'offset',
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
        'ActivÃ©',
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
        'paramÃ¨tres Pipe-tools',
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
        'Pipe Ã  la connexion',
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
        'ParamÃ¨tres par dÃ©faut. UtilisÃ©s si non dÃ©finis (station/client)',
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
        'Pseudo TX delay (attente entre TX et RX si non dÃ©fini dans les paramÃ¨tres KISS du TNC',
        '',
        '',
        '',
        '',
        '',
        ''),

    'port_cfg_pac_len': (
        'Paket LÃ¤nge. 1 - 256',
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
        'Port Bezeichnung fÃ¼r MH und Monitor( Max: 4 ):',
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
        '!! Poort is niet geÃ¯nitialiseerd!!',
        '!! Port non initialisÃ©',
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
        'DerniÃ¨re trame',
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
        'DÃ©filement auto',
        '',
        '',
        '',
        '',
        '',
        ''),

    'msg_box_mh_delete': (
        'MH-Liste LÃ¶schen',
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
        'Komplette MH-Liste lÃ¶schen?',
        'Delete entire MH list?',
        'Volledige MH-lijst verwijderen?',
        'Supprimer la liste MH complÃ¨te',
        '',
        '',
        '',
        '',
        '',
        ''),

    'msg_box_delete_data': (
        'Daten LÃ¶schen',
        'Delete data',
        'Verwijder data',
        'Effacer donnÃ©es',
        '',
        '',
        '',
        '',
        '',
        ''),

    'msg_box_delete_data_msg': (
        'Alle Daten lÃ¶schen?',
        'Delete all data?',
        'Alle gegevens verwijderen?',
        'Effacer toutes les donnÃ©es',
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
        'DonnÃ©es',
        '',
        '',
        '',
        '',
        '',
        ''),

    'multicast_warning': (
        'Vorsicht bei Nodenanbindungen wie TNN. Verlinkungen mehrerer Noden via Multicast kann zu Problemen fÃ¼hren!',
        'Be careful with node connections like TNN. Linking multiple nodes via multicast can lead to problems!',
        'Voorzichtigmet nodeverbinding zoals TNN, verbinden meervoudige nodes via multicast kan leiden naar problemen!',
        'Soyez prudent avec les connexions de node comme TNN. La liaison de plusieurs nodes via la multidiffusion peut entraÃ®ner des problÃ¨mes Â»,',
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
        'Base de donnÃ©es utilisateur',
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
        'Stations mÃ©tÃ©o',
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
        'Obtenir l\'entrÃ©e dans la bdd des appels',
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
        ' # EntrÃ©e non trouvÃ© dans la BDD utilisateur!!',
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
        ' # Nom utilisateur dÃ©fini',
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
        ' # QTH dÃ©fini',
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
        ' # Locator dÃ©fini',
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
        ' # CP dÃ©fini',
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
        ' # Adresse PR-Mail dÃ©finie',
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
        ' # Adresse E-mail dÃ©finie',
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
        ' # HTTP dÃ©fini',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cli_text_encoding_no_param': (
        ' # Bitte ein Ã¤ senden. Bsp.: UM Ã¤.\r # Derzeitige Einstellung:',
        ' # Please send an Ã¤. Example: UM Ã¤.\r # Current setting:',
        ' # Stuur een  Ã¤. voorbeeld Ã¤.\r # Huidige instelling:',
        ' # Veuillez envoyer un Ã¤. Exemple : UM Ã¤.\r # RÃ©glage actuel :',
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
        'Encodage/decodage du texte dÃ©tectÃ© et paramÃ©trÃ© Ã  :',
        '',
        '',
        '',
        '',
        '',
        ''),

    'port_overview': (
        'Port Ãbersicht',
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
        'DurÃ©e connexion',
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
        'Automatisch Umlaut Erkennung. Ã¤ als Parameter. > UM Ã¤',
        'Automatic detection of text encoding. Ã¤ as a parameter. > UM Ã¤',
        'Automatische detectie van tekstcodering. Ã¤ als parameter. > UM Ã¤',
        'DÃ©tection automatique de l\'encodage du texte. Ã¤ comme paramÃ¨tre. > UM Ã¤',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cmd_help_lcstatus': (
        'Verbundene TerminalkanÃ¤le anzeigen (ausfÃ¼hrliche Version)',
        'Show connected terminal channels (detailed version)',
        'Toon aangesloten terminalkanalen (gedetailleerde versie)',
        'Afficher les terminal connectÃ©s (version dÃ©taillÃ©e)',
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
        'Aucune donnÃ©es mÃ©tÃ©os disponnible',
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
        'Pas de donnÃ©es Tracer disponnibles',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cli_change_language': (
        'Sprache Ã¤ndern.',
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
        'Sprache auf Deutsch geÃ¤ndert.',
        'Language changed to English.',
        'Taal veranderd naar Nederlands.',
        'Lange changÃ© pour FranÃ§ais',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cli_no_lang_param': (
        'Sprache nicht erkannt! MÃ¶gliche Sprachen: ',
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
        'Sysop appelÃ©',
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
        'Le Sysop a dÃ©jÃ  ete appelÃ©',
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
        '# UngÃ¼ltiger Ziel Call..',
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
        '# UngÃ¼ltige Port Angabe..',
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
        '# UngÃ¼ltiger Port..',
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
        'MCast Kanal Ãbersicht',
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
        ('-= Vous avez Ã©tÃ© enregistrÃ© avec succÃ¨s sur le serveur MCast =-\r'
         '-= Vous Ãªtes sur le canal {} ({}) =-'),
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
        '-= {} est arrivÃ© sur le canal =-',
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
        '-= {} a quitÃ© le canal',
        '',
        '',
        '',
        '',
        '',
        ''),

    #####################################################
    # BOX CLI
    'hint_no_mail_for': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # Keine Mails vorhanden: {}',
        '\r # No mails available: {}',
        '\r # Geen mails beschikbaar: {}',
        '\r # Aucun mail disponible: {}',
        '',
        '',
        '',
        '',
        '',
        ''),

    'hint_no_mail': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # Keine Mails vorhanden',
        '\r # No mails available',
        '\r # Geen mails beschikbaar',
        '\r # Aucun mail disponible',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cmd_r': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '<MSG#>: Liest die Nachricht mit der entspr. Nummer aus.',
        '<MSG#>: Reads the message with the corresponding number.',
        '<MSG#>: Leest het bericht met het bijbehorende nummer.',
        '<MSG#>: lecture du message correspondant au numÃ©ro de message.',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cmd_sp': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        'SP <Call> @ <BBS>: Sendet eine persoenliche Nachricht an Rufzeichen',
        'SP <Call> @ <BBS>: Sends a personal message to call sign',
        'SP <Call> @ <BBS>: Stuurt een persoonlijk bericht naar roepnamen',
        'SP <Call> @ <BBS>: Envoie un message personnel Ã  l\'indicatid',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cmd_sb': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        ('SB <Rubrik> @ <Verteiler>: Sendet ein Bulletin in eine Rubrik \r'
         '              fuer mehrere Boxen in einer Region.'),
        ('SB <Category> @ <Distribution>: Sends a bulletin to a category \r'
         '              for multiple boxes in a region.'),
        ('SB <categorie> @ <distributie>: Stuurt een bulletin naar een categorie \r'
         '              voor meerdere dozen in een regio.'),
        ('SB <CatÃ©gorie> @ <Distribution>: Envoie un bulletin a la categorie \r'
         '              pour plusieurs boites dans une rÃ©gion.'),
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
        '<Anzahl>: Listet die neuesten Nachrichten in der ang. Zahl.',
        '<Number>: Lists the latest news in the specified number.',
        '<nummer>: Geeft de laatste berichten in het opgegeven nummer weer.',
        '<number>: RÃ©pertorie les derniers messages dans le numÃ©ro spÃ©cifiÃ©.',
        '',
        '',
        '',
        '',
        '',
        ''), #

    'cmd_l_from': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '<CALL>: Listet Bulletins VON einem Rufzeichen.',
        '<CALL>: Lists bulletins FROM a callsign.',
        '<CALL>: Geeft een lijst met bulletins VAN een roepnaam.',
        "<CALL>: RÃ©pertorie les bulletins Ã€ PARTIR d'un indicatif d'appel.",
        '',
        '',
        '',
        '',
        '',
        ''),  #

    'cmd_l_to': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '<CALL/RUBRIK>: Listet Nachrichten AN ein Rufzeichen oder Rubrik.',
        '<CALL/RUBRIK>: Lists messages TO a call sign or heading.',
        '<CALL/RUBRIK>: Geeft een lijst weer van berichten NAAR een roepnaam of kop.',
        "<CALL/RUBRIK>: rÃ©pertorie les messages VERS un indicatif d'appel ou un titre.",
        '',
        '',
        '',
        '',
        '',
        ''),  #

    'cmd_l_at': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '<CALL>: Listet Bulletins VIA Verteiler.',
        '<CALL>: Lists bulletins VIA distribution.',
        '<CALL>: Geeft bulletins weer VIA distributielijst.',
        "<CALL>: RÃ©pertorie les bulletins VIA de distribution.",
        '',
        '',
        '',
        '',
        '',
        ''),  #

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
        'Supprime tous les messages personnels que vous avez dÃ©jÃ  lus Â»,',
        '',
        '',
        '',
        '',
        '',
        ''),

    'cmd_k': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '<MSG#>: Loescht die Nachricht mit der entspr. Nummer.',
        '<MSG#>: Deletes the message with the corresponding number.',
        '<MSG#>: Verwijdert het bericht met het bijbehorende nummer.',
        '<MSG#>: Supprime le message portant ce numÃ©ro',
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
        '\r # (A)=Annuler, (O)=continuer sans arrÃªt, (Return)=continuer -->',
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
        '\r # BOX: Du hast {} neu Mails.\r\r',
        '\r # BOX : You have {} new mails.\r\r',
        '\r # BOX: Je hebt {} nieuwe mails.\r\r',
        '\r # BOX : Vous avez {} nouveaux mails.\r\r',
        '',
        '',
        '',
        '',
        '',
        ''),

    'box_no_hbbs_address': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # Du hast noch keine Heimat-BBS eingetragen. PR <CALL.Verteiler>\r\r',
        "\r # You haven't entered a home BBS yet. PR <CALL.Distribution>>\r\r",
        '\r # U hebt nog geen thuis-BBS ingevoerd. PR <CALL.Distributie>\r\r',
        "\r # Vous n'avez pas encore entrÃ© de BBS personnel. PR <CALL.Distribution>\r\r",
        '',
        '',
        '',
        '',
        '',
        ''),

    'box_cmd_op2': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # OP: Fehler, ungÃ¼ltiger Parameter.\r',
        '\r # OP : Error, Invalid Parameter.\r',
        '\r # OP: Fout, ongeldige parameter.\r',
        '\r # OP : Erreur, ParamÃ¨tre Invalide.\r',
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
        '\r\r # Message {} non trouvÃ©! \r\r',
        '',
        '',
        '',
        '',
        '',
        ''),

    'box_parameter_error': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # Fehler, ungÃ¼ltiger Parameter.\r',
        '\r # Error, Invalid Parameter.\r',
        '\r # Fout, ongeldige parameter.\r',
        '\r # Erreur, ParamÃ¨tre invalide.\r',
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
        '\r # Es wurden {} Nachrichten gelÃ¶scht.\r',
        '\r # {} messages have been deleted.\r',
        '\r # {} berichten zijn verwijderd.\r',
        '\r # {} messages ont Ã©tÃ© supprimÃ©s.\r',
        '',
        '',
        '',
        '',
        '',
        ''),

    'box_msg_del_k': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # Nachrichte(n) {} wurde(n) gelÃ¶scht.\r',
        '\r # Message(s) {} have been deleted.\r',
        '\r # Berichte(n) {} zijn verwijderd.\r',
        '\r # {} Message(s) supprimÃ©s.\r',
        '',
        '',
        '',
        '',
        '',
        ''),

    'box_error_no_address': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # Kein EmpfÃ¤nger angegeben. SP XX0XX oder SP XX0XX@XBBS0\r',
        '\r # No recipient specified. SP XX0XX or SP XX0XX@XBBS0.\r',
        '\r # Geen ontvanger opgegeven. SP XX0XX of SP XX0XX@XBBS0.\r',
        '\r # Pas de recipient specifiÃ©. SP XX0XX or SP XX0XX@XBBS0.\r',
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
        '\r # Message pour {} annulÃ©\r',
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
        ('\r # Ok. Message Ã  l\'adresse {} @ {} est en cours de forward\r'
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
        ('\r# OkÃ©. Bericht aan adres {} blijft lokaal.\r'
         '   Mid: {} Bytes: {}\r\r'),
        ('\r# Ok. message Ã  l\'adresse {} reste local.\r'
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
        'RÃ©gion',
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

    'AutoMail_settings': (
        'Auto Mails',
        'Auto Mails',
        'Auto Mails',
        'Auto Mails',
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
        'Sta het doorsturen van privÃ©mail toe',
        'Autoriser FWD mails privÃ©s',
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
        'AbstÃ¤nde zwischen Connects (Minuten): ',
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
         '2  = am besten (geringe SprÃ¼nge)'),
        ('0 = disabled\n'
         '1 = most recent\n'
         '2 = best (lowes hops)'),
        ('0 = uitgeschakeld\n'
         '1 = meest recente\n'
         '2 = beste (kleine sprongen)'),
        ('0 = dÃ©sactivÃ©\n'
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
        'ThÃ©me bulletin local',
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
        'PrivÃ©mail > uitgaand',
        'Mail PrivÃ© > sortant',
        '',
        '',
        '',
        '',
        '',
        ''),

    'bbs_sett_pn_bbs_in': (
        'Privat Mail > eingehend',
        'Private mail > incoming',
        'PrivÃ©mail > inkomend',
        'Mail PrivÃ© > entrant',
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
        'EnvoyÃ©',
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
        'EnregistrÃ©',
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
        'PrivÃ©',
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
        'ALT + D > DÃ©connecter',
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
        'STRG + plus > TextgrÃ¶Ãe vergrÃ¶Ãern',
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
        'STRG + minus > TextgrÃ¶Ãe verkleinern',
        'CTRL + minus > Reduce text size',
        'CTRL + min > Tekst verkleinen',
        'CTRL + plus > RÃ©duit taille du texte',
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

}
