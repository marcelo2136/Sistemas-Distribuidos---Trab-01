import socket
import struct
import json

def main():
    #SOCKET TCP
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 54000))

    #SOCKET UDP
    MCAST_GRP = '224.1.1.1'
    MCAST_PORT = 55000

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.bind(('', MCAST_PORT))
    mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    cmd = ""
    connected = True
    while connected :
        line = ''
        if cmd != "LISTEN":
            line = input(">")
            line_slice = line.split(" ")
            cmd = line_slice[0]

        obj = { "operacao" : cmd }

        if cmd == "END":
            connected = False

        elif cmd == "LOGIN":
            obj["cpf"] = line_slice[1]

        elif cmd == "VOTAR":
            obj["num"] = line_slice[1]

        json_string = json.dumps(obj)

        if cmd != "LISTEN":
            s.send(json_string.encode("utf-8"))

        data = b''
        if cmd != "LISTEN":
            data = s.recv(1024).decode("utf-8")
        else:
            data = sock.recv(1024).decode("utf-8")  

        data = json.loads(data)
        #print(data)

        if "cmd" in data and data["cmd"] == "LISTEN":
            cmd = "LISTEN"
        elif "cmd" in data and data["cmd"] == "BREAK":
            cmd = "BREAK"

        print(data["msg"])

        if cmd == "BREAK":
            for x in data:
                if x != "msg" and x != "cmd":
                    str_aux = "\t " + x + " | " + data[x]
                    print(str_aux)
            break
    s.close()

if __name__ == "__main__":
    main()