"""
'DE': 0,
'EN': 1,
'NL': 2,
'FR': 3,
'CZ': 4,
'PL': 5,
'PT': 6,
'IT': 7,
'RU': 8,
'UA': 9,

Thanks to NL1NOD(CB) Patrick for the Dutch translations.
Thanks to ClaudeMa(GitHub) for the France translations.
Thanks to CT1DRB(HAM) David for the Portuguese translations.
"""
from cfg.string_tab_SP import STR_TABLE_SP
from cfg.logger_config import logger

STR_TABLE = {
    #  GER
    #  ENG
    #  NL
    #  FR
    #  CZ
    #  PL
    #  PT
    #  IT
    #  RU
    #  UA
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
         '-= C\'est votre connexion n° $connNr. =-\n'
         '-= $ver - Max-Frame : $parmMaxFrame - Pac-Len : $parmPacLen =-\n'
         '\n'
         ' # Dernière connexion le : $lastConnDate à : $lastConnTime\n'
         '\n'),
        # CZ
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
         '-= Olá $destName, =-\n'
         '-= Bem-vindo a $ownCall ($distance km), =-\n'
         '-= no canal de terminal $channel <> Porta $portNr. =-\n'
         '-= É a ligação Nr. $connNr. =-\n'
         '-= $ver - Max-Frame: $parmMaxFrame - Pac-Len: $parmPacLen =-\n'
         '\n'
         ' # Última ligação em: $lastConnDate um: $lastConnTime\n'
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
    'Bitte Sprache wählen.\r',
    'Use this BBS as your home BBS? Y/N> ',
    'Deze BBS gebruiken als thuis-BBS? J/N> ',
    'Utiliser ce BBS comme BBS domestique ? O/N> ',
    'Vyberte prosím jazyk.\r',
    'Wybierz język.\r',
    'Por favor escolha a língua.\r',
    'Seleziona la lingua.\r',
    'Пожалуйста, выберите язык.\r',
    'Будь ласка, оберіть мову.\r'),

    'bbs_new_user_reg_confirm': (
        'Mit <Enter> bestätigen oder neu eingeben um zu ändern.\r> ',
        'Press <Enter> to confirm or re-enter to change.\r>',
        'Druk op <Enter> om te bevestigen of druk nogmaals op enter om te wijzigen.\r>',
        'Appuyez sur <Entrée> pour confirmer ou appuyez à nouveau pour modifier.\r>',
        'Stiskněte <Enter> pro potvrzení nebo znovu napište pro změnu.\r>',
        'Naciśnij <Enter> aby potwierdzić lub wpisz ponownie aby zmienić.\r>',
        'Carregue no <Enter> para confirmar ou escreva novamente para alterar.\r>',
        'Premi <Enter> per confermare o reinserisci per modificare.\r>',
        'Нажмите <Enter> для подтверждения или введите заново для изменения.\r>',
        'Натисніть <Enter> для підтвердження або введіть знову для зміни.\r>'),

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
         "Il s'agit de la première connexion à ce système.\r"
         "Avant de continuer, veuillez répondre aux questions. MERCI!\r"
         "Conseil : vous n’êtes pas obligé de vous infliger cela, il y a quelque chose qui\r"
         "s'appelle Internet.\r"
         '\r'
         'Prénom            :'),
        ('\r'
         'Toto je první připojení k tomuto systému.\r'
         'Než budeme pokračovat, odpovězte prosím na otázky. DĚKUJEME!\r'
         'Tip: Nemusíte tohle podstupovat, existuje něco, čemu se říká\r'
         'Internet.\r'
         '\r'
         'Jméno              :'),
        ('\r'
         'To jest pierwsze połączenie z tym systemem.\r'
         'Zanim przejdziemy dalej, proszę odpowiedzieć na pytania. DZIĘKUJEMY!\r'
         'Wskazówka: Nie musisz tego znosić, istnieje coś co nazywa się\r'
         'Internet.\r'
         '\r'
         'Imię               :'),
        ('\r'
         'Esta é a sua primeira ligação a este sistema.\r'
         'Antes de continuarmos, por favor responda às perguntas. OBRIGADO!\r'
         'Dica: Não precisa passar por isto, existe algo chamado\r'
         'Internet.\r'
         '\r'
         'Primeiro nome      :'),
        ('\r'
         'Questa è la prima connessione a questo sistema.\r'
         'Prima di continuare, rispondi alle domande. GRAZIE!\r'
         'Suggerimento: Non devi subire tutto questo, esiste qualcosa chiamato\r'
         'Internet.\r'
         '\r'
         'Nome               :'),
        ('\r'
         'Это первое подключение к системе.\r'
         'Прежде чем продолжить, пожалуйста ответьте на вопросы. СПАСИБО!\r'
         'Совет: Вам не обязательно это терпеть, есть такая вещь как\r'
         'Интернет.\r'
         '\r'
         'Имя                :'),
        ('\r'
         'Це перше підключення до цієї системи.\r'
         'Перш ніж продовжити, будь ласка, дайте відповіді на питання. ДЯКУЄМО!\r'
         'Порада: Вам не обов’язково це терпіти, є така річ як\r'
         'Інтернет.\r'
         '\r'
         'Ім’я               :')),

    'bbs_new_user_reg2_1': (
        'Ist {}\rnoch deine aktuelle Heimat-BBS ? J/N> ',
        'Is {}\rstill your current home BBS? Y/N> ',
        'Is {}\rnog steeds uw huidige thuis-BBS? J/N> ',
        'Est-ce que {}\rest toujours votre BBS personnelle actuelle? O/N> ',
        'Je {} \r stále vaše aktuální domovská BBS? A/N> ',
        'Czy {} \r jest nadal twoją aktualną BBS domową? T/N> ',
        '{} \r ainda é a sua BBS oficial? S/N> ',
        '{} \r è ancora la tua home BBS attuale? S/N> ',
        '{} \r всё ещё твоя домашняя BBS? Д/Н> ',
        '{} \r досі твоя домашня BBS? Т/Н> '),

    'bbs_new_user_reg2_2': (
        'Dies BBS als Heimat-BBS Nutzen ? J/N> ',
        'Use this BBS as your home BBS? Y/N> ',
        'Deze BBS gebruiken als thuis-BBS? J/N> ',
        'Utiliser cette BBS comme BBS domestique ? O/N> ',
        'Použít tuto BBS jako domovskou? A/N> ',
        'Użyć tej BBS jako BBS domowej? T/N> ',
        'Usar esta BBS como BBS pessoal? S/N> ',
        'Usare questa BBS come home BBS? S/N> ',
        'Использовать эту BBS как домашнюю? Д/Н> ',
        'Використовувати цю BBS як домашню? Т/Н> '),

    'bbs_new_user_reg3': (
        'Heimat-BBS         :',
        'Home-BBS           :',
        'Thuis-BBS          :',
        'Accueil-BBS        :',
        'Domovská BBS       :',
        'BBS domowa         :',
        'BBS oficial        :',
        'Home BBS           :',
        'Домашняя BBS       :',
        'Домашня BBS        :'),

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
         "Données utilisateur de $destCall:\r"
         'Prénom      : {}\r'
         'Accueil BBS : {}\r'
         'QTH         : {}\r'
         'Localisateur: {}\r\r'),
        ('\rVýborně jsi to zvládl!\r\r'
         'Uživatelská data $destCall:\r'
         'Jméno     : {}\r'
         'Dom. BBS  : {}\r'
         'QTH       : {}\r'
         'Locator   : {}\r\r'),
        ('\rDobra robota!\r\r'
         'Dane użytkownika $destCall:\r'
         'Imię      : {}\r'
         'BBS domowa: {}\r'
         'QTH       : {}\r'
         'Locator   : {}\r\r'),
        ('\rMuito bem!\r\r'
         'Dados do utilizador $destCall:\r'
         'Nome        : {}\r'
         'BBS oficial : {}\r'
         'QTH         : {}\r'
         'Locator     : {}\r\r'),
        ('\rHai fatto un ottimo lavoro!\r\r'
         'Dati utente di $destCall:\r'
         'Nome      : {}\r'
         'Home BBS  : {}\r'
         'QTH       : {}\r'
         'Locator   : {}\r\r'),
        ('\rМолодец!\r\r'
         'Данные пользователя $destCall:\r'
         'Имя       : {}\r'
         'Дом. BBS  : {}\r'
         'QTH       : {}\r'
         'Локатор   : {}\r\r'),
        ('\rМолодець!\r\r'
         'Дані користувача $destCall:\r'
         'Ім’я      : {}\r'
         'Дом. BBS  : {}\r'
         'QTH       : {}\r'
         'Локатор   : {}\r\r')),

    'bbs_new_user_error_hbbs_add': (
        '\r # Error, eingegebener Call ist keine BBS.\r # {} Typ ist als {} bekannt.\r # Bitte nochmal versuchen.\r\r',
        '\r # Error, entered call is not a BBS.\r # {} Type is known as {}.\r # Please try again.\r\r',
        '\r # Fout, ingevoerde oproep is geen BBS.\r # {} Type staat bekend als {}.\r # Probeer het opnieuw.\r\r',
        "\r # Erreur, l'indicatif saisi n'est pas une BBS.\r # {} Le type est connu comme {}.\r # Veuillez réessayer.\r\r",
        '\r # Chyba, zadaný call není BBS.\r # {} Typ je znám jako {}.\r # Zkuste to prosím znovu.\r\r',
        '\r # Błąd, podany call nie jest BBS.\r # {} Typ znany jako {}.\r # Spróbuj ponownie.\r\r',
        '\r # Erro, o indicativo inserido não é uma BBS.\r # {} Tipo conhecido como {}.\r # Tente novamente.\r\r',
        '\r # Errore, il call inserito non è una BBS.\r # {} Tipo noto come {}.\r # Riprova.\r\r',
        '\r # Ошибка, введённый call не является BBS.\r # {} Тип известен как {}.\r # Попробуйте ещё раз.\r\r',
        '\r # Помилка, введений call не є BBS.\r # {} Тип відомий як {}.\r # Спробуйте ще раз.\r\r'),

    'bbs_new_user_sysopMsg_top': (
        'Neue Benutzeranmeldung',
        'New user registration',
        'Registratie nieuwe gebruiker',
        "Inscription d'un nouvel utilisateur",
        'Registrace nového uživatele',
        'Rejestracja nowego użytkownika',
        'Novo registo de utilizador',
        'Nuova registrazione utente',
        'Регистрация нового пользователя',
        'Реєстрація нового користувача'),

    'bbs_new_user_sysopMsg_msg': (
        '{} hat sich soeben zum ersten mal auf {} connected.\nZeit: {}\n',
        '{} has just connected to {} for the first time.\nTime: {}\n',
        '{} heeft zojuist voor de eerste keer verbinding gemaakt met {}.\nTijd: {}\n',
        '{} vient de se connecter à {} pour la première fois.\nHeure: {}\n',
        '{} se právě poprvé připojil k {}.\nČas: {}\n',
        '{} właśnie połączył się po raz pierwszy z {}.\nCzas: {}\n',
        '{} acabou de ligar {} pela primeira vez.\nHora: {}\n',
        '{} si è appena connesso per la prima volta a {}.\nOra: {}\n',
        '{} только что впервые подключился к {}.\nВремя: {}\n',
        '{} щойно вперше підключився до {}.\nЧас: {}\n'),

    'language': (
        'Sprache',
        'Language',
        'Taal',
        'Langues',
        'Jazyk',
        'Język',
        'Língua',
        'Lingua',
        'Язык',
        'Мова'),

    'temperature': (
        'Temperatur',
        'Temperature',
        'Temperatuur',
        'Température',
        'Teplota',
        'Temperatura',
        'Temperatura',
        'Temperatura',
        'Температура',
        'Температура'),

    'wx_press': (
        'Luftdruck',
        'Pressure',
        'Luchtdruk',
        'Pression',
        'Tlak vzduchu',
        'Ciśnienie',
        'Pressão',
        'Pressione',
        'Давление',
        'Тиск'),

    'wx_hum': (
        'Luftfeuchtigkeit',
        'Humidity',
        'Vochtigheid',
        'Humidité',
        'Vlhkost vzduchu',
        'Wilgotność',
        'Humidade',
        'Umidità',
        'Влажность',
        'Вологість'),

    #################################################
    # guiUserDB.py
    'userdb_add_sysop_ent1': (
        'Informationen ergänzen?',
        'Add information?',
        'Informatie toevoegen?',
        'Ajouter information?',
        'Doplňit informace?',
        'Dodać informacje?',
        'Adicionar informação?',
        'Aggiungere informazioni?',
        'Дополнить информацию?',
        'Доповнити інформацію?'),

    'userdb_add_sysop_ent2': (
        'Einträge vom Sysop ergänzen ?',
        'Add information from the sysop?',
        'Informatie uit de sysop toevoegen?',
        'Ajouter information sur le sysop?',
        'Doplňit údaje od Sysopa?',
        'Dodać informacje od Sysopa?',
        'Adicionar informação do Sysop?',
        'Aggiungere dati dal Sysop?',
        'Добавить данные от сисопа?',
        'Додати дані від сисопа?'),

    'userdb_save_hint': (
        'Info: User Daten für {} wurden gespeichert..',
        'Info: User data for {} has been saved.',
        'Info: gebruikersgegevens voor {} zijn opgeslagen.',
        'Données utilisateur {} suvegardées',
        'Info: Uživatelská data pro {} byla uložena.',
        'Info: Dane użytkownika {} zostały zapisane.',
        'Info: Dados do utilizador {} foram guardados.',
        'Info: Dati utente per {} salvati.',
        'Инфо: Данные пользователя {} сохранены.',
        'Інфо: Дані користувача {} збережено.'),

    'userdb_del_hint1': (
        '{} löschen ?',
        'delete {}?',
        '{} verwijderen ?',
        '{} effacer ?',
        'Smazat {}?',
        'Usunąć {}?',
        'Eliminar {}?',
        'Eliminare {}?',
        'Удалить {}?',
        'Видалити {}?'),

    'userdb_del_hint2': (
        '{} wirklich löschen ?',
        '{} really delete?',
        '{} echt verwijderen?',
        '{} vraiment supprimer ?',
        'Opravdu smazat {}?',
        'Na pewno usunąć {}?',
        'Eliminar de vez {}?',
        'Eliminare davvero {}?',
        'Действительно удалить {}?',
        'Дійсно видалити {}?'),

    'userdb_del_hint2_1': (
        '{} Einträge löschen ?',
        'Delete {} entries?',
        '{} Items verwijderen?',
        'Supprimer {} entrées ?',
        'Smazat {} záznamů?',
        'Usunąć {} wpisów?',
        'Eliminar {} entradas?',
        'Eliminare {} voci?',
        'Удалить {} записей?',
        'Видалити {} записів?'),

    'userdb_del_hint2_2': (
        'Wirklich alle {} Einträge löschen ?',
        'Really delete all {} entries?',
        'Wilt u alle {} vermeldingen echt verwijderen?',
        'Supprimer vraiment les {} entrées ?',
        'Opravdu smazat všech {} záznamů?',
        'Na pewno usunąć wszystkie {} wpisy?',
        'De facto eliminar todas as {} entradas?',
        'Eliminare davvero tutte le {} voci?',
        'Действительно удалить все {} записей?',
        'Дійсно видалити всі {} записів?'),

    'userdb_newUser': (
        'Neuer Eintrag',
        'New entry',
        'Nieuwe invoer',
        'Nouvelle entrée',
        'Nový záznam',
        'Nowy wpis',
        'Nova entrada',
        'Nuova voce',
        'Новая запись',
        'Новий запис'),

    'prewritewin': (
        'Vorschreibfenster',
        'Prewriting window',
        'Voorschrijfvenster',
        'Fenêtre de préécriture',
        'Okno předpsaní',
        'Okno wstępnego pisania',
        'Janela de pré escrita',
        'Finestra di pre-scrittura',
        'Окно предварительной записи',
        'Вікно попереднього написання'),

    'consol_log': (
        'Logausgabe in der Konsole',
        'Log output in the console',
        'Logboekuitvoer in de console',
        'Consignez la sortie dans la console',
        'Výstup logu do konzole',
        'Wyjście logu w konsoli',
        'Saída de log na consola',
        'Output log nella console',
        'Вывод лога в консоль',
        'Вивід логу в консоль'),

    'call_vali_warning_1': (
        'Call Format!',
        'Call format!',
        'Call Format',
        'Format indicatif!',
        'Formát Callu!',
        'Nieprawidłowy format Call!',
        'Formato do indicativo!',
        'Formato Call!',
        'Формат Call!',
        'Формат Call!'),

    'call_vali_warning_2': (
        'Max 6 Zeichen nur Großbuchstaben und Zahlen.',
        'Max 6 characters only capital letters and numbers.',
        '',
        'Max 6 caractères, lettres majuscules et chiffres uniquement',
        'Max. 6 znaků, pouze velká písmena a čísla.',
        'Max 6 znaków, tylko wielkie litery i cyfry.',
        'Máx. 6 caracteres, apenas letras maíusculas e números.',
        'Max 6 caratteri, solo lettere maiuscole e numeri.',
        'Макс. 6 символов, только заглавные буквы и цифры.',
        'Макс. 6 символів, тільки великі літери та цифри.'),

    'del_station_hint': (
        'Hinweis: Station erfolgreich gelöscht.',
        'Note: Station deleted successfully.',
        'Opmerking: Zender is succesvol verwijderd.',
        'Note: station éffacée avec succès',
        'Poznámka: Stanice byla úspěšně smazána.',
        'Uwaga: Stacja została pomyślnie usunięta.',
        'Nota: Estação eliminada com sucesso.',
        'Nota: Stazione eliminata con successo.',
        'Примечание: Станция успешно удалена.',
        'Примітка: Станцію успішно видалено.'),

    'del_station_warning_1': (
        'Station gelöscht',
        'Station deleted',
        'Zender verwijderd',
        'Station éffacée',
        'Stanice smazána',
        'Stacja usunięta',
        'Estação eliminada',
        'Stazione eliminata',
        'Станция удалена',
        'Станцію видалено'),

    'del_station_warning_2': (
        'Laufwerk C: wurde erfolgreich formatiert.',
        'Drive C: was successfully formatted.',
        'Schijf C: is succesvol geformatteerd.',
        'Disque C a été formaté avec succès',
        'Disk C: byl úspěšně naformátován.',
        'Dysk C: został pomyślnie sformatowany.',
        'Drive C: foi formatada com sucesso.',
        'Disco C: è stato formattato con successo.',
        'Диск C: успешно отформатирован.',
        'Диск C: успішно відформатовано.'),

    'del_station_hint_1': (
        'lösche Station',
        'delete Station',
        '',
        'éffacer station',
        'smazat stanici',
        'usuń stację',
        'apagar estação',
        'elimina stazione',
        'удалить станцию',
        'видалити станцію'),

    'del_station_hint_2': (
        'Willst du diese Station wirklich löschen? \nAlle Einstellungen sowie Texte gehen verloren !',
        'Do you really want to delete this station? \nAll settings and texts will be lost!',
        'Wilt u deze zender echt verwijderen? \nAlle instellingen en teksten gaan verloren!',
        'Voulez vous vraiment supprimer cette station\n Tous les paramètres et textes seront perdus',
        'Opravdu chcete smazat tuto stanici? \nVšechna nastavení a texty budou ztraceny!',
        'Czy na pewno chcesz usunąć tę stację? \nWszystkie ustawienia i teksty zostaną utracone!',
        'Deseja realmente eliminar esta estação? \nTodas as configurações e textos serão perdidos!',
        'Vuoi davvero eliminare questa stazione? \nTutte le impostazioni e i testi andranno persi!',
        'Вы действительно хотите удалить эту станцию? \nВсе настройки и тексты будут потеряны!',
        'Ви дійсно хочете видалити цю станцію? \nВсі налаштування та тексти буде втрачено!'),

    'not_all_station_disco_hint_1': (
        'Stationen nicht disconnected',
        'Stations not disconnected',
        'Stations niet gedisconnect',
        'Stations non déconnectées',
        'Stanice nejsou odpojeny',
        'Nie wszystkie stacje rozłączone',
        'Estações não desligadas',
        'Stazioni non disconnesse',
        'Не все станции отключены',
        'Не всі станції відключені'),

    'not_all_station_disco_hint_2': (
        'Nicht alle Stationen disconnected!',
        'Not all stations are disconnected!',
        'Niet alle stations zijn gedisconnect',
        'Toutes les stations n\'ont pas été déconnectées',
        'Ne všechny stanice jsou odpojeny!',
        'Nie wszystkie stacje zostały rozłączone!',
        'Nem todas as estações foram desligadas!',
        'Non tutte le stazioni sono disconnesse!',
        'Не все станции отключены!',
        'Не всі станції відключені!'),

    'all_station_get_disco_hint_1': (
        'Stationen werden disconnected !',
        'Stations getting disconnected!',
        'Stations worden gedisconnect',
        'Les stations se déconnectent!',
        'Stanice se odpojují!',
        'Stacje są rozłączane!',
        'Estações a serem desligadas!',
        'Le stazioni vengono disconnesse!',
        'Станции отключаются!',
        'Станції відключаються!'),

    'all_station_get_disco_hint_2': (
        'Es werden alle Stationen disconnected',
        'All stations getting disconnected',
        'Alle stations worden gedisconnect',
        'Toutes les stations sont déconnectées',
        'Všechny stanice se odpojují',
        'Wszystkie stacje są rozłączane',
        'Todas as estações serão desligadas',
        'Tutte le stazioni vengono disconnesse',
        'Все станции отключаются',
        'Всі станції відключаються'),

    'close_port': (
        'Info: Versuche Port {} zu schließen.',
        'Info: Try to close Port {}.',
        'info probeer poort te sluiten',
        'Info: Tentative de fermeture du Port {}.',
        'Info: Pokus o uzavření portu {}.',
        'Info: Próba zamknięcia portu {}.',
        'Info: A tentar fechar a porta {}.',
        'Info: Tentativo di chiudere la porta {}.',
        'Инфо: Попытка закрыть порт {}.',
        'Інфо: Спроба закрити порт {}.'),

    'port_closed': (
        'Info: Port {} erfolgreich geschlossen.',
        'Info: Port {} closed successfully.',
        'info: poort goed gesloten',
        'Info: Port {} fermé avec succès.',
        'Info: Port {} úspěšně uzavřen.',
        'Info: Port {} zamknięty pomyślnie.',
        'Info: Porta {} fechada com sucesso.',
        'Info: Porta {} chiusa con successo.',
        'Инфо: Порт {} успешно закрыт.',
        'Інфо: Порт {} успішно закрито.'),

    'send_kiss_parm': (
        'Hinweis: Kiss-Parameter an TNC auf Port {} gesendet..',
        'Note: Kiss parameters sent to TNC on port {}..',
        'Note: Kiss parameter gezonden naar TNC op poort{}..',
        'Note: Paramètres KISS envoyés au TNC port {}...',
        'Pozn.: Kiss-parametry odeslány na TNC portu {}.',
        'Uwaga: Parametry KISS wysłane do TNC na porcie {}.',
        'Nota: Parâmetros KISS enviados para TNC na porta {}.',
        'Nota: Parametri KISS inviati al TNC sulla porta {}.',
        'Примечание: Параметры KISS отправлены на TNC порта {}.',
        'Примітка: Параметри KISS надіслано на TNC порту {}.'),

    'port_in_use': (
        'Error: Port {} konnte nicht initialisiert werden. Port wird bereits benutzt.',
        'Error: Port {} could not be initialized. Port is already in use.',
        'Fout:Poort {} kan niet initialized. Poort is al in gebruik',
        'Erreur: Port {} ne peut être initialisé. Le port est déjà en service',
        'Chyba: Port {} nelze inicializovat. Port je již používán.',
        'Błąd: Nie można zainicjować portu {}. Port jest już w użyciu.',
        'Erro: Não foi possível inicializar a porta {}. Porta em uso.',
        'Errore: Impossibile inizializzare la porta {}. Porta già in uso.',
        'Ошибка: Не удалось инициализировать порт {}. Порт уже используется.',
        'Помилка: Не вдалося ініціалізувати порт {}. Порт вже використовується.'),

    'no_port_typ': (
        'Hinweis: Kein Port-Typ ausgewählt. Port {}',
        'Note: No port type selected. port {}',
        'Note: geen poort type geselecteerd.poort {}',
        'Note: Aucun type de port séléctionné port {}',
        'Pozn.: Není vybrán typ portu. Port {}',
        'Uwaga: Nie wybrano typu portu. Port {}',
        'Nota: Nenhum tipo de porta selecionado. Porta {}',
        'Nota: Nessun tipo di porta selezionato. Porta {}',
        'Примечание: Не выбран тип порта. Порт {}',
        'Примітка: Не вибрано тип порту. Порт {}'),

    'port_not_init': (
        'Error: Port {} konnte nicht initialisiert werden.',
        'Error: Port {} could not be initialized.',
        'Fout: poort {}  kan niet initaliseerd worden',
        'Erreur: Initialisation port {} impossible.',
        'Chyba: Port {} nelze inicializovat.',
        'Błąd: Nie można zainicjować portu {}.',
        'Erro: Não foi possível inicializar a porta {}.',
        'Errore: Impossibile inizializzare la porta {}.',
        'Ошибка: Не удалось инициализировать порт {}.',
        'Помилка: Не вдалося ініціалізувати порт {}.'),

    'port_init': (
        'Info: Port {} erfolgreich initialisiert.',
        'Info: Port {} initialized successfully.',
        'Info: Poort{} geinitalezeerd succesvol',
        'Info: Port {} initialisé avec succès.',
        'Info: Port {} úspěšně inicializován.',
        'Info: Port {} pomyślnie zainicjowany.',
        'Info: Porta {} inicializada com sucesso.',
        'Info: Porta {} inizializzata con successo.',
        'Инфо: Порт {} успешно инициализирован.',
        'Інфо: Порт {} успішно ініціалізовано.'),

    'setting_saved': (
        'Info: {}-Einstellungen wurden gespeichert.',
        'Info: {}-Settings saved.',
        'instellingen opgeslagen',
        'Info: {}-paramètres sauvegardés',
        'Info: Nastavení {} bylo uloženo.',
        'Info: Ustawienia {} zostały zapisane.',
        'Info: Configurações de {} foram salvas.',
        'Info: Impostazioni {} salvate.',
        'Инфо: Настройки {} сохранены.',
        'Інфо: Налаштування {} збережено.'),

    'all_port_reinit': (
        'Info: Ports werden reinitialisiert.',
        'Info: Ports are reinitialized.',
        'Info: poort geinitaliseerd',
        'Info: Ports réinitialisés',
        'Info: Porty se reinicializují.',
        'Info: Porty są reinicjalizowane.',
        'Info: Portas serão reinicializadas.',
        'Info: Porte in fase di reinizializzazione.',
        'Инфо: Порты переинициализируются.',
        'Інфо: Порти переініціалізуються.'),

    'port_reinit': (
        'Info: Port {} wird reinitialisiert.',
        'Info: Port {} is reinitialized.',
        'Info: Poort {}is geinitaliseerd',
        'Info: Port {} réinitialisé.',
        'Info: Port {} se reinicializuje.',
        'Info: Port {} jest reinicjalizowany.',
        'Info: Porta {} está a ser reinicializada.',
        'Info: Porta {} in reinizializzazione.',
        'Инфо: Порт {} переинициализируется.',
        'Інфо: Порт {} переініціалізується.'),

    'all_disco1': (
        'Stationen werden disconnected !',
        'Stations are disconnected!',
        'Stations zijn losgekoppeld!',
        'Les stations sont déconnectées!',
        'Stanice se odpojují!',
        'Stacje są rozłączane!',
        'As estações estão a ser desligadas!',
        'Le stazioni vengono disconnesse!',
        'Станции отключаются!',
        'Станції відключаються!'),

    'all_disco2': (
        'Es werden alle Stationen disconnected',
        'All stations are disconnected',
        'Alle stations zijn losgekoppeld',
        'Toutes les stations sont déconnectées',
        'Všechny stanice se odpojují',
        'Wszystkie stacje są rozłączane',
        'Todas as estações estão a ser desligadas',
        'Tutte le stazioni vengono disconnesse',
        'Все станции отключаются',
        'Всі станції відключаються'),

    'OK': (
        'OK',
        'OK',
        'OK',
        'OK',
        'OK',
        'OK',
        'OK',
        'OK',
        'OK',
        'OK'),

    'cancel': (
        'Abbrechen',
        'Cancel',
        'Onderbreken',
        'Annuler',
        'Zrušit',
        'Anuluj',
        'Cancelar',
        'Annulla',
        'Отмена',
        'Скасувати'),

    'aborted': (
        'Abgebrochen',
        'Aborted',
        'Onderbroken',
        'Annulé',
        'Zrušeno',
        'Przerwano',
        'Cancelado',
        'Annullato',
        'Прервано',
        'Скасовано'),

    'delete': (
        'Löschen',
        'Delete',
        'Verwijder',
        'Effacer',
        'Smazat',
        'Usuń',
        'Eliminar',
        'Elimina',
        'Удалить',
        'Видалити'),

    'next': (
        'Weiter',
        'Next',
        'Volgende',
        'Plus loin',
        'Další',
        'Dalej',
        'Seguinte',
        'Avanti',
        'Далее',
        'Далі'),

    'back': (
        'Zurück',
        'Back',
        'Rug',
        'Dos',
        'Zpět',
        'Wstecz',
        'Voltar',
        'Indietro',
        'Назад',
        'Назад'),

    'delete_selected': (
        'Auswahl löschen',
        'Delete selection',
        'Selectie verwijderen',
        'Supprimer la sélection',
        'Smazat výběr',
        'Usuń zaznaczone',
        'Eliminar seleção',
        'Elimina selezione',
        'Удалить выбранное',
        'Видалити вибране'),

    'add': (
        'Hinzufügen',
        'Add',
        'Toevoegen',
        'Ajouter',
        'Přidat',
        'Dodaj',
        'Adicionar',
        'Aggiungi',
        'Добавить',
        'Додати'),

    'activate': (
        'Aktivieren',
        'Activate',
        'Activeren',
        'Activer',
        'Aktivovat',
        'Aktywuj',
        'Ativar',
        'Attiva',
        'Активировать',
        'Активувати'),

    'delete_mh_history': (
        'MH-Liste Löschen',
        'Delete MH-List',
        'MH-lijst verwijderen',
        "Supprimer la liste MH",
        'Smazat MH seznam',
        'Usuń listę MH',
        'Eliminar lista MH',
        'Elimina lista MH',
        'Удалить список MH',
        'Видалити список MH'),

    'delete_dx_history': (
        'DX-Alarm Verlauf Löschen',
        'Delete DX-Alarm History',
        'Verwijder DX-Alarm History',
        "Effacer l'historique DX-Alarm",
        'Smazat historii DX-Alarm',
        'Usuń historię DX-Alarm',
        'Eliminar histórico dos alarmes de DX',
        'Elimina cronologia DX-Alarm',
        'Удалить историю DX-Alarm',
        'Видалити історію DX-Alarm'),

    'delete_tracer_history': (
        'Tracer-Verlauf Löschen',
        'Delete Trace-History',
        'Verwijder Tracer-History',
        "Effacer l'historique Tracer",
        'Smazat historii Tracer',
        'Usuń historię Tracer',
        'Eliminar histórico Tracer',
        'Elimina cronologia Tracer',
        'Удалить историю Tracer',
        'Видалити історію Tracer'),

    'delete_conn_history': (
        'Verbindungsverlauf löschen',
        'Delete Connection-History',
        'Wis de verbindingsgeschiedenis',
        "Effacer l'historique des connexions",
        'Smazat historii připojení',
        'Usuń historię połączeń',
        'Eliminar histórico das ligações',
        'Elimina cronologia connessioni',
        'Удалить историю соединений',
        'Видалити історію з’єднань'),

    'del_all': (
        'Alles Löschen',
        'Delete all',
        'Verwijder alles',
        'Effacer tout',
        'Smazat vše',
        'Usuń wszystko',
        'Eliminar tudo',
        'Elimina tutto',
        'Удалить всё',
        'Видалити все'),

    'select_all': (
        'Alles auswählen',
        'Select all',
        'Selecteer alles',
        'Tout sélectionner',
        'Vybrat vše',
        'Zaznacz wszystko',
        'Selecionar tudo',
        'Seleziona tutto',
        'Выбрать всё',
        'Вибрати все'),

    'go': (
        'Los',
        'Go',
        'Gaan',
        'Go',
        'Start',
        'Start',
        'Ir',
        'Vai',
        'Пуск',
        'Пуск'),

    'close': (
        'Schließen',
        'Close',
        'Sluiten',
        'Fermer',
        'Zavřít',
        'Zamknij',
        'Fechar',
        'Chiudi',
        'Закрыть',
        'Закрити'),

    'save': (
        'Speichern',
        'Save',
        'Opslaan',
        'Enregistrer',
        'Uložit',
        'Zapisz',
        'Guardar',
        'Salva',
        'Сохранить',
        'Зберегти'),

    'forward': (
        'Weiterleiten',
        'Forward',
        'Vooruit',
        'Forward',
        'Forward',
        'Forward',
        'Encaminhar',
        'Inoltra',
        'Переслать',
        'Переслати'),

    'answer': (
        'Antworten',
        'Answer',
        'Antwoord',
        'Réponse',
        'Odpovědět',
        'Odpowiedz',
        'Responder',
        'Rispondi',
        'Ответить',
        'Відповісти'),

    'send_file': (
        'Datei senden',
        'Send File',
        'Verstuur bestand',
        'Envoi fichier',
        'Odeslat soubor',
        'Wyślij plik',
        'Enviar ficheiro',
        'Invia file',
        'Отправить файл',
        'Надіслати файл'),

    'file_1': (
        'Datei',
        'File',
        'Bestand',
        'Fichier',
        'Soubor',
        'Plik',
        'Ficheiro',
        'File',
        'Файл',
        'Файл'),

    'file_2': (
        'Datei:',
        'File:',
        'Bestand:',
        'Fichier:',
        'Soubor:',
        'Plik:',
        'Ficheiro:',
        'File:',
        'Файл:',
        'Файл:'),

    'locator_calc': (
        'Locator Rechner',
        'Locator Calculator',
        'Lokatie berekenen',
        'Calculateur locator',
        'Kalkulačka lokátoru',
        'Kalkulator Lokatora',
        'Calculador de Locators',
        'Calcolatore Locator',
        'Калькулятор локатора',
        'Калькулятор локатора'),

    'aprs_mon': (
        'APRS Monitor',
        'APRS Monitor',
        'APRS Monitor',
        'Moniteur APRS',
        'APRS Monitor',
        'Monitor APRS',
        'Monitor APRS',
        'Monitor APRS',
        'Монитор APRS',
        'Монітор APRS'),

    'protocol': (
        'Protokoll:',
        'Protocol:',
        'Protocol:',
        'Protocole:',
        'Protokol:',
        'Protokół:',
        'Protocolo:',
        'Protocollo:',
        'Протокол:',
        'Протокол:'),

    'distance': (
        'Distanz',
        'Distance',
        'Afstand',
        'Distance',
        'Vzdálenost',
        'Odległość',
        'Distância',
        'Distanza',
        'Расстояние',
        'Відстань'),

    'send_if_free': (
        'Senden wenn Band frei für (sek.):',
        'Send when band is free for (sec.):',
        'Zenden wanneer band vrij is',
        'Envoyer quand la bande est libre depuis (sec.):',
        'Odeslat, pokud je pásmo volné (sek.):',
        'Wyślij gdy pasmo wolne przez (sek.):',
        'Enviar quando a banda estiver livre por (seg.):',
        'Invia se la banda è libera per (sec.):',
        'Отправить, если диапазон свободен (сек.):',
        'Надіслати, якщо діапазон вільний (сек.):'),

    'size': (
        'Größe:',
        'Size:',
        'Groot:',
        'Taille:',
        'Velikost:',
        'Rozmiar:',
        'Tamanho:',
        'Dimensione:',
        'Размер:',
        'Розмір:'),

    'new': (
        'Neu',
        'New',
        'Nieuw',
        'Nouveau',
        'Nový',
        'Nowy',
        'Novo',
        'Nuovo',
        'Новый',
        'Новий'),

    'wait': (
        'Warten',
        'Wait',
        'Wachten',
        'Attendez',
        'Čekat',
        'Czekaj',
        'Aguardar',
        'Attendi',
        'Ожидание',
        'Чекати'),

    'new_port': (
        'Neuer Port',
        'New port',
        'Nieuwe Poort',
        'Nouveau Port',
        'Nový port',
        'Nowy port',
        'Nova porta',
        'Nuova porta',
        'Новый порт',
        'Новий порт'),

    'new_conn': (
        'Neu Verbindung',
        'New Connection',
        'Nieuwe verbinding',
        'Nouvelle connexion',
        'Nové připojení',
        'Nowe połączenie',
        'Nova ligação',
        'Nuova connessione',
        'Новое соединение',
        'Нове з’єднання'),

    'disconnect': (
        'Disconnecten',
        'Disconnect',
        'Verbreken',
        'Deconnecter',
        'Odpojit',
        'Rozłącz',
        'Desligar',
        'Disconnetti',
        'Отключить',
        'Відключити'),

    'disconnect_all': (
        'ALLE disconnecten',
        'Disconnect ALL',
        'Verbreek alles',
        'Deconnecter tout',
        'Odpojit vše',
        'Rozłącz WSZYSTKIE',
        'Desligar TODAS',
        'Disconnetti TUTTE',
        'Отключить ВСЕ',
        'Відключити ВСІ'),

    'disconnect_all_ask': (
        'Wirklich ALLE Stationen disconnecten ?',
        'Do you want to disconnect ALL stations?',
        'Wilt u ALLE stations verbreken?',
        'Voulez vous déconnecter toutes les stations?',
        'Opravdu odpojit VŠECHNY stanice?',
        'Czy na pewno rozłączyć WSZYSTKIE stacje?',
        'Deseja realmente desligar TODAS as estações?',
        'Vuoi davvero disconnettere TUTTE le stazioni?',
        'Действительно отключить ВСЕ станции?',
        'Дійсно відключити ВСІ станції?'),

    'port_unblock_all': (
        'Eingehende Verbindungen zulassen (alle Ports)',
        'Allow incoming connections (all ports)',
        'Inkomende verbindingen toestaan (alle poorten)',
        'Autoriser les connexions entrantes (tous les ports)',
        'Povolit příchozí spojení (všechny porty)',
        'Zezwól na połączenia przychodzące (wszystkie porty)',
        'Permitir ligações de entrada (todas as portas)',
        'Consenti connessioni in ingresso (tutte le porte)',
        'Разрешить входящие соединения (все порты)',
        'Дозволити вхідні з’єднання (всі порти)'),

    'port_block_ignore_all': (
        'Eingehende Verbindungen ignorieren (alle Ports)',
        'Ignore incoming connections (all ports)',
        'Negeer binnenkomende verbindingen (alle poorten)',
        'Ignorer les connexions entrantes (tous les ports)',
        'Ignorovat příchozí spojení (všechny porty)',
        'Ignoruj połączenia przychodzące (wszystkie porty)',
        'Ignorar ligações de entrada (todas as portas)',
        'Ignora connessioni in ingresso (tutte le porte)',
        'Игнорировать входящие соединения (все порты)',
        'Ігнорувати вхідні з’єднання (всі порти)'),

    'port_block_reject_all': (
        'Eingehende Verbindungen ablehnen (alle Ports)',
        'Reject incoming connections (all ports)',
        'Inkomende verbindingen afwijzen (alle poorten)',
        'Rejeter les connexions entrantes (tous les ports)',
        'Odmítnout příchozí spojení (všechny porty)',
        'Odrzuć połączenia przychodzące (wszystkie porty)',
        'Rejeitar ligações de entrada (todas as portas)',
        'Rifiuta connessioni in ingresso (tutte le porte)',
        'Отклонять входящие соединения (все порты)',
        'Відхиляти вхідні з’єднання (всі порти)'),

    'wx_window': (
        'Wetterstationen',
        'Weather Stations',
        'Weerstations',
        'Stations météos',
        'Meteorologické stanice',
        'Stacje pogodowe',
        'Estações meteorológicas',
        'Stazioni meteo',
        'Метеостанции',
        'Метеостанції'),

    'quit': (
        'Quit',
        'Quit',
        'sluiten',
        'Quitter',
        'Ukončit',
        'Wyjdź',
        'Sair',
        'Esci',
        'Выход',
        'Вихід'),

    'connections': (
        'Verbindungen',
        'Connections',
        'Koppelingen',
        'Connexions',
        'Spojení',
        'Połączenia',
        'Ligações',
        'Connessioni',
        'Соединения',
        'З’єднання'),

    'copy': (
        'Kopieren',
        'Copy',
        'Kopiëren',
        'Copier',
        'Kopírovat',
        'Kopiuj',
        'Copiar',
        'Copia',
        'Копировать',
        'Копіювати'),

    'past': (
        'Einfügen',
        'Past',
        'Invoegen',
        'Coller',
        'Vložit',
        'Wklej',
        'Colar',
        'Incolla',
        'Вставить',
        'Вставити'),

    'cut': (
        'Ausschneiden',
        'Cut out',
        'Knip uit',
        'Couper',
        'Vyjmout',
        'Wytnij',
        'Cortar',
        'Taglia',
        'Вырезать',
        'Вирізати'),

    'past_f_file': (
        'Aus Datei einfügen',
        'Past from File',
        'invoegen uit bestand',
        'Coller depuis fichier',
        'Vložit ze souboru',
        'Wklej z pliku',
        'Colar do ficheiro',
        'Incolla da file',
        'Вставить из файла',
        'Вставити з файлу'),

    'save_to_file': (
        'In Datei speichern',
        'Save to File',
        'Bestand opslaan',
        'Enregistrer dans fichier',
        'Uložit do souboru',
        'Zapisz do pliku',
        'Guardar para ficheiro',
        'Salva su file',
        'Сохранить в файл',
        'Зберегти у файл'),

    'past_qso_f_file': (
        'Aus Datei einfügen',
        'Past from File',
        'Invoegen uit bestand',
        'Coller dans fichier',
        'Vložit ze souboru',
        'Wklej z pliku',
        'Colar de ficheiro',
        'Incolla da file',
        'Вставить из файла',
        'Вставити з файлу'),

    'save_qso_to_file': (
        'QSO in Datei speichern',
        'Save QSO to File',
        'QSO opslaan',
        'Enregistrer QSO dans fichier',
        'Uložit QSO do souboru',
        'Zapisz QSO do pliku',
        'Guardar QSO para ficheiro',
        'Salva QSO su file',
        'Сохранить QSO в файл',
        'Зберегти QSO у файл'),

    'save_mon_to_file': (
        'Monitor in Datei speichern',
        'Save Monitor to File',
        'Kopieer monitor naar bestand',
        'Enregistrer moniteur dans fichier',
        'Uložit monitor do souboru',
        'Zapisz monitor do pliku',
        'Guardar monitor para ficheiro',
        'Salva monitor su file',
        'Сохранить монитор в файл',
        'Зберегти монітор у файл'),

    'clean_prescription_win': (
        'Vorschreibfenster löschen',
        'Clear Prescription window',
        'Voorschrijfvenster verwijderen',
        'Effacer fenêtre préredaction',
        'Vymazat okno předpisu',
        'Wyczyść okno wstępne',
        'Limpar janela de pré-escrita',
        'Pulisci finestra pre-scrittura',
        'Очистить окно предварительной записи',
        'Очистити вікно попереднього написання'),

    'clean_just_qso_win': (
        'QSO löschen',
        'Clear QSO window',
        'QSO verwijderen',
        'Effacer QSO préredaction',
        'Vymazat QSO',
        'Wyczyść QSO',
        'Limpar QSO',
        'Pulisci QSO',
        'Очистить QSO',
        'Очистити QSO'),

    'clean_qso_win': (
        'QSO/Vorschreibfenster löschen',
        'Clear QSO/Prescription window',
        'QSO verwijderen',
        'Effacer QSO/fenêtre préredaction',
        'Vymazat QSO/okno předpisu',
        'Wyczyść QSO/okno wstępne',
        'Limpar QSO/janela de pré-escrita',
        'Pulisci QSO/finestra pre-scrittura',
        'Очистить QSO/окно предварительной записи',
        'Очистити QSO/вікно попереднього написання'),

    'clean_all_qso_win': (
        'Alle QSO/Vorschreibfenster löschen',
        'Clear all QSO/Prescription window',
        'Alle QSO verwijderen',
        'Effacer tous QSO/fenêtres préredactions',
        'Vymazat všechna QSO/okna',
        'Wyczyść wszystkie QSO',
        'Limpar tudo que está na janela de QSO',
        'Pulisci tutti i QSO',
        'Очистить все QSO',
        'Очистити всі QSO'),

    'send_selected': (
        'Auswahl senden',
        'Send selected',
        'Selectie verzenden',
        'Envoyer la sélection',
        'Odeslat výběr',
        'Wyślij zaznaczone',
        'Enviar seleção',
        'Invia selezione',
        'Отправить выбранное',
        'Надіслати вибране'),

    'clean_mon_win': (
        'Monitor löschen',
        'Clear Monitor',
        'Monitor wissen',
        'Effacer moniteur',
        'Vymazat monitor',
        'Wyczyść monitor',
        'Limpar monitor',
        'Pulisci monitor',
        'Очистить монитор',
        'Очистити монітор'),

    'edit': (
        'Bearbeiten',
        'Edit',
        'Bewerken',
        'Editer',
        'Upravit',
        'Edytuj',
        'Editar',
        'Modifica',
        'Редактировать',
        'Редагувати'),

    'statistic': (
        'Statistik',
        'Statistics',
        'Statistieken',
        'Statistiques',
        'Statistika',
        'Statystyki',
        'Estatísticas',
        'Statistiche',
        'Статистика',
        'Статистика'),

    'history': (
        'Verlauf',
        'History',
        'Geschiedenis',
        'Historique',
        'Historie',
        'Historia',
        'Histórico',
        'Cronologia',
        'История',
        'Історія'),

    'linkholder': (
        'Linkhalter',
        'Link holder',
        'Link houder',
        'Liste liens',
        'Držák linků',
        'Trzymacz linków',
        'Suporte de links',
        'Gestore link',
        'Держатель ссылок',
        'Тримач посилань'),

    'right_level_editor': (
        'Rechte-Level Editor',
        'Rights Level Editor',
        'Rechtenniveau Editor',
        'Éditeur de niveau de droits',
        'Editor úrovně práv',
        'Edytor poziomu praw',
        'Editor de nível de direitos',
        'Editor Livello Diritti',
        'Редактор уровней прав',
        'Редактор рівнів прав',
    ),

    'clean_qso': (
        'QSO löschen',
        'delete QSO',
        'QSO verwijderen',
        'Effacer QSO',
        'Smazat QSO',
        'Usuń QSO',
        'Eliminar QSO',
        'Elimina QSO',
        'Удалить QSO',
        'Видалити QSO'),

    'tools': (
        'Tools',
        'Tools',
        'Hulpmiddelen',
        'Outils',
        'Nástroje',
        'Narzędzia',
        'Ferramentas',
        'Strumenti',
        'Инструменты',
        'Інструменти'),

    'station': (
        'Station',
        'Station',
        'Station',
        'Station',
        'Stanice',
        'Stacja',
        'Estação',
        'Stazione',
        'Станция',
        'Станція'),

    'stations': (
        'Stationen',
        'Stations',
        'Stations',
        'Stations',
        'Stanice',
        'Stacje',
        'Estações',
        'Stazioni',
        'Станции',
        'Станції'),

    'port': (
        'Port',
        'Port',
        'Poort',
        'Port',
        'Port',
        'Port',
        'Porta',
        'Porta',
        'Порт',
        'Порт'),

    'address': (
        'Adresse',
        'Address',
        'Adres',
        'Adresse',
        'Adresa',
        'Adres',
        'Endereço',
        'Indirizzo',
        'Адрес',
        'Адреса'),

    'channel': (
        'Kanal',
        'Channel',
        'Kanaal',
        'Canal',
        'Kanál',
        'Kanał',
        'Canal',
        'Canale',
        'Канал',
        'Канал'),

    'beacon': (
        'Baken',
        'Beacons',
        'Baken',
        'Balises',
        'Maják',
        'Beacon',
        'Baliza',
        'Beacon',
        'Маяк',
        'Маяк'),

    'sprech': (
        'Sprachausgabe',
        'Speech output',
        'Spraakuitvoer',
        'Sortie vocale',
        'Hlasový výstup',
        'Wyjście głosowe',
        'Saída de voz',
        'Uscita vocale',
        'Голосовой вывод',
        'Голосовий вивід'),

    'settings': (
        'Einstellungen',
        'Settings',
        'Instellingen',
        'Paramètres',
        'Nastavení',
        'Ustawienia',
        'Configurações',
        'Impostazioni',
        'Настройки',
        'Налаштування'),

    'main_page': (
        'Hauptseite',
        'Main Page',
        'Hoofdpagina',
        'Page principale',
        'Hlavní stránka',
        'Strona główna',
        'Página principal',
        'Pagina principale',
        'Главная страница',
        'Головна сторінка'),

    'password': (
        'Passwort',
        'Password',
        'Wachtwoord',
        'Mot de passe',
        'Heslo',
        'Hasło',
        'Palavra-passe',
        'Password',
        'Пароль',
        'Пароль'),

    'passwords': (
        'Passwörter',
        'Passwords',
        'Wachtwoord',
        'Mots de passe',
        'Hesla',
        'Hasła',
        'Palavras-passe',
        'Password',
        'Пароли',
        'Паролі'),

    'syspassword': (
        'Sys-Passwort:',
        'Sys-Password:',
        'Gebruiker-wachtwoord:',
        'Mot de passe Sys',
        'Sys-Heslo:',
        'Hasło Sys:',
        'Palavra passe do sistema:',
        'Password Sys:',
        'Сис-Пароль:',
        'Сис-Пароль:'),

    'trys': (
        'Fake-Versuche:',
        'Fake-Attempts:',
        'Valse pogingen:',
        'Fausses tentatives :',
        'Falešné pokusy:',
        'Fałszywe próby:',
        'Tentativas falsas:',
        'Tentativi falsi:',
        'Фейковые попытки:',
        'Фейкові спроби:'),

    'fillchars': (
        'Antwortlänge:',
        'Response length:',
        'Reactie lengte:',
        'Longueur réponse :',
        'Délka odpovědi:',
        'Długość odpowiedzi:',
        'Comprimento da resposta:',
        'Lunghezza risposta:',
        'Длина ответа:',
        'Довжина відповіді:'),

    'priv': (
        'Login',
        'Login',
        'Inlog',
        'Login',
        'Přihlášení',
        'Login',
        'Login',
        'Login',
        'Логин',
        'Логін'),

    'login_cmd': (
        'Login Kommando:',
        'Login Command:',
        'Inlog commando:',
        'Commande login :',
        'Příkaz pro přihlášení:',
        'Komenda logowania:',
        'Comando de Login:',
        'Comando do login:',
        'Команда логина:',
        'Команда логіну:'),

    'command': (
        'Befehl',
        'Command',
        'Commando',
        'Commande',
        'Příkaz',
        'Komenda',
        'Comando',
        'Comando',
        'Команда',
        'Команда'),

    'keybind': (
        'Tastaturbelegung',
        'Keyboard layout',
        'Toetsenbordindeling',
        'Racourcis clavier',
        'Klávesové zkratky',
        'Skróty klawiszowe',
        'Atalhos de teclado',
        'Tasti rapidi',
        'Привязка клавиш',
        'Прив’язка клавіш'),

    'about': (
        'Über',
        'About',
        'Over',
        'A propos',
        'O programu',
        'O programie',
        'Sobre',
        'Informazioni',
        'О программе',
        'Про програму'),

    'help': (
        'Hilfe',
        'Help',
        'Hulp',
        'Aide',
        'Nápověda',
        'Pomoc',
        'Ajuda',
        'Aiuto',
        'Помощь',
        'Допомога'),

    'number': (
        'Anzahl',
        'Number',
        'Nummer',
        'Nombre',
        'Počet',
        'Liczba',
        'Número',
        'Numero',
        'Количество',
        'Кількість'),

    'seconds': (
        'Sekunde(n)',
        'Second(s)',
        'Seconde(n)',
        'Seconde(s)',
        'Sekund(a/y)',
        'Sekund(a/y)',
        'Segundo(s)',
        'Secondo(i)',
        'Секунд(а/ы)',
        'Секунд(а/и)'),

    'minutes': (
        'Minute(n)',
        'Minute(s)',
        'Minuut',
        'Minute(s)',
        'Minut',
        'Minut',
        'Minutos',
        'Minuti',
        'Минут',
        'Хвилин'),

    'hours': (
        'Stunden',
        'Hours',
        'Uur',
        'Heures',
        'Hodin',
        'Godzin',
        'Horas',
        'Ore',
        'Часов',
        'Годин'),

    'day': (
        'Tag',
        'Day',
        'Dag',
        'Jour',
        'Den',
        'Dzień',
        'Dia',
        'Giorno',
        'День',
        'День'),

    'month': (
        'Monat',
        'Month',
        'Maand',
        'Mois',
        'Měsíc',
        'Miesiąc',
        'Mês',
        'Mese',
        'Месяц',
        'Місяць'),

    'occup': (
        'Auslastung in %',
        'Occupancy in %',
        'Werkdruk in %',
        'Taux d\'occupation (en %)',
        'Vytížení v %',
        'Obciążenie w %',
        'Ocupação em %',
        'Utilizzo in %',
        'Загрузка в %',
        'Завантаження в %'),

    'call': (
        'Call',
        'Call',
        'Gebruiker',
        'Indicatif',
        'Call',
        'Call',
        'Indicativo',
        'Call',
        'Call',
        'Call'),

    'name': (
        'Name',
        'Name',
        'Naam',
        'Nom',
        'Jméno',
        'Nazwa / Imię',
        'Nome',
        'Nome',
        'Имя',
        'Ім’я'),

    'fwd_list': (
        'Forward Warteschlange',
        'Forward queue',
        'Voorwaartse wachtrij',
        'Forward queue',
        'Fronta forward',
        'Kolejka forward',
        'Fila de forward',
        'Coda Forward',
        'Очередь Forward',
        'Черга Forward'),

    'fwd_path': (
        'Forward Routen',
        'Forward routes',
        'Voorwaartse routes',
        'Routes forward',
        'Forward cesty',
        'Ścieżki forward',
        'Rotas forward',
        'Percorsi Forward',
        'Маршруты Forward',
        'Маршруте Forward'),

    'start_fwd': (
        'FWD Starten',
        'FWD start',
        'Start FWD',
        'Début FWD',
        'Spustit FWD',
        'Uruchom FWD',
        'Iniciar FWD',
        'Avvia FWD',
        'Запустить FWD',
        'Запустити FWD'),

    'start_auto_fwd': (
        'AutoFWD Start',
        'AutoFWD start',
        'Start AutoFWD',
        'Début FWD auto',
        'Spustit AutoFWD',
        'Uruchom AutoFWD',
        'Iniciar AutoFWD',
        'Avvia AutoFWD',
        'Запустить AutoFWD',
        'Запустити AutoFWD'),

    'msg_center': (
        'Nachrichten Center',
        'Message Center',
        'Berichten Center',
        'Centre des méssages',
        'Centrum zpráv',
        'Centrum wiadomości',
        'Centro de mensagens',
        'Centro Messaggi',
        'Центр сообщений',
        'Центр повідомлень'),

    ########################################################
    # Settings
    'text_winPos': (
        'Textfenster Position (oben/mitte/unten)',
        'Text window position (top/middle/bottom)',
        'Positie van het tekstvenster (boven/midden/onder)',
        'Position de la fenêtre de texte (haut/milieu/bas)',
        'Pozice textového okna (nahoru/střed/dolů)',
        'Pozycja okna tekstowego (góra/środek/dół)',
        'Posição da janela de texto (cima/meio/baixo)',
        'Posizione finestra testo (alto/centro/basso)',
        'Позиция текстового окна (верх/середина/низ)',
        'Позиція текстового вікна (вгору/середина/вниз)'),

    'qso_win_color': (
        'QSO Fenster Farben',
        'QSO Win Color',
        'QSO Win Kleur',
        'Couleur fenêtre QSO',
        'Barvy QSO okna',
        'Kolory okna QSO',
        'Côres da janela QSO',
        'Colori finestra QSO',
        'Цвета окна QSO',
        'Кольори вікна QSO'),

    'text_color': (
        'Text Farben',
        'Text Color',
        'Text kleur',
        'Couleur du texte',
        'Barva textu',
        'Kolor tekstu',
        'Côr do texto',
        'Colore testo',
        'Цвет текста',
        'Колір тексту'),

    'bg_color': (
        'Hintergrund Farben',
        'Backgrund Color',
        'BG kleur',
        'Couleur arrière plan',
        'Barva pozadí',
        'Kolor tła',
        'Côr de fundo',
        'Colore sfondo',
        'Цвет фона',
        'Колір фону'),

    'backgrund': (
        'Hintergrund',
        'Backgrund',
        'Achtergrond',
        'Arrière-plan',
        'Pozadí',
        'Tło',
        'Fundo',
        'Sfondo',
        'Фон',
        'Фон'),

    'mon_color': (
        'Monitor Farben',
        'Monitor Colors',
        'Monitor Kleur',
        'Couleur du moniteur',
        'Barvy monitoru',
        'Kolory monitora',
        'Côres do monitor',
        'Colori monitor',
        'Цвета монитора',
        'Кольори монітора'),

    'c_text': (
        'C Text',
        'C Text',
        'C-Text',
        'C-texte',
        'C Text',
        'C Tekst',
        'C Texto',
        'C Text',
        'C Текст',
        'C Текст'),

    'q_text': (
        'Quit Text',
        'Quit Text',
        'Quit-Text',
        'Quit-Text',
        'Quit Text',
        'Tekst wyjścia',
        'Texto Quit',
        'Testo Quit',
        'Текст Quit',
        'Текст Quit'),

    'i_text': (
        'Info Text',
        'Info Text',
        'Info-Text',
        'Info-Text',
        'Info Text',
        'Tekst Info',
        'Texto Info',
        'Testo Info',
        'Текст Info',
        'Текст Info'),

    'li_text': (
        'Lang-Info Text',
        'Long-Info Text',
        'Lange-Info Text',
        'Texte info long',
        'Dlouhý Info Text',
        'Długi tekst Info',
        'Texto Info Longo',
        'Testo Info Lungo',
        'Длинный Info текст',
        'Довгий Info текст'),

    'news_text': (
        'News Text',
        'News Text',
        'Nieuws-Text',
        'texte actualités',
        'News Text',
        'Tekst News',
        'Texto Notícias',
        'Testo News',
        'Текст новостей',
        'Текст новин'),

    'comment': (
        'Kommentar',
        'Comment',
        'Opmerking',
        'Commentaire',
        'Komentář',
        'Komentarz',
        'Comentário',
        'Commento',
        'Комментарий',
        'Коментар'),

    'aprs_settings': (
        'APRS-Einstellungen',
        'APRS-Settings',
        'APRS-instellingen',
        'Paramètres APRS',
        'APRS Nastavení',
        'Ustawienia APRS',
        'Configurações APRS',
        'Impostazioni APRS',
        'Настройки APRS',
        'Налаштування APRS'),

    'digi_settings': (
        'DIGI-Einstellungen',
        'DIGI-Settings',
        'DIGI-instellingen',
        'Paramètres DIGI',
        'DIGI Nastavení',
        'Ustawienia DIGI',
        'Configurações DIGI',
        'Impostazioni DIGI',
        'Настройки DIGI',
        'Налаштування DIGI'),

    'aprs_server': (
        'APRS-Server',
        'APRS-Server',
        'APRS-Server',
        'APRS-Server',
        'APRS Server',
        'Serwer APRS',
        'Servidor APRS',
        'Server APRS',
        'APRS сервер',
        'APRS сервер'),

    'conn_2_aprs_server': (
        'Zum APRS-Server verbinden',
        'Connect to APRS server',
        'Verbinding maken met APRS-server',
        'Se connecter au serveur APRS',
        'Připojit k APRS serveru',
        'Połącz z serwerem APRS',
        'Ligar ao servidor APRS',
        'Connetti al server APRS',
        'Подключиться к APRS серверу',
        'Підключитися до APRS сервера'),

    'aprs_pn_msg': (
        'APRS Messenger',
        'APRS Messenger',
        'APRS Messenger',
        'APRS Messenger',
        'APRS Messenger',
        'APRS Messenger',
        'APRS Messenger',
        'APRS Messenger',
        'APRS Messenger',
        'APRS Messenger'),

    'pn_msg': (
        'Private Nachrichten',
        'Private Messages',
        'Prive berichten',
        'Messages privés',
        'Soukromé zprávy',
        'Wiadomości prywatne',
        'Mensagens privadas',
        'Messaggi privati',
        'Личные сообщения',
        'Приватні повідомлення'),

    'msg': (
        'Nachricht',
        'Message',
        'Bericht',
        'Message',
        'Zpráva',
        'Wiadomość',
        'Mensagem',
        'Messaggio',
        'Сообщение',
        'Повідомлення'),

    'new_msg': (
        'Neue Nachricht',
        'New Message',
        'Nieuw bericht',
        'Nouveau Message',
        'Nová zpráva',
        'Nowa wiadomość',
        'Nova mensagem',
        'Nuovo messaggio',
        'Новое сообщение',
        'Нове повідомлення'),

    ##############################################
    # APRS - DIGI Settings
    'aprs_digi_settings': (
        'Digipeater',
        'Digipeater',
        'Digipeater',
        'Digipeater',
        'Digipeater',
        'Digipeater',
        'Digipeater',
        'Digipeater',
        'Digipeater',
        'Digipeater',
    ),
    'aprs_tracer_settings': (
        'Tracer',
        'Tracer',
        'Tracer',
        'Tracer',
        'Tracer',
        'Tracer',
        'Tracer',
        'Tracer',
        'Tracer',
        'Tracer',
    ),

    'digi_active': (
        'APRS Digipeater aktivieren',
        'Enable APRS Digipeater',
        'APRS Digipeater inschakelen',
        'Activer Digipeater APRS',
        'Povolit APRS Digipeater',
        'Włączyć Digipeater APRS',
        'Ativar Digipeater APRS',
        'Abilita Digipeater APRS',
        'Включить Digipeater APRS',
        'Увімкнути Digipeater APRS',
    ),

    'digi_fillin': (
        'Fill-In Digipeater (nur WIDE1-1)',
        'Fill-In Digipeater (WIDE1-1 only)',
        'Fill-In Digipeater (alleen WIDE1-1)',
        'Digipeater Fill-In (seulement WIDE1-1)',
        'Fill-In Digipeater (pouze WIDE1-1)',
        'Fill-In Digipeater (tylko WIDE1-1)',
        'Digipeater Fill-In (apenas WIDE1-1)',
        'Digipeater Fill-In (solo WIDE1-1)',
        'Fill-In Digipeater (только WIDE1-1)',
        'Fill-In Digipeater (тільки WIDE1-1)',
    ),

    'digi_trace_active': (
        'TRACE Unterstützung aktivieren',
        'Enable TRACE support',
        'TRACE-ondersteuning inschakelen',
        'Activer support TRACE',
        'Povolit podporu TRACE',
        'Włączyć wsparcie TRACE',
        'Ativar suporte TRACE',
        'Abilita supporto TRACE',
        'Включить поддержку TRACE',
        'Увімкнути підтримку TRACE',
    ),

    'digi_trace_all': (
        'TRACE auch für WIDE2-n und höher',
        'TRACE also for WIDE2-n and higher',
        'TRACE ook voor WIDE2-n en hoger',
        'TRACE aussi pour WIDE2-n et plus',
        'TRACE také pro WIDE2-n a vyšší',
        'TRACE również dla WIDE2-n i wyższych',
        'TRACE também para WIDE2-n e superior',
        'TRACE anche per WIDE2-n e superiori',
        'TRACE также для WIDE2-n и выше',
        'TRACE також для WIDE2-n і вище',
    ),

    'digi_dup_time': (
        'Duplikat-Filter Zeitfenster',
        'Duplicate filter time window',
        'Duplicaatfilter tijdvenster',
        'Fenêtre de temps du filtre de doublons',
        'Časové okno filtru duplicit',
        'Okno czasowe filtra duplikatów',
        'Janela de tempo do filtro de duplicados',
        'Finestra temporale filtro duplicati',
        'Временное окно фильтра дубликатов',
        'Часове вікно фільтра дублікатів',
    ),

    'digi_ports': (
        'Digipeater aktiv auf folgenden Ports',
        'Digipeater active on the following ports',
        'Digipeater actief op de volgende poorten',
        'Digipeater actif sur les ports suivants',
        'Digipeater aktivní na následujících portech',
        'Digipeater aktywny na następujących portach',
        'Digipeater ativo nas seguintes portas',
        'Digipeater attivo sulle seguenti porte',
        'Digipeater активен на следующих портах',
        'Digipeater активний на наступних портах',
    ),

    'digi_hint': (
        'Hinweis:\n'
        '• Fill-In Digi digipeatet nur WIDE1-1 von Direktstationen.\n'
        '• TRACE ist für experimentelle / Tracer-Pfade gedacht.\n'
        '• Der Duplikat-Filter verhindert Loops und unnötige Wiederholungen.',

        'Note:\n'
        '• Fill-In Digi only digipeats WIDE1-1 from direct stations.\n'
        '• TRACE is intended for experimental / tracer paths.\n'
        '• The duplicate filter prevents loops and unnecessary repetitions.',

        'Opmerking:\n'
        '• Fill-In Digi digipeatet alleen WIDE1-1 van directe stations.\n'
        '• TRACE is bedoeld voor experimentele / tracer-paden.\n'
        '• De duplicaatfilter voorkomt loops en onnodige herhalingen.',

        'Remarque :\n'
        '• Le Fill-In Digi ne digipeate que les WIDE1-1 des stations directes.\n'
        '• TRACE est destiné aux chemins expérimentaux / tracer.\n'
        '• Le filtre de doublons empêche les boucles et les répétitions inutiles.',

        'Poznámka:\n'
        '• Fill-In Digi digipeatuje pouze WIDE1-1 od přímých stanic.\n'
        '• TRACE je určen pro experimentální / tracer cesty.\n'
        '• Filtr duplicit zabraňuje smyčkám a zbytečným opakováním.',

        'Uwaga:\n'
        '• Fill-In Digi digipeatuje tylko WIDE1-1 od stacji bezpośrednich.\n'
        '• TRACE jest przeznaczony dla ścieżek eksperymentalnych / tracer.\n'
        '• Filtr duplikatów zapobiega pętlom i niepotrzebnym powtórzeniom.',

        'Nota:\n'
        '• Fill-In Digi apenas digipeats WIDE1-1 de estações diretas.\n'
        '• TRACE é destinado a caminhos experimentais / tracer.\n'
        '• O filtro de duplicados evita loops e repetições desnecessárias.',

        'Nota:\n'
        '• Il Fill-In Digi digipeata solo WIDE1-1 dalle stazioni dirette.\n'
        '• TRACE è destinato a percorsi sperimentali / tracer.\n'
        '• Il filtro duplicati impedisce loop e ripetizioni inutili.',

        'Примечание:\n'
        '• Fill-In Digi digipeatит только WIDE1-1 от прямых станций.\n'
        '• TRACE предназначен для экспериментальных / трассировочных путей.\n'
        '• Фильтр дубликатов предотвращает петли и ненужные повторения.',

        'Примітка:\n'
        '• Fill-In Digi digipeatить лише WIDE1-1 від прямих станцій.\n'
        '• TRACE призначений для експериментальних / трасувальних шляхів.\n'
        '• Фільтр дублікатів запобігає петлям та непотрібним повторенням.',
    ),
    ##############################################
    # APRS - I-GATE Settings
    'igate_settings': (
        'I-Gate',
        'I-Gate',
        'I-Gate',
        'I-Gate',
        'I-Gate',
        'I-Gate',
        'I-Gate',
        'I-Gate',
        'I-Gate',
        'I-Gate',
    ),

    'igate_active': (
        'I-Gate aktivieren',
        'Enable I-Gate',
        'I-Gate inschakelen',
        'Activer I-Gate',
        'Povolit I-Gate',
        'Włączyć I-Gate',
        'Ativar I-Gate',
        'Abilita I-Gate',
        'Включить I-Gate',
        'Увімкнути I-Gate',
    ),

    'igate_rf_to_is': (
        'RF → APRS-IS (Upload)',
        'RF → APRS-IS (Upload)',
        'RF → APRS-IS (Upload)',
        'RF → APRS-IS (Upload)',
        'RF → APRS-IS (Upload)',
        'RF → APRS-IS (Upload)',
        'RF → APRS-IS (Upload)',
        'RF → APRS-IS (Upload)',
        'RF → APRS-IS (Загрузка)',
        'RF → APRS-IS (Завантаження)',
    ),

    'igate_is_to_rf': (
        'APRS-IS → RF (Downlink)',
        'APRS-IS → RF (Downlink)',
        'APRS-IS → RF (Downlink)',
        'APRS-IS → RF (Downlink)',
        'APRS-IS → RF (Downlink)',
        'APRS-IS → RF (Downlink)',
        'APRS-IS → RF (Downlink)',
        'APRS-IS → RF (Downlink)',
        'APRS-IS → RF (Выгрузка на радио)',
        'APRS-IS → RF (Вивантаження)',
    ),

    'igate_max_distance': (
        'Maximale Entfernung für Downlink',
        'Maximum distance for Downlink',
        'Maximale afstand voor Downlink',
        'Distance maximale pour Downlink',
        'Maximální vzdálenost pro Downlink',
        'Maksymalna odległość dla Downlink',
        'Distância máxima para Downlink',
        'Distanza massima per Downlink',
        'Максимальное расстояние для Downlink',
        'Максимальна відстань для Downlink',
    ),

    'igate_local_time': (
        'Station gilt als lokal für',
        'Station is considered local for',
        'Station wordt als lokaal beschouwd voor',
        'La station est considérée locale pendant',
        'Stanice je považována za lokální po dobu',
        'Stacja uznawana jest za lokalną przez',
        'Estação é considerada local por',
        'Stazione considerata locale per',
        'Станция считается локальной в течение',
        'Станція вважається локальною протягом',
    ),

    'igate_ports': (
        'Aktiv auf folgenden Ports',
        'Active on the following ports',
        'Actief op de volgende poorten',
        'Actif sur les ports suivants',
        'Aktivní na následujících portech',
        'Aktywny na następujących portach',
        'Ativo nas seguintes portas',
        'Attivo sulle seguenti porte',
        'Активен на следующих портах',
        'Активний на наступних портах',
    ),

    'igate_dup_time': (
        'Duplikat-Filter Zeitfenster',
        'Duplicate filter time window',
        'Duplicaatfilter tijdvenster',
        'Fenêtre de temps du filtre de doublons',
        'Časové okno filtru duplicit',
        'Okno czasowe filtra duplikatów',
        'Janela de tempo do filtro de duplicados',
        'Finestra temporale filtro duplicati',
        'Временное окно фильтра дубликатов',
        'Часове вікно фільтра дублікатів',
    ),
    ##############################################
    # guiBBS_newMSG.py

    'new_pr_mail': (
        'Neue PR-Mail',
        'New PR-Mail',
        'Nieuwe PR-Mail',
        'Nouveau PR-mail',
        'Nová PR-Mail',
        'Nowa PR-Mail',
        'Nova mensagem de PR',
        'Nuova PR-Mail',
        'Новая PR-Mail',
        'Нова PR-Mail'),

    'send': (
        'Senden',
        'Send',
        'Versturen',
        'Envoyer',
        'Odeslat',
        'Wyślij',
        'Enviar',
        'Invia',
        'Отправить',
        'Надіслати'),

    'save_draft': (
        'Entwurf Speichern',
        'Save draft',
        'Concept opslaan',
        'Enregistrer le brouillon',
        'Uložit koncept',
        'Zapisz szkic',
        'Guardar rascunho',
        'Salva bozza',
        'Сохранить черновик',
        'Зберегти чернетку'),

    'save_draft_hint1': (
        'Entwurf gespeichert!',
        'Draft saved!',
        'Concept opgeslagen!',
        'Brouillon enregistré!',
        'Koncept uložen!',
        'Szkic zapisany!',
        'Rascunho guardado!',
        'Bozza salvata!',
        'Черновик сохранён!',
        'Чернетку збережено!'),

    'save_draft_hint2': (
        'Nachricht wurde als Entwurf gespeichert.',
        'Message was saved as a draft.',
        'Bericht is opgeslagen als concept.',
        'Le message a été enregistré comme brouillon.',
        'Zpráva byla uložena jako koncept.',
        'Wiadomość zapisana jako szkic.',
        'Mensagem foi guardada como rascunho.',
        'Messaggio salvato come bozza.',
        'Сообщение сохранено как черновик.',
        'Повідомлення збережено як чернетку.'),

    'not_save_draft_hint1': (
        'Entwurf nicht gespeichert!',
        'Draft not saved!',
        'Concept niet opgeslagen!',
        'Brouillon non enregistré!',
        'Koncept nebyl uložen!',
        'Szkic nie zapisany!',
        'Rascunho não guardado!',
        'Bozza non salvata!',
        'Черновик не сохранён!',
        'Чернетку не збережено!'),

    'not_save_draft_hint2': (
        'Entwurf konnte nicht gespeichert werden.',
        'Draft could not be saved.',
        'Concept kon niet worden opgeslagen.',
        "Le brouillon n'a pas pu être enregistré.",
        'Koncept se nepodařilo uložit.',
        'Nie udało się zapisać szkicu.',
        'Não foi possível guardar o rascunho.',
        'Impossibile salvare la bozza.',
        'Не удалось сохранить черновик.',
        'Не вдалося зберегти чернетку.'),

    'del_message_hint1': (
        'Nachricht löschen?',
        'Delete message?',
        'Bericht verwijderen?',
        'Supprimer le message ?',
        'Smazat zprávu?',
        'Usunąć wiadomość?',
        'Eliminar mensagem?',
        'Eliminare messaggio?',
        'Удалить сообщение?',
        'Видалити повідомлення?'),

    'del_message_hint2': (
        'Nachricht wirklich verwerfen?',
        'Really delete message?',
        'Bericht echt verwijderen?',
        'Supprimer vraiment le message ?',
        'Opravdu smazat zprávu?',
        'Na pewno usunąć wiadomość?',
        'De facto eliminar mensagem?',
        'Eliminare davvero il messaggio?',
        'Действительно удалить сообщение?',
        'Дійсно видалити повідомлення?'),

    'discard': (
        'Verwerfen',
        'Discard',
        'Weggooien',
        'Jeter',
        'Zahodit',
        'Odrzuć',
        'Descartar',
        'Scarta',
        'Отменить',
        'Відхилити'),

    'invalid_call_warning1': (
        'Adresse nicht korrekt',
        'Address incorrect',
        'Adres onjuist',
        'Adresse incorrecte',
        'Adresa není správná',
        'Adres niepoprawny',
        'Endereço incorreto',
        'Indirizzo non corretto',
        'Адрес неверный',
        'Адреса неправильна'),

    'invalid_call_warning2': (
        'Die Adresse des Empfängers ist nicht korrekt.   Keine BBS.',
        "The recipient's address is incorrect. No BBS.",
        'Het adres van de ontvanger is onjuist.   Geen BBS.',
        "L'adresse du destinataire est incorrecte.   Pas de BBS.",
        'Adresa příjemce není správná. Žádná BBS.',
        'Adres odbiorcy jest nieprawidłowy. Brak BBS.',
        'Endereço do destinatário incorreto. Sem BBS.',
        'Indirizzo del destinatario non corretto. Nessuna BBS.',
        'Адрес получателя неверный. Нет BBS.',
        'Адреса отримувача неправильна. Немає BBS.'),

    ##############################################
    'invalid_axcall_warning1': (
        'Call nicht korrekt',
        'Call incorrect',
        'Call onjuist',
        'Call incorrecte',
        'Call není správný',
        'Call niepoprawny',
        'Indicativo incorrecto',
        'Call non corretto',
        'Call неверный',
        'Call неправильний'),

    'invalid_axcall_warning2': (
        'Der eingegebene Call ist nicht korrekt.',
        "The call you entered is incorrect.",
        'Het ingevoerde Call is onjuist.',
        "L'appel Call est incorrect.",
        'Zadaný Call není správný.',
        'Wprowadzony Call jest nieprawidłowy.',
        'O indicativo inserido está incorrecto.',
        'Il Call inserito non è corretto.',
        'Введённый Call неверный.',
        'Введений Call неправильний.'),

    ##############################################
    'send_all_now': (
        'Alles sofort senden',
        'Send everything now',
        'Stuur alles onmiddellijk',
        'Envoyer tout maintenant',
        'Odeslat vše ihned',
        'Wyślij wszystko teraz',
        'Enviar tudo agora',
        'Invia tutto ora',
        'Отправить всё сейчас',
        'Надіслати все зараз'),

    'mark_all_read': (
        'Alle als gelesen markieren',
        'Mark all as read',
        'Markeer alles als gelezen',
        'Tous marquer comme lu',
        'Označit vše jako přečtené',
        'Oznacz wszystkie jako przeczytane',
        'Marcar todas como lidas',
        'Segna tutto come letto',
        'Отметить все как прочитанные',
        'Позначити всі як прочитані'),

    'stat_settings': (
        'Station',
        'Station',
        'Gebruiker',
        'Station',
        'Stanice',
        'Stacja',
        'Estação',
        'Stazione',
        'Станция',
        'Станція'),

    'general_settings': (
        'Allgemein',
        'General',
        'Algemeen',
        'Général',
        'Obecné',
        'Ogólne',
        'Geral',
        'Generale',
        'Общие',
        'Загальні'),

    'GPIO': (
        'GPIO',
        'GPIO',
        'GPIO',
        'GPIO',
        'GPIO',
        'GPIO',
        'GPIO',
        'GPIO',
        'GPIO',
        'GPIO'),

    'gpio_fnc_setting_error_1': (
        'Keine GPIO Funktion',
        'No GPIO function',
        'Geen GPIO-functie',
        'Pas de fonction GPIO',
        'Žádná GPIO funkce',
        'Brak funkcji GPIO',
        'Nenhuma função GPIO',
        'Nessuna funzione GPIO',
        'Нет функции GPIO',
        'Немає функції GPIO'),

    'gpio_fnc_setting_error_2': (
        'Keine GPIO Funktion zugewiesen!',
        'No GPIO function assigned!',
        'Geen GPIO-functie toegewezen!',
        "Aucune fonction GPIO attribuée !",
        'Není přiřazena žádná GPIO funkce!',
        'Nie przypisano żadnej funkcji GPIO!',
        'Nenhuma função GPIO atribuída!',
        'Nessuna funzione GPIO assegnata!',
        'Функция GPIO не назначена!',
        'Функцію GPIO не призначено!'),

    'Digipeater': (
        'Digipeater',
        'Digipeater',
        'Digipeater',
        'Digipeater',
        'Digipeater',
        'Digipeater',
        'Digipeater',
        'Digipeater',
        'Digipeater',
        'Digipeater'),

    'F-Text': (
        'F-Text',
        'F-Text',
        'F-Text',
        'F-Text',
        'F-Text',
        'F-Text',
        'F-Texto',
        'F-Text',
        'F-Текст',
        'F-Текст'),

    'MCast': (
        'MCast',
        'MCast',
        'MCast',
        'MCast',
        'MCast',
        'MCast',
        'MCast',
        'MCast',
        'MCast',
        'MCast'),

    'RX-Echo': (
        'RX-Echo',
        'RX-Echo',
        'RX-Echo',
        'RX-Echo',
        'RX-Echo',
        'RX-Echo',
        'RX-Echo',
        'RX-Echo',
        'RX-Echo',
        'RX-Echo'),

    'new_stat': (
        'Neue Station',
        'New Station',
        'nieuwe gebruiker',
        'Nouvelle station',
        'Nová stanice',
        'Nowa stacja',
        'Estação nova',
        'Nuova stazione',
        'Новая станция',
        'Нова станція'),

    'txt_decoding': (
        'Umlautumwandlung',
        'Text decoding',
        'Text decoding',
        'Decodage texte',
        'Převod Umlautů',
        'Konwersja tekstu',
        'Descodificação do texto',
        'Decodifica testo',
        'Преобразование Umlaut',
        'Перетворення Umlaut'),

    'suc_save': (
        'Info: Station Einstellungen erfolgreich gespeichert.',
        'Info: Station setiings saved.',
        'Info: Gebruiker instellingen goed opgelsagen.',
        'Infos : paramètres station enregistrés',
        'Info: Nastavení stanice úspěšně uloženo.',
        'Info: Ustawienia stacji zapisane pomyślnie.',
        'Info: Configurações da estação guardadas com sucesso.',
        'Info: Impostazioni stazione salvate correttamente.',
        'Инфо: Настройки станции успешно сохранены.',
        'Інфо: Налаштування станції успішно збережено.'),

    'lob1': (
        'Lob: Das hast du sehr gut gemacht !!',
        'Praise: You did very well !!',
        'Dat heb je zeer goed gemaakt !!',
        'Éloge : Vous vous êtes très bien débrouillés !!',
        'Chvála: To jsi zvládl výborně !!',
        'Pochwała: Bardzo dobrze sobie poradziłeś !!',
        'Elogio: Fizeste muito bem !!',
        'Complimenti: Hai fatto davvero bene !!',
        'Похвала: Ты очень хорошо справился !!',
        'Похвала: Ти дуже добре впорався !!'),

    'lob2': (
        'Lob: Das hast du gut gemacht !!',
        'Praise: You did well!!',
        'Dat heb je goed gemaakt ',
        'Éloge : Vous avez bien travaillé !',
        'Chvála: To jsi udělal dobře !!',
        'Pochwała: Dobra robota !!',
        'Elogio: Fizeste bem !!',
        'Complimenti: Hai fatto bene !!',
        'Похвала: Ты хорошо справился !!',
        'Похвала: Ти добре впорався !!'),

    'lob3': (
        'Lob: Das war eine gute Entscheidung. Mach weiter so. Das hast du gut gemacht.',
        'Praise: That was a good decision. Keep it up. You did well.',
        'Dat was een goede beslissing. Ga zo door. Dat heb je goed gemaakt.',
        'Éloge : C\'était une bonne décision. Continuez. Vous avez bien travaillé,',
        'Chvála: To bylo dobré rozhodnutí. Pokračuj takhle. Dobře jsi to zvládl.',
        'Pochwała: To była dobra decyzja. Tak trzymaj. Dobrze to zrobiłeś.',
        'Elogio: Foi uma boa decisão. Continua assim. Fizeste bem.',
        'Complimenti: È stata una buona decisione. Continua così. Hai fatto bene.',
        'Похвала: Это было хорошее решение. Продолжай в том же духе. Молодец.',
        'Похвала: Це було хороше рішення. Продовжуй у тому ж дусі. Молодець.'),

    'lob4': (
        'Lob: Du hast dir heute noch kein Lob verdient.',
        "Praise: You haven't earned any praise today.",
        'Je hebt vandaag geen lof verdiend.',
        'Éloges : Vous n\'avez pas mérité d\'être félicité aujourd\'hui.',
        'Chvála: Dnes sis ještě žádnou chválu nezasloužil.',
        'Pochwała: Dziś jeszcze nie zasłużyłeś na pochwałę.',
        'Elogio: Ainda não mereceste elogios hoje.',
        'Complimenti: Oggi non ti sei ancora guadagnato nessun complimento.',
        'Похвала: Сегодня ты ещё не заслужил похвалы.',
        'Похвала: Сьогодні ти ще не заслужив похвали.'),

    'lob5': (
        'Es tut mir leid, Dave. Ich fürchte, das kann ich nicht.',
        "I'm sorry, Dave. I'm afraid I can't do that.",
        'Het spijt me, Dave. Ik ben bang dat ik dat niet kan.',
        'Je suis désolé, Dave. J\'ai bien peur de ne pas pouvoir le faire ',
        'Je mi líto, Dave. Obávám se, že to nemohu udělat.',
        'Przykro mi, Dave. Obawiam się, że nie mogę tego zrobić.',
        'Lamento, Dave. Receio não poder fazer isso.',
        'Mi dispiace, Dave. Temo di non poterlo fare.',
        'Мне жаль, Дейв. Боюсь, я не могу этого сделать.',
        'Мені шкода, Дейве. Боюсь, я не можу цього зробити.'),

    'hin1': (
        'Hinweis: Der OK Button funktioniert noch !!',
        'Note: The OK button still works !!',
        'De OK knop werkt nog !!',
        'Note le bouton OK fonctionne',
        'Poznámka: Tlačítko OK ještě funguje !!',
        'Uwaga: Przycisk OK nadal działa !!',
        'Nota: O botão OK ainda funciona !!',
        'Nota: Il pulsante OK funziona ancora !!',
        'Примечание: Кнопка OK ещё работает !!',
        'Примітка: Кнопка OK ще працює !!'),

    'hin2': (
        'Hinweis: Knack!! Abgebrochen..',
        'Note: Canceled !!',
        'geannuleerd!',
        'Note : Annulé',
        'Poznámka: Zrušeno..',
        'Uwaga: Anulowano..',
        'Nota: Cancelado..',
        'Nota: Annullato..',
        'Примечание: Отменено..',
        'Примітка: Скасовано..'),

    'date_time': (
        'Datum/Zeit',
        'Date/Time',
        'Datum/tijd',
        'Date/heure',
        'Datum/Čas',
        'Data/Czas',
        'Data/Hora',
        'Data/Ora',
        'Дата/Время',
        'Дата/Час'),

    'time': (
        'Zeit',
        'Time',
        'Tijd',
        'Heure',
        'Čas',
        'Czas',
        'Hora',
        'Ora',
        'Время',
        'Час'),

    'date': (
        'Datum',
        'Date',
        'Datum',
        'Date',
        'Datum',
        'Data',
        'Data',
        'Data',
        'Дата',
        'Дата'),

    'message': (
        'Nachricht',
        'Message',
        'Nieuws',
        'Messages',
        'Zpráva',
        'Wiadomość',
        'Mensagem',
        'Messaggio',
        'Сообщение',
        'Повідомлення'),

    'titel': (
        'Titel',
        'Title',
        'Titel',
        'Titre',
        'Název',
        'Tytuł',
        'Título',
        'Titolo',
        'Заголовок',
        'Заголовок'),

    'from': (
        'Von',
        'From',
        'van ',
        'De',
        'Od',
        'Od',
        'De',
        'Da',
        'От',
        'Від'),

    'to': (
        'An',
        'To',
        'Naar ',
        'Pour',
        'Komu',
        'Do',
        'Para',
        'A',
        'Кому',
        'Кому'),

    'subject': (
        'Betreff',
        'Subject',
        'Onderwerp ',
        'Sujet',
        'Předmět',
        'Temat',
        'Assunto',
        'Oggetto',
        'Тема',
        'Тема'),

    'versatz': (
        'Versatz',
        'Offset',
        'Verzet',
        'Offset',
        'Posun',
        'Przesunięcie',
        'Desvio',
        'Offset',
        'Смещение',
        'Зсув'),

    'intervall': (
        'Intervall',
        'Interval',
        'Interval',
        'Intervalle',
        'Interval',
        'Interwał',
        'Intervalo',
        'Intervallo',
        'Интервал',
        'Інтервал'),

    'active': (
        'Aktiviert',
        'Activated',
        'Ingeschakeld',
        'Activé',
        'Aktivní',
        'Aktywny',
        'Ativo',
        'Attivo',
        'Активен',
        'Активний'),

    'text_fm_file': (
        'Text aus Datei',
        'Text from File',
        'Tekst uit bestand ',
        'Texte depuis fichier',
        'Text ze souboru',
        'Tekst z pliku',
        'Texto do ficheiro',
        'Testo da file',
        'Текст из файла',
        'Текст з файлу'),

    'beacon_settings': (
        'Baken',
        'Beacon',
        'Baken',
        'Balise',
        'Maják',
        'Beacon',
        'Baliza',
        'Beacon',
        'Маяк',
        'Маяк'),

    # Pipe Tool
    'pipetool_settings': (
        'Pipe-Tool Einstellungen',
        'Pipe-Tool Settings',
        'Pipe-Tool Instellingen',
        'paramètres Pipe-tools',
        'Nastavení Pipe-Tool',
        'Ustawienia Pipe-Tool',
        'Configurações Pipe-Tool',
        'Impostazioni Pipe-Tool',
        'Настройки Pipe-Tool',
        'Налаштування Pipe-Tool'),

    'new_pipe': (
        'Neue Pipe',
        'New Pipe',
        'Nieuwe Pipe',
        'Nouveau Pipe',
        'Nová Pipe',
        'Nowa Pipe',
        'Nova Pipe',
        'Nuova Pipe',
        'Новая Pipe',
        'Нова Pipe'),

    'new_pipe_fm_connection': (
        'Pipe auf Verbindung',
        'Pipe on Connection',
        'Pipe op aansluiting',
        'Pipe à la connexion',
        'Pipe na spojení',
        'Pipe na połączeniu',
        'Pipe na ligação',
        'Pipe sulla connessione',
        'Pipe на соединении',
        'Pipe на з’єднанні'),

    'tx_file': (
        'TX Datei',
        'TX File',
        'TX-File',
        'TX fichier',
        'TX soubor',
        'Plik TX',
        'Ficheiro TX',
        'File TX',
        'TX файл',
        'TX файл'),

    'rx_file': (
        'RX Datei',
        'RX File',
        'RX-File',
        'RX fichier',
        'RX soubor',
        'Plik RX',
        'Ficheiro RX',
        'File RX',
        'RX файл',
        'RX файл'),

    'ax25_param': (
        'AX.25 Verbindungsparameter',
        'AX.25 connection parameters',
        'AX.25 verbindingsparameters',
        'Paramètres de connexion AX.25',
        'AX.25 parametry spojení',
        'Parametry połączenia AX.25',
        'Parâmetros de ligação AX.25',
        'Parametri connessione AX.25',
        'Параметры соединения AX.25',
        'Параметри з’єднання AX.25'),

    'packet_timing_param': (
        'Paket- & Timing-Parameter',
        'Package & timing parameters',
        'Pakket- en timingparameters',
        'Paramètres du package et du calendrier',
        'Parametry paketů a časování',
        'Parametry pakietów i timing',
        'Parâmetros de pacotes e timing',
        'Parametri pacchetti e timing',
        'Параметры пакетов и тайминга',
        'Параметри пакетів і таймінгу'),

    'backen_config': (
        'Backend Konfiguration',
        'Backend configuration',
        'Backend-configuratie',
        'Configuration du back-end',
        'Konfigurace backendu',
        'Konfiguracja backendu',
        'Configuração de reserva',
        'Configurazione Backend',
        'Конфигурация Backend',
        'Конфігурація Backend'),

    'net_ser_opt': (
        'Netzwerk / Seriell Optionen',
        'Network / Serial Options',
        'Netwerk-/seriële opties',
        'Options réseau/série',
        'Síťové / Sériové možnosti',
        'Opcje Sieć / Szeregowe',
        'Opções Rede / Série',
        'Opzioni Rete / Seriale',
        'Параметры сети / последовательного порта',
        'Параметри мережі / послідовного порту'),

    'serial_interface': (
        'Serielle Schnittstelle',
        'Serial interface',
        'Seriële interface',
        'Interface série',
        'Sériové rozhraní',
        'Interfejs szeregowy',
        'Interface série',
        'Interfaccia seriale',
        'Последовательный интерфейс',
        'Послідовний інтерфейс'),

    # #####
    'port_cfg_std_parm': (
        'Standard Parameter. Werden genutzt wenn nirgendwo anders (Station/Client) definiert.',
        'Default parameters. Are used if not defined anywhere else (station/client).',
        'Standaardparameters. Worden gebruikt als ze nergens anders zijn gedefinieerd (station/client).',
        'Paramètres par défaut. Utilisés si non définis (station/client)',
        '',
        '',
        'Parâmetros por defeito. Serão usados se não foram definidos anteriormente (estação/cliente)',
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
        'Atraso do Pseudo TX (tempo de espera entre o TX e a RT). Não é definido como um parâmetro KISS no TNC',
        '',
        '',
        ''),

    'port_cfg_pac_len': (
        'Paket Länge. 30 - 256',
        'Packet length. 30-256',
        'Pakket lengte. 30-256',
        'Longueur trame. 30-256',
        '',
        '',
        'Tamanho do packet. 30-256',
        '',
        '',
        ''),

    'port_cfg_pac_max': (   # Not used anymore ...
        'Max Paket Anzahl. 1 - 7',
        'Max Packets. 1 - 7',
        'Max pakketnummer. 1 - 7',
        'Max trame. 1-7',
        '',
        '',
        'Número de packets enviados. 1 - 7',
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
        'Designação da porta para o MH e o monitor (Máx: 4)',
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
        'A porta não foi inicializada',
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
        'último packet',
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
        'Scrool automático',
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
        'Apagar a lista de MH',
        '',
        ''),

    'msg_box_mh_delete_msg': (
        'Komplette MH-Liste löschen?',
        'Delete entire MH list?',
        'Volledige MH-lijst verwijderen?',
        'Supprimer la liste MH complète',
        '',
        '',
        'Apagar completamente a lista de MH',
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
        'Apagar os dados',
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
        'Apagar todos os dados',
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
        'Dados',
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
        'Cuidado com as ligações de nodes tipo TNN. Ligações de nodes múltiplos via multicast pode causar problemas',
        '',
        '',
        ''),

    'connection_history': (
        'Verbindungsverlauf',
        'Connection history',
        'Verbindingsgeschiedenis',
        'Historique des connexions',
        '',
        '',
        'Histórico das ligações',
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
        'Database do utilizador',
        '',
        '',
        ''),

    'show_in_userDB': (
        'In User-DB zeigen',
        'Show in User-DB',
        'Weergeven in Gebruikersdatabase',
        'Afficher dans la base de données utilisateur',
        '',
        '',
        'Mostrar na Database de utilizador',
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
        'Chamar o Sysop',
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
        'Estações meteorológicas',
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
        'Obter entrada na database de indicativos',
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
        'O seu nome',
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
        'O seu QTH',
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
        'O seu Locator',
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
        'O seu código postal',
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
        'A sua BBS oficial',
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
        'O seu endereço email',
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
        'O seu HTTP',
        '',
        '',
        ''),

    'cmd_help_aclear': (
        'APRS Nachrichten löschen',                    # DE
        'Delete / Clear APRS Messages',                # EN
        'APRS Berichten wissen / wissen',              # NL
        'Supprimer les messages APRS',                 # FR
        'Smazat APRS zprávy',                          # CZ
        'Usuń wiadomości APRS',                        # PL
        'Apagar mensagens APRS',                       # PT
        'Cancella messaggi APRS',                      # IT
        'Удалить сообщения APRS',                      # RU
        'Видалити повідомлення APRS',                  # UA
    ),

    # =============================
    'cli_error_no_call': (
        " # Kein Call angegeben.",                    # DE
        " # No call specified.",                      # EN
        " # Geen call opgegeven.",                    # NL
        " # Aucun call spécifié.",                    # FR
        " # Nebyl zadán callsign.",                   # CZ
        " # Nie podano callsignu.",                   # PL
        " # Nenhum indicativo especificado.",         # PT
        " # Nessun call specificato.",                # IT
        " # Не указан callsign.",                     # RU
        " # Не вказано callsign.",                    # UA
    ),

        'cli_error_no_call_in_mh_db': (
        " # {0} nicht in MH-Datenbank gefunden.",                    # DE
        " # {0} not found in MH database.",                          # EN
        " # {0} niet gevonden in MH-database.",                      # NL
        " # {0} non trouvé dans la base MH.",                        # FR
        " # {0} nenalezen v MH databázi.",                           # CZ
        " # {0} nie znaleziono w bazie MH.",                         # PL
        " # {0} não encontrado na base de dados MH.",                # PT
        " # {0} non trovato nel database MH.",                       # IT
        " # {0} не найден в базе MH.",                               # RU
        " # {0} не знайдено в базі MH.",                             # UA
    ),
    # =============================
    'cli_error': (
        " # Fehler.",
        " # Error.",
        " # Fout.",
        " # Erreur.",
        " # Chyba.",
        " # Błąd.",
        " # Erro.",
        " # Errore.",
        " # Ошибка.",
        " # Помилка.",
    ),

    'cli_no_user_db_ent': (
        ' # Eintag nicht in Benutzer Datenbank vorhanden!',
        ' # Entry not in user database!',
        ' # Invoer niet in gebruikersdatabase!',
        ' # Entrée non trouvé dans la BDD utilisateur!!',
        ' # Záznam nebyl nalezen v uživatelské databázi!',
        ' # Brak wpisu w bazie użytkowników!',
        ' # Entrada não encontrada na base de dados de utilizadores!',
        ' # Voce non presente nel database utenti!',
        ' # Запись не найдена в базе пользователей!',
        ' # Запис не знайдено в базі користувачів!'),

    'cli_name_set': (
        ' # Name eingetragen',
        ' # Username is set',
        ' # Naam ingevoerd',
        ' # Nom utilisateur défini',
        ' # Jméno bylo uloženo',
        ' # Imię zostało zapisane',
        ' # Nome registado',
        ' # Nome impostato',
        ' # Имя сохранено',
        ' # Ім’я збережено'),

    'cli_qth_set': (
        ' # QTH eingetragen',
        ' # QTH is set',
        ' # Locatie ingevoerd',
        ' # QTH défini',
        ' # QTH bylo uloženo',
        ' # QTH zapisane',
        ' # QTH registado',
        ' # QTH impostato',
        ' # QTH сохранён',
        ' # QTH збережено'),

    'cli_loc_set': (
        ' # Locator eingetragen',
        ' # Locator is set',
        ' # Locator ingevoerd',
        ' # Locator défini',
        ' # Lokátor uložen',
        ' # Locator zapisany',
        ' # Locator registado',
        ' # Locator impostato',
        ' # Локатор сохранён',
        ' # Локатор збережено'),

    'cli_zip_set': (
        ' # Postleitzahl eingetragen',
        ' # ZIP is set',
        ' # Postcode ingevoerd',
        ' # CP défini',
        ' # PSČ uloženo',
        ' # Kod pocztowy zapisany',
        ' # Código postal registado',
        ' # CAP impostato',
        ' # Индекс сохранён',
        ' # Індекс збережено'),

    'cli_prmail_set': (
        ' # PR-Mail Adresse eingetragen',
        ' # PR-Mail Address is set',
        ' # PR-Mail ingevoerd',
        ' # Adresse PR-Mail définie',
        ' # PR-Mail adresa uložena',
        ' # Adres PR-Mail zapisany',
        ' # Endereço da BBS oficial registada',
        ' # Indirizzo PR-Mail impostato',
        ' # PR-Mail адрес сохранён',
        ' # PR-Mail адресу збережено'),

    'cli_email_set': (
        ' # E-Mail Adresse eingetragen',
        ' # E-Mail Address is set',
        ' # E-Mail ingevoerd',
        ' # Adresse E-mail définie',
        ' # E-mail adresa uložena',
        ' # Adres e-mail zapisany',
        ' # Endereço E-mail registado',
        ' # Indirizzo E-mail impostato',
        ' # E-Mail адрес сохранён',
        ' # E-Mail адресу збережено'),

    'cli_http_set': (
        ' # HTTP eingetragen',
        ' # HTTP is set',
        ' # HTTP ingevoerd',
        ' # HTTP défini',
        ' # HTTP adresa uložena',
        ' # Adres HTTP zapisany',
        ' # HTTP registado',
        ' # HTTP impostato',
        ' # HTTP сохранён',
        ' # HTTP збережено'),

    'cli_text_encoding_no_param': (
        ' # Bitte ein ä senden. Bsp.: UM ä.\r # Derzeitige Einstellung:',
        ' # Please send an ä. Example: UM ä.\r # Current setting:',
        ' # Stuur een  ä. voorbeeld ä.\r # Huidige instelling:',
        ' # Veuillez envoyer un ä. Exemple : UM ä.\r # Réglage actuel :',
        ' # Pošlete prosím ä. Příklad: UM ä.\r # Aktuální nastavení:',
        ' # Wyślij ä. Przykład: UM ä.\r # Aktualne ustawienie:',
        ' # Envie um ä. Exemplo: UM ä.\r # Definição atual:',
        ' # Invia un ä. Esempio: UM ä.\r # Impostazione attuale:',
        ' # Отправьте символ ä. Пример: UM ä.\r # Текущая настройка:',
        ' # Надішліть символ ä. Приклад: UM ä.\r # Поточне налаштування:'),

    'cli_text_encoding_error_not_found': (
        ' # Umlaute wurden nicht erkannt !',
        " # Couldn't detect right text encoding",
        ' # Kan de juiste tekstcodering niet detecteren',
        ' # Ne peut detecter le bon encodage',
        ' # Umlauty nebyly rozpoznány!',
        ' # Nie wykryto prawidłowego kodowania!',
        ' # Não foi possível detetar a codificação!',
        ' # Impossibile rilevare la codifica corretta!',
        ' # Umlauty не распознаны!',
        ' # Umlauty не розпізнано!'),

    'cli_text_encoding_set': (
        ' # Umlaute/Text de/enkodierung gesetzt auf:',
        " # Text de/encoding set to:",
        ' # Tekstde/codering ingesteld op:',
        ' # Encodage/decodage du texte paramétré à :',
        ' # kódování textu nastaveno na:',
        ' # Kodowanie tekstu ustawione na:',
        ' # Codificação de texto definida para:',
        ' # Codifica testo impostata su:',
        ' # Кодировка текста установлена на:',
        ' # Кодування тексту встановлено на:'),

    'cli_text_encoding_current': (
        'Aktuell verwendeter Encoder',
        'Currently used encoder',
        'Huidige gebruikte encoder',
        'Encodeur actuellement utilisé',
        'Aktuálně používaný encoder',
        'Aktualnie używany koder',
        'Codificador atualmente em uso',
        'Encoder attualmente in uso',
        'Текущий используемый кодировщик',
        'Поточний використовуваний кодувальник'),

    'cli_text_encoding_cmd_help': (
        'Text Encoding setzen mit ENC <opt>',
        'Set text encoding with ENC <opt>',
        'Tekstcodering instellen met ENC <opt>',
        'Définir l\'encodage du texte avec ENC <opt>',
        'Nastavit kódování textu pomocí ENC <opt>',
        'Ustaw kodowanie tekstu za pomocą ENC <opt>',
        'Definir codificação de texto com ENC <opt>',
        'Imposta codifica testo con ENC <opt>',
        'Установить кодировку текста командой ENC <opt>',
        'Встановити кодування тексту командою ENC <opt>'),

    'port_overview': (
        'Port Übersicht',
        'Port Overview',
        'Poort overzicht',
        'Vue d\'ensemble Ports',
        'Přehled portů',
        'Przegląd portów',
        'Visão geral das portas',
        'Panoramica porte',
        'Обзор портов',
        'Огляд портів'),

    'cmd_shelp': (
        'Kurzhilfe',
        'Short help',
        'Korte hulp',
        'Aide courte',
        'Krátká nápověda',
        'Krótka pomoc',
        'Ajuda rápida',
        'Aiuto rapido',
        'Краткая справка',
        'Коротка довідка'),

    'time_connected': (
        'Connect Dauer',
        'Connect duration',
        'verbindingsduur',
        'Durée connexion',
        'Doba připojení',
        'Czas połączenia',
        'Duração da ligação',
        'Durata connessione',
        'Время подключения',
        'Тривалість підключення'),

    'cmd_not_known': (
        'Dieses Kommando ist dem System nicht bekannt !',
        'The system does not know this command !',
        'Het systeem kent deze opdracht niet !',
        'Le système ne reconnait pas cette commande',
        'Tento příkaz systém nezná!',
        'System nie zna tego polecenia!',
        'Este comando não é conhecido pelo sistema!',
        'Questo comando non è riconosciuto dal sistema!',
        'Система не знает эту команду!',
        'Система не знає цю команду!'),

    'auto_text_encoding': (
        'Automatisch Umlaut Erkennung. ä als Parameter. > UM ä',
        'Automatic detection of text encoding. ä as a parameter. > UM ä',
        'Automatische detectie van tekstcodering. ä als parameter. > UM ä',
        'Détection automatique de l\'encodage du texte. ä comme paramètre. > UM ä',
        'Automatické rozpoznání Umlautů. ä jako parametr. > UM ä',
        'Automatyczne wykrywanie kodowania. ä jako parametr. > UM ä',
        'Detecção automática de codificação. ä como parâmetro. > UM ä',
        'Rilevamento automatico codifica. ä come parametro. > UM ä',
        'Автоматическое распознавание Umlaut. ä как параметр. > UM ä',
        'Автоматичне розпізнавання Umlaut. ä як параметр. > UM ä'),

    'cmd_help_lcstatus': (
        'Verbundene Terminalkanäle anzeigen (ausführliche Version)',
        'Show connected terminal channels (detailed version)',
        'Toon aangesloten terminalkanalen (gedetailleerde versie)',
        'Afficher les terminal connectés (version détaillée)',
        'Zobrazit připojené terminálové kanály (podrobná verze)',
        'Pokaż podłączone kanały terminala (wersja szczegółowa)',
        'Mostrar canais de terminal conectados (versão detalhada)',
        'Mostra canali terminali connessi (versione dettagliata)',
        'Показать подключённые терминальные каналы (подробно)',
        'Показати підключені термінальні канали (детально)'),

    'cmd_help_cstat': (
        'Verbindungsstatistik der letzten 7 Tage',
        'Connection statistics for the last 7 days',
        'Verbindingsstatistieken van de afgelopen 7 dagen',
        'Statistiques de connexion des 7 derniers jours',
        'Statistika připojení za posledních 7 dní',
        'Statystyki połączeń z ostatnich 7 dni',
        'Estatísticas de ligação dos últimos 7 dias',
        'Statistiche connessioni ultimi 7 giorni',
        'Статистика соединений за последние 7 дней',
        'Статистика з’єднань за останні 7 днів'),

    'cmd_help_chist': (
        'Verbindungsverlauf (letzte 30 Tage)',
        'Connection History (last 30 days)',
        'Verbindingsgeschiedenis (laatste 30 dagen)',
        'Historique des connexions (30 derniers jours)',
        'Historie připojení (posledních 30 dní)',
        'Historia połączeń (ostatnie 30 dni)',
        'Histórico das ligações (últimos 30 dias)',
        'Cronologia connessioni (ultimi 30 giorni)',
        'История соединений (последние 30 дней)',
        'Історія з’єднань (останні 30 днів)'),

    'cmd_help_ch': (
        'Kurze Nachricht an Kanal senden. CH <Kanal> Nachricht',
        'Send short message to channel. CH <Channel> Message',
        'Stuur een kort bericht naar het kanaal. CH <Kanaal> Bericht',
        'Envoyer un court message au canal. CH <Canal> Message',
        'Poslat krátkou zprávu na kanál. CH <Kanál> Zpráva',
        'Wyślij krótką wiadomość na kanał. CH <Kanał> Wiadomość',
        'Enviar mensagem curta para canal. CH <Canal> Mensagem',
        'Invia messaggio breve al canale. CH <Canale> Messaggio',
        'Отправить короткое сообщение в канал. CH <Канал> Сообщение',
        'Надіслати коротке повідомлення в канал. CH <Канал> Повідомлення'),

    'cmd_help_rtt': (
        'Paket Laufzeitmessung',
        'Packet runtime measurement',
        'Looptijdmeting',
        "Mesure du temps d'exécution",
        'Měření doby odezvy paketů',
        'Pomiar czasu RTT pakietów',
        'Medição de tempo de pacotes',
        'Misurazione tempo di percorrenza pacchetti',
        'Измерение времени прохождения пакетов',
        'Вимірювання часу проходження пакетів'),

    'cmd_help_bwstat': (
        'Bandauslastung letzten 10 Minuten',
        'Band utilization last 10 minutes',
        'Bandgebruik laatste 10 minuten',
        "Utilisation du bracelet pendant 10 minutes",
        'Vytížení pásma za posledních 10 minut',
        'Wykorzystanie pasma ostatnie 10 minut',
        'Utilização da banda últimos 10 minutos',
        'Utilizzo banda ultimi 10 minuti',
        'Загрузка диапазона за последние 10 минут',
        'Завантаження діапазону за останні 10 хвилин'),

    'cli_no_wx_data': (
        'Keine Wetterdaten vorhanden.',
        'No WX data available',
        'Geen WX beschikbaar.',
        'Aucune données météos disponnible',
        'Žádná meteorologická data.',
        'Brak danych pogodowych.',
        'Nenhum dado meteorológico disponível.',
        'Nessun dato meteo disponibile.',
        'Нет данных о погоде.',
        'Немає даних про погоду.'),

    'cli_no_data': (
        'Keine Daten vorhanden.',
        'No data available.',
        'Geen gegevens beschikbaar.',
        'Pas de données disponnibles',
        'Žádná data.',
        'Brak danych.',
        'Nenhum dado disponível.',
        'Nessun dato disponibile.',
        'Нет данных.',
        'Немає даних.'),

    'cli_no_tracer_data': (
        'Keine Tracerdaten vorhanden.',
        'No Tracer data available',
        'Geen tracergegevens beschikbaar.',
        'Pas de données Tracer disponnibles',
        'Žádná Tracer data.',
        'Brak danych Tracer.',
        'Nenhum dado Tracer disponível.',
        'Nessun dato Tracer disponibile.',
        'Нет данных Tracer.',
        'Немає даних Tracer.'),

    # ===============================
        'cli_change_language': (
        'Sprache ändern.',
        'Change language.',
        'Taal veranderen',
        'Modifier langue',
        'Změnit jazyk.',
        'Zmień język.',
        'Alterar língua.',
        'Cambia lingua.',
        'Изменить язык.',
        'Змінити мову.'),

    'cli_lang_set': (
        'Sprache auf Deutsch geändert.',
        'Language changed to English.',
        'Taal veranderd naar Nederlands.',
        'Lange changé pour Français',
        'Jazyk změněn na Češtinu.',
        'Język zmieniony na Polski.',
        'Língua alterada para Português.',
        'Lingua cambiata in Italiano.',
        'Язык изменён на Русский.',
        'Мову змінено на Українську.'),

    'cli_no_lang_param': (
        'Sprache nicht erkannt! Mögliche Sprachen: ',
        'Language not recognized! Possible languages: ',
        'Taal niet herkend! Mogelijke talen: ',
        'Langue non reconnue! Langues possibles : ',
        'Jazyk nerozpoznán! Možné jazyky: ',
        'Język nierozpoznany! Możliwe języki: ',
        'Língua não reconhecida! Línguas possíveis: ',
        'Lingua non riconosciuta! Lingue possibili: ',
        'Язык не распознан! Возможные языки: ',
        'Мову не розпізнано! Можливі мови: '),

    # ===============================
    'cmd_rtt_1': (
        ' # Laufzeit hin und zurück: ',
        ' # Round trip time: ',
        ' # Reistijd heen en terug: ',
        ' # Temps de trajet aller-retour : ',
        ' # Doba odezvy (RTT): ',
        ' # Czas rundy (RTT): ',
        ' # Tempo de ida e volta: ',
        ' # Tempo di andata e ritorno: ',
        ' # Время кругового пути (RTT): ',
        ' # Час туди і назад (RTT): '),

    'cmd_bell': (
        'Sysop wird gerufen !!',
        'Sysop is called!!',
        'Gebruiker wordt geroepen!!',
        'Sysop appelé!!',
        'Sysop je volán !!',
        'Sysop jest wzywany !!',
        'O Sysop está a ser chamado!!',
        'Sysop chiamato!!',
        'Сисоп вызывается !!',
        'Сисоп викликається !!'),

    'cmd_bell_again': (
        'Sysop wurde bereits gerufen..',
        'Sysop has already been called..',
        'Gebruiker is al geroepen..',
        'Le Sysop a déjà été appelé..',
        'Sysop již byl volán..',
        'Sysop został już wezwany..',
        'O Sysop já foi chamado..',
        'Sysop è già stato chiamato..',
        'Сисоп уже был вызван..',
        'Сисоп вже був викликаний..'),

    'cmd_bell_gui_msg': (
        'verlangt nach dem Sysop !!',
        'asks for the sysop!!',
        'vraagt om de gebruiker!!',
        'Appel du Sysop!!',
        'volá Sysopa !!',
        'wzywa Sysopa !!',
        'solicita o Sysop !!',
        'richiede il Sysop !!',
        'вызывает сисопа !!',
        'викликає сисопа !!'),

    'cmd_c_noCall': (
        '# Bitte Call eingeben..',
        '# Please enter call..',
        '# Voer een oproep in..',
        '# Entrez indicaif SVP',
        '# Zadejte prosím call..',
        '# Proszę podać call..',
        '# Por favor escreva o indicativo...',
        '# Inserisci il call..',
        '# Пожалуйста, введите call..',
        '# Будь ласка, введіть call..'),

    'cmd_c_badCall': (
        '# Ungültiger Ziel Call..',
        '# Invalid destination call..',
        '# Ongeldige bestemmingsoproep..',
        '# indicatif de destinantion invalide..',
        '# Neplatný cílový call..',
        '# Nieprawidłowy call docelowy..',
        '# Indicativo de destino inválido..',
        '# Call di destinazione non valido..',
        '# Неверный целевой call..',
        '# Недійсний цільовий call..'),

    'cmd_c_badPort': (
        '# Ungültige Port Angabe..',
        '# Invalid port specification..',
        '# Ongeldige poortspecificatie..',
        '# Spécification de port invalide',
        '# Neplatná specifikace portu..',
        '# Nieprawidłowa specyfikacja portu..',
        '# Especificação de porta inválida..',
        '# Specifica di porta non valida..',
        '# Неверная спецификация порта..',
        '# Недійсна специфікація порту..'),

    'cmd_c_noPort': (
        '# Ungültiger Port..',
        '# Invalid port..',
        '# Ongeldige poort..',
        '# Port invalide..',
        '# Neplatný port..',
        '# Nieprawidłowy port..',
        '# Porta inválida..',
        '# Porta non valida..',
        '# Неверный порт..',
        '# Недійсний порт..'),

    'ch_cmd_param_error': (
        '# Ungültige Parameter. CH <Kanal> Nachricht',
        '# Invalid parameters. CH <Channel> Message',
        '# Ongeldige parameters. CH <Kanaal> Bericht',
        '# Paramètres non valides. Message CH <Channel>',
        '# Neplatné parametry. CH <Kanál> Zpráva',
        '# Nieprawidłowe parametry. CH <Kanał> Wiadomość',
        '# Parâmetros inválidos. CH <Canal> Mensagem',
        '# Parametri non validi. CH <Canale> Messaggio',
        '# Неверные параметры. CH <Канал> Сообщение',
        '# Недійсні параметри. CH <Канал> Повідомлення'),

    'ch_cmd_empty_ch': (
        '# Ungültiger Kanal. Kanal nicht verbunden.',
        '# Invalid channel. Channel not connected.',
        '# Ongeldig kanaal. Kanaal niet verbonden.',
        '# Chaîne invalide. Chaîne non connectée.',
        '# Neplatný kanál. Kanál není připojen.',
        '# Nieprawidłowy kanał. Kanał niepołączony.',
        '# Canal inválido. Canal não conectado.',
        '# Canale non valido. Canale non connesso.',
        '# Неверный канал. Канал не подключён.',
        '# Недійсний канал. Канал не підключено.'),
    # ==================

    'ch_cmd_own_ch': (
        '# Kann keine Nachricht an eigenen Kanal senden.',
        '# Cannot send message to own channel.',
        '# Kan geen bericht naar eigen kanaal sturen.',
        "# Impossible d'envoyer un message à sa propre chaîne.",
        '# Nelze poslat zprávu na vlastní kanál.',
        '# Nie można wysłać wiadomości na własny kanał.',
        '# Não é possível enviar mensagem para o próprio canal.',
        '# Impossibile inviare messaggio al proprio canale.',
        '# Невозможно отправить сообщение на собственный канал.',
        '# Неможливо надіслати повідомлення на власний канал.'),

    'ch_cmd_send': (
        '# Nachricht an Kanal {} ({}) gesendet.\r',
        '# Message sent to channel {} ({}).\r',
        '# Bericht verzonden naar kanaal {} ({}).\r',
        "# Message envoyé au canal {} ({}).\r",
        '# Zpráva odeslána na kanál {} ({}).\r',
        '# Wiadomość wysłana na kanał {} ({}).\r',
        '# Mensagem enviada para o canal {} ({}).\r',
        '# Messaggio inviato al canale {} ({}).\r',
        '# Сообщение отправлено в канал {} ({}).\r',
        '# Повідомлення надіслано до каналу {} ({}).\r'),

    'cmd_bwstat_1': (
        'Gesamte Bandauslastung (letzte 10 Minuten, alle Ports)',
        'Total bandwidth utilization (last 10 minutes, all ports)',
        'Totaal bandbreedtegebruik (laatste 10 minuten, alle poorten)',
        'Utilisation totale de la bande passante (10 dernières minutes, tous ports)',
        'Celková zátěž pásma (posledních 10 minut, všechny porty)',
        'Całkowite wykorzystanie pasma (ostatnie 10 minut, wszystkie porty)',
        'Utilização total da largura de banda (últimos 10 minutos, todas as portas)',
        'Utilizzo totale della banda (ultimi 10 minuti, tutte le porte)',
        'Общая загрузка диапазона (последние 10 минут, все порты)',
        'Загальна завантаженість діапазону (останні 10 хвилин, всі порти)'),

    'cmd_bwstat_2': (
        'Bandauslastung aller Ports (%) – 10-Minuten-Verlauf',
        'Band utilization of all ports (%) – 10-minute trend',
        'Bandgebruik van alle poorten (%) – 10-minutentrend',
        'Utilisation de la bande passante de tous les ports (%) – Évolution sur 10 minutes',
        'Vytížení všech portů (%) – 10minutový průběh',
        'Wykorzystanie pasma wszystkich portów (%) – trend 10-minutowy',
        'Utilização de banda de todas as portas (%) – Tendência 10 minutos',
        'Utilizzo banda di tutte le porte (%) – Trend 10 minuti',
        'Загрузка всех портов (%) – 10-минутный тренд',
        'Завантаження всіх портів (%) – 10-хвилинний тренд'),

    'cmd_bwstat_3': (
        'Bandauslastung Port {} (%) – 10-Minuten-Verlauf',
        'Band utilization port {} (%) – 10-minute trend',
        'Bandgebruikpoort {} (%) – 10-minutentrend',
        'Utilisation de la bande passante (%) – Tendance sur 10 minutes',
        'Vytížení portu {} (%) – 10minutový průběh',
        'Wykorzystanie pasma port {} (%) – trend 10-minutowy',
        'Utilização da banda porta {} (%) – Tendência 10 minutos',
        'Utilizzo banda porta {} (%) – Trend 10 minuti',
        'Загрузка порта {} (%) – 10-минутный тренд',
        'Завантаження порту {} (%) – 10-хвилинний тренд'),

    'last_30_days': (
        'letzte 30 Tage',
        'last 30 days',
        'laatste 30 dagen',
        '30 derniers jours',
        'posledních 30 dní',
        'ostatnie 30 dni',
        'últimos 30 dias',
        'ultimi 30 giorni',
        'последние 30 дней',
        'останні 30 днів'),

    'cmd_chist_tab': (
        'Datum      Zeit     Dauer   Call      Port  Locator / Distanz\r',
        'Date       Time     Dur.    Call      Port  Locator / Distance\r',
        'Datum      Tijd     Duur    Call      Port  Locator / Afstand\r',
        'Date       Temps    Durée   Call      Port  Locator / Distance\r',
        'Datum      Čas      Doba    Call      Port  Lokátor / Vzdálenost\r',
        'Data       Czas     Czas    Call      Port  Locator / Odległość\r',
        'Data       Hora     Duração Call      Porta Locator / Distância\r',
        'Data       Ora      Durata  Call      Porta Locator / Distanza\r',
        'Дата       Время    Длит.   Call      Порт  Локатор / Расстояние\r',
        'Дата       Час      Тривал. Call      Порт  Локатор / Відстань\r'),

    #####################################################
    # MCast

    'cmd_help_mcast_move_ch': (
        'MCast Kanal wechseln',
        'Change MCast channel',
        'MCast kanaal wijzigen',
        'Changer canal MCAST',
        'MCast změna kanálu',
        'MCast zmień kanał',
        'Mudar canal MCast',
        'Cambia canale MCast',
        'Сменить канал MCast',
        'Змінити канал MCast'),

    'cmd_help_mcast_ch_info': (
        'MCast Kanal Info',
        'MCast channel info',
        'MCast kanaalinformatie',
        'Info canal MCAST',
        'MCast info kanálu',
        'MCast info kanału',
        'Info canal MCast',
        'Info canale MCast',
        'Инфо о канале MCast',
        'Інфо про канал MCast'),

    'cmd_help_mcast_channels': (
        'MCast Kanal Übersicht',
        'MCast channel overview',
        'MCast kanaaloverzicht',
        'Aperçu canal MCAST',
        'MCast přehled kanálů',
        'MCast przegląd kanałów',
        'Visão geral canais MCast',
        'Panoramica canali MCast',
        'Обзор каналов MCast',
        'Огляд каналів MCast'),

    'cmd_help_mcast_set_axip': (
        'Eigene AXIP Adresse eintragen / anzeigen lassen',
        'Enter/display your own AXIP address',
        'Voer/toon uw eigen AXIP-adres in',
        'Entrez/afficher votre adresse AXIP',
        'Zadat/zobrazit vlastní AXIP adresu',
        'Wpisz/pokaż swój adres AXIP',
        'Escrever/mostrar o teu endereço AXIP',
        'Inserisci/visualizza il tuo indirizzo AXIP',
        'Ввести/показать свой AXIP адрес',
        'Ввести/показати свій AXIP адрес'),

    'mcast_new_user_beacon': (
        '-= Willkommen auf dem AXIP-MCast Server. Registriere dich auf {} =-',
        '-= Welcome to the AXIP-MCast Server. Please connect {} to register =-',
        '-= Welcome to the AXIP-MCast Server. Please connect {} to register =-',
        '-= Bienvenue sur le serveur AXIP-MCast. Veuillez vous connecter {} pour vous enregistrer =-',
        '-= Vítejte na AXIP-MCast serveru. Registrujte se na {} =-',
        '-= Witaj na serwerze AXIP-MCast. Połącz się z {} aby się zarejestrować =-',
        '-= Bem-vindo ao servidor AXIP-MCast. Conecte-se a {} para se registar =-',
        '-= Benvenuto sul server AXIP-MCast. Connettiti a {} per registrarti =-',
        '-= Добро пожаловать на AXIP-MCast сервер. Подключись к {} для регистрации =-',
        '-= Ласкаво просимо на AXIP-MCast сервер. Підключись до {} для реєстрації =-'),

    'mcast_new_user_reg_beacon': (
        ('-= Du wurdest erfolgreich auf dem MCast-Server registriert =-\r'
         '-= Du befindest dich auf Kanal {} ({}) =-'),
        ('-= You have been successfully registered on the MCast server =-\r'
         '-= You are on channel {} ({}) =-'),
        ('-= U bent succesvol geregistreerd op de MCast-server. =-\r'
         '-= Je bevindt je op kanaal {} ({}) =-'),
        ('-= Vous avez été enregistré avec succès sur le serveur MCast =-\r'
         '-= Vous êtes sur le canal {} ({}) =-'),
        ('-= Byl jste úspěšně registrován na MCast serveru =-\r'
         '-= Nacházíte se na kanálu {} ({}) =-'),
        ('-= Zostałeś pomyślnie zarejestrowany na serwerze MCast =-\r'
         '-= Jesteś na kanale {} ({}) =-'),
        ('-= Foi registado com sucesso no servidor MCast =-\r'
         '-= Encontra-se no canal {} ({}) =-'),
        ('-= Sei stato registrato con successo sul server MCast =-\r'
         '-= Sei sul canale {} ({}) =-'),
        ('-= Вы успешно зарегистрированы на MCast сервере =-\r'
         '-= Вы на канале {} ({}) =-'),
        ('-= Ви успішно зареєстровані на MCast сервері =-\r'
         '-= Ви на каналі {} ({}) =-')),

    'mcast_user_enters_channel_beacon': (
        '-= {} hat den Kanal betreten =-',
        '-= {} has entered the channel =-',
        '-= {} is het kanaal binnengekomen =-',
        '-= {} est arrivé sur le canal =-',
        '-= {} vstoupil na kanál =-',
        '-= {} wszedł na kanał =-',
        '-= {} entrou no canal =-',
        '-= {} è entrato nel canale =-',
        '-= {} вошёл в канал =-',
        '-= {} увійшов у канал =-'),

    'mcast_user_left_channel_beacon': (
        '-= {} hat den Kanal verlassen =-',
        '-= {} has left the channel =-',
        '-= {} het kanaal verlaten =-',
        '-= {} a quité le canal',
        '-= {} opustil kanál =-',
        '-= {} opuścił kanał =-',
        '-= {} saiu do canal =-',
        '-= {} ha lasciato il canale =-',
        '-= {} покинул канал =-',
        '-= {} залишив канал =-'),

    #####################################################
    # BOX CLI
    'hint_no_mail_for': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # Keine Mails vorhanden: {}',
        '\r # No mails available: {}',
        '\r # Geen mails beschikbaar: {}',
        '\r # Aucun mail disponible: {}',
        '\r # Žádné maily k dispozici: {}',
        '\r # Brak maili: {}',
        '\r # Nenhuma mensagem disponível: {}',
        '\r # Nessuna mail disponibile: {}',
        '\r # Нет писем: {}',
        '\r # Немає листів: {}'),

    'hint_no_mail': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # Keine Mails vorhanden',
        '\r # No mails available',
        '\r # Geen mails beschikbaar',
        '\r # Aucun mail disponible',
        '\r # Žádné maily',
        '\r # Brak maili',
        '\r # Nenhuma mensagem',
        '\r # Nessuna mail',
        '\r # Нет писем',
        '\r # Немає листів'),

    'cmd_fwdinfo': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        'Zeigt Forward-Statistiken',
        'Shows forward statistics',
        'Toont voorwaartse statistieken',
        'Affiche les statistiques avancées',
        'Zobrazí Forward statistiky',
        'Pokazuje statystyki Forward',
        'Mostra estatísticas de Forward',
        'Mostra statistiche Forward',
        'Показывает статистику Forward',
        'Показує статистику Forward'),

    'cmd_r': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '<MSG#>: Liest die Nachricht mit der entspr. Nummer aus.',
        '<MSG#>: Reads the message with the corresponding number.',
        '<MSG#>: Leest het bericht met het bijbehorende nummer.',
        '<MSG#>: lecture du message correspondant au numéro de message.',
        '<MSG#>: Přečte zprávu s odpovídajícím číslem.',
        '<MSG#>: Odczytuje wiadomość o podanym numerze.',
        '<MSG#>: Lê a mensagem com o número correspondente.',
        '<MSG#>: Legge il messaggio con il numero corrispondente.',
        '<MSG#>: Читает сообщение с указанным номером.',
        '<MSG#>: Читає повідомлення з вказаним номером.'),

    'cmd_sp': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        'SP <Call> @ <BBS>: Sendet eine persoenliche Nachricht an Rufzeichen',
        'SP <Call> @ <BBS>: Sends a personal message to call sign',
        'SP <Call> @ <BBS>: Stuurt een persoonlijk bericht naar roepnamen',
        'SP <Call> @ <BBS>: Envoie un message personnel à l\'indicatid',
        'SP <Call> @ <BBS>: Pošle osobní zprávu volací značce',
        'SP <Call> @ <BBS>: Wysyła wiadomość osobistą do znaku',
        'SP <Call> @ <BBS>: Envia mensagem pessoal para indicativo',
        'SP <Call> @ <BBS>: Invia messaggio personale a nominativo',
        'SP <Call> @ <BBS>: Отправляет личное сообщение callsign',
        'SP <Call> @ <BBS>: Надсилає особисте повідомлення callsign'),

    'cmd_sb': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        ('SB <Rubrik> @ <Verteiler>: Sendet ein Bulletin in eine Rubrik \r'
         '              fuer mehrere Boxen in einer Region.'),
        ('SB <Category> @ <Distribution>: Sends a bulletin to a category \r'
         '              for multiple boxes in a region.'),
        ('SB <categorie> @ <distributie>: Stuurt een bulletin naar een categorie \r'
         '              voor meerdere dozen in een regio.'),
        ('SB <Catégorie> @ <Distribution>: Envoie un bulletin a la categorie \r'
         '              pour plusieurs boites dans une région.'),
        ('SB <Rubrika> @ <Distribuce>: Pošle bulletin do rubriky \r'
         '              pro více boxů v regionu.'),
        ('SB <Rubryka> @ <Dystrybucja>: Wysyła biuletyn do rubryki \r'
         '              dla wielu skrzynek w regionie.'),
        ('SB <Categoria> @ <Distribuição>: Envia boletim para categoria \r'
         '              para várias BBSs na região.'),
        ('SB <Categoria> @ <Distribuzione>: Invia bulletin in categoria \r'
         '              per multiple box nella regione.'),
        ('SB <Рубрика> @ <Рассылка>: Отправляет бюллетень в рубрику \r'
         '              для нескольких боксов в регионе.'),
        ('SB <Рубрика> @ <Розсилка>: Надсилає бюлетень в рубрику \r'
         '              для кількох боксів у регіоні.')),

    'cmd_sr': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        ('SR <Msg#> : Sendet eine Antwort zurueck an den Absender\r'
         '              der <Msg#> = Nachricht Nummer (Send Reply).'),
        ('SR <Msg#> : Sends a reply back to the sender\r'
         '              of <Msg#> = message number (Send Reply).'),
        ('SR <Msg#> : Stuurt een antwoord terug naar de afzender\r'
         '              van <Msg#> = berichtnummer (Send Reply).'),
        ("SR <Msg#>: renvoie une réponse à l'expéditeur\r"
         "              de <Msg#> = numéro de message (Send Reply)."),
        ('SR <Msg#>: Pošle odpověď zpět odesílateli\r'
         '              <Msg#> = číslo zprávy (Send Reply).'),
        ('SR <Msg#>: Wysyła odpowiedź do nadawcy\r'
         '              <Msg#> = numer wiadomości (Send Reply).'),
        ('SR <Msg#>: Envia resposta de volta ao remetente\r'
         '              <Msg#> = número da mensagem (Send Reply).'),
        ('SR <Msg#>: Invia risposta al mittente\r'
         '              <Msg#> = numero messaggio (Send Reply).'),
        ('SR <Msg#>: Отправляет ответ отправителю\r'
         '              <Msg#> = номер сообщения (Send Reply).'),
        ('SR <Msg#>: Надсилає відповідь відправнику\r'
         '              <Msg#> = номер повідомлення (Send Reply).')),

    'cmd_ln': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        'Listet alle eigenen neuen Nachrichten auf.',
        'Lists all of your own new messages.',
        'Geeft al uw eigen nieuwe berichten weer.',
        'Liste tous vos nouveaux messages',
        'Zobrazí všechny vaše nové zprávy.',
        'Listuje wszystkie twoje nowe wiadomości.',
        'Lista todas as suas novas mensagens.',
        'Elenca tutti i tuoi nuovi messaggi.',
        'Показывает все ваши новые сообщения.',
        'Показує всі ваші нові повідомлення.'),

    'cmd_lm': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        'Listet alle eigenen Nachrichten.',
        'Lists all of your own messages.',
        'Geeft al uw eigen berichten weer.',
        'Liste tous vos messages',
        'Zobrazí všechny vaše zprávy.',
        'Listuje wszystkie twoje wiadomości.',
        'Lista todas as suas mensagens.',
        'Elenca tutti i tuoi messaggi.',
        'Показывает все ваши сообщения.',
        'Показує всі ваші повідомлення.'),

    'cmd_ll': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '<Anzahl>: Listet die neuesten Nachrichten in der ang. Zahl.',
        '<Number>: Lists the latest news in the specified number.',
        '<nummer>: Geeft de laatste berichten in het opgegeven nummer weer.',
        '<number>: Répertorie les derniers messages dans le numéro spécifié.',
        '<Počet>: Zobrazí posledních N zpráv.',
        '<Liczba>: Wyświetla najnowsze wiadomości w podanej liczbie.',
        '<Número>: Lista as mensagens mais recentes na quantidade indicada.',
        '<Numero>: Elenca gli ultimi messaggi nel numero specificato.',
        '<Кол-во>: Показывает последние N сообщений.',
        '<Кількість>: Показує останні N повідомлень.'),

    'cmd_l_from': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '<CALL>: Listet Bulletins VON einem Rufzeichen.',
        '<CALL>: Lists bulletins FROM a callsign.',
        '<CALL>: Geeft een lijst met bulletins VAN een roepnaam.',
        "<CALL>: Répertorie les bulletins À PARTIR d'un indicatif d'appel.",
        '<CALL>: Zobrazí bulletiny OD volací značky.',
        '<CALL>: Listuje biuletyny OD znaku.',
        '<CALL>: Lista boletins DE um indicativo.',
        '<CALL>: Elenca bulletin DA un nominativo.',
        '<CALL>: Показывает бюллетени ОТ callsign.',
        '<CALL>: Показує бюлетені ВІД callsign.'),

    'cmd_l_to': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '<CALL/RUBRIK>: Listet Nachrichten AN ein Rufzeichen oder Rubrik.',
        '<CALL/RUBRIK>: Lists messages TO a call sign or heading.',
        '<CALL/RUBRIK>: Geeft een lijst weer van berichten NAAR een roepnaam of kop.',
        "<CALL/RUBRIK>: répertorie les messages VERS un indicatif d'appel ou un titre.",
        '<CALL/RUBRIK>: Zobrazí zprávy PRO značku nebo rubriku.',
        '<CALL/RUBRIK>: Listuje wiadomości DO znaku lub rubryki.',
        '<CALL/RUBRIK>: Lista mensagens PARA indicativo ou rúbrica.',
        '<CALL/RUBRIK>: Elenca messaggi PER nominativo o categoria.',
        '<CALL/RUBRIK>: Показывает сообщения ДЛЯ callsign или рубрики.',
        '<CALL/RUBRIK>: Показує повідомлення ДЛЯ callsign або рубрики.'),

    'cmd_l_at': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '<CALL>: Listet Bulletins VIA Verteiler.',
        '<CALL>: Lists bulletins VIA distribution.',
        '<CALL>: Geeft bulletins weer VIA distributielijst.',
        "<CALL>: Répertorie les bulletins VIA de distribution.",
        '<CALL>: Zobrazí bulletiny VIA distribuce.',
        '<CALL>: Listuje biuletyny VIA dystrybucja.',
        '<CALL>: Lista boletins VIA distribuidor.',
        '<CALL>: Elenca bulletin VIA distribuzione.',
        '<CALL>: Показывает бюллетени ЧЕРЕЗ рассылку.',
        '<CALL>: Показує бюлетені ЧЕРЕЗ розсилку.'),

    'cmd_lb': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        'Listet alle Bulletin Nachrichten.',
        'Lists all bulletin messages.',
        'Geeft een overzicht van alle bulletinberichten.',
        'Liste tous les messages bulletins',
        'Zobrazí všechny bulletin zprávy.',
        'Listuje wszystkie wiadomości bulletin.',
        'Lista todas as mensagens boletim.',
        'Elenca tutti i messaggi bulletin.',
        'Показывает все бюллетени.',
        'Показує всі бюлетені.'),

    'cmd_km': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        'Loescht alle pers. Nachrichten, die man bereits gelesen hat.',
        'Deletes all personal messages that you have already read.',
        'Verwijdert alle persoonlijke berichten die u al hebt gelezen.',
        'Supprime tous les messages personnels que vous avez déjà lus »',
        'Smaže všechny osobní zprávy, které jste již přečetl.',
        'Usuwa wszystkie przeczytane wiadomości osobiste.',
        'Elimina todas as mensagens pessoais já lidas.',
        'Elimina tutti i messaggi personali già letti.',
        'Удаляет все прочитанные личные сообщения.',
        'Видаляє всі прочитані особисті повідомлення.'),

    'cmd_k': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '<MSG#>: Loescht die Nachricht mit der entspr. Nummer.',
        '<MSG#>: Deletes the message with the corresponding number.',
        '<MSG#>: Verwijdert het bericht met het bijbehorende nummer.',
        '<MSG#>: Supprime le message portant ce numéro',
        '<MSG#>: Smaže zprávu s daným číslem.',
        '<MSG#>: Usuwa wiadomość o podanym numerze.',
        '<MSG#>: Elimina a mensagem com o número correspondente.',
        '<MSG#>: Elimina il messaggio con il numero corrispondente.',
        '<MSG#>: Удаляет сообщение с указанным номером.',
        '<MSG#>: Видаляє повідомлення з вказаним номером.'),

    'cmd_mr': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        'Markiert alle pers. Nachrichten als gelesen.',
        'Marks all personal messages as read.',
        'Markeert alle persoonlijke berichten als gelezen.',
        'Marque tous les messages personnels comme lus.',
        'Označí všechny osobní zprávy jako přečtené.',
        'Oznacza wszystkie wiadomości osobiste jako przeczytane.',
        'Marca todas as mensagens pessoais como lidas.',
        'Marca tutti i messaggi personali come letti.',
        'Отмечает все личные сообщения как прочитанные.',
        'Позначає всі особисті повідомлення як прочитані.'),

    'box_cmd_mr_msg': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # {} Nachricht(en) wurde(n) als gelesen markiert.\r',
        '\r # {} message(s) were marked as read.\r',
        '\r # {} bericht(en) zijn gemarkeerd als gelezen.\r',
        '\r # {} message(s) ont été marqués comme lus.\r',
        '\r # {} zpráv(a/y) označeno jako přečtené.\r',
        '\r # {} wiadomość(i) oznaczono jako przeczytane.\r',
        '\r # {} mensagem(ns) marcada(s) como lida(s).\r',
        '\r # {} messaggio(i) marcati come letti.\r',
        '\r # {} сообщение(й) отмечено как прочитанное.\r',
        '\r # {} повідомлення позначено як прочитане.\r'),

    'cmd_op': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        'Anzahl der Zeilen pro Seite. Nur OP aus.',
        'Number of lines per page. Just OP = off.',
        'Aantal regels per pagina. OP alleen = uit',
        'Nombre de lignes par page. Juste OP = off.',
        'Počet řádků na stránku. OP = vypnuto.',
        'Liczba linii na stronę. OP = wyłączone.',
        'Número de linhas por página. OP = desligado.',
        'Numero di righe per pagina. OP = off.',
        'Количество строк на страницу. OP = выкл.',
        'Кількість рядків на сторінку. OP = вимк.'),

    'op_prompt_0': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # (A)=Abbruch, (O)=weiter ohne Stop, (Return)=weiter -->',
        '\r # (A)=Cancel, (O)=continue without stopping, (Return)=continue -->',
        '\r # (A)=Annuleren, (O)=doorgaan zonder te stoppen, (Terug)=doorgaan -->',
        '\r # (A)=Annuler, (O)=continuer sans arrêt, (Return)=continuer -->',
        '\r # (A)=Zrušit, (O)=pokračovat bez stopu, (Return)=dále -->',
        '\r # (A)=Anuluj, (O)=kontynuuj bez zatrzymania, (Return)=dalej -->',
        '\r # (A)=Cancelar, (O)=continuar sem parar, (Return)=continuar -->',
        '\r # (A)=Annulla, (O)=continua senza fermarti, (Return)=avanti -->',
        '\r # (A)=Отмена, (O)=продолжить без остановки, (Return)=далее -->',
        '\r # (A)=Скасувати, (O)=продовжити без зупинки, (Return)=далі -->'),

    'op_prompt_1': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # (A)=Abbruch, (R)=Lesen, (Return)=weiter -->',
        '\r # (A)=Cancel, (R)=Read, (Return)=continue -->',
        '\r # (A)=Annuleren, (R)=Lezen, (Terug)=doorgaan -->',
        '\r # (A)=Annuler, (R)=Lire, (Return)=continuer -->',
        '\r # (A)=Zrušit, (R)=Číst, (Return)=dále -->',
        '\r # (A)=Anuluj, (R)=Czytaj, (Return)=dalej -->',
        '\r # (A)=Cancelar, (R)=Ler, (Return)=continuar -->',
        '\r # (A)=Annulla, (R)=Leggi, (Return)=avanti -->',
        '\r # (A)=Отмена, (R)=Читать, (Return)=далее -->',
        '\r # (A)=Скасувати, (R)=Читати, (Return)=далі -->'),

    'aprs_new_mail_ctext': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # APRS: Du hast {} neue Nachricht(en). Lesen mit AMS\r',
        '\r # APRS: You have {} new message(s). Reading with AMS\r',
        '\r # APRS: Je hebt {} nieuwe bericht(en). Lezen met AMS\r',
        '\r # APRS: Vous avez {} nouveau(x) message(s). Lire avec AMS\r',
        '\r # APRS: Máte {} novou zprávu(y). Čtěte pomocí AMS\r',
        '\r # APRS: Masz {} nową wiadomość(i). Czytaj za pomocą AMS\r',
        '\r # APRS: Tem {} nova(s) mensagem(ns). Ler com AMS\r',
        '\r # APRS: Hai {} nuovo(i) messaggio(i). Leggi con AMS\r',
        '\r # APRS: У вас {} новое(ых) сообщение(й). Читать с AMS\r',
        '\r # APRS: У вас {} нове(их) повідомлення(ь). Читати через AMS\r'),

    'box_new_mail_ctext': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # BOX: Du hast {} neue Mail(s).\r',
        '\r # BOX: You have {} new mails.\r',
        '\r # BOX: Je hebt {} nieuwe mails.\r',
        '\r # BOX: Vous avez {} nouveaux mails.\r',
        '\r # BOX: Máte {} novou mail(y).\r',
        '\r # BOX: Masz {} nową wiadomość(i).\r',
        '\r # BOX: Tem {} novo(s) mail(s).\r',
        '\r # BOX: Hai {} nuova(e) mail.\r',
        '\r # BOX: У вас {} новое(ых) письмо(ем).\r',
        '\r # BOX: У вас {} нове(их) лист(ів).\r'),

    'box_no_hbbs_address': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # Du hast noch keine Heimat-BBS eingetragen. PR <CALL.Verteiler>\r',
        "\r # You haven't entered a home BBS yet. PR <CALL.Distribution>\r",
        '\r # U hebt nog geen thuis-BBS ingevoerd. PR <CALL.Distributie>\r',
        "\r # Vous n'avez pas encore entré de BBS personnel. PR <CALL.Distribution>\r",
        '\r # Nemáte ještě nastavenou domovskou BBS. PR <CALL.Distribuce>\r',
        '\r # Nie masz jeszcze wpisanej BBS domowej. PR <CALL.Dystrybucja>\r',
        '\r # Ainda não tem BBS oficial definida. PR <CALL.Distribuição>\r',
        '\r # Non hai ancora impostato una Home BBS. PR <CALL.Distribuzione>\r',
        '\r # У вас ещё не указана домашняя BBS. PR <CALL.Рассylка>\r',
        '\r # У вас ще немає домашньої BBS. PR <CALL.Розсилка>\r'),

    'box_cmd_op2': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # OP: Fehler, ungültiger Parameter.\r',
        '\r # OP : Error, Invalid Parameter.\r',
        '\r # OP: Fout, ongeldige parameter.\r',
        '\r # OP : Erreur, Paramètre Invalide.\r',
        '\r # OP: Chyba, neplatný parametr.\r',
        '\r # OP: Błąd, nieprawidłowy parametr.\r',
        '\r # OP: Erro, parâmetro inválido.\r',
        '\r # OP: Errore, parametro non valido.\r',
        '\r # OP: Ошибка, неверный параметр.\r',
        '\r # OP: Помилка, недійсний параметр.\r'),

    'box_cmd_op1': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # OP : Kein Seitenstop.\r',
        '\r # OP : No side stop.\r',
        '\r # OP: Geen zijstop.\r',
        '\r # OP :Pas de pagination.\r',
        '\r # OP: Bez zastavování stránky.\r',
        '\r # OP: Bez stopu stron.\r',
        '\r # OP: Sem paragem de página.\r',
        '\r # OP: Nessuna interruzione pagina.\r',
        '\r # OP: Без остановки страниц.\r',
        '\r # OP: Без зупинки сторінок.\r'),

    'box_cmd_op3': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # OP : Seitenstop auf {} Zeilen eingestellt.\r',
        '\r # OP : Page stop set to {} lines.\r',
        '\r # OP: Paginastop ingesteld op {} regels.\r',
        '\r # OP : Pagination de {} lignes.\r',
        '\r # OP: Zastavení stránky nastaveno na {} řádků.\r',
        '\r # OP: Stop stron ustawiony na {} linii.\r',
        '\r # OP: Paragem de página definida para {} linhas.\r',
        '\r # OP: Interruzione pagina impostata a {} righe.\r',
        '\r # OP: Остановка страниц установлена на {} строк.\r',
        '\r # OP: Зупинка сторінок встановлена на {} рядків.\r'),

    'box_lm_header': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        'Msg#  TSLD Byte   An    @ BBS   Von    Dat./Zeit Titel\r',
        'Msg#  TSLD Byte   To    @ BBS   From   Dat./Time Head\r',
        'Msg#  TSLD Byte   Naar  @ BBS   Van    Dat./Tijd Titel\r',
        'Msg#  TSLD Byte   Pour  @ BBS   De     Dat./Heure Titre\r',
        'Msg#  TSLD Byte   Komu  @ BBS   Od     Dat./Čas  Nadpis\r',
        'Msg#  TSLD Byte   Do    @ BBS   Od     Data/Czas Tyt.\r',
        'Msg#  TSLD Byte   Para  @ BBS   De     Data/Hora Título\r',
        'Msg#  TSLD Byte   A     @ BBS   Da     Data/Ora  Titolo\r',
        'Msg#  TSLD Байт   Кому  @ BBS   От     Дата/Время Тема\r',
        'Msg#  TSLD Байт   Кому  @ BBS   Від    Дата/Час  Тема\r'),

    'box_r_no_msg_found': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r\r # Nachricht {} nicht gefunden !\r\r',
        '\r\r # Message {} not found! \r\r',
        '\r\r # Bericht {} niet gevonden!\r\r',
        '\r\r # Message {} non trouvé! \r\r',
        '\r\r # Zpráva {} nenalezena!\r\r',
        '\r\r # Wiadomość {} nie znaleziona!\r\r',
        '\r\r # Mensagem {} não encontrada!\r\r',
        '\r\r # Messaggio {} non trovato!\r\r',
        '\r\r # Сообщение {} не найдено!\r\r',
        '\r\r # Повідомлення {} не знайдено!\r\r'),

    'box_parameter_error': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # Fehler, ungültiger Parameter.\r',
        '\r # Error, Invalid Parameter.\r',
        '\r # Fout, ongeldige parameter.\r',
        '\r # Erreur, Paramètre invalide.\r',
        '\r # Chyba, neplatný parametr.\r',
        '\r # Błąd, nieprawidłowy parametr.\r',
        '\r # Erro, parâmetro inválido.\r',
        '\r # Errore, parametro non valido.\r',
        '\r # Ошибка, неверный параметр.\r',
        '\r # Помилка, недійсний параметр.\r'),

    'box_msg_error': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # Interner Fehler, kann Nachricht nicht lesen.\r',
        '\r # Internal error, cannot read message.\r',
        '\r # Interne fout, kan bericht niet lezen.\r',
        '\r # Erreur interne, impossible lire message.\r',
        '\r # Interní chyba, nelze přečíst zprávu.\r',
        '\r # Błąd wewnętrzny, nie można odczytać wiadomości.\r',
        '\r # Erro interno, não é possível ler a mensagem.\r',
        '\r # Errore interno, impossibile leggere il messaggio.\r',
        '\r # Внутренняя ошибка, невозможно прочитать сообщение.\r',
        '\r # Внутрішня помилка, неможливо прочитати повідомлення.\r'),

    'box_msg_foter': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r\r--- Ende der Nachricht #{} an {} von {} BID:{} ---\r\r',
        '\r\r--- End of message #{} to {} from {} BID:{} ---\r\r',
        '\r\r--- Einde van bericht #{} tot {} van {} BID:{} ---\r\r',
        '\r\r--- Fin des messages #{} por {} de {} BID:{} ---\r\r',
        '\r\r--- Konec zprávy #{} pro {} od {} BID:{} ---\r\r',
        '\r\r--- Koniec wiadomości #{} do {} od {} BID:{} ---\r\r',
        '\r\r--- Fim da mensagem #{} para {} de {} BID:{} ---\r\r',
        '\r\r--- Fine del messaggio #{} a {} da {} BID:{} ---\r\r',
        '\r\r--- Конец сообщения #{} для {} от {} BID:{} ---\r\r',
        '\r\r--- Кінець повідомлення #{} для {} від {} BID:{} ---\r\r'),

    'box_msg_del': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # Es wurden {} Nachricht(en) gelöscht.\r',
        '\r # {} messages have been deleted.\r',
        '\r # {} berichten zijn verwijderd.\r',
        '\r # {} messages ont été supprimés.\r',
        '\r # Bylo smazáno {} zpráv(y).\r',
        '\r # Usunięto {} wiadomość(i).\r',
        '\r # Foram eliminadas {} mensagem(ns).\r',
        '\r # Sono stati eliminati {} messaggio(i).\r',
        '\r # Удалено {} сообщение(й).\r',
        '\r # Видалено {} повідомлення(ь).\r'),

    'box_msg_del_k': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # Nachricht(en) {} wurde(n) gelöscht.\r',
        '\r # Message(s) {} have been deleted.\r',
        '\r # Berichte(n) {} zijn verwijderd.\r',
        '\r # {} Message(s) supprimés.\r',
        '\r # Zpráva(y) {} byla(y) smazána(y).\r',
        '\r # Wiadomość(i) {} została(y) usunięta(y).\r',
        '\r # Mensagem(ns) {} eliminada(s).\r',
        '\r # Messaggio(i) {} eliminato(i).\r',
        '\r # Сообщение(я) {} удалено(ы).\r',
        '\r # Повідомлення {} видалено.\r'),

    'box_error_no_address': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # Kein Empfänger angegeben. SP XX0XX oder SP XX0XX@XBBS0\r',
        '\r # No recipient specified. SP XX0XX or SP XX0XX@XBBS0.\r',
        '\r # Geen ontvanger opgegeven. SP XX0XX of SP XX0XX@XBBS0.\r',
        '\r # Pas de recipient specifié. SP XX0XX or SP XX0XX@XBBS0.\r',
        '\r # Není zadán příjemce. SP XX0XX nebo SP XX0XX@XBBS0\r',
        '\r # Nie podano odbiorcy. SP XX0XX lub SP XX0XX@XBBS0\r',
        '\r # Nenhum destinatário indicado. SP XX0XX ou SP XX0XX@XBBS0\r',
        '\r # Nessun destinatario specificato. SP XX0XX o SP XX0XX@XBBS0\r',
        '\r # Не указан получатель. SP XX0XX или SP XX0XX@XBBS0\r',
        '\r # Не вказано отримувача. SP XX0XX або SP XX0XX@XBBS0\r'),

    'box_error_invalid_dist': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # Kein Verteiler in BBS-Adresse {}\r',
        '\r # No distribution list in BBS address {}\r',
        '\r # Geen distributeur in BBS-adres {}\r',
        '\r # Pas de liste de distribution dans l\'adresse BBS address {}\r',
        '\r # Chybí distribuce v BBS adrese {}\r',
        '\r # Brak dystrybucji w adresie BBS {}\r',
        '\r # Sem distribuidor no endereço BBS {}\r',
        '\r # Nessuna distribuzione nell\'indirizzo BBS {}\r',
        '\r # Нет рассылки в BBS адресе {}\r',
        '\r # Немає розсилки в BBS адресі {}\r'),

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
        ('\r # Routing: {}\r'
         'Název zprávy pro {}:\r'),
        ('\r # Routing: {}\r'
         'Tytuł wiadomości do {}:\r'),
        ('\r # Routing: {}\r'
         'Título da mensagem para {}:\r'),
        ('\r # Routing: {}\r'
         'Titolo del messaggio per {}:\r'),
        ('\r # Routing: {}\r'
         'Заголовок сообщения для {}:\r'),
        ('\r # Routing: {}\r'
         'Заголовок повідомлення для {}:\r')),

    'box_cmd_sp_local': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        ('\r # Lokale Nachricht.\r'
         'Titel der Nachricht an {}:\r'),
        ('\r # Local message.\r'
         'Title of message to {}:\r'),
        ('\r # Lokaal bericht.\r'
         'Berichttitel aan {}:\r'),
        ('\r # Message local.\r'
         'Titre du message pour {}:\r'),
        ('\r # Lokální zpráva.\r'
         'Název zprávy pro {}:\r'),
        ('\r # Wiadomość lokalna.\r'
         'Tytuł wiadomości do {}:\r'),
        ('\r # Mensagem local.\r'
         'Título da mensagem para {}:\r'),
        ('\r # Messaggio locale.\r'
         'Titolo del messaggio per {}:\r'),
        ('\r # Локальное сообщение.\r'
         'Заголовок сообщения для {}:\r'),
        ('\r # Локальне повідомлення.\r'
         'Заголовок повідомлення для {}:\r')),

    'box_cmd_sr_enter_msg': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        'Die Antwort geht an {}.\r',
        'The answer goes to {}\r',
        'Het antwoord gaat naar {}\r',
        'La réponse va à {}\r',
        'Odpověď bude odeslána {}.\r',
        'Odpowiedź zostanie wysłana do {}.\r',
        'A resposta vai para {}.\r',
        'La risposta verrà inviata a {}.\r',
        'Ответ будет отправлен {}.\r',
        'Відповідь буде надіслана {}.\r'),

    'box_cmd_sp_enter_msg': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        'Text eingeben ... (Ende mit /EX oder Strg-Z):\r',
        'Enter text ... (End with /EX or Ctrl-Z):\r',
        'Tekst invoeren... (eindigen met /EX of Ctrl-Z):\r',
        'Entrez texte ... (Fin avec /EX ou Ctrl+z) : \r',
        'Zadejte text ... (konec /EX nebo Ctrl-Z):\r',
        'Wpisz tekst ... (zakończ /EX lub Ctrl-Z):\r',
        'Introduza texto ... (Termine com /EX ou Ctrl-Z):\r',
        'Inserisci testo ... (Fine con /EX o Ctrl-Z):\r',
        'Введите текст ... (завершить /EX или Ctrl-Z):\r',
        'Введіть текст ... (завершити /EX або Ctrl-Z):\r'),

    'box_cmd_sp_abort_msg': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        '\r # Nachricht fuer {} anulliert\r\r',
        '\r # Message for {} canceled\r\r',
        '\r # Bericht voor {} geannuleerd\r\r',
        '\r # Message pour {} annulé\r\r',
        '\r # Zpráva pro {} zrušena\r\r',
        '\r # Wiadomość dla {} anulowana\r\r',
        '\r # Mensagem para {} cancelada\r\r',
        '\r # Messaggio per {} annullato\r\r',
        '\r # Сообщение для {} отменено\r\r',
        '\r # Повідомлення для {} скасовано\r\r'),

    'box_cmd_sp_msg_accepted': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        ('\r # Ok. Nachricht an Adresse {} @ {} wird geforwardet.\r'
         '   via: {} MID: {} Bytes: {}\r\r'),
        ('\r # Ok. Message to address {} @ {} is being forwarded\r'
         '   via: {} Mid: {} Bytes: {}\r\r'),
        ('\r # Ok. Bericht wordt doorgestuurd naar adres {} @ {}\r'
         '   via: {} MID: {} Bytes: {}\r\r'),
        ('\r # Ok. Message à l\'adresse {} @ {} est en cours de forward\r'
         '   via: {} Mid: {} Bytes: {}\r\r'),
        ('\r # Ok. Zpráva na adresu {} @ {} bude forwardována.\r'
         '   via: {} MID: {} Bytes: {}\r\r'),
        ('\r # Ok. Wiadomość do {} @ {} zostanie przekazana dalej.\r'
         '   via: {} MID: {} Bytes: {}\r\r'),
        ('\r # Ok. Mensagem para {} @ {} será enviada.\r'
         '   via: {} MID: {} Bytes: {}\r\r'),
        ('\r # Ok. Messaggio a {} @ {} verrà inoltrato.\r'
         '   via: {} MID: {} Bytes: {}\r\r'),
        ('\r # Ok. Сообщение для {} @ {} будет форвардиться.\r'
         '   via: {} MID: {} Bytes: {}\r\r'),
        ('\r # Ok. Повідомлення для {} @ {} буде форвардитись.\r'
         '   via: {} MID: {} Bytes: {}\r\r')),

    'box_cmd_sp_msg_accepted_local': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        ('\r # Ok. Nachricht an Adresse {} bleibt lokal.\r'
         '   MID: {} Bytes: {}\r\r'),
        ('\r # Ok. Message to address {} remains local.\r'
         '   MID: {} Bytes: {}\r\r'),
        ('\r# Oké. Bericht aan adres {} blijft lokaal.\r'
         '   Mid: {} Bytes: {}\r\r'),
        ('\r# Ok. message à l\'adresse {} reste local.\r'
         '   Mid: {} Bytes: {}\r\r'),
        ('\r # Ok. Zpráva na adresu {} zůstane lokální.\r'
         '   MID: {} Bytes: {}\r\r'),
        ('\r # Ok. Wiadomość do {} pozostaje lokalna.\r'
         '   MID: {} Bytes: {}\r\r'),
        ('\r # Ok. Mensagem para {} permanece local.\r'
         '   MID: {} Bytes: {}\r\r'),
        ('\r # Ok. Messaggio per {} rimane locale.\r'
         '   MID: {} Bytes: {}\r\r'),
        ('\r # Ok. Сообщение для {} останется локальным.\r'
         '   MID: {} Bytes: {}\r\r'),
        ('\r # Ok. Повідомлення для {} залишиться локальним.\r'
         '   MID: {} Bytes: {}\r\r')),

    #####################################################
    # BOX GUI
    'own_station': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        'Eigene Station',
        'Own station',
        'Eigen station',
        'Ma station',
        'Vlastní stanice',
        'Własna stacja',
        'Estação própria',
        'Stazione propria',
        'Собственная станция',
        'Власна станція'),

    'region': (
        # Not longer than 73 Chars (Text + Call-SSID = max. 80 Chars)
        'Region',
        'Region',
        'Regio',
        'Région',
        'Region',
        'Region',
        'Região',
        'Regione',
        'Регион',
        'Регіон'),

    'fwd_settings': (
        'Forward',
        'Forward',
        'Forward',
        'Forward',
        'Forward',
        'Forward',
        'Forward',
        'Forward',
        'Forward',
        'Forward'),

    'fwd_port_settings': (
        'FWD-Port',
        'FWD-Port',
        'FWD-Port',
        'FWD-Port',
        'FWD-Port',
        'Port FWD',
        'Porta FWD',
        'Porta FWD',
        'Порт FWD',
        'Порт FWD'),

    'routing_settings': (
        'Routing',
        'Routing',
        'Routing',
        'Routage',
        'Routing',
        'Routing',
        'Routing',
        'Routing',
        'Маршрутизация',
        'Маршрутизація'),

    'reject_settings': (
        'Reject/Hold',
        'Reject/Hold',
        'Reject/Hold',
        'Reject/Hold',
        'Odmítnout/Pozdržet',
        'Odrzuć/Zatrzymaj',
        'Rejeitar/Em espera',
        'Rifiuta/Trattieni',
        'Отклонить/Задержать',
        'Відхилити/Затримати'),

    'cc_settings': (
        'CC',
        'CC',
        'CC',
        'CC',
        'CC',
        'CC',
        'CC',
        'CC',
        'CC',
        'CC'),

    'AutoMail_settings': (
        'Auto Mails',
        'Auto Mails',
        'Auto Mails',
        'Auto Mails',
        'Automatické maily',
        'Auto maile',
        'Auto Mails',
        'Auto Mail',
        'Авто-почта',
        'Авто-листи'),

    'swap_settings': (
        'SWAP',
        'SWAP',
        'SWAP',
        'SWAP',
        'SWAP',
        'SWAP',
        'SWAP',
        'SWAP',
        'SWAP',
        'SWAP'),

    'noConnect': (
        'Kein ausgehender Connect',
        'No outgoing connect',
        'AGeen uitgaande verbinding',
        'Aucune connexion sortante',
        'Žádný odchozí connect',
        'Brak połączenia wychodzącego',
        'Sem ligação de saída',
        'Nessuna connessione in uscita',
        'Нет исходящего соединения',
        'Немає вихідного підключення'),

    'allowPN_AutoPath': (
        'Erlaube PN AutoPath',
        'Allow PN AutoPath',
        'PN AutoPath toestaan',
        'Autorise PN-route auto',
        'Povolit PN AutoPath',
        'Zezwól na PN AutoPath',
        'Permitir PN AutoPath',
        'Consenti PN AutoPath',
        'Разрешить PN AutoPath',
        'Дозволити PN AutoPath'),

    'allowPN_AlterPath': (
        'PN-Alternativroute zulassen',
        'Allow PN alternative route',
        'Alternatieve PN-route toestaan',
        'Autoriser PN-route alternative',
        'Povolit alternativní PN cestu',
        'Zezwól na alternatywną trasę PN',
        'Permitir rota alternativa PN',
        'Consenti percorso alternativo PN',
        'Разрешить альтернативный маршрут PN',
        'Дозволити альтернативний маршрут PN'),

    'allow_PN_FWD': (
        'Privat Mail FWD zulassen',
        'Allow private mail FWD',
        'Sta het doorsturen van privémail toe',
        'Autoriser FWD mails privés',
        'Povolit FWD soukromých mailů',
        'Zezwól na FWD maili prywatnych',
        'Permitir FWD de mail privado',
        'Consenti FWD mail privati',
        'Разрешить FWD личной почты',
        'Дозволити FWD приватної пошти'),

    'allow_BL_FWD': (
        'Bulletin Mail FWD zulassen',
        'Allow Bulletin mail FWD',
        'Doorsturen van bulletinmail toestaan',
        'Autoriser FWD mails bulletins',
        'Povolit FWD bulletinů',
        'Zezwól na FWD bulletinów',
        'Permitir FWD de boletins',
        'Consenti FWD bulletin',
        'Разрешить FWD бюллетеней',
        'Дозволити FWD бюлетенів'),

    'conn_intervall': (
        'Abstände zwischen Connects (Minuten): ',
        'Intervals between connects (minutes): ',
        'Intervallen tussen verbindingen (minuten): ',
        'Intervalles entre les connexions (minutes): ',
        'Intervaly mezi connecty (minuty): ',
        'Odstępy między połączeniami (minuty): ',
        'Intervalos entre ligações (minutos): ',
        'Intervalli tra connessioni (minuti): ',
        'Интервалы между подключениями (минуты): ',
        'Інтервали між підключеннями (хвилини): '),

    'conn_timeout': (
        'Timeout (Minuten): ',
        'Timeout (minutes): ',
        'Timeout (minuten): ',
        'Timeout (minutes): ',
        'Timeout (minuty): ',
        'Timeout (minuty): ',
        'Timeout (minutos): ',
        'Timeout (minuti): ',
        'Таймаут (минуты): ',
        'Таймаут (хвилини): '),

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
        ('0 = deaktivováno\n'
         '1 = nejaktuálnější\n'
         '2 = nejlepší (nejméně hopů)'),
        ('0 = wyłączone\n'
         '1 = najnowsze\n'
         '2 = najlepsze (najmniej hopów)'),
        ('0 = desativado\n'
         '1 = mais recente\n'
         '2 = melhor (menos hops)'),
        ('0 = disabilitato\n'
         '1 = più recente\n'
         '2 = migliore (meno hop)'),
        ('0 = отключено\n'
         '1 = самый свежий\n'
         '2 = лучший (меньше хопов)'),
        ('0 = вимкнено\n'
         '1 = найсвіжіший\n'
         '2 = найкращий (менше хопів)')),

    'bbs_sett_fwd_global': (
        'Forwarding Global',
        'Forwarding Global',
        'Forwarding globaal',
        'Forward Global',
        'Globální Forward',
        'Forwarding Globalny',
        'Forwarding Global',
        'Forwarding Globale',
        'Глобальный Forward',
        'Глобальний Forward'),

    'bbs_sett_local_dist': (
        'Lokale Verteiler',
        'Local distributors',
        'Lokale distributeurs',
        'Distributeurs locaux',
        'Lokální distributoři',
        'Lokalni dystrybutorzy',
        'Distribuidores locais',
        'Distributori locali',
        'Локальные рассылки',
        'Локальні розсилки'),

    'bbs_sett_local_theme': (
        'Lokale Bulletin Themen',
        'Local Bulletin Themes',
        'Lokale Bulletin thema s',
        'Théme bulletin local',
        'Lokální témata bulletinů',
        'Lokalne tematy bulletinów',
        'Temas locais de boletins',
        'Temi locali bulletin',
        'Локальные темы бюллетеней',
        'Локальні теми бюлетенів'),

    'bbs_sett_block_bbs': (
        'BBS blockieren',
        'Block BBS',
        'BBS blokkeren',
        'Bloquer BBS',
        'Blokovat BBS',
        'Blokuj BBS',
        'Bloquear BBS',
        'Blocca BBS',
        'Блокировать BBS',
        'Блокувати BBS'),

    'bbs_sett_block_call': (
        'CALL blockieren',
        'Block CALL',
        'CALL blokkeren',
        'Bloquer CALL',
        'Blokovat CALL',
        'Blokuj CALL',
        'Bloquear INDICATIVO',
        'Blocca CALL',
        'Блокировать CALL',
        'Блокувати CALL'),

    'bbs_sett_pn_bbs_out': (
        'Privat Mail > ausgehend',
        'Private mail > outgoing',
        'Privémail > uitgaand',
        'Mail Privé > sortant',
        'Soukromé maily > odchozí',
        'Poczta prywatna > wychodząca',
        'Mail privado > saída',
        'Mail privato > in uscita',
        'Личная почта > исходящая',
        'Приватна пошта > вихідна'),

    'bbs_sett_pn_bbs_in': (
        'Privat Mail > eingehend',
        'Private mail > incoming',
        'Privémail > inkomend',
        'Mail Privé > entrant',
        'Soukromé maily > příchozí',
        'Poczta prywatna > przychodząca',
        'Mail privado > entrada',
        'Mail privato > in ingresso',
        'Личная почта > входящая',
        'Приватна пошта > вхідна'),

    'bbs_sett_bl_bbs_in': (
        'Bulletin Mail > eingehend',
        'Bulletin mail > incoming',
        'Bulletin mail > inkomend',
        'Mail Bulletin > entrant',
        'Bulletin maily > příchozí',
        'Bulletin > przychodzące',
        'Boletim mail > entrada',
        'Bulletin mail > in ingresso',
        'Бюллетени > входящие',
        'Бюлетені > вхідні'),

    'bbs_sett_bl_bbs_out': (
        'Bulletin Mail > ausgehend',
        'Bulletin mail > outgoing',
        'Bulletin mail > uitgaand',
        'Mail Bulletin > sortant',
        'Bulletin maily > odchozí',
        'Bulletin > wychodzące',
        'Boletim mail > saída',
        'Bulletin mail > in uscita',
        'Бюллетени > исходящие',
        'Бюлетені > вихідні'),

    'read_ed': (
        'gelesen',
        'read',
        'lezen',
        'Lu',
        'přečteno',
        'przeczytane',
        'lido',
        'letto',
        'прочитано',
        'прочитано'),

    'msgC_sendet_msg': (
        'Gesendet',
        'Sendet',
        'Verstuurd',
        'Envoyé',
        'Odesláno',
        'Wysłane',
        'Enviado',
        'Inviato',
        'Отправлено',
        'Надіслано'),

    'msgC_trash_bin': (
        'Papierkorb',
        'Trash',
        'Afval',
        'Poubelle',
        'Koš',
        'Kosz',
        'Lixeira',
        'Cestino',
        'Корзина',
        'Кошик'),

    'saved': (
        'Gespeichert',
        'Saved',
        'Opgeslagen',
        'Enregistré',
        'Uloženo',
        'Zapisano',
        'Guardado',
        'Salvato',
        'Сохранено',
        'Збережено'),

    'private': (
        'Privat',
        'Private',
        'Privaat',
        'Privé',
        'Soukromé',
        'Prywatne',
        'Privado',
        'Privato',
        'Личное',
        'Приватне'),

    #####################################################
    # guiHelpKeybinds.py
    'key_title': (
        'Tastaturbelegung',
        'Keyboard layout',
        'Toetsenbordindeling',
        'Racourcis clavier',
        'Klávesové zkratky',
        'Skróty klawiaturowe',
        'Atalhos de teclado',
        'Mappatura tastiera',
        'Назначение клавиш',
        'Призначення клавіш'),

    'key_esc': (
        'ESC > Neue Verbindung',
        'ESC > New connection',
        'ESC > Nieuwe verbinding',
        'ESC > Nouvelle connexion',
        'ESC > Nové připojení',
        'ESC > Nowe połączenie',
        'ESC > Nova ligação',
        'ESC > Nuova connessione',
        'ESC > Новое соединение',
        'ESC > Нове з’єднання'),

    'key_altc': (
        'ALT + C > Neue Verbindung',
        'ALT + C > New connection',
        'ALT + C > Nieuwe verbinding',
        'ALT + C > Nouvelle connexion',
        'ALT + C > Nové připojení',
        'ALT + C > Nowe połączenie',
        'ALT + C > Nova ligação',
        'ALT + C > Nuova connessione',
        'ALT + C > Новое соединение',
        'ALT + C > Нове з’єднання'),

    'key_altd': (
        'ALT + D > Disconnect',
        'ALT + D > Disconnect',
        'ALT + D > Ontkoppelen',
        'ALT + D > Déconnecter',
        'ALT + D > Odpojit',
        'ALT + D > Rozłącz',
        'ALT + D > Desligar',
        'ALT + D > Disconnetti',
        'ALT + D > Отключить',
        'ALT + D > Відключити'),

    'key_f': (
        'F1 - F10 > Kanal 1 - 10',
        'F1 - F10 > Channel 1 - 10',
        'F1 - F10 > Kanal 1 - 10',
        'F1 - F10 > Canal 1 - 10',
        'F1 - F10 > Kanál 1 - 10',
        'F1 - F10 > Kanał 1 - 10',
        'F1 - F10 > Canal 1 - 10',
        'F1 - F10 > Canale 1 - 10',
        'F1 - F10 > Канал 1 - 10',
        'F1 - F10 > Канал 1 - 10'),

    'key_f12': (
        'F12 > Monitor',
        'F12 > Monitor',
        'F12 > Monitor',
        'F12 > Moniteur',
        'F12 > Monitor',
        'F12 > Monitor',
        'F12 > Monitor',
        'F12 > Monitor',
        'F12 > Монитор',
        'F12 > Монітор'),

    'key_strgplus': (
        'STRG + plus > Textgröße vergrößern',
        'CTRL + plus > Increase text size',
        'CTRL + plus > Tekst vergroten',
        'CTRL + plus > Augmente taille du texte',
        'CTRL + plus > Zvětšit velikost textu',
        'CTRL + plus > Powiększ rozmiar tekstu',
        'CTRL + plus > Aumentar tamanho do texto',
        'CTRL + plus > Aumenta dimensione testo',
        'CTRL + plus > Увеличить размер текста',
        'CTRL + plus > Збільшити розмір тексту'),

    'key_strgminus': (
        'STRG + minus > Textgröße verkleinern',
        'CTRL + minus > Reduce text size',
        'CTRL + min > Tekst verkleinen',
        'CTRL + plus > Réduit taille du texte',
        'CTRL + minus > Zmenšit velikost textu',
        'CTRL + minus > Zmniejsz rozmiar tekstu',
        'CTRL + minus > Reduzir tamanho do texto',
        'CTRL + minus > Riduci dimensione testo',
        'CTRL + minus > Уменьшить размер текста',
        'CTRL + minus > Зменшити розмір тексту'),

    'key_shiftf': (
        'SHIFT + F1 - F12 > Macro-Texte',
        'SHIFT + F1 - F12 > Macro texts',
        'SHIFT + F1 - F12 > Macro texts',
        'SHIFT + F1 - F12 > Texte Macro',
        'SHIFT + F1 - F12 > Makro texty',
        'SHIFT + F1 - F12 > Teksty makr',
        'SHIFT + F1 - F12 > Textos Macro',
        'SHIFT + F1 - F12 > Testi Macro',
        'SHIFT + F1 - F12 > Макросы',
        'SHIFT + F1 - F12 > Макроси'),

    #####################################################
    # guiNewConnWin.py

    'newcon_title': (
        'Neue Verbindung',
        'New Connection',
        'Nieuwe verbinding',
        'Nouvelle connexion',
        'Nové připojení',
        'Nowe połączenie',
        'Nova ligação',
        'Nuova connessione',
        'Новое соединение',
        'Нове з’єднання'),

    'ziel': (
        'Ziel',
        'Destination',
        'streefcijfer',
        'Cible ',
        'Cíl',
        'Cel',
        'Destino',
        'Destinazione',
        'Цель',
        'Ціль'),

    'newcon_history': (
        'History',
        'History',
        'Geschiedenis',
        'Historique',
        'Historie',
        'Historia',
        'Histórico',
        'Cronologia',
        'История',
        'Історія'),

    #####################################################
    # guiBeaconSettings.py

    'scheduler': (
        'Scheduler',
        'Scheduler',
        'Scheduler',
        'Planificateur',
        'Plánovač',
        'Harmonogram',
        'Agenda',
        'Scheduler',
        'Планировщик',
        'Планувальник'),

    'type': (
        'Typ:',
        'Type:',
        'Typ:',
        'Type : ',
        'Typ:',
        'Typ:',
        'Tipo:',
        'Tipo:',
        'Тип:',
        'Тип:'),

    #####################################################
    # guiPoPT_Scheduler.py

    'week_day': (
        'Wochen tage',
        'Week days',
        'Week dagen:',
        'Jour de la semaine',
        'Dny v týdnu',
        'Dni tygodnia',
        'Dias da semana',
        'Giorni della settimana',
        'Дни недели',
        'Дні тижня'),

    'month_day': (
        'Monats Tage',
        'Month days',
        'Maand dagen:',
        'Jour du mois',
        'Dny v měsíci',
        'Dni miesiąca',
        'Dias do mês',
        'Giorni del mese',
        'Дни месяца',
        'Дні місяця'),

    'intervall_mn': (
        'Interval (mn): ',
        'Intervall (mn): ',
        'Interval (mn): ',
        'Intervalle (mn) : ',
        'Interval (min): ',
        'Interwał (min): ',
        'Intervalo (min): ',
        'Intervallo (min): ',
        'Интервал (мин): ',
        'Інтервал (хв): '),

    'offset_sec': (
        'Versatz (sek): ',
        'Offset (sec): ',
        'Offset (sec): ',
        'Décalage (sec) : ',
        'Posun (sek): ',
        'Przesunięcie (sek): ',
        'Desvio (seg): ',
        'Offset (sec): ',
        'Смещение (сек): ',
        'Зсув (сек): '),

    'reset': (
        'Reset',
        'Reset',
        'Reset',
        'Reset',
        'Reset',
        'Reset',
        'Reset',
        'Reset',
        'Сброс',
        'Скидання'),

    'scheduler_set': (
        'Scheduler-Set',
        'Scheduler set',
        'Scheduler ingesteld',
        'Planificateur',
        'Nastavení plánovače',
        'Ustawienie harmonogramu',
        'Configuração da Agenda',
        'Impostazione Scheduler',
        'Настройка планировщика',
        'Налаштування планувальника'),

    #####################################################
    # guiRxEchoSettings.py

    'echo_warning': (
        'Achtung! Diese Funktion ersetzt kein Digipeater!',
        'Attention! This function does not replace a digipeater!',
        'Let op! Deze functie vervangt geen digipeater!',
        'Attention ! Cette fonction ne remplace pas un digipeater !',
        'Pozor! Tato funkce nenahrazuje digipeater!',
        'Uwaga! Ta funkcja nie zastępuje digipeatera!',
        'Atenção! Esta função não substitui um digipeater!',
        'Attenzione! Questa funzione non sostituisce un digipeater!',
        'Внимание! Эта функция не заменяет digipeater!',
        'Увага! Ця функція не замінює digipeater!'),

    #####################################################
    # guiMain.py._monitor_start_msg
    'mon_start_msg1': (
        'Info: Stationsdaten {} erfolgreich geladen.',
        'Info: Station data {} loaded successfully.',
        'Info: Stationgegevens {} succesvol geladen.',
        'Info: Les données de la station {} ont été chargées avec succès.',
        'Info: Data stanice {} úspěšně načteny.',
        'Info: Dane stacji {} załadowane pomyślnie.',
        'Info: Dados da estação {} carregados com sucesso.',
        'Info: Dati stazione {} caricati con successo.',
        'Инфо: Данные станции {} успешно загружены.',
        'Інфо: Дані станції {} успішно завантажено.'),

    'mon_start_msg2': (
        'konnte nicht initialisiert werden!',
        'could not be initialized!',
        'kon niet worden geïnitialiseerd!',
        "n'a pas pu être initialisé !",
        'nelze inicializovat!',
        'nie można zainicjować!',
        'não pôde ser inicializado!',
        'non può essere inizializzato!',
        'не удалось инициализировать!',
        'не вдалося ініціалізувати!'),

    'mon_start_msg3': (
        'erfolgreich initialisiert.',
        'initialized successfully.',
        'succesvol geïnitialiseerd.',
        "initialisé avec succès.",
        'úspěšně inicializováno.',
        'pomyślnie zainicjowano.',
        'inicializado com sucesso.',
        'inizializzato con successo.',
        'успешно инициализировано.',
        'успішно ініціалізовано.'),

    'mon_end_msg1': (
        'PoPT wird beendet.',
        'Quiting PoPT.',
        'PoPT verlaten.',
        "Quitter PoPT.",
        'PoPT se ukončuje.',
        'Zamykanie PoPT.',
        'A encerrar PoPT.',
        'Chiusura di PoPT.',
        'PoPT завершает работу.',
        'PoPT завершується.'),

    # guiMain Status-Bar
    'ENDE': (
        'ENDE',
        'END',
        'EINDE',
        'FIN',
        'KONEC',
        'KONIEC',
        'FIM',
        'FINE',
        'КОНЕЦ',
        'КІНЕЦЬ'),

    'FREI': (
        'FREI',
        'FREE',
        'VRIJ',
        'GRATUIT',
        'VOLNO',
        'WOLNE',
        'LIVRE',
        'LIBERO',
        'СВОБОДНО',
        'ВІЛЬНО'),

    'AUFBAU': (
        'AUFBAU',
        'INITIALIZE',
        'BOUW',
        "INITIALISER",
        'INICIALIZACE',
        'INICJALIZACJA',
        'INICIALIZANDO',
        'INIZIALIZZAZIONE',
        'ПОДКЛЮЧЕНИЕ',
        'ПІДКЛЮЧЕННЯ'),

    'ABBAU': (
        'ABBAU',
        'DISCONNECT',
        'VERBREKEN',
        "DÉCONNEXION",
        'ODPOJOVÁNÍ',
        'ROZŁĄCZANIE',
        'DESCONECTANDO',
        'DISCONNESSIONE',
        'ОТКЛЮЧЕНИЕ',
        'ВІДКЛЮЧЕННЯ'),

    'BEREIT': (
        'BEREIT',
        'READY',
        'KLAAR',
        "PRÊT",
        'PŘIPRAVEN',
        'GOTOWY',
        'PRONTO',
        'PRONTO',
        'ГОТОВ',
        'ГОТОВИЙ'),

    #####################################
    'Abgebrochen': (
    'Abgebrochen',
    'Discontinued',
    'Afgebroken',
    "Abandon",
    'Zrušeno',
    'Przerwano',
    'Cancelado',
    'Annullato',
    'Прервано',
    'Скасовано'),

    'Abgebrochen_msg': (
        ('Das war eine sehr gute Entscheidung. \n'
        'Das hast du gut gemacht, mach weiter so. '),
        ('That was a very good decision. \n'
         'You did well, keep it up.'),
        ('Dat was een heel goede beslissing. \n'
        'Dat heb je goed gedaan, ga zo door.'),
        ('C\'était une très bonne décision. \n'
        'Tu as bien fait, continue comme ça. '),
        ('To bylo velmi dobré rozhodnutí. \n'
         'Dobře jsi to zvládl, pokračuj takhle.'),
        ('To była bardzo dobra decyzja. \n'
         'Dobrze to zrobiłeś, tak trzymaj.'),
        ('Essa foi uma muito boa decisão. \n'
         'Fizeste bem, continua assim.'),
        ('È stata una decisione molto buona. \n'
         'Hai fatto bene, continua così.'),
        ('Это было очень хорошее решение. \n'
         'Ты хорошо справился, так держать.'),
        ('Це було дуже правильне рішення. \n'
         'Ти молодець, продовжуй у тому ж дусі.')),

    'Port_gelöscht': (
        'Port gelöscht',
        'Port deleted',
        'Poort verwijderd',
        "Port supprimé",
        'Port smazán',
        'Port usunięty',
        'Porta apagada',
        'Porta eliminata',
        'Порт удалён',
        'Порт видалено'),

    'Port_gelöscht_msg': (
        'Das Internet wurde erfolgreich gelöscht.',
        'The Internet has been successfully deleted.',
        'Het internet is succesvol verwijderd.',
        'L\'Internet a été supprimé avec succès.',
        'Internet byl úspěšně smazán.',
        'Internet został pomyślnie usunięty.',
        'A Internet foi eliminada com sucesso.',
        'Internet eliminata con successo.',
        'Интернет был успешно удалён.',
        'Інтернет успішно видалено.'),

    'losche_Port': (
        'lösche Port',
        'delete port',
        'verwijder poort',
        'supprimer port',
        'smazat port',
        'usuń port',
        'apagar porta',
        'elimina porta',
        'удалить порт',
        'видалити порт'),

    'losche_Port_msg': (
        ('Willst du diesen Port wirklich löschen? \n'
        'Alle Einstellungen gehen verloren !'),
        ('Are you sure you want to delete this port? \n'
         'All settings will be lost!'),
        ('Wil je deze poort echt verwijderen? \n'
        'Alle instellingen gaan verloren!'),
        ('Voulez-vous vraiment supprimer ce port? \n'
         'Tous les réglages seront perdus! '),
        ('Opravdu chcete smazat tento port? \n'
         'Všechna nastavení budou ztracena!'),
        ('Czy na pewno chcesz usunąć ten port? \n'
         'Wszystkie ustawienia zostaną utracone!'),
        ('Tem certeza que deseja apagar esta porta? \n'
         'Todas as configurações serão perdidas!'),
        ('Vuoi davvero eliminare questa porta? \n'
         'Tutte le impostazioni andranno perse!'),
        ('Вы действительно хотите удалить этот порт? \n'
         'Все настройки будут потеряны!'),
        ('Ви дійсно хочете видалити цей порт? \n'
         'Всі налаштування буде втрачено!')),

    ######################################
    # Setup Wizard
    'invalid_call_titel': (
        'Ungültiger Call',
        'Invalid Callsign',
        'Ongeldige Call',
        'Call invalide',
        'Neplatný Call',
        'Nieprawidłowy Call',
        'Indicativo inválido',
        'Call non valido',
        'Неверный Call',
        'Недійсний Call'),

    'invalid_call_msg': (
        'Der eingegebene Sysop-Call ist ungültig',
        'The entered sysop-call is invalid',
        'De ingevoerde sysop-aanroep is ongeldig',
        "L'appel sysop-call n'est pas valide",
        'Zadaný Sysop-Call je neplatný',
        'Wprowadzony Call sysopa jest nieprawidłowy',
        'O indicativo do Sysop inserido é inválido',
        'Il Sysop-Call inserito non è valido',
        'Введённый Call сисопа недействителен',
        'Введений Call сисопа недійсний'),

    'wizard_done': (
        'Die Einrichtung von PoPT ist jetzt abgeschlossen.',
        'The setup of PoPT is now complete.',
        'De installatie van PoPT is nu voltooid.',
        "La configuration de PoPT est maintenant terminée.",
        'Nastavení PoPT bylo úspěšně dokončeno.',
        'Konfiguracja PoPT została zakończona.',
        'A configuração do PoPT foi concluída.',
        'La configurazione di PoPT è stata completata.',
        'Настройка PoPT завершена.',
        'Налаштування PoPT завершено.'),

    'wizard_want_port_setup': (
        'Willst du einen Port AX25 Port einrichten ?',
        'Do you want to set up an AX25 port ?',
        'Wilt u een AX25-poort instellen ?',
        "Voulez-vous configurer un port AX25 ?",
        'Chcete nastavit AX25 port?',
        'Czy chcesz skonfigurować port AX25?',
        'Deseja configurar uma porta AX25?',
        'Vuoi configurare una porta AX25?',
        'Хотите настроить AX25 порт?',
        'Бажаєте налаштувати порт AX25?'),

    'yes': (
        'Ja',
        'Yes',
        'Ja',
        "Oui",
        'Ano',
        'Tak',
        'Sim',
        'Sì',
        'Да',
        'Так'),

    'no': (
        'Nein',
        'No',
        'Nee',
        "Non",
        'Ne',
        'Nie',
        'Não',
        'No',
        'Нет',
        'Ні'),

    ######################################
    # Right Level Editor
    'right_level_editor_title': (
        'Rechte-Level Editor',
        'Rights Level Editor',
        'Rechtenniveau Editor',
        'Éditeur de niveaux de droits',
        'Editor úrovní práv',
        'Edytor poziomów praw',
        'Editor de Níveis de Direitos',
        'Editor dei Livelli di Diritti',
        'Редактор уровней прав',
        'Редактор рівнів прав',
    ),

    'glb_rights_txt': (
        'Globale PRP-Rechte (glb_rights)',
        'Global PRP Rights (glb_rights)',
        'Globale PRP-rechten (glb_rights)',
        'Droits PRP globaux (glb_rights)',
        'Globální PRP práva (glb_rights)',
        'Globalne prawa PRP (glb_rights)',
        'Direitos PRP Globais (glb_rights)',
        'Diritti PRP Globali (glb_rights)',
        'Глобальные права PRP (glb_rights)',
        'Глобальні права PRP (glb_rights)',
    ),

    'new_user_std_level': (
        'Standard-Level für neue User:',
        'Default level for new users:',
        'Standaardniveau voor nieuwe gebruikers:',
        'Niveau par défaut pour les nouveaux utilisateurs :',
        'Výchozí úroveň pro nové uživatele:',
        'Domyślny poziom dla nowych użytkowników:',
        'Nível padrão para novos utilizadores:',
        'Livello predefinito per nuovi utenti:',
        'Уровень по умолчанию для новых пользователей:',
        'Рівень за замовчуванням для нових користувачів:',
    ),

    'allow_remote_access': (
        'Remote-Zugriff grundsätzlich erlaubt',
        'Remote access generally allowed',
        'Remote toegang in principe toegestaan',
        'Accès distant généralement autorisé',
        'Dálkový přístup v zásadě povolen',
        'Dostęp zdalny ogólnie dozwolony',
        'Acesso remoto geralmente permitido',
        'Accesso remoto generalmente permesso',
        'Удалённый доступ в принципе разрешён',
        'Віддалений доступ загалом дозволено',
    ),

    'allow_login': (
        'Erweiterte Rechte nur nach Login erlauben',
        'Allow extended rights only after login',
        'Uitgebreide rechten alleen na login toestaan',
        'Autoriser les droits étendus uniquement après connexion',
        'Rozšířená práva povolit pouze po přihlášení',
        'Zezwalaj na rozszerzone prawa tylko po zalogowaniu',
        'Permitir direitos estendidos apenas após login',
        'Consentire diritti estesi solo dopo il login',
        'Разрешать расширенные права только после входа',
        'Дозволяти розширені права тільки після входу',
    ),

    'edit_rights': (
        'Rechte-Level verwalten',
        'Manage Rights Levels',
        'Rechtenniveaus beheren',
        'Gérer les niveaux de droits',
        'Spravovat úrovně práv',
        'Zarządzaj poziomami praw',
        'Gerir Níveis de Direitos',
        'Gestisci Livelli di Diritti',
        'Управление уровнями прав',
        'Керування рівнями прав',
    ),

    'new_level': (
        'Neues Level hinzufügen',
        'Add New Level',
        'Nieuw niveau toevoegen',
        'Ajouter un nouveau niveau',
        'Přidat novou úroveň',
        'Dodaj nowy poziom',
        'Adicionar Novo Nível',
        'Aggiungi Nuovo Livello',
        'Добавить новый уровень',
        'Додати новий рівень',
    ),

    'rename_level': (
        'Level umbenennen',
        'Rename Level',
        'Niveau hernoemen',
        'Renommer le niveau',
        'Přejmenovat úroveň',
        'Zmień nazwę poziomu',
        'Renomear Nível',
        'Rinomina Livello',
        'Переименовать уровень',
        'Перейменувати рівень',
    ),

    'delete_level': (
        'Level löschen',
        'Delete Level',
        'Niveau verwijderen',
        'Supprimer le niveau',
        'Smazat úroveň',
        'Usuń poziom',
        'Excluir Nível',
        'Elimina Livello',
        'Удалить уровень',
        'Видалити рівень',
    ),

    'with_login': (
        'Mit Login',
        'With Login',
        'Met Login',
        'Avec Connexion',
        'S Přihlášením',
        'Z Logowaniem',
        'Com Login',
        'Con Login',
        'С Входом',
        'З Логіном',
    ),

    'without_login': (
        'Ohne Login',
        'Without Login',
        'Zonder Login',
        'Sans Connexion',
        'Bez Přihlášení',
        'Bez Logowania',
        'Sem Login',
        'Senza Login',
        'Без Входа',
        'Без Логіну',
    ),

    'new_level_name': (
        'Name des neuen Rechte-Levels:',
        'Name of the new rights level:',
        'Naam van het nieuwe rechtenniveau:',
        'Nom du nouveau niveau de droits :',
        'Název nové úrovně práv:',
        'Nazwa nowego poziomu praw:',
        'Nome do novo nível de direitos:',
        'Nome del nuovo livello di diritti:',
        'Название нового уровня прав:',
        'Назва нового рівня прав:',
    ),

    'already_exists': (
        'Existiert bereits',
        'Already Exists',
        'Bestaat al',
        'Existe déjà',
        'Již existuje',
        'Już istnieje',
        'Já Existe',
        'Esiste Già',
        'Уже существует',
        'Вже існує',
    ),

    'level_name_already_exists': (
        "Level '{}' existiert bereits!",
        "Level '{}' already exists!",
        "Niveau '{}' bestaat al!",
        "Le niveau '{}' existe déjà !",
        "Úroveň '{}' již existuje!",
        "Poziom '{}' już istnieje!",
        "O nível '{}' já existe!",
        "Il livello '{}' esiste già!",
        "Уровень '{}' уже существует!",
        "Рівень '{}' вже існує!",
    ),

    'error_delete_standard_level': (
        'Das aktuelle Standard-Level kann nicht gelöscht werden!',
        'The current default level cannot be deleted!',
        'Het huidige standaardniveau kan niet worden verwijderd!',
        'Le niveau par défaut actuel ne peut pas être supprimé !',
        'Aktuální výchozí úroveň nelze smazat!',
        'Aktualny domyślny poziom nie może zostać usunięty!',
        'O nível padrão atual não pode ser excluído!',
        'Il livello predefinito attuale non può essere eliminato!',
        'Текущий уровень по умолчанию нельзя удалить!',
        'Поточний рівень за замовчуванням не можна видалити!',
    ),

    'ask_delete_level': (
        "Rechte-Level '{}' wirklich löschen?",
        "Really delete rights level '{}'?",
        "Rechtenniveau '{}' echt verwijderen?",
        'Supprimer vraiment le niveau de droits "{}" ?',
        'Opravdu smazat úroveň práv "{}"?',
        'Czy na pewno usunąć poziom praw "{}"?',
        'Excluir realmente o nível de direitos "{}"?',
        'Eliminare davvero il livello di diritti "{}"?',
        'Действительно удалить уровень прав "{}"?',
        'Дійсно видалити рівень прав "{}"?',
    ),

    'new_name': (
        'Neuer Name',
        'New Name',
        'Nieuwe Naam',
        'Nouveau Nom',
        'Nový Název',
        'Nowa Nazwa',
        'Novo Nome',
        'Nuovo Nome',
        'Новое Название',
        'Нова Назва',
    ),

    'error': (
        'Fehler',
        'Error',
        'Fout',
        'Erreur',
        'Chyba',
        'Błąd',
        'Erro',
        'Errore',
        'Ошибка',
        'Помилка',
    ),

    ######################################
    # User DB Right Level Editor
    'remote_rights': (
        'Remote Rechte',
        'Remote Rights',
        'Remote Rechten',
        'Droits à distance',
        'Vzdálená práva',
        'Prawa zdalne',
        'Direitos Remotos',
        'Diritti Remoti',
        'Удалённые права',
        'Віддалені права',
    ),

    'right_level': (
        'Rechte-Level',
        'Rights Level',
        'Rechtenniveau',
        'Niveau de droits',
        'Úroveň práv',
        'Poziom praw',
        'Nível de Direitos',
        'Livello di Diritti',
        'Уровень прав',
        'Рівень прав',
    ),

    'block_remote_access': (
        'Remote-Zugriff komplett verbieten (blocked)',
        'Completely prohibit remote access (blocked)',
        'Remote toegang volledig verbieden (blocked)',
        'Interdire complètement l’accès distant (blocked)',
        'Úplně zakázat vzdálený přístup (blocked)',
        'Całkowicie zabronić dostępu zdalnego (blocked)',
        'Proibir completamente o acesso remoto (blocked)',
        'Vietare completamente l’accesso remoto (blocked)',
        'Полностью запретить удалённый доступ (blocked)',
        'Повністю заборонити віддалений доступ (blocked)',
    ),

    'individual_rights': (
        'Individuelle Rechte',
        'Individual Rights',
        'Individuele Rechten',
        'Droits individuels',
        'Individuální práva',
        'Prawa indywidualne',
        'Direitos Individuais',
        'Diritti Individuali',
        'Индивидуальные права',
        'Індивідуальні права',
    ),

    'password_for_prp_login': (
        'Zugangspasswort (für PRP-Login)',
        'Access password (for PRP login)',
        'Toegangswachtwoord (voor PRP-login)',
        'Mot de passe d’accès (pour connexion PRP)',
        'Přístupové heslo (pro PRP přihlášení)',
        'Hasło dostępu (do logowania PRP)',
        'Senha de acesso (para login PRP)',
        'Password di accesso (per login PRP)',
        'Пароль доступа (для входа PRP)',
        'Пароль доступу (для входу PRP)',
    ),

    'show': (
        'Anzeigen',
        'Show',
        'Weergeven',
        'Afficher',
        'Zobrazit',
        'Pokaż',
        'Mostrar',
        'Mostra',
        'Показать',
        'Показати',
    ),

    # ====================== APRS Chat ======================
    'aprs_chat_invalid_target': (
        " # Ungültiger Call oder Ziel (ALL/CQ)",  # DE
        " # Invalid call or target (ALL/CQ)",  # EN
        " # Ongeldige call of doel (ALL/CQ)",  # NL
        " # Call ou cible invalide (ALL/CQ)",  # FR
        " # Neplatný call nebo cíl (ALL/CQ)",  # CZ
        " # Nieprawidłowy znak lub cel (ALL/CQ)",  # PL
        " # Indicativo ou destino inválido (ALL/CQ)",  # PT
        " # Call o target non valido (ALL/CQ)",  # IT
        " # Недопустимый позывной или цель (ALL/CQ)",  # RU
        " # Недійсний callsign або ціль (ALL/CQ)",  # UA
    ),

    'aprs_chat_no_service': (
        " # APRS-SMS Dienst nicht verfügbar.",  # DE
        " # APRS-SMS service not available.",  # EN
        " # APRS-SMS dienst niet beschikbaar.",  # NL
        " # Service APRS-SMS non disponible.",  # FR
        " # Služba APRS-SMS není dostupná.",  # CZ
        " # Usługa APRS-SMS niedostępna.",  # PL
        " # Serviço APRS-SMS não disponível.",  # PT
        " # Servizio APRS-SMS non disponibile.",  # IT
        " # Сервис APRS-SMS недоступен.",  # RU
        " # Сервіс APRS-SMS недоступний.",  # UA
    ),

    'aprs_chat_exit': (
        " # APRS Chat beendet.",  # DE
        " # APRS Chat ended.",  # EN
        " # APRS Chat beëindigd.",  # NL
        " # Chat APRS terminé.",  # FR
        " # APRS Chat ukončen.",  # CZ
        " # Czat APRS zakończony.",  # PL
        " # Chat APRS terminado.",  # PT
        " # Chat APRS terminato.",  # IT
        " # Чат APRS завершён.",  # RU
        " # Чат APRS завершено.",  # UA
    ),

    'aprs_chat_title': (
        "=== APRS Chat mit {0} auf Port {1} via {2} ===",  # DE
        "=== APRS Chat with {0} on Port {1} via {2} ===",  # EN
        "=== APRS Chat met {0} op Poort {1} via {2} ===",  # NL
        "=== Chat APRS avec {0} sur Port {1} via {2} ===",  # FR
        "=== APRS Chat s {0} na Portu {1} via {2} ===",  # CZ
        "=== Czat APRS z {0} na Porcie {1} via {2} ===",  # PL
        "=== Chat APRS com {0} na Porta {1} via {2} ===",  # PT
        "=== Chat APRS con {0} su Porta {1} via {2} ===",  # IT
        "=== Чат APRS с {0} на Порту {1} via {2} ===",  # RU
        "=== Чат APRS з {0} на Порту {1} via {2} ===",  # UA
    ),

    'aprs_chat_enter': (
        "Gib Nachrichten direkt ein. //EXIT zum Verlassen.",  # DE
        "Enter messages directly. //EXIT to leave.",  # EN
        "Voer berichten direct in. //EXIT om te verlaten.",  # NL
        "Entrez les messages directement. //EXIT pour quitter.",  # FR
        "Zprávy zadávejte přímo. //EXIT pro ukončení.",  # CZ
        "Wpisz wiadomości bezpośrednio. //EXIT aby wyjść.",  # PL
        "Digite mensagens diretamente. //EXIT para sair.",  # PT
        "Inserisci i messaggi direttamente. //EXIT per uscire.",  # IT
        "Введите сообщения напрямую. //EXIT для выхода.",  # RU
        "Вводьте повідомлення безпосередньо. //EXIT для виходу.",  # UA
    ),

    'aprs_chat_help': (
        "Hilfe mit //H oder //HELP",                 # DE
        "Help with //H or //HELP",                   # EN
        "Help met //H of //HELP",                    # NL
        "Aide avec //H ou //HELP",                   # FR
        "Nápověda přes //H nebo //HELP",             # CZ
        "Pomoc poprzez //H lub //HELP",              # PL
        "Ajuda com //H ou //HELP",                   # PT
        "Aiuto con //H o //HELP",                    # IT
        "Помощь командой //H или //HELP",            # RU
        "Допомога командою //H або //HELP",          # UA
    ),

    'aprs_msgs_title': (
        "=== APRS Messages ===",  # DE
        "=== APRS Messages ===",  # EN
        "=== APRS Berichten ===",  # NL
        "=== Messages APRS ===",  # FR
        "=== APRS Zprávy ===",  # CZ
        "=== Wiadomości APRS ===",  # PL
        "=== Mensagens APRS ===",  # PT
        "=== Messaggi APRS ===",  # IT
        "=== Сообщения APRS ===",  # RU
        "=== Повідомлення APRS ===",  # UA
    ),

    'aprs_msgs_more': (
        "... und weitere Nachrichten",
        "... and more messages",
        "... en meer berichten",
        "... et autres messages",
        "... a dalších zpráv",
        "... i więcej wiadomości",
        "... e mais mensagens",
        "... e altri messaggi",
        "... и ещё сообщений",
        "... та ще повідомлень",
    ),

    'aprs_recent_title': (
        "--- Letzte APRS-Nachrichten ({0}) ---",
        "--- Latest APRS Messages ({0}) ---",
        "--- Laatste APRS-berichten ({0}) ---",
        "--- Derniers messages APRS ({0}) ---",
        "--- Poslední APRS zprávy ({0}) ---",
        "--- Ostatnie wiadomości APRS ({0}) ---",
        "--- Últimas mensagens APRS ({0}) ---",
        "--- Ultimi messaggi APRS ({0}) ---",
        "--- Последние сообщения APRS ({0}) ---",
        "--- Останні повідомлення APRS ({0}) ---",
    ),

    'aprs_recent_no_unread': (
        " # Keine ungelesenen APRS-Nachrichten für {0}.",
        " # No unread APRS messages for {0}.",
        " # Geen ongelezen APRS-berichten voor {0}.",
        " # Aucun message APRS non lu pour {0}.",
        " # Žádné nepřečtené APRS zprávy pro {0}.",
        " # Brak nieprzeczytanych wiadomości APRS dla {0}.",
        " # Nenhuma mensagem APRS não lida para {0}.",
        " # Nessun messaggio APRS non letto per {0}.",
        " # Нет непрочитанных сообщений APRS для {0}.",
        " # Немає непрочитаних повідомлень APRS для {0}.",
    ),

    'aprs_recent_all_cmd': (
        "Alle Nachrichten mit //AMSGS",
        "All messages with //AMSGS",
        "Alle berichten met //AMSGS",
        "Tous les messages avec //AMSGS",
        "Všechny zprávy pomocí //AMSGS",
        "Wszystkie wiadomości poleceniem //AMSGS",
        "Todas as mensagens com //AMSGS",
        "Tutti i messaggi con //AMSGS",
        "Все сообщения с помощью //AMSGS",
        "Всі повідомлення за допомогою //AMSGS",
    ),

    'aprs_clear_done': (
        " # APRS-Nachrichten-Liste bereinigt.",
        " # APRS message list cleared.",
        " # APRS-berichtenlijst opgeschoond.",
        " # Liste des messages APRS nettoyée.",
        " # Seznam APRS zpráv vyčištěn.",
        " # Lista wiadomości APRS wyczyszczona.",
        " # Lista de mensagens APRS limpa.",
        " # Lista messaggi APRS pulita.",
        " # Список сообщений APRS очищен.",
        " # Список повідомлень APRS очищено.",
    ),

    # --- Hilfe ---
    'aprs_chat_help_title': (
        "=== APRS Chat Hilfe ===", "=== APRS Chat Help ===", "=== APRS Chat Help ===",
        "=== Aide Chat APRS ===", "=== Nápověda APRS Chat ===", "=== Pomoc Czat APRS ===",
        "=== Ajuda Chat APRS ===", "=== Aiuto Chat APRS ===", "=== Помощь чата APRS ===",
        "=== Допомога чату APRS ===",
    ),

    'aprs_chat_help_border': (
                                 "--------------------------------------------------",
                             ) * 10,

    'aprs_chat_help_h': (
        "  //H  oder //HELP     - Diese Hilfe",
        "  //H  or  //HELP      - This help",
        "  //H  of   //HELP     - Deze hulp",
        "  //H  ou  //HELP      - Cette aide",
        "  //H  nebo //HELP     - Tato nápověda",
        "  //H  lub  //HELP     - Ta pomoc",
        "  //H  ou  //HELP      - Esta ajuda",
        "  //H  o   //HELP      - Questo aiuto",
        "  //H  или //HELP      - Эта помощь",
        "  //H  або //HELP      - Ця допомога",
    ),

    'aprs_chat_help_exit': (
        "  //EXIT oder //Q      - Chat verlassen",
        "  //EXIT or  //Q       - Leave chat",
        "  //EXIT of   //Q      - Chat verlaten",
        "  //EXIT ou  //Q       - Quitter le chat",
        "  //EXIT nebo //Q      - Ukončit chat",
        "  //EXIT lub  //Q      - Wyjście z czatu",
        "  //EXIT ou  //Q       - Sair do chat",
        "  //EXIT o   //Q       - Uscire dal chat",
        "  //EXIT или //Q       - Выйти из чата",
        "  //EXIT або //Q       - Вийти з чату",
    ),
    'aprs_chat_help_max_hops': (
        "  //WIDE <HOPS>        - Maximale Hops (1-7) setzen (WIDE[x]-[x])",  # DE
        "  //WIDE <HOPS>        - Set maximum hops (1-7) (WIDE[x]-[x])",  # EN
        "  //WIDE <HOPS>        - Maximum hops (1-7) instellen (WIDE[x]-[x])",  # NL
        "  //WIDE <HOPS>        - Définir le nombre max de hops (1-7) (WIDE[x]-[x])",  # FR
        "  //WIDE <HOPS>        - Nastavit maximální hops (1-7) (WIDE[x]-[x])",  # CZ
        "  //WIDE <HOPS>        - Ustaw maksymalną liczbę hops (1-7) (WIDE[x]-[x])",  # PL
        "  //WIDE <HOPS>        - Definir hops máximo (1-7) (WIDE[x]-[x])",  # PT
        "  //WIDE <HOPS>        - Imposta hops massimi (1-7) (WIDE[x]-[x])",  # IT
        "  //WIDE <HOPS>        - Установить максимум hops (1-7) (WIDE[x]-[x])",  # RU
        "  //WIDE <HOPS>        - Встановити максимум hops (1-7) (WIDE[x]-[x])",  # UA
    ),

    'aprs_chat_help_amsgs': (
        "  //AMSGS [n]          - Alle Nachrichten anzeigen",
        "  //AMSGS [n]          - Show all messages",
        "  //AMSGS [n]          - Toon alle berichten",
        "  //AMSGS [n]          - Afficher tous les messages",
        "  //AMSGS [n]          - Zobrazit všechny zprávy",
        "  //AMSGS [n]          - Pokaż wszystkie wiadomości",
        "  //AMSGS [n]          - Mostrar todas as mensagens",
        "  //AMSGS [n]          - Mostra tutti i messaggi",
        "  //AMSGS [n]          - Показать все сообщения",
        "  //AMSGS [n]          - Показати всі повідомлення",
    ),

    'aprs_chat_help_aclear': (
        '  //ACLEAR             - APRS Nachrichten löschen',                    # DE
        '  //ACLEAR             - Delete / Clear APRS Messages',                # EN
        '  //ACLEAR             - APRS Berichten wissen / wissen',              # NL
        '  //ACLEAR             - Supprimer les messages APRS',                 # FR
        '  //ACLEAR             - Smazat APRS zprávy',                          # CZ
        '  //ACLEAR             - Usuń wiadomości APRS',                        # PL
        '  //ACLEAR             - Apagar mensagens APRS',                       # PT
        '  //ACLEAR             - Cancella messaggi APRS',                      # IT
        '  //ACLEAR             - Удалить сообщения APRS',                      # RU
        '  //ACLEAR             - Видалити повідомлення APRS',                  # UA
    ),


    'aprs_chat_help_achange': (
        "Ziel ändern (ohne Chat zu verlassen):",
        "Change target (without leaving chat):",
        "Doel wijzigen (zonder chat te verlaten):",
        "Changer de cible (sans quitter le chat):",
        "Změnit cíl (bez ukončení chatu):",
        "Zmiana celu (bez wychodzenia z czatu):",
        "Alterar destino (sem sair do chat):",
        "Cambia target (senza uscire dal chat):",
        "Сменить цель (не выходя из чата):",
        "Змінити ціль (не виходячи з чату):",
    ),

    'aprs_chat_help_achat': (
        "  //ACHAT <Call> [Port]  - Mit Station chatten",
        "  //ACHAT <Call> [Port]  - Chat with station",
        "  //ACHAT <Call> [Port]  - Chatten met station",
        "  //ACHAT <Call> [Port]  - Chatter avec la station",
        "  //ACHAT <Call> [Port]  - Chatovat se stanicí",
        "  //ACHAT <Call> [Port]  - Czat ze stacją",
        "  //ACHAT <Call> [Port]  - Conversar com estação",
        "  //ACHAT <Call> [Port]  - Chattare con stazione",
        "  //ACHAT <Call> [Port]  - Чат со станцией",
        "  //ACHAT <Call> [Port]  - Чат зі станцією",
    ),

    'aprs_send_error': (
        " # Fehler beim Senden der APRS-Nachricht.",  # DE
        " # Error sending APRS message.",  # EN
        " # Fout bij verzenden APRS-bericht.",  # NL
        " # Erreur lors de l'envoi du message APRS.",  # FR
        " # Chyba při odesílání APRS zprávy.",  # CZ
        " # Błąd podczas wysyłania wiadomości APRS.",  # PL
        " # Erro ao enviar mensagem APRS.",  # PT
        " # Errore nell'invio del messaggio APRS.",  # IT
        " # Ошибка при отправке APRS-сообщения.",  # RU
        " # Помилка при відправці APRS-повідомлення.",  # UA
    ),
    # =======================================
    'default_text': (
        'Standard Text',
        'Default Text',
        'Standaard tekst',
        'Texte standard',
        'Standardní text',
        'Tekst domyślny',
        'Texto padrão',
        'Testo predefinito',
        'Текст по умолчанию',
        'Текст за замовчуванням'
    ),
# ======== END =====================
}   # < End of dict


logger.info("Building Sting Tab / Translation Tab")
for k, tpl_item in dict(STR_TABLE).items():
    new_item = list(tpl_item)
    # Add Spanish People / Index 10
    if k not in STR_TABLE_SP.keys():
        logger.warning(f"String Tab no Entry found for {k} in ESP Table")
    new_item.append(STR_TABLE_SP.get(k, ""))

    # Override old item
    STR_TABLE[k] = tuple(new_item)

logger.info("Building Sting Tab / Translation Tab.. Done..")


if __name__ == '__main__':
    # Generating new Tab for additional Languages
    new_tab = {}
    #out_str = "{\n"
    for k, ent in STR_TABLE.items():
        new_tab[k] = ent[1]
        #out_str += f'"{k}": "{ent[1]}",\n'

    #out_str += "}"
    print(new_tab)
