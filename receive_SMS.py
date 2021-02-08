import serial
import time
import sys

PORT='/dev/ttyUSB2'

class LTEModem(object):

    def __init__(self):
        self.open()

    def open(self):
        self.ser = serial.Serial(PORT, 406800, timeout=5)
        self.SendCommand('ATZ\r')
        self.SendCommand('AT+CMGF=1\r')


    def SendCommand(self,command, getline=True):
        self.ser.write(command)
        data = ''
        if getline:
            data=self.ReadLine()
        return data 

    def ReadLine(self):
        data = self.ser.readline()
        print data
        return data 


    def GetAllSMS(self):
        self.ser.flushInput()
        self.ser.flushOutput()

        # command = 'AT+CMGL="REC UNREAD"\r\n'#gets incoming sms that has not been read
        command = 'AT+CMGL="ALL"\r\n'#gets incoming sms that has not been read
        print self.SendCommand(command,getline=True)
        data = self.ser.readall()
        print data

    def ReadSMS(self, sms_id):
        self.ser.flushInput()
        self.ser.flushOutput()
        command='AT+CMGR='+ str(sms_id) + '\r\n'
        print self.SendCommand(command, getline=True)
        data = self.ser.readall()
        print data


h = LTEModem()
# h.GetAllSMS()
h.ReadSMS(4)
