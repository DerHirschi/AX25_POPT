import random
import string


def get_baycom_pw(password: str, req_pattern: str):
    print(f"BC pw: {password}\n patt: {req_pattern}")
    req_pattern = req_pattern.replace('\r', '')
    tmp = req_pattern.split(' ')
    tmp.reverse()
    tmp_patt = []
    for el in tmp:
        if el.isdigit():
            tmp_patt.append(el)
        if len(tmp_patt) == 5:
            break

    tmp_patt.reverse()
    res = ''
    print(f"patt: {tmp_patt}")
    for index in tmp_patt:
        if len(password) < int(index):
            return ''
        res += password[int(index) - 1]
    print(f"Patt: {req_pattern}")
    return res


def get_random_string(length: int):
    chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for i in range(length))


class BaycomLogin(object):
    def __init__(self, sys_pw: str, sys_pw_parm: str, login_cmd=''):
        if login_cmd:
            login_cmd = login_cmd.replace('\r', '').replace('\n', '')
            self.sys_cmd = login_cmd + '\r'
        else:
            self.sys_cmd = 'SYS\r'
        self.sys_pw = sys_pw
        self.attempts = int(sys_pw_parm[0])
        self.length = int(sys_pw_parm[1])
        self.attempt_count = 0
        self.fail_counter = 0
        self.hot_attempt = 1
        if not self.attempts:
            self.attempts = 1
        self.hot_attempt = random.randint(1, self.attempts)

    def start(self):
        return self.sys_cmd

    def step(self, inp: str):
        # TODO FBB can handle random fill just after real response
        # TODO Maybe own classes for each SW
        if self.attempt_count == self.attempts:
            # print(f'{self.attempt_count}>{self.attempts}')
            return ''

        res = get_baycom_pw(self.sys_pw, inp)
        if not res:
            print('not res')
            self.fail_counter += 1
            return ''
        self.attempt_count += 1
        self.fail_counter = 0
        if self.attempt_count == self.hot_attempt:
            fill = ''
            end_fill = ''
            if self.length:
                fill = get_random_string(random.randint(0, self.length - 5))

            ret = fill + res
            if self.length:
                end_fill = get_random_string(self.length - len(ret))
            ret += end_fill + '\r'
        else:
            length = 5
            if self.length:
                length = self.length
            ret = get_random_string(length) + '\r'

        if self.attempt_count < self.attempts:
            return ret + self.sys_cmd
        return ret


