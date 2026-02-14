# ============================================================
# PRP L3 Test App – vollständiger Bidirektionaler Test
# ============================================================
import random
import threading
import time
import os

from cfg.logger_config import logger
from prp.prp_l3.prp_transport_adapter import MockAx25Transport, PRPTransportAdapter
from prp.prp_remote import PRPremote
from prp.prp_const import PRP_OPT_ESC_CLI

SOUND_ON = True

def beep_sound(freq=1000, beep_len=50, loop=0):
    if not SOUND_ON:
        return
    if not loop:
        os.system(f"beep -f {freq} -l {beep_len}")
        return
    for i in range(loop):
        os.system(f"beep -f {freq} -l {beep_len}")
        time.sleep(beep_len/1000)

def beep_alarm():
    """
    for i in range(4):
        beep_sound(loop=3, freq=1500, beep_len=25,)
        beep_sound(loop=2, beep_len=50, freq=1000)
        beep_sound(beep_len=150, freq=1500, loop=1)
    """

    beep_sound(loop=10, beep_len=50, freq=1900)



# Mocks
class PseudoGUI:
    def init_popt_remote(self, var1): pass

class PseudoPortHandler:
    def handle_prp_response(self, var1, var2):
        logger.info(f"Mock: handle_prp_response({var1}, {var2})")
    def get_gui(self): return PseudoGUI()
    def get_config_value(self): return None
    def handle_remote_monitor_rx(self, var1, var2): pass

def init_prpTester(uid: str):
    config = {
        'uid': uid,
        'remote_uid': uid,
        'to_call_str': uid,
        'conn_typ': 'ax25_l2'
    }
    ph              = PseudoPortHandler()
    adapter         = PRPTransportAdapter()
    mock_transport  = MockAx25Transport(name=config['uid'])

    adapter.register_transport(mock_transport)


    return PRPremote(ph, config, transport_adapter=adapter)

# Simuliere Empfang
def simulate_rx(instance, raw_data):
    logger.info(f"RX → [{instance.uid}]: raw_data Len={len(raw_data)}")
    non_prp_data = instance.prp_rx(raw_data)
    #if non_prp_data:
    #    logger.info(f"RX → [{instance.uid}] - Non PRP-DATA: Len={len(non_prp_data)} - Data: {non_prp_data}")
    return non_prp_data

# Seq-Zähler setzen, um Fehler zu provozieren
def set_seq_counter(instance1, instance2, seq_nr: int, prio=True):
    instance1.prp_transport.set_current_seq(instance2.uid, prio, seq_nr)

