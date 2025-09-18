#include <stdio.h>
#include <signal.h>
#include <unistd.h>
 
void handle_sigint(int sig) {
	printf("\nCtrl+C detected! (signal %d)\n", sig);
}
   
int main() {
	struct sigaction sa;
	sa.sa_handler = handle_sigint;
	sa.sa_flags = SA_RESTART;

	sigaction(SIGINT, &sa, NULL); // Handle Ctrl+C
	sigaction(SIGTSTP, &sa, NULL); // Handle Ctrl+z
	sigaction(SIGQUIT, &sa, NULL); // Handlw Ctrl+\
    
	while (1) {
		printf("Working... you can't stop it!\n");
        sleep(2);
    }
    return 0;
}
     
