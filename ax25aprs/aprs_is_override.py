import re

from aprslib.parsing import chardet, ParseError, UnknownFormat, parse_header, parse_thirdparty, \
    parse_invalid, parse_user_defined, parse_status, parse_mice, parse_message, parse_weather, parse_position
import aprslib

from cfg.logger_config import logger

unsupported_formats = {
        '#':'raw weather report',
        '$':'raw gps',
        '%':'agrelo',
        '&':'reserved',
        '(':'unused',
        ')':'item report',
        '*':'complete weather report',
        '+':'reserved',
        '-':'unused',
        '.':'reserved',
        #'<':'station capabilities',
        '?':'general query format',
        'T':'telemetry report',
        '[':'maidenhead locator beacon',
        '\\':'unused',
        ']':'unused',
        '^':'unused',
}

def _unicode_packet(packet):
    # attempt utf-8
    try:
        return packet.decode('utf-8')
    except UnicodeDecodeError:
        pass

    # attempt to detect encoding
    res = chardet.detect(packet.split(b':', 1)[-1])
    if res['confidence'] > 0.7 and res['encoding'] != 'EUC-TW':
        try:
            return packet.decode(res['encoding'])
        except UnicodeDecodeError:
            pass

    # if everything fails
    return packet.decode('latin-1')

def parse(packet):
    """
    Parses an APRS packet and returns a dict with decoded data

    - All attributes are in metric units
    """

    if not isinstance(packet, aprslib.string_type_parse):
        raise TypeError("Expected packet to be str/unicode/bytes, got %s", type(packet))

    if len(packet) == 0:
        raise ParseError("packet is empty", packet)

    # attempt to detect encoding
    if isinstance(packet, bytes):
        packet = _unicode_packet(packet)

    packet = packet.rstrip("\r\n")
    #logger.debug("Parsing: %s", packet)
    # split into head and body
    try:
        (head, body) = packet.split(':', 1)
    except:
        raise ParseError("packet has no body", packet)

    if len(body) == 0:
        raise ParseError("packet body is empty", packet)

    parsed = {
        'raw': packet,
        }

    # parse head
    try:
        parsed.update(parse_header(head))
    except ParseError as msg:
        raise ParseError(str(msg), packet)

    # parse body
    packet_type = body[0]
    body = body[1:]

    if len(body) == 0 and packet_type != '>':
        raise ParseError("packet body is empty after packet type character", packet)

    # attempt to parse the body
    try:
        _try_toparse_body(packet_type, body, parsed)

    # capture ParseErrors and attach the packet
    except (UnknownFormat, ParseError) as exp:
        exp.packet = packet
        raise

    # if we fail all attempts to parse, try beacon packet
    if 'format' not in parsed:
        if not re.match(r"^(AIR.*|ALL.*|AP.*|BEACON|CQ.*|GPS.*|DF.*|DGPS.*|"
                        "DRILL.*|DX.*|ID.*|JAVA.*|MAIL.*|MICE.*|QST.*|QTH.*|"
                        "RTCM.*|SKY.*|SPACE.*|SPC.*|SYM.*|TEL.*|TEST.*|TLM.*|"
                        "WX.*|ZIP.*|UIDIGI)$", parsed['to']):
            raise UnknownFormat("format is not supported", packet)

        parsed.update({
            'format': 'beacon',
            'text': packet_type + body,
            })

    #logger.debug("Parsed ok.")
    return parsed


def _try_toparse_body(packet_type, body, parsed):
    result = {}

    if packet_type in unsupported_formats:
        raise UnknownFormat("Format is not supported: '{}' {}".format(packet_type, unsupported_formats[packet_type]))

    # ==========================================================
    # 3rd party traffic
    elif packet_type == '}':
        #logger.debug("Packet is third-party")
        body, result = parse_thirdparty(body)

    # ==========================================================
    # invalid
    elif packet_type == ',':
        #logger.debug("Packet is invalid format")
        body, result = parse_invalid(body)

    # ==========================================================
    # user defined
    elif packet_type == '{':
        #logger.debug("Packet is user-defined")
        body, result = parse_user_defined(body)

    # ==========================================================
    # STATUS (inkl. IGATE FIX)

    elif packet_type == '<':
        # IGATE SPECIAL PARSER
        if 'IGATE,' in body:
            logger.debug("Detected IGATE status frame")

            igate_data = {}
            igate_match = re.search(r'<IGATE([^>]*)>', (packet_type + body))

            if igate_match:
                content = igate_match.group(1)
                parts = content.split(',')

                for part in parts:
                    part = part.strip()
                    if not part:
                        continue

                    if '=' in part:
                        k, v = part.split('=', 1)
                        try:
                            igate_data[k.strip()] = int(v.strip())
                        except ValueError:
                            igate_data[k.strip()] = v.strip()
                    else:
                        igate_data[part] = True

            result.update({
                'format': 'igate',
                'status': body,
                'raw': (packet_type + body),
                'igate': igate_data
            })

    elif packet_type == '>':
        #logger.debug("Packet is status")

        # fallback normal status
        body, result = parse_status(packet_type, body)

    # ==========================================================
    # Mic-E
    elif packet_type in "`'":
        #logger.debug("Attempting to parse as mic-e packet")
        body, result = parse_mice(parsed['to'], body)

    # ==========================================================
    # Message
    elif packet_type == ':':
        #logger.debug("Attempting to parse as message packet")
        body, result = parse_message(body)

    # ==========================================================
    # Weather (positionless)
    elif packet_type == '_':
        #logger.debug("Attempting to parse as positionless weather report")
        body, result = parse_weather(body)

    # ==========================================================
    # Telemetry (T#)
    elif body.startswith('T#'):
        #logger.debug("Telemetry packet detected")

        # rudimentärer Parser (aprslib kann das nicht gut)
        result.update({
            'format': 'telemetry',
            'telemetry_raw': body
        })

    # ==========================================================
    # Position
    elif (packet_type in '!=/@;' or
          0 <= body.find('!') < 40):
        #logger.debug("Attempting to parse as position packet")
        body, result = parse_position(packet_type, body)

    # ==========================================================
    # Fallback: Unknown aber behalten
    else:
        logger.debug("Unknown packet type fallback")

        result.update({
            'format': 'unknown',
            'body': body,
        })

    parsed.update(result)


class APRS_IS(aprslib.IS):
    def __init__(self,callsign, passwd, host, port, skip_login):
        super().__init__(callsign=callsign,
                         passwd=passwd,
                         host=host,
                         port=port,
                         skip_login=skip_login)
        self._parse = parse