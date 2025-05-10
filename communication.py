import socket
import threading

class WiFiHandler:
    def __init__(self, ip, port, on_receive_callback):
        self.ip = ip
        self.port = port
        self.socket = None
        self.connected = False
        self.lock = threading.Lock()
        self.receive_thread = None
        self.on_receive_callback = on_receive_callback

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.connected = True
            self.receive_thread = threading.Thread(target=self.receive_loop, daemon=True)
            self.receive_thread.start()
            return True
        except Exception as e:
            print(f"Failed to connect to {self.ip}:{self.port}: {e}")
            return False

    def disconnect(self):
        if self.socket:
            self.socket.close()
            self.socket = None
        self.connected = False
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join()

    def send(self, message):
        if self.socket and self.connected:
            try:
                self.socket.sendto(message.encode(), (self.ip, self.port))
                return True
            except Exception as e:
                print(f"Failed to send message to {self.ip}:{self.port}: {e}")
                return False
        else:
            print("Not connected")
            return False

    def receive_loop(self):
        while self.connected:
            try:
                data, addr = self.socket.recvfrom(1024)
                if self.on_receive_callback:
                    with self.lock:
                        self.on_receive_callback(data.decode())
            except Exception as e:
                print(f"Error receiving data: {e}")
                break

class RefBoxHandler:
    def __init__(self, ip, port, on_receive_callback, on_disconnect_callback):
        self.ip = ip
        self.port = port
        self.socket = None
        self.connected = False
        self.running = False
        self.on_receive_callback = on_receive_callback
        self.on_disconnect_callback = on_disconnect_callback

    def connect(self):
        if not self.connected:
            self.running = True
            threading.Thread(target=self._listen_loop, daemon=True).start()

    def _listen_loop(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.ip, self.port))
                self.socket = s
                self.connected = True
                print(f"Connected to RefBox at {self.ip}:{self.port}")
                while self.running:
                    data = s.recv(1024)
                    if not data:  # Empty data means the connection was closed
                        break
                    message = data.decode("utf-8").strip()
                    if message and self.on_receive_callback:
                        self.on_receive_callback(message)
        except Exception as e:
            print(f"Connection error: {e}")
        finally:
            self.connected = False
            self.running = False
            if self.on_disconnect_callback:
                self.on_disconnect_callback()  # Notify disconnection
            print("RefBox connection closed.")

    def stop(self):
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except OSError:
                pass