#include <windows.h>
#include <stdio.h>

int main() {
    HANDLE hPipe;
    char buffer[1024];
    DWORD dwRead;

    // Cream "tunelul" (Named Pipe)
    hPipe = CreateNamedPipe(
        "\\\\.\\pipe\\Lab5Pipe",
        PIPE_ACCESS_INBOUND,
        PIPE_TYPE_BYTE | PIPE_READMODE_BYTE | PIPE_WAIT,
        1, 1024, 1024, 0, NULL);

    if (hPipe == INVALID_HANDLE_VALUE) {
        printf("Eroare la crearea pipe-ului: %d\n", GetLastError());
        return 1;
    }

    printf("Programul C asteapta date din Python...\n");
    ConnectNamedPipe(hPipe, NULL);

    if (ReadFile(hPipe, buffer, sizeof(buffer) - 1, &dwRead, NULL)) {
        buffer[dwRead] = '\0';
        printf("Am primit HTML-ul!\nRezultat:\n%s\n", buffer);
        
        // Salvam in fisierul de iesire
        FILE *f = fopen("output.html", "w");
        if (f) {
            fprintf(f, "%s", buffer);
            fclose(f);
            printf("Validat si scris in output.html\n");
        }
    }

    CloseHandle(hPipe);
    return 0;
}