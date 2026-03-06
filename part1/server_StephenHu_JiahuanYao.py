import socket   # import for socket

#server config
HOST = '127.0.0.1'
PORT = 7000

# response logic for server (Ping->Pong, Pong->Ping, else reverse string)
def calculate_response(message):
    if message == "Ping":
        return "Pong"
    elif message == "Pong":
        return "Ping"
    else:
        return message[::-1]

def main():
    # set up server socket, port, and listen for connections
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")

        #loop to accept connections and handle requests
        while True:
            conn, addr = s.accept()
            with conn:
                data = conn.recv(1024).decode()
                if not data:
                    continue

                # print script for data received from proxy
                print("----------------------------")
                print("Received from Proxy:")
                print("----------------------------")
                print(f'"{data}"')

                # call response logic
                response = calculate_response(data)

                # print script for data being sent to proxy
                print("----------------------------")
                print("Sent to Proxy:")
                print("----------------------------")
                print(f'"{response}"')

                # send response back to proxy
                conn.sendall(response.encode())

if __name__ == "__main__":
    main()
