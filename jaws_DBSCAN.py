import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from time import sleep
from rich.console import Console
from rich.progress import Progress
from rich.table import Table
from scipy.spatial import distance
import numpy as np
import json
from datetime import datetime

# Initialize console and progress bar
console = Console()
progress = Progress(console=console)

# Increase this value based on your preference
N_ANOMALIES_TO_DISPLAY = 20
N_TOP_ANOMALIES = 5            
# Predefined colors for clusters
cluster_colors = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
]
    
# Key will be some unique identifier for an anomaly, value will be metadata like timestamp
anomaly_history = {}
# New dictionary to hold cluster centers
cluster_centers = {}

# function to update anomaly history
def update_anomaly_history(anomalies, anomaly_history):
    current_time = datetime.now()
    to_remove = []

    for unique_id, meta in anomaly_history.items():
        if (current_time - meta['timestamp']).total_seconds() > 30:
            to_remove.append(unique_id)
        else:
            meta['status'] = 'Decaying'
            meta['timestamp'] = current_time

    for unique_id in to_remove:
        del anomaly_history[unique_id]

    for i, row in anomalies.iterrows():
        unique_id = f"{row['dst_ip']}_{row['type']}_{row['size']}"
        if unique_id not in anomaly_history:
            anomaly_history[unique_id] = {'timestamp': current_time, 'status': 'New'}
        else:
            anomaly_history[unique_id]['status'] = 'New'

# New function to update cluster centers
def update_cluster_centers(X_normalized, labels):
    unique_labels = set(labels)
    for label in unique_labels:
        if label != -1:
            core_samples = X_normalized[labels == label]
            cluster_centers[label] = np.mean(core_samples, axis=0)

def display_anomalies(anomalies, N_ANOMALIES_TO_DISPLAY):
    table = Table(title=f"Top {N_ANOMALIES_TO_DISPLAY} Anomaly Packets")
    table.add_column("Destination IP", style="cyan")
    table.add_column("Type", style="cyan")
    table.add_column("Size", style="cyan")
    table.add_column("Distance", style="cyan")
    table.add_column("Status", style="cyan")

    for i, row in enumerate(anomalies.itertuples()):
        status = "New" if row.distance_to_center < 30 else "Decaying"  # Adjust this condition as needed
        if i < N_TOP_ANOMALIES:
            table.add_row(row.dst_ip, row.type, str(row.size), f"{row.distance_to_center}", status, style="red")
        else:
            table.add_row(row.dst_ip, row.type, str(row.size), f"{row.distance_to_center}", status)

    console.print(table)

# Function to apply PCA and DBSCAN
def apply_dbscan_and_pca(X_normalized, eps=0.5, min_samples=5):
    pca = PCA(n_components=2)  # Reducing data to 2 dimensions
    X_pca = pca.fit_transform(X_normalized)
    
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbscan.fit_predict(X_normalized)
    return X_pca, labels

# Initialize figure with reduced dimensions
fig, ax1 = plt.subplots(1, 1, figsize=(14, 7))
plt.show(block=False)
plt.tight_layout()

def plot_and_annotate_anomalies(ax, anomalies, X_pca, labels, df):
    # Sort anomalies based on their distance to cluster center
    sorted_anomalies = anomalies.sort_values(by='distance_to_center', ascending=False)

    for idx, row in enumerate(sorted_anomalies.itertuples()):
        point = X_pca[row.Index]
        color = 'red' if idx < N_TOP_ANOMALIES else 'black'
        ax.scatter(point[0], point[1], c=color, s=row.size / 50, zorder=3)  # zorder ensures points are above cluster
        if idx < N_ANOMALIES_TO_DISPLAY:
            ax.annotate(f"{row.dst_ip}, {row.type}, {row.size}", (point[0], point[1]), textcoords="offset points", xytext=(0, 5), ha='center')

with progress:
    task_id = progress.add_task("[cyan]Processing next update, refreshing in...", total=30)
    while True:
        try:
            df = pd.read_json('packets.json', orient='records')

            # Convert timestamps from Unix timestamp in milliseconds to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

            df['type_code'] = df['type'].astype('category').cat.codes
            df['dst_ip_code'] = df['dst_ip'].astype('category').cat.codes
            X = df[['type_code', 'size', 'dst_ip_code']].to_numpy()

            scaler = StandardScaler()
            X_normalized = scaler.fit_transform(X)
            X_pca, labels = apply_dbscan_and_pca(X_normalized)
            unique_labels = set(labels)
            ax1.clear()

            for label in unique_labels:
                if label == -1:  # Noise points
                    color = '#000000'
                else:
                    color = cluster_colors[label % len(cluster_colors)]

                points_in_cluster = np.array([X_pca[i] for i in range(len(X_pca)) if labels[i] == label])
                sizes = [df.iloc[i]['size'] for i in range(len(X_pca)) if labels[i] == label]
                ax1.scatter(points_in_cluster[:, 0], points_in_cluster[:, 1], c=color, s=np.array(sizes)/50)
            
            # Distance to nearest cluster center
            distances = []
            for i, label in enumerate(labels):
                if label == -1:
                    distances.append(np.inf)  # Assign infinite distance for noise points
                else:
                    core_samples = X_normalized[labels == label]
                    mean_core_sample = np.mean(core_samples, axis=0)
                    distances.append(distance.euclidean(X_normalized[i], mean_core_sample))
                    
            df['distance_to_center'] = distances
            anomalies = df.nlargest(N_ANOMALIES_TO_DISPLAY, 'distance_to_center')

            current_time = datetime.now()
            
            # Update and display anomalies
            update_anomaly_history(anomalies, anomaly_history)
            display_anomalies(anomalies, N_ANOMALIES_TO_DISPLAY)

            # Updating cluster centers
            update_cluster_centers(X_normalized, labels)

            # Add this line to actually plot and annotate anomalies
            plot_and_annotate_anomalies(ax1, anomalies, X_pca, labels, df)
            
            ax1.set_ylabel('Principal Component 2')
            plt.draw()
            plt.pause(0.01)

            console.print(f"[green]Updated 2D plot with {len(df)} packets.[/green]")
            progress.update(task_id, completed=30)
            sleep(1)

            progress.reset(task_id)
            for i in range(30):
                sleep(1)
                progress.update(task_id, advance=1)
        except KeyboardInterrupt:
            console.print("[yellow]Program manually terminated by user.[/yellow]")
            plt.close('all')  # Closes all Matplotlib windows.
            break  # Exit the while loop
        except json.JSONDecodeError:
            console.print("[red]An error occurred while reading the JSON file. Retrying...[/red]")
            with open("error_log.txt", "a") as f:
                f.write("JSONDecodeError occurred\n")
            sleep(1)
        except Exception as e:
            console.print(f"[red]An unexpected error occurred: {e}. Retrying...[/red]")
            with open("error_log.txt", "a") as f:
                f.write(f"Unexpected error: {e}\n")
            sleep(1)
