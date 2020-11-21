#! /usr/bin/python

'''

stupid way to sniff

ed@nuc:~/modbus$ ./read.py
read:
read: 0b1001b40001020000d38400
read: 0b1001b40001020000d38400
read: 0b1001b40001020000d38400
read: 0b1001b40001020000d38400
read: 0b1001b40001020000d38400
read: 0b1001b40001020000d38400
read: 0b1001b40001020000d38400
read: 0b1001b40001020000d38400
read: 0b1001b40001020000d38400
read: 0b1001b40001020000d38400
read: 0b1001b40001020000d38400
read: 0b1001b40001020000d38400
read: 0b1001b40001020000d38400
read: 0b1001b40001020000d38400
read: 0b1001b40001020000d38400
read: 0b1001b40001020000d38400
read: 0b1001b40001020000d38400
read: 0b1001b40001020000d384000b1001b40001020000d38400
----------- quiet period...

request entries for client 10
read: 0a04f80000ffffffff02760015002f0004006800dc001e000100040001000000cd00c8008c000800d40003000f0000007000c800a0003c0008ffff0003000700c801f40000ffff2c0a00c800a0003c0008ffff0003000700c801f40000ffffffffffffffffffffffffffffffffffffffffffffffffffffffff01f40000000401b900000001ffffffffffff00960096012c02bc0028ffff014a0128ffff2125127400000000ffffffffffffffffffffffffffffffff00090000000000000000001000000064002fffff0004ffffffff007d0000ffff80018001ffff000c000b0014ffffffffffffffff000000000128ffffffff0002ffffffffffffa81b000000
----------- new cycle...

read: 210300650001937500
read: 220300650001934600
read: 230300650001929700
read: 240300650001932000
read: 25030065000192f100
read: 26030065000192c200
read: 270300650001931300

'''
          

import sys
import time
import serial
import os
import struct

 

ser = serial.Serial(
 port='/dev/ttyUSB0',
 baudrate = 9600,
 parity=serial.PARITY_NONE,
 stopbits=serial.STOPBITS_ONE,
 bytesize=serial.EIGHTBITS,
 timeout=10
)


# a 9600 baus, 1 caractere time = 1,2 ms, 3.5ct = 4 ms

new_cycle   = False
new_message = False
quiet       = False

starttime   = time.time()
last_data_time = time.time()

message = ""


while True:

  new_time = time.time()
  delta_time = new_time - last_data_time

  # a new message (1 message is delivered in 100ms)
  if delta_time > 0.10 and new_message == False: 
      sys.stdout.write( "read: "+message)
      sys.stdout.write('\n')
      sys.stdout.flush()
      new_message = True
      message = ""

  # a new cycle (1 pause is obtained after 1 sec)
  # have a new cycle after 5s
  # quiet period till next cycle (within 5sec)
  if delta_time > 0.5 and quiet == False and new_cycle == False:
      sys.stdout.write('----------- quiet period...\n\n')
      sys.stdout.flush()
      quiet = True

      # documentation: https://unserver.xyz/modbus-guide/#read-input-registers---0x04-section
      # [1B ID][1B FC][2B ADDR][2B NUM][2B CRC]
      # Opportunity yo query: request info to 0a
      # available modbus command:
      #03 lecture registre me maintien
      #04 lecture registre entree
      #06 ecriture registre entree

      # get all values
      sys.stdout.write("request entries for client 10\n")
      ser.write( "\x0a\x04\x00\x00\x00\x7c\xf0\x90")
      ser.flush()

      # set value
      #           [0A][06][00][0D][00][03][59][73]
      #sys.stdout.write("client 10: request to assign 3 on register 0x0d\n")
      #ser.write("\x0a\x06\x00\x0d\x00\x03\x59\x73")
      #ser.flush()
      #time.sleep( 0.10);

  if delta_time > 4 and new_cycle == False:
      new_cycle = True
      quiet = False
      sys.stdout.write('----------- new cycle...\n\n')
      sys.stdout.flush()


  #read byte per byte
  if (ser.inWaiting()>0):

      #got data
      new_message = False
      new_cycle = False

      x=ser.read( ser.inWaiting())
      last_data_time = new_time

      message += x.encode('hex')

  time.sleep( 0.01);


