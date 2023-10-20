import os
import datetime
from paramiko import SSHClient, AutoAddPolicy
from rich.console import Console
from rich.traceback import install

# Install rich traceback for better error display
install()

# Initialize the rich console
console = Console()

# Set your variables here
file_path_relative = "./packets.json"
ec2_ip = "ADDR"
ec2_username = "ec2-user" # ec2-user is common...
ec2_key_path_relative = "./KEY.pem"

# Convert relative paths to absolute paths
file_path = os.path.abspath(file_path_relative)
ec2_key_path = os.path.abspath(ec2_key_path_relative)

def transfer_file_to_ec2(file_path, ec2_ip, ec2_username, ec2_key_path):
    try:
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(ec2_ip, username=ec2_username, key_filename=ec2_key_path)

        # Generate the current date and time to append to the filename
        current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        file_name, file_extension = os.path.splitext(os.path.basename(file_path))
        remote_file_name = f"{file_name}_{current_time}{file_extension}"

        # Assuming /tmp as the destination directory
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
