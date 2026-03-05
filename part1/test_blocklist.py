import socket
import json

data = {
    'server_ip': '10.0.0.1',  # This is in the blocklist
    'server_port': 7000,
    'message': 'Ping'
}

print('----------------------------')
print('Sent to Proxy:')
print('----------------------------')
print(f'data = {{')
print(f'  "server_ip": "{data["server_ip"]}"')
print(f'  "server_port": {data["server_port"]}')
print(f'  "message": "{data["message"]}"')
print(f'}}')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(('127.0.0.1', 8000))
    s.sendall(json.dumps(data).encode())
    response = s.recv(1024).decode()

print('----------------------------')
print('Received from Proxy:')
print('----------------------------')
print(f'"{response}"')
