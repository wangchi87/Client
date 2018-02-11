import json

def packageMsg(key, msg):
    rtnStr = {}
    rtnStr[key] = msg
    return json.dumps(rtnStr)

def packageSysMsg(key, msg):
    rtnStr = {}
    rtnStr['SysMsg'] = {key: msg}
    return json.dumps(rtnStr)


def packagePublicChatMsg(sender, msg):
    rtnStr = {}
    rtnStr['ChatMsg'] = {'toAll': [sender, msg]}
    return json.dumps(rtnStr)


def packagePrivateChatMsg(sender, receiver, msg):
    rtnStr = {}
    rtnStr['ChatMsg'] = {'toClient': [sender, receiver, msg]}
    return json.dumps(rtnStr)


def packageRoomChatMsg(sender, roomName, msg):
    rtnStr = {}
    rtnStr['ChatMsg'] = {'toRoom': [sender, roomName, msg]}
    return json.dumps(rtnStr)
