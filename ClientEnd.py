# -*- coding: utf-8 -*-

import socket, sys, select, traceback
from Tkinter import *

from SocketWrapper import *

class Client:

    clientSock = None
    port = 12354
    host = None

    RECV_BUFFER = 4096

    messageList = []

    threadIsAlive = False

    def __init__(self):
        self.host = socket.gethostname()
        self.clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def connectToServer(self):
        self.__connect()

    def __connect(self):
        try:
            self.clientSock.connect((self.host, self.port))
        except:
            print "unable to connect server"


    def closeClient(self):
        if self.threadIsAlive:
            print 'close socket'
            socketSend(self.clientSock, "CLIENT_SHUTDOWN")
            self.clientSock.close()
            self.threadIsAlive = False
        else:
            print 'socket has been closed already'

    def mainLoop(self, tkMsgList):

        self.threadIsAlive = True

        rList = [self.clientSock, sys.stdin]

        try:

            while True:

                readList, writeList, errorList = select.select(rList, [], rList)

                quitProgram = False

                for element in readList:
                    if element == self.clientSock:
                        data = socketRecv(self.clientSock, self.RECV_BUFFER)
                        if not data:
                            print "this connection is not available"
                            quitProgram = True
                        else:

                            if data == 'server msg: SERVER_SHUTDOWN':
                                print "server is shut down"
                                quitProgram = True
                                break
                            print data
                            #self.msgList.insert(END, self.usrName + ': ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '\n ','userColor')
                            tkMsgList.insert(END, data)
                    else:
                        data = sys.stdin.readline()

                        # 当 直接从terminal关闭程序的时候，貌似程序并不会抛出异常
                        # 反之，程序会读取一个空的字符串；此处，我们认为''代表此种情况
                        # 但是是否有更合理的解决方案？
                        if data == 'esc\n' or data == '':
                            quitProgram = True
                            break
                        else:
                            # remove '\n' and append EOD as segmentation sign
                            socketSend(self.clientSock, data[:-1])

                #print 'select error list:', errorList

                if quitProgram:
                    self.closeClient()
                    break

        except KeyboardInterrupt as e:
            # print "KeyboardInterrupt"
            # f = open("keyboard.txt", 'a')
            # traceback.print_exc(file=f)
            # f.flush()
            # f.close()
            print e
            self.closeClient()

        except BaseException as e:
            # killing the thread will trigger
            # the error from the blocked select function
            print e
            self.closeClient()
            sys.exit(1)

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
        #             for element in readList:
        #                 if element == self.clientSock:
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

