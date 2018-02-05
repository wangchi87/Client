
import socket

def socketCreation():
    try:
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    except socket.error as err:
        print "failed to create socket: ", err
    else:
        return sock

def socketBind(sock, host, port):
    try:
        sock.bind((host,port))
    except socket.error as err:
        print "failed to bind address: ", err

def socketListen(sock):
    try:
        sock.listen(5)
    except socket.error as err:
        print "failed to listen socket: ", err

def socketAccept(sock):
    try:
        s, a = sock.accept()
    except socket.error as err:
        print "failed to accept client: ", err
    else:
        return s, a

def socketConnection(sock, host, port):
    try:
        sock.connect((host, port))
    except socket.error as err:
        print "failed to connect to server: ", err
        return False
    else:
        return True

def socketSend(sock, data):
    #print 'socket send data', data
    # we add EOD(end of data) as the segmentation of data stream
    data += 'EOD'

    data.encode('utf-8')
    try:
        sock.sendall(data)
    except socket.error as err:
        print "failed to send data: ", err

def socketRecv(sock, recvBuffSize):
    print 'socket recv data'
    data = ''
    while 1:

        buf = sock.recv(recvBuffSize)
        buf.decode('utf-8')
        data = data + buf

        if data[-3:] == 'EOD':
            break

        # server never send ''!
        # this will happen only when the client is terminated unexpectedly
        if not data:
            return data

    return data[:-3]

    # data = ''
    # while 1:
    #     print 'client sock recv'
    #     try:
    #         buf = sock.recv(recvBuffSize)
    #     except socket.error as err:
    #         print "failed to receive data", err
    #     else:
    #         data = data + buf
    #         if data[-3:] == 'EOD':
    #             break
    #
    # return data[:-3]