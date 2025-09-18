from scapy.all import rdpcap, TCP, IP
import sys
from collections import defaultdict

def analyze_pcap(pcap_file):
    try:
        packets = rdpcap(pcap_file)
    except Exception as e:
        print(f"Error reading PCAP file: {e}")
        return

    syn_counts = defaultdict(int)
    syn_ack_counts = defaultdict(int)

    for pkt in packets:
        if IP in pkt and TCP in pkt:
            ip_src = pkt[IP].src
            ip_dst = pkt[IP].dst
            tcp_flags = pkt[TCP].flags

            if tcp_flags == 'S':
                syn_counts[ip_src] += 1
            elif tcp_flags == 'SA':
                syn_ack_counts[ip_dst] += 1

    suspicious_ips = []
    for ip in syn_counts:
        syn = syn_counts[ip]
        syn_ack = syn_ack_counts.get(ip, 0)

        if syn >= 3 * syn_ack:
            suspicious_ips.append(ip)

    for ip in sorted(suspicious_ips):
        print(ip)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python syn_scanner.py <pcap_file>")
        sys.exit(1)
    analyze_pcap(sys.argv[1])

