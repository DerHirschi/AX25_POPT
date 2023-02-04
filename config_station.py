
class DefaultStationConfig(object):
    ##########################
    # Parameter for Connection
    """ Port Parameter """
    parm_PortName: '' = ''
    parm_StationCalls: [''] = []
    parm_isSmartDigi = False
    parm_is_StupidDigi = False  # Just if parm_isDigi is set to False
    parm_TXD = 1200  # TX Delay for RTT Calculation  !! Need to be high on AXIP for T1 calculation
    """ Connection Parameter """
    parm_PacLen = 170  # Max Pac len
    parm_MaxFrame = 5  # Max (I) Frames
    parm_T1 = 3000  # T1 (Response Delay Timer) activated if data come in to prev resp to early
    parm_T2 = 2888  # T2 sek (Response Delay Timer) Default: 2888 / parm_baud
    parm_T3 = 120   # T3 sek (Inactive Link Timer) Default:180 Sek
    parm_N2 = 20    # Max Try   Default 20
    parm_baud = 1200  # Baud for calculating Timer
    # port_parm_MaxPac = 20 # Max Packets in TX Buffer (Non Prio Packets)
    ##########################
    # Parameter for CLI
    parm_cli_ctext = ''


class MD5TESTstationCFG(DefaultStationConfig):
    parm_PortName = 'DW'
    parm_StationCalls = ['MD5TES', 'MD6TES']
    parm_isSmartDigi = True    # Bullshit Idea
    parm_is_StupidDigi = False
    ##########################
    # Parameter for CLI
    parm_cli_ctext = '-= TEST C-TEXT =-'

