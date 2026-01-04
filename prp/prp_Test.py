# ============================================================
# PRP L3 Test App – vollständiger Bidirektionaler Test
# ============================================================
import random
import time

from cfg.logger_config import logger
from prp.prp_remote import PRPremote
from prp.prp_const import PRP_OPT_ESC_CLI



# Mocks
class PseudoGUI:
    def init_popt_remote(self, var1): pass

class PseudoPortHandler:
    def handle_prp_response(self, var1, var2):
        logger.info(f"Mock: handle_prp_response({var1}, {var2})")
    def get_gui(self): return PseudoGUI()
    def get_config_value(self): return None
    def handle_remote_monitor_rx(self, var1, var2): pass

def init_prpTester(is_server: bool):
    ph = PseudoPortHandler()
    uid = 'SERVER' if is_server else 'CLIENT'
    config = {
        'uid': uid,
        'remote_uid': 'CLIENT' if is_server else 'SERVER',
        'to_call_str': uid,
        'conn_typ': 'ax25_l2'
    }
    return PRPremote(ph, config)

# Simuliere Empfang
def simulate_rx(instance, raw_data):
    logger.info(f"RX → [{instance.uid}]: raw_data Len={len(raw_data)}")
    non_prp_data = instance.prp_rx(raw_data)
    if non_prp_data:
        logger.info(f"RX → [{instance.uid}] - Non PRP-DATA: Len={len(non_prp_data)} - Data: {non_prp_data}")


# Seq-Zähler setzen, um Fehler zu provozieren
def set_seq_counter(instance1, instance2, seq_nr: int, prio=True):
    instance1.prp_transport.set_current_seq(instance2.uid, prio, seq_nr)


# Sende und liefere Frame an Empfänger
def send_and_get_l3_pack(sender, orig_opt_id, data, prio=True, pac_size=128):
    logger.info(f"TX → [{sender.uid}]: Sende ORIG-OPT={orig_opt_id}, Len={len(data)} Bytes")
    seq_list = sender.prp_tx_reliable(opt_id=orig_opt_id,
                                      tx_flag=True,
                                      data=data,
                                      prio=prio,
                                      pac_size=pac_size)

    logger.info(f"  TX → SEQ-List: {seq_list}")
    # Alle L3-Frames aus TX-Buffer holen zurückgeben
    return sender.prp_tx_buffer.get_payload_fm_tx_buffer(1000000), seq_list  # Alle Frames


# Sende und liefere Frame an Empfänger
def send_and_deliver(sender, receiver, orig_opt_id, data, prio=True):
    logger.info(f"TX → [{sender.uid}]: Sende ORIG-OPT={orig_opt_id}, Len={len(data)} Bytes")
    seq_list = sender.prp_tx_reliable(opt_id=orig_opt_id, tx_flag=True, data=data, prio=prio)
    logger.info(f"  SEQ-List: {seq_list}")

    # Alle L3-Frames aus TX-Buffer holen und an Empfänger liefern
    raw_data = sender.prp_tx_buffer.get_payload_fm_tx_buffer(100000)  # Alle Frames
    #for frame in frames:
    simulate_rx(receiver, raw_data)

    # Response to Server
    # Alle L3-Frames aus TX-Buffer holen und an Empfänger liefern
    raw_data = receiver.prp_tx_buffer.get_payload_fm_tx_buffer(10000)  # Alle Frames
    # for frame in frames:
    simulate_rx(sender, raw_data)

# =========================================================================
# =========================================================================
# =========================================================================
# =========================================================================
class Simulator:
    def __init__(self, prp_server: PRPremote, prp_client: PRPremote):
        self._server = prp_server
        self._client = prp_client

        self._server_tx_buff = bytearray()
        self._client_tx_buff = bytearray()

    def tasker(self):
        self._client.tasker()
        self._server.tasker()

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

            time.sleep(1)
            self.tasker()
            # Empfange ACK/NACK vom Server
            response_cl = self._client.prp_tx_buffer.get_payload_fm_tx_buffer(100000)
            response_se = self._server.prp_tx_buffer.get_payload_fm_tx_buffer(100000)
            while response_cl or response_se:
                if response_cl:
                    simulate_rx(self._server, response_cl)
                if response_se:
                    simulate_rx(self._client, response_se)
                time.sleep(1)
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
# =========================================================================
# =========================================================================
# Test 1: Einfaches Paket
def test_simple(server, client):
    logger.info("\n=== Test 1: Einfaches Paket + ACK ===")
    send_and_deliver(client, server, PRP_OPT_ESC_CLI, b'hello world')

