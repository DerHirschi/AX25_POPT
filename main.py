from gui.guiMaín_old import TkMainWin
# from ax25.ax25PortHandler import MYHEARD

VER = '0.1a'

if __name__ == '__main__':
    try:
        main = TkMainWin()
    except KeyboardInterrupt:
        pass
    del main
    print("Ende")
    # MYHEARD.save_mh_data()
