# -*- coding: UTF-8 -*-

from Tkinter import *
from ClientEnd import *

import time
import threading
import signal

# login window
class LoginWindow(Toplevel):
    '''
    this class is used to create a login window
    '''

    client = None
    mainFrm = None


    def __init__(self, mainFrm, client):
        Toplevel.__init__(self)
        self.mainFrm = mainFrm
        self.title(u'登录窗口')
        logFrmPos = '%dx%d+%d+%d' % (400, 300, (1500 - 400) / 2, (900 - 300) / 2)
        self.geometry(logFrmPos)
        self.configureUI()

        self.client = client

    def configureUI(self):
        self.logFrm = Frame(self, width=380, height=250)

        self.logCaption = Label(self.logFrm, text=u'登录窗口')

        self.logUNlabel = Label(self.logFrm, text=u'用户名')
        self.logPWDlabel = Label(self.logFrm, text=u'密码')

        self.logUsrName = Entry(self.logFrm)
        self.logUsrPWD = Entry(self.logFrm)

        self.logBtnEnter = Button(self.logFrm, text=u'登录', command = self.enterBtn)
        self.logBtnRegist = Button(self.logFrm, text=u'注册', command = self.registBtn)

        self.logFrm.pack()
        self.logCaption.grid(row=0, column=0, columnspan=2, pady='2c')
        self.logUNlabel.grid(row=1, column=0)
        self.logUsrName.grid(row=1, column=1)
        self.logPWDlabel.grid(row=2, column=0)
        self.logUsrPWD.grid(row=2, column=1)
        self.logBtnEnter.grid(row=3, column=0, columnspan=2, pady='5m')
        self.logBtnRegist.grid(row=4, column=0, columnspan=2, pady='1m')

    def tryLogin(self):
        pass

        return True

    def enterBtn(self):
        if self.tryLogin():
            self.destroy()
            self.mainFrm.deiconify()
            self.mainFrm.setUsrName('网易用户')
        else:
            self.destroy()
            self.mainFrm.destroy()

    def registBtn(self):
        pass


class Dialog(Tk):

    usrName = 'usrName'
    loginWin = None
    clientSock = None
    isSocketAlive = False
    client = None

    msgThread = None
    sockThread = None


    def __init__(self):
        Tk.__init__(self)
        self.title(u"聊天窗口")
        self['background'] = 'grey'
        self.configureUI()

        self.protocol('WM_DELETE_WINDOW', self.closeDialog)

        self.withdraw()

        # 发起链接
        self.isSocketAlive = False
        self.__connect()
        self.clientSock = self.client.clientSock

        if self.isSocketAlive:
            self.loginWin = LoginWindow(self, self.client)

            self.msgThread = threading.Thread(target=self.socketLoop)
            self.msgThread.setDaemon(True)
            self.msgThread.start()
        else:
            print 'failed to connect server'
            sys.exit(1)

    def __connect(self):
        self.client = Client()
        self.isSocketAlive = self.client.connectToServer()


    def setUsrName(self, myStr):
        self.usrName = myStr
        self.label2['text'] = myStr
        print self.usrName

    def configureUI(self):
        # main window

        self.frmTop = Frame(self,width=380, height=250)
        self.frmMid = Frame(self,width=380, height=250)
        self.frmBtm = Frame(self,width=380, height=30)
        self.frmRight = Frame(self,bg='red',width=80, height=580)

        self.label1 = Label(self, justify=LEFT, text=u"""消息列表""")
        self.label2 = Label(self, justify=LEFT, text=self.usrName)

        self.msgList = Text(self.frmTop, width=260, height=230)
        self.msg = Text(self.frmMid, width=260, height=230)

        self.sendBtn = Button(self.frmBtm, text = '发送消息', command=self.BtnCommand)
        self.sendBtn.bind('<Button-2>', self.BtnCommand2)

        self.label1.grid(row = 0, column = 0,sticky=W)
        self.frmTop.grid(row = 1, column = 0)
        self.label2.grid(row=2, column=0,sticky=W)
        self.frmMid.grid(row = 3, column = 0)
        self.frmBtm.grid(row=4, column=0)
        self.frmRight.grid(row=0, column=1,rowspan=5,sticky=N+S)

        self.msgList.grid()
        self.msgList.tag_config('userColor', foreground='red')

        self.msg.grid()
        self.sendBtn.grid()

        self.msgList.grid_propagate(0)
        self.msg.grid_propagate(0)
        self.frmTop.grid_propagate(0)
        self.frmMid.grid_propagate(0)
        self.frmBtm.grid_propagate(0)
        self.frmRight.grid_propagate(0)

    def BtnCommand(self):
        self.msgList.insert(END, self.usrName +': '+ time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '\n ', 'userColor')
        usrMsg = self.msg.get('0.0', END)
        self.msgList.insert(END, usrMsg)
        self.msg.delete('0.0', END)
        socketSend(self.clientSock, usrMsg)

    def BtnCommand2(self, event):
        self.msgList.insert(END, ' a message :')

    def closeSocket(self):
        self.client.closeClient()

    def socketLoop(self):
        print 'socket loop with threading'
        self.client.mainLoop(self.msgList)

    def msgListner(self):
        print 'message loop with threading'
        while 1:
            if len(self.client.messageList) > 0:
                msg = self.client.messageList.pop()
                print msg

    def closeDialog(self):
        self.closeSocket()
        # kill thread
        self.destroy()


def myHandler(signum, frame):
    print('I received: ', signum)


if __name__ == "__main__":

    # 当用右上角方框直接中断程序的时候，会出现SIGKILL信号
    # 在这种情况下，会向socket发送空字符串
    signal.signal(signal.SIGABRT, myHandler)
    signal.signal(signal.SIGINT, myHandler)

    d = Dialog()
    try:
        d.mainloop()
    except Exception as e:
        print e, 'xxx'





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