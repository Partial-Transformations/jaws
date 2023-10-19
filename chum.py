from rich.progress import Progress
import socket
import ssl
import random
import time

# Listen on all available interfaces
HOST = 'ADDR'
# Port to listen on
PORT = 443
# Size of each chunk to send. This is the number of bytes to send at a time.
CHUNK_SIZE = 4096

# Function to generate random data. This will be used to simulate a file transfer.
def generate_random_data(size):
    return bytes([random.randint(0, 255) for _ in range(size)])

def main():
    # Get file size from user.
    mock_file_size_MB = float(input("Enter the file size in MB: "))
    MOCK_FILE_SIZE = int(mock_file_size_MB * 1024 * 1024)

    # Calculate the total number of chunks to send.
    total_chunks = MOCK_FILE_SIZE // CHUNK_SIZE
    if MOCK_FILE_SIZE % CHUNK_SIZE:
        total_chunks += 1

    # Create a socket object. SOCK_STREAM means it will be a TCP socket.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        print(f"Connecting to {HOST}:{PORT}...")
        sock.connect((HOST, PORT))

        # Upgrade to TLS. This will fail if the server does not support TLS.
        context = ssl._create_unverified_context()
        
        # Perform SSL handshake. This will block until the handshake is complete.
        with context.wrap_socket(sock, server_hostname=HOST) as ssock:
            print(f"Connected to {HOST}:{PORT} over TLS")
            
            # Send file size to server.
            with Progress() as progress:
                task = progress.add_task("[cyan]Transferring...", total=total_chunks)
                
                for i in range(total_chunks):
                    chunk_size = CHUNK_SIZE if (i < total_chunks - 1) else (MOCK_FILE_SIZE % CHUNK_SIZE)
                    data = generate_random_data(chunk_size)
                    ssock.sendall(data)
                    progress.update(task, completed=i+1)

                    # Introduce a random delay to simulate variable transmission rate
                    #random_delay = random.uniform(0.05, 0.5)  # Random delay between 0.05 and 0.5 seconds
                    random_delay = random.uniform(0.01, 0.1)  # Random delay between 0.01 and 0.1 seconds
                    time.sleep(random_delay)
            
            # Close the connection.
            print("File transfer simulation complete.")

if __name__ == "__main__":
    while True:
        main()
        repeat = input("Would you like to run again? (y/n): ")
        if repeat.lower() != 'y':
            break
