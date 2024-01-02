# JAWS
![hehe](/assets/ohey.jpeg)

Proof of concept pipeline for gathering network packets on a given `interface` and understanding various shapes of the network including... scatter plots, DBSCAN outlier, subgraph analysis, and directed network graphs.

`sea.py` -- The main file. Update the `batch`, `interface`, CSV file names, and if you use the `chum.py` script, your AWS or "exfiltration simulation ip". Also update any packet details you wish to capture.

`chum.py` -- This script in conjunctuon with `listner.py`, and any "remote server" (I've been testing with a free EC2 instance at no cost...), can help simulate "exfiltration events". In addition, the `sea.py` script, when given this `ip address`, will label the data accordingly... eiter `BASE` pr `CHUM`.

The rest of the scripts in `/util` are for backup. `_subgraph` and `_indegree` are now combined in `sub.py` and `listener` is a classic listener script.

With `sea` and `chum` running, a `packets.csv` file is either created or updated with packets. From there, you can run the following scripts to visualize the data:

`finder.py` -- Simple 2D scatter showing `port` and `size`. It also handled `BASE` and `CHUM` packets differently, coloring the chum packets red. For quickly seeing what is going on and how the data set is shapping up. Also for exploring port activity.

`scan.py` -- PCA and DBSCAN with `dst_port` pulled out and used as the outlier label. Displays as a polar plot for thematics... For exploring how the data is clustering and which ports stand out.

`captain.py` -- Runs both finder and scan in threads.

`sub.py` -- Perform subgraph analysis with in and out degree, outputs a CSV file and a directed graph visual. For topology of the network.

`jaws.py` -- Simple Random Forest classifier script currently set to `dst_port` and `size`, returning `dst_ip`. WIP.

`report.py` -- For a given `ip address`, returns a timeseries plot. Also passes this address to OpenAI for public information. WIP.

Screenshot for demonstration. Running on a 24" monitor... If less, you may want to adjust the figure parameters before running.
![screenshot](/assets/example.png)