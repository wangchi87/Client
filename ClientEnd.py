# -*- coding: utf-8 -*-

import json
import threading
import time

from SocketWrapper import *


class Client:

    clientSock = None
    port = 12354
    host = None

    RECV_BUFFER = 4096

    __isSocketAlive = False

    hbThread = None
    sendThread = None
    recvThread = None

    msgToSend = []
    __chatMsgRecved = []
    __sysMsgRecved = []
    __usrOnlineTimeMsg = []

    def __init__(self):
        self.host = '127.0.0.1'#socket.gethostname()
        self.clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connectToServer(self):
        self.__isSocketAlive = socketConnection(self.clientSock, self.host, self.port)

        self.hbThread = threading.Thread(target=self.sendHeartBeatPackage)
        self.hbThread.setDaemon(True)
        self.hbThread.start()

        self.recvThread = threading.Thread(target=self.recvMsg)
        self.recvThread.setDaemon(True)
        self.recvThread.start()

        self.sendThread = threading.Thread(target=self.sendMsg)
        self.sendThread.setDaemon(True)
        self.sendThread.start()

        return self.__isSocketAlive

    def isSocketAlive(self):
        return self.__isSocketAlive

    def addMsgToQueue(self, msg):
        self.msgToSend.append(msg)

    def popChatMsgFromQueue(self):
        if len(self.__chatMsgRecved) > 0:
            return self.__chatMsgRecved.pop()
        else:
            return None

    def popSysMsgFromQueue(self):
        if len(self.__sysMsgRecved) > 0:
            return self.__sysMsgRecved.pop()
        else:
            return None

    def popUsrOnlineTimeMsgFromQueue(self):
        if len(self.__usrOnlineTimeMsg) > 0:
            return self.__usrOnlineTimeMsg.pop()
        else:
            return None

    def sendMsg(self):
        while self.__isSocketAlive:
            if len(self.msgToSend) > 0:
                msg = self.msgToSend.pop()
                self.__safeSocketSend(msg)
            time.sleep(0.1)

    def recvMsg(self):
        while self.__isSocketAlive:
            try:
                recvedData = socketRecv(self.clientSock, self.RECV_BUFFER)
            except socket.error as err:
                print "failed to receive data", err
                self.closeClient()
                return
            else:
                if (not recvedData):
                    print "program terminated"
                    break
                if recvedData == 'server msg: SERVER_SHUTDOWN':
                    print "server is shut down"
                    break
                # print recvedData
                self.__parseRecvedData(recvedData)
            time.sleep(0.1)

    def __parseRecvedData(self, msg):
        try:
            data = json.loads(msg)
        except ValueError as e:
            print 'exception in loading json data', e
            print msg
        else:
            # print data
            for k, v in data.items():
                if k == 'SysLoginAck' or k == 'SysRegisterAck':
                    self.__sysMsgRecved.append(v)
                elif k == 'Chat':
                    self.__chatMsgRecved.append(v)
                elif k == 'SysUsrOnlineDurationMsg':
                    self.__usrOnlineTimeMsg.append(v)

    def closeClient(self):
        if self.__isSocketAlive:
            print 'close socket'
            self.__safeSocketSend("CLIENT_SHUTDOWN")
            self.clientSock.close()
            self.__isSocketAlive = False
        else:
            print 'socket has been closed already'

    def sendHeartBeatPackage(self):
        '''
        There are two benefits of sending heart beat package:
        1. the heart beat package will allow the server to be aware of whether the client is ALIVE or not
        2. the heart beat package also serve as PASSWORD to maintain a connection with the server,
            so that the connection which is NOT raised from our client program will be rejected(closed by the server)
        '''
        while self.__isSocketAlive:
            self.__safeSocketSend("-^-^-pyHB-^-^-")
            time.sleep(0.5)

    def __safeSocketSend(self, msg):
        if not socketSend(self.clientSock, msg):
            self.__isSocketAlive = False

if __name__ == "__main__":

    client = Client()

