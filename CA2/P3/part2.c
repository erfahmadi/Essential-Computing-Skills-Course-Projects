#include <stdio.h>
#include <signal.h>
#include <unistd.h>

void handle_sigint(int sig) {
	printf("\nCtrl+C detected! (signal %d)\n", sig);
}

int main() {
	signal(SIGINT, handle_sigint); // Handle Ctrl+C
	signal(SIGTSTP, handle_sigint); // Handle Ctrl+z
	signal(SIGQUIT, handle_sigint); // Handlw Ctrl+\
	
	while (1) {
		printf("Working... you can't stop it!\n");
		sleep(2);
	}
	return 0;
}
