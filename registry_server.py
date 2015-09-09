import socket, select, sys

def remove_peer(peername):

    for peer in CONNECTED_PEERS:
        if peer != server_socket:          
            if peer.getpeername()[0] == peers[peername][0] and peer.getpeername()[1] == int(peers[peername][1]):
                CONNECTED_PEERS.remove(peer)                
                peer.close()
if __name__ == "__main__":

    CONNECTED_PEERS = []
    PORT = 5001
    RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT)) 
    server_socket.listen(10) 
    CONNECTED_PEERS.append(server_socket)
    print("Registry server started on port " + str(PORT))
    peers = {}
    while 1:
        inputs = [CONNECTED_PEERS]
        read_sockets, write_sockets, error_sockets = select.select(CONNECTED_PEERS, [], [])    
        for sock in read_sockets:
            if sock == server_socket:
                sockfd, addr = server_socket.accept()               
                CONNECTED_PEERS.append(sockfd)
                print("Client (%s, %s) connected" % addr)
                
            else:
                try:
                    data = sock.recv(RECV_BUFFER)                
                    if data == "-online_users\n":
                        to_send = ""
                        for user in peers:
                            if str(sock.getpeername()[0]) != peers[user][0] or int(sock.getpeername()[1]) != int(peers[user][1]):
                                to_send += str(user) + " " + peers[user][0] + " " + str(peers[user][2]) + "\n"
                        to_send = to_send.strip("\n")
                        sock.send(to_send)
                    elif data == "-logoff\n":
                        print("Client %s is offline" % str(sock.getpeername()))
                        for peer in peers:
                            if sock.getpeername()[0] == peers[peer][0] and sock.getpeername()[1] == int(peers[peer][1]): 
                                remove_peer(peer)                    
                                del peers[peer]
                                break;                       
                    elif data.split()[0] == "listening":
                        peers[data.split()[2]] = (sock.getpeername()[0], sock.getpeername()[1], data.split()[1])
                except:
                    print("Client %s is offline" % str(sock.getpeername()))
                    for peer in peers:
                        if sock.getpeername()[0] == peers[peer][0] and sock.getpeername()[1] == int(peers[peer][1]): 
                            remove_peer(peer)                    
                            del peers[peer]
                            break;                    
                    continue
