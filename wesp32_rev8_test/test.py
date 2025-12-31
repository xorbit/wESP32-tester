import machine
import time
import json

# GPIO connections on test fixture
gpio_conn = [
  { 'out': 2, 'io': (23, 32) },
  { 'out': 1, 'io': (33, 34) },
  { 'out': 2, 'io': (5, 12, 35) },
  { 'out': 2, 'io': (4, 18) },
  { 'out': 2, 'io': (13, 15) },
  { 'out': 2, 'io': (2, 14) }
]

def testGPIO():
  # List of problem pairs (output, input)
  problems = []
  # Test pins as output in two cycles.  There's one set of connections
  # that connects three pins together, but one is input only.
  for out_idx in range(2):
    # Go through each defined connection for setup
    for conn in gpio_conn:
      if out_idx < conn['out']:
        # Make the indexed pin output, the other pins input
        for pin_idx, pin in enumerate(conn['io']):
          if pin_idx == out_idx:
            machine.Pin(pin, machine.Pin.OUT)
          else:
            machine.Pin(pin, machine.Pin.IN)
    # Go through each defined connection again for testing
    for test_conn in gpio_conn:
      if out_idx < test_conn['out']:
        # Turn the output for the indexed connection under test high,
        # the others low
        for conn in gpio_conn:
          if out_idx < conn['out']:
            machine.Pin(conn['io'][out_idx]) \
                    .value(1 if conn == test_conn else 0)
        # Now check that the inputs connected to the active output
        # are high and the rest are low
        for conn in gpio_conn:
          if out_idx < conn['out']:
            for pin_idx, pin in enumerate(conn['io']):
              if pin_idx != out_idx and machine.Pin(pin).value() \
                  != (1 if conn == test_conn else 0):
                problems.append((conn['io'][out_idx], pin))
  # Return list of problem pairs
  return list(set(problems))

def getVPlus():
  return machine.ADC(machine.Pin(39)).read() * 15.7 * 1.1 / 4095

def getV3V3():
  return machine.ADC(machine.Pin(36)).read() * 5.7 * 1.1 / 4095

# Wait for network
network_tries = 8
while lan.ifconfig()[0] == '0.0.0.0' and network_tries:
  time.sleep(2)
  network_tries = network_tries - 1

# Get the IP address
ip = lan.ifconfig()[0]  
# Run the GPIO test to discover problems
gpio_problems = testGPIO()

# Print all test results as JSON
print(json.dumps({
  'vplus': getVPlus(),
  'v3v3': getV3V3(),
  'gpio': {
    'ok': not bool(gpio_problems),
    'problems': gpio_problems,
  },
  'ip': {
    'ok': ip != '0.0.0.0',
    'address': ip
  }
}))

