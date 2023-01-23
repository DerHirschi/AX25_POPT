import logging
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
logger = logging.getLogger(__name__)


def bl2str(inp):
    if inp:
        return '+'
    else:
        return '-'


class Call(object):
    call = ''
    hex_str: b''
    """Address > CRRSSID1    Digi > HRRSSID1"""
    s_bit: bool  # Stop Bit      Bit 8
    c_bit: bool  # C bzw H Bit   Bit 1
    ssid: int    # SSID          Bit 4 - 7
    r_bits: bin  # Bit 2 - 3 not used. Free to use for any application .?..

    def dec_call(self, inp: b''):
        self.call = ''
        for c in inp[:-1]:
            self.call += chr(int(c) >> 1)
        """Address > CRRSSID1    Digi > HRRSSID1"""
        bi = bin(int(hex(inp[-1])[2:], 16))[2:].zfill(8)
        self.s_bit = bool(int(bi[7], 2))  # Stop Bit      Bit 8
        self.c_bit = bool(int(bi[0], 2))  # C bzw H Bit   Bit 1
        self.ssid = int(bi[3:7], 2)  # SSID          Bit 4 - 7
        self.r_bits = bi[1:3]  # Bit 2 - 3 not used. Free to use for any application .?..


class CByte(object):
    """
    ctl_str = ''       # Monitor Out
    type = ''          # Control Field Type ( U, I, S )
    flag = ''          # Control Field Flag ( RR, REJ, SABM ... )
    pf = False         # P/F Bit
    cmd = False        # Command or Report ( C Bits in Address Field )
    nr = -1            # N(R)
    ns = -1            # N(S)
    pid = False        # Next Byte PID Field Trigger
    info = False       # Info Field Trigger
    hex = 0x00         # Input as Hex
    """
    def __init__(self):
        self.ctl_str = ''            # Monitor Out
        self.type = ''               # Control Field Type ( U, I, S )
        self.flag = ''               # Control Field Flag ( RR, REJ, SABM ... )
        self.pf = False              # P/F Bit
        self.cmd = False             # Command or Report ( C Bits in Address Field )
        self.nr = -1                 # N(R)
        self.ns = -1                 # N(S)
        self.pid = False             # Next Byte PID Field Trigger
        self.info = False            # Info Field Trigger
        self.hex = 0xff              # Input as Hex
        self.pac_types = {
            0x3f: self.SABMcByte,
            0x53: self.DISCcByte,
            0x1f: self.DMcByte,
            0x73: self.UAcByte,
            0x13: self.UIcByte,
            0x97: self.FRMRcByte
        }

    def dec_cbyte(self, in_byte):
        if int(in_byte) in self.pac_types.keys():
            print("Predefined Pac Type.. {}".format(in_byte))
            self.pac_types[int(in_byte)]()
        else:
            print("Not predefined Pac Type..")
            # self.ctl_byte.dec_cbyte(self.hexstr[index])
            self.hex = hex(int(in_byte))
            bi = bin(int(in_byte))[2:].zfill(8)
            pf = bool(int(bi[3], 2))  # P/F
            self.pf = pf
            if bi[-1] == '0':  # I-Block   Informationsübertragung
                nr = int(bi[:3], 2)
                ns = int(bi[4:7], 2)
                self.ctl_str = 'I' + str(nr) + str(ns) + bl2str(pf)
                self.type, self.flag = 'I', 'I'
                self.nr, self.ns = nr, ns
                self.pid, self.info = True, True
            elif bi[-2:] == '01':  # S-Block
                self.nr = int(bi[:3], 2)
                self.type = 'S'
                ss_bits = bi[4:6]
                if ss_bits == '00':  # Empfangsbereit RR
                    self.ctl_str = 'RR' + str(self.nr) + bl2str(pf)  # P/F Bit add +/-
                    self.flag = 'RR'
                elif ss_bits == '01':  # Nicht empfangsbereit RNRR
                    self.ctl_str = 'RNRR' + bl2str(pf)  # P/F Bit add +/-
                    self.flag = 'RNRR'
                elif ss_bits == '10':  # Wiederholungsaufforderung REJ
                    self.ctl_str = 'REJ' + str(self.nr) + bl2str(pf)  # P/F Bit add +/-
                    self.flag = 'REJ'
                else:  # ss_bits == '11':                                  # Selective Reject SREJ
                    self.ctl_str = 'SREJ' + str(self.nr) + bl2str(pf)  # P/F Bit add +/-
                    self.flag = 'SREJ'

            elif bi[-2:] == '11':  # U-Block
                self.type = 'U'
                mmm = bi[0:3]
                mm = bi[4:6]
                if mmm == '001' and mm == '11':
                    self.ctl_str = "SABM" + bl2str(pf)  # Verbindungsanforderung
                    self.flag = 'SABM'
                elif mmm == '011' and mm == '11':
                    self.ctl_str = "SABME" + bl2str(pf)  # Verbindungsanforderung EAX25 (Modulo 128 C Field)
                    self.flag = 'SABME'
                elif mmm == '010' and mm == '00':
                    self.ctl_str = "DISC" + bl2str(pf)  # Verbindungsabbruch
                    self.flag = 'DISC'
                elif mmm == '000' and mm == '11':
                    self.ctl_str = "DM" + bl2str(pf)  # Verbindungsrückweisung
                    self.flag = 'DM'
                elif mmm == '011' and mm == '00':
                    self.ctl_str = "UA" + bl2str(pf)  # Unnummerierte Bestätigung
                    self.flag = 'UA'
                elif mmm == '100' and mm == '01':
                    self.ctl_str = "FRMR" + bl2str(pf)  # Rückweisung eines Blocks
                    self.flag = 'FRMR'
                    self.info = True
                elif mmm == '000' and mm == '00':
                    self.ctl_str = "UI" + bl2str(pf)  # Unnummerierte Information UI
                    self.flag = 'UI'
                    self.pid, self.info = True, True
                elif mmm == '111' and mm == '00':
                    self.ctl_str = 'TEST' + bl2str(pf)  # TEST Frame
                    self.flag = 'TEST'
                    self.info = True
                elif mmm == '101' and mm == '11':
                    self.ctl_str = 'XID' + bl2str(pf)  # XID Frame
                    self.flag = 'XID'
                else:
                    logger.error('C-Byte Error U Frame ! > ' + str(bi) + ' ' + str(in_byte))

    def SABMcByte(self):
        self.ctl_str = 'SABM+'
        self.hex = hex(0x3f)
        self.type = 'U'
        self.flag = 'SABM'
        self.pf = True
        self.cmd = True
        self.pid = False
        self.info = False

    def DISCcByte(self):
        self.ctl_str = 'DISC+'
        self.hex = hex(0x53)
        self.type = 'U'
        self.flag = 'DISC'
        self.pf = True
        self.cmd = True
        self.pid = False
        self.info = False

    def DMcByte(self):
        self.ctl_str = 'DM+'
        self.hex = hex(0x1f)
        self.type = 'U'
        self.flag = 'DM'
        self.pf = True
        self.cmd = False
        self.pid = False
        self.info = False

    def UAcByte(self):
        self.ctl_str = 'UA+'
        self.hex = hex(0x73)
        self.type = 'U'
        self.flag = 'UA'
        self.pf = True
        self.cmd = False
        self.pid = False
        self.info = False

    def UIcByte(self):   # !! UI+ ???
        self.ctl_str = 'UI+'
        self.hex = hex(0x13)
        self.type = 'U'
        self.flag = 'UI'
        self.pf = True
        self.cmd = False
        self.pid = True
        self.info = True

    def FRMRcByte(self):
        self.ctl_str = 'FRMR+'
        self.hex = hex(0x97)
        self.type = 'U'
        self.flag = 'FRMR'
        self.pf = True
        self.cmd = False
        self.pid = False
        self.info = True


