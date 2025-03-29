"""
Ported from
https://github.com/ARSFI/Winlink-Compression
by Grok 3-beta (AI by x.com)
"""
import array


class LZHUF_Comp:
    # Öffentliche Konstanten
    N = 2048  # Puffergröße
    F = 60  # Vorausschaupuffer
    THRESHOLD = 2
    NODE_NIL = N
    N_CHAR = (256 - THRESHOLD) + F
    T = (N_CHAR * 2) - 1
    R = T - 1
    MAX_FREQ = 0x8000
    TB_SIZE = N + F - 2

    # Öffentliche Tabellen für Positionscodierung/Dekodierung
    P_LEN = bytearray([0x03, 0x04, 0x04, 0x04, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05,
                       0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06,
                       0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07,
                       0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07,
                       0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08,
                       0x08, 0x08, 0x08, 0x08])

    P_CODE = bytearray([0x00, 0x20, 0x30, 0x40, 0x50, 0x58, 0x60, 0x68, 0x70, 0x78, 0x80, 0x88,
                        0x90, 0x94, 0x98, 0x9C, 0xA0, 0xA4, 0xA8, 0xAC, 0xB0, 0xB4, 0xB8, 0xBC,
                        0xC0, 0xC2, 0xC4, 0xC6, 0xC8, 0xCA, 0xCC, 0xCE, 0xD0, 0xD2, 0xD4, 0xD6,
                        0xD8, 0xDA, 0xDC, 0xDE, 0xE0, 0xE2, 0xE4, 0xE6, 0xE8, 0xEA, 0xEC, 0xEE,
                        0xF0, 0xF1, 0xF2, 0xF3, 0xF4, 0xF5, 0xF6, 0xF7, 0xF8, 0xF9, 0xFA, 0xFB,
                        0xFC, 0xFD, 0xFE, 0xFF])
    """
    D_CODE = array.array('i', [0x00] * 32 + [0x01] * 16 + [0x02] * 16 + [0x03] * 16 + [0x04] * 8 +
                         [0x05] * 8 + [0x06] * 8 + [0x07] * 8 + [0x08] * 8 + [0x09] * 8 +
                         [0x0A] * 8 + [0x0B] * 8 + [0x0C] * 4 + [0x0D] * 4 + [0x0E] * 4 +
                         [0x0F] * 4 + [0x10] * 4 + [0x11] * 4 + [0x12] * 4 + [0x13] * 4 +
                         [0x14] * 4 + [0x15] * 4 + [0x16] * 4 + [0x17] * 4 + [0x18] * 2 +
                         [0x19] * 2 + [0x1A] * 2 + [0x1B] * 2 + [0x1C] * 2 + [0x1D] * 2 +
                         [0x1E] * 2 + [0x1F] * 2 + [0x20] * 2 + [0x21] * 2 + [0x22] * 2 +
                         [0x23] * 2 + [0x24] * 2 + [0x25] * 2 + [0x26] * 2 + [0x27] * 2 +
                         [0x28] * 2 + [0x29] * 2 + [0x2A] * 2 + [0x2B] * 2 + [0x2C] * 2 +
                         [0x2D] * 2 + [0x2E] * 2 + [0x2F] * 2 + [0x30, 0x31, 0x32, 0x33,
                                                                 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3A, 0x3B, 0x3C,
                                                                 0x3D, 0x3E, 0x3F])
    """
    D_CODE = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                        0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01,
                        0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01,
                        0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02,
                        0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02,
                        0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03,
                        0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03,
                        0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04,
                        0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05,
                        0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06,
                        0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07,
                        0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08,
                        0x09, 0x09, 0x09, 0x09, 0x09, 0x09, 0x09, 0x09,
                        0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A,
                        0x0B, 0x0B, 0x0B, 0x0B, 0x0B, 0x0B, 0x0B, 0x0B,
                        0x0C, 0x0C, 0x0C, 0x0C, 0x0D, 0x0D, 0x0D, 0x0D,
                        0x0E, 0x0E, 0x0E, 0x0E, 0x0F, 0x0F, 0x0F, 0x0F,
                        0x10, 0x10, 0x10, 0x10, 0x11, 0x11, 0x11, 0x11,
                        0x12, 0x12, 0x12, 0x12, 0x13, 0x13, 0x13, 0x13,
                        0x14, 0x14, 0x14, 0x14, 0x15, 0x15, 0x15, 0x15,
                        0x16, 0x16, 0x16, 0x16, 0x17, 0x17, 0x17, 0x17,
                        0x18, 0x18, 0x19, 0x19, 0x1A, 0x1A, 0x1B, 0x1B,
                        0x1C, 0x1C, 0x1D, 0x1D, 0x1E, 0x1E, 0x1F, 0x1F,
                        0x20, 0x20, 0x21, 0x21, 0x22, 0x22, 0x23, 0x23,
                        0x24, 0x24, 0x25, 0x25, 0x26, 0x26, 0x27, 0x27,
                        0x28, 0x28, 0x29, 0x29, 0x2A, 0x2A, 0x2B, 0x2B,
                        0x2C, 0x2C, 0x2D, 0x2D, 0x2E, 0x2E, 0x2F, 0x2F,
                        0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37,
                        0x38, 0x39, 0x3A, 0x3B, 0x3C, 0x3D, 0x3E, 0x3F,])

    """
    D_LEN = array.array('i', [0x03] * 32 + [0x04] * 48 + [0x05] * 48 + [0x06] * 48 + [0x07] * 48 +
                        [0x08] * 16)
    """
    D_LEN = bytearray([0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03,
                        0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03,
                        0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03,
                        0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03,
                        0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04,
                        0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04,
                        0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04,
                        0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04,
                        0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04,
                        0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04,
                        0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05,
                        0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05,
                        0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05,
                        0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05,
                        0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05,
                        0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05,
                        0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05,
                        0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05,
                        0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06,
                        0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06,
                        0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06,
                        0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06,
                        0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06,
                        0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06,
                        0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07,
                        0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07,
                        0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07,
                        0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07,
                        0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07,
                        0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07,
                        0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08,
                        0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08,])


    def __init__(self):
        # Private Variablen mit Unterstrich
        self._text_buf = bytearray(self.TB_SIZE + 2)
        self._l_son = array.array('i', [0] * (self.N + 2))
        self._r_son = array.array('i', [0] * (self.N + 257))
        self._dad = array.array('i', [0] * (self.N + 2))
        self._freq = array.array('i', [0] * (self.T + 1))
        self._son = array.array('i', [0] * self.T)
        self._parent = array.array('i', [0] * (self.T + self.N_CHAR))

        self._in_buf = None
        self._out_buf = None
        self._in_ptr = 0
        self._in_end = 0
        self._out_ptr = 0
        self._enc_dec = False  # True für Encode, False für Decode
        self._get_buf = 0
        self._get_len = 0
        self._put_buf = 0
        self._put_len = 0
        self._text_size = 0
        self._code_size = 0
        self._match_position = 0
        self._match_length = 0

    def init(self):
        """Initialisiert alle Strukturen und Zähler."""
        self._in_ptr = 0
        self._in_end = 0
        self._out_ptr = 0
        self._get_buf = 0
        self._get_len = 0
        self._put_buf = 0
        self._put_len = 0
        self._text_size = 0
        self._code_size = 0
        self._match_position = 0
        self._match_length = 0
        self._in_buf = None
        self._out_buf = None
        self._text_buf[:] = bytearray(self.TB_SIZE + 2)
        self._l_son[:] = array.array('i', [0] * (self.N + 2))
        self._r_son[:] = array.array('i', [0] * (self.N + 257))
        self._dad[:] = array.array('i', [0] * (self.N + 2))
        self._freq[:] = array.array('i', [0] * (self.T + 1))
        self._son[:] = array.array('i', [0] * self.T)
        self._parent[:] = array.array('i', [0] * (self.T + self.N_CHAR))

    def getc(self):
        """Liest ein Zeichen aus dem Eingabepuffer."""
        if self._in_ptr < self._in_end:
            c = self._in_buf[self._in_ptr] & 0xFF
            self._in_ptr += 1
            return c
        return 0

    def putc(self, c):
        """Schreibt ein Zeichen in den Ausgabepuffer."""
        self._out_buf[self._out_ptr] = c & 0xFF
        self._out_ptr += 1

    def encode(self, i_buf):
        """Kodierung/Komprimierung."""
        self.init()
        self._enc_dec = True
        self._in_buf = bytearray(i_buf + b'\x00' * 100)
        self._out_buf = bytearray(len(i_buf) * 2 + 10000)
        self._in_end = len(i_buf)

        # Schreibe Größe
        self.putc(self._in_end & 0xFF)
        self.putc((self._in_end >> 8) & 0xFF)
        self.putc((self._in_end >> 16) & 0xFF)
        self.putc((self._in_end >> 24) & 0xFF)
        self._code_size += 4

        if self._in_end == 0:
            return bytearray()

        self._text_size = 0
        self.start_huff()
        self.init_tree()
        s = 0
        r = self.N - self.F
        for i in range(r):
            self._text_buf[i] = 0x20  # Leerzeichen

        len_ = 0
        while len_ < self.F and self._in_ptr < self._in_end:
            self._text_buf[r + len_] = self.getc() & 0xFF
            len_ += 1
        self._text_size = len_

        for i in range(1, self.F + 1):
            self.insert_node(r - i)
        self.insert_node(r)

        while len_ > 0:
            if self._match_length > len_:
                self._match_length = len_
            if self._match_length <= self.THRESHOLD:
                self._match_length = 1
                self.encode_char(self._text_buf[r])
            else:
                self.encode_char((255 - self.THRESHOLD) + self._match_length)
                self.encode_position(self._match_position)

            last_match_length = self._match_length
            i = 0
            while i < last_match_length and self._in_ptr < self._in_end:
                i += 1
                self.delete_node(s)
                c = self.getc()
                self._text_buf[s] = c & 0xFF
                if s < self.F - 1:
                    self._text_buf[s + self.N] = c
                s = (s + 1) & (self.N - 1)
                r = (r + 1) & (self.N - 1)
                self.insert_node(r)
            self._text_size += i

            while i < last_match_length:
                i += 1
                self.delete_node(s)
                s = (s + 1) & (self.N - 1)
                r = (r + 1) & (self.N - 1)
                len_ -= 1
                if len_ > 0:
                    self.insert_node(r)

        self.encode_end()
        return self._out_buf[:self._code_size]

    def decode(self, i_buf):
        """Dekodierung/Dekomprimierung."""
        self.init()
        self._enc_dec = False
        self._in_buf = bytearray(i_buf + b'\x00' * 100)
        # self._out_buf = bytearray((expected_size or 0) + 10000)
        self._in_end = len(i_buf)

        # Größe lesen
        self._text_size = self.getc()
        self._text_size |= self.getc() << 8
        self._text_size |= self.getc() << 16
        self._text_size |= self.getc() << 24

        if self._text_size == 0:
            return bytearray()

        # Wenn expected_size nicht gegeben, nutze self._text_size für Ausgabegröße
        # if expected_size is None:
        self._out_buf = bytearray(self._text_size + 10000)
        # print(self._text_size)
        self.start_huff()
        for i in range(self.N - self.F):
            self._text_buf[i] = 0x20

        r = self.N - self.F
        count = 0
        while count < self._text_size:
            c = self.decode_char()
            if c < 256:
                self.putc(c & 0xFF)
                self._text_buf[r] = c & 0xFF
                r = (r + 1) & (self.N - 1)
                count += 1
            else:
                try:
                    i = ((r - self.decode_position()) - 1) & (self.N - 1)
                except ValueError:
                    print(f"Out-Buf: {self._out_buf[:count]}")
                    print(f"Out-Buf len:{len(self._out_buf[:count])}")
                    raise ValueError()
                j = (c - 255) + self.THRESHOLD
                for k in range(j):
                    c = self._text_buf[(i + k) & (self.N - 1)]
                    self.putc(c & 0xFF)
                    self._text_buf[r] = c & 0xFF
                    r = (r + 1) & (self.N - 1)
                    count += 1

        return self._out_buf[:count]

    def init_tree(self):
        """Initialisiert den Baum."""
        for i in range(self.N + 1, self.N + 257):
            self._r_son[i] = self.NODE_NIL
        for i in range(self.N):
            self._dad[i] = self.NODE_NIL

    def insert_node(self, r):
        """Fügt einen Knoten in den Baum ein."""
        geq = True
        p = self.N + 1 + self._text_buf[r]
        self._r_son[r] = self._l_son[r] = self.NODE_NIL
        self._match_length = 0

        while True:
            if geq:
                if self._r_son[p] == self.NODE_NIL:
                    self._r_son[p] = r
                    self._dad[r] = p
                    return
                p = self._r_son[p]
            else:
                if self._l_son[p] == self.NODE_NIL:
                    self._l_son[p] = r
                    self._dad[r] = p
                    return
                p = self._l_son[p]

            i = 1
            while i < self.F and self._text_buf[r + i] == self._text_buf[p + i]:
                i += 1
            geq = (self._text_buf[r + i] >= self._text_buf[p + i]) or (i == self.F)

            if i > self.THRESHOLD:
                if i > self._match_length:
                    self._match_position = ((r - p) & (self.N - 1)) - 1
                    self._match_length = i
                    if self._match_length >= self.F:
                        break
                if i == self._match_length:
                    c = ((r - p) & (self.N - 1)) - 1
                    if c < self._match_position:
                        self._match_position = c

        self._dad[r] = self._dad[p]
        self._l_son[r] = self._l_son[p]
        self._r_son[r] = self._r_son[p]
        self._dad[self._l_son[p]] = r
        self._dad[self._r_son[p]] = r
        if self._r_son[self._dad[p]] == p:
            self._r_son[self._dad[p]] = r
        else:
            self._l_son[self._dad[p]] = r
        self._dad[p] = self.NODE_NIL

    def delete_node(self, p):
        """Löscht einen Knoten aus dem Baum."""
        if self._dad[p] == self.NODE_NIL:
            return

        if self._r_son[p] == self.NODE_NIL:
            q = self._l_son[p]
        elif self._l_son[p] == self.NODE_NIL:
            q = self._r_son[p]
        else:
            q = self._l_son[p]
            while self._r_son[q] != self.NODE_NIL:
                q = self._r_son[q]
            self._r_son[self._dad[q]] = self._l_son[q]
            self._dad[self._l_son[q]] = self._dad[q]
            self._l_son[q] = self._l_son[p]
            self._dad[self._l_son[p]] = q
            self._r_son[q] = self._r_son[p]
            self._dad[self._r_son[p]] = q

        self._dad[q] = self._dad[p]
        if self._r_son[self._dad[p]] == p:
            self._r_son[self._dad[p]] = q
        else:
            self._l_son[self._dad[p]] = q
        self._dad[p] = self.NODE_NIL

    def get_bit(self):
        """Liest ein Bit."""
        while self._get_len <= 8:
            self._get_buf = (self._get_buf | (self.getc() << (8 - self._get_len))) & 0xFFFF
            self._get_len += 8
        ret_val = (self._get_buf >> 15) & 0x1
        self._get_buf = (self._get_buf << 1) & 0xFFFF
        self._get_len -= 1
        return ret_val

    def get_byte(self):
        """Liest ein Byte."""
        while self._get_len <= 8:
            self._get_buf = (self._get_buf | (self.getc() << (8 - self._get_len))) & 0xFFFF
            self._get_len += 8
        ret_val = (self._get_buf >> 8) & 0xFF
        self._get_buf = (self._get_buf << 8) & 0xFFFF
        self._get_len -= 8
        return ret_val

    def put_code(self, n, c):
        """Schreibt n Bits."""
        self._put_buf = (self._put_buf | (c >> self._put_len)) & 0xFFFF
        self._put_len += n
        if self._put_len >= 8:
            self.putc((self._put_buf >> 8) & 0xFF)
            self._put_len -= 8
            if self._put_len >= 8:
                self.putc(self._put_buf & 0xFF)
                self._code_size += 2
                self._put_len -= 8
                self._put_buf = (c << (n - self._put_len)) & 0xFFFF
            else:
                self._put_buf = ((self._put_buf & 0xFF) << 8) & 0xFFFF
                self._code_size += 1

    def start_huff(self):
        """Initialisiert den Huffman-Baum."""
        for i in range(self.N_CHAR):
            self._freq[i] = 1
            self._son[i] = i + self.T
            self._parent[i + self.T] = i
        i, j = 0, self.N_CHAR
        while j <= self.R:
            self._freq[j] = (self._freq[i] + self._freq[i + 1]) & 0xFFFF
            self._son[j] = i
            self._parent[i] = self._parent[i + 1] = j
            i += 2
            j += 1
        self._freq[self.T] = 0xFFFF
        self._parent[self.R] = 0

    def reconst(self):
        """Rekonstruiert den Huffman-Baum."""
        j = 0
        for i in range(self.T):
            if self._son[i] >= self.T:
                self._freq[j] = (self._freq[i] + 1) >> 1
                self._son[j] = self._son[i]
                j += 1

        i, j = 0, self.N_CHAR
        while j < self.T:
            k = i + 1
            f = (self._freq[i] + self._freq[k]) & 0xFFFF
            self._freq[j] = f
            k = j - 1
            while f < self._freq[k]:
                k -= 1
            k += 1
            for n in range(j, k, -1):
                self._freq[n] = self._freq[n - 1]
                self._son[n] = self._son[n - 1]
            self._freq[k] = f
            self._son[k] = i
            i += 2
            j += 1

        for i in range(self.T):
            k = self._son[i]
            self._parent[k] = i
            if k < self.T:
                self._parent[k + 1] = i

    def update(self, c):
        """Aktualisiert den Huffman-Baum."""
        if self._freq[self.R] == self.MAX_FREQ:
            self.reconst()
        c = self._parent[c + self.T]
        while c != 0:
            self._freq[c] += 1
            k = self._freq[c]
            n = c + 1
            if k > self._freq[n]:
                while n + 1 < len(self._freq) and k > self._freq[n + 1]:
                    n += 1
                self._freq[c] = self._freq[n]
                self._freq[n] = k
                i = self._son[c]
                self._parent[i] = n
                if i < self.T:
                    self._parent[i + 1] = n
                j = self._son[n]
                self._son[n] = i
                self._parent[j] = c
                if j < self.T:
                    self._parent[j + 1] = c
                self._son[c] = j
                c = n
            c = self._parent[c]

    def encode_char(self, c):
        """Kodierung eines Zeichens."""
        code, len_ = 0, 0
        k = self._parent[c + self.T]
        while k != self.R:
            code = code >> 1
            if k & 1:
                code |= 0x8000
            len_ += 1
            k = self._parent[k]
        self.put_code(len_, code)
        self.update(c)

    def encode_position(self, c):
        """Kodierung einer Position."""
        i = c >> 6
        self.put_code(self.P_LEN[i], self.P_CODE[i] << 8)
        self.put_code(6, (c & 0x3F) << 10)

    def encode_end(self):
        """Beendet die Kodierung."""
        if self._put_len > 0:
            self.putc(self._put_buf >> 8)
            self._code_size += 1

    def decode_char(self):
        """Dekodiert ein Zeichen."""
        c = self._son[self.R]
        while c < self.T:
            c = self._son[c + self.get_bit()]
        c -= self.T
        self.update(c)
        return c & 0xFFFF

    def decode_position(self):
        """Dekodiert eine Position."""
        i = self.get_byte()
        if i >= len(self.D_LEN):
            raise ValueError(f"Invalid position index {i}, max {len(self.D_LEN) - 1}")
        c = (self.D_CODE[i] << 6) & 0xFFFF
        j = self.D_LEN[i] - 2
        while j > 0:
            i = ((i << 1) | self.get_bit()) & 0xFFFF
            j -= 1
        return c | (i & 0x3F)


# Beispielverwendung
if __name__ == "__main__":
    comp = LZHUF_Comp()
    data = b"Hello, World!"
    # data2 = bytearray.fromhex("9f000000ef71b7dc1de6ff0f0b77bdbebb77cdace662767a17b9d69dfdd6becf9be3b2a9613e95af47c356a27ee2c6a827a5c5e1ccf3d7f6fe0180fe3f09a9df4d0d859c27b996196672d2903d2ff7eff309aa620998f6dffc44bf7de090760b1093b7e4c48ec01e7fdf21c4812241")
    compressed   = comp.encode(data)
    decompressed = comp.decode(compressed)
    print(f"Compressed:   {compressed}")
    print(f"Compressed:   {compressed.hex()}")
    print(f"Decompressed: {decompressed.decode('utf-8')}")
    print(f"Len Compressed:   {len(compressed)}")
    print(f"Len Decompressed: {len(decompressed)}")