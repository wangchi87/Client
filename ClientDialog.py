# -*- coding: UTF-8 -*-

import signal
from ScrolledText import ScrolledText
from Tkinter import *

from ClientEnd import *
from Utilities import *


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
        self.title(u'登录窗口')

        self.configureUI()

        self.__client = client
        self.protocol('WM_DELETE_WINDOW', self.closeDialog)

    def configureUI(self):
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
            self.mainFrm.startMsgThread()
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
    __privateRooms = {}

    def __init__(self):
        Tk.__init__(self)
        self.title(u"聊天大厅")
        self['background'] = 'grey'
        self.configureUI()
        self.withdraw()
        self.protocol('WM_DELETE_WINDOW', self.closeDialog)

        self.__chatMsgThread = threading.Thread(target=self.__processChatMsg)
        self.__chatMsgThread.setDaemon(True)
        self.__sysMsgThread = threading.Thread(target=self.__processSysMsg)
        self.__sysMsgThread.setDaemon(True)

        self.__connect()

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

    def startMsgThread(self):
        self.__chatMsgThread.start()
        self.__sysMsgThread.start()

    def __connect(self):
        self.__client = Client()
        self.__client.connectToServer()

    def setUsrName(self, myStr):
        self.__usrName = myStr
        self.text_label_usrName['text'] = myStr
        print self.__usrName

    def __sendMsgBtn(self):
        usrMsg = self.msg.get('0.0', END)
        self.__displayNewMsg(self.__usrName, usrMsg, 'userColor')
        self.msg.delete('0.0', END)
        data = packagePublicChatMsg(usrMsg)
        self.__client.appendToMsgSendingQueue(data)

    def closeDialog(self):
        self.__client.closeClient()
        self.destroy()

        for pr in self.__privateRooms.values():
            pr.closeRoom()

    def __processChatMsg(self):
        while self.__client.isSocketAlive() and self.hasAlreadyLoggedIn():
            time.sleep(0.1)
            msgDict = self.__client.popChatMsgFromQueue()
            if msgDict is not None:
                print msgDict
                for k, v in msgDict.items():
                    # k is the msg sender usrname or 'toAll'
                    # v is the msg
                    if k == 'toAll':
                        msg = v
                        sepIndex = msg.find(': ')
                        usr = msg[0: sepIndex]
                        usrMsg = msg[sepIndex + 1:]
                        self.__displayNewMsg(usr, usrMsg)
                    else:
                        # print k, v
                        # privateRoom = None
                        # if self.__privateRooms.has_key(k):
                        #     privateRoom = self.__privateRooms[k]
                        # else:
                        # privateRoom = PrivateRoom(self.__usrName, k, self.__client, self)
                        # prt = threading.Thread(target=privateRoom.mainloop)
                        # prt.setDaemon(True)
                        # prt.start()
                        #     self.__privateRooms[k] = privateRoom
                        # print privateRoom
                        # privateRoom.appendMsgToMsgList(v)
                        # self.msgList.insert(END, k +'(private msg) : '+ msgTime + v)
                        self.__displayNewMsg(k + "(private msg)", v)
                        pass


        print 'end of displaying chat msg thread'

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

        while self.__client.isSocketAlive() and self.hasAlreadyLoggedIn():
            sysMsg = self.__client.popSysMsgFromQueue()

            if sysMsg is None:
                time.sleep(0.2)
            else:
                # print 'sysMsg: ', sysMsg
                for k, v in sysMsg.items():
                    if k == 'SysUsrOnlineDurationMsg':
                        self.__setUsrTime(v)

                    if k == 'SysAllOnlineClientsAck':
                        print "SysAllOnlineClientsAck", self.userList.size(), v
                        if v.keys()[0] == 'allOnlineUsernames':
                            allCurrentUsers = self.userList.get(0, self.userList.size())
                            for e in v.values()[0]:
                                if e != self.__usrName and e not in allCurrentUsers:
                                    self.userList.insert(END, e)

                    # other user login
                    if k == 'SysUsrLogin' and v != self.__usrName:
                        print 'SysUsrLogin', self.userList.size(), v
                        allCurrentUsers = self.userList.get(0, self.userList.size())
                        if v not in allCurrentUsers:
                            self.userList.insert(END, v)

                    #other user log out
                    if k == 'SysUsrLogOut' and v != self.__usrName:
                        for i in range(0, self.userList.size()):
                            if v == self.userList.get(i):
                                self.userList.delete(i)

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
            friendUsrName = self.userList.get(sel)
            pr = PrivateRoom(self.__usrName, friendUsrName, self.__client, self)
            self.__privateRooms[friendUsrName] = pr
            pr.mainloop()
        else:
            print 'please select a user'

    def closePrivateChatRoom(self, friendUsrname):
        if self.__privateRooms.has_key(friendUsrname):
            self.__privateRooms.__delitem__(friendUsrname)
        # print 'private rooms', self.__privateRooms

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

        self.text_label_msgDisplay = Label(self, justify=LEFT, text=u"""消息列表""")
        self.text_label_usrName = Label(self, justify=LEFT, text=self.__usrName)

        self.msgList = ScrolledText(self.frmTop, borderwidth=1, highlightthickness=0, relief='flat', bg='#fffff0',
                                    state=DISABLED)
        self.msgList.tag_config('userColor', foreground='red')
        self.msgList.place(x=0, y=0, width=380, height=250)

        self.msg = ScrolledText(self.frmMid)
        self.msg.grid(row=0, column=0)

        self.sendBtn = Button(self.frmBtm, text='发送消息', command=self.__sendMsgBtn)
        # self.sendBtn.bind('<Button-2>', self.BtnCommand2)

        self.pvtChatBtn = Button(self.frmRight, text='私聊', command=self.__privateChatCmd)

        self.labelLastOnlineTime = Label(self.frmRight, text='         上次登录时间         \n')
        self.labelTotalOnlineTime = Label(self.frmRight, text='        总共在线时间         \n')

        self.userListStr = StringVar()
        self.userList = Listbox(self.frmRight, borderwidth=1, highlightthickness=0, relief='flat', bg='#ededed',
                                listvariable=self.userListStr)

        self.text_label_msgDisplay.grid(row=0, column=0, padx=2, pady=2, sticky=W)
        self.frmTop.grid(row=1, column=0, padx=2, pady=2)
        self.text_label_usrName.grid(row=2, column=0, padx=2, pady=2, sticky=W)
        self.frmMid.grid(row=3, column=0, padx=2, pady=2, )
        self.frmBtm.grid(row=4, column=0, padx=2, pady=2, )
        self.frmRight.grid(row=0, column=1, rowspan=5, sticky=N + S)

        self.sendBtn.grid()

        self.labelLastOnlineTime.grid(row=0, column=0, pady='10m', sticky=E)
        self.labelTotalOnlineTime.grid(row=1, column=0, pady='5m', sticky=E)
        self.userList.place(x=7, y=308, width=150, height=250)
        self.pvtChatBtn.place(x=7, y=560, width=90, height=25)
        self.frmTop.grid_propagate(0)
        self.frmMid.grid_propagate(0)
        self.frmBtm.grid_propagate(0)
        self.frmRight.grid_propagate(0)



