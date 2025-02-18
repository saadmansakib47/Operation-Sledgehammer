import sys
import socket
import threading
import subprocess

# Helper function to execute shell commands
def run_command(command):
    command = command.strip()
    if not command:
        return ""
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        return output.decode()
    except Exception as e:
        return f"Failed to execute command: {str(e)}\n"

# Netcat class
class Netcat:
    def __init__(self, target, port, listen):
        self.target = target
        self.port = port
        self.listen = listen
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        """Connect to a target machine (client mode)"""
        try:
            self.socket.connect((self.target, self.port))
            print(f"[+] Connected to {self.target}:{self.port}")
            while True:
                data = self.socket.recv(4096).decode()
                if not data:
                    break
                print(data, end="")
        except Exception as e:
            print(f"[-] Connection failed: {str(e)}")
        finally:
            self.socket.close()

    def listen(self):
        """Listen for incoming connections (server mode)"""
        self.socket.bind((self.target, self.port))
        self.socket.listen(5)
        print(f"[+] Listening on {self.target}:{self.port}")

        while True:
            client_socket, addr = self.socket.accept()
            print(f"[+] Connection from {addr}")
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_client(self, client_socket):
        """Handle incoming client connection"""
        while True:
            client_socket.send(b"Shell> ")  # Prompt
            cmd_buffer = client_socket.recv(1024).decode()
            if not cmd_buffer:
                break
            response = run_command(cmd_buffer)
            client_socket.send(response.encode())

        client_socket.close()

# Command-line argument parsing
if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python netcat.py -t <target> -p <port> [-l]")
        sys.exit(1)

    target = sys.argv[sys.argv.index("-t") + 1]
    port = int(sys.argv[sys.argv.index("-p") + 1])
    listen = "-l" in sys.argv

    netcat = Netcat(target, port, listen)
    if listen:
        netcat.listen()
    else:
        netcat.connect()
