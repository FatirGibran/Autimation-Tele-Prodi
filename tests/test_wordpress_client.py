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

    @patch("urllib.request.urlopen")
    def test_get_or_create_category_existing(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'[{"id": 42, "name": "Artificial Intelligence"}]'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        cat_id = self.client.get_or_create_category("Artificial Intelligence")
        self.assertEqual(cat_id, 42)

    @patch("urllib.request.urlopen")
    def test_get_or_create_tag_new(self, mock_urlopen):
        # 1st call (search): returns empty list [], 2nd call (post): returns created tag {"id": 88}
        search_resp = MagicMock()
        search_resp.read.return_value = b'[]'
        create_resp = MagicMock()
        create_resp.read.return_value = b'{"id": 88, "name": "wasm"}'

        mock_urlopen.side_effect = [
            MagicMock(__enter__=MagicMock(return_value=search_resp)),
            MagicMock(__enter__=MagicMock(return_value=create_resp))
        ]

        tag_id = self.client.get_or_create_tag("wasm")
        self.assertEqual(tag_id, 88)

    @patch("urllib.request.urlopen")
    def test_update_post(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"id": 123, "title": {"rendered": "Updated Title"}}'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        res = self.client.update_post(123, {"title": "Updated Title"})
        self.assertEqual(res["id"], 123)
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.get_method(), "POST")
        self.assertIn("/posts/123", req.full_url)

    @patch("urllib.request.urlopen")
    def test_delete_post(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"id": 123, "status": "trash"}'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        res = self.client.delete_post(123, force=False)
        self.assertEqual(res["status"], "trash")
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.get_method(), "DELETE")
        self.assertIn("force=false", req.full_url)

    @patch("urllib.request.urlopen")
    def test_upload_media(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"id": 555, "source_url": "https://example.com/pic.jpg"}'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        res = self.client.upload_media(b"binary_image_data", "pic.jpg", "image/jpeg")
        self.assertEqual(res["id"], 555)
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.get_method(), "POST")
        self.assertEqual(req.headers.get("Content-type"), "image/jpeg")

    @patch("urllib.request.urlopen")
    def test_check_connection_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"id": 1, "name": "Admin User", "slug": "admin"}'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        status = self.client.check_connection()
        self.assertTrue(status["ok"])
        self.assertEqual(status["user_id"], 1)
        self.assertEqual(status["username"], "admin")

    @patch("urllib.request.urlopen")
    def test_check_connection_failure(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("Connection refused")

        status = self.client.check_connection()
        self.assertFalse(status["ok"])
        self.assertIn("Connection refused", status["error"])

    @patch.object(WordPressClient, "update_post")
    def test_batch_update_post_status(self, mock_update):
        def side_effect(pid, updates):
            if pid == 102:
                raise RuntimeError("Post not found")
            return {"id": pid, "status": updates["status"]}

        mock_update.side_effect = side_effect

        result = self.client.batch_update_post_status([101, 102], "publish")
        self.assertEqual(result["total"], 2)
        self.assertEqual(result["succeeded"], [101])
        self.assertEqual(len(result["failed"]), 1)
        self.assertEqual(result["failed"][0]["id"], 102)
        self.assertFalse(result["all_success"])

if __name__ == "__main__":
    unittest.main()

