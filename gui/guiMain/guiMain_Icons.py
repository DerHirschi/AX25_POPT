from cfg.constant import CFG_gui_icon_path, CFG_aprs_icon_path, CFG_gui_conn_hist_path, CLI_TYP_SYSOP, CLI_TYP_NODE, \
    CLI_TYP_DIGI, CLI_TYP_PIPE, CLI_TYP_BOX, CLI_TYP_TASK_FWD, CLI_TYP_CONVERSE, CLI_TYP_NO_CLI
from cfg.logger_config import logger
from fnc.gui_fnc import build_aprs_icon_tab, get_image


class GuiIcons:
    def __init__(self):
        logger.info("GuiIcons: Init APRS-Icon Tab 16x16")
        self.aprs_icon_tab_16 = build_aprs_icon_tab((16, 16))
        logger.info("GuiIcons: Init APRS-Icon Tab 24x24")
        self.aprs_icon_tab_24 = build_aprs_icon_tab((24, 24))
        logger.info("GuiIcons: Init APRS-Icon Tab 32x32")
        self.aprs_icon_tab_32 = build_aprs_icon_tab((32, 32))
        logger.info("GuiIcons: Init Monitor-Tree-Icon Tab 16x16 & 32x16")
        self.rx_tx_icons = {
            'rx':       get_image(CFG_gui_icon_path + '/pfeil_rechts_gruen.png', size=(16, 16)),  # RX
            'tx':       get_image(CFG_gui_icon_path + '/pfeil_links_rot.png',    size=(16, 16)),  # TX
            'rx-node':  get_image(CFG_gui_icon_path + '/node_rx.png',            size=(32, 16)),
            'tx-node':  get_image(CFG_gui_icon_path + '/node_tx.png',            size=(32, 16)),
            'rx-bbs':   get_image(CFG_gui_icon_path + '/bbs_rx.png',             size=(32, 16)),
            'tx-bbs':   get_image(CFG_gui_icon_path + '/bbs_tx.png',             size=(32, 16)),
            'rx-term':  get_image(CFG_gui_icon_path + '/term_rx.png',            size=(32, 16)),
            'tx-term':  get_image(CFG_gui_icon_path + '/term_tx.png',            size=(32, 16)),
            'rx-dx':    get_image(CFG_gui_icon_path + '/dx_rx.png',              size=(32, 16)),
            'rx-block': get_image(CFG_gui_icon_path + '/block_rx.png',           size=(32, 16)),
        }
        logger.info("GuiIcons: InitConnection-Typ-Icon Tab 16x16 & 32x16")
        self.conn_typ_icons = {
            # Connection Tab
            CLI_TYP_SYSOP:      get_image(CFG_aprs_icon_path + '/0-44.png', size=(16, 16)),
            CLI_TYP_NODE:       get_image(CFG_aprs_icon_path + '/0-78.png', size=(16, 16)),
            CLI_TYP_DIGI:       get_image(CFG_aprs_icon_path + '/0-82.png', size=(16, 16)),
            CLI_TYP_PIPE:       get_image(CFG_aprs_icon_path + '/1-26.png', size=(16, 16)),
            CLI_TYP_BOX:        get_image(CFG_aprs_icon_path + '/0-34.png', size=(16, 16)),
            CLI_TYP_TASK_FWD:   get_image(CFG_aprs_icon_path + '/0-61.png', size=(16, 16)),
            CLI_TYP_CONVERSE:   get_image(CFG_aprs_icon_path + '/1-54.png', size=(16, 16)),
            # Connection History Tab
            f'{CLI_TYP_SYSOP}-CONN-OUT':  get_image(CFG_gui_conn_hist_path + '/term_conn_out.png', size=(32, 16)),
            f'{CLI_TYP_SYSOP}-CONN-IN':   get_image(CFG_gui_conn_hist_path + '/term_conn_in.png', size=(32, 16)),
            f'{CLI_TYP_SYSOP}-DISCO-OUT': get_image(CFG_gui_conn_hist_path + '/term_disco_out.png', size=(32, 16)),
            f'{CLI_TYP_SYSOP}-DISCO-IN':  get_image(CFG_gui_conn_hist_path + '/term_disco_in.png', size=(32, 16)),

            f'{CLI_TYP_NODE}-CONN-OUT':  get_image(CFG_gui_conn_hist_path + '/node_conn_out.png', size=(32, 16)),
            f'{CLI_TYP_NODE}-CONN-IN':   get_image(CFG_gui_conn_hist_path + '/node_conn_in.png', size=(32, 16)),
            f'{CLI_TYP_NODE}-DISCO-OUT': get_image(CFG_gui_conn_hist_path + '/node_disco_out.png', size=(32, 16)),
            f'{CLI_TYP_NODE}-DISCO-IN':  get_image(CFG_gui_conn_hist_path + '/node_disco_in.png', size=(32, 16)),

            f'{CLI_TYP_DIGI}-CONN-OUT':  get_image(CFG_gui_conn_hist_path + '/digi_conn_out.png', size=(32, 16)),
            f'{CLI_TYP_DIGI}-CONN-IN':   get_image(CFG_gui_conn_hist_path + '/digi_conn_in.png', size=(32, 16)),
            f'{CLI_TYP_DIGI}-DISCO-OUT': get_image(CFG_gui_conn_hist_path + '/digi_disco_out.png', size=(32, 16)),
            f'{CLI_TYP_DIGI}-DISCO-IN':  get_image(CFG_gui_conn_hist_path + '/digi_disco_in.png', size=(32, 16)),

            f'{CLI_TYP_NO_CLI}-CONN-OUT':  get_image(CFG_gui_conn_hist_path + '/digi_conn_out.png', size=(32, 16)),
            f'{CLI_TYP_NO_CLI}-CONN-IN':   get_image(CFG_gui_conn_hist_path + '/digi_conn_in.png', size=(32, 16)),
            f'{CLI_TYP_NO_CLI}-DISCO-OUT': get_image(CFG_gui_conn_hist_path + '/digi_disco_out.png', size=(32, 16)),
            f'{CLI_TYP_NO_CLI}-DISCO-IN':  get_image(CFG_gui_conn_hist_path + '/digi_disco_in.png', size=(32, 16)),

            f'{CLI_TYP_PIPE}-CONN-OUT':  get_image(CFG_gui_conn_hist_path + '/pipe_conn_out.png', size=(32, 16)),
            f'{CLI_TYP_PIPE}-CONN-IN':   get_image(CFG_gui_conn_hist_path + '/pipe_conn_in.png', size=(32, 16)),
            f'{CLI_TYP_PIPE}-DISCO-OUT': get_image(CFG_gui_conn_hist_path + '/pipe_disco_out.png', size=(32, 16)),
            f'{CLI_TYP_PIPE}-DISCO-IN':  get_image(CFG_gui_conn_hist_path + '/pipe_disco_in.png', size=(32, 16)),

            f'{CLI_TYP_BOX}-CONN-OUT':  get_image(CFG_gui_conn_hist_path + '/bbs_conn_out.png', size=(32, 16)),
            f'{CLI_TYP_BOX}-CONN-IN':   get_image(CFG_gui_conn_hist_path + '/bbs_conn_in.png', size=(32, 16)),
            f'{CLI_TYP_BOX}-DISCO-OUT': get_image(CFG_gui_conn_hist_path + '/bbs_disco_out.png', size=(32, 16)),
            f'{CLI_TYP_BOX}-DISCO-IN':  get_image(CFG_gui_conn_hist_path + '/bbs_disco_in.png', size=(32, 16)),

            f'{CLI_TYP_TASK_FWD}-CONN-OUT':  get_image(CFG_gui_conn_hist_path + '/fwd_conn_out.png', size=(32, 16)),
            f'{CLI_TYP_TASK_FWD}-CONN-IN':   get_image(CFG_gui_conn_hist_path + '/fwd_conn_in.png', size=(32, 16)),
            f'{CLI_TYP_TASK_FWD}-DISCO-OUT': get_image(CFG_gui_conn_hist_path + '/fwd_disco_out.png', size=(32, 16)),
            f'{CLI_TYP_TASK_FWD}-DISCO-IN':  get_image(CFG_gui_conn_hist_path + '/fwd_disco_in.png', size=(32, 16)),

            f'{CLI_TYP_CONVERSE}-CONN-OUT':    get_image(CFG_gui_conn_hist_path + '/conv_conn_out.png', size=(32, 16)),
            f'{CLI_TYP_CONVERSE}-CONN-IN':     get_image(CFG_gui_conn_hist_path + '/conv_conn_in.png', size=(32, 16)),
            f'{CLI_TYP_CONVERSE}-DISCO-OUT':   get_image(CFG_gui_conn_hist_path + '/conv_disco_out.png', size=(32, 16)),
            f'{CLI_TYP_CONVERSE}-DISCO-IN':    get_image(CFG_gui_conn_hist_path + '/conv_disco_in.png', size=(32, 16)),
            f'{CLI_TYP_CONVERSE}-CONN-INTER':  get_image(CFG_gui_conn_hist_path + '/conv_conn_inter.png', size=(32, 16)),
            f'{CLI_TYP_CONVERSE}-DISCO-INTER': get_image(CFG_gui_conn_hist_path + '/conv_disco_inter.png',
                                                         size=(32, 16)),

        }
        logger.info("GuiIcons: Init FWD-Q-Tree-Icon Tab 16x16")
        self.fwd_q_flag_icons = {
            'F':  get_image(CFG_aprs_icon_path + '/1-26.png',       size=(16, 16)),
            '$':  get_image(CFG_aprs_icon_path + '/0-82.png',       size=(16, 16)),
            'S+': get_image(CFG_gui_icon_path + '/status_ok.png',   size=(16, 16)),
            'S-': get_image(CFG_aprs_icon_path + '/1-06.png',       size=(16, 16)),
            'S=': get_image(CFG_aprs_icon_path + '/0-67.png',       size=(16, 16)),
            'R':  get_image(CFG_aprs_icon_path + '/1-65.png',       size=(16, 16)),
            'H':  get_image(CFG_aprs_icon_path + '/0-72.png',       size=(16, 16)),
            'EE': get_image(CFG_aprs_icon_path + '/1-78.png',       size=(16, 16)),
        }
        self.fwd_q_flag_icons.update(
            {
                'SW': self.fwd_q_flag_icons['S='],
                'EO': self.fwd_q_flag_icons['EE']
            }
        )
        logger.info("GuiIcons: Init Icon Tabs. Done")


    def get_aprs_icon_tab_16(self):
        return self.aprs_icon_tab_16

    def get_aprs_icon_tab_24(self):
        return self.aprs_icon_tab_24

    def get_aprs_icon_tab_32(self):
        return self.aprs_icon_tab_32

    def get_conn_typ_icon_16(self):
        return self.conn_typ_icons

    def get_rx_tx_icons(self):
        return self.rx_tx_icons

    def get_fwd_q_icon_16(self):
        return self.fwd_q_flag_icons

