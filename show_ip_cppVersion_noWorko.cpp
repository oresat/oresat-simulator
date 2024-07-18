#include <stdio.h>
#include <cstring>
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <iostream>

using namespace std;

int main(int argc, char *argv[]) {
    struct addrinfo objA, *objAresults, *objAptr;
   
    int status;
    
    char ip[INET6_ADDRSTRLEN];

    if (argc != 2) 
    {
        cerr << "Error." << endl;   
        return 1;
    }


    memset(&objA, 0, sizeof(objA));
    objA.ai_family = AF_UNSPEC;
    objA.ai_socktype = SOCK_STREAM;

    if ((status = getaddrinfo(argv[1], NULL, &objA, &objAresults)) != 0)
    {
        cerr << "getaddrinfo() error: " << gai_strerror(status);
        return -1;
    }

    cout << "IP Addresses for: " << argv[1] << endl;

    for (objAptr = objAresults; objAptr != nullptr; objAptr = objAptr->ai_next)
    {
        void *addr;
        char *ipver;
        
        if (objAptr->ai_family == AF_INET) 
        {   
            struct sockaddr_in *ipv4 = (struct sockaddr_in *)objAptr->ai_addr;
            addr = &(ipv4->sin_addr);
            ipver = "IPv4";
        }
        else 
        {
            struct sockaddr_in6 *ipv6 = (struct sockaddr_in6 *)objAptr->ai_addr;
            addr = &(ipv6->sin6_addr);
            ipver = "IPv6";
        }
    }
        
    inet_ntop(objAptr->ai_family, addr, ipstr, sizeof(ipstr));
    cout << ipver << "\n" << ipstr << endl;

    freeaddrinfo(objAresults);

    return 0;
}












