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

class Fonts:
    def __init__(self, timefont_size, datefont_size, infofont_size):
        self.timefont = ImageFont.truetype(FONT, timefont_size)
        self.datefont = ImageFont.truetype(FONT, datefont_size)
        self.infofont = ImageFont.truetype(FONT, infofont_size)

def main():
    locale.setlocale(locale.LC_ALL, LOCALE)

    epd = epd2in7.EPD()
    epd.init()

    fonts = Fonts(timefont_size = 75, datefont_size = 26, infofont_size = 18)

    read_button2()
    read_button3()
    read_button4()
    draw_rpi_logo(epd)
    #system_loop(epd, fonts)
    #clock_loop(epd, fonts)

def go_to_sleep(sleep_secs):
    now = datetime.now()
    seconds_until_next_minute = sleep_secs - now.time().second
    time.sleep(seconds_until_next_minute)

def clock_loop(epd, fonts):
    while True:
        now = datetime.now()
        draw_clock_data(epd, fonts, now)
        go_to_sleep(60)

def system_loop(epd, fonts):
    while True:
        draw_system_data(epd, fonts)
        go_to_sleep(60)

def draw_rpi_logo(epd):
    Himage = Image.open(os.path.join('.', 'raspberry.bmp'))
    epd.display(epd.getbuffer(Himage))
    while True:
        go_to_sleep(60)

def draw_clock_data(epd, fonts, datetime_now):
    datestring = datetime_now.strftime(DATEFORMAT).capitalize()
    timestring = datetime_now.strftime(TIMEFORMAT)

    Limage = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(Limage)
    draw.text((20, 20), timestring, font = fonts.timefont, fill = 0)
    draw.text((20, 100), datestring, font = fonts.datefont, fill = 0)
    epd.display(epd.getbuffer(Limage))

def draw_system_data(epd, fonts):
    corestring = str(psutil.cpu_count()) + ' CPU @ ' + str(psutil.cpu_freq().current) + ' MHz';
    usagestring = 'CPU usage: ' + str(psutil.cpu_percent());
    memstring = 'RAM: ' + str(int(psutil.virtual_memory().available/(1024*1024))) + ' MiB';
    tempstring = 'CPU Temp. ' + str(round(psutil.sensors_temperatures(fahrenheit=False)['cpu_thermal'][0].current)) + ' \u00b0C';
    psstring = 'Running ps: ' + str(len(psutil.pids()))
    sysstring = corestring + '\n' + usagestring + '\n' + memstring + '\n' + tempstring + '\n' + psstring
    
    #iflist = [name for name in psutil.net_if_addrs().keys()]
    netstring = '\n'.join([str(ifname +' '+str(ip.address)) for ifname in psutil.net_if_addrs().keys() for ip in psutil.net_if_addrs()[ifname] if ip.family == socket.AF_INET])

    Limage = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(Limage)
    draw.text((10, 10), sysstring, font = fonts.infofont, fill = 0)
    draw.text((10, 110), netstring, font = fonts.infofont, fill = 0)
    epd.display(epd.getbuffer(Limage))

def read_button2():
    GPIO.setmode(GPIO.BCM)
    pin = 6  # 2nd button
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(pin, GPIO.FALLING, callback=button_pressed, bouncetime=200)

def read_button3():
    GPIO.setmode(GPIO.BCM)
    pin = 13  # 3rd button
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(pin, GPIO.FALLING, callback=button_pressed, bouncetime=200)

def read_button4():
    GPIO.setmode(GPIO.BCM)
    pin = 19  # 4th button in the 2.7 inch hat this pin according to the schematics.
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(pin, GPIO.FALLING, callback=button_pressed, bouncetime=200)

def button_pressed(pin):
    print("Button %d was pressed..." % pin)
    #subprocess.call(["sudo", "poweroff"])

if __name__ == '__main__':
    main()
