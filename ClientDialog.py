# -*- coding: UTF-8 -*-

import signal

from ClientEnd import *
from Room import *


# login window
class LoginWindow(Toplevel):
    '''
    this class is used to create a login window
    '''

    __client = None
    mainFrm = None
    __usrName = None

    def __init__(self, mainFrm, client):
        Toplevel.__init__(self)
        self.mainFrm = mainFrm
        self.configureUI()

        self.__client = client
        self.protocol('WM_DELETE_WINDOW', self.closeDialog)

    def configureUI(self):
        self.title(u'登录窗口')
        logFrmPos = '%dx%d+%d+%d' % (325, 330, (1500 - 400) / 2, (900 - 300) / 2)
        self.geometry(logFrmPos)
        self.resizable(width=True, height=True)

        self.logFrm = Frame(self)
        self.logLeft = Frame(self, width=70, height=330)
        self.logRight = Frame(self, width=70, height=330)
        self.logLeft.grid(row=0, column=0)
        self.logFrm.grid(row=0, column=1)
        self.logRight.grid(row=0, column=2)
        # self.logFrm.place(x=0, y=0, width=250, height=330)

        self.logCaption = Label(self.logFrm, text=u'登录窗口')

        self.logUNlabel = Label(self.logFrm, text=u'用户名')
        self.logPWDlabel = Label(self.logFrm, text=u'密码')
        self.logInfo = Label(self.logFrm)

        self.logUsrName = Entry(self.logFrm, text=u'netease1')
        self.logUsrPWD = Entry(self.logFrm, text=u'1234', show='*')

        self.logBtnEnter = Button(self.logFrm, text=u'登录', command=self.enterBtn)
        self.logBtnRegist = Button(self.logFrm, text=u'注册', command=self.registBtn)

        self.logCaption.pack(pady=15)
        self.logUNlabel.pack(pady=5)
        self.logUsrName.pack(pady=5)
        self.logPWDlabel.pack(pady=5)
        self.logUsrPWD.pack(pady=5)
        self.logInfo.pack(pady=5)
        self.logBtnEnter.pack(pady=5)
        self.logBtnRegist.pack(pady=5)

    def tryLogin(self):

        self.logBtnEnter['state'] = 'disabled'

        if self.mainFrm.hasAlreadyLoggedIn():
            print "already logged in"
            return False

        self.__usrName = self.logUsrName.get()
        password = self.logUsrPWD.get()

        jstr = packageSysMsg('SysLoginRequest', {self.__usrName: password})
        self.__client.appendToMsgSendingQueue(jstr)

        # wait for system login msg replied from server
        startTime = time.time()
        while 1:
            if time.time() - startTime > 120:
                self.logInfo['text'] = "Failed to login, please try again"
                self.logBtnEnter['state'] = 'normal'
                return False

            sysMsg = self.__client.popSysMsgFromQueue()

            # sysMsg is something like {"SysLoginAck": "Successful login"}
            if sysMsg == None:
                time.sleep(0.002)
            elif sysMsg.keys()[0] == 'SysLoginAck':
                break
            else:
                self.__client.appendSysMsg(sysMsg)

        if sysMsg is not None:
            if sysMsg.values()[0] == 'Successful login':
                self.mainFrm.usrLoggedIn()
                return True
            else:
                self.logInfo['text'] = sysMsg.values()[0]
            self.logBtnEnter['state'] = 'normal'
            return False

    def enterBtn(self):
        if self.tryLogin():
            self.destroy()
            self.mainFrm.deiconify()
            self.mainFrm.setUsrName(self.__usrName)

            self.mainFrm.queryAllOnlineClients()

    def registBtn(self):
        self.logBtnRegist['state'] = 'disabled'

        if self.mainFrm.hasAlreadyLoggedIn():
            self.logBtnRegist['state'] = 'normal'
            return False

        self.__usrName = self.logUsrName.get()
        password = self.logUsrPWD.get()

        jstr = packageSysMsg('SysRegisterRequest', {self.__usrName: password})
        self.__client.appendToMsgSendingQueue(jstr)

        # wait for system registration reply msg from server
        startTime = time.time()
        while 1:
            if time.time() - startTime > 120:
                self.logInfo['text'] = "Failed to register, please try again"
                self.logBtnRegist['state'] = 'normal'
                return

            sysMsg = self.__client.popSysMsgFromQueue()

            # sysMsg is something like {"SysRegisterAck": "Successful registration"}
            if sysMsg == None:
                time.sleep(0.2)
            elif sysMsg.keys()[0] == 'SysRegisterAck':
                break
            else:
                self.__client.appendSysMsg(sysMsg)
                time.sleep(0.2)

        if sysMsg is not None:
            if sysMsg.values()[0] == 'Succesful registration':
                self.logInfo['text'] = sysMsg.values()[0]
                self.logBtnRegist['state'] = 'normal'
                return True
            else:
                self.logInfo['text'] = sysMsg.values()[0]
            self.logBtnRegist['state'] = 'normal'
            return False

    def closeDialog(self):
        self.__client.closeClient()
        self.mainFrm.destroy()


