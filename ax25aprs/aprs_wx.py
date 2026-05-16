from ax25aprs.aprs_dec import parse_aprs_fm_aprsframe
from cfg.logger_config import logger


class APRSwx:
    def __init__(self, aprs_main, port_handler):
        logger.info("APRS-WX: Init")
        self._aprs_main     = aprs_main
        self._port_handler  = port_handler

        self._wx_update_tr = False

    # =========================
    def aprs_wx_msg_rx(self, aprs_pack):
        if not aprs_pack.get("weather", False):
            return False
        new_aprs_pack = self._correct_wrong_wx_data(aprs_pack)
        from_aprs = new_aprs_pack.get('from', '')
        if from_aprs:
            ########
            # db
            db = self._get_db()
            if db:
                db.aprsWX_insert_data(new_aprs_pack)

            user_db = self._get_userDB()
            user_db.set_typ(aprs_pack.get('from', ''), 'APRS-WX')

            self._wx_update_tr = True
            return True
        return False

    @staticmethod
    def _correct_wrong_wx_data(aprs_pack):
        raw = aprs_pack.get('raw', '')
        if raw:
            if 'h100b' in raw or 'b9' in raw:
                raw = raw.replace('h100b', 'h00b').replace('b9', 'b09')
                new_pack = parse_aprs_fm_aprsframe(raw)
                new_pack['locator'] = str(aprs_pack.get('locator', ''))
                new_pack['distance'] = float(aprs_pack.get('distance', -1))
                new_pack['port_id'] = str(aprs_pack.get('port_id', ''))
                new_pack['rx_time'] = aprs_pack['rx_time']
                return new_pack
        return aprs_pack

    def get_wx_data(self, last_rx_days=1):
        db = self._get_db()
        if not db:
            return []
        return list(db.aprsWX_get_data_f_wxTree(last_rx_days=last_rx_days))
        # return dict(self.aprs_wx_msg_pool)

    def get_wx_data_f_call(self, call: str):
        db = self._get_db()
        if not db:
            return []
        return list(db.aprsWX_get_data_f_call(call))

    def delete_wx_data(self):
        db = self._get_db()
        if db:
            db.aprsWX_delete_data()

    def get_update_tr(self):
        if not self._wx_update_tr:
            return False
        self._wx_update_tr = False
        return True

    ######################################
    def _get_userDB(self):
        try:
            return self._port_handler.get_userDB()
        except Exception as ex:
            logger.error(ex)
            return None

    def _get_db(self):
        return self._port_handler.get_database()

