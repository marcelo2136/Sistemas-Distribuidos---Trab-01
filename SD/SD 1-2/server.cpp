#ifndef _WIN32_WINNT
    #define _WIN32_WINNT 0x0600
#elif _WIN32_WINNT < 0x0600
    #undef _WIN32_WINNT
    #define _WIN32_WINNT 0x0600
#endif


#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <WS2tcpip.h>
#pragma comment (lib, "ws2_32.lib")



class Pessoa {
    std::string nome;
    std::string cpf;
    int idade;
public:
    Pessoa(std::string nome, std::string cpf, int idade){
        this->cpf = cpf;
        this->idade = idade;
        this->nome = nome;
    }

    std::string to_str(){
        std::string str;
        str = nome + '$' + cpf + '$' + std::to_string(idade);
        return str;
    }

    friend std::ostream& operator<<(std::ostream& os, const Pessoa& pessoa){
        os << "Nome: " << pessoa.nome << " | CPF: " << pessoa.cpf << "\nIdade: " << pessoa.idade << '\n';
        return os;
    }

};



int main(){
    std::vector<Pessoa*> pessoas;

    //Windsock
    WSADATA wsData;
    WORD ver = MAKEWORD(2, 2);

    int wsOk = WSAStartup(ver, &wsData);
    if (wsOk != 0){
        std::cout << "ERRO (WSA)\n";
        return 0;
    }

    //Socket
    SOCKET listening = socket(AF_INET, SOCK_STREAM, 0);
    if(listening == INVALID_SOCKET){
        std::cout << "ERRO (SOCKET)\n";
        return 0;
    }

    //IP e porta
    sockaddr_in hint;
    hint.sin_family = AF_INET;
    hint.sin_port = htons(54000);
    hint.sin_addr.S_un.S_addr = INADDR_ANY;

    //BIND
    bind(listening, (sockaddr*)&hint, sizeof(hint));

    //Windsock e BIND
    listen(listening, SOMAXCONN);

    //Conexão
    sockaddr_in client;
    int clientSize = sizeof(client);

    SOCKET clientSocket = accept(listening, (sockaddr*)&client, &clientSize);
    if(clientSocket == INVALID_SOCKET){
        std::cout << "ERRO (SOCKET CLIENTE)\n";
        return 0;
    }

    char host[NI_MAXHOST];
    char service[NI_MAXHOST];

    ZeroMemory(host, NI_MAXHOST);
    ZeroMemory(service, NI_MAXSERV);

    if(getnameinfo((sockaddr*)&client, sizeof(client), host, NI_MAXHOST, service, NI_MAXSERV, 0) == 0){
        std::cout << "HOST CONECTADO\n";
    }
    else{
        inet_ntop(AF_INET, &client.sin_addr, host, NI_MAXHOST);
        std::cout << "HOST CONECTADO!\n";
    }

    //fecha socket
    closesocket(listening);

    //loop
    char buff[4096];

    while (true){
        ZeroMemory(buff, 4096);

        //std::cout << 1;

        int byteReceived = recv(clientSocket, buff, 4096, 0);
        if(byteReceived == SOCKET_ERROR){
            std::cout << "ERRO RECV()\n";
            break;
        }

        if(byteReceived == 0){
            std::cout << "CLIENTE DESCONECTOU\n";
            break;
        }

        std::string receiver(buff, 0, byteReceived);

        std::stringstream ss;
        std::string aux;

        if (receiver[0] == '&'){

            ss << "Tamanho do Vetor: " << receiver[1] << '\n';
            //std::cout << "!!!!" << aux;
            //send(clientSocket, aux.c_str(), aux.length() + 1, 0);
        }
        else if(receiver[0] == '$'){
            std::string nome, cpf;
            int idade;
            receiver = receiver.substr(receiver.find('$') + 1);
            nome = receiver.substr(0, receiver.find('$'));

            receiver = receiver.substr(receiver.find('$') + 1);
            cpf  = receiver.substr(0, receiver.find('$'));

            receiver = receiver.substr(receiver.find('$') + 1);
            idade = stoi(receiver.substr(0, receiver.find('$')));

            pessoas.push_back(new Pessoa(nome, cpf, idade));

            
            ss << *pessoas[pessoas.size()-1];
        }

        aux = ss.str();
        send(clientSocket, aux.c_str(), aux.length() + 1, 0);

        //Mensagem de retorno
        //send(clientSocket, buff, byteReceived + 1, 0);
    }



    std::cout << "Tamanho do Vetor: " << pessoas.size() << '\n';
    for(int i = 0; i < pessoas.size(); i++){
        std::cout << *pessoas[i];
    }

    ///////////////////////////     ARQUIVO
    ///////////////////////////
    std::fstream fs;
    fs.open ("server.txt", std::fstream::in | std::fstream::out | std::fstream::app);

    fs << "Tamanho do Vetor: " << pessoas.size() << '\n';

    for(int i = 0; i < pessoas.size(); i++){
        fs << *pessoas[i];
    }

    fs.close();
    ///////////////////////////
    ///////////////////////////


    closesocket(clientSocket);
    WSACleanup();

    return 0;
};


// g++ client.cpp -o client -lws2_32
// g++ server.cpp -o server -lws2_32