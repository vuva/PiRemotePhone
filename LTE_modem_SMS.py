import serial
import time
import sys
import argparse
# import log

PORT='/dev/ttyUSB2'

class LTEModem(object):

    def __init__(self):
        self.open()

    def open(self):
        self.ser = serial.Serial(PORT, 406800, timeout=5)
        self.sendCommand('ATZ\r')
        self.sendCommand('AT+CMGF=1\r')


    def sendCommand(self,command, getline=True):
        self.ser.write(command)
        data = ''
        if getline:
            data=self.readLine()
        time.sleep(1)
        return data 

    def readLine(self):
        data = self.ser.readline()
        print data
        return data 


    def getAllSMS(self):
        self.ser.flushInput()
        self.ser.flushOutput()

        command = 'AT+CMGL="ALL"\r\n'#gets all SMS in SIM card 
        self.sendCommand(command)
        data = self.ser.readall()
        print data

    def getUnreadSMS(self):
        self.ser.flushInput()
        self.ser.flushOutput()

        command = 'AT+CMGL="REC UNREAD"\r\n'#gets incoming sms that has not been read
        self.sendCommand(command)
        data = self.ser.readall()
        print data

    def readSMS(self, sms_id):
        self.ser.flushInput()
        self.ser.flushOutput()
        command='AT+CMGR='+ str(sms_id) + '\r\n'
        self.sendCommand(command)
        data = self.ser.readall()
        print data

    def sendMessage(self, recipient, content):
        command = '''AT+CMGS="''' + recipient + '''"\r'''
        self.sendCommand(command)
        command = content + "\r"
        self.sendCommand(command)
        command = chr(26) 
        self.sendCommand(command)
        # self.ser.write('''AT+CMGS="''' + recipient + '''"\r''')
        # time.sleep(1)
        # self.ser.write(content + "\r")
        # time.sleep(1)
        # self.ser.write(chr(26))
        # time.sleep(1)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Query SMS from SIM card.')
    parser.add_argument('-a','--all', required=False, action="store_true", help='Get all messages in SIM card')
    parser.add_argument('-u','--unread', required=False, action="store_true", help='Get unread messages in SIM card')
    parser.add_argument('-m','--id', required=False, help='Message ID')
    parser.add_argument('-s','--send', required=False, nargs=2, help='Send message. Parameters: recipient content')
    args = parser.parse_args()
    
    modem = LTEModem()
    if args.all:
        modem.getAllSMS()

    if args.unread:
        modem.getUnreadSMS()
    
    if args.id is not None:
        modem.readSMS(args.id)

    if args.send is not None:
        modem.sendMessage(args.send[0],args.send[1] )
