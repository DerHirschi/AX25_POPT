from cli.cli import *


class DefaultPortConfig(object):
    ##########################
    # Parameter for Connection
    """ Port Parameter """
    parm_PortNr: int = -1
    parm_PortName: '' = ''
    parm_PortTyp: '' = ''   # 'KISSTCP' (Direwolf), 'KISSSER' (Linux AX.25 Device (kissattach)), 'AXIPCL' AXIP UDP
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
    parm_full_duplex = False    # Pseudo Full duplex Mode (Just for AXIP)
    # port_parm_MaxPac = 20 # Max Packets in TX Buffer (Non Prio Packets)
    ##########################
    # Parameter for CLI
    parm_cli: {str: DefaultCLI}
    parm_cli_ctext = ''
    #####################
    # Monitor Text Color
    parm_mon_clr_tx = "medium violet red"
    parm_mon_clr_rx = "green"

    ##########################
    # Global Objs
    glb_mh = None
    glb_port_handler = None
    glb_gui = None


class Port0(DefaultPortConfig):
    parm_PortName = 'DW'
    parm_PortTyp = 'KISSTCP'
    parm_PortParm = ('192.168.178.152', 8001)
    parm_StationCalls = ['MD5TES', 'MD6TES-1']
    parm_isSmartDigi = False
    parm_is_StupidDigi = True  # Just if parm_isSmartDigi is set to False
    parm_TXD = 1400  # TX Delay for RTT Calculation  !! Need to be high on AXIP for T1 calculation
    """ Connection Parameter """
    parm_PacLen = 170   # Max Pac len
    parm_MaxFrame = 5   # Max (I) Frames
    parm_T1 = 1800      # T1 (Response Delay Timer) activated if data come in to prev resp to early
    parm_T2 = 3000      # T2 sek (Response Delay Timer) Default: 2888 / parm_baud
    parm_T3 = 120       # T3 sek (Inactive Link Timer) Default:180 Sek
    parm_N2 = 20        # Max Try   Default 20
    parm_baud = 1200    # Baud for calculating Timer
    parm_full_duplex = False    # Pseudo Full duplex Mode (Just for AXIP)
    # port_parm_MaxPac = 20 # Max Packets in TX Buffer (Non Prio Packets)
    ##########################
    # Parameter for CLI
    parm_cli = {
        'MD5TES': UserCLI,
        'MD6TES-1': NodeCLI
    }
    # Optional Parameter. Can be deleted if not needed. Param will be get from cli.py
    parm_cli_ctext = '-= TEST C-TEXT MD5TES -Port0 =-\r\r'
    parm_cli_bye_text = '73 ...\r'
    parm_cli_prompt = '\rTEST-STATION---Port0>'
    #####################
    # Monitor Text Color
    parm_mon_clr_tx = "medium violet red"
    parm_mon_clr_rx = "green"


class Port1(DefaultPortConfig):
    parm_PortName = 'DW2'
    parm_PortTyp = 'KISSTCP'
    parm_PortParm = ('192.168.178.150', 8001)
    parm_StationCalls = ['MD5TES', 'MD6TES-2']
    parm_isSmartDigi = True
    parm_is_StupidDigi = False  # Just if parm_isSmartDigi is set to False
    parm_TXD = 1400  # TX Delay for RTT Calculation  !! Need to be high on AXIP for T1 calculation
    """ Connection Parameter """
    parm_PacLen = 170   # Max Pac len
    parm_MaxFrame = 5   # Max (I) Frames
    parm_T1 = 1800      # T1 (Response Delay Timer) activated if data come in to prev resp to early
    parm_T2 = 3000      # T2 sek (Response Delay Timer) Default: 2888 / parm_baud
    parm_T3 = 180       # T3 sek (Inactive Link Timer) Default:180 Sek
    parm_N2 = 20        # Max Try   Default 20
    parm_baud = 1200    # Baud for calculating Timer
    parm_full_duplex = False  # Pseudo Full duplex Mode (Just for AXIP)
    # port_parm_MaxPac = 20 # Max Packets in TX Buffer (Non Prio Packets)
    ##########################
    # Parameter for CLI
    parm_cli = {
        'MD5TES': UserCLI,
        'MD6TES-2': NodeCLI
    }
    # Optional Parameter. Can be deleted if not needed. Param will be get from cli.py
    parm_cli_ctext = '-= TEST C-TEXT MD5TES Port1 =-\r\r'
    parm_cli_bye_text = '73 ...\r'
    parm_cli_prompt = '\rTEST-STATION---Port1>'
    #####################
    # Monitor Text Color
    parm_mon_clr_tx = "red2"
    parm_mon_clr_rx = "green2"


