from time import sleep
from datetime import datetime
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy.spatial import distance
from rich.console import Console
from rich.progress import Progress
from rich.table import Table

# Initialize the rich console styling and refresh timer/progress bar.
console = Console()
progress = Progress(console=console)

# Predefined colors for clusters, currently a single color, but accepts a list.
cluster_colors = ["#0077be", "#0099cc", "#66b3e6", "#99ccff", "#cce0ff"]

# New dictionary to hold cluster centers.
cluster_centers = {}

# Key will be some unique identifier for an anomaly, value will be metadata like timestamp.
anomaly_history = {}

# Variables for defining the number of anomalies to display in the console, followed by the numner of "Top" anomalies to call out in red.
N_ANOMALIES_TO_DISPLAY = 20
N_TOP_ANOMALIES = 5

# More variables for moving average and its window size.
# A small window size will yield a moving average that closely follows the original data but may also include noise.
# A larger window size will smooth out fluctuations and noise but could lag behind the real-time changes in data.
moving_avg_window = []
WINDOW_SIZE = 5 # 10

# This function will apply PCA to reduce the data to 2 dimensions, and then apply DBSCAN to cluster the data. The function returns the reduced data and the labels.
# Smaller eps: Will create more clusters and may classify more points as noise (anomalies in your case).
# Larger eps: Will create fewer, larger clusters and potentially fewer noise points.
# Smaller min_samples: Easier to form a cluster, which might lead to more, smaller clusters and potentially fewer noise points.
# Larger min_samples: Harder to form a cluster, could lead to fewer, larger clusters and more noise points (anomalies).
# A larger eps and smaller min_samples will create fewer, larger clusters. This setting is more lenient and is less likely to identify outliers.
# A smaller eps and larger min_samples will create more clusters and will likely identify more points as noise or outliers. This setting is stricter.
def apply_dbscan_and_pca(X_normalized, eps=0.5, min_samples=10):
    pca = PCA(n_components=2)  # Reducing data to 2 dimensions
    X_pca = pca.fit_transform(X_normalized)
    # DBSCAN is a density-based clustering algorithm that groups points based on their distance to each other.
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbscan.fit_predict(X_normalized)
    return X_pca, labels

# Function to update cluster centers. This function will update the cluster centers based on the mean of the core samples in each cluster.
def update_cluster_centers(X_normalized, labels):
    unique_labels = set(labels)
    for label in unique_labels:
        if label != -1:
            core_samples = X_normalized[labels == label]
            cluster_centers[label] = np.mean(core_samples, axis=0)

# Function to update anomaly history. Attempts to track anomalies based on their timestmp in the anomaly_history dictionary. Older anomalies are removed from the dictionary, and new anomalies are added. Updating the status in the console table from new to decaying and new again.
def update_anomaly_history(anomalies, anomaly_history):
    current_time = datetime.now()
    to_remove = []

    for unique_id, meta in anomaly_history.items():
        if (current_time - meta['timestamp']).total_seconds() > 30:
            to_remove.append(unique_id)
        else:
            meta['status'] = 'DECAYING'
            meta['timestamp'] = current_time

    for unique_id in to_remove:
        del anomaly_history[unique_id]

    for i, row in anomalies.iterrows():
        unique_id = f"{row['dst_ip']}_{row['dst_port']}_{row['type']}_{row['size']}"
        if unique_id not in anomaly_history:
            anomaly_history[unique_id] = {'timestamp': current_time, 'status': 'NEW'}
        else:
            anomaly_history[unique_id]['status'] = 'NEW'

def display_anomalies(anomalies, N_ANOMALIES_TO_DISPLAY):
    table = Table() #title=f"Top {N_ANOMALIES_TO_DISPLAY} Anomaly Packets"
    
    # Table for displaying anomalies in the console.
    table.add_column("DEST IP", style="cyan")
    table.add_column("PORT", style="cyan")  
    table.add_column("TYPE", style="cyan")
    table.add_column("SIZE", style="cyan")
    table.add_column("DIST", style="cyan")
    table.add_column("STATUS", style="cyan")
    
    # Loop through the anomalies dataframe and add each row to the table. The first N_TOP_ANOMALIES will be highlighted in red.
    for i, row in enumerate(anomalies.itertuples()):
        status = "NEW" if row.distance_to_center < 30 else "DECAYING"  # This is the distance from the cluster center. Currently set to 30. 
        
        # This produces the list of top anomalies in red, and the rest of the top 20 in default coloring.
        if i < N_TOP_ANOMALIES:
            table.add_row(row.dst_ip, str(row.dst_port), row.type, str(row.moving_avg_size), f"{row.distance_to_center}", status, style="red")
        else:
            table.add_row(row.dst_ip, str(row.dst_port), row.type, str(row.moving_avg_size), f"{row.distance_to_center}", status)

    console.print(table)

# This function will plot the anomalies on the 2D plot and annotate them with their destination IP, type, and size.
def plot_and_annotate_anomalies(ax, anomalies, X_pca, labels, df):
    # Sort anomalies based on their distance to cluster center
    sorted_anomalies = anomalies.sort_values(by='distance_to_center', ascending=False)
    
    # Plotting the anomalies. 
    # The size of the point is based on the size of the packet.
    # The zorder ensures that the points are above the clusters.
    # The annotation will display the destination IP, type, and size of the packet.
    # The annotation will only display for the first N_ANOMALIES_TO_DISPLAY.
    # The color of the annotation will be red for the first N_TOP_ANOMALIES, and black for the rest.
    for idx, row in enumerate(sorted_anomalies.itertuples()):
        point = X_pca[row.Index]
        color = 'red' if idx < N_TOP_ANOMALIES else 'blue' #color of plotted anomalies.
        ax.scatter(point[0], point[1], c=color, s=row.size, zorder=3)  # zorder ensures points are above cluster
        if idx < N_ANOMALIES_TO_DISPLAY:
            ax.annotate(f"{row.dst_ip}, {row.type}, {row.size}", (point[0], point[1]), textcoords="offset points", xytext=(0, 5), ha='center')

