import pandas as pd
import matplotlib.pyplot as plt
import openai
from datetime import datetime

openai.api_key = "KEY"

def get_ip_info_from_gpt(ip_address):
    combined_prompt = f"Provide information about IP address {ip_address}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are looking up IP addresses that show up as anomalies on our network, we would like you to return as much of the requested information as possible. "},
            {"role": "user", "content": f"Provide information about IP address {ip_address}, returning ISP, Services, Country, State/Region, City, and Latitude/Longitude."}
        ],
        max_tokens=500
    )
    ip_info = response.choices[0]['message']['content']
    return ip_info

def filter_and_plot(dst_ip):
    try:
        df = pd.read_json('packets.json', orient='records')
    except (FileNotFoundError, pd.errors.EmptyDataError):
        print("[error] Failed to load packets.json or the file is empty.")
        return

    # Convert timestamps to datetime objects
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    # Filter packets by dst_ip
    filtered_df = df[df['dst_ip'] == dst_ip]

    if filtered_df.empty:
        print(f"[info] No packets found with destination IP: {dst_ip}")
        return

    # Get and display IP information
    ip_info = get_ip_info_from_gpt(dst_ip)
    print("\nInformation about the IP address:")
    print(ip_info)

    # Time Series Visualization
    plt.figure(figsize=(14, 4))

    plt.plot_date(filtered_df['timestamp'], filtered_df['size'], linestyle='solid')

    plt.title(f"Packet Size over Time for dst_ip = {dst_ip}")
    plt.xlabel('Timestamp')
    plt.ylabel('Packet Size (bytes)')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    dst_ip_to_filter = input("Enter the dst_ip you'd like to visualize: ")
    filter_and_plot(dst_ip_to_filter)
