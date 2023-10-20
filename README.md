# JAWS
![hehe](/assets/ohey.jpeg)

A little side project demonstrating the use of machine learning in cybersecurity by applying cluster analysis to network traffic. To add to it, Ive almost strictly been collabortating with ChatGPT on my side projects and this was one of those. Entirelly written by ChatGPT, but under strict supervision by me, and in some situations (threading for instance), could not get ChatGPT to reason through the challange and so abandoned the approach to maintain a full AI written outcome.

You can then run `sea.py`, which uses `pyshark` to capture all packets on the desired interface. In this instance, we used our local Ethernet interface. The sea program, to avoid complexities (ChatGPT failed on several attempts to incorporating threading), writes batches of 100 packets to a pandas dataframe and then saves that to a stable file called `packets.json` -- You can inspect `sea.py` to see how it works what it is capturing.

The big boi program, `jaws.py`. Consumers all packet data in `packets.json` and processes it through DBSCAN to output clusters and plot those clusters along with labels on a 2D graph. The program also outputs a list of Top 20 Anomalies in the console with the top 5 highlighed in red. Every 30 seconds the data refreshes, in full... tried several attempts to handle only new packets but failed to get ChatGPT to reason through the problem. I have run the programs together past 1m packets with little memory impact.

To bring it all full circle, you can either generate packets using a tool like the ones found on this list:
https://www.brianlinkletter.com/2023/02/network-emulators-and-network-simulators-2023/

Or... you can setup a free Amazon EC2 instance and upload `listener.py` to it. Run the listener, and then run `sea.py` & `chum.py` on the local machine. Chum will create TLS encrypted packets and send them to the EC2 instance. the chum program contains some variables adjusting the style of packet, but in general it allows the end-user to give it a "file size" and it simulates exfiltration.

![the flow!](/assets/diagram_2.png)
![the flow!](/assets/flow.png)

### Im sure there is lots I could improve on, there are limitations to writing console toys with ChatGPT... but leave some issues or something:

Updates: Added `hunt.py` which requests an IP address, just copy it from `jaws`, and returns a ChatGPT lookup with common parameters for IP address ownership like location :0 as well as a time series graph of activity for that `dst_ip`.

Updates: Added `push.py` for those using the free EC2 instance approach. This contains variables for a file name (currently set to our packets file) and the EC2 parameters and then push that file to the server `/home/ec2-user/packet_captures/`. It also appends the datetime to the file name. I created this because I am using an edge device to capture packets from a remote network and needed a way to quickly and easily get the file off the edge device when it regained connectivity. *Educational purposes only, the "edge device" and "remote network" are actually a Clockwork uConsole, LAN Tap, and my home network.