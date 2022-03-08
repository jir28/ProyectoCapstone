import sys
from yeelight import Bulb
import showerS


if __name__ == '__main__':
    bulb = Bulb("192.168.100.96")
    bulb.turn_on()
    while True:
        tem = showerS.flujo()
        if(tem==5):
            sys.exit()
