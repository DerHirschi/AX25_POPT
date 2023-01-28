
class DefaultStationConfig(object):
    ##########################
    # Parameter for Connection
    parm_StationCalls: [''] = []
    parm_isDigi = False
    parm_PacLen = 250  # Max Pac len
    parm_MaxFrame = 7  # Max (I) Frames
    parm_TXD = 50  # TX Delay for RTT Calculation  !! Need to be high on AXIP for T1 calculation
    parm_T0 = 1200  # T0 (Response Delay Timer) activated if data come in to prev resp to early
    parm_T1 = 2200  # T1 (Response Delay Timer) activated if data come in to prev resp to early
    parm_T2 = 3     # T2 sek (Response Delay Timer) Default: 2888 / (parm_baud / 100)
    parm_T3 = 50   # T3 sek (Inactive Link Timer) Default:180 Sek
    parm_N2 = 20    # Max Try   Default 20
    parm_baud = 1200  # Baud for calculating Timer
    # port_parm_MaxPac = 20 # Max Packets in TX Buffer (Non Prio Packets)
    ##########################
    # Parameter for CLI
    parm_cli_ctext = ''


class MD5TESTstationCFG(DefaultStationConfig):
    parm_StationCalls = ['MD5TES', 'MD6TES']
    ##########################
    # Parameter for CLI
    parm_cli_ctext = '-= TEST C-TEXT =-'

