import pyshark
from rich.console import Console
import pandas as pd

console = Console()

batch_size = 100
df = pd.DataFrame(columns=['packet_id', 'type', 'size', 'src_ip', 'dst_ip', 'timestamp'])
packet_id = 0  # Initialize packet ID

def process_packet(packet):
    global df, packet_id

    packet_info = {
        "packet_id": packet_id,
        "type": packet.highest_layer,
        "size": len(packet),
        "src_ip": packet.ip.src if 'IP' in packet else 'N/A',
        "dst_ip": packet.ip.dst if 'IP' in packet else 'N/A',
        "timestamp": packet.sniff_time.isoformat()  # Add timestamp
    }

    if packet_info['dst_ip'] == 'IP ADDR HERE':
        console.print(f"[red]Captured packet: {packet_info}[/red]")
    else:
        console.print(f"[yellow]Captured packet: {packet_info}[/yellow]")

    new_row = pd.Series(packet_info, name='x')
    df = pd.concat([df, pd.DataFrame(new_row).T], ignore_index=True)

    if len(df) >= batch_size:
        try:
            existing_data = pd.read_json('packets.json', orient='records')
        except (FileNotFoundError, pd.errors.EmptyDataError):
            existing_data = pd.DataFrame(columns=['packet_id', 'type', 'size', 'src_ip', 'dst_ip', 'timestamp'])

        combined_data = pd.concat([existing_data, df], ignore_index=True)
        combined_data.to_json('packets.json', orient='records')
        console.print(f"[green]Saved {batch_size} packets to stable file.[/green]")

        df = pd.DataFrame(columns=['packet_id', 'type', 'size', 'src_ip', 'dst_ip', 'timestamp'])

    packet_id += 1  # Increment packet ID

if __name__ == "__main__":
    capture = pyshark.LiveCapture(interface='Ethernet')
    capture.apply_on_packets(process_packet)
