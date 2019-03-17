# Untitled - By: jiaqiyang - 周六 3月 16 2019

import sensor, image, time, lcd, pyb, micropython
from machine import Pin, deepsleep,reset


micropython.alloc_emergency_exception_buf(100)


globalval = 0
active_run_count = 0

def initialize():
#Camera initialization
#color mode: gray scal
#resolution rate: 640X480 VGA
#focus area: 300X300
    print("Start Initialization")
    sensor.reset()
    sensor.set_pixformat(sensor.GRAYSCALE)
    sensor.set_framesize(sensor.VGA)
    sensor.skip_frames(time = 2000)
    sensor.set_auto_gain(False) # must turn this off to prevent image washout...
    sensor.set_windowing((300, 300))
    lcd.init() # Initialize the lcd screen.



#PIN initialization
##UART
###set 3
###braudrate: 9600
uart = pyb.UART(3, 9600, timeout_char=1000)
##GPIO
###PIN3
pin3 = Pin('P3', Pin.IN)
#clock
clock = time.clock()



def QR_decode(img):
    qr_list = img.find_qrcodes()
    break_indicator = 0
    payload = 0
    #print("current a is ______ ", type(a))
    if qr_list == []:
        print("-------------------------------\nFinding QR Codes......  ",qr_list)
    else:
        payload = qr_list[0][4]
        print("-------------------------------\nFound! Decode Result: ")
        print(payload,"\n-------------------------------")
        break_indicator = 1
    return break_indicator, payload

#def lcd():

def UART_send(input):
    uart.write(input+"\r")
    uart.sendbreak()

def active_mode1(p):
    pin3.irq(trigger=Pin.IRQ_RISING, handler=None)
    global globalval
    globalval +=1
    if globalval > 1:
        globalval = 0
    #print(p)
    pin3.irq(trigger=Pin.IRQ_RISING, handler=active_mode1)
def active_mode():
    #start_flag
    global globalval
    global active_run_count
    active_run_count += 1
    initialize()
    UART_send("ready")
    while(True):
        clock.tick()
        img = sensor.snapshot()     #get the raw image
        print("Start scanning!")

        #initialize the red led indication in active mode
        red_led = pyb.LED(1)
        red_led.toggle()


        #qr decoding
        corr_img = img.lens_corr(1.2) # strength of 1.2 is good for the 2.8mm lens.
        break_indicator, payload = QR_decode(img)
        lcd.display(corr_img)

        if break_indicator == 1:
            UART_send(payload)
            print("break_indicator",break_indicator)
            globalval = 0
            break

#system delay for 500ms
        pyb.delay(500)
    pyb.delay(3000)
    idle_state()

pin3.irq(trigger=Pin.IRQ_RISING, handler=active_mode1)


def idle_state():
    clock = time.clock()
    global globalval
    global active_run_count
    count = 0
    while(True):
        #clock.tick()
        #blue LED indicates sleep mode
        print('active run = ',active_run_count)
        if (globalval != 0) and (active_run_count == 0):
            active_mode()
            active_run_count = 0
        print("sleep",count)

        red_blue = pyb.LED(3)
        red_blue.toggle()
        pyb.delay(500)
        count +=1

idle_state()

