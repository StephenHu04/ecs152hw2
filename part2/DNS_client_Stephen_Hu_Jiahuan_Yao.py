import socket
import struct
import time
import sys
import random

# Root nameserver IPs (a-root through m-root)
ROOT_SERVERS = [
    "198.41.0.4",      # a.root-servers.net
    "170.247.170.2",   # b.root-servers.net
    "192.33.4.12",     # c.root-servers.net
    "199.7.91.13",     # d.root-servers.net
    "192.203.230.10",  # e.root-servers.net
    "192.5.5.241",     # f.root-servers.net
    "192.112.36.4",    # g.root-servers.net
    "198.97.190.53",   # h.root-servers.net
    "192.36.148.17",   # i.root-servers.net
    "192.58.128.30",   # j.root-servers.net
    "193.0.14.129",    # k.root-servers.net
    "199.7.83.42",     # l.root-servers.net
    "202.12.27.33",    # m.root-servers.net
]

DNS_PORT = 53
TIMEOUT = 10

# DNS record type codes
RECORD_TYPES = {
    1:   "A",
    2:   "NS",
    5:   "CNAME",
    6:   "SOA",
    15:  "MX",
    16:  "TXT",
    28:  "AAAA",
    33:  "SRV",
    255: "ANY",
}


def build_dns_query(domain):
    """Construct a raw DNS query packet for an A record."""
    transaction_id = random.randint(0, 65535)
    flags = 0x0100          # Standard query, recursion desired
    qdcount = 1             # One question
    ancount = arcount = nscount = 0

    header = struct.pack(">HHHHHH",
                         transaction_id, flags,
                         qdcount, ancount, nscount, arcount)

    # Encode domain name as length-prefixed labels
    qname = b""
    for label in domain.split("."):
        encoded = label.encode()
        qname += struct.pack("B", len(encoded)) + encoded
    qname += b"\x00"  # Terminate with null byte

    qtype  = struct.pack(">H", 1)   # A record
    qclass = struct.pack(">H", 1)   # IN (Internet)

    return header + qname + qtype + qclass, transaction_id


def parse_name(data, offset):
    """Parse a (possibly compressed) DNS name from packet data."""
    labels = []
    visited = set()

    while True:
        if offset >= len(data):
            break
        length = data[offset]

        # Pointer compression: top 2 bits are 11
        if (length & 0xC0) == 0xC0:
            if offset + 1 >= len(data):
                break
            pointer = ((length & 0x3F) << 8) | data[offset + 1]
            if pointer in visited:
                break  # Avoid infinite loop
            visited.add(pointer)
            name, _ = parse_name(data, pointer)
            labels.append(name)
            offset += 2
            break
        elif length == 0:
            offset += 1
            break
        else:
            offset += 1
            labels.append(data[offset:offset + length].decode(errors="replace"))
            offset += length

    return ".".join(labels), offset


def parse_dns_response(data):
    """Parse a full DNS response packet. Returns (answer_records, authority_records, additional_records, header_info)."""
    if len(data) < 12:
        return [], [], [], {}

    tid, flags, qdcount, ancount, nscount, arcount = struct.unpack(">HHHHHH", data[:12])
    offset = 12

    # Skip question section
    for _ in range(qdcount):
        _, offset = parse_name(data, offset)
        offset += 4  # qtype + qclass

    answer_records = []
    authority_records = []
    additional_records = []

    def parse_rr_section(count, section_list):
        nonlocal offset
        for _ in range(count):
            name, offset = parse_name(data, offset)
            if offset + 10 > len(data):
                break
            rtype, rclass, ttl, rdlength = struct.unpack(">HHIH", data[offset:offset + 10])
            offset += 10
            rdata = data[offset:offset + rdlength]
            offset += rdlength

            type_name = RECORD_TYPES.get(rtype, f"TYPE{rtype}")
            value = parse_rdata(rtype, rdata, data, offset - rdlength)
            section_list.append((type_name, name, value))

    parse_rr_section(ancount, answer_records)       # Answer
    parse_rr_section(nscount, authority_records)    # Authority
    parse_rr_section(arcount, additional_records)   # Additional

    header_info = {
        "id": tid,
        "flags": flags,
        "ancount": ancount,
        "nscount": nscount,
        "arcount": arcount,
    }
    return answer_records, authority_records, additional_records, header_info


def parse_rdata(rtype, rdata, full_packet, rdata_offset):
    """Decode rdata based on record type."""
    if rtype == 1:  # A
        if len(rdata) == 4:
            return ".".join(str(b) for b in rdata)
    elif rtype == 28:  # AAAA
        if len(rdata) == 16:
            groups = struct.unpack(">8H", rdata)
            return ":".join(f"{g:04x}" for g in groups)
    elif rtype in (2, 5, 12):  # NS, CNAME, PTR
        name, _ = parse_name(full_packet, rdata_offset)
        return name
    elif rtype == 15:  # MX
        pref = struct.unpack(">H", rdata[:2])[0]
        name, _ = parse_name(full_packet, rdata_offset + 2)
        return f"{pref} {name}"
    elif rtype == 6:  # SOA
        name, _ = parse_name(full_packet, rdata_offset)
        return name
    elif rtype == 16:  # TXT
        return rdata[1:].decode(errors="replace")
    return rdata.hex()


