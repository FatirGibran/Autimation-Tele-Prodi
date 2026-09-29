import os
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from config import settings

logger = logging.getLogger("WebhookServer")

class WebhookHandler(BaseHTTPRequestHandler):
    secret_token: str = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")

    def log_message(self, format, *args):
        # Delegate to standard logging
        logger.info("%s - - [%s] %s", self.address_string(), self.log_date_time_string(), format % args)

    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy", "service": "tele-editorial-bot"}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "not found"}')

    def do_POST(self):
        if self.path == "/webhook":
            # Verify secret token if configured
            if self.secret_token:
                incoming_token = self.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
                if incoming_token != self.secret_token:
                    self.send_response(403)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(b'{"error": "forbidden", "message": "invalid secret token"}')
                    return

            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)

            # Validate that body is valid JSON
            try:
                if post_data:
                    json.loads(post_data.decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"error": "bad request", "message": "invalid json payload"}')
                return

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok": true}')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "not found"}')

def create_server(host: str = "", port: int = 8080, handler_class=WebhookHandler) -> HTTPServer:
    return HTTPServer((host, port), handler_class)

def run_server(port: int = 8080):
    httpd = create_server("", port)
    print(f"Webhook & health server running on port {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down webhook server gracefully...")
        httpd.server_close()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    run_server(port)
