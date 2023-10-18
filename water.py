import pyshark
from rich.console import Console
import pandas as pd

console = Console()
# Number of packets per batch
batch_size = 100  

# Initialize empty DataFrame
df = pd.DataFrame(columns=['type', 'size', 'src_ip', 'dst_ip'])

def process_packet(packet):
    global df

    # Extract required information
    packet_info = {
        "type": packet.highest_layer,
        "size": len(packet),
        "src_ip": packet.ip.src if 'IP' in packet else 'N/A',
        "dst_ip": packet.ip.dst if 'IP' in packet else 'N/A'
    }

    # Check destination IP and color it red if it's IP ADDR HERE
    if packet_info['dst_ip'] == 'IP ADDR HERE':
        console.print(f"[red]Captured packet: {packet_info}[/red]")
    else:
        console.print(f"[yellow]Captured packet: {packet_info}[/yellow]")

    # Append to DataFrame
    new_row = pd.Series(packet_info, name='x')
    df = pd.concat([df, pd.DataFrame(new_row).T], ignore_index=True)

    if len(df) >= batch_size:
        # Read existing data if any
        try:
            existing_data = pd.read_json('packets.json', orient='records')
        except FileNotFoundError:
            existing_data = pd.DataFrame(columns=['type', 'size', 'src_ip', 'dst_ip'])

        # Concatenate new data with existing data
        combined_data = pd.concat([existing_data, df], ignore_index=True)

        # Write directly to the stable JSON file
        combined_data.to_json('packets.json', orient='records')

        console.print(f"[green]Saved {batch_size} packets to stable file.[/green]")

        # Reset DataFrame for new batch
        df = pd.DataFrame(columns=['type', 'size', 'src_ip', 'dst_ip'])

if __name__ == "__main__":
    # Replace 'Ethernet' with your interface
    capture = pyshark.LiveCapture(interface='Ethernet')  
    capture.apply_on_packets(process_packet)
