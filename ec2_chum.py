from rich.progress import Progress
import socket
import ssl
import random
import time

# Configuration variables
HOST = 'IP ADDR HERE'  # Replace with your EC2 instance's public IP
PORT = 443  # Port to connect to
CHUNK_SIZE = 4096  # Typical size for a chunk of file data
MOCK_FILE_SIZE = 5242880  # Mock file size in bytes
INTERVAL = 30  # Time in seconds to wait before running the script again

def generate_random_data(size):
    return bytes([random.randint(0, 255) for _ in range(size)])

def main():
    # Calculate how many chunks need to be sent
    total_chunks = MOCK_FILE_SIZE // CHUNK_SIZE
    if MOCK_FILE_SIZE % CHUNK_SIZE:
        total_chunks += 1  # Account for the last smaller chunk

    # Create a socket object
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        print(f"Connecting to {HOST}:{PORT}...")
        sock.connect((HOST, PORT))

        # Create an unverified SSL context
        context = ssl._create_unverified_context()
        
        # Upgrade socket to SSL/TLS
        with context.wrap_socket(sock, server_hostname=HOST) as ssock:
            print(f"Connected to {HOST}:{PORT} over TLS")
            
            with Progress() as progress:
                file_transfer_task = progress.add_task("[cyan]Transferring...", total=total_chunks)
                
                for i in range(total_chunks):
                    chunk_size = CHUNK_SIZE if (i < total_chunks - 1) else (MOCK_FILE_SIZE % CHUNK_SIZE)
                    data = generate_random_data(chunk_size)
                    ssock.sendall(data)
                    progress.update(file_transfer_task, completed=i+1)
            
            print("File transfer simulation complete.")
        
        print(f"Waiting {INTERVAL} seconds to run again...")
        
        with Progress() as progress:
            countdown_task = progress.add_task("[magenta]Counting down...", total=INTERVAL)
            
            for i in range(INTERVAL):
                time.sleep(1)
                progress.update(countdown_task, completed=i+1)

if __name__ == "__main__":
    while True:
        main()
