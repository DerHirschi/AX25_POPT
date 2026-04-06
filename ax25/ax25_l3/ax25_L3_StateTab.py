"""
PoPT - AX25 L3 State Tab
"""

import time
from cfg.logger_config import logger

###########################################################################
###########################################################################
###########################################################################
class DefaultStat(object):
    stat_index = 0  # ENDE Verbindung wird gelöscht...

    def __init__(self, ax25_conn):
        self._ax25conn = ax25_conn
        # Incoming Frame
        self._pf     = False
        self._cmd    = False
        # CTL TAB
        self._ctl_tab = {
            'SABME':    self._rx_SABME,
            'SABM':     self._rx_SABM,
            'DISC':     self._rx_DISC,
            'UA':       self._rx_UA,
            'DM':       self._rx_DM,
            'RR':       self._rx_RR,
            'RNR':      self._rx_RNR,
            'REJ':      self._rx_REJ,
            'I':        self._rx_I,
            'FRMR':     self._rx_FRMR,
            'UI':       self._rx_UI,
        }

    def _change_state(self, zustand_id=1):
        self._ax25conn.change_l3_state(zustand_id)

    def state_rx_handle(self, ax25_frame):
        if ax25_frame.ctl_byte.flag not in self._ctl_tab:
            logger.warning(f"Unknown CLT-Byte:{ax25_frame.ctl_byte.flag}")
            return
        self._pf    = ax25_frame.ctl_byte.pf
        self._cmd   = ax25_frame.ctl_byte.cmd
        self._ctl_tab[ax25_frame.ctl_byte.flag]()

    def _rx_SABME(self):
        """ EAX.25 """
        pass

    def _rx_SABM(self):
        self._cleanup()

    def _rx_UI(self):
        pass

    def _rx_DISC(self):
        """UA, wenn der DISC-Block ohne Poll empfangen wurde."""
        if self._cmd:
            self._ax25conn.send_UA()
        elif not self._pf:
            self._ax25conn.send_UA()
        self.S1_end_connection()

    def _rx_UA(self):
        if self.stat_index:
            self._ax25conn.send_SABM()
            self._ax25conn.set_T1()
            self._change_state(2)

    def _rx_DM(self):
        # RESET !!!!!!!
        if self.stat_index:
            """
            self._ax25conn.reset_conn() ####
            self._ax25conn.send_SABM()
            self._ax25conn.set_T1()
            self._change_state(2)
            """
            self._ax25conn.send_DISC()
            self.S1_end_connection()


    def _rx_RR(self):
        pass

    def _rx_RNR(self):
        pass

    def _rx_REJ(self):
        pass

    def _rx_I(self):
        if self.stat_index:
            # self._ax25conn.set_T1(stop=True)
            self._prozess_I_frame()

    def _rx_FRMR(self):
        if self.stat_index:
            self._ax25conn.send_DISC()
            self._ax25conn.set_T1()
            self._change_state(4)

    def tx(self):
        pass

    def _send_to_link(self, inp: b''):
        self._ax25conn.send_to_link(inp)

    def _state_cron(self):
        pass

    def cron(self):
        """Global Cron"""
        # TODO Move up
        ###########
        # TODO Connection Timeout
        # if self.stat_index:
        if self._ax25conn.n2 > self._ax25conn.parm_N2:
            self._n2_fail()
        else:
            if time.time() > self._ax25conn.t1:
                self._t1_fail()
            if time.time() > self._ax25conn.t3:
                self._t3_fail()
        self._state_cron()  # State Cronex
        """
        if self.stat_index == 0:
            self.cleanup()
        """

    def _cleanup(self):
        # print('STATE 0 Cleanup')
        self._ax25conn.conn_cleanup()

    def S1_end_connection(self, reconn=True):
        self._change_state(1)
        self._ax25conn.end_connection(reconn)

    def S0_end_connection(self):
        self._change_state(0)
        self._cleanup()

    def _t1_fail(self):
        pass
        # self.cleanup()

    def _t3_fail(self):
        self._cleanup()

    def _n2_fail(self):
        self._cleanup()

    def _reject(self):
        self._ax25conn.send_DM()
        self.S1_end_connection()

    def _prozess_I_frame(self):
        return self._ax25conn.prozess_I_frame()

    def _delUNACK(self):
        return self._ax25conn.delUNACK()

