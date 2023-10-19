import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from time import sleep
from rich.console import Console
from rich.progress import Progress
from rich.table import Table
from scipy.spatial import distance
import numpy as np
import json
import random
from datetime import datetime

# Increase this value based on your preference
N_ANOMALIES_TO_DISPLAY = 20
N_TOP_ANOMALIES = 5
# Key will be some unique identifier for an anomaly, value will be metadata like timestamp
anomaly_history = {}
# Predefined colors for clusters
cluster_colors = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
]

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

# Function to apply PCA
def apply_pca(X_normalized):
    pca = PCA(n_components=2)   # Reducing data to 2 dimensions
    return pca.fit_transform(X_normalized)

# Initialize console and progress bar
console = Console()
progress = Progress(console=console)

# Initialize figure with reduced dimensions
fig, ax1 = plt.subplots(1, 1, figsize=(14, 12))

# Set up 3D scatter plot
# plt.tight_layout()
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
            X_pca = apply_pca(X_normalized)
            
            n_clusters = get_optimal_clusters(X_normalized)
            
            ax1.clear()
            
            kmeans = KMeans(n_clusters=n_clusters, n_init=10)
            kmeans.fit(X_normalized)
            centroids = kmeans.cluster_centers_
            labels = kmeans.labels_
            
            for i in range(n_clusters):
                color = cluster_colors[i % len(cluster_colors)]
                points_in_cluster = np.array([X_pca[j] for j in range(len(X_pca)) if labels[j] == i])
                sizes = [df.iloc[j]['size'] for j in range(len(X_pca)) if labels[j] == i] 
                ax1.scatter(points_in_cluster[:, 0], points_in_cluster[:, 1], c=color, s=np.array(sizes)/50)


            for i, centroid in enumerate(centroids):
                color = cluster_colors[i % len(cluster_colors)]
                ax1.scatter(centroid[0], centroid[1], marker='o', s=300, linewidths=3, color=color, zorder=10)

            
            distances = [distance.euclidean(X_normalized[i], centroids[labels[i]]) for i in range(len(X_normalized))]
            df['distance_to_center'] = distances
            anomalies = df.nlargest(N_ANOMALIES_TO_DISPLAY, 'distance_to_center')

            current_time = datetime.now()

            # Update and decay existing anomalies in the history
            to_remove = []  # List to keep track of keys to remove
            for unique_id, meta in anomaly_history.items():
                time_diff = (current_time - meta['timestamp']).total_seconds()
                if time_diff > 30:  # Change this value based on your decay time
                    to_remove.append(unique_id)  # Mark for removal
                else:
                    meta['status'] = 'Decaying'
                    meta['timestamp'] = current_time  # Update timestamp

            # Remove fully decayed anomalies
            for unique_id in to_remove:
                del anomaly_history[unique_id]

            # Update the anomaly_history dictionary
            for i, row in anomalies.iterrows():
                unique_id = f"{row['dst_ip']}_{row['type']}_{row['size']}"
                if unique_id not in anomaly_history:
                    anomaly_history[unique_id] = {'timestamp': current_time, 'status': 'New'}
                else:
                    time_diff = (current_time - anomaly_history[unique_id]['timestamp']).total_seconds()
                    anomaly_history[unique_id]['status'] = 'New' if time_diff < 30 else 'Decaying'

            # console.print(f"[yellow]Top {N_ANOMALIES_TO_DISPLAY} Anomaly Packets:[/yellow]\n{anomalies}")
            table = Table(title=f"Top {N_ANOMALIES_TO_DISPLAY} Anomaly Packets")

            # Add headers
            table.add_column("Destination IP", style="cyan")
            table.add_column("Type", style="cyan")
            table.add_column("Size", style="cyan")
            table.add_column("Distance", style="cyan")
            table.add_column("Status", style="cyan")

            # Add rows, with special formatting for the top anomalies
            for i, row in enumerate(anomalies.itertuples()):
                current_time = datetime.now()
                packet_time = datetime.fromisoformat(str(row.timestamp))  # Explicitly convert to string
                time_diff = (current_time - packet_time).total_seconds()
                #status = "New" if time_diff < 300 else "Decaying"  # Change 300 as per your decay duration in seconds
                status = "New" if time_diff < 30 else "Decaying"  # Change 30 as per your decay duration in seconds

                if i < N_TOP_ANOMALIES:
                    table.add_row(row.dst_ip, row.type, str(row.size), f"{row.distance_to_center}", status, style="red")
                else:
                    table.add_row(row.dst_ip, row.type, str(row.size), f"{row.distance_to_center}", status)

            console.print(table)

            # Highlighting the top N anomalies in a different color (e.g., red)
            for i, row in anomalies.head(N_TOP_ANOMALIES).iterrows():
                anomaly_pca = X_pca[df.index.get_loc(i)]
                current_time = datetime.now()
                packet_time = datetime.fromisoformat(str(row.timestamp))  # Explicitly convert to string
                time_diff = (current_time - packet_time).total_seconds()

                # Calculate alpha based on the time difference
                #alpha_value = max(0.2, 1 - (time_diff / 300))  # Decaying over 5 minutes (300 seconds)
                alpha_value = max(0.2, 1 - (time_diff / 30))  # Decaying over 30 seconds
                ax1.scatter(anomaly_pca[0], anomaly_pca[1], c='red', s=row['size']/50, alpha=alpha_value)

            for i, row in anomalies.head(N_TOP_ANOMALIES).iterrows():
                unique_id = f"{row['dst_ip']}_{row['type']}_{row['size']}"
                anomaly_pca = X_pca[df.index.get_loc(i)]
                
                alpha_value = 1.0  # Default opacity for "New"
                if unique_id in anomaly_history:
                    if anomaly_history[unique_id]['status'] == 'Decaying':
                        alpha_value = 0.5  # Change this value to set your preferred opacity for "Decaying" anomalies
                
                ax1.scatter(anomaly_pca[0], anomaly_pca[1], c='red', s=row['size']/50, alpha=alpha_value)
                ax1.text(anomaly_pca[0], anomaly_pca[1], f"{row['dst_ip']} ({row['type']}, {row['size']} bytes)", color='black')

            ax1.set_ylabel('Packet Size')
            plt.draw()
            plt.pause(0.01)
            # plt.close()  # Close the current figure to free up memory -- Nice, but doesnt work with 30 second refresh...

            console.print(f"[green]Updated 2D plot with {len(df)} packets.[/green]")
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
