import openai
import pandas as pd
import matplotlib.pyplot as plt

openai.api_key = "Open AI API KEY"

def get_ip_info_from_gpt(ip_address):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "For the following IP address, return owner, location, lat, long, purpose, and other public information about it."},
                {"role": "user", "content": f"{ip_address}"}
            ],
            max_tokens=500
        )
        ip_info = response.choices[0]['message']['content']
        return ip_info
    except openai.error.OpenAIError as e:
        print("OpenAI API error: ", e, "\n")
        return None

def filter_and_plot(src_ip, csv_files):
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
        except (FileNotFoundError, pd.errors.EmptyDataError):
            print(f"Failed to load {csv_file} or the file is empty...\n")
            continue

        print("\n", df[df['src_ip'] == src_ip], "\n")
        filtered_df = df[df['src_ip'] == src_ip]

        if filtered_df.empty:
            print(f"No packets found for: {src_ip} in {csv_file}", "\n")
            continue

        ip_info = get_ip_info_from_gpt(src_ip)
        if ip_info is not None:
            print("\nInformation about the IP address:")
            print("\n", ip_info, "\n")

        plt.figure(figsize=(20, 4))
        filtered_df.loc[:, 'timestamp'] = pd.to_datetime(filtered_df['timestamp'], unit='ms')
        plt.plot_date(filtered_df['timestamp'], filtered_df['size'], linestyle='solid')
        plt.title(f"Packet Size over Time for: {src_ip} in {csv_file}", fontsize=8)
        plt.xlabel('Time', fontsize=8)
        plt.ylabel('Packet Size (bytes)', fontsize=8)
        plt.grid(True, linewidth=0.25, color='#BEBEBE', linestyle='-')
        plt.tick_params(axis='both', which='major', labelsize=8)
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    print("\n")
    src_ip_to_filter = input("Enter an ip address to search: ")
    csv_files = ['./packets_base_443.csv', './packets_exfil_443.csv', './packets_exfil_40687.csv']
    filter_and_plot(src_ip_to_filter, csv_files)