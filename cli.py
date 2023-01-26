

class DefaultCLI(object):
    c_text = '-= Test C-TEXT =-\r\n\r\n'
    bye_text = '73 ...\r\n'
    prompt = '\r\nTEST-STATION>'
    encoding = 'UTF-8', 'ignore'

    def __init__(self):
        self.state_index = 0
        self.state_exec = {
            0: self.s0,     # C-Text
            1: self.s1,     # Prompt
            10: self.s10,   # Bye bye Text
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
        inp = self.input
        return self.prompt

    def s10(self):
        return self.bye_text


class NodeCLI(DefaultCLI):
    pass
