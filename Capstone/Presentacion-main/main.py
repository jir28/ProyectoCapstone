import sys
from yeelight import Bulb
import showerS


if __name__ == '__main__':
    #tem = showerS.flujo()
    bulb = Bulb("10.111.0.46")
    bulb.turn_on()

while True:
        tem = showerS.flujo()
        if(tem==5):
           sys.exit()