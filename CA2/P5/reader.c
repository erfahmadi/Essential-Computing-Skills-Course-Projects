#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>

#define MAX_BUF_SIZE 1024

int main(int argc, char *argv[]) {
    char device[MAX_BUF_SIZE];
    char user_msg[MAX_BUF_SIZE];
    int fd, ret;
    if (argc < 2) {
        printf("Usage: %s <device_file>\n", argv[0]);
        return 1;
    }
    strcpy(device, argv[1]);
    fd = open(device, O_RDONLY);
    if (fd < 0) {
        perror("open");
        return 1;
    }
    memset(user_msg, 0, sizeof(user_msg));
    ret = read(fd, user_msg, MAX_BUF_SIZE);
    if (ret >= 0) {
        printf("Read: %s\n", user_msg);
    } else {
        perror("read");
    }
    close(fd);
    return 0;
}

