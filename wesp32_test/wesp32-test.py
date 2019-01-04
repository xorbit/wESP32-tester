#!/usr/bin/env python3

import sys
import os
import glob
import time
import subprocess
from termcolor import colored
import json

# These limits are a little sloppy, but the ESP32 ADC isn't very good
# so we just do ballpark checks
VPLUS_MIN = 11.0
VPLUS_MAX = 13.0
V3V3_MIN = 3.0
V3V3_MAX = 3.6

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

# Copy a file to the wESP32 internal file system
def ampy_put(filename):
  return subprocess.call(['ampy', '-p', ports[0], 'put', filename],
          stdout=FOUT, stderr=FOUT) == 0

# Run a MicroPython script on the wESP32
def ampy_run(filename):
  try:
    return (True, subprocess.check_output(['ampy', '-p', ports[0],
          'run', filename], stderr=FOUT).decode('utf-8'))
  except:
    return (False, "")

# Check V+ range
def vplus_ok(v):
  return v >= VPLUS_MIN and v <= VPLUS_MAX
  
# Check V3V3 range
def v3v3_ok(v):
  return v >= V3V3_MIN and v <= V3V3_MAX

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
      'esp32-micropython.bin'], stdout=FOUT, stderr=FOUT) != 0):
    error("ERROR: Failed to program MicroPython!")
    continue
  
  time.sleep(1)
  print("Loading boot.py...")
  
  if (not ampy_put('boot.py')):
    error("ERROR: Failed to load boot.py!")
    continue
  
  print("Running test.py test program on wESP32...")
  
  (success, output) = ampy_run('test.py')
  if (not success):
    error("ERROR: Failed to run test.py!")
    continue
  
  try:
    results = json.loads(output)
  except:
    error("ERROR: Failed to parse output from wESP32 test!")
    continue
  
  print(colored("V+ measured: {:4.1f} V".format(results['vplus']),
        None if vplus_ok(results['vplus']) else 'red'))
  print(colored("V3V3 measured: {:4.1f} V".format(results['v3v3']),
        None if v3v3_ok(results['v3v3']) else 'red'))
  print(colored("Network: {:s}".format("OK" if results['ip']['ok']
        else "ERROR"), None if results['ip']['ok'] else 'red'))
  print(colored("GPIO matrix scan: {:s}".format("OK" if
        results['gpio']['ok'] else "ERROR"), None if
        results['gpio']['ok'] else 'red'))
  if not results['gpio']['ok']:
    print(colored("Faulty GPIO pairs: {}".format(results['gpio']
        ['problems']), 'red'))
  
  if (not (vplus_ok(results['vplus']) and v3v3_ok(results['v3v3'])
      and results['ip']['ok'] and results['gpio']['ok'])):
    error("wESP32 failed test! Please remove wESP32.")
    continue
  
  print(colored("OK! All tests passed, please remove wESP32.", 'green'))
  wait_wesp32_present(False)
  