class S1Frei(DefaultStat):  # INIT RX
    """
    I mit |I ohne |RR mit |RR ohne|REJ mit|REJ ohne|RNR mit | RNR ohne| SABM    | DISC
    DM            | DM    |       | DM    |        | DM     |         | UA,S5 3)| DM 4)
    """
    stat_index = 1  # FREI

    def _rx_SABM(self):
        self._ax25conn.insert_new_connection()
        self._ax25conn.accept_connection()
        self._ax25conn.send_UA()
        self._change_state(5)
        self._ax25conn.n2 = 0
        self._ax25conn.set_T1(stop=True)
        self._ax25conn.set_T2(stop=True)
        self._ax25conn.set_T3()
        self._ax25conn.exec_cli()  # Process CLI ( C-Text and so on )

        # Handle Incoming Connection

    def _rx_DISC(self):
        self._reject()
        """
        self.ax25conn.send_DM()
        self._change_state(4)
        """

    def _rx_UA(self):
        self._change_state(0)
        self._ax25conn.set_T1(stop=True)

    def _rx_DM(self):
        self._change_state(0)
        self._ax25conn.set_T1(stop=True)

    def _rx_RR(self):
        if self._pf:
            self._reject()
        """
        self._change_state(0)
        self._ax25conn.set_T1(stop=True)
        """

    def _rx_RNR(self):
        if self._pf:
            self._reject()
        """
        self._change_state(0)
        self._ax25conn.set_T1(stop=True)
        """

    def _rx_REJ(self):
        if self._pf:
            self._reject()
        """
        self._change_state(0)
        self._ax25conn.set_T1(stop=True)
        """

    def _rx_I(self):
        if self._pf:
            self._reject()
        """
        self._change_state(0)
        self._ax25conn.set_T1(stop=True)
        """

    def _rx_FRMR(self):
        self._change_state(4)

    def _t1_fail(self):
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()
        """
        if self.ax25conn.is_link_remote:
            parm_n2 = self.ax25conn.parm_N2
        else:
            parm_n2 = 3
        """
        parm_n2 = 3
        if self._ax25conn.n2 > parm_n2:
            # print("S1 t1 FAIL > N2")
            self._change_state(0)

    def _t3_fail(self):
        # print("S1 t3 FAIL")
        self._change_state(0)

class S2Aufbau(DefaultStat):  # INIT TX
    stat_index = 2  # AUFBAU Verbindung Aufbau

    def tx(self):
        """ NOT USED... CLEANUP !!!"""
        pass

    def _rx_SABM(self):
        self._accept()

    def _rx_DISC(self):
        self._reject()

    def _rx_UA(self):
        self._accept()

    def _rx_DM(self):
        self._reject()

    def _rx_FRMR(self):
        pass

    def _rx_I(self):
        pass

    def _accept(self):
        # print("S2 - ACCEPT")
        self._ax25conn.tx_buf_2send = []  # Clean Send Buffer.
        self._ax25conn.clear_tx_buff()    # Clean Send Buffer.
        self._ax25conn.n2 = 0
        self._ax25conn.accept_connection()
        self._change_state(5)

    def _reject(self):
        self._ax25conn.send_sys_Msg_to_gui(f'*** Busy from {self._ax25conn.to_call_str}')
        self._ax25conn.send_to_link(f'*** Busy from {self._ax25conn.to_call_str}'.encode('ASCII', 'ignore'))
        self.S1_end_connection(reconn=False)

    def _state_cron(self):
        pass

    def _t1_fail(self):
        if self._ax25conn.n2 < self._ax25conn.parm_N2:
            self._ax25conn.send_SABM()
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()

    def _t3_fail(self):
        pass

    def _n2_fail(self):
        self._ax25conn.handle_N2_fail()
        self.S1_end_connection(reconn=False)

