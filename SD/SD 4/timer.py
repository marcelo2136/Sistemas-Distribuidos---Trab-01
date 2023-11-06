import socket
import json
from datetime import datetime

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 54000))

    connected = True
    prev = ""
    while connected :
        now = datetime.now()
        tm_now = now.strftime("%H:%M:%S")

        obj = {}
        obj["operacao"] = "TIMER"
        obj["time_now"] = tm_now

        print(obj)

        json_string = json.dumps(obj)
        if prev != tm_now:
            s.send(json_string.encode("utf-8"))
            prev = tm_now

        data = s.recv(1024).decode("utf-8")
        data = json.loads(data)
        print(data)
        if data["msg"] == "BREAK":
            break
        elif data["msg"] == "ok":
            prev = ""
    s.close()

if __name__ == "__main__":
    main()