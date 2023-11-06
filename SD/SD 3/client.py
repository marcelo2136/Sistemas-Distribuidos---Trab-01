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
            strg += '\n' + apic.str_apicultor()

    def add_apicultores(self, apicultor):
        self.apicultores.append(apicultor)

    def set_id(self, id):
        self.id = id



s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", 54000))

# Using indica se é uma mensagem de comando ou um objeto/resposta. Se True, o programa não lê imput
# Comandos (para o cliente):
#   add_apiario {quantidade de colmeias}    ->  (client) Adicionar Apiário
#   add_apicultor {nome} {idade} {apiario}  ->  (client) Adicionar Apicultor
#   consulta {operacao} {id do apiario}     ->  (client) Consulta um ou mais Apiários.  
#                                               operacao = "apiario"    -> Consulta um Apiário específico
#                                               operacao = "all"        -> Consulta todos os Apiários
using = False
while True :
    line = ""

# Using indica se é uma mensagem de comando ou um objeto/resposta. Se True, o programa não lê imput
    if using == False :
        line = input(line)
        cmd = line.split(" ")

    obj = ''
    if cmd[0] == "exit" or cmd[0] == "end":
        obj = "end"
        msg = pickle.dumps(obj)
        s.send(msg)
        break

    elif cmd[0] == "add_apiario" :
        if using == False :
            obj = "$A1"
        else :
            obj = Apiario(0,int(cmd[1]))  

    elif cmd[0] == "add_apicultor" :
        if using == False :
            obj = "$A2" + cmd[3]
        else :
            obj = Apicultor(cmd[1],int(cmd[2]))  

    elif cmd[0] == "consulta" :
        if cmd[1] == "apiario":
            obj = "$C0" + cmd[2]
        elif cmd[1] == "all":
            obj = "$C1"
    
    #Serializando a mensagem
    msg = pickle.dumps(obj)
    s.send(msg)


    # Comandos de retorno #
    data = s.recv(1024)

    #Desserialização
    data = pickle.loads(data)
    
    #Comando para os if/else
    retn = data[0:3]

    
    if retn == "$A1" or retn == "$A2":
        using = True

    elif retn == "#A1":
        print(data[3:])
        using = False

    elif retn == "#E0":
        break
s.close()