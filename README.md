# Raspberry Pi eInk Smart Screen

_Smart Clock / Sysmon / Nobel-card for Raspbery Pi 3 using the e-Paper 2.7 inch display from Waveshare._

Originally inspired by the [vekkari](https://github.com/jaittola/vekkari) project by [Jukka Aittola](https://github.com/jaittola), this project has quickly evolved into a new project: a fully-featured smart clock. All you need is a Raspberry-Pi 3/4 and the e-Paper 2.7 inch display from Waveshare.

The eInk Smart Clock has multiple display modes, selectable using the four push-buttons soldered on the HAT:
- Raspberry Pi Logo (sort of standby mode)
- Clock (hours and minutes, day of the week, date) with 1 minute refresh interval
- System statics  (CPU, RAM, Processes, IP addresses)
- Nobel Prize information (year, category, winner and motivation - offline dump of the official data obtained from http://api.nobelprize.org/v1/prize.json)

## Buttons

- Button 1: Show Raspberry Logo
- Button 2: Show System Statics
- Button 3: Show Clock (time & date)
- Button 4: Show random Nobel info

## Hardware Requirements

- Raspberry Pi 3
- [2.7inch E-Ink display HAT for Raspberry Pi](https://www.waveshare.com/product/raspberry-pi/displays/e-paper/2.7inch-e-paper-hat.htm)
- 8+ GB SD card

## Installation

- Install [Raspberry Pi OS](https://www.raspberrypi.org/downloads/) on SD card (```python3``` should be already present on Raspberry Pi OS)
- Install git: ```sudo apt install git```
- Issue the command to fetch this project: ```git clone https://github.com/emanueleg/rpi-eink-clock.git```
- Enter the project directory: ```cd rpi-eink-clock``` and install required libraries and python modules [TODO]
- Run the script: ```./epaper-clock``` and verify if it works as expected (hit Ctrl-C to exit)
- If you want the script run at every boot, install this project as service so it could automatically run when Raspberry boots up [TODO]

## License

* Official Waveshare Electronic paper driver/libraries (```epdconfig.py``` and ```epdconfig.py```) are available under the MIT License.
* The official Raspberry Pi Logo used in ```raspberry.bmp``` is a (TM) of Raspberry Pi Foundation (https://www.raspberrypi.org/) and available under the [Raspberry Pi Trademark rules and brand guidelines](https://www.raspberrypi.org/trademark-rules/)
* Nobel data are provided by Nobel Media AB and are available under the Creative Commons Zero (CC0) license - see the [Terms of Use for api.nobelprize.org and data.nobelprize.org ](https://www.nobelprize.org/about/terms-of-use-for-api-nobelprize-org-and-data-nobelprize-org/)
* This project is a fork, hence the original licenses still apply to the initial edits. Since commit rpi-eink-clock@1a285353e120afca18e326debc70ca17c941fff9 quite all the code is brand new: the license for the project is now the Apache License 2.0
