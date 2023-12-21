# JAWS
![hehe](/assets/ohey.jpeg)

A closed-loop network packet capture, analysis, and modeling toolset. Intended as a case-study for data-quality analysis and model fine-tuning. There was a v1 that was insane, it tried to do all this auto-magical anomaly detection, but it was rubbish...

If you wish to play with it... Start by configuring `interface` and other paramaters and running `sea.py`, which uses `pyshark` to capture all packets on the desired interface. In this instance, we used our local Ethernet interface. You can inspect `sea.py` to see how it works what it is capturing, but highlevel the script writes batches (configurable) of 100 packets to a pandas dataframe and then writes that to a stable file called `packets.csv`

`sea.py` can be used to create all sorts of network activity datasets, for example, using the other scripts in the `/util` directory, you could set up and run a free AWS EC2 instance. This will allow for the simulation of exfiltration events using the `chum.py` and `listener.py`. Going back to and inspecting the `sea.py` script, you may notice that you can configure it to blacklist IP addresses and label activity. The script is setup to label all normal activity packets as `norm` and all chum packets as `chum`. I have used a combination of running the script without any exfiltration events for a clean "baseline activity" dataset and running the script while simulating exfiltration events to create test sets.

`push.py` is a utility for pushing a file the EC2 instance. I was using this on an edge device to push packets.json before going offline and no longer having access to said device. Disclaimer: I owned all of these devices...

It is also advisable to rename `packets.csv` between script cycles, this is because the rest of the scripts accept a list of packet csv files. For instance, the next step could be running `finder.py` using all of the datasets to understand where chum activity is happening against the backdrop/noise of baseline network activity. I have used this analysis to train and fine-tune detection models. Or you could play with `detect.py`, which is a v0 detection model.

Lastly, using analysis to determine anomlies or suspect addresses, you can `jaws.py` to pass an IP address to OpenAI for "OSINT"... I have explored several prompts and approach and feel that the current file returns a good list of public information include lat/long... but feel free to modify further. Additionally, this script also uses the IP address and all included csv files to create a time-series graph of network activity for this specific IP address.

This current state represents a refactor and simplification. Next steps include further development of the detection model and analysis documentation to improve this case-study.

![the diagram!](/assets/diagram_4.png)
