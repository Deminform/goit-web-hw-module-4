import concurrent.futures
import json
import mimetypes
import os
import pathlib
import socket
import urllib.parse
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == "/":
            self.send_html_file("html_files/index.html")
        elif pr_url.path == "/message":
            self.send_html_file("html_files/message.html")
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file("html_files/error.html", 404)

    def do_POST(self):
        data = self.rfile.read(int(self.headers["Content-Length"]))
        self.send_by_udp(data)
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(f".{self.path}", "rb") as file:
            self.wfile.write(file.read())

    @staticmethod
    def send_by_udp(data, ip="localhost", port=5000, chunk_size=1024):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server = ip, port
        for i in range(0, len(data), chunk_size):
            chunk = data[i : i + chunk_size]
            sock.sendto(chunk, server)
        response, address = sock.recvfrom(chunk_size)
        print(f'Recorded: "{response.decode()}" | from UDP server: {address}')
        sock.close()


def udp_server(ip="localhost", port=5000):
    print(f"Starting UDP server on {ip}:{port}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    sock.bind(server)
    try:
        print(f"UDP server on {ip}:{port}")
        while True:
            data_buffer = []
            while True:
                data, address = sock.recvfrom(1024)
                if not data:
                    break
                data_buffer.append(data)
                if len(data) < 1024:
                    break
            full_data = b"".join(data_buffer).decode()
            result = urllib.parse.unquote_plus(full_data)
            data_dict = {
                key: value
                for key, value in [el.split("=", 1) for el in result.split("&", 1)]
            }
            status = add_json_record("./storage/data.json", data_dict)
            sock.sendto(str(status).encode(), address)
            print(f'Record is: "{data_dict}" | recorded: "{status}"')
    except KeyboardInterrupt:
        print(f"Destroy server")
    finally:
        sock.close()


def add_json_record(filename, data):
    records = {}
    try:
        if os.path.getsize(filename) != 0:
            with open(filename, "r", encoding="utf-8") as file:
                records.update(json.load(file))

        with open(filename, "r+", encoding="utf-8") as file_path:
            records.update({str(datetime.today()): data})
            json.dump(records, file_path, ensure_ascii=False, indent=4)

        return True
    except FileNotFoundError as msg:
        return msg


def http_server(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ("localhost", 3000)
    http = server_class(server_address, handler_class)
    print(f"Starting HTTP server on {server_address[0]}:{server_address[1]}")
    try:
        http.serve_forever()
        print("Server loop running")
    except KeyboardInterrupt:
        http.server_close()


if __name__ == "__main__":
    methods = [http_server, udp_server]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        for method in methods:
            executor.submit(method)