# Test 2: Fragmentierung
def test_fragmentation(server, client):
    logger.info("\n=== Test 2: Fragmentierung ===")
    big_data = b'X' * 1000
    send_and_deliver(client, server, PRP_OPT_ESC_CLI, big_data)

# Test 3: Reordering
def test_reordering(server, client):
    logger.info("\n=== Test 3: Reordering ===")
    # Seq 2 zuerst
    send_and_deliver(client, server, PRP_OPT_ESC_CLI, b'packet2')
    # Seq 1 danach
    send_and_deliver(client, server, PRP_OPT_ESC_CLI, b'packet1')

# Test 4: Verlust + Retry
def test_loss_retry(server, client):
    logger.info("\n=== Test 4: Verlust + NACK + Retry ===")
    # Sende packet1
    send_and_deliver(client, server, PRP_OPT_ESC_CLI, b'packet1')
    # Sende packet3 (packet2 fehlt)
    send_and_deliver(client, server, PRP_OPT_ESC_CLI, b'packet3')
    # Server hat Lücke → sendet NACK → Client retry packet2

# Test 5: Reordering – alle Frames kommen an, aber falsch gereiht
def test_reordering_full(server, client):
    logger.info("\n=== Test 5: Reordering – alle Pakete ankommen, aber falsch gereiht ===")
    # Sende in falscher Reihenfolge
    send_and_deliver(client, server, PRP_OPT_ESC_CLI, b'packet3')
    send_and_deliver(client, server, PRP_OPT_ESC_CLI, b'packet1')
    send_and_deliver(client, server, PRP_OPT_ESC_CLI, b'packet2')
    # Server sollte puffern → NACK → Client retry → dann ACK + Rekonstruktion

# Test 6: Große Daten + Async Reordering
def test_large_async_reordering(server, client):
    logger.info("\n=== Test 6: Große Daten + Async Reordering ===")
    large_data1 = b'A' * 5000  # 5KB
    large_data2 = b'B' * 6000  # 6KB
    large_data3 = b'C' * 7000  # 7KB

    # Async falsch gereiht senden
    send_and_deliver(client, server, PRP_OPT_ESC_CLI, large_data3)
    send_and_deliver(client, server, PRP_OPT_ESC_CLI, large_data1)
    send_and_deliver(client, server, PRP_OPT_ESC_CLI, large_data2)
    # Erwarte Puffer, NACK, Retry, Rekonstruktion

# Test 7: SEQ-Korruption
def test_seq_corruption(server, client):
    logger.info("\n=== Test 7: SEQ-Korruption (out-of-order) ===")
    send_and_deliver(client, server, PRP_OPT_ESC_CLI, b'test corruption')

# Test 8: Große Bitmask (viele Lücken)
def test_large_bitmask(server, client):
    logger.info("\n=== Test 8: Große Bitmask (viele Lücken) ===")
    for i in range(0, 100, 2):  # Gerade SEQ → Lücken bei ungeraden
        send_and_deliver(client, server, PRP_OPT_ESC_CLI, f'packet{i}'.encode())
    # Erwarte NACK mit len >1 (z.B. len=13 für 100 SEQ)

# Test 9: Massive Daten (10KB+, multiple)
def test_massive_data(server, client):
    logger.info("\n=== Test 9: Massive Daten (10KB+, multiple) ===")
    massive_data = b'M' * 10000  # 10KB
    for _ in range(3):  # 3x send
        send_and_deliver(client, server, PRP_OPT_ESC_CLI, massive_data)

# Test 10: Bitmask + Reordering + Lücken
def test_bitmask_reordering(server, client):
    logger.info("\n=== Test 10: Bitmask + Reordering + Lücken ===")
    seqs = [1, 3, 1, 5, 2, 7, 4, 9, 6, 8, 10]  # Falsch + Lücken simuliert
    for s in seqs:
        set_seq_counter(client, server, s)
        send_and_deliver(client, server, PRP_OPT_ESC_CLI, f'packet{s}'.encode())
    send_and_deliver(client, server, PRP_OPT_ESC_CLI, f'packet - LAST PACK !!!'.encode())
    send_and_deliver(client, server, PRP_OPT_ESC_CLI, f'packet - LAST PACK 2 !!!'.encode())


