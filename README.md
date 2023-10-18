# JAWS
![hehe](/assets/ohey.jpeg)

Demonstration of packet clustering analysis using Python, Pyshark, Kmeans, and PCA. Designed/written in collaboration with ChatGPT.

To use the program, you can either generate packets using a tool like the ones found on this list:
https://www.brianlinkletter.com/2023/02/network-emulators-and-network-simulators-2023/

Or, you can setup a free Amazon EC2 instance and upload `ec2_listener.py` to it. Run the listener (443), and then run `ec2_chum.py` on the local machine. This will create TLS encrypted packets and send them to the EC2 instance. the `chum` program contains some variables for tuning the burst, but in general, this program is intended to mimic a file exfiltration to a remote client.

With a network simulator or our chum program running, you can then run `water.py`, which uses `pyshark` to capture all packets on the desire interface. In this instance, we used our local Ethernet interface. The water program to avoid complexities (ChatGPT failed on several attempts to incorporating threading), writes batches of 100 packets to a pandas dataframe and then saves that to a stable file called `packets.json` -- You can inspect `water.py` to see that we are capturing.

Lastly, the big boi program, `jaws`. Consumes all the data in packets.json and runs analysis for "anomalies". `jaws_3d_kmeans.py` was the first version which is much simpler compared to the 2D PCA approach. The 3D Plot using Kmeans did work, but was very slow to recognize anomalies and it wasnt until we prototyped the 2D PCA visual that I realized it was easier to read. This led to creating `jaws_2d_pca.py`, which reads the packets.json file and runs analysis on the entire dataset each round. Yes... not memory optimized, but I have plenty and this was just easier to reason about...  Anyways, focusong on `dst_ip`, `type`, and `size`, the program uses PCA to reduce the feature set and then returns a 2D plot of anomaly packets.

To bring it full circle, we created `ec2_chum.py` to provide a closed loop test that demonstrates the recognition of anomalies within network traffic.

Some screenshots and captions:
![Screenshots and annotations outlining the process described above.](/assets/process.png)
