#!/usr/bin/python3

import pickle
import csv

popt_userDB = '../../data/UserDB.popt'
output_file = 'output.csv'
trenner = '|'

not_public_vars = [
            'not_public_vars',
            'is_new',
            'pac_len',
            'max_pac',
            'CText',
            'routes',
            'Language',
            'Distance',
            'Info',
            'software_str',
            'sys_pw',
            'sys_pw_parm',
            'sys_pw_autologin',
            'Call',
            'call_str',
            'SSID',
        ]

with open(popt_userDB, 'rb') as inp:
    user_db = pickle.load(inp)

with open(output_file, 'w', encoding='utf8') as csv_file:
    wr = csv.writer(csv_file, delimiter=trenner)
    tmp = list(user_db[list(user_db.keys())[0]].keys())
    head = ['Call']
    for el in tmp:
        if el not in not_public_vars:
            head.append(el)
    wr.writerow(head)

    for call, db_ent in user_db.items():
        row = [call]
        for k in head[1:]:
            row.append(db_ent.get(k, ''))
        wr.writerow(row)