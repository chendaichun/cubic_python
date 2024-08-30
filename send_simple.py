# -*- coding: utf-8 -*-
'''
没有丢包的 cubic
'''
import socket
import time
import random
import numpy as np
import sys
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure

clients = []
#Settings for CUBIC. Working.
addr = "localhost"  #Address
port = 9060         #Port for communication
cwnd = 1            #Congestion Window size
ssthresh = 70       #Slow Start Threshold
timeout = 1         #Timeout limit in seconds
linearConst = 1    #LinCubicear Constant for AIMD
cubeConst = 0.05       #CUBIC Constant
congProb = 50        #Probability of congestion happening
inf = float('inf')  #Infinite constant

seqNumber = 0       #Starting sequence number is 0

"""# Definitions ThisIsADefaultMessage.ShayanIsWorking!"""

sendType = 0
def send(times = 1, msg="B"):
  #Send packets 'times' time. Continue from the seqNumber
  #It adds the thread to clients so later on the ACK would be received
  #It also records the time of sending the packet
  global addr, port, cwnd, ssth, timeout, seqNumber, clients, sendType
  sendType = 0
  for i in range(times):
    clients.append((socket.socket(socket.AF_INET, socket.SOCK_STREAM), time.time(), len(msg)))
    clients[-1][0].connect((addr, port)) #Connect the receiver
    clients[-1][0].send((str(seqNumber)+' '+msg).encode()) #Send with the seqNumber
    seqNumber += 1  #Increment the sequence number

def getack(index = 0):
  #Gets the ACK for the package index.
  #This also acts as the proxy i.e. if the ack gets lost
  global addr, port, cwnd, ssth, timeout, seqNumber, clients, sendType

  if index == 'empty' or index == 'delete' or index == 'flush':
    for i in range(len(clients)):
      clients[i][0].close()
    clients = []

  if len(clients) == 0:
    return 0

  if index == 'all' or index == -1:  #Get all ACKs and return the longest RTT
    index = len(clients)-1

  maxRTT = 0
  maxSeq = 0
  for i in range(index+1):
    tmp = clients[i][0].recv(1024).decode()
    clients[i][0].close()
    nowTime = time.time()-clients[i][1]
    maxRTT = max(maxRTT, nowTime)
    maxSeq = max(maxSeq, clients[i][2])

    if sendType == 0:
      rand = random.randrange(100)
      if rand < congProb: #Congestion Occured
        maxRTT = inf
    if sendType == 1:
      rand = random.random()
      if rand < congProb/100*(maxSeq/11534336):
        maxRTT = inf


  clients = clients[index+1:] #Delete the received sequences
  if maxRTT > timeout:
    maxRTT = inf
  return maxRTT

getack('flush')

#Round Trip Time
send()
print(getack())

"""# CUBIC Simple"""


getack('flush')

#TCP CUBIC. Working. Without packet losses.

history = []

flag = 0  #To mark the last time linearly increased
justBeforeLoss = 0
for i in range(200):
  #sys.stdout.write("\r Progress Done: " + str(int(i))+ " CWND: "+str(cwnd)+ " ssthresh: "+str(ssthresh))
  #sys.stdout.flush()
  ssthresh = 3
  print("\r Progress Done: " + str(int(i))+ " CWND: "+str(cwnd)+ " ssthresh: "+str(ssthresh))
  history.append(cwnd)
  send(cwnd)
  tmp = getack('all')
  if tmp == inf:  #Congestion or timeout happened
    print("Congestion Happened")
    if cwnd == int(justBeforeLoss/2):
      justBeforeLoss = int(justBeforeLoss/2)
      cwnd = max(1, int(cwnd/2))
      continue
    ssthresh = int(justBeforeLoss/2)
    cwnd = max(1, ssthresh)
    continue

  if i < 10: #In the Slow Start Phase
    print("Slow start phase")
    justBeforeLoss = cwnd
    cwnd *= 2

  #elif cwnd >= ssthresh:  #AIMD Phase
  else:
    print("Cubic Phase")
    justBeforeLoss = cwnd
    pred = int(int((ssthresh*2-cwnd)/linearConst)**3)
    pred = (ssthresh*2-cwnd)/2.6/cubeConst
    print("pred:", pred, "incement by:", cubeConst*pred)
    cwnd += int(max(1, cubeConst*pred))

print(history)

figure(figsize=(14, 6), dpi=200)
plt.plot(range(len(history)), history)
plt.scatter(range(len(history)), history)
#plt.axhline(y=ssthresh, color='r', linestyle='-')
plt.xlabel("time", fontsize=18)
plt.ylabel("Congestion Window", fontsize=18)
plt.savefig("./1234.png")

