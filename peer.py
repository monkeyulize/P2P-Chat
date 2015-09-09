import socket, select, string, sys

def help_prompt() :
    print("-online_users\n\tList all online users logged onto the registry server")
    print("-connect [username]\n\tRequest a connection to the peer with specified username")
    print("-disconnect [username]\n\tEnd chat session with specified username")
    print("-talk [username] [message]\n\tSend specified message to the peer with specified username")
    print("-logoff\n\tLog off the registry server")


def send_message(ip, port, message):
    for sock in CONNECTED_PEERS:
        if sock != listen and sock != s and sock != sys.stdin:
            if str(sock.getpeername()[0]) == ip and int(sock.getpeername()[1]) == int(port):               
                sock.send(message)
        
def remove_peer(peername):
    for peer in CONNECTED_PEERS:
        if peer != sys.stdin and peer != listen and peer != s:            
            if peer.getpeername()[0] == peers[peername][0] and peer.getpeername()[1] == int(peers[peername][1]):
                CONNECTED_PEERS.remove(peer)
                peer.close()
       

    
if __name__ == "__main__":
     
    if len(sys.argv) != 4:
        print('Usage : python peer.py [hostname] [port] [username]')
        sys.exit()
    CONNECTED_PEERS = []
    RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
    #system argument 
    host = sys.argv[1]
    port = int(sys.argv[2])
    my_username = sys.argv[3]
    # create a socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    
    
    # Set a timeout on blocking socket operations.
    s.settimeout(2)
    
    # connect to remote host
    try :
        s.connect((host, port))
    except :
        print('Unable to connect')
        sys.exit()
    print('Connected to registry server')
    listen.bind((s.getsockname()[0], 0))
    listen.listen(10)
    s.send("listening " + str(listen.getsockname()[1]) + " " + my_username)


    CONNECTED_PEERS.append(listen)
    CONNECTED_PEERS.append(sys.stdin)
    CONNECTED_PEERS.append(s)
    peers = {}
    while 1:
         
        # Get the list sockets which are readable
        read_sockets, write_sockets, error_sockets = select.select(CONNECTED_PEERS , [], [])
        
        for sock in read_sockets:
            #incoming message from remote server
            if sock == listen:
                sockfd, addr = listen.accept()
                CONNECTED_PEERS.append(sockfd)
                print("Peer (%s, %s) connected" % addr)
            elif sock == s:
                data = sock.recv(4096)
                if not data :
                    print '\nDisconnected from registry server'
                    CONNECTED_PEERS.remove(s)
                    s.close()
                else :
                    peers.clear()
                    for line in data.split('\n'):

                        peers[line.split()[0]] = (line.split()[1], line.split()[2])
                        

                    print(data)

            elif sock == sys.stdin:
                msg = sys.stdin.readline()
                if(msg.split()[0] == "-help"):
                    help_prompt()
                elif (msg.split()[0] == "-connect"):
                    if len(msg.split()) != 2:
                        print ("Incorrect usage, type -help for more info")
                    else:
                        peer_found = False
                        conn_refused = False
                        p = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        p.settimeout(2)
                        print("Connecting...")
                        for peer in peers:
                            if msg.split()[1] == peer:
                                try:
                                    p.connect((peers[peer][0], int(peers[peer][1])))
                                    print("Connected")
                                    p.send("my_username " + my_username)
                                    CONNECTED_PEERS.append(p)
                                    peer_found = True
                                    break
                                except:
                                    print("Connection refused, peer might be offline\nTry using -online_users again")
                                    conn_refused = True
                                    break
                        if peer_found == False and conn_refused == False:
                            print("Peer not found, try using -online_users")
                elif (msg.split()[0] == "-online_users"):
                    print("Requesting online users")
                    s.send(msg)
                elif (msg.split()[0] == "-logoff"):
                    print("Logging off...")
                    s.send(msg)
                    sys.exit()
                elif (msg.split()[0] == "-talk"):
                    if len(msg.split(' ', 2)) != 3:
                        print ("Incorrect usage, type -help for more info")
                    else:
                        peer_found = False
                        for peer in peers:
                            if msg.split()[1] == peer:
                                send_message(peers[peer][0], peers[peer][1], msg.split(' ', 2)[2])
                                peer_found = True
                        if peer_found == False:
                            print("Peer not found, try connecting to them")
                elif (msg.split()[0] == "-disconnect"):
                    if len(msg.split()) != 2:
                        print ("Incorrect usage, type -help for more info")
                    else:
                        for peer in peers:                       
                            if msg.split()[1] == peer:
                                remove_peer(peer)
                                print("Disconnected from %s" % peer)
            else:  
                data = sock.recv(RECV_BUFFER)
                if not data:
                    for peer in peers:
                        if sock.getpeername()[0] == peers[peer][0] and sock.getpeername()[1] == int(peers[peer][1]): 
                            print("!%s is offline" % peer)
                            remove_peer(peer)
                            break
                    
                else:
                    if data.split()[0] == "my_username":
                        peers[data.split()[1]] = (sock.getpeername()[0], sock.getpeername()[1])
                    else:                       
                        for peer in peers:
                            if sock.getpeername()[0] == peers[peer][0] and sock.getpeername()[1] == int(peers[peer][1]):                                                               
                                print("<" + peer + "> " + data.strip())
                                break

                    
