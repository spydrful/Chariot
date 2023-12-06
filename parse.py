import socket
import json
import sys

class ApiParser:
    def __init__(self, api_ip, api_port=4028):
        self.api_ip = api_ip
        self.api_port = api_port

    def connect(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.api_ip, self.api_port))

    def disconnect(self):
        self.s.close()

    def send_command(self, command, parameter=None):
        command_data = {"command": command, "parameter": parameter} if parameter else {"command": command}
        self.s.send(json.dumps(command_data).encode('utf-8'))

    def receive_response(self):
        response = self.linesplit(self.s)
        response = response.replace(b'\x00', b'').decode('utf-8')
        return json.loads(response)

    def linesplit(self, socket):
        buffer = socket.recv(4096)
        done = False
        while not done:
            more = socket.recv(4096)
            if not more:
                done = True
            else:
                buffer = buffer + more
        if buffer:
            return buffer

def process_ips(filename):
    with open(filename, 'r') as file:
        ips = [line.strip() for line in file.readlines()]

    api_port = 4028

    for ip in ips:
        api_parser = ApiParser(api_ip=ip, api_port=api_port)  # Set api_ip dynamically
        response = None  # Initialize response variable
        try:
            api_parser.connect()
            api_parser.send_command('summary', ip)
            response = api_parser.receive_response()
        except ConnectionRefusedError as e:
            print(f"Error for {ip}: {e}")
        finally:
            api_parser.disconnect()

        print(f"Result for {ip}: {response}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py filename.txt")
        sys.exit(1)

    filename = sys.argv[1]
    process_ips(filename)
