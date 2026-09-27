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

if __name__ == "__main__":
    unittest.main()
