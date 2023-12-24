import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm

csv_files = ['./data/unlabeled.csv']

cmap = plt.get_cmap('ocean')

plt.figure(figsize=(12, 12))
for i, csv_file in enumerate(csv_files):
    df = pd.read_csv(csv_file)
    subset = df[df['label'] == 'norm']
    color = cmap(i / len(csv_files))
    plt.scatter(subset['size'], subset['dst_port'], color=[color], label=f'norm from {csv_file}', alpha=0.3, zorder=1, s=100, marker='^')
    subset = df[df['label'] == 'chum']
    plt.scatter(subset['size'], subset['dst_port'], color='red', label='chum', alpha=0.9, zorder=1, s=100, marker='^')

plt.xlabel('Packet Size')
plt.ylabel('Destination Port')
plt.grid(True, linewidth=0.25, color='#BEBEBE', alpha=0.5, zorder=0)
plt.tight_layout()
plt.show()