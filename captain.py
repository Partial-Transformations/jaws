import subprocess
import threading

def run_finder():
    subprocess.run(["python", "./finder.py"])

def run_scan():
    subprocess.run(["python", "./scan.py"])

def main():
    thread_finder = threading.Thread(target=run_finder)
    thread_scan = threading.Thread(target=run_scan)

    thread_finder.start()
    thread_scan.start()

if __name__ == '__main__':
    main()
