import numpy
import socket
import cv2
import time
import threading

myip = "127.0.0.1"
peers = [{"name": "harshit","ip": "127.0.0.1", "recport": 125,"sendport": 126},{"name":"mobile","ip": "127.0.0.1", "recport": 129,"sendport": 128},{"name": "piyush","ip": "127.0.0.1","recport": 122,"sendport": 124}]
threadsnd = list(range(len(peers)))
sock = list(range(len(peers)))
threadrec = list(range(len(peers)))
cap = list(range(len(peers)))
encoded = numpy.zeros((200,200,3))
shut = numpy.zeros(len(peers))

stop = False
def capture(cam):
    global encoded
    cap = cv2.VideoCapture(cam)
    while True:
        ret,frame = cap.read()
        frame = cv2.resize(frame,(300,300))
        encoded = cv2.imencode(".jpg",frame)[1].tobytes()
        if shut.all() or stop:
            cap.release()
            print("peer closed the connection")
            break

def send(sock,cam,i):
    while True:
        sock.sendto(encoded,(peers[i]["ip"],peers[i]["sendport"]))
        if shut.all() or stop:
            sock.close()
            break

def rec(sock,name,i):
  try:
    global stop
    global shut
    while True:
        rec = sock.recv(100000)
        arr = numpy.fromstring(rec,numpy.uint8)
        decimg = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        cv2.imshow(name,decimg)
        if cv2.waitKey(10) == 27: #press esc to close the program
            break
    cv2.destroyWindow(name)
    stop = True
  except ConnectionResetError:
    print("encountered Connection reset error")
    cv2.destroyWindow(name)
    shut[i] = True
    
def start(cam=0):
    
    threadcap = threading.Thread(target=capture, args=(cam,),name = "threadcap")
    threadcap.start()
    time.sleep(2)
    
    for i in range(len(peers)):
        
       
        threadsnd[i] = threading.Thread(target=send, args=(sock[i],cam,i,),)
        threadsnd[i].start()
        
        threadrec[i] = threading.Thread(target=rec, args = (sock[i],peers[i]["name"],i,))
        threadrec[i].start()
        
def startsocket():
    
     for i in range(len(peers)):
        
        sock[i] = socket.socket(family=socket.AF_INET,type=socket.SOCK_DGRAM)
        sock[i].bind((myip,peers[i]["recport"]))

startsocket()

start()