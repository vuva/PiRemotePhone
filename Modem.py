#!/usr/bin/env python3
import datetime
import time
import logging
import re
import serial
import locale

CODEC= "latin1" # ISO/IEC 8859-1  : Work well for German, change this to switch to default UTF-8

PATTERN = re.compile(r'\+CMGL: (?P<index>\d+),'
                 '"(?P<status>.+?)",'
                 '"(?P<number>.+?)",'
                 '("(?P<name>.+?)")?,'
                 '("(?P<date>.+?)")?\r\n'
                 )

AT_COMMAND = {
        'RESET': 'ATZ',
        'SET_TEXT_MODE': 'AT+CMGF=1',
        'QUERY_ALL_MESSAGES': 'AT+CMGL="ALL"',
        'QUERY_UNREAD_MESSAGES': 'AT+CMGL="REC UNREAD"',
        'QUERY_MESSAGE_BY_ID': 'AT+CMGR=%d',
        'SEND_MESSAGE': 'AT+CMGS="%s"',
        'DELETE_MESSAGE': 'AT+CMGD=%d',
             }

# logging.basicConfig(filename='remote-phone.log', filemode='a',format ='%(asctime)s %(name)s %(levelname)s %(message)s', level=logging.DEBUG)
logger = logging.getLogger('modem')

class ModemError(RuntimeError):
    pass


class Message(object):
    """A received SMS message"""

    format = '%y/%m/%d,%H:%M:%S'

    def __init__(self, index, modem, number, date, text):
        self.index = index
        self.modem = modem
        self.number = number
        if date is not None:
            # modem incorrectly reports UTC time rather than local
            # time so ignore time zone info
            date = date[:-3]
            self.date = datetime.datetime.strptime(date, self.format)
        self.text = text



class Modem(object):
    """Provides access to a gsm modem"""
    
    def __init__(self, dev_id):
        self.conn = serial.Serial(dev_id, 9600, timeout=1, rtscts=1)
        # make sure modem is OK
        self.sendCommand(AT_COMMAND['RESET'])
        time.sleep(2)
        self.sendCommand(AT_COMMAND['SET_TEXT_MODE'])

    def getAllSMS(self):
        return self.queryMessages(AT_COMMAND['QUERY_ALL_MESSAGES'])

    def getUnreadSMS(self):
        return self.queryMessages(AT_COMMAND['QUERY_UNREAD_MESSAGES'])
    
    def getSMSByID(self, sms_id):
        return self.queryMessages(AT_COMMAND['QUERY_MESSAGE_BY_ID'] % sms_id)
    
    def sendMessage(self, number, message):
        """Send a SMS message
        message should be no more than 160 ASCII characters.
        """
        self.sendCommand('AT+CMGS="%s"' % number)
        result = self.sendCommand(message + '\x1A', flush=False)
        if result is not None:
            return 'OK'

    def queryMessages(self, command):
        """Return received messages"""
        msgs = []
        text = None
        index = None
        date = None

        response = self.sendCommand(command)

        for line in response[:-1]:
            line = line.decode(CODEC)
            m = PATTERN.match(line)
            if m is not None:
                if text is not None:
                    msgs.append(Message(index, self, number, date, text))
                status = m.group('status')
                index = int(m.group('index'))
                number = m.group('number')
                date = m.group('date')
                text = ''
            elif text is not None:
                if line == '\r\n':
                    text += '\n'
                else:
                    text += line.strip()
        if text is not None:
            msgs.append(Message(index, self, number, date, text))
        return msgs
    
    def delete(self, sms_id):
        response = self.modem.sendCommand(AT_COMMAND['DELETE_MESSAGE'] % sms_id)
        ok = False
        for line in response:
            if 'OK' in line:
                ok = True
        if not ok:
            raise ModemError('Delete of message %d seemed to fail' 
                             % self.index)

    def wait(self, timeout=None):
        """Blocking wait until a message is received or timeout (in secs)"""
        old_timeout = self.conn.timeout
        self.conn.timeout = timeout
        results = self.conn.read()
        logger.debug('wait read "%s"' % results)
        self.conn.timeout = old_timeout
        results = self.conn.readlines()
        logger.debug('after wait read "%s"' % results)
        
    def sendCommand(self, at_command, flush=True):
        logger.debug('sending "%s"' % at_command)
        self.write((at_command + '\r'))
        if flush:
            self.write('\r\n')
            #logger.debug('sending crnl')
        results = self.conn.readlines()
        logger.debug('received "%s"' % results)
        for line in results:
            if 'ERROR' in line.decode(CODEC):
                raise ModemError(results)
        return results

    def write(self, command):
        self.conn.write(command.encode())


    def __del__(self):
        try:
            self.conn.close()
        except AttributeError:
            pass
