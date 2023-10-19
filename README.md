# JAWS
![hehe](/assets/ohey.jpeg)

Demonstration of packet clustering analysis using Python, Pyshark, Kmeans, and PCA. Designed/written in collaboration with ChatGPT.

To use the program, you can either generate packets using a tool like the ones found on this list:
https://www.brianlinkletter.com/2023/02/network-emulators-and-network-simulators-2023/

Or, you can setup a free Amazon EC2 instance and upload `ec2_listener.py` to it. Run the listener (443), and then run `ec2_chum.py` on the local machine. This will create TLS encrypted packets and send them to the EC2 instance. the `chum` program contains some variables adjusting the style of packet, but in general it allows the end-user to give it a "file size" and it simulates exfiltration.

With a network simulator, or our chum program running, you can then run `sea.py`, which uses `pyshark` to capture all packets on the desired interface. In this instance, we used our local Ethernet interface. The sea program, to avoid complexities (ChatGPT failed on several attempts to incorporating threading), writes batches of 100 packets to a pandas dataframe and then saves that to a stable file called `packets.json` -- You can inspect `sea.py` to see what it is capturing.

Lastly, the big boi program, `jaws`. Consumes all the data in packets.json and runs analysis for "anomalies". `jaws_3d_kmeans.py` was the first version which is much simpler compared to the 2D PCA approach, it also lacks much of advanced features to better manage the anomalies. While the 3D Plot using Kmeans did work, it was very slow to recognize anomalies isnt great to look at in the end... it wasnt until I prototyped the 2D PCA visual (by just running PCA on the data) that I realized it was easier to read. This led to creating `jaws_2d_pca.py`, which reads the packets.json file and runs analysis on the entire dataset each round. Yes... not memory optimized, but I have plenty of RAM and this was just easier to reason about for ChatGPT...  Anyways, focusong on `dst_ip`, `type`, and `size`, the program uses PCA to reduce the feature set and then returns a 2D plot of packets, with anomalies called out in red with labels. It also attempts to track the anomalies for reporting in the console (Top 20 Anomalies rolling) and also for applying a decay to their visibility on the graph.

To bring it all full circle, I created `ec2_chum.py` to provide a closed loop testing toolset that demonstrates the recognition of anomalies within network traffic.

Some screenshots and captions:
![Screenshots and annotations outlining the process described above.](/assets/flow.png)
