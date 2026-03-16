from http.server import HTTPServer, BaseHTTPRequestHandler

HOST = "127.0.0.1"
PORT = 5005

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/ping":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"pong")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *args):
        return

def run():
    server = HTTPServer((HOST, PORT), SimpleHandler)
    print(f"Server running on http://{HOST}:{PORT}")
    server.serve_forever()

if __name__ == "__main__":
    run()
