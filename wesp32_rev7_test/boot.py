# This file is executed on every boot (including wake-boot from deepsleep)
import machine
import network

# Connect to LAN
lan = network.LAN(mdc = machine.Pin(16), mdio = machine.Pin(17),
                  power = None, phy_type = network.PHY_RTL8201, phy_addr=0)
if machine.reset_cause() != machine.SOFT_RESET:
  lan.active(True)

# Define convenient reset function
def reset():
  machine.reset()

