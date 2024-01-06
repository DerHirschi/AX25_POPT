"""
    Layer 2 ??
    AX.25 Packet enc-/decoding
    TODO: Cleanup/optimising
"""
from ax25.ax25Error import AX25EncodingERROR, AX25DecodingERROR, logger
from fnc.ax25_fnc import reverse_uid, get_call_str, call_tuple_fm_call_str


def bl2str(inp):
    """ Bool to String """
    if inp:
        return '+'
    else:
        return '-'


def format_hex2bin(inp=''):
    fl = hex(int(inp, 2))[2:]
    if len(fl) == 1:
        return '0' + fl
    return fl


def bytearray2hexstr(inp):
    return ''.join('{:02x}'.format(x) for x in inp)


def format_hexstr(inp):
    if type(inp) is int:
        return '{:02x}'.format(inp)
    elif type(inp) is str:
        return '{:02x}'.format(int(inp, 16))


def decode_FRMR(ifield):
    if len(ifield) != 3:
        print("Invalid I-Field length")
        return '\nInvalid I-Field length\n'

    control_byte = ifield[0]
    pid_byte = ifield[1]
    data_bytes = ifield[2:]

    # Decode Control byte
    control_bits = bin(control_byte)[2:].zfill(8)
    ns = int(control_bits[0:3], 2)
    nr = int(control_bits[3:6], 2)
    pf_bit = int(control_bits[6], 2)

    # Decode PID byte
    pid = pid_byte

    # Decode Data bytes
    data = []
    for byte in data_bytes:
        data.append(chr(byte))
    tmp = "\nDecoded FRMR Frame:\n" +  \
          f"Control: NS={ns}, NR={nr}, PF={pf_bit}\n" + \
          f"PID: {pid}\n" + \
          f"Data: {''.join(data)}\n"

    print("Decoded FRMR Frame:")
    print("Control: NS={}, NR={}, PF={}".format(ns, nr, pf_bit))
    print("PID: {}".format(pid))
    print("Data: {}".format("".join(data)))
    logger.warning("Decoded FRMR Frame:")
    logger.warning("Control: NS={}, NR={}, PF={}".format(ns, nr, pf_bit))
    logger.warning("PID: {}".format(pid))
    logger.erwarningror("Data: {}".format("".join(data)))
    return tmp


class Call:
    def __init__(self):
        self.call = ''
        self.call_str = ''
        self.hex_str = b''
        """Address > CRRSSID1    Digi > HRRSSID1"""
        self.s_bit = False   # Stop Bit      Bit 8
        self.c_bit = False   # C bzw H Bit   Bit 1
        self.ssid = 0        # SSID          Bit 4 - 7
        self.r_bits = '11'   # Bit 2 - 3 not used. Free to use for any application .?..

    def dec_call(self, inp: b''):
        self.call = ''
        for c in inp[:-1]:
            self.call += chr(int(c) >> 1)
        self.call = self.call.replace(' ', '').upper()
        """Address > CRRSSID1    Digi > HRRSSID1"""
        bi = bin(inp[-1])[2:].zfill(8)
        self.s_bit = bool(int(bi[7], 2))    # Stop Bit      Bit 8
        self.c_bit = bool(int(bi[0], 2))    # C bzw H Bit   Bit 1
        self.ssid = int(bi[3:7], 2)         # SSID          Bit 4 - 7
        self.r_bits = bi[1:3]               # Bit 2 - 3 not used. Free to use for any application .?..
        self.call_str = get_call_str(self.call, self.ssid)

    def enc_call(self):
        """
        out_str += encode_address_char(dest)
        out_str += encode_ssid(dest_ssid, dest_c)
        out_str += encode_address_char(call)
        """
        if self.call:
            self.call_str = get_call_str(self.call, self.ssid)
        elif self.call_str:
            tmp = call_tuple_fm_call_str(self.call_str)
            self.call = tmp[0]
            self.ssid = tmp[1]
        else:
            logger.error('AX25EncodingERROR: No Call set !')
            logger.error('AX25EncodingERROR: Call: {}'.format(self.call) )
            logger.error('AX25EncodingERROR: Call_str: {}'.format(self.call_str) )
            raise AX25EncodingERROR()
        out = ''
        # Address
        ascii_str = "{:<6}".format(self.call.upper())
        t = bytearray(ascii_str.encode('ASCII'))
        for i in t:
            out += hex(i << 1)[2:]
        # SSID and BITs
        ssid_in = bin(self.ssid << 1)[2:].zfill(8)
        if self.c_bit:
            ssid_in = '1' + ssid_in[1:]  # Set C or H Bit. H Bit if msg was geDigit
        if self.s_bit:
            ssid_in = ssid_in[:-1] + '1'  # Set Stop Bit on last DIGI
        ssid_in = ssid_in[:1] + self.r_bits + ssid_in[3:]  # Set R R Bits True.
        out += format_hex2bin(ssid_in)
        self.hex_str = out.encode()

    def validate(self):
        """
        :return: bool
        """
        if len(self.call) < 2 or len(self.call) > 6:    # Calls like CQ or ID
            logger.error('Call validator: Call length')
            return False
        """
        if not self.call.isascii():
            logger.error('Call validator: Call.isascii()')
            return False
        """
        if self.ssid > 15 or self.ssid < 0:
            logger.error('Call validator: SSID')
            return False
        for c in self.call:
            if c.isupper() or c.isdigit():
                pass
            else:
                return False
        return True


