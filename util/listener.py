import socket
import ssl
import traceback

# Used in conjunction with chum.py
# Place this script on your server and run it. It will listen for incoming connections on the port you configure below, allowing the connection and "accepting" the payload, acting as our "exfiltration server".

HOST = '0.0.0.0'
PORT = 40687

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen()

    print(f"Listening on {HOST}:{PORT}")
    while True:
        try:
            conn, addr = sock.accept()
            print(f"Connected by {addr}")
        except Exception as e:
            print(f"Error accepting connection: {e}")
            continue
        
        with conn:
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            try:
                context.load_cert_chain(certfile="anomaly_cert.pem", keyfile="anomaly_key.pem")
            except Exception as e:
                print(f"Error loading certificate and key: {e}")
                traceback.print_exc()
                continue

            try:
                with context.wrap_socket(conn, server_side=True) as sconn:
                    print("SSL handshake successful")
                    while True:
                        data = sconn.recv(1024)
                        if not data:
                            print("Connection closed by client")
                            break
                        print(f"Received {len(data)} bytes")
            except ssl.SSLError as e:
                print(f"SSL handshake failed: {e}")
                traceback.print_exc()
            except Exception as e:
                print(f"An error occurred: {e}")
                traceback.print_exc()
