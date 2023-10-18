import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from time import sleep
from rich.console import Console
from rich.progress import Progress
from scipy.spatial import distance
import numpy as np
import json
import random

# Increase this value based on your preference
N_ANOMALIES_TO_DISPLAY = 20  

# Function to generate random color
def generate_random_color():
    return "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# Function to determine the optimal number of clusters
def get_optimal_clusters(X):
    distortions = []
    K = range(1, 10)
    for k in K:
        kmeanModel = KMeans(n_clusters=k, n_init=10)
        kmeanModel.fit(X)
        distortions.append(kmeanModel.inertia_)
    
    if not distortions:
        return 1

    elbow_point = np.argmin(np.gradient(np.gradient(distortions))) + 1
    return elbow_point

# Initialize console and progress bar
console = Console()
progress = Progress(console=console)

# Initialize figure with reduced dimensions
fig, ax1 = plt.subplots(1, 1, figsize=(14, 12))

# Set up 3D scatter plot
ax1 = fig.add_subplot(111, projection="3d")
plt.tight_layout()
plt.show(block=False)

with progress:
    task_id = progress.add_task("[cyan]Processing next update, refreshing in...", total=30)
    while True:
        try:
            df = pd.read_json('packets.json', orient='records')
            df['type_code'] = df['type'].astype('category').cat.codes
            df['dst_ip_code'] = df['dst_ip'].astype('category').cat.codes
            X = df[['type_code', 'size', 'dst_ip_code']].to_numpy()
            
            scaler = StandardScaler()
            X_normalized = scaler.fit_transform(X)
            
            n_clusters = get_optimal_clusters(X_normalized)
            
            ax1.clear()
            
            kmeans = KMeans(n_clusters=n_clusters, n_init=10)
            kmeans.fit(X_normalized)
            centroids = kmeans.cluster_centers_
            labels = kmeans.labels_
            
            for i in range(n_clusters):
                color = generate_random_color()
                points_in_cluster = np.array([X[j] for j in range(len(X)) if labels[j] == i])
                ax1.scatter(points_in_cluster[:, 0], points_in_cluster[:, 1], points_in_cluster[:, 2], c=color, s=points_in_cluster[:, 1]/50)
            
            for i, centroid in enumerate(centroids):
                color = generate_random_color()
                ax1.scatter(centroid[0], centroid[1], centroid[2], marker='o', s=300, linewidths=3, color=color, zorder=10)
            
            distances = [distance.euclidean(X_normalized[i], centroids[labels[i]]) for i in range(len(X_normalized))]
            df['distance_to_center'] = distances
            anomalies = df.nlargest(N_ANOMALIES_TO_DISPLAY, 'distance_to_center')

            console.print(f"[yellow]Top {N_ANOMALIES_TO_DISPLAY} Anomaly Packets:[/yellow]\n{anomalies}")

            for i, row in anomalies.iterrows():
                ax1.scatter(row['type_code'], row['size'], row['dst_ip_code'], c='orange', s=row['size']/50)
                ax1.text(row['type_code'], row['size'], row['dst_ip_code'], f"{row['dst_ip']} ({row['type']}, {row['size']} bytes)", color='black')

            ax1.set_ylabel('Packet Size')
            plt.draw()
            ax1.view_init(elev=50, azim=ax1.azim + 90)
            plt.pause(0.01)

            console.print(f"[green]Updated 3D plot with {len(df)} packets.[/green]")
            progress.update(task_id, completed=30)
            sleep(1)

            progress.reset(task_id)
            for i in range(30):
                sleep(1)
                progress.update(task_id, advance=1)
        except json.JSONDecodeError:
            console.print("[red]An error occurred while reading the JSON file. Retrying...[/red]")
            sleep(1)
        except Exception as e:
            console.print(f"[red]An unexpected error occurred: {e}. Retrying...[/red]")
            sleep(1)
