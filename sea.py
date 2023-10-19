import pyshark
import pandas as pd
from rich.console import Console

# Initialize rich console
console = Console()
# Variable for batch size. This is the number of packets to save to the file at a time.
batch_size = 100
# Initialize dataframe. This will be used to store packets in batches.
df = pd.DataFrame(columns=['packet_id', 'type', 'size', 'src_ip', 'dst_ip', 'src_port', 'dst_port', 'timestamp'])
packet_id = 0  # Initialize packet ID

# Function to process packets. This will be called for each packet captured.
def process_packet(packet):
    global df, packet_id

    # Create a dictionary with packet information. This will be used to create a dataframe.
    packet_info = {
        "packet_id": packet_id, # Incremented below
        "type": packet.highest_layer, # Highest layer of the OSI model that the packet was captured at
        "size": len(packet), # Size of the packet in bytes
        "src_ip": packet.ip.src if 'IP' in packet else 'N/A', # Source IP address
        "dst_ip": packet.ip.dst if 'IP' in packet else 'N/A', # Destination IP address
        "src_port": packet[packet.transport_layer].srcport if hasattr(packet, 'transport_layer') and packet.transport_layer else 'N/A', # Source port
        "dst_port": packet[packet.transport_layer].dstport if hasattr(packet, 'transport_layer') and packet.transport_layer else 'N/A', # Destination port
        "timestamp": float(packet.sniff_time.timestamp()) * 1000  # Convert to Unix timestamp in milliseconds. This is the time the packet was captured.
    }

    # Print packet information to console. Color the packet red if it was sent to the server, yellow otherwise.
    if packet_info['dst_ip'] == 'ADDR':
        console.print(f"[red]Captured packet: {packet_info}[/red]")
    else:
        console.print(f"[yellow]Captured packet: {packet_info}[/yellow]")

    # Add packet information to dataframe. This will be saved to a file later.
    new_row = pd.Series(packet_info, name='x')
    df = pd.concat([df, pd.DataFrame(new_row).T], ignore_index=True)

    # If the dataframe has reached the batch size, save it to a file.
    if len(df) >= batch_size:
        try:
            existing_data = pd.read_json('packets.json', orient='records')
        except (FileNotFoundError, pd.errors.EmptyDataError):
            existing_data = pd.DataFrame(columns=['packet_id', 'type', 'size', 'src_ip', 'dst_ip', 'src_port', 'dst_port', 'timestamp'])

        # Combine existing data with new data and save to file.
        combined_data = pd.concat([existing_data, df], ignore_index=True)
        # Save to file
        combined_data.to_json('packets.json', orient='records')
        # Print message to console
        console.print(f"[green]Saved {batch_size} packets to stable file.[/green]")

        # Clear dataframe
        df = pd.DataFrame(columns=['packet_id', 'type', 'size', 'src_ip', 'dst_ip', 'src_port', 'dst_port', 'timestamp'])
    
    packet_id += 1  # Increment packet ID

if __name__ == "__main__":
    capture = pyshark.LiveCapture(interface='Ethernet')
    capture.apply_on_packets(process_packet)
