#!/usr/bin/env python3

import sys
import os
import glob
import time
import subprocess
from termcolor import colored
import json

# Binary to program
MICROPYTHON_BINARY = 'SIL_WESP32-20250415-v1.25.0.bin'

# Show or suppress output from tools we call based on DEBUG
DEBUG = False
if (DEBUG):
  FOUT = sys.stdout
else:
  FOUT = open(os.devnull, 'w')

# wESP32 module presence checker
def wait_wesp32_present(present):
  while ((subprocess.call(['esptool.py', '--chip', 'esp32', '--port',
          ports[0], 'chip_id'], stdout=FOUT, stderr=FOUT) != 0) == present):
    pass

# Error message helper
def error(message):
  print(colored(message, 'red'))
  wait_wesp32_present(False)

# Copy MicroPython file to the wESP32
def mpremote_cp(filename):
  try:
    return (True, subprocess.check_output(['mpremote', 'connect', ports[0],
          'cp', filename, ':' + filename], stderr=FOUT).decode('utf-8'))
  except Exception as e:
    print (e)
    return (False, "")

# Main loop
while True:

  print("Waiting for wESP32 tester...")
  
  ports = []
  while not ports:
    ports = glob.glob('/dev/ttyUSB*')
    time.sleep(0.1)

  print("Serial port detected, waiting for access...")
  
  while (not os.access(ports[0], os.R_OK|os.W_OK)):
    time.sleep(0.1)
  
  print("Waiting for wESP32 board to be detected...")
  
  wait_wesp32_present(True)
    
  print("wESP32 detected! Erasing flash...")

  if (subprocess.call(['esptool.py', '--chip', 'esp32', '--port',
      ports[0], 'erase_flash'], stdout=FOUT, stderr=FOUT) != 0):
    error("ERROR: Failed to erase flash!")
    continue
  
  print("Programming MicroPython firmware...")
  
  if (subprocess.call(['esptool.py', '--chip', 'esp32', '--port',
      ports[0], '--baud', '921600', 'write_flash', '-z', '0x1000',
      MICROPYTHON_BINARY], stdout=FOUT, stderr=FOUT) != 0):
    error("ERROR: Failed to program MicroPython!")
    continue
  
  time.sleep(1)
  print("Loading boot.py...")
  
  if (not mpremote_cp('boot.py')):
    error("ERROR: Failed to load boot.py!")
    continue

  print(colored("Done! Please remove wESP32.", 'green'))
  wait_wesp32_present(False)
  