# Initialize figure with reduced dimensions and display the plot.
fig, ax1 = plt.subplots(1, 1, figsize=(15, 7)) # Change the graph dimensions, in inches.
plt.tight_layout() # Tight layout, reducing padding. Comment out if needed.

# Main loop. This loop will read the JSON file, convert the data to a Pandas dataframe, and then apply DBSCAN and PCA to cluster the data. The loop will then update the plot and display the anomalies in the console.
with progress:
    # This progress bar will refresh every 30 seconds.
    task_id = progress.add_task("[cyan]Waiting on packets... refreshing in...", total=30)
    while True:
        try:
            df = pd.read_json('packets.json', orient='records')

            # Moving avgerage of packet sizes. This will smooth out the data and reduce noise.
            new_packet_sizes = df['size'].tolist()
            moving_avg_window.extend(new_packet_sizes)
            if len(moving_avg_window) > WINDOW_SIZE:
                moving_avg_window = moving_avg_window[-WINDOW_SIZE:]

            moving_avg = sum(moving_avg_window) / len(moving_avg_window)

            # Convert category to codes for type, dst_ip, src_port, and dst_port.
            df['type_code'] = df['type'].astype('category').cat.codes
            df['dst_ip_code'] = df['dst_ip'].astype('category').cat.codes
            
             # Convert category to codes for src_port and dst_port.
            df['src_port_code'] = df['src_port'].astype('category').cat.codes
            df['dst_port_code'] = df['dst_port'].astype('category').cat.codes

            # Convert timestamps from Unix timestamp in milliseconds to datetime.
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

            # Add moving average column to dataframe.
            df['moving_avg_size'] = moving_avg

            # Convert dataframe to numpy array. This is the data that will be clustered.
            X = df[['type_code', 'moving_avg_size', 'dst_ip_code', 'src_port_code', 'dst_port_code']].to_numpy()

            # Normalize the data. This is important because DBSCAN is a distance-based clustering algorithm.
            # If the data is not normalized, the clustering will be skewed towards the features with the largest values.
            scaler = StandardScaler()
            X_normalized = scaler.fit_transform(X)
            X_pca, labels = apply_dbscan_and_pca(X_normalized)
            unique_labels = set(labels)
            ax1.clear()

            # Plotting the clusters. The size of the point is based on the size of the packet.
            for label in unique_labels:
                if label == -1:  # Noise points
                    color = '#1F2BB5'
                else:
                    color = cluster_colors[label % len(cluster_colors)]
                # Plotting the points in each cluster. The size of the point is based on the size of the packet.
                points_in_cluster = np.array([X_pca[i] for i in range(len(X_pca)) if labels[i] == label])
                sizes = [df.iloc[i]['moving_avg_size'] for i in range(len(X_pca)) if labels[i] == label]
                ax1.scatter(points_in_cluster[:, 0], points_in_cluster[:, 1], c=color, s=np.array(sizes)/50)
            
            # Distance to nearest cluster center. This will be used to determine which points are anomalies.
            distances = []
            # Loop through each point and calculate the distance to the nearest cluster center.
            for i, label in enumerate(labels):
                if label == -1:
                    distances.append(np.inf)  # Assign infinite distance for noise points
                else:
                    core_samples = X_normalized[labels == label]
                    mean_core_sample = np.mean(core_samples, axis=0)
                    distances.append(distance.euclidean(X_normalized[i], mean_core_sample))

            # Add distance to nearest cluster center as a column in the dataframe.     
            df['distance_to_center'] = distances
            anomalies = df.nlargest(N_ANOMALIES_TO_DISPLAY, 'distance_to_center')
            
            # Update and display anomalies. This will update the anomaly history and display the anomalies in the console.
            update_anomaly_history(anomalies, anomaly_history)
            display_anomalies(anomalies, N_ANOMALIES_TO_DISPLAY)

            # Updating cluster centers. This will update the cluster centers based on the mean of the core samples in each cluster.
            update_cluster_centers(X_normalized, labels)

            # Add this line to actually plot and annotate anomalies.
            plot_and_annotate_anomalies(ax1, anomalies, X_pca, labels, df)
            
            # Add this line to plot the cluster centers.
            plt.title(f"Packet Clusters (Total Packets: {len(df)})")
            #plt.xlabel(f'Principal Component 1 ({explained_var[0]*100:.2f}%)')
            #plt.ylabel(f'Principal Component 2 ({explained_var[1]*100:.2f}%)')
            plt.draw()
            plt.pause(0.01)

            # Update the progress bar.
            console.print(f"[green]Updating 2D plot of packet clusters using: {len(df)} packets.[/green]")
            progress.update(task_id, completed=30)
            sleep(1)

            # Reset the progress bar.
            progress.reset(task_id)
            for i in range(30):
                sleep(1)
                progress.update(task_id, advance=1)

        # Error handling. This will catch any errors and log them to the error_log.txt file.
        except KeyboardInterrupt:
            console.print("[yellow]Program manually terminated by user.[/yellow]")
            plt.close('all')  # Closes all Matplotlib windows.
            break  # Exit the while loop

        # This error will occur if the JSON file is empty.
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