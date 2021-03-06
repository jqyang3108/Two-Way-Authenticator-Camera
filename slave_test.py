# UART 控制
#
# 这个例子展示了如何使用OpenMV的串口。连接P4到 USB转串口模块 的RX。
# 会显示"Hello World!"

import time
from pyb import UART, Pin

# OpenMV上P4，P5对应的串口3
# 第二个参数是波特率。用来更精细的控制
uart = UART(3, 9600, timeout_char=1000)
uart.init(9600, bits=8, parity=None, stop=1)
count = 1


#pin3.irq(trigger=Pin.IRQ_RISING, handler=test)

while(True):
    a = "Hello World!" + str(count) + '\r'
    print(pin3.value())
    uart.write(a)
    uart.sendbreak()
    print("sent",a)
    time.sleep(1000)
    count +=1


def main():

    print("main print test")
