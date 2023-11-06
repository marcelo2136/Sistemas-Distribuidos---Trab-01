import socket
import threading
import json
from datetime import datetime

class Candidato:
    def __init__(self, nome, partido,numero):
        self.nome = nome
        self.partido = partido
        self.numero = numero
        self.votos = 0
        self.voto_percentual = 0

    def add_voto(self):
        self.votos += 1

    def get_votos(self):
        return self.votos

    def get_numero(self):
        return self.numero
    
    def str_candidato(self):
        return "Num: " + self.numero + " | Nome: " + self.nome + " | Partido: " + self.partido



def time_left(max, actual):
    time = (int(max[0:2])*60*60)  + (int(max[3:5])*60) + int(max[6:8])
    time -= (int(actual[0:2])*60*60)  + (int(actual[3:5])*60) + int(actual[6:8])
    return time


resultado_final = False
votos = 0
candidatos = {}
connections = {}
limit_time = ""

def handle_client(clientsocket, address, udp_socket, max_time):
    print(f"[{address}] CONECTOU")
    global votos
    cpf_votante = ''
    admin = False
    logged = False
    voted = False
    connected = True

    while connected == True :
        global resultado_final
        if resultado_final == True:
            return
        
        msg = clientsocket.recv(1024).decode("utf-8")

        retn = {}
        retn_msg = ""
        json_recv = json.loads(msg)

        cmd = json_recv["operacao"] 

        if cmd != "TIMER" :
            print(msg)

        #TIMER
        if cmd == "TIMER" and time_left(max_time, json_recv["time_now"]) <= 0:
            print(max_time)
            list_aux = {}

            for x in candidatos:
                vt_percentual = str(float("{:.2f}".format((candidatos[x].get_votos()/votos)*100))) + "%"
                list_aux[vt_percentual] = candidatos[x]

            list_aux = dict(sorted(list_aux.items(), reverse=True))
            list_results = {}

            list_results["msg"] = "VENCEDOR: " + list(list_aux.values())[0].str_candidato() + " | Com " + str(candidatos[list(list_aux.values())[0].get_numero()].get_votos()) + " votos"
            
            for x in list_aux:
                list_results[x] = list_aux[x].str_candidato()
            list_results["cmd"] = "BREAK"

            retn_msg = json.dumps(list_results)
            udp_socket.sendto(retn_msg.encode("utf-8"), ("224.1.1.1", 55000))

            retn_msg = "BREAK"
            resultado_final = True
        
        elif cmd == "TIMER":
            retn_msg = "ok"

        elif  cmd == "END":
            retn_msg = "[SERVER] DESCONECTANDO..."
            connected = False

        elif cmd == "LOGIN":
            cpf = json_recv["cpf"]
            if logged == False and cpf not in connections:
                cpf_votante = cpf
                
                connections[cpf] = "SEMVOTO"

                logged = True
                retn_msg = "[SERVER] LOGADO COM SUCESSO!"
                retn_msg += "\n\tEscolha seu candidato:"
                for cdt in candidatos:
                    retn_msg += "\n\t\t" + candidatos[cdt].str_candidato()

            else:
                retn_msg = "[SERVER] VOCÊ JÁ ESTÁ LOGADO!"

        elif cmd == "VOTAR":
            numero = json_recv["num"]
            if numero in candidatos and voted == False and logged == True:
                candidatos[numero].add_voto()
                votos += 1
                connections[cpf_votante] = "COMVOTO"
                voted = True

                print(f"Voto para {candidatos[numero].str_candidato()}, {candidatos[numero].get_votos()} votos totais")

                retn_msg = "[SERVER] VOTO EFETUADO!"
                retn["cmd"] = "LISTEN"

            elif logged == False:
                retn_msg = "[SERVER] FAÇA O LOGIN!"
            elif voted == True:
                retn_msg = "[SERVER] VOCÊ JÁ VOTOU!"
            else:
                retn_msg = "[SERVER] CANDIDATO AUSENTE!"
        
        #Comandos do Admin
        elif cmd == "LOG-A":
            cpf = json_recv["cpf"]
            if logged == False:
                connections[cpf] = "ADMIN"
                logged = True
                admin = True
                retn_msg = "[SERVER] LOGADO COM SUCESSO!"
            else:
                retn_msg = "[SERVER] VOCÊ JÁ ESTÁ LOGADO!"

        elif cmd == "ADD-C" and admin == True:
            numero = json_recv["numero"]
            if numero not in candidatos:
                novo_candidato = Candidato(json_recv["nome"], json_recv["partido"], numero)
                candidatos[numero] = novo_candidato
                retn_msg = "[SERVER] CANDIDATO ADICIONADO!"
            else:
                retn_msg = "[SERVER] PARTIDO JÁ POSSUI UM CANDIDATO!"
        
        elif cmd == "DEL-C" and admin == True:
            numero = json_recv["numero"]
            if numero in candidatos:
                votos -= candidatos[numero].get_votos()
                del candidatos[numero]
                retn_msg = "[SERVER] CANDIDATO DELETADO!"
            else:
                retn_msg = "[SERVER] CANDIDATO INEXISTENTE!"

        elif cmd == "ALERT" and admin == True:
            retn_msg = "[ALERTA] " + json_recv["msg"]
            list_json = {}
            list_json["msg"] = retn_msg
            retn_msg = json.dumps(list_json)
            udp_socket.sendto(retn_msg.encode("utf-8"), ("224.1.1.1", 55000))

            retn_msg = "[SERVER] MENSAGEM ENVIADA!"

        retn["msg"] = retn_msg

        retn_json = json.dumps(retn)
        clientsocket.sendall(retn_json.encode("utf-8"))

        if retn["msg"] == "BREAK" or cmd == "END":
            clientsocket.close()
    return







def main():

    now = datetime.now()
    tm_now = now.strftime("%H:%M:%S")

    print(datetime.now())
    limit_time = input("Insira a data limite (Formato HH:MM:SS): ")
    print(time_left(limit_time,tm_now))

    #SOCKET TCP
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 54000))

    s.listen()

    #SOCKET UDP
    ttl = 5

    s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s_udp.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    #clientsocket, address = s.accept()

    while True:
        clientsocket, address = s.accept()

        print(f"Conectado com {address}!")
        thread = threading.Thread(target=handle_client, args=(clientsocket, address, s_udp, limit_time))
        thread.start()

        print(f"[CONEXÕES ATIVAS] {threading.active_count() - 1}")
       
   
if __name__ == "__main__":
    main()