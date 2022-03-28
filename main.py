import sys
from yeelight import Bulb
import showerS


if __name__ == '__main__':
    bulb = Bulb("ip de tu foco xiamoi yeelight")
    bulb.turn_on()
    while True:
        tem = showerS.flujo()
        if(tem==5):
            sys.exit()
