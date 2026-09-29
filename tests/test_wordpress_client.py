import unittest
from unittest.mock import patch, MagicMock
from wordpress_client import WordPressClient

class TestWordPressClient(unittest.TestCase):
    def setUp(self):
        self.client = WordPressClient(
            api_url="https://bif-pwt.telkomuniversity.ac.id/wp-json/wp/v2",
            username="editor",
            app_password="secretpassword"
        )

    @patch("urllib.request.urlopen")
    def test_create_post_success(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"id": 1234, "status": "draft", "slug": "test-slug"}'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        res = self.client.create_post(
            title="Judul Test",
            content="<p>Konten</p>",
            slug="test-slug",
            yoast_meta={"focus_keyphrase": "keyphrase", "seo_title": "Title", "meta_description": "Desc"}
        )
        self.assertEqual(res["id"], 1234)
        self.assertEqual(res["status"], "draft")

    def test_auth_headers_generation(self):
        headers = self.client._get_headers()
        self.assertIn("Authorization", headers)
        self.assertTrue(headers["Authorization"].startswith("Basic "))
        self.assertEqual(headers["Content-Type"], "application/json")

    @patch("urllib.request.urlopen")
    def test_get_post_success(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"id": 4321, "title": {"rendered": "Fetched"}}'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        res = self.client.get_post(4321)
        self.assertEqual(res["id"], 4321)
        self.assertEqual(res["title"]["rendered"], "Fetched")

    @patch("time.sleep")
    @patch("urllib.request.urlopen")
    def test_retry_on_server_error(self, mock_urlopen, mock_sleep):
        import urllib.error
        from io import BytesIO

        err_response = urllib.error.HTTPError("url", 500, "Internal Error", {}, BytesIO(b"error"))
        success_response = MagicMock()
        success_response.read.return_value = b'{"id": 999}'

        # Fails once with 500, then succeeds
        mock_urlopen.side_effect = [err_response, MagicMock(__enter__=MagicMock(return_value=success_response))]

        client = WordPressClient(
            api_url="https://bif-pwt.telkomuniversity.ac.id/wp-json/wp/v2",
            username="editor",
            app_password="secretpassword",
            max_retries=2,
            retry_delay=0.01
        )
        res = client.get_post(999)
        self.assertEqual(res["id"], 999)
        self.assertEqual(mock_urlopen.call_count, 2)
        mock_sleep.assert_called_once()

if __name__ == "__main__":
    unittest.main()
