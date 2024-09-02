import json
import socket
import urllib.parse
from datetime import datetime


def udp_server(ip='localhost', port=5000):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    sock.bind(server)
    try:
        while True:
            data_buffer = []
            while True:
                data, address = sock.recvfrom(1024)
                if not data:
                    break
                data_buffer.append(data)
                if len(data) < 1024:
                    break
            full_data = b''.join(data_buffer).decode()
            result = urllib.parse.unquote_plus(full_data)
            data_dict = {key: value for key, value in [el.split('=', 1) for el in result.split('&', 1)]}
            status = add_json_record('./storage/data.json', data_dict)
            sock.sendto(str(status).encode(), address)
            print(f'Record is: "{data_dict}" | recorded: "{status}"')
    except KeyboardInterrupt:
        print(f'Destroy server')
    finally:
        sock.close()


def add_json_record(filename, data):
    records = {}
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            records.update(json.load(file))
    except FileNotFoundError as msg:
        return msg
    else:
        with open(filename, 'r+', encoding='utf-8') as file_path:
            records.update({str(datetime.today()): data})
            json.dump(records, file_path, ensure_ascii=False, indent=4)
        return True


if __name__ == '__main__':
    udp_server()
