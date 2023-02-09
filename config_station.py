import ax25.ax25Statistics
from cli.cli import *


class DefaultPortConfig(object):
    ##########################
    # Parameter for Connection
    """ Port Parameter """
    parm_PortName: '' = ''
    parm_PortTyp: '' = ''
    parm_PortParm = ''
    parm_StationCalls: [''] = []
    parm_isSmartDigi = False
    parm_is_StupidDigi = False  # Just if parm_isDigi is set to False
    parm_TXD = 1400  # TX Delay for RTT Calculation  !! Need to be high on AXIP for T1 calculation
    """ Connection Parameter """
    parm_PacLen = 170   # Max Pac len
    parm_MaxFrame = 5   # Max (I) Frames
    parm_T1 = 1800      # T1 (Response Delay Timer) activated if data come in to prev resp to early
    parm_T2 = 3000      # T2 sek (Response Delay Timer) Default: 2888 / parm_baud
    parm_T3 = 120       # T3 sek (Inactive Link Timer) Default:180 Sek
    parm_N2 = 20        # Max Try   Default 20
    parm_baud = 1200    # Baud for calculating Timer
    # port_parm_MaxPac = 20 # Max Packets in TX Buffer (Non Prio Packets)
    ##########################
    # Parameter for CLI
    parm_cli = DefaultCLI
    parm_cli_ctext = ''
    parm_mh = ax25.ax25Statistics.MH()


class Port0(DefaultPortConfig):
    parm_PortName = 'DW'
    parm_PortTyp = 'KISSTCP'
    parm_PortParm = ('192.168.178.152', 8001)
    parm_StationCalls = ['MD5TES', 'MD6TES-1']
    parm_isSmartDigi = True
    parm_is_StupidDigi = False  # Just if parm_isSmartDigi is set to False
    parm_TXD = 1400  # TX Delay for RTT Calculation  !! Need to be high on AXIP for T1 calculation
    """ Connection Parameter """
    parm_PacLen = 170   # Max Pac len
    parm_MaxFrame = 5   # Max (I) Frames
    parm_T1 = 1800      # T1 (Response Delay Timer) activated if data come in to prev resp to early
    parm_T2 = 3000      # T2 sek (Response Delay Timer) Default: 2888 / parm_baud
    parm_T3 = 120       # T3 sek (Inactive Link Timer) Default:180 Sek
    parm_N2 = 20        # Max Try   Default 20
    parm_baud = 1200    # Baud for calculating Timer
    # port_parm_MaxPac = 20 # Max Packets in TX Buffer (Non Prio Packets)
    ##########################
    # Parameter for CLI
    parm_cli = UserCLI
    # Optional Parameter. Can be deleted if not needed. Param will be get from cli.py
    parm_cli_ctext = '-= TEST C-TEXT MD5TES -Port0 =-\r\r'
    parm_cli_bye_text = '73 ...\r'
    parm_cli_prompt = '\rTEST-STATION---Port0>'


class Port1(DefaultPortConfig):
    parm_PortName = '01'
    parm_PortTyp = 'KISS'
    parm_PortParm = '/tmp/tty1'
    parm_StationCalls = ['MD5TES', 'MD6TES-2']
    parm_isSmartDigi = True
    parm_is_StupidDigi = False  # Just if parm_isSmartDigi is set to False
    parm_TXD = 1400  # TX Delay for RTT Calculation  !! Need to be high on AXIP for T1 calculation
    """ Connection Parameter """
    parm_PacLen = 170   # Max Pac len
    parm_MaxFrame = 5   # Max (I) Frames
    parm_T1 = 1800      # T1 (Response Delay Timer) activated if data come in to prev resp to early
    parm_T2 = 3000      # T2 sek (Response Delay Timer) Default: 2888 / parm_baud
    parm_T3 = 120       # T3 sek (Inactive Link Timer) Default:180 Sek
    parm_N2 = 20        # Max Try   Default 20
    parm_baud = 1200    # Baud for calculating Timer
    # port_parm_MaxPac = 20 # Max Packets in TX Buffer (Non Prio Packets)
    ##########################
    # Parameter for CLI
    parm_cli = UserCLI
    # Optional Parameter. Can be deleted if not needed. Param will be get from cli.py
    parm_cli_ctext = '-= TEST C-TEXT MD5TES Port1 =-\r\r'
    parm_cli_bye_text = '73 ...\r'
    parm_cli_prompt = '\rTEST-STATION---Port1>'


class Port2(DefaultPortConfig):
    pass


class Port3(DefaultPortConfig):
    pass


class Port4(DefaultPortConfig):
    pass


class Port5(DefaultPortConfig):
    pass


class Port6(DefaultPortConfig):
    pass


class Port7(DefaultPortConfig):
    pass


class Port8(DefaultPortConfig):
    pass


class Port9(DefaultPortConfig):
    pass


class Port10(DefaultPortConfig):
    pass
