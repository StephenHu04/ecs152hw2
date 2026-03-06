import socket   #import for socket
import json     #import for json data format
import sys      #import for system arguments

# Proxy and Server configs
PROXY_HOST = '127.0.0.1'
PROXY_PORT = 8000
SERVER_IP = '127.0.0.1'
SERVER_PORT = 7000

def main():
    # argument check
    if len(sys.argv) < 2:
        print("Use format: python3 client_name1_name2.py <4-character-string-message>")
        sys.exit(1)

    # argument size check
    message = sys.argv[1]
    if len(message) != 4:
        print("Error: Argument must be exactly 4 character string.")
        sys.exit(1)

    data = {
        "server_ip": SERVER_IP,
        "server_port": SERVER_PORT,
        "message": message
    }

    # print script for data being sent to proxy
    print("----------------------------")
    print("Sent to Proxy:")
    print("----------------------------")
    print(f'data = {{')
    print(f'"server_ip": "{data["server_ip"]}"')
    print(f'"server_port": {data["server_port"]}')
    print(f'"message": "{data["message"]}"')
    print(f'}}')

    # send to proxy and receive response
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((PROXY_HOST, PROXY_PORT))
        s.sendall(json.dumps(data).encode())
        response = s.recv(1024).decode()

    # print script for data received from proxy
    print("----------------------------")
    print("Received from Proxy:")
    print("----------------------------")
    print(f'"{response}"')

if __name__ == "__main__":
    main()
