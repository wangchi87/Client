# -*- coding: utf-8 -*-

import socket, sys, select, traceback, time, threading

from SocketWrapper import *

class Client:

    clientSock = None
    port = 12354
    host = None

    RECV_BUFFER = 4096
    # messageList = []

    __isSocketAlive = False

    # rList = None
    # wList = None

    hbThread = None
    sendThread = None
    recvThread = None

    msgToSend = []
    msgReceived = []

    def __init__(self):
        self.host = '127.0.0.1'#socket.gethostname()
        self.clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connectToServer(self):
        self.__isSocketAlive = socketConnection(self.clientSock, self.host, self.port)

        # self.hbThread = threading.Thread(target=self.sendHeartBeatPackage)
        # self.hbThread.setDaemon(True)
        # self.hbThread.start()

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

    def popMsgFromQueue(self):
        if len(self.msgReceived) > 0:
            return self.msgReceived.pop()
        else:
            return None

    def sendMsg(self):
        while self.__isSocketAlive:
            if len(self.msgToSend) > 0:
                msg = self.msgToSend.pop()
                socketSend(self.clientSock, msg)
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
                print recvedData
                self.msgReceived.append(recvedData)
            time.sleep(0.1)

    def closeClient(self):
        if self.__isSocketAlive:
            print 'close socket'
            socketSend(self.clientSock, "CLIENT_SHUTDOWN")
            # self.rList.remove(self.clientSock)
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
            socketSend(self.clientSock, "-^-^-pyHB-^-^-")
            time.sleep(0.5)

    # def mainLoop(self, tkMsgList):
    #
    #     self.rList = [self.clientSock]
    #     self.wList = []
    #
    #     quitProgram = False
    #
    #     try:
    #
    #         while self.__isSocketAlive and (not quitProgram):
    #             print self.rList
    #             readList, writeList, errorList = select.select(self.rList, self.wList, self.rList)
    #
    #             for sock in readList:
    #                 if sock == self.clientSock:
    #                     try:
    #                         recvedData = socketRecv(sock, self.RECV_BUFFER)
    #                     except socket.error as err:
    #                         print "failed to receive data", err
    #                         sock.close()
    #                         self.__isSocketAlive = False
    #                         self.rList.remove(sock)
    #                         return
    #                     else:
    #                         if recvedData == 'server msg: SERVER_SHUTDOWN' or (not recvedData):
    #                             print "server is shut down"
    #                             quitProgram = True
    #                             break
    #                         print recvedData
    #                         #self.msgList.insert(END, self.usrName + ': ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '\n ','userColor')
    #                         tkMsgList.insert(END, recvedData)
    #                 # else:
    #                 #     recvedData = sys.stdin.readline()
    #                 #
    #                 #     # 当 直接从terminal关闭程序的时候，貌似程序并不会抛出异常
    #                 #     # 反之，程序会读取一个空的字符串；此处，我们认为''代表此种情况
    #                 #     # 但是是否有更合理的解决方案？
    #                 #     if recvedData == 'esc\n' or recvedData == '':
    #                 #         quitProgram = True
    #                 #         break
    #                 #     else:
    #                 #         # remove '\n' and append EOD as segmentation sign
    #                 #         socketSend(self.clientSock, data[:-1])
    #
    #             if quitProgram:
    #                 self.closeClient()
    #                 break
    #
    #     except KeyboardInterrupt as e:
    #         # print "KeyboardInterrupt"
    #         # f = open("keyboard.txt", 'a')
    #         # traceback.print_exc(file=f)
    #         # f.flush()
    #         # f.close()
    #         print e
    #         self.closeClient()
    #
    #     except select.error as e:
    #         self.closeClient()
    #         print 'Select error', e
    #
    #
    #     except BaseException as e:
    #         # killing the thread will trigger
    #         # the error from the blocked select function
    #         print e
    #         self.closeClient()
    #         sys.exit(1)

        # except SystemExit:
        #     f = open("c:log.txt", 'a')
        #     traceback.print_exc(file=f)
        #     f.flush()
        #     f.close()
        #     self.closeClient()
        #
        # except Exception:
        #     print 'close'
        #     self.closeClient()

        # def __mainLoop(self):
        #
        #     rList = [self.clientSock, sys.stdin]
        #
        #     try:
        #
        #         while True:
        #
        #             readList, writeList, errorList = select.select(rList, [], [])
        #
        #             quitLoop = False
        #
        #             for sock in readList:
        #                 if sock == self.clientSock:
        #                     data = socketRecv(self.clientSock, self.RECV_BUFFER)
        #                     if not data:
        #                         print "this connection is not available"
        #                         quitLoop = True
        #                     else:
        #
        #                         if data == 'server msg: SERVER_SHUTDOWN':
        #                             print "server is shut down"
        #                             quitLoop = True
        #                             break
        #                         print data
        #                 else:
        #                     data = sys.stdin.readline()
        #
        #                     # 当 直接从terminal关闭程序的时候，貌似程序并不会抛出异常
        #                     # 反之，程序会读取一个空的字符串；此处，我们认为''代表此种情况
        #                     # 但是是否有更合理的解决方案？
        #                     if data == 'esc\n' or data == '':
        #                         quitLoop = True
        #                         break
        #                     else:
        #                         # remove '\n' and append EOD as segmentation sign
        #                         socketSend(self.clientSock, data[:-1])
        #
        #             if quitLoop:
        #                 self.closeClient()
        #                 break
        #
        #     except KeyboardInterrupt:
        #         print "KeyboardInterrupt"
        #         f = open("keyboard.txt", 'a')
        #         traceback.print_exc(file=f)
        #         f.flush()
        #         f.close()
        #         self.closeClient()
        #
        #     except SystemExit:
        #         f = open("c:log.txt", 'a')
        #         traceback.print_exc(file=f)
        #         f.flush()
        #         f.close()
        #         self.closeClient()

if __name__ == "__main__":

    client = Client()

