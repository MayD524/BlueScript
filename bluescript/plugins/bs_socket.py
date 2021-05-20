from concurrent.futures import ThreadPoolExecutor
import bs_memory
import bs_types
import socket
import UPL

class BLUE_SERVER:
    def __init__(self, hostname, hostIP, port):
        self.run_server = True
        self.hostname = hostname
        self.hostIP = hostIP
        self.port = port 
        self.get_connections()
        
    def run_cli(self, conn, addr):
        with conn:
            print('Connected by ', addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                
                conn.sendall(data)    
        
    def get_connections(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.sock.bind((self.hostIP, self.port))
        self.sock.listen()
        while self.run_server:
            with ThreadPoolExecutor(10) as executor:
                conn, addr = self.sock.accept()
                executor.submit(self.run_cli, conn, addr)        

class BLUE_CLIENT:
    def __init__(self, client_name, ServerIP, port):
        self.name = client_name
        self.IP = ServerIP
        self.port = port
        self.client()
    
    def client_send(self):
        pass
        
    def client(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.IP, self.port))
            sock.sendall(b"Hello, world")
            data = sock.recv(1024)
            
            print(repr(data))