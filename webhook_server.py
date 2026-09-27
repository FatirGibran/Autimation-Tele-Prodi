import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from config import settings

class WebhookHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy", "service": "tele-editorial-bot"}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/webhook":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            
            # Acknowledge Telegram webhook quickly
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok": true}')
        else:
            self.send_response(404)
            self.end_headers()

def run_server(port: int = 8080):
    server_address = ("", port)
    httpd = HTTPServer(server_address, WebhookHandler)
    print(f"Webhook & health server running on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    run_server(port)