class Dialog(Tk):
    __usrName = 'usrName'
    __loginWin = None
    __client = None

    __loggedIn = False

    __sysMsgThread = None
    __chatMsgThread = None

    # manage private rooms, KEY is usrname, value is the handle of room object
    __privateRoomLists = {}

    # roomLists maintain the rooms the client are in or created
    # key is room name, value is the handle of room object
    __roomLists = {}

    __createRoomWin = None
    __enterRoomWin = None

    def __init__(self):
        Tk.__init__(self)
        self.title(u"聊天大厅")
        self['background'] = 'grey'
        self.configureUI()
        self.withdraw()
        self.protocol('WM_DELETE_WINDOW', self.closeDialog)

        self.__connect()

        self.after(100, self.__processRecevdMsg)

        if self.__client.isSocketAlive():
            self.__loginWin = LoginWindow(self, self.__client)
        else:
            print 'failed to connect server'
            sys.exit(1)

        self.mainloop()

    def hasAlreadyLoggedIn(self):
        return self.__loggedIn

    def usrLoggedIn(self):
        self.__loggedIn = True

    def usrLoggedOut(self):
        self.__loggedIn = False

    def getUsrName(self):
        return self.__usrName

    def __connect(self):
        self.__client = Client()
        self.__client.connectToServer()

    def setUsrName(self, myStr):
        self.__usrName = myStr
        self.textLabelUsrName['text'] = myStr
        print self.__usrName

    def __sendMsgBtn(self):
        usrMsg = self.msg.get('0.0', END)
        self.__displayNewMsg(self.__usrName, usrMsg, 'userColor')
        self.msg.delete('0.0', END)
        data = packagePublicChatMsg(self.__usrName, usrMsg)
        self.__client.appendToMsgSendingQueue(data)

    def closeDialog(self):
        self.__client.closeClient()
        self.destroy()

        for pr in self.__privateRoomLists.values():
            pr.closeRoom()

    def __processRecevdMsg(self):
        self.__processChatMsg()
        self.__processSysMsg()
        self.after(100, self.__processRecevdMsg)

    def __processChatMsg(self):
        if self.__client.isSocketAlive() and self.hasAlreadyLoggedIn():
            msgDict = self.__client.popChatMsgFromQueue()
            if msgDict is not None:
                # print msgDict
                for k, v in msgDict.items():

                    # k is the msg type: 'toAll', 'toClient' or 'toRoom'
                    if k == 'toAll':
                        # v is like [sender, msg]
                        usr = v[0]
                        usrMsg = v[1]
                        self.__displayNewMsg(usr, usrMsg)

                    elif k == 'toClient' and v[1] == self.__usrName:
                        # v is like [sender, receiver, msg]
                        sender = v[0]
                        prvtMsg = v[2]
                        self.__displayNewMsg(sender + " (private msg)", prvtMsg)
                        # pr = PrivateRoom('a', 'v', self.__client, self)
                        # pr.mainloop()

                    elif k == 'toRoom':
                        sender = v[0]
                        roomName = v[1]
                        roomMsg = v[2]

                        roomWin = self.__roomLists[roomName]
                        roomWin.displayNewMsg(sender, roomMsg)

    def __displayNewMsg(self, usrname, msg, config=''):
        # append msg to list component
        self.msgList['state'] = 'normal'
        msgTime = time.strftime(" %Y-%m-%d %H:%M:%S", time.localtime()) + '\n'
        self.msgList.insert(END, usrname + ': ' + msgTime + msg, config)
        self.msgList['state'] = 'disabled'

    def queryAllOnlineClients(self):
        keyMsg = "SysAllOnlineClientsRequest"
        data = packageSysMsg(keyMsg, '')
        self.__client.appendToMsgSendingQueue(data)

    def __processSysMsg(self):
        if self.__client.isSocketAlive() and self.hasAlreadyLoggedIn():
            sysMsg = self.__client.popSysMsgFromQueue()
            if sysMsg:
                self.__analyseSysMsg(sysMsg)

    def __analyseSysMsg(self, sysMsg):
        # print 'sysMsg: ', sysMsg
        for k, v in sysMsg.items():
            if k == 'SysUsrOnlineDurationMsg':
                self.__setUsrTime(v)

            if k == 'SysAllOnlineClientsAck':
                # case: {'allOnlineUsernames': ['usr1', 'usr5', 'usr4']}
                if v.keys()[0] == 'allOnlineUsernames':
                    allCurrentUsers = self.userList.get(0, self.userList.size())
                    for e in v.values()[0]:
                        if e != self.__usrName and e not in allCurrentUsers:
                            self.userList.insert(END, e)

            # other user login
            if k == 'SysUsrLogin' and v != self.__usrName:
                # print 'SysUsrLogin', self.userList.size(), v
                allCurrentUsers = self.userList.get(0, self.userList.size())
                if v not in allCurrentUsers:
                    self.userList.insert(END, v)

            # other user log out
            if k == 'SysUsrLogOut' and v != self.__usrName:
                for i in range(0, self.userList.size()):
                    if v == self.userList.get(i):
                        self.userList.delete(i)

            if k == "SysCreateRoomAck":
                roomName = v.keys()[0]
                msg = v.values()[0]

                self.__createRoomWin.withdraw()
                if msg == 'Successful Room Creation':
                    self.__roomLists[roomName].showRoom()
                elif msg == 'Room already exists':
                    self.__roomLists[roomName].showRoom()

            if k == 'SysEnterRoomAck':
                roomName = v.keys()[0]
                msg = v.values()[0]
                # print 'room list', self.__roomLists
                self.__enterRoomWin.withdraw()
                if msg == 'Successfully Enter The Room':
                    self.__roomLists[roomName].showRoom()
                elif msg == 'Already In The Room':
                    self.__roomLists[roomName].showRoom()
                elif msg == 'Room Not Exists':
                    pass

            if k == 'SysRoomListAck':
                self.__enterRoomWin.updateRoomList(v)

            if k == 'SERVER_SHUTDOWN':
                self.__client.closeClient()
                self.__displayNewMsg('SysMsg', "Server is down, you can close the program, and come back later")

    def __setUsrTime(self, timeStr):
        if timeStr is not None:
            msg = timeStr.split(';')
            self.labelLastOnlineTime['text'] = '上次登录时间\n'.decode('utf-8') + msg[0]
            self.labelTotalOnlineTime['text'] = '总共在线时间\n'.decode('utf-8') + msg[1]

    def __privateChatCmd(self):
        sel = self.userList.curselection()
        if sel.__len__() > 0:
            receiverName = self.userList.get(sel)

            usrMsg = self.msg.get('0.0', END)
            self.__displayNewMsg(self.__usrName, usrMsg, 'userColor')
            self.msg.delete('0.0', END)
            data = packagePrivateChatMsg(self.__usrName, receiverName, usrMsg)
            self.__client.appendToMsgSendingQueue(data)

            # pr = PrivateRoom(self.__usrName, receiverName, self.__client, self)
            # self.__privateRoomLists[receiverName] = pr
            # pr.mainloop()
        else:
            tkMessageBox.showinfo("Note", "Please select a user")

    def closePrivateChatRoom(self, friendUsrname):
        if self.__privateRoomLists.has_key(friendUsrname):
            self.__privateRoomLists.__delitem__(friendUsrname)

    def __creatRoomCmd(self):
        if not self.__createRoomWin:
            self.__createRoomWin = CreateRoomGUI(self.__client, self.__usrName, self)
            self.__createRoomWin.mainloop()
        else:
            self.__createRoomWin.deiconify()

    def __enterRoomCmd(self):
        self.queryAllRooms()

        if not self.__enterRoomWin:
            self.__enterRoomWin = EnterRoomGUI(self.__client, self.__usrName, self)
            self.__enterRoomWin.mainloop()
        else:
            self.__enterRoomWin.deiconify()

    def queryAllRooms(self):
        key = 'SysRoomListRequest'
        value = ''
        msg = packageSysMsg(key, value)
        self.__client.appendToMsgSendingQueue(msg)

    def addNewRoom(self, roomName, room):
        if not self.__roomLists.has_key(roomName):
            self.__roomLists[roomName] = room

    def configureUI(self):
        # main window
        bgColor = '#208090'
        self['bg'] = bgColor
        self.geometry("550x600+520+500")
        self.resizable(width=True, height=True)

        self.frmTop = Frame(self, width=380, height=250)
        self.frmMid = Frame(self, width=380, height=250)
        self.frmBtm = Frame(self, width=380, height=30)
        self.frmRight = Frame(self, width=200, height=580)
        self.frmBtm['bg'] = bgColor
        self.frmRight['bg'] = bgColor

        # message zone
        self.textLabelMsgDisplay = Label(self, justify=LEFT, text=u"""消息列表""")
        self.textLabelUsrName = Label(self, justify=LEFT, text=self.__usrName)

        self.msgList = ScrolledText(self.frmTop, borderwidth=1, highlightthickness=0, relief='flat', bg='#fffff0',
                                    state=DISABLED)
        self.msgList.tag_config('userColor', foreground='red')
        self.msgList.place(x=0, y=0, width=380, height=250)

        self.msg = ScrolledText(self.frmMid)
        self.msg.grid(row=0, column=0)

        # buttons
        self.sendBtn = Button(self.frmBtm, text='发送消息', background='grey', command=self.__sendMsgBtn)
        self.pvtChatBtn = Button(self.frmRight, text='私聊', background='grey',command=self.__privateChatCmd)
        self.creatRoomBtn = Button(self.frmRight, text='创建房间',background='grey', command=self.__creatRoomCmd)
        self.enterRoomBtn = Button(self.frmRight, text='进入房间',background='grey',command=self.__enterRoomCmd)

        self.labelLastOnlineTime = Label(self.frmRight, text='  上次登录时间  \n')
        self.labelTotalOnlineTime = Label(self.frmRight, text=' 总共在线时间  \n')

        self.textLabelOnlineUsers = Label(self.frmRight, justify=LEFT, text=u"""其他在线用户""")
        self.userListStr = StringVar()
        self.userList = Listbox(self.frmRight, borderwidth=1, highlightthickness=0, relief='flat', bg='#ededed',
                                listvariable=self.userListStr)

        # layout
        self.textLabelMsgDisplay.grid(row=0, column=0, padx=2, pady=2, sticky=W)
        self.frmTop.grid(row=1, column=0, padx=2, pady=2)
        self.textLabelUsrName.grid(row=2, column=0, padx=2, pady=2, sticky=W)
        self.frmMid.grid(row=3, column=0, padx=2, pady=2, )
        self.frmBtm.grid(row=4, column=0, padx=2, pady=2, )
        self.frmRight.grid(row=0, column=1, rowspan=5, sticky=N + S)

        self.sendBtn.grid()

        # right frame layout
        self.labelLastOnlineTime.place(x=30, y=30, width=120, height=50)
        self.labelTotalOnlineTime.place(x=30, y=90, width=120, height=50)
        self.creatRoomBtn.place(x=30, y=160, width=120, height=30)
        self.enterRoomBtn.place(x=30, y=200, width=120, height=30)
        self.textLabelOnlineUsers.place(x=30, y=260, width=120, height=30)
        self.userList.place(x=7, y=311, width=150, height=250)
        self.pvtChatBtn.place(x=7, y=565, width=90, height=30)

        self.frmTop.grid_propagate(0)
        self.frmMid.grid_propagate(0)
        self.frmBtm.grid_propagate(0)
        self.frmRight.grid_propagate(0)


def myHandler(signum, frame):
    print "exit program"


if __name__ == "__main__":
    signal.signal(signal.SIGINT, myHandler)

    d = Dialog()

