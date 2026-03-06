# ECS 152A Project 2: Proxy Server & DNS Client

This project implements two networking applications from scratch using Python sockets.

---

## Part 1: Proxy Server (Ping-Pong Project)

### Overview
A TCP-based proxy server that forwards client requests to a backend server. Implements:
- **Ping-Pong**: Client sends "Ping" → Server responds "Pong" (and vice versa)
- **String Reversal**: Any other 4-character string gets reversed
- **IP Blocklist**: Blocked IPs receive "Blocklist Error" instead of forwarding

### Files
- `client_Stephen_Hu_Jiahuan_Yao.py` - Client (sends requests)
- `proxy_server_Stephen_Hu_Jiahuan_Yao.py` - Proxy (forwards requests while enforcing blocklist)
- `server_Stephen_Hu_Jiahuan_Yao.py` - Backend server (processes requests)

### How to Run

You need **3 separate PowerShell terminals**:

**Terminal 1 - Start the Server:**
```powershell
cd c:\Users\steph\Downloads\ecs152hw2\part1
python server_Stephen_Hu_Jiahuan_Yao.py
```
Expected: `Server listening on 127.0.0.1:7000`

**Terminal 2 - Start the Proxy:**
```powershell
cd c:\Users\steph\Downloads\ecs152hw2\part1
python proxy_server_Stephen_Hu_Jiahuan_Yao.py
```
Expected: `Proxy listening on 127.0.0.1:8000`

**Terminal 3 - Run Client Tests:**
```powershell
cd c:\Users\steph\Downloads\ecs152hw2\part1

# Test Ping → Pong
python client_Stephen_Hu_Jiahuan_Yao.py Ping

# Test Pong → Ping
python client_Stephen_Hu_Jiahuan_Yao.py Pong

# Test String Reversal
python client_Stephen_Hu_Jiahuan_Yao.py Test

# Test Another Reversal
python client_Stephen_Hu_Jiahuan_Yao.py Help
```

### Expected Output

Each client request will print:
1. **Client View**: JSON data sent to proxy
2. **Proxy View**: Data received from client, forwarded to server, and response from server
3. **Server View**: Data received and response sent

For `Ping` test:
- Client sends: `{"server_ip": "127.0.0.1", "server_port": 7000, "message": "Ping"}`
- Proxy forwards: `"Ping"`
- Server responds: `"Pong"`
- Client receives: `"Pong"`

### Testing Blocklist

Blocked IPs in the proxy:
- `10.0.0.1`
- `192.168.1.100`
- `172.16.0.5`
- `203.0.113.42`
- `198.51.100.7`

To test blocklist, temporarily modify `client_Stephen_Hu_Jiahuan_Yao.py`:
```python
SERVER_IP = '10.0.0.1'  # Change from '127.0.0.1'
```
Then run:
```powershell
python client_Stephen_Hu_Jiahuan_Yao.py Ping
```
Expected response: `"Blocklist Error"`

**Remember to change it back to `127.0.0.1` after testing!**

---

## Part 2: DNS Client

### Overview
A DNS resolver built from scratch that queries public DNS servers to resolve domain names. It:
1. Constructs raw DNS packets manually
2. Sends queries to root nameservers
3. Follows the referral chain: Root → TLD → Authoritative → Answer
4. Extracts resolved IP addresses
5. Makes HTTP requests to the resolved IPs
6. Measures RTT (Round Trip Time) at each hop

### Files
- `DNS_client_Stephen_Hu_Jiahuan_Yao.py` - DNS resolver

### How to Run

Single command (takes 15-30 seconds):
```powershell
cd c:\Users\steph\Downloads\ecs152hw2\part2

# Resolve wikipedia.org
python DNS_client_Stephen_Hu_Jiahuan_Yao.py wikipedia.org

# Resolve example.com
python DNS_client_Stephen_Hu_Jiahuan_Yao.py example.com

# Resolve google.com
python DNS_client_Stephen_Hu_Jiahuan_Yao.py google.com
```

### Expected Output

For `wikipedia.org`:
```
--------------------------------------------
Querying 198.41.0.4 for wikipedia.org
--------------------------------------------
NS : a2.org.afilias-nst.info
[...more NS records...]
A : 199.249.112.1
[...glue records...]
RTT: XX.XX ms

--------------------------------------------
Querying 199.249.112.1 for wikipedia.org
--------------------------------------------
NS : ns0.wikimedia.org
[...more NS records...]
RTT: XX.XX ms

--------------------------------------------
Querying 208.80.154.238 for wikipedia.org
--------------------------------------------
A : 198.35.26.96
RTT: XX.XX ms

Resolved wikipedia.org -> 198.35.26.96

--------------------------------------------
Making HTTP request to 198.35.26.96
--------------------------------------------
HTTP/1.1 301 Moved Permanently
RTT: XX.XX ms
```

### Referral Chain Explanation

The DNS resolution follows 3 hops:
1. **Root Nameserver** (198.41.0.4) → Returns NS records for .org TLD
2. **TLD Nameserver** (one of .org servers) → Returns NS records for wikipedia.org's authoritative server
3. **Authoritative Nameserver** → Returns the final IP address (A record)
4. **HTTP Request** → Connects to the resolved IP

---

## Port Configuration

- **Server**: Port 7000 (localhost)
- **Proxy**: Port 8000 (localhost)
- **DNS**: Port 53 (standard, UDP)

These can be modified in the respective files if needed, but ensure consistency across all three for Part 1.