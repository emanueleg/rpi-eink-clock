#!/usr/bin/env python3

##
# epaper-clock.py
#
# Copyright (C) Emanuele Goldoni 2019
#
# original author: Jukka Aittola (jaittola(at)iki.fi) 2017
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
##


import epd2in7
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

import RPi.GPIO as GPIO

from datetime import datetime
import time
import locale
import subprocess
import psutil
import socket
#import sys
import os

LOCALE="it_IT.UTF8"
DATEFORMAT = "%a %x"
TIMEFORMAT = "%H:%M"
FONT = '/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf'
BOUNCETIME = 200

class Fonts:
    def __init__(self, timefont_size, datefont_size, infofont_size):
        self.timefont = ImageFont.truetype(FONT, timefont_size)
        self.datefont = ImageFont.truetype(FONT, datefont_size)
        self.infofont = ImageFont.truetype(FONT, infofont_size)

class Display:
    
    epd = None
    fonts = None
    mode = 1
    
    def __init__(self):
        locale.setlocale(locale.LC_ALL, LOCALE)

        self.epd = epd2in7.EPD()
        self.epd.init()
        
        self.fonts = Fonts(timefont_size = 75, datefont_size = 26, infofont_size = 18)

        self.read_button1()
        self.read_button2()
        self.read_button3()
        self.read_button4()
        self.draw_rpi_logo()

    def start(self):
        while True:
            if 2 == self.mode:
                self.draw_system_data()
            elif 3 == self.mode:
                self.draw_clock_data()
            else:
                self.draw_rpi_logo()
            self.sleep1min()
    
    def sleep1min(self):
        now = datetime.now()
        seconds_until_next_minute = 60 - now.time().second
        time.sleep(seconds_until_next_minute)

    def draw_rpi_logo(self):
        Himage = Image.open(os.path.join('.', 'raspberry.bmp'))
        self.epd.display(self.epd.getbuffer(Himage))


    def draw_clock_data(self):
        datetime_now = datetime.now()
        datestring = datetime_now.strftime(DATEFORMAT).capitalize()
        timestring = datetime_now.strftime(TIMEFORMAT)

        Limage = Image.new('1', (self.epd.height, self.epd.width), 255)  # 255: clear the frame
        draw = ImageDraw.Draw(Limage)
        draw.text((20, 20), timestring, font = self.fonts.timefont, fill = 0)
        draw.text((20, 100), datestring, font = self.fonts.datefont, fill = 0)
        self.epd.display(self.epd.getbuffer(Limage))

    def draw_system_data(self):
        corestring = str(psutil.cpu_count()) + ' CPU @ ' + str(psutil.cpu_freq().current) + ' MHz';
        usagestring = 'CPU usage: ' + str(psutil.cpu_percent());
        memstring = 'RAM: ' + str(int(psutil.virtual_memory().available/(1024*1024))) + ' MiB';
        tempstring = 'CPU Temp. ' + str(round(psutil.sensors_temperatures(fahrenheit=False)['cpu_thermal'][0].current)) + ' \u00b0C';
        psstring = 'Running ps: ' + str(len(psutil.pids()))
        sysstring = corestring + '\n' + usagestring + '\n' + memstring + '\n' + tempstring + '\n' + psstring
        
        #iflist = [name for name in psutil.net_if_addrs().keys()]
        netstring = '\n'.join([str(ifname +' '+str(ip.address)) for ifname in psutil.net_if_addrs().keys() for ip in psutil.net_if_addrs()[ifname] if ip.family == socket.AF_INET])

        Limage = Image.new('1', (self.epd.height, self.epd.width), 255)
        draw = ImageDraw.Draw(Limage)
        draw.text((10, 10), sysstring, font = self.fonts.infofont, fill = 0)
        draw.text((10, 110), netstring, font = self.fonts.infofont, fill = 0)
        self.epd.display(self.epd.getbuffer(Limage))


    def read_button1(self):
        GPIO.setmode(GPIO.BCM)
        pin = 5  # 2nd button
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pin, GPIO.FALLING, callback=self.button_pressed, bouncetime=BOUNCETIME)

    def read_button2(self):
        GPIO.setmode(GPIO.BCM)
        pin = 6  # 2nd button
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pin, GPIO.FALLING, callback=self.button_pressed, bouncetime=BOUNCETIME)

    def read_button3(self):
        GPIO.setmode(GPIO.BCM)
        pin = 13  # 3rd button
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pin, GPIO.FALLING, callback=self.button_pressed, bouncetime=BOUNCETIME)

    def read_button4(self):
        GPIO.setmode(GPIO.BCM)
        pin = 19  # 4th button in the 2.7 inch hat this pin according to the schematics.
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pin, GPIO.FALLING, callback=self.button_pressed, bouncetime=BOUNCETIME)

    def button_pressed(self, pin):
        #print("Button %d was pressed..." % pin)
        if 5 == pin:
            self.draw_rpi_logo()
            self.mode = 1
        elif 6 == pin:
            self.draw_system_data()
            self.mode = 2
        elif 13 == pin:
            self.draw_clock_data()
            self.mode = 3
        elif 19 == pin:
            self.mode = 4
            print("Shutting down system...")
            #subprocess.call(["sudo", "poweroff"])

if __name__ == '__main__':
    display = Display()
    display.start()
