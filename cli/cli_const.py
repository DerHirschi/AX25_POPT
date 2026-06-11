#######################################################
# CLI Default Commands
"""
CLI_DEF_CMD_ALL = ['?', 'ATR', 'AXIP', 'BELL', 'BWSTAT', 'BYE', 'C!', 'CH', 'CHINFO', 'CHIST', 'CHLIST', 'CONNECT', 'CONV', 'CSTAT', 'DXLIST', 'ECHO', 'EMAIL', 'FWDINFO', 'HELP', 'INFO', 'K', 'KM', 'L<', 'L>', 'L@', 'LANG', 'LB', 'LCSTATUS', 'LINFO', 'LL', 'LM', 'LMH', 'LN', 'LOC', 'MH', 'MR', 'NAME', 'NEWS', 'OP',
                   'POPT',
                   #'POKER',
                   'PORT',
                   'PRMAIL', 'PSTAT', 'QTH', 'QUIT', 'R', 'RTT', 'SB', 'SETAXIP', 'SP', 'SR', 'UMLAUT', 'USER', 'VERSION', 'WEB', 'WX', 'ZIP']
"""
CLI_DEF_CMD_BASIC = ['QUIT', 'BYE', 'HELP', '?', 'Q']

CLI_DEF_CMD_CONV  = ['L', 'H', 'Q', 'U']

CLI_DEF_CMD_SYSOP = ['QUIT',
                               'BYE',
                               # NODE
                               'ECHO',
                               'CONNECT',
                               'C!',
                               'CH',
                               'CONV',
                               'PORT',
                               'PSTAT',
                               'BWSTAT',
                               'MH',
                               'LMH',
                               'AXIP',
                               'DXLIST',
                               'LCSTATUS',
                               'CSTAT',
                             'CHIST',

                             'RTT',
                               # APRS
                               'ATR',
                               'WX',
                               # User Info
                               'BELL',
                               'INFO',
                               'LINFO',
                               'NEWS',
                               # UserDB
                               'USER',
                               'NAME',
                               'QTH',
                               'LOC',
                               'ZIP',
                               'PRMAIL',
                               'EMAIL',
                               'WEB',
                               # BOX
                               #'LB',
                               #'LN',
                               #'LM',
                               #'R',
                               #'KM',
                               # CLI OPT
                               'OP',
                               'LANG',
                               'UMLAUT',
                               'ENCODER',
                               #
                               'VERSION',
                               'POPT',
                               #'POKER',
                               'HELP',
                               '?',
                                'L', 'U', 'H', 'Q', # Converse,
                                # === Path  
                                'PATH',
                     # ==== AUTH

                     'SYS',
                     'LOGOUT',
                     # ==== Monitor
                     'MONITOR',
                     ]

CLI_DEF_CMD_NODE =['QUIT',
                               'BYE',
                               # NODE
                               'ECHO',
                               'CONNECT',
                               'C!',
                               'CH',
                               'CONV',
                               'PORT',
                               'PSTAT',
                               'BWSTAT',
                               'RTT',
                               #'PREMON',
                               'MH',
                               'LMH',
                               'AXIP',
                               'DXLIST',
                               'LCSTATUS',
                               'CSTAT',
                               'CHIST',
                               # APRS
                               'ATR',
                               'WX',
                               # User Info
                               'BELL',
                               'INFO',
                               'LINFO',
                               'NEWS',
                               # UserDB
                               'USER',
                               'NAME',
                               'QTH',
                               'LOC',
                               'ZIP',
                               'PRMAIL',
                               'EMAIL',
                               'WEB',
                               # BOX
                               #'LB',
                               #'LN',
                               #'LM',
                               #'R',
                               #'KM',
                               # CLI OPT
                               'OP',
                               'LANG',
                               'UMLAUT',
                               'ENCODER',
                               #
                               'VERSION',
                               'POPT',

                               'POKER',

                               'HELP',
                               '?',
                                # ==== APRS Chat
                                'ACHAT',
                                'AMSGS',
                                'ACLEAR',
                                # === Path
                                'PATH',
                                # ==== AUTH
                                'SYS',
                                'LOGOUT',
                     # ==== Monitor
                     'MONITOR',
                   ]

CLI_DEF_CMD_BOX = ['QUIT',
                              'BYE',
                              'CH',
                              'CONV',
                              'LCSTATUS',
                              'CSTAT',
                              'CHIST',
                              'PSTAT',
                              'BWSTAT',
                              'RTT',
                              ## APRS
                              # 'ATR',
                              'WX',
                              ## User Info
                              'BELL',
                              'FWDINFO',
                              'INFO',
                              'LINFO',
                              'NEWS',
                              # UserDB
                              'USER',
                              'NAME',
                              'QTH',
                              'LOC',
                              'ZIP',
                              'PRMAIL',
                              'EMAIL',
                              'WEB',
                              # BOX
                              'LB',
                              'LN',
                              'LM',
                              'LL',
                              'L<',
                              'L>',
                              'L@',
                              'R',
                              'SP',
                              'SB',
                              'SR',
                              'KM',
                              'K',
                              'MR',
                              # CLI OPT
                              'OP',
                              'LANG',
                              'UMLAUT',
                   'ENCODER',
                   #
                              'VERSION',
                              'POPT',
                              #'POKER',
                              'HELP',
                              '?',
                   # ==== APRS Chat
                   'ACHAT',
                   'AMSGS',
                   'ACLEAR',
                   # === Path
                   'PATH',
                   # ==== AUTH
                   'SYS',
                   'LOGOUT',
                   ]

CLI_DEF_CMD_MCAST = ['QUIT',
                              'BYE',
                              ## MCAST
                              'CH',
                              'CHLIST',
                              'CHINFO',
                              'SETAXIP',
                              ## NODE
                              # 'ECHO',
                              # 'CONNECT',
                              # 'C!',
                              # 'PORT',
                              # 'MH',
                              # 'LMH',
                              # 'AXIP',
                              # 'DXLIST',
                              # 'LCSTATUS',
                              ## APRS
                              # 'ATR',
                              # 'WX',
                              ## User Info
                              'BELL',
                              'INFO',
                              'LINFO',
                              'NEWS',
                              # UserDB
                              'USER',
                              'NAME',
                              'QTH',
                              'LOC',
                              'ZIP',
                              'PRMAIL',
                              'EMAIL',
                              'WEB',
                              # BOX
                              # 'LB',
                              # 'LN',
                              # 'LM',
                              # 'R',
                              # 'KM',
                              # CLI OPT
                              'OP',
                              'LANG',
                              'UMLAUT',
                     'ENCODER',
                     #
                              'VERSION',
                              'POPT',
                              'HELP',
                              '?']


CLI_DEF_CMD_ALL = []

for el in CLI_DEF_CMD_BASIC + CLI_DEF_CMD_SYSOP + CLI_DEF_CMD_NODE + CLI_DEF_CMD_BOX + CLI_DEF_CMD_MCAST:
    if el not in CLI_DEF_CMD_ALL:
        CLI_DEF_CMD_ALL.append(el)

CLI_DEF_CMD_ALL = sorted(CLI_DEF_CMD_ALL)