import socket
import threading
import paramiko

# Configuration
ssh_host = "Your VM IP"
ssh_user = "Your Username"
ssh_password = "Your Password"
web_server_host = "127.0.0.1"
web_server_port = 8080
local_port = 9090

# Create SSH client
client = paramiko.SSHClient()

client.load_system_host_keys()

client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    # Connect to the SSH server
    client.connect(hostname=ssh_host, username=ssh_user, password=ssh_password)

    # Set up port forwarding
    transport = client.get_transport()

    # Forwarder function
    def forward(local_socket, remote_host, remote_port):
        remote_socket = transport.open_channel("direct-tcpip", (remote_host, remote_port), local_socket.getpeername())
        while True:
            try:
                data = local_socket.recv(1024)
                if len(data) == 0:
                    break
                remote_socket.send(data)
            except Exception:
                break
        local_socket.close()
        remote_socket.close()

    # Listen on the local port
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", local_port))
    server.listen(5)

    print(f"Tunnel established: http://127.0.0.1:{local_port}")

    while True:
        print('atiq')
        local_socket, _ = server.accept()
        print(local_socket)
        threading.Thread(target=forward, args=(local_socket, web_server_host, web_server_port)).start()

except Exception as e:
    print(f"Failed to establish SSH tunnel: {e}")

finally:
    client.close()
