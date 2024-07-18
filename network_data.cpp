using namespace std;
#include<sys/types.h>
#include<sys/socket.h>
#include<netdb.h>
#include<iostream>
#include<cstring>

int main() {

    int status; //Used to catch potential error status of getaddrinfo call
    struct addrinfo objA; //Instance of addrinfo struct stores prep data for socket address.
    struct addrinfo *objAresults; //Points to results of addrinfo

    /* Operations */
    memset(&objA, 0, sizeof(objA)); //Basic C++ note: & is "pass by reference" no copy is made
                                    //Karla says to never pass a struct by value
    objA.ai_family = AF_UNSPEC; //Options are AF_INET (IPv4), AF_INET6 (iPv6), or AF_UNSPEC    
    objA.ai_socktype = SOCK_STREAM; //Use TCP (UDP is SOCK_DGRAM) and less accurate
    objA.ai_flags = AI_PASSIVE; //Setting allows IP address to fill automatically

    /* Attempt to get a socket descriptor with error checking. */ 
    status = getaddrinfo(NULL, "::1", &objA, &objAresults);
    if (status != 0) 
    {
        cerr << "Getaddrinfo() error: " << gai_strerror(status) << endl;
        exit(-1); //Terminate program.
    }
    else cout << "Getaddrinfo() successful." << endl;
    
    //objAresults now points to a linked list of one or more "struct addrinfos"
    
    return 0; 
}