class S3sendFRMR(DefaultStat):
    stat_index = 3  # Blockrückruf

    def _rx_UA(self):
        pass

    def _rx_DM(self):
        pass

    def _rx_RR(self):
        pass

    def _rx_RNR(self):
        pass

    def _rx_REJ(self):
        pass

    def _rx_I(self):
        pass

    def _t1_fail(self):
        pass
        # Send FRMR

    def _t3_fail(self):
        pass
        # Send FRMR

    def _n2_fail(self):
        # self.ax25conn.send_SABM()
        self.S1_end_connection()

class S4Abbau(DefaultStat):
    stat_index = 4  # ABBAU

    def tx(self):
        self._ax25conn.n2 = 0
        self._ax25conn.clear_tx_buff()
        self._ax25conn.tx_buf_2send = []
        self._ax25conn.tx_buf_unACK = {}
        self._ax25conn.send_DISC()
        self._ax25conn.set_T1()

    def _rx_UA(self):
        self.end_conn()

    def _rx_DM(self):
        self.end_conn()

    def _rx_SABM(self):
        self._reject()

    def _rx_RR(self):
        pass
        """
        if self._pf:
            self.reject()
        """

    def _rx_REJ(self):
        pass
        """
        if self._pf:
            self.reject()
        """

    def _rx_I(self):
        pass
        """
        if self._pf:
            self.reject()
        """

    def _rx_RNR(self):
        pass
        """
        if self._pf:
            self.reject()
         """

    def end_conn(self):
        self.S1_end_connection()
        self._ax25conn.n2 = 100

    def _state_cron(self):
        pass

    def _t1_fail(self):
        # self._change_state(2)
        self._ax25conn.send_DISC()
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()

    def _t3_fail(self):
        pass

    def _n2_fail(self):
        self.S1_end_connection()

