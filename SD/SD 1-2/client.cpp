#ifndef _WIN32_WINNT
    #define _WIN32_WINNT 0x0600
#elif _WIN32_WINNT < 0x0600
    #undef _WIN32_WINNT
    #define _WIN32_WINNT 0x0600
#endif


#include <fstream>
#include <iostream>
#include <string>
#include <vector>
#include <sstream>
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
        str = '$' + nome + '$' + cpf + '$' + std::to_string(idade);
        return str;
    }

    friend std::ostream& operator<<(std::ostream& os, const Pessoa& pessoa){
        os << "Nome: " << pessoa.nome << " | CPF: " << pessoa.cpf << "\nIdade: " << pessoa.idade << '\n';
        return os;
    }

};


int main(){

    int quant;
    std::cin >> quant;
    
    std::vector<Pessoa*> pessoas;

    std::string nome, cpf;
    int idade;

    for(int i = 0; i < quant; i++){
        std::getline(std::cin >> std::ws, nome);
        std::getline(std::cin, cpf);
        std::cin >> idade;

        pessoas.push_back(new Pessoa(nome, cpf, idade));
        std::cout << *pessoas[i];
    }


    //IP e Porta
    std::string ipAddress = "127.0.0.1";
    int port = 54000;

    //Windsock
    WSAData data;
    WORD ver = MAKEWORD(2, 2);
    int wsResult = WSAStartup(ver, &data);
    if(wsResult != 0){
        std::cout << "ERRO (WINDSOCK)\n";
        return 0;
    }

    //Socket
    SOCKET sock = socket(AF_INET, SOCK_STREAM, 0);
    if(sock == INVALID_SOCKET){
        std::cout << "ERRO (SOCKET)\n";
        WSACleanup();
        return 0;
    }

    //Hint Structure
    sockaddr_in hint;
    hint.sin_family = AF_INET;
    hint.sin_port = htons(port);
    inet_pton(AF_INET, ipAddress.c_str(), &hint.sin_addr);

    //Conectar ao server
    int connResult = connect(sock, (sockaddr*)&hint, sizeof(hint));
    if(connResult == SOCKET_ERROR){
        std::cout << "ERRO (CONNECT)\n";
        closesocket(sock);
        WSACleanup();
        return 0;
    }

    //Loop
    char buff[4096];
    std::string userInput;


    std::string aux_quant = '&' + std::to_string(quant) + '&';
    

    int sendResult = send(sock, aux_quant.c_str(), aux_quant.size() + 1, 0);
    ZeroMemory(buff, 4096);
    int bytesReceived = recv(sock, buff, 4096, 0);


    std::cout << "-----------------------------------\n";
    std::cout << "Retorno Server\n";
    std::cout << "-----------------------------------\n";

    if(bytesReceived > 0){
        std::cout << "SERVER " << std::string(buff, 0, bytesReceived) << '\n';
    }

    for(int i = 0; i < quant; i++){      
        userInput = pessoas[i]->to_str();

        if(userInput.size() > 0){
            int sendResult = send(sock, userInput.c_str(), userInput.size() + 1, 0);
            if(sendResult != SOCKET_ERROR){
                ZeroMemory(buff, 4096);
                int bytesReceived = recv(sock, buff, 4096, 0);

                if(bytesReceived > 0){
                    std::cout << "SERVER " << std::string(buff, 0, bytesReceived);
                }
            }

        }
    }


    //Print
    std::cout << "-----------------------------------\n";
    std::cout << "Print\n";
    std::cout << "-----------------------------------\n";
    std::cout << "Tamanho do Vetor: " << pessoas.size() << '\n';
    for(int i = 0; i < pessoas.size(); i++){
        std::cout << *pessoas[i];
    }


    //ARQUIVO

    std::fstream fs;
    fs.open ("client.txt", std::fstream::in | std::fstream::out | std::fstream::app);

    fs << "Tamanho do Vetor: " << pessoas.size() << '\n';

    for(int i = 0; i < pessoas.size(); i++){
        fs << *pessoas[i];
    }

    fs.close();

/*
    do{
        std::cout << ">";
        std::getline(std::cin, userInput);
        
        if(userInput.size() > 0){
            int sendResult = send(sock, userInput.c_str(), userInput.size() + 1, 0);
            if(sendResult != SOCKET_ERROR){
                ZeroMemory(buff, 4096);
                int bytesReceived = recv(sock, buff, 4096, 0);

                if(bytesReceived > 0){
                    std::cout << "SERVER " << std::string(buff, 0, bytesReceived) << '\n';
                }
            }

        }


    } while(userInput.size() > 0);
*/
    closesocket(sock);
    WSACleanup();

    return 0;
}