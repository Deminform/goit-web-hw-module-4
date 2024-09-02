import mimetypes
import pathlib
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('html_files/index.html')
        elif pr_url.path == '/message':
            self.send_html_file('html_files/message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('html_files/error.html', 404)

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        self.send_by_udp(data)
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())

    @staticmethod
    def send_by_udp(data, ip='localhost', port=5000, chunk_size=1024):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server = ip, port
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            sock.sendto(chunk, server)
        response, address = sock.recvfrom(chunk_size)
        print(f'Recorded: "{response.decode()}" | from UDP server: {address}')
        sock.close()


def http_server(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == '__main__':
    http_server()


