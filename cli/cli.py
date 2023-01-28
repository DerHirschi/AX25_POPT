

class DefaultCLI(object):
    c_text = '-= Test C-TEXT =-\r\r'
    bye_text = '73 ...\r'
    prompt = '\rTEST-STATION>'
    encoding = 'UTF-8', 'ignore'

    def __init__(self):
        self.state_index = 0
        self.state_exec = {
            0: self.s0,     # C-Text
            1: self.s1,     # Prompt
            2: self.s2,     # Bye bye Text
            3: self.s3,
            4: self.s4,
            5: self.s5,
            6: self.s6,
            7: self.s7,
            8: self.s8,
            9: self.s9,
        }
        self.input = b''

    def cli_exec(self, inp=b''):
        self.input = inp.decode(self.encoding[0], self.encoding[1])
        ret = self.state_exec[self.state_index]()
        ret += self.prompt
        return ret.encode(self.encoding[0], self.encoding[1])

    def s0(self):
        self.state_index = 1
        return self.c_text

    def s1(self):
        return self.prompt

    def s2(self):
        return self.bye_text

    def s3(self):
        pass

    def s4(self):
        pass

    def s5(self):
        pass

    def s6(self):
        pass

    def s7(self):
        pass

    def s8(self):
        pass

    def s9(self):
        pass


class NodeCLI(DefaultCLI):
    pass
