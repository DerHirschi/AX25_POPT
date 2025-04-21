from bbs.bbs_constant import GET_MSG_STRUC
from bbs.bbs_fnc import find_eol
from cfg.constant import CFG_bbs_import_path, CFG_bbs_import_file
from cfg.logger_config import BBS_LOG


def get_mail_import():
    log_tag = "Mail import> "
    import_file = CFG_bbs_import_path + CFG_bbs_import_file
    try:
        with open(import_file, 'rb') as inp:
            import_data = inp.read()
            inp.close()
    except (FileNotFoundError, EOFError) as e:
        # BBS_LOG.error(log_tag + f"read from Import File: {e}")
        return []
    except PermissionError as e:
        BBS_LOG.error(log_tag + f"read from Import File: {e}")
        return []
    if not import_data:
        return []
    try:
        with open(import_file, 'wb') as file:
            file.write(b'')
    except FileNotFoundError as e:
        BBS_LOG.warning(log_tag + f"write to Import File - File not Found: {e} ")
        with open(import_file, 'xb') as file:
            file.write(b'')
    except (FileNotFoundError, EOFError, PermissionError) as e:
        BBS_LOG.error(log_tag + f"write to Import File: {e}")
        return []

    eol = find_eol(import_data)
    data_lines = import_data.split(eol)
    if len(data_lines) < 4:
        BBS_LOG.error(log_tag + f"len(lines) < 4:  {len(data_lines)}")
        return []

    imported_msgs = []
    msg   = {}
    for line in data_lines:
        dec_line = line.decode('UTF-8', 'ignore')
        if not msg:
            if dec_line.startswith('SP ') or dec_line.startswith('SB '):
                # SB ALL @ EU < LA6CU $12345ABCD
                if not ' < ' in dec_line:
                    continue
                if dec_line.startswith('SB '):
                    msg_typ = 'B'
                    if not ' @ ' in dec_line:
                        continue
                else:
                    msg_typ = 'P'
                tmp_line         = dec_line[3:]
                to_add, from_add = tmp_line.split(' < ')
                to_address_list  = to_add.split(' @ ')
                if len(to_address_list) == 2:
                    to_call, to_bbs = to_address_list
                else:
                    to_call, to_bbs = to_address_list[0], ''

                if ' $' in from_add:
                    from_call, bid = from_add.split(' $')
                else:
                    from_call, bid = from_add, ''

                if '@' in from_call:
                    from_call, from_bbs = from_call.split('@')
                    from_call = from_call.replace(' ', '')
                    from_bbs  = from_bbs.replace(' ', '')
                else:
                    from_call, from_bbs = from_call, ''

                if any((
                    not to_call,
                    not from_call
                )):
                    continue

                msg = GET_MSG_STRUC()

                msg['sender']       = str(from_call).upper()
                msg['sender_bbs']   = str(from_bbs).upper()
                msg['receiver']     = str(to_call).upper()
                msg['recipient_bbs']= str(to_bbs).upper()
                msg['message_type'] = str(msg_typ)
                msg['bid']          = str(bid)
                msg['x_info']       = "*** PoPT-Box Mail Import ***"
            else:
                continue
        elif not msg.get('subject', ''):
            if not dec_line:
                dec_line = ' '
            msg['subject'] = dec_line

        else:
            if not msg.get('msg', b''):
                if line in (b'/EX', b'/ex'):
                    msg = {}
                    continue
                msg['msg'] = line + eol
            else:
                if line in (b'/EX', b'/ex'):
                    # End
                    msg['message_size'] = len(msg['msg'])
                    imported_msgs.append(dict(msg))
                    msg = {}
                    continue
                msg['msg'] += line + eol

    return imported_msgs
