#!/usr/bin/env python3
import argparse
import os
import sys
import threading
import time

from scapy.all import *
from scapy.all import IP, TCP, UDP, Ether, RandMAC, Raw


class Receiver(threading.Thread):
    def __init__(self, iface, proto='udp', count_bytes=False, log_file=None):
        threading.Thread.__init__(self)
        self.daemon = True
        self.iface = iface
        self.proto = proto.lower()
        self.count_bytes = count_bytes
        self.byte_count = 0
        self.packet_count = 0
        self.running = True
        self.log_file = log_file
        self.log_fh = None
        if self.count_bytes and self.log_file:
            if not os.path.exists(self.log_file):
                with open(self.log_file, 'w') as f:
                    f.write('timestamp,byte_count\n')

    def received(self, p):
        if self.proto == 'udp' and p.haslayer(UDP):
            self.packet_count += 1
            if self.count_bytes:
                self.byte_count += len(p)
                if self.log_fh:
                    self.log_fh.write(f"{time.time()},{self.byte_count}\n")
                    self.log_fh.flush()
        elif self.proto == 'tcp' and p.haslayer(TCP):
            self.packet_count += 1
            if self.count_bytes:
                self.byte_count += len(p)
                if self.log_fh:
                    self.log_fh.write(f"{time.time()},{self.byte_count}\n")
                    self.log_fh.flush()

    def run(self):
        if self.count_bytes and self.log_file:
            self.log_fh = open(self.log_file, 'a')
        try:
            sniff(iface=self.iface, prn=lambda x: self.received(x), stop_filter=lambda x: not self.running)
        except KeyboardInterrupt:
            self.running = False
        if self.log_fh:
            self.log_fh.close()
            self.log_fh = None

    def stop(self):
        self.running = False

class Sender(threading.Thread):
    def __init__(self, iface, dst_mac, dst_ip, proto='udp', dport=12345, src_ip=None, threads=1):
        threading.Thread.__init__(self)
        self.daemon = True
        self.iface = iface
        self.dst_mac = dst_mac
        self.dst_ip = dst_ip
        self.proto = proto.lower()
        self.dport = dport
        self.running = True
        self.src_ip = src_ip
        self.threads = threads
        self.workers = []

    def send_worker(self):
        ether_ip_layer = Ether(src=RandMAC(), dst=self.dst_mac) / IP(dst=self.dst_ip, src=self.src_ip)
        if self.proto == 'udp':
            payload = b'A' * 1312 #Make the frames the same size
            pkt = ether_ip_layer / UDP(dport=self.dport) / Raw(load=payload)
        else:
            payload = b'A' * 1300
            pkt = ether_ip_layer / TCP(dport=self.dport) / Raw(load=payload)
        try:
            while self.running:
                sendpfast(pkt, mbps=100, loop=1000, iface=self.iface)
        except KeyboardInterrupt:
            self.running = False

    def run(self):
        for i in range(self.threads):
            t = threading.Thread(target=self.send_worker)
            t.daemon = True
            t.start()
            self.workers.append(t)
        for t in self.workers:
            t.join()

    def stop(self):
        self.running = False

def main():
    parser = argparse.ArgumentParser(description='Scapy-based Mininet traffic tool (multi-threaded)')
    parser.add_argument('--mode', choices=['send', 'receive'], required=True)
    parser.add_argument('--iface', required=True, help='Interface to use')
    parser.add_argument('--proto', choices=['udp', 'tcp'], default='udp')
    parser.add_argument('--dst_mac', default='ff:ff:ff:ff:ff:ff', help='Destination MAC (send only)')
    parser.add_argument('--dst_ip', help='Destination IP (send only)')
    parser.add_argument('--src_ip', help='Source IP (send only)')
    parser.add_argument('--dport', type=int, default=12345, help='Destination port (send only)')
    parser.add_argument('--count_bytes', action='store_true', help='Count bytes received (receive only)')
    parser.add_argument('--log_file', help='File to log received data rate (receive only)')
    parser.add_argument('--threads', type=int, default=1, help='Number of sending threads (send only)')
    args = parser.parse_args()

    if args.mode == 'receive':
        receiver = Receiver(args.iface, proto=args.proto, count_bytes=args.count_bytes, log_file=args.log_file)
        receiver.start()
        print(f"Started receiver on {args.iface} for {args.proto.upper()} packets.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            receiver.stop()
            print(f"\nTotal packets: {receiver.packet_count}")
            if args.count_bytes:
                print(f"Total bytes: {receiver.byte_count}")
    else:
        if not args.dst_ip:
            print('Destination IP required for send mode.')
            sys.exit(1)
        sender = Sender(args.iface, args.dst_mac, args.dst_ip, proto=args.proto, dport=args.dport, src_ip=args.src_ip, threads=args.threads)
        sender.start()
        print(f"Started sender on {args.iface} to {args.dst_ip} ({args.proto.upper()}) with {args.threads} threads")
        try:
            while sender.is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            sender.stop()
            print("\nSender stopped.")

if __name__ == '__main__':
    main()
