from ax25pac import *
import logging

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# a = DecAX25(b'\xc0\x00\x88\xb0`\xa6\x82\xae\xe0\x9a\x88d\xa6\x82\xae`\x86\x84`\xa6\x82\xae\xe1?\xc0')
a = AX25Frame()
a.decode(b'\xc0\x00\x9a\x88d\xa6\x82\xae\xe2\x88\xb0`\xa6\x82\xae`\x86\x84`\xa6\x82\xae`\x86\x84`\xa6\x82\xaea \xf0    2d,19h P0  FRA323     2d,19h P0  FRA323-8 \r  2d,19h P0  NOD3\xc0')

#a.decode(b'\xc0\x00\x88\xb0`\xa6\x82\xae\xe0\x9a\x88d\xa6\x82\xae`\x86\x84`\xa6\x82\xae\xe1?\xc0')
print("{}-{}".format(a.from_call.call, a.from_call.ssid))
print("{}-{}".format(a.to_call.call, a.to_call.ssid))
for call in a.via_call:
    print("{}-{}".format(call.call, call.ssid))

print("ctl_str: {}".format(a.ctl_byte.ctl_str))
print("type: {}".format(a.ctl_byte.type))
print("flag: {}".format(a.ctl_byte.flag))
print("pf: {}".format(a.ctl_byte.pf))
print("cmd: {}".format(a.ctl_byte.cmd))
print("nr: {}".format(a.ctl_byte.nr))
print("ns: {}".format(a.ctl_byte.ns))
print("pid: {}".format(a.ctl_byte.pid))
print("info: {}".format(a.ctl_byte.info))
print("hex: {}".format(a.ctl_byte.hex))
print("pid_byte.flag: {}".format(a.pid_byte.flag))
print("pid_byte.hex: {}".format(hex(a.pid_byte.hex)))