class CByte:
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
        self.mon_str = ''            # Monitor Out
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

    def enc_cbyte(self):    # Just if not standard Packets (pac_types)
        # if self.hex not in self.pac_types.keys():
        ret = ''.zfill(8)
        if self.pf:
            ret = ret[:3] + '1' + ret[4:]
        # I Block
        if self.flag == 'I':
            ret = bin(max(min(self.nr, 7), 0))[2:].zfill(3) + ret[3:]           # N(R)
            ret = ret[:4] + bin(max(min(self.ns, 7), 0))[2:].zfill(3) + '0'     # N(S)
        # S Block
        elif self.flag in ['RR', 'RNR', 'REJ', 'SREJ']:
            ret = ret[:-2] + '01'
            ret = bin(max(min(self.nr, 7), 0))[2:].zfill(3) + ret[3:]
            if self.flag == 'RR':
                ret = ret[:4] + '00' + ret[-2:]
            elif self.flag == 'RNR':
                ret = ret[:4] + '01' + ret[-2:]
            elif self.flag == 'REJ':
                ret = ret[:4] + '10' + ret[-2:]
            elif self.flag == 'SREJ':
                ret = ret[:4] + '11' + ret[-2:]
        # U Block   should have static hex ( self.pac_types ) but for special reasons.
        elif self.flag in ['SABM', 'DISC', 'DM', 'UA', 'FRMR', 'UI', 'TEST', 'XID']:
            ret = ret[:-2] + '11'
            if self.flag == 'SABM':
                ret = '001' + ret[3] + '11' + ret[-2:]
            elif self.flag == 'DISC':
                ret = '010' + ret[3] + '00' + ret[-2:]
            elif self.flag == 'DM':
                ret = '000' + ret[3] + '11' + ret[-2:]
            elif self.flag == 'UA':
                ret = '011' + ret[3] + '00' + ret[-2:]
            elif self.flag == 'UI':
                ret = '000' + ret[3] + '00' + ret[-2:]
            elif self.flag == 'FRMR':
                ret = '100' + ret[3] + '01' + ret[-2:]
            elif self.flag == 'TEST':  # TODO Not completely implemented yet
                ret = '111' + ret[3] + '00' + ret[-2:]
                self.info = True
            elif self.flag == 'XID':  # TODO Not implemented yet
                ret = '101' + ret[3] + '11' + ret[-2:]
                self.info = True
        self.hex = hex(int(ret, 2))

    def dec_cbyte(self, in_byte):
        if int(in_byte) in self.pac_types.keys():
            self.pac_types[int(in_byte)]()
        else:
            self.hex = hex(int(in_byte))
            bi = bin(int(in_byte))[2:]
            bi = bi.zfill(8)
            pf = bool(int(bi[3], 2))  # P/F
            self.pf = pf
            if bi[-1] == '0':  # I-Block   Informationsübertragung
                nr = int(bi[:3], 2)
                ns = int(bi[4:7], 2)
                self.mon_str = 'I' + str(nr) + str(ns) + bl2str(pf)
                self.type, self.flag = 'I', 'I'
                self.nr, self.ns = nr, ns
                self.pid, self.info = True, True
            elif bi[-2:] == '01':  # S-Block
                self.nr = int(bi[:3], 2)
                self.type = 'S'
                ss_bits = bi[4:6]
                if ss_bits == '00':  # Empfangsbereit RR
                    self.mon_str = 'RR' + str(self.nr) + bl2str(pf)  # P/F Bit add +/-
                    self.flag = 'RR'
                elif ss_bits == '01':  # Nicht empfangsbereit RNR
                    self.mon_str = 'RNR' + bl2str(pf)  # P/F Bit add +/-
                    self.flag = 'RNR'
                elif ss_bits == '10':  # Wiederholungsaufforderung REJ
                    self.mon_str = 'REJ' + str(self.nr) + bl2str(pf)  # P/F Bit add +/-
                    self.flag = 'REJ'
                else:  # ss_bits == '11':                                  # Selective Reject SREJ
                    self.mon_str = 'SREJ' + str(self.nr) + bl2str(pf)  # P/F Bit add +/-
                    self.flag = 'SREJ'

            elif bi[-2:] == '11':  # U-Block
                self.type = 'U'
                mmm = bi[0:3]
                mm = bi[4:6]
                if mmm == '001' and mm == '11':
                    self.mon_str = "SABM" + bl2str(pf)  # Verbindungsanforderung
                    self.flag = 'SABM'
                elif mmm == '011' and mm == '11':
                    self.mon_str = "SABME" + bl2str(pf)  # Verbindungsanforderung EAX25 (Modulo 128 C Field)
                    self.flag = 'SABME'
                elif mmm == '010' and mm == '00':
                    self.mon_str = "DISC" + bl2str(pf)  # Verbindungsabbruch
                    self.flag = 'DISC'
                elif mmm == '000' and mm == '11':
                    self.mon_str = "DM" + bl2str(pf)  # Verbindungsrückweisung
                    self.flag = 'DM'
                elif mmm == '011' and mm == '00':
                    self.mon_str = "UA" + bl2str(pf)  # Unnummerierte Bestätigung
                    self.flag = 'UA'
                elif mmm == '100' and mm == '01':
                    self.mon_str = "FRMR" + bl2str(pf)  # Rückweisung eines Blocks
                    self.flag = 'FRMR'
                    self.info = True
                elif mmm == '000' and mm == '00':
                    self.mon_str = "UI" + bl2str(pf)  # Unnummerierte Information UI
                    self.flag = 'UI'
                    self.pid, self.info = True, True
                elif mmm == '111' and mm == '00':
                    self.mon_str = 'TEST' + bl2str(pf)  # TEST Frame
                    self.flag = 'TEST'
                    self.info = True
                elif mmm == '101' and mm == '11':
                    self.mon_str = 'XID' + bl2str(pf)  # XID Frame
                    self.flag = 'XID'
                else:
                    logger.error('C-Byte Error Decoding U Frame ! Unknown C-Byte> ' + str(bi) + ' ' + hex(in_byte))
                    raise AX25DecodingERROR

    def validate(self):
        if self.hex == 0xff:
            logger.error('C_Byte validator')
            return False
        return True

    def IcByte(self):
        self.type = 'I'
        self.flag = 'I'
        # self.pf = False
        self.cmd = True
        self.pid = True
        self.info = True
        self.mon_str = self.flag + str(self.nr) + str(self.ns) + bl2str(self.pf)

    def RRcByte(self):
        self.type = 'S'
        self.flag = 'RR'
        # self.pf = False
        # self.cmd = True
        self.pid = False
        self.info = False
        self.mon_str = self.flag + str(self.nr) + bl2str(self.pf)

    def RNRcByte(self):
        self.type = 'S'
        self.flag = 'RNR'
        # self.pf = False
        # self.cmd = True
        self.pid = False
        self.info = False
        self.mon_str = self.flag + bl2str(self.pf)

    def REJcByte(self):
        self.type = 'S'
        self.flag = 'REJ'
        # self.pf = False
        # self.cmd = True
        self.pid = False
        self.info = False
        self.mon_str = self.flag + str(self.nr) + bl2str(self.pf)

    def SREJcByte(self):    # EAX.25 ??
        self.type = 'S'
        self.flag = 'SREJ'
        # self.pf = False
        # self.cmd = True
        self.pid = False
        self.info = False
        self.mon_str = self.flag + str(self.nr) + bl2str(self.pf)

    def SABMcByte(self):
        self.hex = hex(0x3f)
        self.type = 'U'
        self.flag = 'SABM'
        self.pf = True
        self.cmd = True
        self.pid = False
        self.info = False
        self.mon_str = self.flag + bl2str(self.pf)

    def DISCcByte(self):
        self.hex = hex(0x53)
        self.type = 'U'
        self.flag = 'DISC'
        self.pf = True
        self.cmd = True
        self.pid = False
        self.info = False
        self.mon_str = self.flag + bl2str(self.pf)

    def DMcByte(self):
        self.hex = hex(0x1f)
        self.type = 'U'
        self.flag = 'DM'
        self.pf = True
        self.cmd = False
        self.pid = False
        self.info = False
        self.mon_str = self.flag + bl2str(self.pf)

    def UAcByte(self):
        self.hex = hex(0x73)
        self.type = 'U'
        self.flag = 'UA'
        self.pf = True
        self.cmd = False
        self.pid = False
        self.info = False
        self.mon_str = self.flag + bl2str(self.pf)

    def UIcByte(self):   # !! UI+ ???
        self.hex = hex(0x13)
        self.type = 'U'
        self.flag = 'UI'
        self.pf = True
        self.cmd = False
        self.pid = True
        self.info = True
        self.mon_str = self.flag + bl2str(self.pf)

    def FRMRcByte(self):
        self.hex = hex(0x97)
        self.type = 'U'
        self.flag = 'FRMR'
        # self.pf = True
        self.cmd = False
        self.pid = False
        self.info = True
        self.mon_str = self.flag + bl2str(self.pf)


