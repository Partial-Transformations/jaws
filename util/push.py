import os
import datetime
from paramiko import SSHClient, AutoAddPolicy
from rich.console import Console
from rich.traceback import install

# A utiltiy to push the packets.csv file to a EC2 instance (or other remote) for later download. This is useful if you are running this on a temporary end-point or edge network.

install()
console = Console()
file_path_relative = "./packets.json"
ec2_ip = "AWS DNS IP ADDR" # Replace with your EC2 instance's IP address
ec2_username = "ec2-user" # Replace with your EC2 instance's username
ec2_key_path_relative = "./key.pem" # Replace with the path to your EC2 key

file_path = os.path.abspath(file_path_relative)
ec2_key_path = os.path.abspath(ec2_key_path_relative)

def transfer_file_to_ec2(file_path, ec2_ip, ec2_username, ec2_key_path):
    try:
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(ec2_ip, username=ec2_username, key_filename=ec2_key_path)

        current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        file_name, file_extension = os.path.splitext(os.path.basename(file_path))
        remote_file_name = f"{file_name}_{current_time}{file_extension}"

        remote_path = f"/home/ec2-user/packet_captures/{remote_file_name}"

        with console.status("[bold green]Transferring the file..."):
            ftp_client = ssh.open_sftp()
            ftp_client.put(file_path, remote_path)
            ftp_client.close()

        console.log(f"[bold green]Successfully transferred {file_path} to {remote_path} on {ec2_ip}")

    except Exception as e:
        console.log(f"[bold red]An error occurred: {e}")

if __name__ == "__main__":
    # Check if the file exists
    if not os.path.exists(file_path):
        console.log("[bold red]The specified file doesn't exist. Exiting.")
    else:
        transfer_file_to_ec2(file_path, ec2_ip, ec2_username, ec2_key_path)
