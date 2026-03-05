import socket
import json

PROXY_HOST = '127.0.0.1'
PROXY_PORT = 8000

# Sample IP blocklist
IP_BLOCKLIST = [
    "10.0.0.1",
    "192.168.1.100",
    "172.16.0.5",
    "203.0.113.42",
    "198.51.100.7"
]

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as proxy_sock:
        proxy_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        proxy_sock.bind((PROXY_HOST, PROXY_PORT))
        proxy_sock.listen()
        print(f"Proxy listening on {PROXY_HOST}:{PROXY_PORT}")

        while True:
            conn, addr = proxy_sock.accept()
            with conn:
                raw = conn.recv(4096).decode()
                if not raw:
                    continue

                data = json.loads(raw)

                print("----------------------------")
                print("Received from Client:")
                print("----------------------------")
                print('data = {')
                print(f'  "server_ip": "{data["server_ip"]}"')
                print(f'  "server_port": {data["server_port"]}')
                print(f'  "message": "{data["message"]}"')
                print('}')

                server_ip = data["server_ip"]
                server_port = data["server_port"]
                message = data["message"]

                # Check blocklist
                if server_ip in IP_BLOCKLIST:
                    print("----------------------------")
                    print("Blocklist Error: IP is blocked")
                    print("----------------------------")
                    conn.sendall("Blocklist Error".encode())
                    continue

                # Forward to server
                print("----------------------------")
                print("Sent to Server:")
                print("----------------------------")
                print(f'"{message}"')

                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
                    server_sock.connect((server_ip, server_port))
                    server_sock.sendall(message.encode())
                    response = server_sock.recv(1024).decode()

                print("----------------------------")
                print("Received from Server:")
                print("----------------------------")
                print(f'"{response}"')

                print("----------------------------")
                print("Sent to Client:")
                print("----------------------------")
                print(f'"{response}"')

                conn.sendall(response.encode())

if __name__ == "__main__":
    main()
