# -*- coding: UTF-8 -*-

import time
import tkMessageBox
from ScrolledText import ScrolledText
from Tkinter import *

from Utilities import *


class CreateRoomGUI(Toplevel):
    __client = None
    __usrName = None
    __mainFrm = None

    __roomName = None
    __room = None

    def __init__(self, client, usrName, mfm):
        Toplevel.__init__(self)
        self.protocol('WM_DELETE_WINDOW', self.closeRoom)
        self.__usrName = usrName
        self.__client = client
        self.__mainFrm = mfm
        self.configureUI()

    def closeRoom(self):
        self.withdraw()

    def configureUI(self):
        self.title(u'创建房价')
        logFrmPos = '%dx%d+%d+%d' % (325, 230, (1500 - 400) / 2, (900 - 300) / 2)
        self.geometry(logFrmPos)
        self.resizable(width=True, height=True)

        self.labelText = Label(self, text=u'房价名称')
        self.labelCreationInfo = Label(self)
        self.textRoomName = Entry(self, text=u'room')

        self.logBtnRegister = Button(self, text=u'创建', command=self.registerBtn)
        self.logBtnCancel = Button(self, text=u'取消', command=self.cancelBtn)

        self.labelText.pack(pady=15)
        self.labelCreationInfo.pack(pady=5)
        self.textRoomName.pack(pady=5)
        self.logBtnRegister.pack(pady=5)
        self.logBtnCancel.pack(pady=5)

    def cancelBtn(self):
        self.withdraw()

    def registerBtn(self):
        roomName = self.textRoomName.get()
        key = 'SysCreateRoomRequest'
        value = {'admin': self.__usrName, 'roomName': roomName}
        msg = packageSysMsg(key, value)
        self.__client.appendToMsgSendingQueue(msg)
        print msg

        # get sys ack meg, add new room to maifrm.room list
        self.__room = Room(self.__client, roomName, self.__mainFrm, self)


class EnterRoomGUI(Toplevel):
    __client = None
    __usrName = None
    __mainFrm = None
    __roomList = []

    __roomName = None
    __room = None

    def __init__(self, client, usrName, mfm):
        Toplevel.__init__(self)
        self.protocol('WM_DELETE_WINDOW', self.closeRoom)
        self.__usrName = usrName
        self.__client = client
        self.__mainFrm = mfm

        # query all existing room
        self.queryAllRooms()
        self.configureUI()

    def closeRoom(self):
        self.withdraw()

    def configureUI(self):
        self.title(u'进入房间')
        logFrmPos = '%dx%d+%d+%d' % (250, 400, (1500 - 400) / 2, (900 - 300) / 2)
        self.geometry(logFrmPos)
        self.resizable(width=True, height=True)

        self.labelText = Label(self, text=u'所有房间')
        self.labelCreationInfo = Label(self)

        self.roomListBox = Listbox(self, bg='#fffff0')
        self.roomListBox.grid_propagate(0)

        self.logBtnRegister = Button(self, text=u'进入', command=self.enterRoomBtn)
        self.logBtnCancel = Button(self, text=u'取消', command=self.cancelBtn)

        self.labelText.place(x=75, y=20, width=100, height=30)

        self.roomListBox.place(x=25, y=80, width=200, height=200)
        self.labelCreationInfo.place(x=25, y=300, width=200, height=30)
        self.logBtnRegister.place(x=50, y=350, width=50, height=30)
        self.logBtnCancel.place(x=150, y=350, width=50, height=30)

    def cancelBtn(self):
        self.withdraw()

    def enterRoomBtn(self):
        if self.roomListBox.size() == 0:
            tkMessageBox.showinfo("Note", "There is no room available")
            return

        # self.roomListBox.selection_set(0)
        sel = self.roomListBox.curselection()
        if sel.__len__() > 0:
            self.__roomName = self.roomListBox.get(sel)
            key = 'SysEnterRoomRequest'
            value = {'roomName': self.__roomName}
            msg = packageSysMsg(key, value)
            self.__client.appendToMsgSendingQueue(msg)
            self.__room = Room(self.__client, self.__roomName, self.__mainFrm, self)
        else:
            tkMessageBox.showinfo("Note", "Please select a room")

    def queryAllRooms(self):
        key = 'SysRoomListRequest'
        value = ''
        msg = packageSysMsg(key, value)
        self.__client.appendToMsgSendingQueue(msg)

    def updateRoomList(self, list):
        self.roomListBox.delete(0, END)
        for r in list:
            self.roomListBox.insert(END, r)

    def setRoomList(self, rooms):
        self.__roomList = rooms


class Room(Toplevel):
    __client = None
    __usrName = None
    __roomName = None
    __mainFrm = None
    __topFrm = None

    def __init__(self, client, roomName, mfm, topFrm):
        Toplevel.__init__(self)

        self['background'] = 'grey'

        self.protocol('WM_DELETE_WINDOW', self.closeRoom)
        self.__usrName = mfm.getUsrName()

        self.title("Room Name:" + roomName)
        self.__roomName = roomName

        self.configureUI()
        self.__client = client

        self.__topFrm = topFrm
        self.__mainFrm = mfm
        self.__mainFrm.addNewRoom(self.__roomName, self)

        self.withdraw()
        self.mainloop()

    def showRoom(self):
        print 'show room'
        self.__topFrm.withdraw()
        self.deiconify()

    def closeRoom(self):
        self.withdraw()

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
        self.displayNewMsg(self.__usrName, usrMsg, 'userColor')
        self.msg.delete('0.0', END)
        data = packageRoomChatMsg(self.__usrName, self.__roomName, usrMsg)
        self.__client.appendToMsgSendingQueue(data)

    def displayNewMsg(self, usrname, msg, config=''):
        self.msgList['state'] = 'normal'
        msgTime = time.strftime(" %Y-%m-%d %H:%M:%S", time.localtime()) + '\n'
        self.msgList.insert(END, usrname + ': ' + msgTime + msg, config)
        self.msgList['state'] = 'disabled'


class PrivateRoom(Toplevel):
    __client = None
    __receiverName = None
    __usrName = None

    __mainFrm = None

    def __init__(self, mn, fn, client, mfm):
        Toplevel.__init__(self)

        self['background'] = 'grey'

        self.protocol('WM_DELETE_WINDOW', self.closeRoom)
        self.__usrName = mn

        self.title(u"与" + fn + u"私聊")
        self.__receiverName = fn

        self.configureUI()
        self.__client = client
        self.__mainFrm = mfm

    def closeRoom(self):
        # TODO: 再次进入房间？？？
        self.__mainFrm.closePrivateChatRoom(self.__receiverName)
        self.withdraw()

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
        data = packagePrivateChatMsg(self.__usrName, self.__receiverName, usrMsg)
        self.__client.appendToMsgSendingQueue(data)

    def __displayNewMsg(self, usrname, msg, config=''):
        self.msgList['state'] = 'normal'
        msgTime = time.strftime(" %Y-%m-%d %H:%M:%S", time.localtime()) + '\n'
        self.msgList.insert(END, usrname + ': ' + msgTime + msg, config)
        self.msgList['state'] = 'disabled'
