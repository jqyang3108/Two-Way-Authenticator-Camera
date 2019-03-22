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
    print(" ------------------------\n|  Start Initialization  |\n ------------------------")
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
        print("\nFinding QR Codes......  ",qr_list,"    |")
    else:
        payload = qr_list[0][4]
        print("-------------------------------\nFound! Decode Result: ")
        print(payload,"\n-------------------------------")
        break_indicator = 1
    return break_indicator, payload

#def lcd():

def UART_send(str1):
    pyb.delay(100)
    leng = len(str1)
    group = int(len(str1)/58)
    datalist = []
    package_list =[]
    data = 0
    package_group = 1

    #find # of groups in package
    if(len(str1)%58 != 0):
        group +=1
    #print(group, " groups")
    i = 0

    datalist = [str1[i:i+58] for i in range(0, len(str1), 58)]
    for data in datalist:
        print(i)
        package_list.append("{}@@{}".format(i,data))
        i+=1


    #pyb.delay(200)
    print(package_list)
    mcu_resp = 0
    count = 0
    while(True):
        print("\n-------------Total Group: {} Sending Group: {}---------------------".format(group, count+1))
        uart.write(package_list[count])
        pyb.delay(200)
        uart.sendbreak()
        pyb.delay(200)
        while(True):
            if(uart.any()):
                mcu_resp = uart.readline().decode("utf-8").split('@@')
                #print("mcu_resp is ", mcu_resp)
                break

        if (mcu_resp[1] == "received\x00"):
            print("Group {} received".format(count+1))
            count+=1
        elif(mcu_resp[1] == "resend\x00"):
            print("Group {} not received".format(count+1))
        else:
            print("Transmission error!",count)
        print('--------------------------\n')
        if((count) == group):
            print("\n========submission complete============\n")
            uart.write("allsent!\r")
            pyb.delay(100)
            uart.sendbreak()
            break

        pyb.delay(200)

    #while(True):

def active_mode1(p):
    pin3.irq(trigger=Pin.IRQ_RISING, handler=None)
    value1 = pin3.value()
    pyb.delay(100)
    value2 = pin3.value()
    global globalval
    globalval +=1
    if globalval > 1:
        globalval = 0
    return
    #print(p)
def active_mode():
    #start_flag
    global globalval
    global active_run_count
    active_run_count += 1
    initialize()
    uart.write("ready")
    pyb.delay(500)
    uart.sendbreak()

    pyb.delay(500)
    print(" ---------------------\n|  Start scanning!  |\n---------------------\n\n--------------------------")
    while(True):
        clock.tick()
        img = sensor.snapshot()     #get the raw image
        #initialize the red led indication in active mode
        red_led = pyb.LED(1)
        red_led.toggle()


        #qr decoding
        corr_img = img.lens_corr(1.2) # strength of 1.2 is good for the 2.8mm lens.
        break_indicator, payload = QR_decode(img)
        lcd.display(corr_img)

        if break_indicator == 1:
            UART_send(payload)
            #print("Scan complete!",break_indicator)
            globalval = 0
            pin3.irq(trigger=Pin.IRQ_FALLING, handler=active_mode1)
            break

#system delay for 100ms
        pyb.delay(100)

    pyb.delay(3000)
    print("\n ----------------\n| Scan complete! Go to idle  |\n----------------\n")
    red_led.off()
    idle_state()



def idle_state():
    clock = time.clock()
    global globalval
    global active_run_count
    count = 0
    active_run_count = 0
    while(True):
        #clock.tick()
        #blue LED indicates sleep mode
        #print(pin3.value())
        print('active run = ',active_run_count)
        if (globalval != 0) and (active_run_count == 0):
            active_mode()
            active_run_count = 0
        print("--------------------------------\nIn sleep mode",count)

        red_blue = pyb.LED(3)
        red_blue.toggle()
        pyb.delay(500)
        count +=1
pyb.delay(1000)
def start():
    pin3.irq(trigger=Pin.IRQ_RISING, handler=active_mode1)
start()
idle_state()
