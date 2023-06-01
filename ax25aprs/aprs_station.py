
class APRS_Station(object):
    def __init__(self):
        self.aprs_parm_call = ''
        self.aprs_parm_loc = ''
        self.aprs_parm_lat = ''
        self.aprs_parm_lon = ''

        self.aprs_parm_digi = False
        self.aprs_parm_igate = False
        self.aprs_parm_igate_tx = False
        self.aprs_parm_igate_rx = False
        self.aprs_parm_igate_tx_flt = ''
        self.aprs_parm_igate_rx_flt = ''

        self.aprs_parm_igate_address = '', 0
        self.aprs_parm_igate_login = ''
        self.aprs_parm_igate_passw = ''

        self.aprs_beacon_text = ''