class S5Ready(DefaultStat):
    """
    I mit |I ohne |RR mit |RR ohne|REJ mit|REJ ohne|RNR mit | RNR ohne| SABM    | DISC
    RR    | I/RR 1)| RR   | I/- 2)| RR    | I      | RR,S9  | S9      | UA      | UA,S1
    """
    stat_index = 5  # BEREIT

    def _rx_SABM(self):
        self._ax25conn.send_UA()
        self._ax25conn.set_T1(stop=True)
        #self._ax25conn.set_T2(stop=True)

    def _rx_UA(self):
        pass

    def _rx_RR(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        # if self._pf or self._cmd:
        self._ax25conn.set_T1(stop=True)
        self._ax25conn.set_T2(stop=True)
        if self._cmd:
            self._ax25conn.send_RR(pf_bit=self._pf, cmd_bit=False)

    def _rx_REJ(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        if self._pf:
            self._ax25conn.set_T1(stop=True)
            self._ax25conn.send_RR(pf_bit=self._pf, cmd_bit=False)
        else:
            # Maybe all ? or Automode ?
            self._ax25conn.resend_unACK_buf(1)

    def _rx_I(self):
        if not self._prozess_I_frame():
            self._ax25conn.send_REJ(pf_bit=self._pf, cmd_bit=False)
            self._ax25conn.set_T1()
            self._change_state(6)  # go into REJ_state
        else:
            #if self._pf:
            #    self._ax25conn.send_RR(pf_bit=self._pf, cmd_bit=False)
            #elif self._ax25conn.is_tx_buff_empty():
            self._ax25conn.send_RR(pf_bit=self._pf, cmd_bit=False)

    def _rx_RNR(self):
        self._delUNACK()
        if self._pf:
            self._ax25conn.send_RR(pf_bit=self._pf, cmd_bit=False)
        self._change_state(9)

    def tx(self):
        if time.time() < self._ax25conn.t1:
            return
        self._ax25conn.build_I_fm_raw_buf()

    def _state_cron(self):
        pass

    def _t1_fail(self):
        # TODO Move up
        if time.time() < self._ax25conn.t2:
            return
        if self._ax25conn.n2:
            # Nach 5 Versuchen
            if self._ax25conn.n2 > 4:
                # BULLSHIT ?
                self._ax25conn.send_RR(pf_bit=True, cmd_bit=True)
                self._ax25conn.set_T1()
                self._change_state(7)  # S7 Warten auf Final
                # self.rtt_timer.set_rtt_single_timer()
            else:
                if self._ax25conn.tx_buf_unACK:
                    #if self._ax25conn.n2 > 1:
                    #    self._ax25conn.resend_unACK_buf(1)
                    #else:
                    #    self._ax25conn.resend_unACK_buf()
                    self._ax25conn.resend_unACK_buf(1)
                    self._ax25conn.n2 += 1
        else:
            if self._ax25conn.tx_buf_unACK:
                self._ax25conn.resend_unACK_buf()
                self._ax25conn.n2 += 1
                return
            # if not self._ax25conn.tx_buf_unACK:
            self._ax25conn.build_I_fm_raw_buf()

    def _t3_fail(self):
        self._ax25conn.send_RR(pf_bit=True, cmd_bit=True)
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()
        self._change_state(7)  # S7 Warten auf Final
        # self.rtt_timer.set_rtt_single_timer()

class S6sendREJ(DefaultStat):
    """"""
    stat_index = 6  # REJ ausgesandt

    def tx(self):
        pass

    def _rx_SABM(self):
        self._ax25conn.send_UA()
        self._change_state(5)

    def _rx_I(self):
        if self._prozess_I_frame():
            if self._pf:
                self._ax25conn.send_RR(pf_bit=self._pf, cmd_bit=False)
            elif self._ax25conn.is_tx_buff_empty:
                self._ax25conn.send_RR(pf_bit=self._pf, cmd_bit=False)
            self._change_state(5)

    def _rx_REJ(self):

        self._ax25conn.n2 = 0
        self._delUNACK()
        if self._pf:
            self._ax25conn.send_RR(pf_bit=self._pf, cmd_bit=False)
        else:
            # Maybe all ? or Automode ?
            self._ax25conn.resend_unACK_buf(1)

    def _rx_RR(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        # if self._pf or self._cmd:
        if self._cmd:
            self._ax25conn.send_RR(pf_bit=self._pf, cmd_bit=False)
            self._ax25conn.set_T1()
            self._ax25conn.set_T2(stop=True)

    def _rx_RNR(self):
        self._delUNACK()
        if self._pf:
            self._ax25conn.send_RR(pf_bit=self._pf, cmd_bit=False)
        self._change_state(15)

    def _state_cron(self):
        pass

    def _t1_fail(self):
        self._ax25conn.send_RR(pf_bit=True, cmd_bit=True)
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()
        self._change_state(7)  # S7 Warten auf Final

    def _t3_fail(self):
        self._ax25conn.send_RR(pf_bit=True, cmd_bit=True)
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()
        self._change_state(7)  # S7 Warten auf Final

    def _n2_fail(self):
        self._ax25conn.send_SABM()
        self._change_state(2)

class S7WaitForFinal(DefaultStat):
    stat_index = 7  # Warten auf Final

    def _rx_SABM(self):
        self._ax25conn.send_UA()
        self._change_state(5)
        # self.rtt_timer.rtt_single_rx(stop=True)

    def _rx_I(self):
        if self._prozess_I_frame():
            # self._change_state(5)
            if self._pf:
                self._ax25conn.send_RR(pf_bit=self._pf, cmd_bit=False)
            elif self._ax25conn.is_tx_buff_empty:
                self._ax25conn.send_RR(pf_bit=self._pf, cmd_bit=True)

    def _rx_REJ(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        #self._ax25conn.set_T1(stop=True)
        # Maybe all ? or Automode ?
        # self.ax25conn.set_T1()    ?????????
        # self._ax25conn.set_T1()
        if self._pf:
            #self._ax25conn.resend_unACK_buf(1)
            self._ax25conn.set_T1(stop=True)
            self._change_state(5)
        else:
            self._ax25conn.send_RR(pf_bit=True, cmd_bit=True)
            self._ax25conn.set_T1()

    def _rx_RR(self):
        self._ax25conn.n2 = 0
        self._delUNACK()

        if self._pf:
            # self.rtt_timer.rtt_single_rx()
            self._ax25conn.set_T1(stop=True)
            self._ax25conn.set_T2(stop=True)
            self._change_state(5)

    def _rx_RNR(self):
        self._delUNACK()
        if self._pf:
            # self.rtt_timer.rtt_single_rx()
            self._ax25conn.set_T1(stop=True)
            self._ax25conn.set_T2(stop=True)
            self._change_state(9)
        else:
            self._change_state(12)

    def _state_cron(self):
        pass

    def _t1_fail(self):
        self._ax25conn.send_RR(pf_bit=True, cmd_bit=True)
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()

    def _t3_fail(self):
        pass

    def _n2_fail(self):
        self._ax25conn.send_SABM()
        self._change_state(2)

class S8SelfNotReady(DefaultStat):
    stat_index = 8  # nicht bereit

    def _rx_SABM(self):
        self._ax25conn.send_UA()

    def _rx_I(self):
        self._prozess_I_frame()
        self._ax25conn.send_RNR(pf_bit=self._pf, cmd_bit=False)

    def _rx_RR(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        # if self._pf or self._cmd:
        if self._cmd:
            self._ax25conn.send_RNR(pf_bit=self._pf, cmd_bit=False)
            self._ax25conn.set_T2(stop=True)
            self._ax25conn.set_T1(stop=True)

    def _rx_REJ(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        #self._ax25conn.set_T2(stop=True)
        if self._pf:
            self._ax25conn.send_RNR(pf_bit=self._pf, cmd_bit=False)
        else:
            self._ax25conn.resend_unACK_buf(1)

    def _rx_RNR(self):
        self._delUNACK()
        if self._pf:
            self._ax25conn.send_RNR(pf_bit=self._pf, cmd_bit=False)
        self._change_state(10)

    def _state_cron(self):
        pass

    def _t1_fail(self):
        if time.time() > self._ax25conn.t2:
            # Nach 5 Versuchen
            if self._ax25conn.n2:
                if self._ax25conn.n2 > 4:
                    # BULLSHIT ?
                    self._ax25conn.send_RNR(pf_bit=True, cmd_bit=True)
                    self._ax25conn.set_T1()
                    self._change_state(11)  # S7 Warten auf Final
                    # self.rtt_timer.set_rtt_single_timer()
                else:
                    if self._ax25conn.tx_buf_unACK:
                        self._ax25conn.resend_unACK_buf(1)
                        self._ax25conn.n2 += 1
            else:
                if self._ax25conn.tx_buf_unACK:
                    self._ax25conn.resend_unACK_buf()
                    self._ax25conn.n2 += 1
                    return
                #if not self._ax25conn.tx_buf_unACK:
                self._ax25conn.build_I_fm_raw_buf()
                # self._ax25conn.set_T1()

    def _t3_fail(self):
        self._ax25conn.send_RNR(pf_bit=True, cmd_bit=True)
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()
        self._change_state(11)  # S7 Warten auf Final
        # self.rtt_timer.set_rtt_single_timer()

    def _n2_fail(self):
        pass

class S9DestNotReady(DefaultStat):
    stat_index = 9  # Gegenstelle nicht bereit

    def _rx_SABM(self):
        self._ax25conn.send_UA()
        self._change_state(5)

    def _rx_I(self):
        if self._prozess_I_frame():
            self._ax25conn.send_RR(pf_bit=self._pf, cmd_bit=False)
        else:
            self._ax25conn.send_REJ(pf_bit=self._pf, cmd_bit=False)
            self._change_state(15)

    def _rx_RR(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        # if self._pf or self._cmd:
        if self._cmd:
            self._ax25conn.send_RR(pf_bit=self._pf, cmd_bit=False)
        self._ax25conn.set_T1(stop=True)

        self._change_state(5)

    def _rx_REJ(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        # self._ax25conn.set_T2(stop=True)
        if self._pf:
            self._ax25conn.send_RR(pf_bit=self._pf, cmd_bit=False)
        self._change_state(5)

    def _rx_RNR(self):
        # self._change_state(10)
        self._delUNACK()
        if self._pf:
            self._ax25conn.send_RR(pf_bit=self._pf, cmd_bit=False)

    def _t1_fail(self):
        pass
        """
        self.ax25conn.send_RR(pf_bit=True, cmd_bit=True)
        self.ax25conn.n2 += 1
        self.ax25conn.set_T1()
        self._change_state(12)  # S7 Warten auf Final
        """

    def _t3_fail(self):
        self._ax25conn.send_RR(pf_bit=True, cmd_bit=True)
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()
        self._change_state(12)  # S7 Warten auf Final

    def _n2_fail(self):
        pass

class S10BothNotReady(DefaultStat):
    stat_index = 10  # Beide Seiten nicht bereit

    def _rx_SABM(self):
        self._ax25conn.send_UA()
        self._change_state(8)

    def _rx_I(self):
        self._prozess_I_frame()
        self._ax25conn.send_RNR(pf_bit=self._pf, cmd_bit=False)

    def _rx_RR(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        # if self._pf or self._cmd:
        if self._cmd:
            self._ax25conn.send_RNR(pf_bit=self._pf, cmd_bit=False)
            self._ax25conn.set_T1(stop=True)

        self._change_state(8)

    def _rx_REJ(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        #self._ax25conn.set_T2(stop=True)
        if self._pf:
            self._ax25conn.send_RNR(pf_bit=self._pf, cmd_bit=False)
        self._change_state(8)

    def _rx_RNR(self):
        # self._change_state(10)
        self._delUNACK()
        if self._pf:
            self._ax25conn.send_RNR(pf_bit=self._pf, cmd_bit=False)

    def _t1_fail(self):
        pass
        """
        self.ax25conn.send_RNR(pf_bit=True, cmd_bit=True)
        self.ax25conn.n2 += 1
        self.ax25conn.set_T1()
        self._change_state(13)  # S7 Warten auf Final
        """

    def _t3_fail(self):
        self._ax25conn.send_RNR(pf_bit=True, cmd_bit=True)
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()
        self._change_state(13)  # S7 Warten auf Final

    def _n2_fail(self):
        pass

class S11SelfNotReadyFinal(DefaultStat):
    stat_index = 11  # Selber nicht bereit und auf Final warten

    def _rx_SABM(self):
        self._ax25conn.send_UA()
        self._change_state(8)

    def _rx_I(self):
        self._prozess_I_frame()
        self._ax25conn.send_RNR(pf_bit=self._pf, cmd_bit=False)

    def _rx_RR(self):
        self._ax25conn.n2 = 0
        # if self._pf or self._cmd:
        self._delUNACK()

        if self._cmd:
            self._ax25conn.send_RNR(pf_bit=True, cmd_bit=False)
            self._ax25conn.set_T1()
        elif self._pf:
            self._ax25conn.set_T1(stop=True)
            self._change_state(8)
            # self.rtt_timer.rtt_single_rx()

    def _rx_REJ(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        #self._ax25conn.set_T2(stop=True)
        if self._pf:
            self._ax25conn.send_RNR(pf_bit=self._pf, cmd_bit=False)
            self._change_state(8)  # ???
            # self.rtt_timer.rtt_single_rx()  # ???
        else:
            self._ax25conn.resend_unACK_buf(1)
            #self._ax25conn.set_T1()
            # self.ax25conn.set_T1(stop=True)

    def _rx_RNR(self):
        self._delUNACK()
        if self._pf and not self._cmd:
            # self.rtt_timer.rtt_single_rx()
            self._change_state(10)
        elif self._cmd:
            self._ax25conn.send_RR(pf_bit=self._pf, cmd_bit=False)
            self._change_state(13)
        else:
            self._change_state(13)
        # self.rtt_timer.rtt_single_rx(stop=True)

    def _state_cron(self):
        pass

    def _t1_fail(self):
        self._ax25conn.send_RNR(pf_bit=True, cmd_bit=True)
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()

    def _t3_fail(self):
        pass

    def _n2_fail(self):
        self._ax25conn.send_SABM()
        self._change_state(2)

class S12DestNotReadyFinal(DefaultStat):
    stat_index = 12  # Gegenstelle nicht bereit und auf Final warten

    def _rx_SABM(self):
        self._ax25conn.send_UA()
        self._change_state(5)

    def _rx_I(self):
        self._prozess_I_frame()
        self._ax25conn.send_RR(pf_bit=self._pf, cmd_bit=False)

    def _rx_RR(self):
        self._ax25conn.n2 = 0
        self._delUNACK()

        # if self._pf or self._cmd:
        if self._cmd:
            self._ax25conn.set_T1(stop=True)
            self._change_state(5)
        else:
            self._change_state(7)

    def _rx_REJ(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        #self._ax25conn.set_T2(stop=True)
        #self._ax25conn.resend_unACK_buf(1)
        #self._ax25conn.set_T1()
        if self._pf:
            self._change_state(5)
            # self.ax25conn.send_RR(pf_bit=self._pf, cmd_bit=False)
        else:
            self._change_state(7)

    def _rx_RNR(self):
        # self._change_state(10)
        self._delUNACK()
        if self._pf:
            self._change_state(9)
            # self.ax25conn.send_RR(pf_bit=self._pf, cmd_bit=False)

    def _t1_fail(self):
        self._ax25conn.send_RR(pf_bit=True, cmd_bit=True)
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()

    def _t3_fail(self):
        pass

    def _n2_fail(self):
        self._ax25conn.send_SABM()
        self._change_state(2)

class S13BothNotReadyFinal(DefaultStat):
    stat_index = 13  # Beide Seiten nicht bereit und auf Final warten

    def _rx_SABM(self):
        self._ax25conn.send_UA()
        self._change_state(8)

    def _rx_I(self):
        self._prozess_I_frame()
        self._ax25conn.send_RNR(pf_bit=self._pf, cmd_bit=False)

    def _rx_RR(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        if self._pf:
            self._change_state(8)
            self._ax25conn.send_RNR(pf_bit=self._pf, cmd_bit=False)
            self._ax25conn.set_T1(stop=True)
        else:
            self._change_state(11)

    def _rx_REJ(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        # self._ax25conn.set_T2(stop=True)
        if self._pf:
            self._ax25conn.send_RNR(pf_bit=self._pf, cmd_bit=False)
            self._change_state(8)
        else:
            self._ax25conn.resend_unACK_buf(1)
            self._change_state(11)

    def _rx_RNR(self):
        self._delUNACK()
        if self._pf:
            self._ax25conn.send_RNR(pf_bit=self._pf, cmd_bit=False)
        else:
            self._change_state(11)

    def _t1_fail(self):
        self._ax25conn.send_RNR(pf_bit=True, cmd_bit=True)
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()

    def _t3_fail(self):
        pass

    def _n2_fail(self):
        self._ax25conn.send_SABM()
        self._change_state(2)

class S14sendREJselfNotReady(DefaultStat):  # TODO  /  / Testing
    stat_index = 14  # REJ ausgesandt u. Selbst nicht bereit

    def _rx_SABM(self):
        self._ax25conn.send_UA()
        self._change_state(8)

    def _rx_I(self):
        self._prozess_I_frame()
        self._ax25conn.send_RNR(pf_bit=self._pf, cmd_bit=False)

    def _rx_RR(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        # if self._pf or self._cmd:
        if self._cmd:
            self._ax25conn.send_RNR(pf_bit=self._pf, cmd_bit=False)
            self._ax25conn.set_T1(stop=True)

    def _rx_REJ(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        #self._ax25conn.set_T2(stop=True)
        if self._pf:
            self._ax25conn.send_RNR(pf_bit=self._pf, cmd_bit=False)
        else:
            self._ax25conn.resend_unACK_buf(1)

    def _rx_RNR(self):
        self._delUNACK()
        if self._pf:
            self._ax25conn.send_RNR(pf_bit=self._pf, cmd_bit=False)
        self._change_state(16)

    def _t1_fail(self):
        self._ax25conn.send_RNR(pf_bit=True, cmd_bit=True)
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()
        self._change_state(11)  # S7 Warten auf Final

    def _t3_fail(self):
        self._ax25conn.send_RNR(pf_bit=True, cmd_bit=True)
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()
        self._change_state(11)  # S7 Warten auf Final

    def _n2_fail(self):
        pass

class S15sendREJdestNotReady(DefaultStat):  # TODO  /  / Testing
    stat_index = 15  # REJ ausgesandt u. Gegenstelle nicht bereit

    def _rx_SABM(self):
        self._ax25conn.send_UA()
        self._change_state(5)

    def _rx_I(self):
        self._prozess_I_frame()
        self._ax25conn.send_RR(pf_bit=self._pf, cmd_bit=False)
        self._change_state(9)

    def _rx_RR(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        # if self._pf or self._cmd:
        if self._cmd:
            self._ax25conn.send_RR(pf_bit=self._pf, cmd_bit=False)
            self._ax25conn.set_T1(stop=True)

        self._change_state(6)

    def _rx_REJ(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        #self._ax25conn.set_T2(stop=True)
        if self._pf:
            self._ax25conn.send_RR(pf_bit=self._pf, cmd_bit=False)
        else:
            self._ax25conn.resend_unACK_buf(1)

        self._change_state(6)

    def _rx_RNR(self):
        self._delUNACK()
        if self._pf:
            self._ax25conn.send_RR(pf_bit=self._pf, cmd_bit=False)

    def _t1_fail(self):
        self._ax25conn.send_RR(pf_bit=True, cmd_bit=True)
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()
        self._change_state(12)  # S7 Warten auf Final

    def _t3_fail(self):
        self._ax25conn.send_RR(pf_bit=True, cmd_bit=True)
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()
        self._change_state(12)  # S7 Warten auf Final

    def _n2_fail(self):
        pass

class S16sendREJbothNotReady(DefaultStat):  # TODO  / / Testing
    stat_index = 16  # REJ ausgesandt u. beide Seiten nicht bereit

    def _rx_SABM(self):
        self._ax25conn.send_UA()
        self._change_state(5)

    def _rx_I(self):
        self._prozess_I_frame()
        self._ax25conn.send_RNR(pf_bit=self._pf, cmd_bit=False)

    def _rx_RR(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        # if self._pf or self._cmd:
        if self._cmd:
            self._ax25conn.send_RNR(pf_bit=self._pf, cmd_bit=False)
            self._ax25conn.set_T1(stop=True)

        self._change_state(14)

    def _rx_REJ(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        #self._ax25conn.set_T2(stop=True)
        if self._pf:
            self._ax25conn.send_RNR(pf_bit=self._pf, cmd_bit=False)
        else:
            self._ax25conn.resend_unACK_buf(1)

        self._change_state(14)

    def _rx_RNR(self):
        self._delUNACK()
        if self._pf:
            self._ax25conn.send_RNR(pf_bit=self._pf, cmd_bit=False)

    def _t1_fail(self):
        self._ax25conn.send_RR(pf_bit=True, cmd_bit=True)
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()
        self._change_state(11)  # S7 Warten auf Final

    def _t3_fail(self):
        self._ax25conn.send_RR(pf_bit=True, cmd_bit=True)
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()
        self._change_state(11)  # S7 Warten auf Final

    def _n2_fail(self):
        pass

AX25L3_STATE_TAB = {
            0:  (DefaultStat, 'ENDE'),
            1:  (S1Frei, 'FREI'),
            2:  (S2Aufbau, 'AUFBAU'),
            3:  (S3sendFRMR, 'FRMR'),
            4:  (S4Abbau, 'ABBAU'),
            5:  (S5Ready, 'BEREIT'),
            6:  (S6sendREJ, 'REJ'),
            7:  (S7WaitForFinal, 'FINAL'),
            8:  (S8SelfNotReady, 'RNR'),
            9:  (S9DestNotReady, 'DEST-RNR'),
            10: (S10BothNotReady, 'BOTH-RNR'),
            11: (S11SelfNotReadyFinal, 'RNR-F'),
            12: (S12DestNotReadyFinal, 'DEST-RNR-F'),
            13: (S13BothNotReadyFinal,  'BOTH-RNR-F'),
            14: (S14sendREJselfNotReady, 'RNR-REJ'),
            15: (S15sendREJdestNotReady, 'DEST-RNR-REJ'),
            16: (S16sendREJbothNotReady, 'BOTH-RNR-REJ'),
        }