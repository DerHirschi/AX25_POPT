import ax25.ax25Statistics
from cli.cli import *


class DefaultStationConfig(object):
    ##########################
    # Parameter for Connection
    """ Port Parameter """
    parm_PortName: '' = ''
    parm_StationCalls: [''] = []
    parm_isSmartDigi = False
    parm_is_StupidDigi = False  # Just if parm_isDigi is set to False
    parm_TXD = 1400  # TX Delay for RTT Calculation  !! Need to be high on AXIP for T1 calculation
    """ Connection Parameter """
    parm_PacLen = 170  # Max Pac len
    parm_MaxFrame = 5  # Max (I) Frames
    parm_T1 = 1800  # T1 (Response Delay Timer) activated if data come in to prev resp to early
    parm_T2 = 3000  # T2 sek (Response Delay Timer) Default: 2888 / parm_baud
    parm_T3 = 120   # T3 sek (Inactive Link Timer) Default:180 Sek
    parm_N2 = 20    # Max Try   Default 20
    parm_baud = 1200  # Baud for calculating Timer
    # port_parm_MaxPac = 20 # Max Packets in TX Buffer (Non Prio Packets)
    ##########################
    # Parameter for CLI
    parm_cli = DefaultCLI
    parm_cli_ctext = ''
    parm_mh = ax25.ax25Statistics.MH()


class MD5TESTstationCFG(DefaultStationConfig):
    parm_PortName = 'DW'
    parm_StationCalls = ['MD5TES', 'MD6TES']
    parm_isSmartDigi = True     # Stupid DIGI has to be False
    parm_is_StupidDigi = False
    ##########################
    # Parameter for CLI
    parm_cli = NodeCLI
    # Optional Parameter. Can be deleted if not needed. Param will be get from cli.py
    parm_cli_ctext = '-= TEST C-TEXT MD5TES CFG =-\r\r'
    parm_cli_bye_text = '73 ...\r'
    parm_cli_prompt = '\rTEST-STATION---2>'

