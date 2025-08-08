# PocketMine UDP Stresser

A simple tool to send RakNet UDP Unconnected Ping (0x01) packets to PocketMine servers.

Supports:
- Multiple threads
- Packet count or duration limits
- Delay between packets
- Optional SOCKS5 proxy support

**Use only for testing on servers you own or have permission to test.**

## Requirements

- PySocks (`pip install PySocks`)

## Usage

```bash
python udp_spammer.py <ip> [port] [options]
