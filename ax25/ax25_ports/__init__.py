from fnc.os_fnc import is_linux, is_macos
from .ax25Port_AGWPE_TCP import AGWPE_TCP
from .ax25Port_AX25Kernel import AX25KernelDEV
from .ax25Port_AXIP import AXIP
from .ax25Port_KISS import KissTCP, KISSSerial
from .ax25Port_TNC_EMU import TNC_EMU_TCP_SRV, TNC_EMU_TCP_CL

AX25DeviceTAB = {
            'KISSTCP': KissTCP,
            'KISSSER': KISSSerial,
            'AXIP': AXIP,
            'AX25KERNEL': AX25KernelDEV,
            'TNC-EMU-TCP-SRV': TNC_EMU_TCP_SRV,
            'TNC-EMU-TCP-CL': TNC_EMU_TCP_CL,
            'AGWPE-TCP': AGWPE_TCP,
        }
if not is_linux() or is_macos():
    del AX25DeviceTAB['AX25KERNEL']
