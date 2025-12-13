####################################################################################
PRP_SW_RESTR             = 'PoPT'       # Software restriction
PRP_VER_RESTR            = '2.123.20'   # Version restriction - Allgemein
PRP_VER_RESTR_HANDSHAKE  = '2.123.24'   # Version restriction - Handshake
####################################################################################
PRP_FLAG  = b'\x8D\x81'      # PRP Flag
####################################################################################
# ESC & END Flags
PRP_FEND  = b'\x8D'
PRP_FESC  = b'\x8F'
PRP_TFEND = b'\x92'
PRP_TFESC = b'\x9B'

PRP_FESC_TFEND = b''.join([PRP_FESC, PRP_TFEND])    # "FEND is sent as FESC, TFEND"  /  0x8D is sent as 0x8F 0x92
PRP_FESC_TFESC = b''.join([PRP_FESC, PRP_TFESC])    # "FESC is sent as FESC, TFESC"  /  0x8F is sent as 0x8F 0x9B
####################################################################################
# OPT-ID ≥ 20
PRP_OPT_20              = 20 # Handshake
PRP_OPT_21              = 21 # PRP-Frame Abort
PRP_OPT_DISCO           = 22 # Connection (soft)Disco
PRP_OPT_LOGIN_REQ       = 23 # Login Request
PRP_OPT_LOGIN_RESP      = 24 # Login Response
PRP_OPT_LOGOUT          = 25 # Logout
PRP_OPT_STATE_UPDATE    = 26 # State Update > PRP Einstellungen/Zustände ändern
PRP_OPT_ESC_CLI         = 62 # Payload wird an CLI durchgereicht
PRP_OPT_PRP_BATCH       = 63 # PRP-Frame Batch processing
####################################################################################
# ACK / Response
PRP_DONT_ACK = (PRP_OPT_DISCO, PRP_OPT_LOGIN_REQ, PRP_OPT_20, PRP_OPT_21)
PRP_ACK      = b'O'
PRP_NACK     = b'F'
####################################################################################
# PRP-ABORT Frame.
PRP_ABORT_FRAME = b'\x8d\x81\x15\x00\x00\x0fd' # Verwirft teilweise empfangenen PRP-Frame, wenn PRP-ABORT im Datenstrom gefunden
####################################################################################
# OPT Tab für Monitor
PRP_CTL_TAB = {
                20: 'Handshake',
                21: 'ABORT',            # Bricht angefangenen RX-Frame ab / löscht Rest-Buffer
                22: 'Disconnect',
                23: 'Login REQ',
                24: 'Login RESP',
                25: 'Logout',
                26: 'State Update',
                62: 'CLI-ESC',
                63: 'BATCH',
               }
####################################################################################
# Response (GUI Handling)
PRP_RM_RESP_LOGIN   = 'rsp_login'   # Remote Login OK
PRP_RM_RESP_LOGOUT  = 'rsp_logout'  # Remote Login FAILED | Logout
####################################################################################
# Parameter
PRP_BATCH_MAX_PAY  = 1024   # Max Raw-Data(PRP-Frames size) Threshold for Batch
PRP_BATCH_MIN_PACK = 4      # Min PRP-Frames to send as Batch