def send_dns_query(server_ip, domain):
    """Send a DNS query and return (answer_records, authority_records, additional_records, rtt_ms)."""
    query, _ = build_dns_query(domain)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT)

    try:
        t_start = time.time()
        sock.sendto(query, (server_ip, DNS_PORT))
        response, _ = sock.recvfrom(4096)
        rtt = (time.time() - t_start) * 1000
    finally:
        sock.close()

    answer, authority, additional, _ = parse_dns_response(response)
    return answer, authority, additional, rtt


def resolve(domain):
    """
    Iteratively resolve domain starting from a root server.
    Follows the referral chain: root -> TLD NS -> authoritative NS -> answer.
    """
    current_server = ROOT_SERVERS[0]
    visited_servers = set()

    while True:
        if current_server in visited_servers:
            print(f"Loop detected at {current_server}, stopping.")
            break
        visited_servers.add(current_server)

        print("--------------------------------------------")
        print(f"Querying {current_server} for {domain}")
        print("--------------------------------------------")

        try:
            answer, authority, additional, rtt = send_dns_query(current_server, domain)
        except socket.timeout:
            print(f"Timeout querying {current_server}, trying next root server...")
            # Try next root server
            for rs in ROOT_SERVERS:
                if rs not in visited_servers:
                    current_server = rs
                    break
            else:
                print("All root servers timed out.")
                return None
            continue

        all_records = answer + authority + additional
        if not all_records:
            print("No records received.")
            return None

        # Print all records
        for rtype, name, value in all_records:
            print(f"{rtype} : {value}")

        print(f"RTT: {rtt:.2f} ms")

        # Check for A record in ANSWER section (final answer)
        a_answer = [r for r in answer if r[0] == "A"]
        if a_answer:
            final_ip = a_answer[0][2]
            return final_ip

        # Check for NS referrals in AUTHORITY section
        ns_records = [r for r in authority if r[0] == "NS"]
        ns_names = [r[2] for r in ns_records]

        if not ns_names:
            print("No NS referrals found.")
            return None

        # Build a map: ns_name -> IP from additional (glue) records
        glue_map = {}
        for rtype, name, value in additional:
            if rtype == "A" and name in ns_names:
                glue_map[name] = value

        if glue_map:
            # Use first available glue record
            next_server = next(iter(glue_map.values()))
        elif ns_names:
            # No glue — need to resolve NS name separately
            print(f"No glue record for {ns_names[0]}, resolving NS name...")
            ns_ip = resolve_ns(ns_names[0])
            if ns_ip is None:
                print(f"Could not resolve NS {ns_names[0]}")
                return None
            next_server = ns_ip
        else:
            print("No NS referrals found.")
            return None

        current_server = next_server


def resolve_ns(ns_name):
    """Resolve an NS hostname using the root servers (helper for missing glue)."""
    for root in ROOT_SERVERS:
        try:
            answer, authority, additional, _ = send_dns_query(root, ns_name)
            a_records = [r for r in answer if r[0] == "A"]
            if a_records:
                return a_records[0][2]
        except socket.timeout:
            continue
    return None


def make_http_request(ip, domain):
    """Make a raw HTTP/1.1 GET request to the resolved IP."""
    print("--------------------------------------------")
    print(f"Making HTTP request to {ip}")
    print("--------------------------------------------")

    request = (
        f"GET / HTTP/1.1\r\n"
        f"Host: {domain}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    )

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(TIMEOUT)

    try:
        sock.connect((ip, 80))
        t_start = time.time()
        sock.sendall(request.encode())

        response = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk 
            # Stop after headers to avoid downloading huge body
            if b"\r\n\r\n" in response:
                 break

        rtt = (time.time() - t_start) * 1000
    except Exception as e:
        print(f"HTTP request failed: {e}")
        return
    finally:
        sock.close()

    # Extract status line
    status_line = response.split(b"\r\n")[0].decode(errors="replace")
    print(status_line)
    print(f"RTT: {rtt:.2f} ms")


def main():
    if len(sys.argv) < 2:
        print("Usage: python DNS_client_name1_name2.py <domain>")
        sys.exit(1)

    domain = sys.argv[1]
    resolved_ip = resolve(domain)

    if resolved_ip:
        make_http_request(resolved_ip, domain)
    else:
        print(f"Could not resolve {domain}") 


if __name__ == "__main__":
    main()
