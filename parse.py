import socket
import json
import sys
import requests
import logging
import configparser
import os

class ApiParser:
    def __init__(self, api_ip: str, api_port: int = 4028):
        self.api_ip = api_ip
        self.api_port = api_port

    def connect(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.api_ip, self.api_port))

    def disconnect(self):
        self.s.close()

    def send_command(self, command: str, parameter: str = None):
        command_data = {"command": command, "parameter": parameter} if parameter else {"command": command}
        self.s.send(json.dumps(command_data).encode('utf-8'))

    def receive_response(self) -> dict:
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


def load_config(config_file='config/config.ini'):
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), config_file)

    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    config.read(config_path)

    influxdb_url = config.get('InfluxDB', 'url')
    bucket = config.get('InfluxDB', 'bucket')
    org = config.get('InfluxDB', 'org')
    token = config.get('InfluxDB', 'token')

    return influxdb_url, bucket, org, token
def process_ips(filename: str, influxdb_url: str, bucket: str, org: str, token: str):
    with open(filename, 'r') as file:
        ips = [line.strip() for line in file.readlines()]

    api_port = 4028

    for ip in ips:
        api_parser = ApiParser(api_ip=ip, api_port=api_port)
        response = None
        try:
            api_parser.connect()
            api_parser.send_command('summary', ip)
            response = api_parser.receive_response()
        except ConnectionRefusedError as e:
            logging.error(f"Error for {ip}: {e}")
        finally:
            api_parser.disconnect()

        logging.info(f"Result for {ip}: {response}")

        # Send data to InfluxDB
        send_to_influxdb(influxdb_url, bucket, org, token, ip, response)

def send_to_influxdb(influxdb_url: str, bucket: str, org: str, token: str, ip: str, data: dict):
    url = f"{influxdb_url}/api/v2/write?org={org}&bucket={bucket}&precision=s"
    headers = {"Authorization": f"Token {token}"}

    # Add InfluxDB tag to the data
    tags = f"Antminer=L7"

    # Extract fields and values
    fields = []
    for key, value in data.items():
        if isinstance(value, (int, float, str)):
            fields.append(f"{key}={json.dumps(value)}")

    payload = f"mining_data,ip={ip},{tags} {','.join(fields)}"

    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        print(f"Data sent to InfluxDB for {ip}")
        #print(f"InfluxDB Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending data to InfluxDB for {ip}: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) < 2:
        print("Usage: python parser.py filename.txt")
        sys.exit(1)

    # Load configuration from file
    influxdb_url, bucket, org, token = load_config()

    filename = sys.argv[1]
    process_ips(filename, influxdb_url, bucket, org, token)