class PIDByte:

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
        # self.text()     # Standard PID Text 0xf0

    def decode(self, in_byte: b''):
        if int(in_byte) in self.pac_types.keys():
            self.pac_types[int(in_byte)]()
        else:
            logger.debug("decode in_pid_bate hex: {}".format(hex(in_byte)))
            logger.debug("decode in_pid_bate byte: {}".format(type(in_byte)))
            #in_byte = int(in_byte, 16)

            bi = bin(in_byte)[2:].zfill(8)
            if bi[2:5] in ['01', '10']:
                self.ax25_l3(hex(int(in_byte)))

    def validate(self):
        if self.hex == 0x00:
            logger.error('PID_Byte validator : {}'.format(self.hex))
            return False
        return True

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


class AX25Frame:
    def __init__(self):
        # self.kiss = b''
        self.data_bytes = b''       # AX25-Frame decoded Raw-Data
        self.from_call = Call()
        self.to_call = Call()
        self.via_calls: [Call] = []
        self.is_digipeated = True   # Is running through all Digi's ?
        self.digi_call = ''         # Own DIGI Call to set C-BIT
        self.ctl_byte = CByte()
        self.pid_byte = PIDByte()
        self.data = b''             # Payload
        # self.aprs_data = {}
        self.data_len = 0
        self.addr_uid = ''          # Unique ID/Address String
        self.axip_add = '', 0       # For AXIP Handling

    def build_uid(self, dec=True):
        self.addr_uid = '{}:{}'.format(
            self.from_call.call_str,
            self.to_call.call_str
        )
        for ca in self.via_calls:
            self.addr_uid += f':{ca.call_str}'
        if not dec:
            self.addr_uid = reverse_uid(self.addr_uid)

    def set_stop_bit(self):
        if not self.via_calls:
            self.to_call.s_bit = False
            self.from_call.s_bit = True
        else:
            self.to_call.s_bit = False
            self.from_call.s_bit = False
            for el in self.via_calls:
                el.s_bit = False
            self.via_calls[-1].s_bit = True

    def set_check_h_bits(self, dec=True):
        """
        Dec: Check if Packet runs through all Digi's
        Enc: Set all ViaCalls C-Bits to 0
        """
        if dec:
            for ca in self.via_calls:
                if not ca.c_bit:
                    self.is_digipeated = False
                    break
        else:
            for ca in self.via_calls:
                ca.c_bit = False

    def digi_set_h_bits(self):
        if self.digi_call:
            tr = True
            for ca in self.via_calls:
                ca.c_bit = bool(tr)
                if ca.call_str == self.digi_call:
                    tr = False

    def decode_ax25frame(self, hexstr=b''):
        if hexstr:
            self.data_bytes = hexstr
        if self.data_bytes and len(self.data_bytes) > 14:

            try:
                self.to_call.dec_call(self.data_bytes[:7])
                # print("ToCall > {}".format(self.hexstr[:7]))
            except IndexError:
                print("Index ERROR To Call!!!!!!!!!!")
                raise AX25DecodingERROR(self)
            try:
                self.from_call.dec_call(self.data_bytes[7:14])
                # print("FromCall > {}".format(self.hexstr[7:14]))
            except IndexError:
                print("Index ERROR From Call!!!!!!!!!!")
                raise AX25DecodingERROR(self)
            n = 2
            if not self.from_call.s_bit:
                while True:
                    tmp = Call()
                    try:
                        tmp.dec_call(self.data_bytes[7 * n: 7 + 7 * n])
                        # print("Via Call N:{} > {}".format(n, self.hexstr[7 * n: 14 * n]))
                    except IndexError:
                        print("Index ERROR Via Call!!!!!!!!!!")
                        raise AX25DecodingERROR(self)
                    self.via_calls.append(tmp)
                    n += 1
                    if tmp.s_bit:
                        break

            index = 7 * n
            # Dec C-Byte
            try:
                self.ctl_byte.dec_cbyte(self.data_bytes[index])
            except (AX25DecodingERROR, IndexError) as e:
                logger.error('Decoding Error !! {}'.format(e))
                logger.error('Decoding Error !! MSG: {}'.format(self.data_bytes))
                logger.error('Decoding Error !! FM_CALL: {}'.format(self.from_call.call_str))
                logger.error('Decoding Error !! TO_CALL: {}'.format(self.to_call.call_str))
                raise AX25DecodingERROR(self)

            # Get Command Bits
            if self.to_call.c_bit and not self.from_call.c_bit:
                self.ctl_byte.cmd = True
            elif not self.to_call.c_bit and self.from_call.c_bit:
                self.ctl_byte.cmd = False
            # Get PID if available
            if self.ctl_byte.pid:
                index += 1
                try:
                    self.pid_byte.decode(self.data_bytes[index])
                except IndexError:
                    raise AX25DecodingERROR(self)
            if self.ctl_byte.info:
                index += 1
                if self.ctl_byte.flag == 'FRMR':
                    self.data = decode_FRMR(self.data_bytes[index:])
                else:
                    self.data = self.data_bytes[index:]
                self.data_len = len(self.data)
            # Check if all Digi s have repeated packet
            self.set_check_h_bits(dec=True)
            # Build address UID
            self.build_uid(dec=True)
            if not self.validate():
                raise AX25DecodingERROR(self)
            # self.decode_aprs()
        else:
            raise AX25DecodingERROR(self)

    def encode_ax25frame(self, digi=False):
        # print(f'encode >>>>>> {self.digi_call}')

        self.data_bytes = b''
        # Set Command/Report Bits
        if self.ctl_byte.cmd:
            self.to_call.c_bit = True
            self.from_call.c_bit = False
        else:
            self.to_call.c_bit = False
            self.from_call.c_bit = True
        # Set Stop Bit
        self.set_stop_bit()
        # Encode Address Fields
        try:
            self.to_call.enc_call()
        except AX25EncodingERROR:
            raise AX25EncodingERROR()
        try:
            self.from_call.enc_call()
        except AX25EncodingERROR:
            raise AX25EncodingERROR()

        self.data_bytes += self.to_call.hex_str
        self.data_bytes += self.from_call.hex_str
        # Via Stations
        # Set all H-Bits to 0
        if not digi:
            # TODO Crap
            self.set_check_h_bits(dec=False)
        for station in self.via_calls:
            try:
                station.enc_call()
            except AX25EncodingERROR:
                raise AX25EncodingERROR()
            self.data_bytes += station.hex_str
        self.digi_set_h_bits()
        # C Byte
        self.ctl_byte.enc_cbyte()
        self.data_bytes += format_hexstr(self.ctl_byte.hex).encode()
        # PID
        if self.ctl_byte.pid:
            self.data_bytes += format_hexstr(self.pid_byte.hex).encode()

        try:
            # !!!!!!! Käfer !!!! ????
            self.data_bytes = bytes.fromhex(self.data_bytes.decode())
        except ValueError:
            logger.error("Encoding bytes.fromhex VALUE ERROR !!!!")
            logger.error("V: {}".format(self.data_bytes))
            logger.error("from_call")
            for k in vars(self.from_call).keys():
                logger.error("{} > {}".format(k, vars(self.from_call)[k]))
            logger.error("")
            logger.error("to_call")
            for k in vars(self.to_call).keys():
                logger.error("{} > {}".format(k, vars(self.to_call)[k]))
            logger.error("")
            logger.error("pid_byte")
            for k in vars(self.pid_byte).keys():
                logger.error("{} > {}".format(k, vars(self.pid_byte)[k]))
            logger.error("")
            logger.error("ctl_byte")
            for k in vars(self.ctl_byte).keys():
                logger.error("{} > {}".format(k, vars(self.ctl_byte)[k]))
            raise AX25EncodingERROR(self)

        # Data
        if self.ctl_byte.info:
            self.data_len = len(self.data)
            self.data_bytes += self.data
        if not self.validate():
            logger.error('Encoding Error Validator')
            print('Encoding Error Validator')
            raise AX25EncodingERROR
        # Build address UID
        self.build_uid(dec=False)
        # Replace Kiss Flags with Kiss ESC ( C0 > DB DC )
        # self.hexstr = arschloch_kiss_frame(self.hexstr)

    def validate(self):
        """
        :return: bool
        """
        if 256 < len(self.data_bytes) < 15:
            print(f'Validate Error: Pac length {len(self.data_bytes)}')
            logger.error(f'Validate Error: Pac length {len(self.data_bytes)}')
            AX25EncodingERROR(self)
            return False
        if not self.from_call.validate():
            print('Validate Error: From Call')
            logger.error('Validate Error: From Call')
            AX25EncodingERROR(self)
            return False
        if not self.to_call.validate():
            print('Validate Error: TO Call')
            logger.error('Validate Error: TO Call')
            AX25EncodingERROR(self)
            return False
        for ca in self.via_calls:
            if not ca.validate():
                print('Validate Error: ca.validate')
                AX25EncodingERROR(self)
                return False
        if not self.ctl_byte.validate():
            print('Validate Error: C_Byte')
            logger.error('Validate Error: C_Byte')
            AX25EncodingERROR(self)
            return False
        if self.ctl_byte.pid:
            if not self.pid_byte.validate():
                print('Validate Error: PID_Byte')
                logger.error('Validate Error: PID_Byte')
                AX25EncodingERROR(self)
                return False
        return True

    #############
    # DIGI Stuff
    def digi_check_and_encode(self, call: str, h_bit_enc=False):
        """
        Check if Call is in Via Calls and is digipeated from previous Stations
        :param h_bit_enc: bool: Set H-Bit of call and encode Packet for digipeating
        :param call: str: Call we're looking for
        :return: bool:
        """
        if h_bit_enc:
            self.set_check_h_bits(dec=False)
        for ca in self.via_calls:
            """ C-Bit = H-Bit in Digi Address Space """
            if (not ca.c_bit and not ca.call_str == call) and h_bit_enc:
                ca.c_bit = True
            if not ca.c_bit and ca.call_str == call:
                if h_bit_enc:
                    ca.c_bit = True
                    self.encode_ax25frame(digi=True)    # TODO !!! Double encoding ??
                return True
        return False

    def short_via_calls(self, call: str):
        ind = 0
        search_ind = 0
        for el in self.via_calls:
            if call in el.call_str:
                search_ind = int(ind)
                ind += 1
            else:
                ind += 1
        if search_ind:
            self.via_calls = self.via_calls[search_ind:]


def via_calls_fm_str(inp_str: str):
    ret = []
    inp_str = inp_str.replace('\r', '').replace('\n', '')
    tmp = inp_str.split(' ')

    for call in tmp:
        call = call.replace(' ', '')
        if call:
            call_obj = Call()
            call_obj.call_str = call.upper()
            try:
                call_obj.enc_call()
            except AX25EncodingERROR:
                return False
            else:
                ret.append(call_obj)
    return ret
