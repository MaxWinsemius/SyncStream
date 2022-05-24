#include <iostream>
#include <cstring>
#include <string>
#include <sys/socket.h>
#include <unistd.h>
#include <netinet/in.h>

#include <errno.h>
#include <sys/types.h>
#include <stdlib.h>
#include <stdio.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <iomanip>

#define DEBUG_PRINTALLRGB false

void *get_in_addr(struct sockaddr *sa)
{
    //if (sa->sa_family == AF_INET) {
        return &(((struct sockaddr_in*)sa)->sin_addr);
    //}

    //return &(((struct sockaddr_int6*)sa)->sin6_addr);
}

void console_clear()
{
    // Beautiful method of clearing the console whoop whoop
    std::cout << u8"\033[2J\033[1;1H";
}

void print_data(int port, int buffer_size, int* buffer)
{
    // TODO: print buffer
    std::cout << "Working on port " << port << " with bufsize " << buffer_size << " and max packet length ";
}

void print_full_frame_buffer(unsigned char* frame_buffer, int frame_buffer_size)
{
    for (int i = 0; i < frame_buffer_size; i++) {
        int r = frame_buffer[i*3    ] * 16;
        int g = frame_buffer[i*3 + 1] * 16;
        int b = frame_buffer[i*3 + 2] * 16;
        char rgb[50];
        //rgb < r << ";" << g << ";" << b << "m";
        sprintf(rgb, "%i;%i;%im", r, g, b);


        std::cout << "\x1b[48;2;" << rgb <<  "\x1b[38;2;" << rgb << "#";
    }

    std::cout << "\033[0m\n";
}

void process_udp(char* buffer, unsigned char* frame_buffer, int numbytes, int frame_buffer_size)
{
    // With retrieved package, check if it is valid with skip if it is invalid
    if (numbytes % 3 != 0) {
        std::cerr << "Size of the message is not of triplet size, but of " << numbytes << " instead. Skipping message\n";
        return;
    }

    // Store framebuffer
    for (int i = 0; i < numbytes; i += 3) {
        char m0 = buffer[i];
        char m1 = buffer[i + 1];
        char m2 = buffer[i + 2];
        
        unsigned int index = ((unsigned int) m0 << 4) + (((unsigned int) (m1 & 0xF0)) >> 4);
        if (index >= frame_buffer_size) {
            std::cerr << "Pixel at (3*index) " << 3 * index << " received, but framebuffer size is " << frame_buffer_size;
            std::cerr <<" Skipping pixel\n";
            continue;
        }

        if (DEBUG_PRINTALLRGB) {
            printf("[%4i %4i %2i] ", index, (unsigned int) m0 << 4, (unsigned int) (m1 & 0xF0) >> 4);
        }

        unsigned int r = (unsigned int) (m1 & 0x0F);
        unsigned int g = (unsigned int) ((m2 & 0xF0) >> 4);
        unsigned int b = (unsigned int) (m2 & 0x0F);
        frame_buffer[3*index]     = r;
        frame_buffer[3*index + 1] = g;
        frame_buffer[3*index + 2] = b;
        if (DEBUG_PRINTALLRGB) {
            printf("R:%i G:%i B:%i\n", r, g, b);
        }
    }
}

int main( int argc, char* argv[] )
{
    int buffer_size = 300;
    char* port = "1337";
    int frame_buffer_size = 10;
    unsigned char* frame_buffer;

    int sockfd;
    struct addrinfo hints, *servinfo, *p;
    int rv;
    int numbytes;
    struct sockaddr_storage client_addr;
    socklen_t addr_len;
    char s[INET6_ADDRSTRLEN];

    // Retrieve arguments
    switch (argc) {
        case 4:
            buffer_size = std::stoi(argv[3]);
        case 3:
            port = argv[2];
        case 2:
            frame_buffer_size = std::stoi(argv[1]);
        default:
            break;
    }

    // Init:
    // Create framebuffer of correct size
    char* buffer = (char*) malloc(sizeof(int) * buffer_size);
    memset(buffer, 0, buffer_size);

    frame_buffer = (unsigned char*) malloc(sizeof(unsigned char) * frame_buffer_size * 3);

    // open UDP socket with given or default port OR the next available port after previously selected port
    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_DGRAM;
    hints.ai_flags = AI_PASSIVE;

    if ((rv = getaddrinfo(NULL, port, &hints, &servinfo)) != 0) {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(rv));
        return 1;
    }

    for (p = servinfo; p != NULL; p = p->ai_next) {
        if ((sockfd = socket(p->ai_family, p->ai_socktype, p->ai_protocol)) == -1) {
            perror("Listener: socket");
            continue;
        }

        if (bind(sockfd, p->ai_addr, p->ai_addrlen) == -1) {
            close(sockfd);
            perror("listener: bind");
            continue;
        }

        break;
    }

    if (p == NULL) {
        perror("Listener: failed to bind socket\n");
        return 2;
    }

    freeaddrinfo(servinfo);

    printf("Running at port %s, with %i leds\n", port, frame_buffer_size);
    printf("Listener waiting to recvfrom...\n");
    printf("Hello, please make sure you are using a gpu-accelerated terminal if you want to prevent epilepsy attacks!\n");

    // Start waiting for message on UDP socket
    // Loop:
    while (true) {
        // Wait for UDP package
        addr_len = sizeof(client_addr);
        //printf("Waiting for udp package to arrive, addr len = %i\n", addr_len);
        if ((numbytes = recvfrom(sockfd, buffer, buffer_size, 0, (struct sockaddr *)&client_addr, &addr_len)) == -1) {
            perror("recvfrom");
            return 3;
        }
        console_clear();

        //printf("received package, addr len = %i\n", addr_len);
        process_udp(buffer, frame_buffer, numbytes, frame_buffer_size);

        // Write framebuffer to console
        print_full_frame_buffer(frame_buffer, frame_buffer_size);

        printf("\n\n\n");
        printf("Running at port %s, with %i leds\n", port, frame_buffer_size);
    }

    return 0;
}
