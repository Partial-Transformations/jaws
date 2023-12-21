import pandas as pd
import matplotlib.pyplot as plt

csv_files = ['./packets_base_443.csv', './packets_exfil_443.csv', './packets_exfil_40687.csv']

plt.figure(figsize=(12, 12))
for i, csv_file in enumerate(csv_files):
    df = pd.read_csv(csv_file)
    subset = df[df['label'] == 'norm']
    color = 'blue' if i == 0 else 'lightblue'
    plt.scatter(subset['size'], subset['dst_port'], c=color, label=f'norm from {csv_file}', alpha=0.5, zorder=1, s=100, marker='^')
    subset = df[df['label'] == 'chum']
    plt.scatter(subset['size'], subset['dst_port'], c='red', label='chum', alpha=0.5, zorder=1, s=100, marker='^')

plt.xlabel('Packet Size')
plt.ylabel('Destination Port')
plt.grid(True, linewidth=0.25, color='#BEBEBE', alpha=0.5, zorder=0)
plt.tight_layout()
plt.show()