# =========================================================================
# =========================================================================
# =========================================================================
# =========================================================================
class Simulator:
    def __init__(self,
                 data_len: int,
                 random_pac_lost: int,
                 random_data_lost: bool,
                 pac_size: int,
                 prio: bool,
                 ):
        self.prp_server: PRPremote = init_prpTester('SERVER')
        self.prp_client: PRPremote = init_prpTester('CLIENT')

        # ==========================================
        self._tx_cache_free_limit = 2000

        # ==========================================
        # Auswertung
        # ==========================================
        get_res_vars = lambda : {
            'send_data': bytearray(),
            'recv_data': bytearray(),

            'lost_bytes':  0,
            'lost_packet': 0,
            'total_bytes': 0,
            'total_packet': 0,
        }
        self.prp_test_results = {
            'SERVER': get_res_vars(),
            'CLIENT': get_res_vars(),
        }
        self.start_time        = None  # Speichert den Startzeitpunkt
        self.original_data_len = data_len
        # ==========================================

        self._cfg = self._cfg = {
            "data_len": data_len,
            "pac_size": pac_size ,
            "random_pac_lost": random_pac_lost,
            "random_data_lost": random_data_lost,
            "prio": prio

        }
        # ==========================================
        logger.info(f"==== Test Init: Erstelle Random Cfg")

        chance      = round(self._cfg.get('random_pac_lost', 0) / 10)
        rest        = 10 - chance
        cfg_list    = ([False] * chance) + ([True] * rest)
        self._ran_cfg = []
        while cfg_list:
            var = random.choice(cfg_list)
            self._ran_cfg.append(var)
            cfg_list.remove(var)

        # ==========================================
        # Test Daten erstellen
        self._tx_data_Chunks_server = []
        self._tx_data_Chunks_client = []

        # ==========================================
        # CTRL
        self.app_running  = True
        self._cl_tasker_tick = False
        self._se_tasker_tick = False
        #self._tasker_th   = threading.Thread(target=self.tasker)
        self._client_th = threading.Thread(target=self._client_tasks)
        self._server_th = threading.Thread(target=self._server_tasks)
        #self._client_prp_th = threading.Thread(target=self._client_prp_tasks)
        #self._server_prp_th = threading.Thread(target=self._server_prp_tasks)

        self._time_scale  = 1000

        self.stepper    = False
        self._step_tick = False

        self.inj_stepper    = False
        self._inj_step_tick = False

        #logger.info("==== Test APP - Starte Tasker Thread ====")
        #self._tasker_th.start()

    # =========================================
    def start_app(self):
        beep_sound()
        logger.info("======== Test APP - Start ========")

        data_len = self._cfg.get('data_len', 1000000)

        data = [bytearray(), bytearray()]
        logger.info(f"======== Erzeuge Testdaten - {round(data_len/1024, 2)} kB / {round(data_len/1024/1024, 2)} MB ========")
        prz = 0
        while len(data[0]) < data_len:
            data[0] += random.randint(0, 65535).to_bytes(2, 'little')
            data[1] += random.randint(0, 65535).to_bytes(2, 'little')
            new_prz =  round(len(data[0]) / data_len * 100)
            if new_prz > prz:
                pr_ten = round(new_prz / 10)
                pr_rest = 10 - pr_ten
                bar = f"{'#' * pr_ten}{'.' * pr_rest}"
                logger.info(f"== [{bar}] {new_prz}% - {round(len(data[0])/1024/1024, 2)} MB / {round(data_len/1024/1024, 2)} MB")
                prz = int(new_prz)
        logger.info(f"== Testdaten Erzeugt {round(len(data[0])/1024/1024, 2)} MB / Soll: {round(data_len/1024/1024, 2)} MB")

        self.prp_test_results['SERVER']['send_data'] = bytearray(data[0])
        self.prp_test_results['CLIENT']['send_data'] = bytearray(data[1])

        beep_sound()
        logger.info(f"======== Erzeuge Test Daten Chunks ========")
        while data[0]:
            ran_len = random.randint(30, 2200)
            tmp0 = data[0][:ran_len]
            tmp1 = data[1][:ran_len]
            data[0] = data[0][len(tmp0):]
            data[1] = data[1][len(tmp1):]
            self._tx_data_Chunks_server.append(tmp0)
            self._tx_data_Chunks_client.append(tmp1)

        logger.info(f"== Cfg ==========================")
        logger.info(f"== Cfg data_len    : {data_len}")
        logger.info(f"== Cfg pac_size    : {self._cfg.get('random_pac_lost', 0)}")
        logger.info(f"== Cfg Pac-Lost    : {self._cfg.get('random_data_lost', False)}")
        logger.info(f"== Cfg Data-Lost   : {self._cfg.get('pac_size', 1280)}")
        logger.info(f"== Cfg Prio        : {self._cfg.get('prio', True)}")
        logger.info(f"== Erzeugte Test Daten ==========")
        logger.info(f"== Länge Datensatz : {data_len} Bytes / {round(data_len / 1024)} kB / {round(data_len / 1024 / 1024)} MB")
        logger.info(f"== Anzahl Chunks   : {len(self._tx_data_Chunks_server)} Chunks")
        logger.info(f"=================================")
        self.start_time = time.time()
        # ==========================
        # random_cfg zwischenspeichern und True setzen für Handshake
        ran_cfg = list(self._ran_cfg)
        self._ran_cfg = [True]
        # ==========================
        beep_sound(freq=2025, beep_len=20)
        self.app_running = True
        logger.info("==== Test APP - Starte Client Thread ====")
        self._client_th.start()
        logger.info("==== Test APP - Starte Client PRP-Thread ====")
        #self._client_prp_th.start()
        logger.info("==== Test APP - Starte Server Thread ====")
        self._server_th.start()
        logger.info("==== Test APP - Starte Server PRP-Thread ====")
        #self._server_prp_th.start()
        beep_sound(freq=1200, beep_len=50)

        logger.info("==== Sende Handshake an Server ====")
        self.prp_client.prp_tx_l3_handshake()

        time.sleep(1)
        logger.info("==== Test APP - Starte Test Ablauf ====")

        # ==========================
        # random_cfg wiederherstellen
        self._ran_cfg = list(ran_cfg)
        try:
            self.run_main()
        except Exception as ex:
            self.app_running = False
            logger.error(ex)
            breakpoint()
            raise ex

    def close_app(self):
        self.app_running = False
        beep_sound()
        beep_sound()
        beep_sound()
        #if hasattr(self._tasker_th, 'is_alive'):
        #    if self._tasker_th.is_alive():
        #        logger.info("==== Test APP ENDE - Warte auf Tasker Thread ====")
        #        beep_sound()
        #        return

        logger.info(f"==== ----------------------------------------------------------------- ====")
        logger.info("==== Test Auswertung ====")
        if all((
                self.prp_test_results['SERVER']['send_data'] == self.prp_test_results['SERVER']['recv_data'],
                self.prp_test_results['CLIENT']['send_data'] == self.prp_test_results['CLIENT']['recv_data'],
        )):
            logger.error(f"==== ----------------------------------------------------------------- ====")
            logger.info(f"==== Test OK.. Insgesamt {self._cfg.get('data_len', 0)} Bytes übertragen ====")
            logger.error(f"==== ----------------------------------------------------------------- ====")
            beep_sound(loop=2)
        else:
            logger.error(f"==== ----------------------------------------------------------------- ====")
            logger.error(f"==== Test NICHT OK !!! {self._cfg.get('data_len', 0)} Bytes übertragen ====")
            logger.error(f"==== SERVER TX-REST len={len(self.prp_test_results['SERVER']['send_data'])}")
            logger.error(f"==== SERVER RX-REST len={len(self.prp_test_results['SERVER']['recv_data'])}")
            logger.error(f"==== ----------------------------------------------------------------- ====")
            logger.error(f"==== CLIENT TX-REST len={len(self.prp_test_results['CLIENT']['send_data'])}")
            logger.error(f"==== CLIENT RX-REST len={len(self.prp_test_results['CLIENT']['recv_data'])}")
            logger.error(f"==== ----------------------------------------------------------------- ====")

            beep_sound(loop=2, beep_len=100, freq=1500)
            beep_alarm()

        logger.info(f"==== ----------------------------------------------------------------- ====")
        logger.info(f"== Cfg ==========================")
        logger.info(f"== Cfg data_len    : {self._cfg.get('data_len', 0)}")
        logger.info(f"== Cfg pac_size    : {self._cfg.get('pac_size', 128)}")
        logger.info(f"== Cfg Pac-Lost    : {self._cfg.get('random_pac_lost', 50)}")
        logger.info(f"== Cfg Data-Lost   : {self._cfg.get('random_data_lost', True)}")
        logger.info(f"== Cfg Prio        : {self._cfg.get('prio', True)}")
        logger.info(f"== Erzeugte Test Daten ==========")
        #logger.info(f"== Chunk Daten     : {chunk_data}")
        logger.info(f"== Länge Datensatz : {self._cfg.get('data_len', 0)} Bytes / {round(self._cfg.get('data_len', 0) / 1024, 2)} kB / {round(self._cfg.get('data_len', 0) / 1024 / 1024, 2)} MB")
        logger.info(f"== Anzahl Chunks   : {len(self._tx_data_Chunks_server)} Chunks")
        logger.info(f"==== ----------------------------------------------------------------- ====")
        logger.info(f"==== Client Results -------------------------------------------------------- ====")
        prz_lost = self.prp_test_results['CLIENT']['lost_bytes'] / self.prp_test_results['CLIENT']['total_bytes'] * 100
        logger.info(f"== Data TX Total : {self.prp_test_results['CLIENT']['total_bytes']} Bytes / {round(self.prp_test_results['CLIENT']['total_bytes'] / 1024, 2)} kB / {round(self.prp_test_results['CLIENT']['total_bytes'] / 1024 / 1024, 2)} MB")
        logger.info(f"== Data TX Lost  : {self.prp_test_results['CLIENT']['lost_bytes']} Bytes / {round(self.prp_test_results['CLIENT']['lost_bytes'] / 1024, 2)} kB / {round(self.prp_test_results['CLIENT']['lost_bytes'] / 1024 / 1024, 2)} MB")
        logger.info(f"== Pac TX Total  : {self.prp_test_results['CLIENT']['total_packet']} Pac")
        logger.info(f"== Pac TX Lost   : {self.prp_test_results['CLIENT']['lost_packet']} Pac")
        logger.info(f"== Lost-Rate     : {round(prz_lost, 1)} %")
        logger.info(f"==== ----------------------------------------------------------------- ====")
        logger.info(f"==== Server Results -------------------------------------------------------- ====")
        prz_lost = self.prp_test_results['SERVER']['lost_bytes'] / self.prp_test_results['SERVER']['total_bytes'] * 100
        logger.info(f"== Data TX Total : {self.prp_test_results['SERVER']['total_bytes']} Bytes / {round(self.prp_test_results['SERVER']['total_bytes'] / 1024, 2)} kB / {round(self.prp_test_results['SERVER']['total_bytes'] / 1024 / 1024, 2)} MB")
        logger.info(f"== Data TX Lost  : {self.prp_test_results['SERVER']['lost_bytes']} Bytes / {round(self.prp_test_results['SERVER']['lost_bytes'] / 1024, 2)} kB / {round(self.prp_test_results['SERVER']['lost_bytes'] / 1024 / 1024, 2)} MB")
        logger.info(f"== Pac TX Total  : {self.prp_test_results['SERVER']['total_packet']} Pac")
        logger.info(f"== Pac TX Lost   : {self.prp_test_results['SERVER']['lost_packet']} Pac")
        logger.info(f"== Lost-Rate     : {round(prz_lost, 1)} %")
        logger.info(f"==== ----------------------------------------------------------------- ====")
        #breakpoint()

    # =========================================
    def step_inj(self):
        self._inj_step_tick = not self._inj_step_tick

    def step_loop(self):
        self._step_tick = not self._step_tick

    # =========================================
    def set_random_chance(self, val: int):
        self._cfg['random_pac_lost'] = min(val, 90)
        chance = self._cfg['random_pac_lost']
        if not val:
            self._ran_cfg = [True]
            return
        chance = round(chance / 10)
        rest = 10 - chance
        cfg_list = ([False] * chance) + ([True] * rest)
        self._ran_cfg = []
        while cfg_list:
            var = random.choice(cfg_list)
            self._ran_cfg.append(var)
            cfg_list.remove(var)

    def set_time_scale(self, val: int):
        self._time_scale = int(val)

    # =========================================
    # Tasker
    def _client_tasks(self):
        while self.app_running:
            sleep_t = 4 / self._time_scale
            time.sleep(sleep_t)
            try:

                self._wait_step()       # STEP
                self._exchange_data(self.prp_client, self.prp_server)

                time.sleep(sleep_t)

                self._wait_step()  # STEP
                self.prp_client.tasker()

                if self.prp_test_results['CLIENT']['recv_data']:
                    self._check_diff()
            except Exception as ex:
                self.app_running = False
                logger.error(f"== Client Exchange-Tasker Error: {ex}")
                raise ex
            #self._cl_tasker_tick = bool(not self._cl_tasker_tick)

    def _client_prp_tasks(self):
        while self.app_running:
            sleep_t = 4 / self._time_scale
            time.sleep(sleep_t)
            try:
                self._wait_step()  # STEP
                self.prp_client.tasker()

            except Exception as ex:
                self.app_running = False
                logger.error(f"== Client PRP-Tasker Error: {ex}")
                raise ex
            self._cl_tasker_tick = bool(not self._cl_tasker_tick)

    def _server_tasks(self):
        while self.app_running:
            sleep_t = 4 / self._time_scale
            time.sleep(sleep_t)
            try:

                self._wait_step()       # STEP
                self._exchange_data(self.prp_server, self.prp_client)

                time.sleep(sleep_t)

                self._wait_step()  # STEP
                self.prp_server.tasker()

                if self.prp_test_results['SERVER']['recv_data']:
                    self._check_diff()

            except Exception as ex:
                self.app_running = False
                logger.error(f"== Server Exchange-Tasker Error: {ex}")
                raise ex
            self._se_tasker_tick = bool(not self._se_tasker_tick)

    def _server_prp_tasks(self):
        while self.app_running:
            sleep_t = 4 / self._time_scale
            time.sleep(sleep_t)
            try:
                self._wait_step()  # STEP
                self.prp_server.tasker()

            except Exception as ex:
                self.app_running = False
                logger.error(f"== Server PRP-Tasker Error: {ex}")
                raise ex
            self._se_tasker_tick = bool(not self._se_tasker_tick)

    def tasker(self):
        pass
    # =========================================
    # SERVER <exchange> CLIENT
    """
    def _flush_tx_buffers(self):
        sleep_t = 4 / self._time_scale
        time.sleep(sleep_t)
        while ((self._exchange_data(self.prp_client, self.prp_server) or
               self._exchange_data(self.prp_server, self.prp_client)) and self.app_running):
            time.sleep(sleep_t)
    """

    def _exchange_data(self, sender: PRPremote, receiver: PRPremote):
        uid_sender   = sender.uid
        uid_receiver = receiver.uid

        tx_buff: list = sender.prp_tx_buffer.get_TEST_payload_fm_tx_buffer()  # Alle Frames
        tx_buff_len = len(tx_buff)
        if not tx_buff_len:
            return False
        beep_sound(beep_len=1, freq=1200)
        total_pac_c  = 0
        pac_los_c    = 0
        total_data_c = 0
        data_los_c   = 0

        for opt_id, prp_pack in tx_buff:
            pack_len = len(prp_pack)
            self.prp_test_results[uid_receiver]['total_bytes']  += pack_len
            self.prp_test_results[uid_receiver]['total_packet'] += 1
            total_data_c += pack_len
            total_pac_c  += 1
            # Entscheidung: Wird das Paket zugestellt?
            if self._get_random_choice():
                self.prp_test_results[uid_receiver]['recv_data'] += simulate_rx(receiver, prp_pack)
                continue

            beep_sound(beep_len=1, freq=2400)
            self.prp_test_results[uid_receiver]['lost_bytes']  += pack_len
            self.prp_test_results[uid_receiver]['lost_packet'] += 1
            data_los_c += pack_len
            pac_los_c  += 1

        zugestellt_b = total_data_c - data_los_c
        zugestellt_p = total_pac_c  - pac_los_c

        logger.info(f"==================== Flushing TX Buffer ====================")
        #logger.info(f"== RX --- [{uid_sender}] → [{uid_receiver}]: {total_data_c} Bytes / {total_pac_c} Packets")
        logger.info(f"== RX →→→ [{uid_sender}] → [{uid_receiver}]: {zugestellt_b} Bytes / {zugestellt_p} Packets (zugestellt)")
        logger.info(f"== RX XXX [{uid_sender}] → [{uid_receiver}]: {data_los_c} Bytes / {pac_los_c} Packets (PAKETVERLUST simuliert)")
        logger.info(f"============================================================")

        return True

    # =========================================
    # Loop CTRL
    def _wait_step(self):
        if not self.stepper:
            return
        wait_tick = not bool(self._step_tick)
        while wait_tick != self._step_tick and self.app_running:
            time.sleep(0.3)

    def _wait_injection_step(self):
        if not self.inj_stepper:
            return
        wait_tick = not bool(self._inj_step_tick)
        while wait_tick != self._inj_step_tick and self.app_running:
            time.sleep(0.3)

    # =========================================
    # Helfer
    def _get_random_choice(self):
        deliver = True
        if self._cfg.get('random_pac_lost', 0):
            deliver = random.choice(self._ran_cfg)
        return deliver

    def _get_tx_cache_len(self, prp_remote: PRPremote):
        return prp_remote.prp_transport.get_tx_cache_len(self._cfg.get('prio', True))

    # =========================================
    def _inject_data_chunk(self, data, sender: PRPremote):
        logger.info(f"== TX → [{sender.uid}]: Len={len(data)} Bytes")
        sender.prp_tx_reliable(opt_id=PRP_OPT_ESC_CLI,
                               tx_flag=True,
                               data=data,
                               prio=self._cfg.get('prio', True),
                               pac_size=self._cfg.get('pac_size', 128))

    def _is_tx_cache_free(self, prp_remote: PRPremote):
        return self._get_tx_cache_len(prp_remote) < self._tx_cache_free_limit

    # =========================================
    def _check_diff(self):
        # .....
        """
        logger.info(f"== Client > {round(len(self._client_send_data)/1024/1024,2)} MB / {round(self._cfg.get('data_len', 0)/1024/1024, 2)} MB")
        logger.info(f"== Client > {len(self._client_recv_data)} Bytes RX")
        new_prz = round(len(self._client_send_data) / self._cfg.get('data_len', 0) * 100, 1)
        pr_ten = round(new_prz / 10)
        pr_rest = 10 - pr_ten
        bar = f"{'#' * pr_ten}{'.' * pr_rest}"

        logger.info(f"== Client > [{bar}] {new_prz} %")
        logger.info(f"== Server > {round(len(self._server_send_data)/1024/1024,2)} MB / {round(self._cfg.get('data_len', 0)/1024/1024, 2)} MB")
        logger.info(f"== Server > {len(self._server_recv_data)} Bytes RX")
        new_prz = round(len(self._server_send_data) / self._cfg.get('data_len', 0) * 100, 1)
        pr_ten = round(new_prz / 10)
        pr_rest = 10 - pr_ten
        bar = f"{'#' * pr_ten}{'.' * pr_rest}"
        logger.info(f"== Server > [{bar}] {new_prz} %")
        """
        #while self._server_recv_data:
        i = len(self.prp_test_results['SERVER']['recv_data'])
        if self.prp_test_results['SERVER']['recv_data'] != self.prp_test_results['CLIENT']['send_data'][:i]:
            logger.error("=== [SERVER] Diff Found: I ")
            beep_alarm()
            raise ValueError

        self.prp_test_results['SERVER']['recv_data'].clear()
        self.prp_test_results['CLIENT']['send_data'] = self.prp_test_results['CLIENT']['send_data'][i:]


        i = len(self.prp_test_results['CLIENT']['recv_data'])

        if self.prp_test_results['CLIENT']['recv_data'] != self.prp_test_results['SERVER']['send_data'][:i]:
            logger.error(f"=== [CLIENT] Diff Found: I ")
            beep_alarm()
            raise ValueError

        self.prp_test_results['CLIENT']['recv_data'].clear()
        self.prp_test_results['SERVER']['send_data'] = self.prp_test_results['SERVER']['send_data'][i:]

    # =============== MAIN =====================
    def run_main(self):
        # Senden der Chunks
        data_set_client = list(self._tx_data_Chunks_client)
        data_set_server = list(self._tx_data_Chunks_server)
        #breakpoint()
        idx_c = 0
        idx_s = 0
        while self.app_running and (data_set_server or data_set_client):

            # ===============================================
            # Client > Server
            # ===============================================
            time.sleep(40 / self._time_scale)
            self._wait_step()
            self._wait_injection_step()

            # == TX Buffer frei?
            if self._is_tx_cache_free(self.prp_client) and data_set_client:
                idx_c += 1
                data_to_send = data_set_client.pop(0)
                logger.debug(f"== [Client] Sende Chunk {idx_c}/{len(self._tx_data_Chunks_server)}")
                logger.debug(f"== [Client]: {len(data_to_send)} Bytes")
                beep_sound(beep_len=3)

                # == Inject Data
                self._inject_data_chunk(data_to_send, self.prp_client)


            # == Warte Tasker Tick
            #time.sleep(4 / self._time_scale)
            #tasker_tick = bool(self._cl_tasker_tick)
            #while tasker_tick == self._cl_tasker_tick and self.app_running:
            #    time.sleep(0.001)

            # ===============================================
            # Client > Server
            # ===============================================
            self._wait_injection_step()

            # == TX Buffer frei?
            if self._is_tx_cache_free(self.prp_server) and data_set_server:
                idx_s += 1
                data_to_send = data_set_server.pop(0)
                logger.debug(f"== Sende Chunk {idx_s}/{len(self._tx_data_Chunks_server)}")
                logger.debug(f"== Server: {len(data_to_send)} Bytes")
                beep_sound(beep_len=3)

                # == Inject Data
                self._inject_data_chunk(data_to_send, self.prp_server)

            # == Warte Tasker Tick
            #time.sleep(4 / self._time_scale)
            #tasker_tick = bool(self._se_tasker_tick)
            #while tasker_tick == self._se_tasker_tick and self.app_running:
            #    time.sleep(0.001)

        logger.info("==== Test ENDE ===================")
        beep_sound(beep_len=500, freq=1900)

        logger.info("==== Übertrage Reste")
        time.sleep(2)
        # self._flush_tx_buffers()
        if any(self.prp_client.prp_transport.get_all_pending()) or any(self.prp_server.prp_transport.get_all_pending()):
            logger.info("== Verarbeite pending ..")
            logger.info(f"Pending Client: {self.prp_client.prp_transport.get_all_pending()}")
            logger.info(f"Pending Server: {self.prp_server.prp_transport.get_all_pending()}")
            #i   = 0
            #w_n = 0
            """
            while any(self.prp_client.prp_transport.get_all_pending()) or any(self.prp_server.prp_transport.get_all_pending()):
                beep_sound(beep_len=1,loop=2)
                time.sleep(1)
                if i < 10:
                    i += 1
                    continue
                i    = 0
                w_n += 1
                logger.info(f"== Verarbeite pending ..{'.' * w_n}")
                logger.info(f"Pending Client: {self.prp_client.prp_transport.get_all_pending()}")
                logger.info(f"Pending Server: {self.prp_server.prp_transport.get_all_pending()}")
            """

        logger.info("======== Test abgeschlossen ========")
        logger.info(f"Pending Client: {self.prp_client.prp_transport.get_all_pending()}")
        logger.info(f"Pending Server: {self.prp_server.prp_transport.get_all_pending()}")

        logger.info("======== Checking Diff .....")
        self._check_diff()
        beep_sound(beep_len=500,loop=2)

        for _ in range(3):
            beep_sound(beep_len=50, freq=1900)
            time.sleep(1)

        beep_sound(beep_len=500, freq=1900)
        #input("Warte .......................")
        self.close_app()

    """
    def send_to_server(self, data_len: int,
                       random_pac_lost=True,
                       random_data_lost=True,
                       pac_size=128,
                       prio=True):
        logger.info(f"TX → [{self._client.uid} → {self._server.uid}]: "
                    f"data_len={data_len} Bytes - "
                    f"random_pac_lost={random_pac_lost}, random_data_lost={random_data_lost} - "
                    f"pac_size={pac_size} - prio={prio}")

        chunk_data = b'0123456789'  # 10 Bytes pro Chunk-Basis

        data = chunk_data * int(data_len / 10)
        data_to_send = []
        while data:
            ran_len = random.randint(30, 1000)
            tmp = data[:ran_len]
            data = data[len(tmp):]
            data_to_send.append(tmp)


        send = []
        not_send = []
        # Senden der Chunks
        for idx, data in enumerate(data_to_send, 1):

            logger.debug(f"Sende Chunk {idx}/{len(data_to_send)} – {len(data)} Bytes")

            tx_buffer, seq_list = send_and_get_l3_pack(
                self._client, PRP_OPT_ESC_CLI, data, prio, pac_size=pac_size
            )

            # Entscheidung: Wird das Paket zugestellt?
            deliver = True
            if random_pac_lost:
                deliver = random.choice([True, False])  # 50% Chance auf Verlust

            if deliver:
                if isinstance(seq_list, list):
                    send += seq_list
                simulate_rx(self._server, tx_buffer)


            else:
                if isinstance(seq_list, list):
                    not_send += seq_list
                #async_chunks.append()

            time.sleep(0.5)
            self.tasker()
            # Empfange ACK/NACK vom Server
            response_cl = self._client.prp_tx_buffer.get_payload_fm_tx_buffer(100000)
            response_se = self._server.prp_tx_buffer.get_payload_fm_tx_buffer(100000)
            while response_cl or response_se:
                if response_cl:
                    simulate_rx(self._server, response_cl)
                if response_se:
                    simulate_rx(self._client, response_se)
                time.sleep(0.5)
                self.tasker()

                response_cl = self._client.prp_tx_buffer.get_payload_fm_tx_buffer(10000)
                response_se = self._server.prp_tx_buffer.get_payload_fm_tx_buffer(10000)

        logger.info(f"RX → [{self._server.uid}]: Seq-List {send} (zugestellt)")
        logger.warning(f"RX →X [{self._server.uid}]: Seq-List {not_send} (PAKETVERLUST simuliert)")

        logger.info("Übertrage Reste")
        time.sleep(2)
        self.tasker()
        response_cl = self._client.prp_tx_buffer.get_payload_fm_tx_buffer(100000)
        response_se = self._server.prp_tx_buffer.get_payload_fm_tx_buffer(100000)
        while response_cl or response_se:
            if response_cl:
                simulate_rx(self._server, response_cl)
            if response_se:
                simulate_rx(self._client, response_se)
            time.sleep(2)
            self.tasker()
            response_cl = self._client.prp_tx_buffer.get_payload_fm_tx_buffer(10000)
            response_se = self._server.prp_tx_buffer.get_payload_fm_tx_buffer(10000)

        logger.info("======== send_to_server abgeschlossen ========")
        logger.info(f"Pending Client: {self._client.prp_transport.get_all_pending()}")
        logger.info(f"Pending Server: {self._server.prp_transport.get_all_pending()}")
        time.sleep(10)
    """
# =========================================================================
# =========================================================================


# Main
if __name__ == '__main__':
    logger.info("=== PRP L3 Erweiterter Test Start ===")
    #server = init_prpTester(True)
    #client = init_prpTester(False)
    sim = None
    n = 0
    data_len_sum = 0
    try:
        #while n < 100:
        while True:
            data_size = random.randrange(3048576, 9242880)
            if data_size % 2:
                data_size += 1
            pac_los = min(n * 10, 90)
            sim = Simulator(data_len=data_size,
                               random_pac_lost=pac_los,      # 0, 25, 50, 75
                               random_data_lost=False,
                               pac_size=129,
                               prio=True)

            sim.start_app()
            n += 1
            logger.info(f"=== Test {n} Ende ..  {round(data_size/1024, 1)} kB übertragen ===")
            data_len_sum += data_size
            time.sleep(0.5)

    except KeyboardInterrupt:
        if hasattr(sim, 'close_app'):
            sim.close_app()
        logger.info("=== Test Abgebrochen bei User ===")
    logger.info(f"=== {n} Test durchläufe  ..  ===")
    logger.info(f"=== {round(data_len_sum/1024, 1)} kB insgesamt übertragen ===")
    logger.info("=== Alle Tests abgeschlossen! ===")
