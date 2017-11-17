import network
import time
import math
import esp
import machine
import urtc
import dht
from machine import Pin, I2C
from neopixel import NeoPixel



def Timer():
    global mytimer1, mytimer2, mytimer3, mytimer4, sek1, sek5, debug

    sek1=False
    sek5=False
    sek3600=False
    # wait for 100 mS to pass
    time.sleep_ms(100)
    mytimer1=mytimer1+1
    # Timer för 1 sek
    if mytimer1 == 10:
        mytimer1=0
        mytimer2=mytimer2+1
        mytimer3=mytimer3+1
        mytimer4=mytimer4+1
        sek1=True
    # Timer för 5 sek
    if mytimer2 == 5:
        sek5=True
        mytimer2=0
    # Stäng av debug 25 sek efter start
    if mytimer3==25: debug=False
    # Timer för 1 timme sek
    if mytimer4 == 3600:
        sek3600=True
        mytimer4=0    
    return


def Readtemp(old_temp):
    global temp

    temp.measure()
    new_temp=temp.temperature()
    # 90% av gamla värdet och 10% nya värdet
    x=(((old_temp * 9) + new_temp)/10)
    return(x)


def Readlight():
    global light_history, light_sensor, night, light

    # 4 st historiska värden sparas
    x=4
    while x>0:
        light_history[x] =light_history[x-1] 
        x-=1
    light = light_sensor.value()       
    light_history[0] = light   
    a=light_history[0]+light_history[1]+light_history[2]+light_history[3]+light_history[4]
    # 5 i rad för byte annars behåll värde
    if (a==5): night=True
    if (a==0): night=False
    return
        

def LEDpaneldebug():
    global night, light
    global sek1, old_temp, movement
    global old_temp, nightlight, fade

    # rgb data för NEO-pixel
    red=(64,0,0)
    white=(64,64,64)
    blue=(0,0,64)
    green=(0,64,32)
    yellow=(64,64,0)
    orange=(64,35,0)
    off=(0,0,0)
    
    # debug info till LEDs
    # LED 0. variabel night. dag/natt visas vit/röd
    if (night): led[0]=red
    else: led[0]=white
    
    # LED 1. variabel sek1 som blink (röd)
    if (sek1): led[1]=red
    else: led[1]=off    
    
    # LED 2. Ljussensor I/O pin (röd)
    if (light): led[2]=red
    else: led[2]=white    
    
    # LED 3. PIR sensor I/O pin (röd)
    if (movement): led[3]=red
    else: led[3]=off     

    # LED 4. Variabel network
    if (network): led[4]=blue
    else: led[4]=off    
    
    # LED 5. variabel nightlight (röd)
    if (nightlight): led[5]=red
    else: led[5]=off      

    # LED 6. variabel fade (röd)
    if (fade): led[6]=red
    else: led[6]=off      

    # LED 7. aktuell temp
    # Temp 10 till 20 grader ska presenteras som gul-röd skala (0-255)
    intensity=1
    new_temp=old_temp
    if old_temp<10:new_temp=10
    if old_temp>20:new_temp=20
    temp=new_temp-10
    temp=temp*25.5
    new_temp=int(temp)
    rgbtemp=(int(255*intensity), 255-int(new_temp*intensity), 0)
    led[7]=rgbtemp    
    led.write()
    return


def LEDpanelnormal():
    global sek1, night, old_temp, intensity, nightlight, manuellInt

    red=(4,0,0)
    white=(4,4,4)
    off=(0,0,0)    
    # debug info till LEDS
    # LED 0. variabel night. dag/natt visas vit/röd
    if (night): led[0]=red
    else: led[0]=white
    
    # LED 1. variabel sek1 som blink (röd)
    if (sek1): led[1]=red
    else: led[1]=off    
    
    # LED 2 till 7. visar aktuell temperatur
    if (nightlight):
        new_temp=old_temp
        if old_temp<10:new_temp=10
        if old_temp>20:new_temp=20
        temp=new_temp-10
        temp=temp*25.5
        new_temp=int(temp)
        rgbtemp=(int(255*intensity), int((255-new_temp)*intensity), 0)
        for i in range(2, 8):
            led[i]=rgbtemp
    else: # Ingen nightlight
        for i in range(2, 8):
            led[i]=(0,0,0)       
    led.write()
    return


