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

    __msgToSend = []
    __chatMsgRecved = []
    __sysMsgRecved = []

    __dataBuffer = ''
    __dataBufMutexLock = None

    __msgHeaderSize = 13

    def __init__(self):
        self.host = '127.0.0.1'#socket.gethostname()
        self.clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__dataBufMutexLock = threading.Lock()

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

        self.proMsgThread = threading.Thread(target=self.readMsgFromBuf)
        self.proMsgThread.setDaemon(True)
        self.proMsgThread.start()

        return self.__isSocketAlive

    def isSocketAlive(self):
        return self.__isSocketAlive

    def appendToMsgSendingQueue(self, msg):
        self.__msgToSend.append(msg)

    def popChatMsgFromQueue(self):
        if len(self.__chatMsgRecved) > 0:
            return self.__chatMsgRecved.pop(0)
        else:
            return None

    def appendSysMsg(self, msg):
        self.__sysMsgRecved.append(msg)

    def popSysMsgFromQueue(self):
        if len(self.__sysMsgRecved) > 0:
            return self.__sysMsgRecved.pop(0)
        else:
            return None

    def sendMsg(self):
        while self.__isSocketAlive:
            if len(self.__msgToSend) > 0:
                msg = self.__msgToSend.pop(0)
                self.__safeSocketSend(msg)
            time.sleep(0.1)

    def recvMsg(self):
        # append received data to data buffer
        while self.__isSocketAlive:
            try:
                recvedData = self.clientSock.recv(self.RECV_BUFFER)
            except socket.error as err:
                print "failed to receive data", err
                self.closeClient()
                return
            else:
                if (not recvedData):
                    print "program terminated"
                    break
                while 1:
                    if self.__dataBufMutexLock.acquire():
                        self.__dataBuffer += recvedData
                        self.__dataBufMutexLock.release()
                        break

    def readMsgFromBuf(self):
        # process msg in data buffer
        while self.__isSocketAlive:
            while len(self.__dataBuffer) > 0:

                msgStartIndex = self.__dataBuffer.find('msgHeader')

                if msgStartIndex > 0:
                    print("there might be error in data buffer")

                msgHeaderEndIndex = msgStartIndex + self.__msgHeaderSize
                msgHeader = self.__dataBuffer[msgStartIndex:msgHeaderEndIndex]
                headPack = struct.unpack('!9sI', msgHeader)
                msgBodySize = headPack[1]
                msgBodyEndIndex = msgHeaderEndIndex + msgBodySize
                msgBody = self.__dataBuffer[msgHeaderEndIndex: msgBodyEndIndex]
                # print msgBody
                self.__parseRecvedData(msgBody)

                if self.__dataBufMutexLock.acquire():
                    self.__dataBuffer = self.__dataBuffer[msgStartIndex + self.__msgHeaderSize + msgBodySize:]
                    self.__dataBufMutexLock.release()



    def __parseRecvedData(self, msg):
        '''
        the protocol of msg we used here are as following:
        all the message are packed in a dict structure:

        message can be attributed as system message or chat message, which leads to the dict structure:
        1. {'SysMsg': {a:b}}:
            a field are used to identify the types of system msg, for instance: "SysLoginRequest"
            b field are usually the real msg that we want to send, it could be a str or dict, according to the type of a field
        2. {'ChatMsg': {a:b}}:
            a field here is to identify to whom the chat msg is to send:
                'toAll' means: we want to broadcast the msg
                if a field is a user name, it means we want to send msg privately
            b field is the msg we want to send
        '''
        try:
            data = json.loads(msg)
        except ValueError as e:
            print 'exception in loading json data', e
            print msg
        else:
            print data
            for k, v in data.items():
                # print k, v
                if k == 'ChatMsg':
                    # v will be a dict {'toAll': msg} or {'XXX': msg}
                    # print v
                    self.__chatMsgRecved.append(v)
                elif k == 'SysMsg':
                    # v will be a dict, like {'SysLoginRequestAck': 'xxx'} or {'allUsernames': {}}
                    self.__sysMsgRecved.append(v)


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
            time.sleep(2)

    def __safeSocketSend(self, msg):
        if not socketSend(self.clientSock, msg):
            self.__isSocketAlive = False
            self.closeClient()

if __name__ == "__main__":

    client = Client()

