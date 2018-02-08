import json

def packageMsg(key, msg):
    rtnStr = {}
    rtnStr[key] = msg
    return json.dumps(rtnStr)

def packageChatMsg(msg):
    rtnStr = {}
    rtnStr['ChatMsg'] = {'toAll': msg}
    return json.dumps(rtnStr)

def packageSysMsg(key, msg):
    rtnStr = {}
    rtnStr['SysMsg'] = {key: msg}
    return json.dumps(rtnStr)


def packagePrivateChatMsg(usrnameToSend, msg):
    rtnStr = {}
    rtnStr['ChatMsg'] = {usrnameToSend: msg}
    return json.dumps(rtnStr)