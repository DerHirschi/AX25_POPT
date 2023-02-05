

class DefaultCLI(object):
    c_text = '-= Test C-TEXT =-\r\r'
    bye_text = '73 ...\r'
    prompt = '\rTEST-STATION>'
    prefix = '//'

    def __init__(self):
        self.state_index = 0
        self.state_exec = {}
        self.input = ''
        self.encoding = 'UTF-8', 'ignore'
        self.init()

    def init(self):
        self.state_exec = {
            0: self.s0,  # C-Text
            1: self.s1,  # Prompt
            2: self.s2,  # Bye bye Text
        }

    def cli_exec(self, inp=b''):
        self.input = inp.decode(self.encoding[0], self.encoding[1])
        ret = self.state_exec[self.state_index]()
        # ret += self.prompt
        return ret.encode(self.encoding[0], self.encoding[1])

    def s0(self):   # C-Text
        self.state_index = 1
        return self.c_text + self.prompt

    def s1(self):
        return self.prompt

    def s2(self):
        return self.bye_text


class NodeCLI(DefaultCLI):
    c_text = '-= Test C-TEXT 2=-\r\r'   # Can overwrite in config
    bye_text = '73 ...\r'
    prompt = '\rTEST-STATION-2>'
    prefix = ''

    def init(self):
        self.state_exec = {
            0: self.s0,  # C-Text
            1: self.s1,  # Prompt
            2: self.s2,  # Bye bye Text
        }

    def s1(self):
        return self.prompt

    def s2(self):
        return self.bye_text

