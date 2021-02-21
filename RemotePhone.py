#!/usr/bin/env python3
import time
import sys
import argparse
import logging
import paho.mqtt.publish as publish

from Modem import *

logging.basicConfig(filename='remote-phone.log', filemode='a',format ='%(asctime)s %(name)s %(levelname)s %(message)s', level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

logger = logging.getLogger('remote-phone')

PORT='/dev/ttyUSB2'

MQTT_HOST = '192.168.0.81'
MQTT_TOPIC = '/PiRemotePhone/new_sms'
GET_SMS_INTERVAL=3600

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Query SMS from SIM card.')
    parser.add_argument('-a','--all', required=False, action="store_true", help='Get all messages in SIM card')
    parser.add_argument('-u','--unread', required=False, action="store_true", help='Get unread messages in SIM card')
    parser.add_argument('-m','--id', required=False, help='Message ID')
    parser.add_argument('-r','--remove', required=False, help='Remove Message ')
    parser.add_argument('-s','--send', required=False, nargs=2, help='Send message. Parameters: recipient content')
    parser.add_argument('-d','--daemon', required=False, action="store_true",help='Daemon mode')
    args = parser.parse_args()
    
    modem = Modem(PORT)
    if args.all:
        sms_list =modem.getAllSMS()
        for sms in sms_list:
            logger.info("\n%d.\tSender: %s \nReceived: %s \n%s\n", sms.index, sms.number ,sms.date, sms.text)

    if args.unread:
        sms_list =modem.getUnreadSMS()
        for sms in sms_list:
            logger.info("\n%d.\tSender: %s \nReceived: %s \n%s\n", sms.index, sms.number ,sms.date, sms.text)
    
    if args.id is not None:
        sms_list =modem.getSMSByID(args.id)
        for sms in sms_list:
            logger.info("\n%d.\tSender: %s \nReceived: %s \n%s\n", sms.index, sms.number ,sms.date, sms.text)

    if args.remove is not None:
        sms_list =modem.delete(remove)
        for sms in sms_list:
            logger.info("\n%d.\tSender: %s \nReceived: %s \n%s\n", sms.index, sms.number ,sms.date, sms.text)

    if args.send is not None:
        result=modem.sendMessage(args.send[0],args.send[1])
        if result is not None:
            logger.info("\nMessage sent.")

    if args.daemon:
        while True:
            sms_list =modem.getUnreadSMS()
            for sms in sms_list:
                message="\n%d.\tSender: %s \nReceived: %s \n%s\n" % (sms.index, sms.number ,sms.date, sms.text)
                publish.single(topic=MQTT_TOPIC, payload=message, hostname=MQTT_HOST)
                logger.debug('\nPublished: ', message)

            time.sleep(GET_SMS_INTERVAL)
