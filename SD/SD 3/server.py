import socket
import pickle

class Apicultor:
    def __init__(self, nome, idade):
        self.nome = nome
        self.idade = idade
        
    def str_apicultor(self):
        return "Nome: " + self.nome + " | Idade: " + str(self.idade)


class Apiario:
    def __init__(self, id, num_colmeias):
        self.id = id
        self.num_colmeias = num_colmeias
        self.apicultores = []

    def str_apiario(self):
        strg = ""
        strg += "Apiario " + str(self.id) + " com " + str(self.num_colmeias) + " colmeias"
        for apic in self.apicultores :
            strg += '\n\t' + apic.str_apicultor()
        return strg

    def add_apicultores(self, apicultor):
        self.apicultores.append(apicultor)

    def set_id(self, id):
        self.id = id



s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind(("127.0.0.1", 54000))
s.listen()
clientsocket, address = s.accept()
print(f"Conectado com {address}!")

cmd = b''
lista = []

# "Using" indica se é uma mensagem de comando ou um objeto/resposta. Caso for True, o programa não lerá input
# Comandos (para o servidor):
#   $A{numero} ->   (client) Adicionar objeto (numero = 1 (Apiario) ; numero = 2 (Apicultor))
#                   (server) Autorização para enviar objeto
#   $C{numero}{index} ->   (client) Consulta {numero = 0 (Apiario) ; numero = 1 (Todos os Apiarios)}
#                                            {index = posição do Apiario na lista}
#   #A1 -> Resposta do servidor, em texto.
using = False
while True :
    msg = clientsocket.recv(1024)

# Using indica se é uma mensagem de comando ou um objeto/resposta. Se True, o programa não lê imput
    if using == False :
        #Dessempacotamento da mensagem (se for um comando)
        cmd = pickle.loads(msg)

    retn = ""
    if cmd == "end" :
        break
    elif cmd == "$A1" :
        #Using = False -> Comando para indicar o futuro envio de um objeto
        #Using = True  -> O objeto em si
        if using == False :
            using = True
            retn = cmd
        else :
            #Dessempacotamento da mensagem (se for um objeto Apiário)
            obj = pickle.loads(msg)
            obj.set_id(len(lista))
            lista.append(obj)

            using = False
            retn = "#A1Apiario Adicionado!"

    #Para adicionar um Apicultor
    elif cmd[0:3] == "$A2" :
        #Using = False -> Comando para indicar o futuro envio de um objeto
        #Using = True  -> O objeto em si
        if using == False :
            using = True
            retn = cmd[0:3]
        else :
            #Dessempacotamento da mensagem (se for um objeto Apicultor)
            obj = pickle.loads(msg)

            if(int(cmd[3:]) < len(lista)):
                lista[int(cmd[3])].add_apicultores(obj)
                retn = "#A1Apicultor Adicionado!"   
            else:
                retn = "#A1ERRO: Apiario invalido"
            using = False

    # Consultas
    #   $C0 = Consultar um Apiário específico
    #   $C1 = Consultar todos os Apiários
    elif cmd[0:3] == "$C0" :
        retn += "#A1"
        retn += lista[int(cmd[3])].str_apiario()

    elif cmd[0:3] == "$C1" :
        retn += "#A1"
        for apiario in lista :
            retn += '\n' + apiario.str_apiario()
    
    #Caso não houver um comando reconhecível, retorna "#E0", indicando falha
    else :
        retn = "#E0"
    
    #Empacotamento da mensagem de retorno
    retn = pickle.dumps(retn)
    clientsocket.sendall(retn)
s.close()