class PIDByte(object):
    def __init__(self):
        self.hex = 0x00
        self.flag = ''
        self.escape = False
        self.pac_types = {
            0xF0: self.text,
            0xCF: self.netrom,
            0xCC: self.ip,
            0xCD: self.arpa,
            0xCE: self.flexnet,
            0x01: self.x25plp,
            0x06: self.tcip_comp,
            0x07: self.tcip_uncomp,
            0x08: self.segm_fragment,
            0xC3: self.textnet_datag,
            0xC4: self.linkqual_protoc,
            0xCA: self.appletalk,
            0xCB: self.appletalk_arp,
            0xFF: self.esc,
        }

    def decode(self, in_byte: b''):
        if int(in_byte) in self.pac_types.keys():
            self.pac_types[int(in_byte)]()
        else:
            in_byte = int(in_byte, 16)
            bi = bin(in_byte)[2:].zfill(8)
            if bi[2:5] in ['01', '10']:
                self.ax25_l3(hex(int(in_byte)))

    def text(self):
        self.hex = 0xF0
        self.flag = 'Text (NO L3)'

    def netrom(self):
        self.hex = 0xCF
        self.flag = 'NET/ROM (L3/4)'

    def ip(self):
        self.hex = 0xCC
        self.flag = 'IP (L3)'

    def arpa(self):
        self.hex = 0xCD
        self.flag = 'ARPA Address res(L3)'

    def flexnet(self):
        self.hex = 0xCE
        self.flag = 'FlexNet'

    def x25plp(self):
        self.hex = 0x01
        self.flag = 'X.25 PLP'

    def tcip_comp(self):
        self.hex = 0x06
        self.flag = 'Compressed TCP/IP'

    def tcip_uncomp(self):
        self.hex = 0x07
        self.flag = 'Uncompressed TCP/IP'

    def segm_fragment(self):
        self.hex = 0x08
        self.flag = 'Segmentation fragment'

    def textnet_datag(self):
        self.hex = 0xC3
        self.flag = 'TEXTNET datagram'

    def linkqual_protoc(self):
        self.hex = 0xC4
        self.flag = 'Link Quality Protocol'

    def appletalk(self):
        self.hex = 0xCA
        self.flag = 'Appletalk'

    def appletalk_arp(self):
        self.hex = 0xCB
        self.flag = 'Appletalk ARP'

    def ax25_l3(self, in_hex):
        self.hex = in_hex
        self.flag = 'AX.25 (L3)'

    def esc(self):
        self.hex = 0xFF
        self.flag = 'Escape. Next Byte has more L3 Infos'
        self.escape = True


