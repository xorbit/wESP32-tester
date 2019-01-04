#!/usr/bin/env python3

import os
import glob
import serial
import time
from termcolor import colored


while True:

  print("Waiting for wESP32-Prog...")
  
  ports = []
  while not ports:
    ports = glob.glob('/dev/ttyUSB*')
    time.sleep(0.1)

  print("Serial port detected, waiting for access...")
  
  while (not os.access(ports[0], os.R_OK|os.W_OK)):
    time.sleep(0.1)
  
  print("Testing wESP32-Prog...")
  
  test_ok = True
  s = serial.Serial(port=ports[0], baudrate=115200, timeout=0.1)

  s.setRTS(False)
  s.setDTR(False)
  s.write(b'0')
  res = s.read(1)
  if (res not in [b'0', b'1', b'2', b'3']):
    print(colored("ERROR: Serial data did not echo correctly, is the tester connected?", 'red'))
    test_ok = False
  if (res != b'3'):
    print(colored("ERROR: IO0 and/or EN pulled low when neither is asserted!", 'red'))
    test_ok = False

  s.setRTS(True)
  s.write(b'0')
  if (s.read(1) != b'1'):
    print(colored("ERROR: EN not pulled low correctly!", 'red'))
    test_ok = False

  s.setDTR(True)
  s.write(b'0')
  if (s.read(1) != b'3'):
    print(colored("ERROR: IO0 and/or EN pulled low when both are asserted!", 'red'))
    test_ok = False

  s.setRTS(False)
  s.write(b'0')
  if (s.read(1) != b'2'):
    print(colored("ERROR: IO0 not pulled low correctly!", 'red'))
    test_ok = False

  if (test_ok):
    print(colored("OK! All tests passed.", 'green'))
    s.write(b'@')

  s.close()
  print("Please unplug wESP32-Prog.")
  
  while ports:
    ports = glob.glob('/dev/ttyUSB*')
    time.sleep(0.1)

