import socket
import json

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 54000))

    connected = True
    while connected :
        line = input(">")

        line_slice = line.split(" ")

        cmd = line_slice[0]

        obj = { "operacao" : cmd}

        if cmd == "END":
            connected = False

        elif cmd == "LOG-A":
            obj["cpf"]      = line_slice[1]
        
        elif cmd == "ADD-C":
            obj["nome"]     = line_slice[1]
            obj["partido"]  = line_slice[2]
            obj["numero"]   = line_slice[3]

        elif cmd == "DEL-C":
            obj["numero"]   = line_slice[1]

        elif cmd == "ALERT":
            obj["msg"]      = line[6:]
            print(line[5:])

        json_string = json.dumps(obj)
        s.send(json_string.encode("utf-8"))


        data = s.recv(1024).decode("utf-8")
        data = json.loads(data)

        print(data["msg"])

    s.close()

if __name__ == "__main__":
    main()