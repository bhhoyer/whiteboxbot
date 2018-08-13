#!/usr/bin/python

import pyudev
import serial
import select
import time
import sys
import argparse
from time import sleep
from os.path import basename
import subprocess

control_packet = b'\x61\x00\x01\x00'
reset = control_packet + b'\x33'
get_prod_id = control_packet + b'\x30'
get_version = control_packet + b'\x31'
set_channel_format = b'\x61\x00\x03\x00' + b'\x15' + b'\x00\x01'
set_ratep = b'\x61\x00\x0d\x00' + b'\x0a' + b'\x01\x30\x07\x63\x40\x00\x00\x00\x00\x00\x00\x48'

#silence = b'\x61\x00\x0b\x01' + b'\x01\x48' +  b'\x00\x00\x00\x00\x00\x00\x00\x00\x00'
silence = bytearray.fromhex("61 00 0B 01 01 48 AC AA 40 20 00 44 40 80 80")

#decode_test = b'\x61\x00\x0b\x01' + b'\x01\x48' +  b'\x27\x2f\xa8\x4b\x0b\x36\x21\x00\x8d'

def send_ambe_command(port, command):
    header = b''
    found = False

    written = port.write(command)

    # Find the start byte
    for i in range(0,100):
        byte = port.read(1)
        if len(byte) > 0 and byte[0] == '\x61':
            found = True
            break

    if(not found):
        print "Cannot find start byte"
        return

    header = port.read(3)
    if len(header) != 3:
        print "Cannot read rest of header"
        return

    length = (ord(header[0]) * 256) + ord(header[1])
    response = header[2] + port.read(length)
    return response

def test_ambe_port(port, speed=460800, seconds=1):

	print "ThumbDV Test Program"
	print "Insert ThumbDV anytime"
	
    open('/sys/bus/usb-serial/devices/' + basename(port) + '/latency_timer', 'w').write('1')
    serial_port = serial.Serial(port, speed, timeout=1, rtscts=True)

    reset_response = send_ambe_command(serial_port, reset)
    if reset_response != '\x00\x39':
        print "AMBE 3000 will not reset"
        return

    prod_id = send_ambe_command(serial_port, get_prod_id)[2:]
    print 'Product ID: {0}'.format(prod_id)

    version = send_ambe_command(serial_port, get_version)[2:]
    print 'Version: {0}'.format(version)

    ratep = send_ambe_command(serial_port, set_ratep)
    if ratep != '\x00\x0a\x00':
        print "Set RATEP failed"
        return

    chanfmt = send_ambe_command(serial_port, set_channel_format)
    if chanfmt != '\x00\x15\x00':
        print "Set Channel Format Failed"
        return

    print "Firing off decode packets..."
    serial_port.timeout = 0
    epoll = select.epoll()
    epoll.register(serial_port.fileno(), select.EPOLLIN)
    serial_port.write(silence)
    start_time = time.time()

    while True:
        events = epoll.poll(0.02)
	if ( time.time() > start_time + seconds ):
            break
        for fileno, event in events:
            packet = serial_port.read(serial_port.in_waiting)
            sys.stdout.write('.')
            sys.stdout.flush()
            serial_port.write(silence)

    print "\nDone"
    serial_port.close()
    
#added BHH
subprocess.call(["./ftx_prog",
   	"--manufacturer","NW Digital Radio 02/18",
   	"--product","ThumbDV",
   	"--max-bus-power","200"])

def main():
    parser = argparse.ArgumentParser(description="Test ThumbDV Devices")
    parser.add_argument('--port', '-p', help="Port name to test.  If absent will wait for a ThumbDV to be plugged in.")
    parser.add_argument('--speed', '-s', type=int, help="Speed to talk to the ThumbDV device(s) at", default=460800)
    parser.add_argument('--time', '-t', type=int, help="Duration of ThumbDV decode test", default=2)

    args = parser.parse_args()

    if args.port == None:
        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
        monitor.filter_by('tty')

        for device in iter(monitor.poll, None):
            if device.action != 'add':
                continue
            if device['ID_MODEL_ID'] != '6015' or device['ID_VENDOR_ID'] != '0403':
                print "Nodevice"
                continue

            print "Found and FTDI Device insertion at {0}".format(device.device_node)
            print 'FTDI Manufacturer is {0}'.format(device['ID_VENDOR_ENC'])
            print "Opening {0}...".format(device.device_node)
            test_ambe_port(device.device_node, args.speed, args.time)
    else:
        test_ambe_port(args.port, args.speed, args.time)

if __name__ == "__main__":
    main()