class Port2(DefaultPortConfig):
    parm_PortName = 'AXIP'
    parm_PortTyp = 'AXIP'
    parm_PortParm = ('0.0.0.0', 8093)      # outgoing IP when want not using standard PC IP  , Port
    parm_StationCalls = ['MD7TES', 'MD6TES-2']
    parm_isSmartDigi = False
    parm_is_StupidDigi = False  # Just if parm_isSmartDigi is set to False
    parm_TXD = 1  # TX Delay for RTT Calculation  !! Need to be high on AXIP for T1 calculation
    """ Connection Parameter """
    parm_PacLen = 230  # Max Pac len
    parm_MaxFrame = 5  # Max (I) Frames
    parm_T1 = 1     # T1 (Response Delay Timer) activated if data come in to prev resp to early
    parm_T2 = 1     # T2 sek (Response Delay Timer) Default: 2888 / parm_baud
    parm_T3 = 180   # T3 sek (Inactive Link Timer) Default:180 Sek
    parm_N2 = 20  # Max Try   Default 20
    parm_baud = 119200  # Baud for calculating Timer
    parm_full_duplex = True  # Pseudo Full duplex Mode (Just for AXIP)
    # port_parm_MaxPac = 20 # Max Packets in TX Buffer (Non Prio Packets)
    ##########################
    # Parameter for CLI
    parm_cli = {
        'MD7TES': UserCLI,
        'MD6TES-2': NodeCLI
    }
    # Optional Parameter. Can be deleted if not needed. Param will be get from cli.py
    parm_cli_ctext = '-= TEST C-TEXT MD5TES Port2 =-\r\r'
    parm_cli_bye_text = '73 ...\r'
    parm_cli_prompt = '\rTEST-STATION---Port2>'
    #####################
    # Monitor Text Color
    parm_mon_clr_tx = "orange2"
    parm_mon_clr_rx = "PaleGreen3"


class Port3(DefaultPortConfig):
    parm_PortName = 'SER'
    parm_PortTyp = 'KISSSER'
    parm_PortParm = ('/dev/pts/9', 9600)
    parm_StationCalls = ['MD8TES', 'MD7TES-2']
    parm_isSmartDigi = False
    parm_is_StupidDigi = False  # Just if parm_isSmartDigi is set to False
    parm_TXD = 1400  # TX Delay for RTT Calculation  !! Need to be high on AXIP for T1 calculation
    """ Connection Parameter """
    parm_PacLen = 170  # Max Pac len
    parm_MaxFrame = 5  # Max (I) Frames
    parm_T1 = 1800  # T1 (Response Delay Timer) activated if data come in to prev resp to early
    parm_T2 = 3000  # T2 sek (Response Delay Timer) Default: 2888 / parm_baud
    parm_T3 = 180  # T3 sek (Inactive Link Timer) Default:180 Sek
    parm_N2 = 20  # Max Try   Default 20
    parm_baud = 1200  # Baud for calculating Timer
    parm_full_duplex = False  # Pseudo Full duplex Mode (Just for AXIP)
    # port_parm_MaxPac = 20 # Max Packets in TX Buffer (Non Prio Packets)
    ##########################
    # Parameter for CLI
    parm_cli = {
        'MD8TES': UserCLI,
        'MD7TES-7': NodeCLI
    }
    # Optional Parameter. Can be deleted if not needed. Param will be get from cli.py
    parm_cli_ctext = '-= TEST C-TEXT MD5TES Port3 =-\r\r'
    parm_cli_bye_text = '73 ...\r'
    parm_cli_prompt = '\rTEST-STATION---Port3>'
    #####################
    # Monitor Text Color
    parm_mon_clr_tx = "gold2"
    parm_mon_clr_rx = "SkyBlue4"


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
