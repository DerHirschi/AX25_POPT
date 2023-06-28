class RxEchoVars(object):
    def __init__(self, port_id: int):
        self.port_id = port_id
        self.rx_ports: {int: [str]} = {}
        self.tx_ports: {int: [str]} = {}
        self.tx_buff: [] = []
    """
    def buff_input(self, ax_frame, port_id: int):
        if port_id != self.port_id:
            self.tx_buff.append(ax_frame)
    """