class PrivateRoom(Tk):
    __client = None
    __friendUsrName = None
    __usrName = None

    __mainFrm = None

    def __init__(self, mn, fn, client, mfm):
        Tk.__init__(self)

        self['background'] = 'grey'

        self.protocol('WM_DELETE_WINDOW', self.closeRoom)
        self.__usrName = mn

        self.title(u"与" + fn + u"私聊")
        self.__friendUsrName = fn

        self.configureUI()
        self.__client = client
        self.__mainFrm = mfm

    def closeRoom(self):
        self.__mainFrm.closePrivateChatRoom(self.__friendUsrName)
        self.destroy()

    def configureUI(self):
        # main window
        bgColor = '#208090'
        self['bg'] = bgColor
        self.geometry("400x500+520+500")
        self.resizable(width=True, height=True)

        self.frmTop = Frame(self, width=380, height=250)
        self.frmMid = Frame(self, width=380, height=150)
        self.frmBtm = Frame(self, width=380, height=30)
        self.frmBtm['bg'] = bgColor

        self.text_label_msgDisplay = Label(self, justify=LEFT, text=u"""消息列表""")
        self.text_label_usrName = Label(self, justify=LEFT, text=self.__usrName)

        self.msgList = ScrolledText(self.frmTop, borderwidth=1, highlightthickness=0, relief='flat', bg='#fffff0')
        self.msgList.tag_config('userColor', foreground='red')
        self.msgList.place(x=0, y=0, width=380, height=250)

        self.msg = ScrolledText(self.frmMid)
        self.msg.grid(row=0, column=0)

        self.sendBtn = Button(self.frmBtm, text='发送消息', command=self.__sendMsgBtn)
        self.sendBtn.grid()

        self.text_label_msgDisplay.grid(row=0, column=0, padx=2, pady=2, sticky=W)
        self.frmTop.grid(row=1, column=0, padx=2, pady=2)
        self.text_label_usrName.grid(row=2, column=0, padx=2, pady=2, sticky=W)
        self.frmMid.grid(row=3, column=0, padx=2, pady=2, )
        self.frmBtm.grid(row=4, column=0, padx=2, pady=2, )

        self.frmTop.grid_propagate(0)
        self.frmMid.grid_propagate(0)
        self.frmBtm.grid_propagate(0)

    def __sendMsgBtn(self):
        usrMsg = self.msg.get('0.0', END)
        self.__displayNewMsg(self.__usrName, usrMsg, 'userColor')
        self.msg.delete('0.0', END)
        # data = packagePublicChatMsg(usrMsg)
        # self.__client.appendToMsgSendingQueue(data)
        data = packagePrivateChatMsg(self.__friendUsrName, usrMsg)
        self.__client.appendToMsgSendingQueue(data)

    def __displayNewMsg(self, usrname, msg, config=''):
        self.msgList['state'] = 'normal'
        msgTime = time.strftime(" %Y-%m-%d %H:%M:%S", time.localtime()) + '\n'
        self.msgList.insert(END, usrname + ': ' + msgTime + msg, config)
        self.msgList['state'] = 'disabled'

