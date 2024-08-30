"""# REALISTIC

# Reno Realistic
"""
import socket
import time
import random
import numpy as np
import sys
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
clients = []
#Settings for RENO. REALISTIC.
inf = float('inf')
addr = "localhost"  #Address
port = 9060         #Port for communication
cwnd = 1            #Congestion Window size
ssthresh = inf       #Slow Start Threshold
timeout = 0.33         #Timeout limit in seconds
linearConst = 70000    #LinCubicear Constant for AIMD
cubeConst = 0.1     #CUBIC Constant
congProb = 100        #Probability in Percentage of congestion happening
  #Infinite constant

seqNumber = 0       #Starting sequence number is 0

sendType = 0
def send(times = 1, msg="ThisIsADefaultMessage.ShayanIsWorking!"):
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

def send2(times = 1, msg="A"):
  #Send packets 'times' time. Continue from the seqNumber
  #It adds the thread to clients so later on the ACK would be received
  #It also records the time of sending the packet
  global addr, port, cwnd, ssth, timeout, seqNumber, clients, sendType
  sendType = 1
  print("hah1.7")
  clients.append((socket.socket(socket.AF_INET, socket.SOCK_STREAM), time.time(), times))
  print("hah1.71")
  clients[-1][0].settimeout(5)  # 设置超时为5秒

  clients[-1][0].connect((addr, port)) #Connect the receiver
  print("hah1.73")
  clients[-1][0].send((str(seqNumber)+' '+msg * times).encode()) #Send with the seqNumber
  print("hah1.8")
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

#TCP RENO REALISTIC

history = []
sshistory = []

startinSS = ssthresh
congestNum = 0

startingTime = time.time()
bTrans = 0 #Bytes Transfered

flag = 0  #To mark the last time linearly increased
justBeforeLoss = 0
for i in range(200):
  print("\r Progress Done: " + str(int(i))+ " CWND: "+str(cwnd)+ " ssthresh: "+str(ssthresh)+ " Running time: "+str(time.time()-startingTime),  " Mega Bytes:", int(bTrans/1024/1024))
  #sys.stdout.flush()
  sshistory.append(ssthresh)
  if time.time()-startingTime > 45:
    break
  history.append(cwnd)
  send2(cwnd)
  tmp = getack('all')
  if tmp == inf:  #Congestion or timeout happened
    print(">>> Congestion Happened")
    congestNum += 1
    if ssthresh == int(justBeforeLoss/2):
      ssthresh = int(ssthresh/2)
      cwnd = ssthresh
      continue
    ssthresh = int(justBeforeLoss/2)
    cwnd = ssthresh   #TCP Reno
    continue

  bTrans += cwnd #Congestion did not happen. Add

  if cwnd < ssthresh: #In the Slow Start Phase
    justBeforeLoss = cwnd
    cwnd *= 2

  elif cwnd >= ssthresh:  #AIMD Phase
    justBeforeLoss = cwnd
    cwnd += linearConst

print("Bytes Transfered:", bTrans, " Kilo Bytes:", int(bTrans/1024), " Mega Bytes:", int(bTrans/1024/1024), " Congest Num:", congestNum)

figure(figsize=(14, 6), dpi=200)
plt.plot(range(len(history)), history, label="CWND")
plt.scatter(range(len(history)), history)
#plt.axhline(y=ssthresh, color='r', linestyle='-')

plt.xlabel("Iteration", fontsize=18)
plt.legend(loc="upper left")
plt.ylabel("Bytes", fontsize=18)
plt.savefig("./12345.png")
