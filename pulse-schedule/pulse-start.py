#!/usr/bin/env python3
"""
https://stackoverflow.com/questions/8241099/executing-tasks-in-parallel-in-python

"""

import argparse
import serial
import time
from threading import Thread
import subprocess


class quantel():
    """
    Models an  Serial connection
    """

    def __init__(self, serial_port='/dev/ttyS0', baud_rate=9600,
                 read_timeout=20):
        """
        Initializes the serial connection to the Arduino board
        """
        self.ser = serial.Serial(serial_port, baud_rate)
        self.ser.timeout = read_timeout  # Timeout for readline()

    def standBy(self):
        """
        Unicode strings must be encoded (e.g. 'hello'.encode('utf-8').
        """
        command = "S\r\n".encode('utf-8')
        # print(command)
        self.ser.write(command)
        time.sleep(0.5)
        line = self.ser.readline()   # read a '\n' terminated line
        print(f"reply: {line}")
        return line

    def triggerQSwitch(self):
        """
        Unicode strings must be encoded (e.g. 'hello'.encode('utf-8').
        """
        command = "CC\r\n".encode('utf-8')
        self.ser.write(command)
        time.sleep(0.5)
        line = self.ser.readline()   # read a '\n' terminated line
        print(f"reply: {line}")
        return line

    def close(self):
        """
        To ensure we are properly closing our connection to the
        Arduino device.
        """
        self.ser.close()
        # print('Connection to Quantel Laser closed')


def parse_args():
    parser = argparse.ArgumentParser(
            description='Script to start ESTHER Operation Pulse')

    parser.add_argument('-r', '--host_rp', default='10.10.136.229',
                        help='Red Pitay IP address')
    parser.add_argument('-s', '--laserStandby',
                        action='store_true', help='Set Quantel in Standby')
    parser.add_argument('-c', '--redpitayaConfig',
                        action='store_true', help='Check Red Pitaya Config')
    parser.add_argument('-f', '--fire',
                        action='store_true', help='Fire Quantel')
    return parser.parse_args()


def task1():
    time.sleep(2)
    print("Task 1 Finished")


def taskFireQuantel():
    time.sleep(1)
    qt = quantel()
    # reply = qt.standBy()
    reply = qt.triggerQSwitch()
    qt.close()
    print(reply)
    print("Trigger Quantel Finished")


def taskRPitayaStart(host="10.10.136.229"):
    # list_files = subprocess.run(["ls", "-l"])
    # list_files = subprocess.run(["ls", "-l"], stdout=subprocess.DEVNULL)
    # print("The exit code was: %d" % list_files.returncode)
    rp_query = subprocess.run(["/home/esther/.local/bin/rpsa_client",
                               "--remote",
                               "--mode=start",
                               f"--hosts={host:s}"])
    print("RP Start exit code was: %d" % rp_query.returncode)


def checkRPitayaConfig(host="10.10.136.229"):
    # list_files = subprocess.run(["ls", "-l"], stdout=subprocess.DEVNULL)
    # print("The exit code was: %d" % list_files.returncode)
    rp_query = subprocess.run(["/home/esther/.local/bin/rpsa_client",
                               "--config",
                               f"--hosts={host:s}",
                               "--get=VV"])
    print("RP exit code was: %d" % rp_query.returncode)
    # The subprocess.run() facilitates this by its input argument:


def task4():
    pass


def task5():
    pass


def firePulse():
    t1 = Thread(target=task1)
    t2 = Thread(target=taskRPitayaStart)
    t3 = Thread(target=taskFireQuantel)

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()


if __name__ == '__main__':
    args = parse_args()

    if args.laserStandby:
        qt = quantel()
        reply = qt.standBy()
        qt.close()
        print(reply)
        exit()

    if args.redpitayaConfig:
        checkRPitayaConfig(host=args.host_rp)
        exit()

    if args.fire:
        firePulse()

    # if your arduino was running on a serial port other than '/dev/ttyACM0/'
    # declare: qt = quantel(serial_port='/dev/ttyXXXX')


"""
    def moveTo(self, motor_number, value):
        Internally sends b'WD{pin_number}:{digital_value}' over the serial
        connection
        Unicode strings must be encoded (e.g. 'hello'.encode('utf-8').
        command = f'M{motor_number} {value}\r\n'.encode('utf-8')
        print(command)
        self.ser.write(command)
        return line
"""

# vim: syntax=python ts=4 sw=4 sts=4 sr et    