def myHandler(signum, frame):
    print('I received: ', signum)


if __name__ == "__main__":

    # 当用右上角方框直接中断程序的时候，会出现SIGKILL信号
    # 在这种情况下，会向socket发送空字符串
    signal.signal(signal.SIGABRT, myHandler)
    signal.signal(signal.SIGINT, myHandler)

    d = Dialog()
    # try:
    #     d.mainloop()
    # except Exception as e:
    #     print e, 'xxx'





'''
root = Tk()
root.title('Talking')


# 发送按钮事件
def sendmessage():
    # 在聊天内容上方加一行 显示发送人及发送时间
    msgcontent = '我: ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '\n '
    text_msglist.insert(END, msgcontent, 'green')
    text_msglist.insert(END, text_msg.get('0.0', END))
    text_msg.delete('0.0', END)


# 创建几个frame作为容器
frame_left_top = Frame(width=380, height=250, bg='red')
frame_left_center = Frame(width=380, height=90, bg='black')
frame_left_center2 = Frame(width=380, height=90)
frame_left_bottom = Frame(width=380, height=20)
frame_left_bottom2 = Frame(width=380, height=20)
frame_right = Frame(width=170, height=400, bg='yellow')

##创建需要的几个元素
text_msglist = Text(frame_left_top, width=380, height=220)
text_msg = Text(frame_left_center, width=380, height=80)
button_sendmsg = Button(frame_left_bottom, text=u'发送', command=sendmessage,bg='purple')
button2 = Button(frame_left_bottom2, text = 'test')
button2.pack()

# 创建一个绿色的tag
text_msglist.tag_config('green', foreground='#008B00')

# 使用grid设置各个容器位置
frame_left_top.grid(row=0, column=0, padx=2, pady=5)
frame_left_center.grid(row=1, column=0, padx=2, pady=5)
frame_left_bottom.grid(row=2, column=0)
frame_left_bottom.grid(row=3, column=0)
frame_right.grid(row=0, column=1, rowspan=3, padx=4, pady=5)
frame_left_top.grid_propagate(0)
frame_left_center.grid_propagate(0)
frame_left_bottom.grid_propagate(0)
frame_left_bottom2.grid_propagate(0)

# 把元素填充进frame
text_msglist.grid()
text_msg.grid()
button_sendmsg.grid(sticky=E)
'''
# 主事件循环
#root.mainloop()