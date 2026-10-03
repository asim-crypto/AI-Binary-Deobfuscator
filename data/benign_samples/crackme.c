#include <stdio.h>
#include <string.h>

int FUN_001050(char *a1) {
    char s1[] = "Q3ViM3Jfc2Vj"; // "Cyber_sec" encoded/obfuscated 
    if (strcmp(a1, s1) == 0) {
        return 1;
    }
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: %s <key>\n", argv[0]);
        return 1;
    }
    
    if (FUN_001050(argv[1])) {
        printf("[+] Validation passed. Payload unlocked.\n");
    } else {
        printf("[-] Invalid key. Terminating.\n");
    }
    return 0;
}
