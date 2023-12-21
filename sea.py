import pyshark
import pandas as pd
from rich.console import Console
import os

console = Console()
batch_size = 100
#ip_blacklist = ['IP ADDR']
chum_addr = 'IP ADDR'
df = pd.DataFrame(columns=['packet_id', 'type', 'size', 'src_ip', 'dst_ip', 'src_port', 'dst_port', 'timestamp'])

if os.path.exists('packets.csv'):
    existing_data = pd.read_csv('packets.csv')
    if not existing_data.empty:
        packet_id = existing_data['packet_id'].max() + 1
    else:
        packet_id = 0
else:
    packet_id = 0

def process_packet(packet):
    global df, packet_id
    packet_info = {
        "packet_id": packet_id,
        "type": packet.highest_layer,
        "size": len(packet),
        "src_ip": '0.0.0.0',
        "dst_ip": '0.0.0.0',
        "src_port": 0,
        "dst_port": 0,
        "timestamp": float(packet.sniff_time.timestamp()) * 1000,
        "label": 'norm'
    }

    if 'IP' in packet:
        packet_info["src_ip"] = packet.ip.src
        packet_info["dst_ip"] = packet.ip.dst
        packet_info["src_port"] = int(packet[packet.transport_layer].srcport) if hasattr(packet, 'transport_layer') and packet.transport_layer and packet[packet.transport_layer].srcport.isdigit() else 0
        packet_info["dst_port"] = int(packet[packet.transport_layer].dstport) if hasattr(packet, 'transport_layer') and packet.transport_layer and packet[packet.transport_layer].dstport.isdigit() else 0
        packet_info["label"] = 'chum' if packet.ip.dst == chum_addr else 'norm'

    #if packet_info['src_ip'] in ip_blacklist:
       #return

    if packet_info['dst_ip'] == chum_addr:
        console.print(f"[red1]CHUM PACKET >>> ID:{packet_info['packet_id']} TYPE:{packet_info['type']} SIZE:{packet_info['size']} SRC:{packet_info['src_ip']} DST:{packet_info['dst_ip']} SRC PORT:{packet_info['src_port']} DST PORT:{packet_info['dst_port']} TIMESTAMP:{packet_info['timestamp']}[/red1]")
    else:
        console.print(f"[deep_sky_blue3]REAL PACKET >>> ID:[deep_sky_blue1]{packet_info['packet_id']}[/deep_sky_blue1] TYPE:[cyan1]{packet_info['type']}[/cyan1] SIZE:[cyan1]{packet_info['size']}[/cyan1] SRC:[white]{packet_info['src_ip']}[/white] DST:[white]{packet_info['dst_ip']}[/white] SRC PORT:[cyan1]{packet_info['src_port']}[/cyan1] DST PORT:[cyan1]{packet_info['dst_port']}[/cyan1] TIMESTAMP:[deep_sky_blue1]{packet_info['timestamp']}[/deep_sky_blue1][/deep_sky_blue3]")

    new_row = pd.Series(packet_info, name='x')
    df = pd.concat([df, pd.DataFrame(new_row).T], ignore_index=True)

    if len(df) >= batch_size:
        try:
            existing_data = pd.read_csv('packets.csv')
        except (FileNotFoundError, pd.errors.EmptyDataError):
            existing_data = pd.DataFrame(columns=['packet_id', 'type', 'size', 'src_ip', 'dst_ip', 'src_port', 'dst_port', 'timestamp'])

        combined_data = pd.concat([existing_data, df], ignore_index=True)
        combined_data.to_csv('packets.csv', index=False)
        console.print(f"[green]Saved {batch_size} packets to CSV file.[/green]")
        df = pd.DataFrame(columns=['packet_id', 'type', 'size', 'src_ip', 'dst_ip', 'src_port', 'dst_port', 'timestamp'])
    
    packet_id += 1

if __name__ == "__main__":
    print(f"\nBatch size: {batch_size}", end="\n\n")
    #print(f"IP blacklist: {ip_blacklist}", end="\n\n")
    print(df, end="\n\n")
    capture = pyshark.LiveCapture(interface='Ethernet')
    capture.apply_on_packets(process_packet)