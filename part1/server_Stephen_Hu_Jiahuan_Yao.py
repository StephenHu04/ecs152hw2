import socket
import sys

HOST = '127.0.0.1'
PORT = 7000

def calculate_response(message):
    if message == "Ping":
        return "Pong"
    elif message == "Pong":
        return "Ping"
    else:
        return message[::-1]

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            with conn:
                data = conn.recv(1024).decode()
                if not data:
                    continue

                print("----------------------------")
                print("Received from Proxy:")
                print("----------------------------")
                print(f'"{data}"')

                response = calculate_response(data)

                print("----------------------------")
                print("Sent to Proxy:")
                print("----------------------------")
                print(f'"{response}"')

                conn.sendall(response.encode())

if __name__ == "__main__":
    main()
