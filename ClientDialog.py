# -*- coding: UTF-8 -*-

import signal
import threading
import time
from ScrolledText import ScrolledText
from Tkinter import *

from ClientEnd import *
from Utilities import *


# login window
class LoginWindow(Toplevel):
    '''
    this class is used to create a login window
    '''

    client = None
    mainFrm = None
    usrName = None

    def __init__(self, mainFrm, client):
        Toplevel.__init__(self)
        self.mainFrm = mainFrm
        self.title(u'登录窗口')
        logFrmPos = '%dx%d+%d+%d' % (400, 300, (1500 - 400) / 2, (900 - 300) / 2)
        self.geometry(logFrmPos)
        self.configureUI()

        self.client = client
        self.protocol('WM_DELETE_WINDOW', self.closeDialog)

    def configureUI(self):
        self.logFrm = Frame(self, width=380, height=400)

        self.logCaption = Label(self.logFrm, text=u'登录窗口')

        self.logUNlabel = Label(self.logFrm, text=u'用户名')
        self.logPWDlabel = Label(self.logFrm, text=u'密码')
        self.logInfo = Label(self.logFrm)

        self.logUsrName = Entry(self.logFrm, text=u'netease1')
        self.logUsrPWD = Entry(self.logFrm, text=u'1234',show = '*')

        self.logBtnEnter = Button(self.logFrm, text=u'登录', command = self.enterBtn)
        self.logBtnRegist = Button(self.logFrm, text=u'注册', command = self.registBtn)

        self.logFrm.pack()
        self.logCaption.grid(row=0, column=0, columnspan=2, pady='2c')
        self.logUNlabel.grid(row=1, column=0)
        self.logUsrName.grid(row=1, column=1)
        self.logPWDlabel.grid(row=2, column=0)
        self.logUsrPWD.grid(row=2, column=1)
        self.logInfo.grid(row=3, column=0, columnspan=2, pady='1m')
        self.logBtnEnter.grid(row=4, column=0, columnspan=2, pady='2m')
        self.logBtnRegist.grid(row=5, column=0, columnspan=2, pady='1m')

        # self.logFrm.grid_propagate(0)

    def tryLogin(self):
        self.usrName = self.logUsrName.get()
        password = self.logUsrPWD.get()

        jstr = packageMsg('SysLoginRequest', {self.usrName: password})
        self.client.addMsgToQueue(jstr)

        while 1:
            sysMsg = self.client.popSysMsgFromQueue()
            if sysMsg != None:
                if sysMsg =='Successful login':
                    return True
                else:
                    self.logInfo['text'] = sysMsg
                return False


    def enterBtn(self):
        if self.tryLogin():
            self.destroy()
            self.mainFrm.deiconify()
            self.mainFrm.setUsrName(self.usrName)


    def registBtn(self):
        self.usrName = self.logUsrName.get()
        password = self.logUsrPWD.get()

        jstr = packageMsg('SysRegisterRequest', {self.usrName: password})
        self.client.addMsgToQueue(jstr)

        while 1:
            sysMsg = self.client.popSysMsgFromQueue()
            if sysMsg != None:
                if sysMsg =='Succesful registration':
                    self.logInfo['text'] = sysMsg
                    return True
                else:
                    self.logInfo['text'] = sysMsg
                return False

    def closeDialog(self):
        self.client.closeClient()
        self.mainFrm.destroy()


class Dialog(Tk):

    usrName = 'usrName'
    loginWin = None
    clientSock = None
    client = None

    msgThread = None


    def __init__(self):
        Tk.__init__(self)
        self.title(u"聊天窗口")
        self['background'] = 'grey'
        self.configureUI()
        self.withdraw()
        self.protocol('WM_DELETE_WINDOW', self.closeDialog)

        self.__connect()

        if self.client.isSocketAlive():
            self.loginWin = LoginWindow(self, self.client)

            displayMsgThread = threading.Thread(target=self.__displayMsg)
            displayMsgThread.setDaemon(True)
            displayMsgThread.start()

            usrOnlineMsgThread = threading.Thread(target=self.__setUsrOnlineTimeLoop)
            usrOnlineMsgThread.setDaemon(True)
            usrOnlineMsgThread.start()
        else:
            print 'failed to connect server'
            sys.exit(1)

        self.mainloop()

    def __connect(self):
        self.client = Client()
        self.client.connectToServer()


    def setUsrName(self, myStr):
        self.usrName = myStr
        self.text_label_usrName['text'] = myStr
        print self.usrName

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
        self.text_label_usrName = Label(self, justify=LEFT, text=self.usrName)

        self.msgList = ScrolledText(self.frmTop, borderwidth=1, highlightthickness=0, relief='flat', bg='#fffff0')
        self.msgList.tag_config('userColor', foreground='red')
        self.msgList.place(x=0, y=0, width=380, height=250)

        self.msg = ScrolledText(self.frmMid)
        self.msg.grid(row=0, column=0)

        self.sendBtn = Button(self.frmBtm, text = '发送消息', command=self.BtnCommand)
        self.sendBtn.bind('<Button-2>', self.BtnCommand2)

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
        self.frmTop.grid_propagate(0)
        self.frmMid.grid_propagate(0)
        self.frmBtm.grid_propagate(0)
        self.frmRight.grid_propagate(0)

    def BtnCommand(self):
        self.msgList.insert(END, self.usrName +': '+ time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '\n ', 'userColor')
        usrMsg = self.msg.get('0.0', END)
        self.msgList.insert(END, usrMsg)
        self.msg.delete('0.0', END)
        msg = {}
        msg['Chat'] = usrMsg
        data = json.dumps(msg)

        self.client.addMsgToQueue(data)
        # socketSend(self.clientSock, usrMsg)

    def BtnCommand2(self, event):
        self.msgList.insert(END, ' a message :')


    def closeDialog(self):
        self.client.closeClient()
        self.destroy()

    def __displayMsg(self):
        while self.client.isSocketAlive():
            time.sleep(0.1)
            msg = self.client.popChatMsgFromQueue()
            if msg != None:
                seperator = msg.find(': ')
                usr = msg[0:seperator + 1]
                usrMsg = msg[seperator + 1:]
                usr = usr + time.strftime(" %Y-%m-%d %H:%M:%S", time.localtime()) + '\n'
                self.msgList.insert(END, usr + usrMsg)
        print 'end of displaying msg thread'

    def __setUsrOnlineTimeLoop(self):
        while self.client.isSocketAlive():
            time.sleep(5)
            self.setUsrTime()
        print 'end of updating usr online time'

    def setUsrTime(self):
        msg = self.client.popUsrOnlineTimeMsgFromQueue()
        if msg != None:
            msg = msg.split(';')
            self.labelLastOnlineTime['text'] = '上次登录时间\n'.decode('utf-8') + msg[0]
            self.labelTotalOnlineTime['text'] = '总共在线时间\n'.decode('utf-8') + msg[1]

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