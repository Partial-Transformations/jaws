import pandas as pd
from sklearn.decomposition import PCA
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv('./data/packets_.csv')
df.drop(['packet_id', 'timestamp', 'dns_domain', 'http_url', 'label'], axis=1, inplace=True)
df = pd.get_dummies(df, columns=['protocol', 'tcp_flags', 'src_ip', 'dst_ip', 'src_port', 'dst_port', 'src_mac', 'dst_mac'], drop_first=True)

sample_rate = 0.1
if sample_rate < 1.0:
    df = df.sample(frac=sample_rate, random_state=42)

scaler = StandardScaler()
df_scaled = scaler.fit_transform(df)
pca = PCA(n_components=2)
principal_components = pca.fit_transform(df_scaled)
eps = 0.3
min_samples = 5
dbscan = DBSCAN(eps=eps, min_samples=min_samples)
clusters = dbscan.fit_predict(principal_components)

fig, ax = plt.subplots(figsize=(12, 12))
fig.canvas.manager.window.wm_geometry("+50+50")
colors = ['#BEBEBE' if x == -1 else plt.cm.ocean(x) for x in clusters]
ax.scatter(principal_components[:, 0], principal_components[:, 1], c=colors, s=50, marker='^', zorder=10)
plt.grid(True, linewidth=0.25, color='#BEBEBE', alpha=0.5, zorder=1)
plt.tight_layout()
plt.show()
