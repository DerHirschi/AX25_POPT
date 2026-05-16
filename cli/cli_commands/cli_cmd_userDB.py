from cfg.logger_config import logger
from cli.cli_modulBase import CliModulBase
from fnc.str_fnc import zeilenumbruch, conv_time_DE_str


class CliCmdUserDB(CliModulBase):
    def __init__(self, cli_main):
        super().__init__(cli_main=cli_main)

    # ============================================
    # USER
    def cmd_user_db_detail(self):
        if not self._parameter:
            # max_lines = 20  # TODO: from parameter
            db_list = list(self._user_db.db.keys())
            header = "\r" \
                     f" USER-DB - {len(db_list)} Calls\r" \
                     "-------------------------------------------------------------------------------\r"
            ent_ret = ""
            db_list.sort()
            # c = 0
            # colum_c = 0
            for call in db_list:
                ent_ret += f"{call} "
                """
                colum_c += 1
                if colum_c > 6:
                    ent_ret += "\r"
                    colum_c = 0
                    c += 1
                """
                """
                if c >= max_lines:
                    break
                """
            ent_ret = zeilenumbruch(ent_ret)
            ent_ret += "\r-------------------------------------------------------------------------------\r\r"
            return header + ent_ret

        # -------
        call_str = self._parameter[0].decode(self._get_encoding()[0], self._get_encoding()[1]).upper()
        db_ent = self._user_db.get_entry(call_str, add_new=False)
        if db_ent:
            header = "\r" \
                     f"| USER-DB: {call_str}\r" \
                     "|-------------------\r"
            ent = db_ent
            ent_ret = ""
            for att in dir(ent):
                if '__' not in att and \
                        att not in self._user_db.not_public_vars:
                    if getattr(ent, att):
                        ent_ret += f"| {att.ljust(10)}: {getattr(ent, att)}\r"
            ent_ret += "|-------------------\r\r"
            return header + ent_ret

        return "\r" \
               f"{self._getTabStr_CLI('cli_no_user_db_ent')}" \
               "\r"

    # ============================================
    # NAME & STR CMD
    def cmd_set_name(self):
        if not self._parameter:
            if self._user_db_ent:
                return f" #\r Name: {self._user_db_ent.Name}\r"
            return "\r # USER-DB Error !\r"
        if self._user_db_ent:
            self._user_db_ent.Name = self._parameter[0] \
                .decode(self._get_encoding()[0], self._get_encoding()[1]). \
                replace(' ', ''). \
                replace('\n', ''). \
                replace('\r', '')
            self._user_db_ent.last_edit = conv_time_DE_str()
            return "\r" \
                   f"{self._getTabStr_CLI('cli_name_set')}: {self._user_db_ent.Name}" \
                   "\r"

        logger.error("User-DB Error. cmd_set_name NO ENTRY FOUND !")
        return "\r # USER-DB Error !\r"

    # ============================================
    # QTH  & STR CMD
    def cmd_set_qth(self):
        if not self._parameter:
            if self._user_db_ent:
                return f"\r # QTH: {self._user_db_ent.QTH}\r"
            return "\r # USER-DB Error !\r"
        if self._user_db_ent:
            self._user_db_ent.QTH = self._parameter[0] \
                .decode(self._get_encoding()[0], self._get_encoding()[1]). \
                replace(' ', ''). \
                replace('\n', ''). \
                replace('\r', '')
            self._user_db_ent.last_edit = conv_time_DE_str()
            return "\r" \
                   f"{self._getTabStr_CLI('cli_qth_set')}: {self._user_db_ent.QTH}" \
                   "\r"

        logger.error("User-DB Error. cli_qth_set NO ENTRY FOUND !")
        return "\r # USER-DB Error !\r"

    # ============================================
    # LOC  & STR CMD
    def cmd_set_loc(self):
        if not self._parameter:
            if self._user_db_ent:
                if self._user_db_ent.Distance:
                    return f"\r # Locator: {self._user_db_ent.LOC} > {round(self._user_db_ent.Distance)} km\r"
                return f"\r # Locator: {self._user_db_ent.LOC}\r"
            return "\r # USER-DB Error !\r"
        if self._user_db_ent:
            self._user_db_ent.LOC = self._parameter[0] \
                .decode(self._get_encoding()[0], self._get_encoding()[1]). \
                replace(' ', ''). \
                replace('\n', ''). \
                replace('\r', '')
            self._user_db_ent.last_edit = conv_time_DE_str()
            # self._connection.set_distance()
            self._user_db.set_distance(self._user_db_ent.call_str)
            if self._user_db_ent.Distance:
                return "\r" \
                       f"{self._getTabStr_CLI('cli_loc_set')}: {self._user_db_ent.LOC}" \
                       "\r"
            return "\r" \
                   f"{self._getTabStr_CLI('cli_loc_set')}: {self._user_db_ent.LOC} > {round(self._user_db_ent.Distance)} km" \
                   "\r"

        logger.error("User-DB Error. cmd_set_loc NO ENTRY FOUND !")
        return "\r # USER-DB Error !\r"

    # ============================================
    # ZIP
    def cmd_set_zip(self):
        if not self._parameter:
            if self._user_db_ent:
                return f"\r # ZIP: {self._user_db_ent.ZIP}\r"
            return "\r # USER-DB Error !\r"
        if self._user_db_ent:
            self._user_db_ent.ZIP = self._parameter[0] \
                .decode(self._get_encoding()[0], self._get_encoding()[1]). \
                replace(' ', ''). \
                replace('\n', ''). \
                replace('\r', '')
            self._user_db_ent.last_edit = conv_time_DE_str()
            return "\r" \
                   f"{self._getTabStr_CLI('cli_zip_set')}: {self._user_db_ent.ZIP}" \
                   "\r"

        logger.error("User-DB Error. cmd_set_zip NO ENTRY FOUND !")
        return "\r # USER-DB Error !\r"

    # ============================================
    # PRMAIL
    def cmd_set_pr_mail(self):
        if not self._parameter:
            if self._user_db_ent:
                return f"\r # PR-Mail: {self._user_db_ent.PRmail}\r"
            return "\r # USER-DB Error !\r"
        if self._user_db_ent:
            self._user_db_ent.PRmail = (self._parameter[0]
                .decode(self._get_encoding()[0], self._get_encoding()[1])
                                        .replace(' ', '')
                                        .replace('\n', '')
                                        .replace('\r', '')).upper()
            self._user_db_ent.last_edit = conv_time_DE_str()
            return "\r" \
                   f"{self._getTabStr_CLI('cli_prmail_set')}: {self._user_db_ent.PRmail}" \
                   "\r"

        logger.error("User-DB Error. cmd_set_pr_mail NO ENTRY FOUND !")
        return "\r # USER-DB Error !\r"

    # ============================================
    # EMAIL
    def cmd_set_e_mail(self):
        if not self._parameter:
            if self._user_db_ent:
                return f"\r # E-Mail: {self._user_db_ent.Email}\r"
            return "\r # USER-DB Error !\r"
        if self._user_db_ent:
            self._user_db_ent.Email = self._parameter[0] \
                .decode(self._get_encoding()[0], self._get_encoding()[1]). \
                replace(' ', ''). \
                replace('\n', ''). \
                replace('\r', '')
            self._user_db_ent.last_edit = conv_time_DE_str()
            return "\r" \
                   f"{self._getTabStr_CLI('cli_email_set')}: {self._user_db_ent.Email}" \
                   "\r"

        logger.error("User-DB Error. cmd_set_e_mail NO ENTRY FOUND !")
        return "\r # USER-DB Error !\r"

    # ============================================
    # WEB
    def cmd_set_http(self):
        if not self._parameter:
            if self._user_db_ent:
                return f"\r # WEB: {self._user_db_ent.HTTP}\r"
            return "\r # USER-DB Error !\r"
        if self._user_db_ent:
            self._user_db_ent.HTTP = self._parameter[0] \
                .decode(self._get_encoding()[0], self._get_encoding()[1]). \
                replace(' ', ''). \
                replace('\n', ''). \
                replace('\r', '')
            self._user_db_ent.last_edit = conv_time_DE_str()
            return "\r" \
                   f"{self._getTabStr_CLI('cli_http_set')}: {self._user_db_ent.HTTP}" \
                   "\r"

        logger.error("User-DB Error. cmd_set_http NO ENTRY FOUND !")
        return "\r # USER-DB Error !\r"

