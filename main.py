from gui.guiMaín import TkMainWin
# from ax25.ax25PortHandler import MYHEARD

if __name__ == '__main__':
    try:
        TkMainWin()
    except KeyboardInterrupt:
        pass
    print("Ende")
    # MYHEARD.save_mh_data()
