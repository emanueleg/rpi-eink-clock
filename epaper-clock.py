#!/usr/bin/env python3

##
# epaper-clock.py - smart clock / system monitor and more
#
# Copyright (C) Emanuele Goldoni 2020
#
# Released under the Apache License, Version 2.0
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
import json
import random
import textwrap

LOCALE="it_IT.UTF8"
DATEFORMAT = "%a %x"
TIMEFORMAT = "%H:%M"
FONT = '/usr/share/fonts/truetype/freefont/FreeMono.ttf'
FONTBOLD = '/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf'
BOUNCETIME = 500

NOBELPRIZE_JSON = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources/prize.json')
RASPBERRY_BMP_LOGO = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources/raspberry.bmp')

PIN_BTN1 = 5
PIN_BTN2 = 6
PIN_BTN3 = 13
PIN_BTN4 = 19

DISPMODE_LOGO = 1
DISPMODE_SYSSTATS = 2
DISPMODE_CLOCK = 3
DISPMODE_NOBEL = 4

class Fonts:
    def __init__(self, timefont_size, datefont_size, infofont_size, smallfont_size):
        self.timefont = ImageFont.truetype(FONTBOLD, timefont_size)
        self.datefont = ImageFont.truetype(FONTBOLD, datefont_size)
        self.infofont = ImageFont.truetype(FONTBOLD, infofont_size)
        self.smallfont = ImageFont.truetype(FONT, smallfont_size)

class Display:
    
    epd = None
    fonts = None
    mode = DISPMODE_NOBEL
    nobeldata = None
    
    def __init__(self):
        locale.setlocale(locale.LC_ALL, LOCALE)
        self.fonts = Fonts(timefont_size = 75, datefont_size = 26, infofont_size = 18, smallfont_size=16)

        with open(NOBELPRIZE_JSON) as f:
            self.nobeldata = json.load(f)
        
        self.epd = epd2in7.EPD()
        self.epd.init()
        self.read_buttons()

    def start(self, start_mode = DISPMODE_LOGO):
        if not type(start_mode)==int:
            self.mode = DISPMODE_LOGO
        else:
            self.mode = start_mode
        while True:
            if DISPMODE_SYSSTATS == self.mode:
                self.draw_system_data()
            elif DISPMODE_CLOCK == self.mode:
                self.draw_clock_data()
            elif DISPMODE_NOBEL == self.mode: 
                self.draw_rnd_nobel_info()
            else:
                self.mode = DISPMODE_LOGO
                self.draw_rpi_logo()
            self.sleep_until_next_min()
    
    def sleep_until_next_min(self):
        now = datetime.now()
        seconds_until_next_minute = 60 - now.time().second
        time.sleep(seconds_until_next_minute)

    def draw_rpi_logo(self):
        Himage = Image.open(RASPBERRY_BMP_LOGO)
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
        corestring = 'CPU freq: ' + str(psutil.cpu_freq().current) + ' MHz';
        usagestring = 'CPU usage: ' + str(psutil.cpu_percent());
        tempstring = 'CPU temp. ' + str(round(psutil.sensors_temperatures(fahrenheit=False)['cpu_thermal'][0].current)) + ' \u00b0C';
        memstring = 'Free RAM: ' + str(int(psutil.virtual_memory().available/(1024*1024))) + ' MiB';
        psstring = 'Running ps: ' + str(len(psutil.pids()))
                
        #iflist = [name for name in psutil.net_if_addrs().keys()]
        ifaddresses = [ifname+' '+str(ip.address) for ifname in psutil.net_if_addrs().keys() for ip in psutil.net_if_addrs()[ifname] if ip.family == socket.AF_INET]
        
        sysstring = corestring + '\n' + usagestring + '\n' + tempstring + '\n' + memstring + '\n' + psstring
        netstring = '\n'.join(ifaddresses)

        Limage = Image.new('1', (self.epd.height, self.epd.width), 255)
        draw = ImageDraw.Draw(Limage)
        draw.text((10, 10), sysstring, font = self.fonts.infofont, fill = 0)
        draw.text((10, 110), netstring, font = self.fonts.infofont, fill = 0)
        self.epd.display(self.epd.getbuffer(Limage))
    
    def draw_rnd_nobel_info(self):
        p = random.choice(self.nobeldata['prizes'])
        #print(p) #just debugging
        y = p['year']
        c = p['category'].title()
        if ('laureates' in p.keys()):
            w = random.choice(p['laureates'])
            n = w['firstname']
            n += ' '+w['surname'] if 'surname' in w.keys() else ""
            m = w['motivation']
        else:
            n = ""
            m = p['overallMotivation']
        Limage = Image.new('1', (self.epd.height, self.epd.width), 255)
        draw = ImageDraw.Draw(Limage)
        draw.text((5, 5), c + ' (' + y + ')', font = self.fonts.infofont, fill = 0)
        draw.text((5, 27), n, font = self.fonts.infofont, fill = 0)
        draw.text((5, 50), textwrap.fill(textwrap.shorten(m, 140), 25), font = self.fonts.smallfont, fill = 0)
        self.epd.display(self.epd.getbuffer(Limage))

    def read_buttons(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIN_BTN1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(PIN_BTN1, GPIO.FALLING, callback=self.button_pressed, bouncetime=BOUNCETIME)
        GPIO.setup(PIN_BTN2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(PIN_BTN2, GPIO.FALLING, callback=self.button_pressed, bouncetime=BOUNCETIME)
        GPIO.setup(PIN_BTN3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(PIN_BTN3, GPIO.FALLING, callback=self.button_pressed, bouncetime=BOUNCETIME)
        GPIO.setup(PIN_BTN4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(PIN_BTN4, GPIO.FALLING, callback=self.button_pressed, bouncetime=BOUNCETIME)

    def button_pressed(self, pin):
        #print("Button %d was pressed..." % pin)
        if PIN_BTN1 == pin:
            self.draw_rpi_logo()
            self.mode = DISPMODE_LOGO
        elif PIN_BTN2 == pin:
            self.draw_system_data()
            self.mode = DISPMODE_SYSSTATS
        elif PIN_BTN3 == pin:
            self.draw_clock_data()
            self.mode = DISPMODE_CLOCK
        elif PIN_BTN4 == pin:
            self.draw_rnd_nobel_info()
            self.mode = DISPMODE_NOBEL


if __name__ == '__main__':
    display = Display()
    display.start(DISPMODE_CLOCK)
