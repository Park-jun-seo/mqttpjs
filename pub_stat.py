import paho.mqtt.client as mqtt
import time
import psutil as ps
from datetime import datetime
from datetime import timedelta
import pandas as pd
import os
import re
import numpy as np
count = 0

host = "192.168.0.13"
#host = "192.168.43.226"

def on_connect(client, userdata, flags, rc):
    print("Connect result: {}".format(mqtt.connack_string(rc)))
    client.connected_flag = True

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed with QoS: {}".format(granted_qos[0]))

def on_message(client, userdata, msg):
    global count
    count +=1
    payload_string = msg.payload.decode('utf-8')
    print("{:d} Topic: {}. Payload: {}".format(count, msg.topic, payload_string))

def pubTempData(client, freq=10, limit=100):
    delta = 1/freq
    
    for i in range(limit*freq):
        ti = datetime.now()
        temp = os.popen("vcgencmd measure_temp").readline()
        da = re.findall(r'\d+\.\d+',temp.rstrip())[0]
        usemem = ps.virtual_memory()[3]/(1024**2)
        totalmem = ps.virtual_memory()[0]/(1024**2)
        cpups = ps.cpu_percent()
        cum1 = '{:s}'.format(ti.strftime("%Y-%m-%d %H:%M:%S.%f"))
        cum2 = "{:s},{:.1f},{:.1f},{:.1f}".format(da,cpups,totalmem,usemem)
    
        #row = 'temp_time({:s}),temp_data("{:s},{:.1f},{:.1f},{:.1f}")'.format(ti.strftime("%Y-%m-%d %H:%M:%S.%f"),da,cpups,totalmem,usemem)
        cum3 = cum1 + ','+cum2
        client.publish("cpu/temp",payload=cum3, qos=1)
        if i%freq == 0:
            #print('%d temp_time(%s), temp_data("%s")'%(i,cum1,cum2))
            print("%d,%s"%(i,cum3))
            #print("%d,%s %s"%(i,cum1,cum2))
            #print(ps.cpu_percent())
            #temp_time(2020-05-29 15:58:08.742108), temp_data("52.1,27.4,874.5,258.7")
        time.sleep(delta)

if __name__ == "__main__":
    print ("get client")
    client = mqtt.Client("CPU_TEMP_PUB01")
    client.username_pw_set('pjs', password='4654')
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    print ("Try to connect {} ".format(host))
    client.connect(host, port=1883, keepalive=120)
    print ("connected {} ".format(host))
    client.loop_start()
    pubTempData(client)

    print ("sleep end")
    client.loop_stop()