class AX25Frame(object):
    def __init__(self):
        self.kiss = b''
        self.hexstr = b''           # Dekiss
        self.from_call = Call()
        self.to_call = Call()
        self.via_call = []
        self.ctl_byte = CByte()

        self.pid_byte = PIDByte()
        self.data = b''
        self.data_len = 0

    def decode(self, hexstr: b''):
        self.kiss = hexstr[:2]
        self.hexstr = hexstr[2:-1]                      # Dekiss
        self.to_call.dec_call(self.hexstr[:7])
        self.from_call.dec_call(self.hexstr[7:14])
        n = 2
        if not self.to_call.s_bit:
            while True:
                tmp = Call()
                tmp.dec_call(self.hexstr[7 * n: 7 + 7 * n])
                self.via_call.append(tmp)
                if tmp.s_bit:
                    break
                n += 1
        index = (7 * n) + 7
        # Dec C-Byte
        self.ctl_byte.dec_cbyte(self.hexstr[index])
        # Get Command Bits
        if self.to_call.c_bit and not self.from_call.c_bit:
            self.ctl_byte.cmd = True
        elif not self.to_call.c_bit and self.from_call.c_bit:
            self.ctl_byte.cmd = False
        # Get PID if available
        if self.ctl_byte.pid:
            index += 1
            self.pid_byte.decode(self.hexstr[index])
            # self.pid_byte.pac_types[self.hexstr[index]]()