def ReadPIR():
    global pir_sensor, movement

    movement=False
    if (pir_sensor.value()==1):
        movement=True
    #print ("PIR=", movement)
    return


def TestDebug():
    global debug

    # Kolla om "flash" knappen är nertryckt
    switchpin=Pin(0,Pin.IN)
    if not (switchpin.value()): 
        #print("Debug switch pressed")
        debug=not debug
    return

def ReadManuellInt():
    
    adc=machine.ADC(0)
    adcVal= adc.read()
    # gör om 0-1024 till 0.01-1
    if adcVal>999: adcVal=1000
    if adcVal<10: adcVal=10
    adcVal=int(adcVal/10)/100
    print("adc=", adcVal)
    return adcVal

def TestNetwork():
    global sta_if, network
    
    if (sta_if.isconnected()):
        connected=True
    return

    
def main():    
    global mytimer1, mytimer2, mytimer3, mytimer4
    global sek1, sek5, sek3600
    global light_sensor, light_history
    global pir_sensor, movement
    global temp, night, led, light
    global old_temp, debug, intensity 
    global nightlight, fade, network
    global sta_if, urtc, manuellInt
    
    
    # Init del, körs en gång
    intensity=1
    nightlight=False
    fade=False
    debug=True
    old_temp=4
    mytimer1=0
    mytimer2=0
    mytimer3=0
    mytimer4=0
    manuellInt=0
    sek1=False
    sek5=False
    sek3600=False
    night=False
    movement=False
    connected=False
    
    #Init av RTC klocka på I2C
    i2c=I2C(scl=Pin(2), sda=Pin(13), freq=100000)
    tid=urtc.DS1307(i2c)
    print("tid:",tid.datetime())

    #Använd nästa rad för att sätta tid vid boot
    ##tid.datetime((2017,11,10,0,8,10,0,0))
    
      
    # Initiering av nätverk
    sta_if=network.WLAN(network.STA_IF)
    sta_if.active(True)    
    sta_if.connect('SpetbyWireless', '0705315205')
    #sta_if.connect('SpetbyWireless_2', '0705315205')
    #sta_if.connect('Spetby_1', '0705315205')
    
    # PIR sensor HC-SR501 på GPIO5
    pir_sensor_pin = 5
    pir_sensor=Pin(pir_sensor_pin, Pin.IN)
    light=False

    # Ljussensor på GPIO14
    light_sensor_pin = 14
    light_sensor=Pin(light_sensor_pin, Pin.IN)
    light_history=[0,0,0,0,0]

    # Tempsensor DHT11 på GPIO4
    temp=dht.DHT11(machine.Pin(4))

    #Neopixel 8 LEDs på GPIO12
    pin=Pin(12, Pin.OUT)
    led=NeoPixel(pin, 8)

    # grunddata är alla LEDs släckta
    led[0] = (0,0,0)
    led[1] = (0,0,0)
    led[2] = (0,0,0)
    led[3] = (0,0,0)
    led[4] = (0,0,0)
    led[5] = (0,0,0)
    led[6] = (0,0,0)
    led[7] = (0,0,0)    
    
   
    # Huvudprogram, körs som evighetsloop
    print("Main started")
    while 1:
        #Vänta 100mS
        Timer()
        
        # Kolla om rörelse
        ReadPIR()
        
        # Läs av Manuell intensitet från ADC[0]
        manuellInt= ReadManuellInt()
                
        #Kolla om koppling mot nät finns
        if (not connected):TestNetwork()
        
        if (sek5):
            old_temp=Readtemp(old_temp)

        if (sek5):
            Readlight()

        if ((night) & (movement)):
            # Tänd nattlampa
            nightlight=True
            fade=False
            intensity=1

        if ((nightlight) & (not movement)):
            # Börja fada ner nattlampan
            fade=1

        if ((nightlight) & (fade)):
            # Fadning pågår (100 steg)
            intensity=intensity-0.01

        if ((nightlight) & (intensity<0.01)):
            # Fade klar
            fade=False
            nightlight=False

        # olika info på LED beroende på om debug är satt
        if (debug):LEDpaneldebug()
        else: LEDpanelnormal()
        if (sek1): TestDebug()

        # En gång i timmen skickar vi data till servern
        if (sek3600):
            # Här ska vi göra POST mot server
            print("HTTP:Post till server")


if __name__ =='__main__':
    main()