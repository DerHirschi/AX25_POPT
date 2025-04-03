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
    #TB_SIZE = N + F - 2
    TB_SIZE = N + F - 1

    # Öffentliche Tabellen für Positionscodierung/Dekodierung
    P_LEN = bytearray([0x03, 0x04, 0x04, 0x04, 0x05, 0x05, 0x05, 0x05,
                        0x05, 0x05, 0x05, 0x05, 0x06, 0x06, 0x06, 0x06,
                        0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06,
                        0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07,
                        0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07,
                        0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07,
                        0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08,
                        0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08])

    P_CODE = bytearray([0x00, 0x20, 0x30, 0x40, 0x50, 0x58, 0x60, 0x68, 0x70, 0x78, 0x80, 0x88,
                        0x90, 0x94, 0x98, 0x9C, 0xA0, 0xA4, 0xA8, 0xAC, 0xB0, 0xB4, 0xB8, 0xBC,
                        0xC0, 0xC2, 0xC4, 0xC6, 0xC8, 0xCA, 0xCC, 0xCE, 0xD0, 0xD2, 0xD4, 0xD6,
                        0xD8, 0xDA, 0xDC, 0xDE, 0xE0, 0xE2, 0xE4, 0xE6, 0xE8, 0xEA, 0xEC, 0xEE,
                        0xF0, 0xF1, 0xF2, 0xF3, 0xF4, 0xF5, 0xF6, 0xF7, 0xF8, 0xF9, 0xFA, 0xFB,
                        0xFC, 0xFD, 0xFE, 0xFF])

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
        self.init()
        self._enc_dec = True
        self._in_buf = bytearray(i_buf + b'\x00' * 100)
        self._out_buf = bytearray(len(i_buf) * 2 + 10000)
        self._in_end = len(i_buf)

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
            self._text_buf[i] = 0x20

        len_ = 0
        while len_ < self.F and self._in_ptr < self._in_end:
            self._text_buf[r + len_] = self.getc() & 0xFF
            len_ += 1
        self._text_size = len_

        for i in range(1, self.F + 1):
            self.insert_node(r - i)
        self.insert_node(r)

        iteration_count = 0
        max_iterations = 1000000
        while len_ > 0:
            iteration_count += 1
            if iteration_count > max_iterations:
                #print(f"Breaking encode loop due to max iterations: len_={len_}, r={r}")
                break
            #print(
            #    f"encode: r={r}, len_={len_}, match_length={self._match_length}, text_buf[r:r+F]={self._text_buf[r:r + self.F]}")
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
        geq = True
        p = self.N + 1 + self._text_buf[r]
        self._r_son[r] = self._l_son[r] = self.NODE_NIL
        self._match_length = 0

        iteration_count = 0
        max_iterations = 1000
        while True:
            iteration_count += 1
            if iteration_count > max_iterations:
                #print(f"Breaking due to max iterations: r={r}, p={p}")
                break
            if p == r:
                #print("Breaking due to p == r")
                break
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
            while (i < self.F and
                   r + i < len(self._text_buf) and
                   p + i < len(self._text_buf) and
                   self._text_buf[r + i] == self._text_buf[p + i]):
                i += 1
            #print(f"Comparison ended at i={i}")

            # Nur aktualisieren, wenn Übereinstimmung größer als THRESHOLD
            if i > self.THRESHOLD:
                if i > self._match_length:
                    self._match_position = ((r - p) & (self.N - 1)) - 1
                    self._match_length = i
                    if self._match_length >= self.F:
                        return  # Frühzeitige Rückkehr bei voller Übereinstimmung
                if i == self._match_length:
                    c = ((r - p) & (self.N - 1)) - 1
                    if c < self._match_position:
                        self._match_position = c

            # Nächste Richtung bestimmen
            if i >= self.F:
                geq = True
            elif r + i >= len(self._text_buf) or p + i >= len(self._text_buf):
                geq = True  # Wenn Puffergrenze erreicht, als "größer" behandeln
            else:
                geq = self._text_buf[r + i] >= self._text_buf[p + i]

            # Baumaktualisierung nur bei komplexer Operation
            if self._dad[p] != self.NODE_NIL:  # Sicherstellen, dass p nicht bereits freigegeben ist
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
                return  # Nach Aktualisierung zurückkehren

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
    data = b'\rThe fox from \'The Fox and The Hound\' by Shanaka Dias\r\r   .       .\'.\r  : \'.--\'-/ ::\r  :;\'_\';\'`_\'\':\r  ://o)._(o\\ \'.\r ;\'  (O_.\'\'.   ;\r  \'._;|_/_: _.\'\r     .\'-\'.\'\\\r    ,\'   ;  `\'._\rsnd \';.   ;/    \'-.    ____\r    :\';   :        :-\'`  : \'.\r    :,,/:. \\  ,.\'   :     :  \'.\r   _; /;,:\'|,,(   _.\'-.__:_..\'\r  :,,:    _: /\'--;\r         :,,:-\'-\'\r\rDumbo the elephant by Shanaka Dias\r\r                   _\r                  ( \\\r       __         _)_\\_\r      \' \\;---.-._S_____2_\r        /   / /_/       (______\r     __(  _;-\'    =    =|____._\'.__\r    /   _/     _  @\\ _(@(      \'--.\\\r    (_ /      /\\  _   =( ) ___     \\\\\r      /      /\\ \\_ \'.___\'-.___~.    \'\\\rsnd  /      /\\ \\__\'--\') \'-.__c` \\    |\r    |     .\'  )___\'--\'/  /`)     \\   /\r    |    |\'-|    _|--\'\\_(_/       \'.\'\r    |    |   \\_  -\\\r     \\   |     \\ /`)\r      \'._/      (_/\r\rArnie in Terminator II and Terminator\r\r                     ______\r                   <((((((\\\\\\\r                   /      . }\\\r                   ;--..--._|}\r(\\                 \'--/\\--\'  )\r \\\\                | \'-\'  :\'|\r  \\\\               . -==- .-|\r   \\\\               \\.__.\'   \\--._\r   [\\\\          __.--|       //  _/\'--.\r   \\ \\\\       .\'-._ (\'-----\'/ __/      \\\r    \\ \\\\     /   __>|      | \'--.       |\r     \\ \\\\   |   \\   |     /    /       /\r      \\ \'\\ /     \\  |     |  _/       /\r       \\  \\       \\ |     | /        /\r snd    \\  \\      \\        /\r\r2001: A Space Odyssey\r\r                                             _.--"""""--._\r                                          ,-\'             `-.\r               _                        ,\' --- -  ----   --- `.\r             ,\'|`.                    ,\'       ________________`.\r            O`.+,\'O                  /        /____(_______)___\\ \\\r   _......_   ,=.         __________;   _____  ____ _____  _____  :\r ,\'   ,--.-`,,;,:,;;;;;;;///////////|   -----  ---- -----  -----  |\r( SSt(  ==)=========================|      ,---.    ,---.    ,.   |\r `._  `--\'-,``````"""""""\\\\\\\\\\\\\\\\\\\\\\:     /`. ,\'\\  /_    \\  /\\/\\  ;\r    ``````                           \\    :  Y  :  :-\'-. :  : ): /\r                                      `.  \\  |  /  \\=====/  \\/\\/\'\r                                        `. `-\'-\'    `---\'    ;\'\r                                          `-._           _,-\'\r                                              `--.....--\'   ,--.\r                                                           ().0()\r                                                            `\'-\'\r\rMary Poppins\r\r           _\r        .-\' \'-.\r       /       \\\r      |,-,-,-,-,|\r     ___   |\r    _)_(_  |\r    (/ \\)  |\r    _\\_/_  /)\r   / \\_/ \\//\r   |(   )\\/\r   ||)_( \r   |/   \\\r   n|   |\r  / \\   |\r  |_|___|\r     \\|/\rjgs _/L\\_\r\rIgor - Frankenstein Junior by Morfina\r\r        .WWWW.\r       WWWW""\'\r     .WWWW O O\r  .WWWW"WW.\'-. \r WWWWWWWWWWWWW.\rWWWWWWWWWWWWWWW\r"WWWWWWWWWW"\'\\___\r /  /__ __/\\___( \\\r(____( \\X( mrf /||\\  \r   / /||\\ \\\r   \\______/\r    \\ | \\ |  \r     )|  \\|\r    (_|  /|\r    |X| (X|  \r    |X| |X\'._  \r   (__| (____)\r\rBaloo and Mowgli from \'The Jungle Book\' by Shanaka Dias\r\r                                .-c.\r                    _ ..,   _  (  ")\\\r                   [\'" 6\'-\'        __\\  /   \\  /_\r           snd   `----\'     \'-._\\\r\rNemo by Horroroso\r\r                                    ,-----.\r                                   ,\'       `-.\r                                  /            `.\r                                 /         _.----_o.\r                                __   ,---\'\'    ,8888b.\r                               d88;-\'         d888j"\' `---.\r                         ,----,Y8888.        ,888\'         `-.\r                       ,\'     / d8888.       888             ,\\\r   ,----.             ;      /  d88888bo.   J888       ,,.  (\'@\\\r ,\'      `---.        :    ,\'   :88888888[  d88;     ,\' `8)  \\  :\r;             `-----oooi.-\'      `8888888;  d88     (      )  `-:\r|                  d8888.     ,--_888od8P  ,88P      `----\'      :\r|                  88888.  ,-\'     `Y8P\'   d88;                  |\r:                  88M888 (           \\    d8b          _____,.--P\r \\                 888888. :               `88.         \'.__    /\r  \\                888888L :            |   Y88b_           `;\'\'\r   \\               `Y88J8P;-\\           ;    `Y888L        ,\'\r    \\        _.---\'  `"";\'   `-.       //\\_    `""\'`-_.---\'\r     `-----\'\'            \\      `.----\'/   \\__,----\'\'\r                          `-----\'      \\_    /           -hrr-\r                                         `--\'\r\rJudge Dredd\r\r                      ______\r                   ,-~   _  ^^~-.,\r                 ,^        -,____ ^,         ,/\\/\\/\\,\r                /           (____)  |      S~        ~7\r               ;  .---._    | | || _|     S  I AM THE  Z\r               | |      ~-.,\\ | |!/ |     /_   LAW!   _\\\r               ( |    ~<-.,_^\\|_7^ ,|     _//_      _\\\r               | |      ", 77>   (T/|   _/\'   \\/\\/\\/\r               |  \\_      )/<,/^\\)i(|\r               (    ^~-,  |________||\r               ^!,_    / /, ,\'^~^\',!!_,..---.\r                \\_ "-./ /   (-~^~-))\' =,__,..>-,\r                  ^-,__/#w,_  \'^\' /~-,_/^\\      )\r               /\\  ( <_    ^~~--T^ ~=, \\  \\_,-=~^\\\r  .-==,    _,=^_,.-"_  ^~*.(_  /_)    \\ \\,=\\      )\r /-~;  \\,-~ .-~  _,/ \\    ___[8]_      \\ T_),--~^^)\r   _/   \\,,..==~^_,.=,\\   _.-~O   ~     \\_\\_\\_,.-=}\r ,{       _,.-<~^\\  \\ \\\\      ()  .=~^^~=. \\_\\_,./\r,{ ^T^ _ /  \\  \\  \\  \\ \\)    [|   \\oDREDD >\r  ^T~ ^ { \\  \\ _\\.-|=-T~\\\\    () ()\\<||>,\' )\r   +     \\ |=~T  !       Y    [|()  \\ ,\'  / -naughty\r\r    /\\  ____\r    <> ( oo )\r    <>_| ^^ |_\r    <>   @    \\\r   /~~\\ . . _ |\r  /~~~~\\    | |\r /~~~~~~\\/ _| |\r |[][][]/ / [m]\r |[][][[m]\r |[][][]|\r |[][][]|\r |[][][]|\r |[][][]|\r |[][][]|\r |[][][]|\r |[][][]|\r |[][][]|\r |[|--|]|\r |[|  |]|\r ========\r==========\r|[[    ]]|\r==========\r[By the Cyberfox.]\r\rNightmare before Christmas\r\r                                    .\'\r                                  .\':            ,\r                                 : :            ;;\r                                :  :          ,\' ;         \r                                :  :        _;. ;       _O\r                                 : `.     ,(  \\\\:____.-"_;\r                                  \'.;_,-"",        __,-:\r                                   `` \\_ :  ( -----(::|\\\\\r                                        "(____"-:   ):|:`\\\r                                  __..--""    "- ;  |:|:.`\\.\r                            __..-"       :.   .. )  |:):::.`\\.,""`\r                      __..-"               \'\'\' ) ;  /;/::::.` \\` "\r                __..-"                       )  ;  _(;::::::./` "`\r            _.""                               ;,""`||.:::-"``,"`\r.        _."                                 .) \',_(||`;__,"""` \r:\\     ."     _.."--..__                   . ;     ";;""\r: "-.."    _;"          ""-.._ ....       . ;      ||\r`._      ;\'                   ""-.._..  .. ;       ||\r   "-..-"                           ""-.._;        |\'\r                   THE                             |\r            N I G H T M A R E                     ,:. \r                 BEFORE                          /ctr\\\r            C H R I S T M A S                   \'/{{`\'`\r                - Zero -\r\rLost in Space by Joan Stark\r\r     ,.-""``""-.,\r    /  ,:,;;,;,  \\\r    \\  \';\';;\';\'  /\r     `\'---;;---\'`\r     <>_==""==_<>\r     _<<<<<>>>>>_\r   .\'____\\==/____\'.\r   |__   |__|   __|\r  /C  \\  |..|  /  D\\\r  \\_C_/  |;;|  \\_c_/\r   |____o|##|o____|\r    \\ ___|~~|___ /\r     \'>--------<\'\r     {==_==_==_=}\r     {= -=_=-_==}\r     {=_=-}{=-=_}\r     {=_==}{-=_=}\r     }~~~~""~~~~{\rjgs  }____::____{\r    /`    ||    `\\\r    |     ||     |\r    |     ||     |\r    |     ||     |\r    \'-----\'\'-----\'\r\rSoldier & Ballerina (Steadfast Tin Soldier)\r\r      |\r      |\r      |\r      |.    !\r      "| .-\'!\r       I |  P\r       I ;__|\r       I ||\'\'     scc,\r       I )\\=( _   } s&D\r      .I- ;_\\-=\\  L sc\r      |IT   \\\',_\\__7 &s\r      |I| //\\\'.---..)s&\r      |I|//_ \\\\   \\  (_\r      LI|-----|/   \\.\' \'-.______\r      {ID  :\' |}   /   \'..\'-- .;___.-,_\r       "|  Y  |  .:  \\  ,    /_,.--\'=--\'\r        |  |  /  | /  ;. \':.\'\r        |: |_/   |; :  ::_/\r        |\' /     |I |___/\r        |-|       \'\' | )\r        | |          | /\r        | |          |;\rsnd   __|_|_ __      |/>\r     ( _\'---\'__)     |(\r      \'~~~~~~~\'      "\r\rE.T.\r\r     .-"""-"""-"""--.--"""-"""-""""-.\r   -"  I   I   I  I    I   I  I    I  "-.\r  "   MMMMMMMMMMn)))).(((((nMMMMMMMMM    "\r "   M .-\'\'\'\'-. "MMM    MMM" .-\'\'\'-. M    "\rI   M\' .-\'\'\'\'\'-. -MM   MM- .\'.-\'\'\'\'-. M    I\rI  M  \'MMMMMMMMM .\'\'\'\'\'. \'MMMMMMMMM\'  M    I\rI  M  M  M$M  MM       :  MM  M$M  M  M    I\rI      M MMM  M   -"".""-   M MMM  M       I\rI       """"""   MMMMMMMMM   """"""   .    I\r I     \'-....-\' : MMMMMMM  :  \'-...-\'.\'   I\r  " .  \'-....-\'    -   -     \'-...-\'     "\r   , \'.        :                     .\'"\r    "  \'....\'                  \'.....\' "\r     "-\'...;\' :             :  \'....\'-"\r       "-     ".-----....--."      -"\r         "-                 .   -"\r           "-     \'-...- \'.\'   -"\r             "-.; \'-....-\'  .-"\r                 I"-......I"\r                 I        I\r                 I \'-- --\'I\r                 I        I\r                 I \'-- --\'I\r                 I        I\r                 I \'-- --\'I\r                 I        I         TAG\r                 I \'-- --\'I\r\rMonsters Inc. by John Stachowicz\r\r               /\\_.----._\r             ." _,=<\'"=. ",/|\r            /,-\'    "=.`.   (\r           //         \\ |    \\\r          /,    _.,.   |      \\    (|\r        ," |   ,\\\'v/\', |       \\  _)(\r       /   |   !>(")<|/         \\ c_ \\\r    _-/     \\  \'=,Z\\\\7           . C. \\\r_,-" V  /    \'-._,>*"     \\      |   \\ \\\r\\  <"|  )\\ __ __ ____ _    Y     |    \\ \\\r \\ \\ |   >._____________.< |     "-.   \\ \\\r  \\ \\|   \\ \\/\\/\\/\\/\\/\\/ /\' /    =_  \'-._) \\\r   \\ (    \\            /         |"*=,_   /\r    \\ \\    \\_/\\/\\/\\/\\_/         /      """\r    _).^     "******"          /\r   (()!|\\                     /\r    *==" ",                 ,"\r           ",_            ,"\r              \\"*<==> ,=*"\r               \\ \\ / /\r           _____>_V /\r          f  .-----"\r          |  \\    \\ \\\r          |   \\    \\ \'-.\r          J    \\    \\   \\\r         (  \\ \\ \\ _.-J   )\r          \\V)V)=*.\',\'  ,\'\r   jjs        (V(V)(V)/\r\rStargate\r\r                        ___.-----.___\r                     _.--_.--=-=--._--._\r                   __.---"         "---.__\r                  _.--:    ~          :--._\r                 _.-:              ~    :-._\r               _.-:         ~            :-._\r              _.-:  ~                ~    :-._\r             _.-:       ~   ~     ~        :-._\r            _.-:      ~        ~       ~    :-._\r            _.-:   ~                     ~  :-._ \r             _.-:       ~          ~       :-._ \r              _.-:            ~         ~ :-._  \r               _.-:  ~                   :-._ \r                _.-:        ~      ~    :-._  ===--._\r        _..-===  _-.-:                :-.-_          \'-..._\r      /      \\|/  _.-.-:____________:-.-._        o        "-.__\r   _.\'          .\'  _.-.-.========.-.-._  \'.     \\|/             \\_\r   \\           /\\ .\'    /          \\    \'. /\\                o     \'--._\rLGB \\         / //   _ /            \\ _   \\\\ \\              \\|/        /\r_.--\'o        \\_/_.-\' /______________\\ \'-._\\_/                      _.\'\r    \\|/              /                \\         _.---._            \\\r                    /                  \\ \\|/  .\'  .".  \'.           \\\r                   /____________________\\     \'._ \'.\' _.\'            \\\r                   \'====================\'        /   \\           _.--\'\r--._                                         _.-/     \\-._       \\\r    \\  _.---_                               |  \\_______/  |   _.-\'\r    / / \'    "._o                            \\||.-----.||/   \\\r ,-"  \\|/_."\'-.\\|/                                            \\\r/                                                             /\r\rShere Khan, Jungle book\r\r                           .e@$$$$$$$eeeu=~=._\r                        zd$$$$$$$$$$$$$$\'   z$b..  _,x,\r                     z????$$$$$$$$P",-==   dP""`$$$.  .;\r                  .e"..     `"?$Fu^\'e$$$$$be.   )$$\' 4r\'$$nn,     _. -\r                ud$$$P  zeeeu.   ld$$$$$$$$$$$$c`=._,$$  <"$$$$= \'\r              z$$$$$$e ?$$"   "FE=e2R$$$$$$$$$$$$bu"h._..d. "`nMb`    _\r           .-J$$$$$$$$,?$$b,.,J",xc3$$$$$$$$$$$$$$$" Mh. "  \'MMMMP- ~\r      ..ze$F R$$$$$$$$$bcccd$$"J(T-\r"b".nMMP\'b.   "",c$$$$$$$$P.MMMMMMMb.<       )!! >\'dMMMMMMM  __\r .HMMMM  "??$$$$$PF"uPF",, umnmnHMMMMMbx.... \'\'.n\'MMMMMCund~    `~ ~ -\r\'M\'HMMMh         .e$ee$$?7 MMMMMT"",MMMMMMMMMMMMM.MMMMMMMMM\r  MMMMMMMx -...e$$$P??,nMM "`,nndMMMMMMMMMMMMMMMMk`MMMMMMMP\r H"MMMMMMMMhx???",nHMMP",nh MMMMMM?MP"xHMMMMMMMMMF-?TMMMM"\r   MMPTMMMMMMMMMMP"u- :n.`"%\'MF.xnF.nMMMMMMMMMP".::::."Te\r  \'M".MPTMMMMMP"zeEeP.MMMMM"..4MF,HMMMMMMMMMF\'.::::::::`R.\r   " MF dMMMf z$$$$$ MMMF\'xMMMr`HMMMMMMMMM".:::::::.::...?_\r     T  M P  $$$$$$%dMF\'dMMMM"xk\'MPJMMMMP ::\'.\'\';i!!!!\'`^.xhMmx\r       \'M   4$$$$$P.P,HMMMMM,HMMh TMMMMM> :!!!!!!!\'`.xnMMMMMMMMMn\r            J$$$$$ ",MMMMMM,MMMM\'h TMMMML\'!;!!!`.nHMMMMMMMMMMMMMMMn\r            $$$$$P HMMMMMM,MMMM MMM."MMMM \\!i`.HMMMMMMMMMMMMMMMMMMMMr\r            $$$$$"dMMMMMMMMMMMfdMMMM.`MMMh   xMMMMMMMMMMMMMMMMMMMMMMM\r           4$$$$$ MMMMMMMMMMMMMMMMMMMx`MMMMMMMMMMMMMMMMMMMMMMMMMMMMMM\'\r          ,4$$$$$.MMMMMMMMMMMMMMMMMMMMh TMMMMMMMMMMMMMMMMMMMMMMMMMMMf\r         ; J$$$$F;MMMMMMMMMMMMMMMMMMMMMM."MMMMMMMMMMMMMMMMMMMMMMP""\r       .db $$$$$ MMMMMMMMMMMMMMMMMMMMMMMMh."MMMMMMMMMMMMMMPF"\r      , d$b$$$$$ MMMMMMMMMMMMMMMMMMMMMMMMMM u"?f""?=\r     .  $$$$$$$$ MMMMMMMMMMMMMMMMMMMMMMMMMfJ$b\r    z$  d$$$$$$$ MMMMMMMMMMMMMMMMMMMMMMMMM P" `\r   e$$h ?$$$$$$$ MMMMMMMMMMMMMMMMMMMMMMMMf^  zF`.\r\r                                       /\\\r                                      /  \\\r                                     / /\\ \\\r                                    / /  \\ \\\r                                   / /    \\ \\\r                                  / /      \\ \\\r                                 / /        \\ \\\r                                / /          \\ \\\r                               / /            \\ \\\r_ _____  _ _ _  ___ __________/ /              \\ \\_____________________________\r`|_   _|| |_| || __|___________/                \\________________________  ,-\'\r   | |`-|  _  || _|                                                  ,-\',-\'\r   |_|`-|_| |_||___|                                             _,-\',-\'\r  ____    `-.`-____        ____        ___      ___  ___  _____,-_,-\'________\r |    \\      `/    |    ,-\'    `-.    |   |    |   ||   ||        | /        |\r |     \\     /     |-.,\'  __  __  `.  |   |    |   ||   ||    ____||    _____|\r |      \\   /      |-/   /  \\/  \\   \\ |   |    |   ||   ||   |____ |   (____\r |       \\_/       ||    \\      /    ||   |    |   ||   ||        ||        \\\r |   |\\       /|   ||     |     ]    | \\   \\  /   / |   ||    ____| \\____    |\r |   | \\     / |   |/\\    |____|    /   \\   \\/   /  |   ||   |____  _____)   |\r |   |  \\   /  |   | / .  ,\' | `. ,\'   , \\      /   |   ||        ||         |\r |___|   \\_/   |___|/   `-.____,-\'  ,-\',`-\\____/    |___||________||________/\r                 / /             ,-\',-\' `-.`-.             \\ \\\r                / /           ,-\',-\'       `-.`-.           \\ \\\r               / /         ,-\',-\'             `-.`-.         \\ \\\r              / /       ,-\',-\'                   `-.`-.       \\ \\\r             / /     ,-\',-\'                         `-.`-.     \\ \\\r            / /   ,-\',-\'                               `-.`-.   \\ \\\r           / / ,-\',-\'                                     `-.`-. \\ \\\r          / /-\',-\'                                           `-.`-\\ \\\r         /_,-\'`                                                 `\'-._\\\r\rLady by Susie Oviatt\r\r                               ...,,,,,... \r                           ,%%%%%%%%%%%%%%%Ss, \r                          %%%%%%%%%%%%,,,%%%%SSs,. \r                      .,;;;;;;,%%%%%%,%%%%%,%%SSs%% \r                  ..;;;;;;;;;;;;;;,%%%%,,,,%%%SSS%\' \r                 .;;;;;;;;;;;;;;;;;;%%,a@;;;%%%SS\' \r               .,;;;;;;;;;;;;;;;;;;;%,a@;;  `%%SSS,. \r             ,;;;;;;;;;;;;;;;;;;;;;\'%,@@;;,,,%%%SSSSSSSS\'\'\'. \r            ;;;;;;;;;;;;;;;;;;;;;;;,%%@@@aaaa%%%SSSSSSS,   ; \r          ,;;;;;;;;;;;;;;;;;;;;;;;;;,%%@@@@@%%%SSSSSSSSSs,,\' \r         ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;%%%%%%%%SSSSSSSSSSSS\' \r        ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;%%%%%%%SSSSSSSSSSS\' \r       ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;\'%%%%%%%%SSSSSSSS\' \r      ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,%%%%%%\' \r      ;;;;,;;;;;;;;;;;;;;;;;;;;;;;;;;;;,%%%%% \r      ;;;,;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,%;%;%. \r      `;;,;;;;;;;;;;;;;;;;;;;;;;;,;;;;;;,sSSSSSSs%, \r        `,;;;;,;;;;;;;;;;;;;;;;;;;,;;;;\'sSSSSSSSSSSS. \r          ;;;,;;;;;;;;;;;;;,;;;;;,;;;;\'SSSSSSSSSSSSSSs \r           `;\';;;;;;;;;;;;;,;;;;,;;;\'sSSSSSSSSSSSSSsSSs. \r              `;;;;;;;;;;;,;;;;\'%%%%;SSSSSSSSSSSSSSSSsSs \r             .,%%;;;;;;;;\'%%%%%%%%%;sSSSSSSSSSSsSSSSSSsS \r          .,%%%%%`;;;\'%%%%%%%%%%%%%;SSSSSSSSSSSSSsSSSSs\' \r       .,%%%%%%%%%\'%%%%%%%%%%%%%%%;sSSSSSSSSSSSSSSsSSS\' \r   .,%%%%%%%%%%%%%%%%%%%%%%%%%%%%;sSSSSSSSSSSSSSSSsS\' \r ,%%%%%%%%%%%%%%%%%%%%;%%%%%%%%%%;SSSSSSSSSSSSSSSs\' \r%%%%%%%%%%%%%;%%%%%%%;%%%%%%%%%%;sSSSSSSSSSSSSSS\' \r%%%%%%%%%%%%%%%;%%%%;%%%%%%%%%%%;SSSSSSSSSSSS\'%% \r%%%%%%%%%%%%%%%%%;%;%%%%%%%%%%%;sSSSSSSSS\'%%%%%%% \r%%%%%%%%%%%%%%%%%%;%%%%%%%%%%%;sSSSS\'ssssSSSS%%%%% \r%%%%%%%%%%%%%%%%%%;%%%%%%%%%%%\'      `SSSSSSSSS%%%% \r%%%%%%%%%%%%%%%%%;%%%%%%%%%%%\'         `SSsSSSSSS%%% \r%%%%%%%%%%%%%%%%% %%%%%%%%%%\'            S\'`SSsSSSSSSs. \r%%%%%%%%%%%%%%%%\' \'%%%%%%%%\'                 S\'`SSssssSS. \r%%%%%%%%%%%%;sSSs   `SSSSSSs.                    `SSSS%SS \r%%%%%%%%%;sSSSSSS    `SSSSSSS\r\rShai-Hulud (sandworm, dune) by Jonathan R. Oglesbee\r\r                               .-.._    ___\r                            ,-\'   |:\\ /\'--.`.\r                           /\'    ,|:|/::::| \'\\\r                         ,\'  ,.-:::::::::::.  \\\r                       _/\' /::::::::::::::::`  \\\r                      /\'  \':::::::_,--.::::::`.\'\\\r                     /  ,\'::::.,-\'     `\\::::::||\r                    |  /:::_/\'           `\\::::||\r                    |  \\::-                \\:::||\r                    /_                      \\_/ |\r                   |  \'-._                      /\r                   |\'.    \'`-..._              |\r                   ..  \'--_             \'\'----.|\r                   | `._   \'-----  \'\'\'----__,..\\\r                   |.._ \'-.._________..--\'   ,\'|_\r                   |   `--..__            _,\' /| \'\'--.\r \'\'\'\'\'\'---..__     |          \'`-------\'\'\'   /-\\ .-.._\\_\r              \'-\\__ \\-----....__        _..\'   ,.-. `. .`\\\r                   \'`.          """--"""    _/\' _. \\ \\  | \\\r                      \\--..___       ___..--   / | \' |  |  \\   ___...---\r             _,........\\      """--""        ./  |/-..__=..|,-\'\r   ______, \'\'           `            __,...-\'\'  ,\'     -.. \'\r,-\'                      `.-...,-\'\'\'\'          - |        \'`----------\r                          \\              _.,-\'\' .\'\r                           \\ ..______.,-\'      ,\'\r                            \'-.             ,/\'\r                               \'\'---\'......-\'\r                                                    /`-._\r                                                    |::::""--.._\r                                /(     )\\           /::::::;;;;;\\____\r                                \\\\  _  //          /;;::::::;;;;;;;;;\\\r                    _           / \\(_)/ \\         /;;;;:::::::;;;;;;;;\\___\r                   /;|          |       <        |;;;;;;;:::::::;;;;;;:::;\\\r              ,-._/;;\\           \\_    /        /;;;;;;;;;:::::::::::;;;;;;|\r         _.-;;::::;;;;\\           /    |       /;;;;;:::::::::;;;:::::;;;;;;\\\r        /;;::;;;;;;;;;;\\          |    /     _/;;;;::::::::::;;;;;:::::;;;;;;\\\r    _.-;::::::;;;;;;;;;;\\         \\__  \\    /;;;;;:::::::::;;;;;::::;;;;;;;;;;\\\r_.-;;;::::::::::;;;;;;;;;\\           `-\'  \r/;;;;:::::::::;;;;;;;;;::;;;;;;;;;;;\\\r;;;;;:::::::::::::;;;;;;;;|              \r/;;;;;:::::;;;;;;;;;;;:::::;;;;;;;;JRO\\\r\r                    OUCHOMA         MARXGROUCHO\r           RXGROUCHOMARXGR      ARXGROUCHOMARXGROU\r       HOMARXGROUCHOMARXGR   HOMARXGROUCHOMARXGROUC\r     RXGROUCHOMARXGROUCHO   XGROUCHOMARXGROUCHOMARXGRO\r OMARXGROUCHOMARXGROUCH  ARXGROUCHOMARXGROUCHOMARXGROUC\r CHOMARXGROUCHOMARXGR   HOMARXGROUCHOMARXGROUCHOMARXGROU\rOMARXGROUCHOMARXGR      ARXGROUCHOMARXGROUCHOMARXGROUCHOMA\rROUCHOMARXGROU             OMA   ROUCHOMARXGROUCHOMARXGROU\rOMARXGROUCH                               CHOMARXGROUCHOMAR\r CHOMARXGR                                ROUCHOMARXGROUCHOM\r XGROUCHO                                   RXGROUCHOMARXGROU\r  CHOMAR                                     UCHOMARXGROUCHOM\r    CHO                                       OUCHOMARXGROUCHOM\r                                              RXGROUCHOMARXGROUC\r                             HOMARXGRO        GROUCHOMARXGROUCHO\r          ROUCH            MARXGROUCHOM       CHOMARXGROUCHOMARX\r     MARXGROUCHOM        HOMARXGROUCHOMAR     CHOMARXGROUCHOMARX\r OUCHOMARXGROUCHO       UCHOMARXGROUCHOMARX   UCHOMARXGROUCHOMAR\rOUCHOMARXGROUCHOM       CHOMARXGROUCHOMARXG    HOMARXGROUCHOMARX\r XG      MARXG            OUCHO ARXGROUCH       OUCHOMARXGROUCH\rARX      OMARX  OU       GR     MARXGRO          OUCHOMARXGROUC  MARX\rU       GROUCHOMA       HO     ROUCHOMARXG       ARXGROUCHOMAR   O   OM\rA      C  MAR   O       X     H         C         UCHOMARXGRO   OM    RO\rO     ROU     RXG       A      C        O          OUCHOMARX   UCHO    G\rCH      R    OM         O       U     RXG           ROUCHOM   GROUCHOMA\r XG                     GR           OU     RXGROU    ARXGR  CHOMARXGR\r  MA        OM           ARX        AR     CH    XG      MARXGROUCHOM\r   OMA     UC              ARX     HO      O      RX     H  ARXGROUC\r     OMARXGR                 ARXGROU       G       AR    U HOMARXGR\r           U                               OU       GR   HOMARXGROUC\r           A                 C              ARXG     OM  XGROUCHO  R\r           UC               RXGROU             O      OUCHOMARXG   CH\r            UC       ROU   MARXGROU            H         CHOMAR     C\r             HO     ROUCHOMARXGROUCH           OM        HOMARXG    HO\r        OMARXGROUCHOMARXGROUCHOMARXGR           OU       GROU  O     ROU\r        UCHOMARXGROUCHOMARXGROUCHOMAR            GR        X   U       G\r        GROUCHOMARXGROUCHOMARXGROUCHO             R        M  XG       A\r        XGROUCHOMARXGROUCHOMARXGROUC       ROUCHO A        O AR        M\r         XGROUCHOMAR   OUCHOMARXGRO       XG    H M        HOM        HO\r                                      RXGROU    ARXG        RX        A\r                      UCHOMA         MA    OU      XG                OM\r                    OUCHOM          MA      CH                       M\r                       CHOM        HO        CH                     HO\r                          R        M  XGR                           M\r                                   H    XG                         CH\r                                   OMARXGR                        CH\r                                    X                            OM\r                                   RX                            OM\r      GROUCHO                     MA                            CH\r                                 CH                             O\r                                CH                             OU\r                               MA                              O\r                             XGR                            ARXG\r                           OUC                         ARXGRO\r                           O                         OMA\r                           O                        HO\r                           XG                      RO\r                            OM                    OM\r                             C                   OU\r                             X                   A\r                         GROUCHOMARXGROUCHOMARXGROUCHOMARXGR\r                         GROUCHOMARXGROUCHOMARXGROUCHOMARXGR\r                         GROUCHOMARXGROUCHOMARXGROUCHOMARXGR\r                         GROUCHOMARXGROUCHOMARXGROUCHOMARXGR\r                         CHOMARXGROUCHOMARXGROUCHOMARXGROUCH\r\rNightmare before Christmas\r\r          ,:;.\r         -_7//`\r         `.,\\\\___,,---.\r             \\_____    \\___                 M E R R Y \r                   \\       "".,\r                   (/,,///|\\\\\\;;,-.           C H R I S T M A S\r                 ,;;`  _     _ \\-.\r                ,;;` / `,  / `, . \\             E V E R Y B O D Y !\r                _/   \'.;\' " `-\' |`` \r                // \\            /\r                ,/: `._      _.\':`\r                 ,\\`.  `-\'`-\' .\'/`\r                  ,\\\\`.....,.\'//`                          _\r                   ,\\\\   ||  //`                          /_\\,--/\r                    ,\\\\._||_//`                          // \\__/\r                  __//`_\'\'\'\'\'\\\\_                        //   \\_____\r               __/ __//_""`` \\\\ \\_                   _\\//,_     \\\r            __/ __/|  \\_""` \\\\)   \\_                \' /"/``      \\\r         __/ __/   |  ; \'\'   \\)`/\\_ \\_               / /\r     ___/ __/       )  ;     :`/   \\_ \\_            / /\r____/ ___/          )   ;    :`      \\_ \\_         / /\r\\  __/              \\   :    ;`        \\_ \\_      / /\r \\_ `-.__            )   :   ;           \\_ \\_   / /\r   `-.__ `-.____//    \\   ;  :             \\_ \\_/ /\r        `-._____)====.,)  :  ;               \\_  /\r                \\\\\\  |\\   ;  ;                 \\/\r            ctr    (( /   :  ;\r               _ \\_(_/   / : ;\r             _/ __       |/ ; :\r           _/ _/ /  /|  /   ;  ;\r          / _/  /  ) |  |    ; :\r         / /   /  /  |  |    ; :\r        / /   (  (   |  |    ; :\r       ( (     ) /   |  |    ; :\r       (  \\    ||    | /|    ; ;\r        \\  \\   ||    | ||     ;:\r         \\  \\  ||    | ||     ;;\r          \\ | ,_|.   | ||     ;:\r          | | ````   | ||     `:\r          | |        | ||      :\r         ,_.|.       | ||      :.\r         `````       | ||      \':_\r                     | ||\r                     | ||\r                     | ||\r                     | ||\r                     | ||\r                     | ||\r                     | ||               THE       \r                    \\|_||/       N I G H T M A R E\r                    /|/|\\\\            BEFORE      \r                     | ||        C H R I S T M A S\r                     | ||            - Jack -     \r                     | ||\r                     | //\r                     |||\r                     |||\r                     |||\r                     |||  \r                     \\`-`-.\r                      """""`\r\r'.replace(b'\r', b'\r\n')
    compressed   = comp.encode(data)
    decompressed = comp.decode(compressed)
    print(f"Compressed:   {compressed}")
    print(f"Compressed:   {compressed.hex()}")
    print(f"Decompressed: {decompressed.decode('utf-8')}")
    print(f"Len Compressed:   {len(compressed)}")
    print(f"Len Decompressed: {len(decompressed)}")