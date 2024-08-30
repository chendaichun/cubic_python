import socket
import time
import random
import numpy as np
import sys
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
clients = []
# CUBIC 的设置，用于丢包的情况。
inf = float('inf')  # 无穷大常量
addr = "localhost"  # 地址
port = 9060         # 通信端口
cwnd = 1            # 拥塞窗口大小
ssthresh = inf      # 慢启动阈值（无穷大，表示没有设限）
timeout = 0.33      # 超时时间限制（以秒为单位）
linearConst = 50000 # 线性增量常数（用于加性增量乘性减量，AIMD）
cubeConst = 0.1     # CUBIC 常数（用于 CUBIC 算法中的窗口调整）
congProb = 0
    # 拥塞发生的概率，百分比表示
# 这个拥塞发生的概率应该是随机发生的概率，但是实际上的链接之中也会发生拥塞；

seqNumber = 0       # 初始序列号为 0

"""# Definitions"""

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
  clients.append((socket.socket(socket.AF_INET, socket.SOCK_STREAM), time.time(), times))
  clients[-1][0].connect((addr, port)) #Connect the receiver
  clients[-1][0].settimeout(timeout)
  clients[-1][0].send((str(seqNumber)+' '+msg * times).encode()) #Send with the seqNumber
  seqNumber += 1  #Increment the sequence number

def getack(index = 0):
  #Gets the ACK for the package index.
  #This also acts as the proxy i.e. if the ack gets lost
  # 获取指定包的 ACK（确认消息）。
  # 这也充当了代理的角色，即如果 ACK 丢失

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
      if rand < congProb: #拥塞发生 这里好像没啥用。。。。  
        maxRTT = inf
    if sendType == 1:
      rand = random.random()
      if rand < congProb/100*(maxSeq/11534336):
        maxRTT = inf


  clients = clients[index+1:] #Delete the received sequences
  if maxRTT > timeout:
    maxRTT = inf
  return maxRTT

"""# CUBIC Realistic"""


getack('flush')

#TCP CUBIC. Working. Handling packet losses

history = [] # 带宽？？？
sshistory = []
btrans_list = [0]
startinSS = ssthresh

flag = 0  #To mark the last time linearly increased
justBeforeLoss = 0

startingTime = time.time()
bTrans = 0 #Bytes Transfered

for i in range(200):
  #sys.stdout.write("\r Progress Done: " + str(int(i))+ " CWND: "+str(cwnd)+ " ssthresh: "+str(ssthresh))
  #sys.stdout.flush()
  print("\r Progress Done: " + str(int(i))+ " CWND: "+str(cwnd)+ " ssthresh: "+str(ssthresh)+ " Running time: "+str(time.time()-startingTime),  " Mega Bytes:", int(bTrans/1024/1024))
  if time.time()-startingTime > 4500:
    break
  history.append(cwnd)
  sshistory.append(ssthresh)
  send2(cwnd)
  tmp = getack('all')
  if tmp == inf:  #Congestion or timeout happened
    print(">>> Congestion Happened")
    if ssthresh == int(justBeforeLoss/2):
      ssthresh = int(ssthresh/2)
      cwnd = ssthresh
      continue
    ssthresh = int(justBeforeLoss/2)
    cwnd = ssthresh   #TCP Reno
    continue
  bTrans += cwnd #Congestion did not happen. Add
  btrans_list.append(bTrans)
  if cwnd < ssthresh: #In the Slow Start Phase
    print("Slow start phase")
    justBeforeLoss = cwnd
    cwnd *= 2

  #elif cwnd >= ssthresh:  #AIMD Phase
  else:
    print("Cubic Phase")
    justBeforeLoss = cwnd
    pred = int(int((ssthresh*2-cwnd)/linearConst)**3)
    pred = int(abs(ssthresh*2-cwnd)**1)/2/cubeConst
    print("pred:", pred, "incement by:", cubeConst*pred)
    cwnd += int(max(1, cubeConst*pred))

print("Bytes Transfered:", bTrans, " Kilo Bytes:", int(bTrans/1024), " Mega Bytes:", int(bTrans/1024/1024))


#Time
start_time = time.time()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", 9060))
client.send("1 testToFindTime".encode())
print(client.recv(1024).decode())

print((time.time() - start_time))


figure(figsize=(14, 6), dpi=200)
plt.plot(range(len(btrans_list)), btrans_list/1024/1024, label="CWND")
plt.scatter(range(len(btrans_list)), btrans_list/1024/1024)
#plt.axhline(y=ssthresh, color='r', linestyle='-')

plt.xlabel("Iteration", fontsize=18)
plt.legend(loc="upper left")
plt.ylabel("Bytes", fontsize=18)
plt.savefig("./12345.png")
