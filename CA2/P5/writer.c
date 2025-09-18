#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>

#define MAX_BUF_SIZE 1024

int main(int argc, char *argv[]) {
    char device[MAX_BUF_SIZE];
    char user_msg[MAX_BUF_SIZE];
    int fd, ret;
    if (argc < 3) {
        printf("Usage: %s <device_file> <message>\n", argv[0]);
        return 1;
    }
    strcpy(device, argv[1]);
    strcpy(user_msg, argv[2]);
    fd = open(device, O_WRONLY);
    if (fd < 0) {
        perror("open");
        return 1;
    }
    ret = write(fd, user_msg, strlen(user_msg));
    if (ret >= 0) {
        printf("Wrote: %s\n", user_msg);
    } else {
        perror("write");
    }
    close(fd);
    return 0;
}

