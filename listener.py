import socket
import ssl
import traceback

# Listen on all available interfaces
HOST = '0.0.0.0'
# Port to listen on
PORT = 443

# Create a socket object. SOCK_STREAM means it will be a TCP socket.
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Reuse address
    sock.bind((HOST, PORT))
    sock.listen()

    print(f"Listening on {HOST}:{PORT}")

    # Accept connections. This will block until a connection is received.
    while True:
        try:
            conn, addr = sock.accept()
            print(f"Connected by {addr}")
        except Exception as e:
            print(f"Error accepting connection: {e}")
            continue
        
        # Create a connection object. This will be used to send and receive data.
        with conn:
            # Upgrade to TLS. This will fail if the client does not support TLS.
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            
            # Load certificate and key files. These files must be in the same directory as this script.
            try:
                context.load_cert_chain(certfile="anomaly_cert.pem", keyfile="anomaly_key.pem")  # Replace with your cert and key files
            except Exception as e:
                print(f"Error loading certificate and key: {e}")
                traceback.print_exc()
                continue

            # Perform SSL handshake. This will block until the handshake is complete.
            # If the handshake fails, an exception will be raised.
            # If the handshake succeeds, a new connection object will be returned.
            # This new connection object will be used to send and receive data.
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
