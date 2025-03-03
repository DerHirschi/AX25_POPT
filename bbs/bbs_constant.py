"""
+ or Y : Yes, message accepted
- or N : No, message already received
= or L : Later, already receiving this message
H : Message is accepted but will be held
R : Message is rejected
E : There is an error in the line
!offset or Aoffset : Yes, message accepted from (Offset)
"""

###########################################
# FWD Protocol
FWD_RESP_LATER          = '='
FWD_RESP_OK             = '+'
FWD_RESP_N_OK           = '-'
FWD_RESP_REJ            = 'R'
FWD_RESP_HLD            = 'H'
FWD_RESP_ERR            = 'E'
FWD_RESP_ERR_OFFSET     = '!offset'   # TODO

FWD_RESP_TAB = {
    True:  FWD_RESP_N_OK,
    False: FWD_RESP_OK,
}

FWD_LATER               = [FWD_RESP_LATER,      'L']
FWD_OK                  = [FWD_RESP_OK,         'Y']
FWD_N_OK                = [FWD_RESP_N_OK,       'N']
FWD_REJ                 = FWD_RESP_REJ
FWD_HLD                 = FWD_RESP_HLD
FWD_ERR                 = FWD_RESP_ERR
FWD_ERR_OFFSET          = [FWD_RESP_ERR_OFFSET, 'Aoffset', '']

###########################################
# MSG
CR              = b'\x0D'       # b'\r'
LF              = b'\x0A'       # b'\n'
CNTRL_Z         = b'\x1a'
SP              = b'\x20'       # b' '
TAB             = b'\x09'       # b'\t'
EOL             = (CR + LF, CR)
EOMA            = (CNTRL_Z + CR, CNTRL_Z + CR + LF)
EOMB            = (
    CR + b'/EX' + CR,
    CR + b'/ex' + CR,
    CR + LF + b'/EX' + CR + LF,
    CR + LF + b'/ex' + CR + LF
)
EOM             = tuple([x for x in EOMA + EOMB])
#------------------------
STAMP           = b'R:'
STAMP_BID       = b'$:'
STAMP_MSG_NUM   = b'#:'
MSG_ID          = lambda msg_num, bbs_call: f"{msg_num}_{bbs_call}"

###########################################
# Import/Export RFC-822 Header
MSG_H_TO        = (b'To:', b'To  :' )
MSG_H_FROM      = (b'From:',        )
MSG_H_SUBJ      = b'Subject:'
MSG_H_MSG_ID    = b'Message-ID:'
MSG_H_CC        = b'cc:'
MSG_H_REPLY     = b'Reply-To:'
#------------------------------------------
# Extension Keys produced by W0RLI Systems
MSG_XH_W_MSG_TYP  = b'X-msgtype:'
MSG_XH_W_BID      = b'X-BID:'
#------------------------------------------
# Extension Keys produced by JNOS Systems
MSG_XH_J_MSG_TYP  = b'X-BBS-Msg-Type:'
MSG_XH_J_HOLD     = b'X-BBS-Hold:'
MSG_XH_J_FWD_TO   = b'X-Forwarded-To:'
# ???
MSG_XH_INFO       = b'X-Info:'
#------------------------------------------


MSG_HEADER_ALL    = MSG_H_TO + MSG_H_FROM + (
    MSG_H_SUBJ,
    MSG_H_MSG_ID,
    MSG_H_CC,
    MSG_H_REPLY,
    MSG_XH_W_MSG_TYP,
    MSG_XH_W_BID,
    MSG_XH_J_MSG_TYP,
    MSG_XH_J_HOLD,
    MSG_XH_J_FWD_TO,
    MSG_XH_INFO
)
##############################################

def GET_MSG_STRUC():
    return dict(
        message_type=   '',
        sender=         '',
        recipient_bbs=  '',
        receiver=       '',
        mid=            '',
        bid_mid=        '',
        sender_bbs=     '',
        message_size=   0,
        #
        msg=            b'',
        header=         b'',
        path=           [],
        fwd_path=       [],
        msg_time=       '',
        subject=        '',
        bid=            '',
        flag=           '',
    )