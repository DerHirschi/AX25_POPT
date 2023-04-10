import cli.ClientDB
import ax25.ax25Statistics
import gui.guiMain
import ax25.ax25InitPorts

LANGUAGE = 0    # QUICK FIX
"""
0 = German
1 = English
2 = Dutch
"""

if __name__ == '__main__':
    GLB_MH_list = ax25.ax25Statistics.MH()
    GLB_CLIENT_db = cli.ClientDB.ClientDB()

    #################
    # Init AX25 Stuff
    GLB_AX25port_handler = ax25.ax25InitPorts.AX25PortHandler(GLB_MH_list)

    #############
    # INIT GUI
    # TODO: if setting_gui (running without GUI option):
    try:
        main_win = gui.guiMain.TkMainWin(GLB_AX25port_handler)
    except KeyboardInterrupt:
        GLB_AX25port_handler.close_all_ports()

    ################
    # On Close Window
    # del main_win
    if GLB_AX25port_handler.is_running:
        print("Close all Ports")
        GLB_AX25port_handler.close_all_ports()
    print("Save MH")
    GLB_MH_list.save_mh_data()
    print("Client DB")
    GLB_CLIENT_db.save_data()

    print("Ende")
