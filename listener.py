import socket
import ssl
import traceback

HOST = '0.0.0.0'  # Listen on all available interfaces
PORT = 443

# Create a socket object
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Reuse address
    sock.bind((HOST, PORT))
    sock.listen()

    print(f"Listening on {HOST}:{PORT}")

    # Accept connections
    while True:
        try:
            conn, addr = sock.accept()
            print(f"Connected by {addr}")
        except Exception as e:
            print(f"Error accepting connection: {e}")
            continue

        with conn:
            # Upgrade to TLS
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            
            try:
                context.load_cert_chain(certfile="anomaly_cert.pem", keyfile="anomaly_key.pem")  # Replace with your cert and key files
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
