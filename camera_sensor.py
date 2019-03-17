import sensor, image, time, lcd,pyb
from pyb import UART

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.VGA)
sensor.skip_frames(time = 2000)
lcd.init() # Initialize the lcd screen.
sensor.set_auto_gain(False) # must turn this off to prevent image washout...
sensor.set_windowing((300, 300))
clock = time.clock()

uart = UART(3, 9600, timeout_char=1000)


while(True):
    clock.tick()
    b = "Hello World!\r"

    red_led = pyb.LED(1)
    red_led.on()

    img = sensor.snapshot()
    img.lens_corr(1.2) # strength of 1.8 is good for the 2.8mm lens.
    a =img.find_qrcodes()
    #print("current a is ______ ", type(a))
    lcd.display(img)
    if a == []:
        #uart.write("not Found!  "+"\r")
        print(" not Found!  ",a)
    else:
        img.draw_rectangle(a[0].rect(), color = (255, 0, 0))
        print(a[0][4],"\n\n\n")
        uart.write(a[0][4]+"\r")
        uart.sendbreak()
        break
    pyb.delay(1000)
    red_led.off()
    print(clock.fps())
    #time.sleep(200)

