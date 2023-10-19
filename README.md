# JAWS
![hehe](/assets/ohey.jpeg)

A little side project demonstrating the use of machine learning in cybersecurity by applying cluster analysis to network traffic. To add to it, Ive almost strictly been collabortating with ChatGPT on my side projects and this was one of those. Entirelly written by ChatGPT, but under strict supervision by me, and in some situations (threading for instance), could not get ChatGPT to reason through the challange and so abandoned the approach to maintain a full AI written outcome.

To use the program, you can either generate packets using a tool like the ones found on this list:
https://www.brianlinkletter.com/2023/02/network-emulators-and-network-simulators-2023/

Or... you can setup a free Amazon EC2 instance and upload `listener.py` to it. Run the listener, and then run `sea.py` & `chum.py` on the local machine. Chum will create TLS encrypted packets and send them to the EC2 instance. the `chum` program contains some variables adjusting the style of packet, but in general it allows the end-user to give it a "file size" and it simulates exfiltration.

With a network simulator, or our chum program ready, you can then run `sea.py`, which uses `pyshark` to capture all packets on the desired interface. In this instance, we used our local Ethernet interface. The sea program, to avoid complexities (ChatGPT failed on several attempts to incorporating threading), writes batches of 100 packets to a pandas dataframe and then saves that to a stable file called `packets.json` -- You can inspect `sea.py` to see how it works what it is capturing.

Lastly, the big boi program, `jaws`. Consumes all of the data in packets.json and runs analysis for "anomalies". Yes... not very memory optimized, but I gots plenty of RAM and this was just easier for ChatGPT to reason about...  Anyways, focusong on `dst_ip`, `type`, and `size`, the program uses PCA to reduce the feature set and then returns a 2D plot of packet clusters, with top anomalies called out in red with labels. It also attempts to track the anomalies for both reporting in the console (Top 20 Anomalies rolling) and also for applying a decay to their visibility on the graph. I started with a simple Kmeans approach, but have also implemented a DBSCAN approach, use `_Kmeans` and `_DBSCAN` as you wish.

To bring it all full circle, I created `chum.py` to provide a closed loop testing toolset that demonstrates the recognition of anomalies within network traffic. Its up to you to run chum like an attacker to see those packets appear as anomalies on the graph.

### Im sure there is lots I could improve on, there are limitations to writing console toys with ChatGPT... but leave some issues or something:

Updates: Added `hunt.py` which requests an IP address, just copy it from `jaws`, and returns a ChatGPT lookup with common parameters for IP address ownership like location :0 as well as a time series graph of activity for that `dst_ip`.

Updates: Updated `jaws` to use DBSCAN instead of Kmeans, updated reamdme to reflect this change.