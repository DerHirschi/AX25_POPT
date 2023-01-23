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
"""
#a.decode(b'\xc0\x00\x88\xb0`\xa6\x82\xae\xe0\x9a\x88d\xa6\x82\xae`\x86\x84`\xa6\x82\xae\xe1?\xc0')
print("{}-{}".format(a.from_call.call, a.from_call.ssid))
print("r_bits {}  - Type: ".format(a.from_call.r_bits, type(a.from_call.r_bits)))
print(type(a.from_call.r_bits))
print("{}-{}".format(a.to_call.call, a.to_call.ssid))
print("r_bits {}  - Type: ".format(a.to_call.r_bits, type(a.to_call.r_bits)))
for call in a.via_calls:
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
print("data: {}".format(a.data))
print("data_len: {}".format(a.data_len))
"""
"""
a = AX25Frame()
a.from_call.call = 'MD2SAW'
a.from_call.ssid = 0
a.to_call.call = 'DX0SAW'
a.to_call.ssid = 0
a.ctl_byte.SABMcByte()
"""
#print(a.hexstr)
a.encode()
print(a.hexstr)
#print(a.hexstr[59])
#print(a.hexstr[59:])
#print(hex(a.hexstr[59]))
#print(bytes.fromhex(a.hexstr.decode()))

b = AX25Frame()
#a.encode()
#print(a.hexstr)

b.decode((bytes.fromhex('c000') + a.hexstr + bytes.fromhex('c0')))

print("{}-{}".format(b.from_call.call, b.from_call.ssid))
print("r_bits {}  - Type: ".format(b.from_call.r_bits, type(b.from_call.r_bits)))
print(type(b.from_call.r_bits))
print("{}-{}".format(b.to_call.call, b.to_call.ssid))
print("r_bits {}  - Type: ".format(b.to_call.r_bits, type(b.to_call.r_bits)))
for call in b.via_calls:
    print("{}-{}".format(call.call, call.ssid))

print("ctl_str: {}".format(b.ctl_byte.ctl_str))
print("type: {}".format(b.ctl_byte.type))
print("flag: {}".format(b.ctl_byte.flag))
print("pf: {}".format(b.ctl_byte.pf))
print("cmd: {}".format(b.ctl_byte.cmd))
print("nr: {}".format(b.ctl_byte.nr))
print("ns: {}".format(b.ctl_byte.ns))
print("pid: {}".format(b.ctl_byte.pid))
print("info: {}".format(b.ctl_byte.info))
print("hex: {}".format(b.ctl_byte.hex))
print("pid_byte.flag: {}".format(b.pid_byte.flag))
print("pid_byte.hex: {}".format(hex(b.pid_byte.hex)))
print("data: {}".format(b.data))
print("data_len: {}".format(b.data_len))
