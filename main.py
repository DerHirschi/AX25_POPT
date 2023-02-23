import cli.ClientDB
import ax25.ax25Statistics
import gui.guiMainNew
import ax25.ax25InitPorts
VER = '2.32a'

if __name__ == '__main__':
    GLB_MH_list = ax25.ax25Statistics.MH()
    GLB_CLIENT_db = cli.ClientDB.ClientDB()

    #################
    # Init AX25 Stuff
    GLB_AX25port_handler = ax25.ax25InitPorts.AX25PortHandler(GLB_MH_list)

    #############
    # INIT GUI
    # TODO: if setting_gui:
    try:
        main_win = gui.guiMainNew.TkMainWin(GLB_AX25port_handler)
    except KeyboardInterrupt:
        pass

    ################
    # On Close Window
    # del main_win
    if GLB_AX25port_handler.is_running:
        GLB_AX25port_handler.close_all_ports()
    GLB_MH_list.save_mh_data()
    GLB_CLIENT_db.save_data()

    print("Ende")