# ==================================================
# Neuer Test: Extreme Bitmask (bis 20+ Bytes)
# ==================================================
def test_extreme_bitmask(server, client):
    logger.info("\n=== Test EXTREME: Große Bitmask (bis 20+ Bytes) + chaotisches Reordering ===")

    # Starte bei SEQ 10, um Platz für viele Lücken zu haben
    base_seq = 10
    max_seq = base_seq + 160  # Ziel: ca. 160 Pakete → Bitmask ca. 20 Bytes (160 bits)

    # Erzeuge eine zufällige, stark durcheinandergewürfelte Reihenfolge
    seq_numbers = list(range(base_seq, max_seq))
    random.shuffle(seq_numbers)

    # Nur jedes 2. oder 3. Paket senden → viele Lücken
    # Wir senden nur ~70% der Pakete, um große Lücken zu erzeugen
    send_seqs = seq_numbers[:len(seq_numbers) // 3 * 2]  # ca. 66%
    send_seqs.sort()  # Sortiert, damit wir sehen, wie viele fehlen

    logger.info(f"Sende {len(send_seqs)} Pakete von SEQ {base_seq} bis {max_seq - 1} (in chaotischer Reihenfolge)")
    logger.info(f"Erwartete max. Bitmask-Länge: ~{(max_seq - base_seq) // 8} Bytes")

    # Chaos: Sende in völlig falscher Reihenfolge
    random.shuffle(send_seqs)

    for seq in send_seqs:
        set_seq_counter(client, server, seq)
        data = f'CHAOS-PACKET-{seq:03d}'.encode('utf-8')
        send_and_deliver(client, server, PRP_OPT_ESC_CLI, data)

    logger.info("=== Chaos-Phase abgeschlossen – warte auf NACKs und Retransmits ===")

    # Abschluss: Sende ein paar große finale Pakete
    final_seqs = [max_seq, max_seq + 5, max_seq + 10]
    for seq in final_seqs:
        set_seq_counter(client, server, seq)
        send_and_deliver(client, server, PRP_OPT_ESC_CLI, f'FINAL - BIG PACKET {seq}'.encode())

    logger.info("=== Extrem-Test abgeschlossen ===")


# ==================================================
# Optional: Noch größer – 256+ SEQ (Wrap-around testen)
# ==================================================
def test_wrap_around_bitmask(server, client):
    logger.info("\n=== Test WRAP: Bitmask mit SEQ-Wrap-around (über 255) ===")

    # Starte kurz vor dem Wrap
    seqs = [250, 252, 254, 0, 2, 5, 10, 15, 20]  # Mischung vor/nach 255
    random.shuffle(seqs)

    for seq in seqs:
        set_seq_counter(client, server, seq)
        send_and_deliver(client, server, PRP_OPT_ESC_CLI, f'WRAP-PACKET-{seq}'.encode())

    logger.info("=== Wrap-around Test abgeschlossen ===")

# Main
if __name__ == '__main__':
    logger.info("=== PRP L3 Erweiterter Test Start ===")
    #server = init_prpTester(True)
    #client = init_prpTester(False)

    # test_simple(server, client)
    # test_fragmentation(server, client)
    # test_reordering(server, client)
    # test_loss_retry(server, client)
    # test_reordering_full(server, client)
    # test_large_async_reordering(server, client)
    # test_seq_corruption(server, client)
    # test_large_bitmask(server, client)
    # test_massive_data(server, client)
    # test_bitmask_reordering(server, client)
    # test_extreme_bitmask(server, client)
    # test_wrap_around_bitmask(server, client)
    n = 0
    try:
        #while n < 100:
        while True:
            server = init_prpTester(True)
            client = init_prpTester(False)

            sim = Simulator(server, client)
            data_size = random.randrange(3000, 500000)
            sim.send_to_server(data_len=data_size,
                               random_pac_lost=True,
                               random_data_lost=False,
                               pac_size=129,
                               prio=True)
            n += 1
            logger.info(f"=== Test {n} Ende ..  ===")

            time.sleep(0.5)

    except KeyboardInterrupt:
        logger.info("=== Test Abgebrochen bei User ===")

    logger.info("=== Alle Tests abgeschlossen! ===")
