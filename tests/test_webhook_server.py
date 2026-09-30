import unittest
import json
import threading
import urllib.request
import urllib.error
from webhook_server import WebhookHandler, create_server

class TestWebhookServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Bind to port 0 to get an ephemeral OS-assigned free port
        cls.server = create_server("127.0.0.1", 0)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_health_check_endpoint(self):
        url = f"http://127.0.0.1:{self.port}/health"
        with urllib.request.urlopen(url) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data["status"], "healthy")
            self.assertEqual(data["service"], "tele-editorial-bot")

    def test_not_found_endpoint(self):
        url = f"http://127.0.0.1:{self.port}/nonexistent"
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(url)
        self.assertEqual(ctx.exception.code, 404)

    def test_webhook_valid_payload(self):
        url = f"http://127.0.0.1:{self.port}/webhook"
        payload = json.dumps({"update_id": 1001, "message": {"text": "hello"}}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertTrue(data["ok"])

    def test_webhook_invalid_payload(self):
        url = f"http://127.0.0.1:{self.port}/webhook"
        req = urllib.request.Request(url, data=b"not-json-content", headers={"Content-Type": "text/plain"})
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req)
        self.assertEqual(ctx.exception.code, 400)

    def test_verify_hmac_sha256(self):
        import hmac
        import hashlib
        from webhook_server import verify_hmac_sha256

        secret = "my-secret-key-123"
        payload = b'{"event": "ping"}'
        sig = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()

        self.assertTrue(verify_hmac_sha256(payload, sig, secret))
        self.assertTrue(verify_hmac_sha256(payload, f"sha256={sig}", secret))
        self.assertFalse(verify_hmac_sha256(payload, "invalid_sig", secret))
        self.assertFalse(verify_hmac_sha256(payload, sig, "wrong_secret"))
        self.assertFalse(verify_hmac_sha256(payload, "", secret))

if __name__ == "__main__":
    unittest.main()
