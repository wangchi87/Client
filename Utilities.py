import json

def packageMsg(key, msg):
    rtnStr = {}
    rtnStr[key] = msg
    return json.dumps(rtnStr)


def packagePublicChatMsg(msg):
    rtnStr = {}
    rtnStr['ChatMsg'] = {'toAll': msg}
    return json.dumps(rtnStr)


def packageSysMsg(key, msg):
    rtnStr = {}
    rtnStr['SysMsg'] = {key: msg}
    return json.dumps(rtnStr)


def packagePrivateChatMsg(usrname, msg):
    # at server end, usrname indicates the name of receiver.
    # at cliend end, usrname indicates the name of sender
    rtnStr = {}
    rtnStr['ChatMsg'] = {usrname: msg}
    return json.dumps(rtnStr)