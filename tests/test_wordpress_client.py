import json
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

    @patch("urllib.request.urlopen")
    def test_get_post_revisions(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'[{"id": 55, "author": 1, "date": "2026-10-01T12:00:00"}]'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        revisions = self.client.get_post_revisions(123)
        self.assertEqual(len(revisions), 1)
        self.assertEqual(revisions[0]["id"], 55)

    @patch.object(WordPressClient, "update_post")
    def test_schedule_post(self, mock_update):
        mock_update.return_value = {"id": 123, "status": "future", "date": "2026-10-15T08:00:00"}

        res = self.client.schedule_post(123, "2026-10-15T08:00:00")
        mock_update.assert_called_once_with(123, {"status": "future", "date": "2026-10-15T08:00:00"})
        self.assertEqual(res["status"], "future")

    @patch.object(WordPressClient, "get_or_create_tag")
    @patch.object(WordPressClient, "update_post")
    def test_assign_post_tags(self, mock_update, mock_get_tag):
        mock_get_tag.side_effect = lambda t: 10 if t == "ai" else 20
        mock_update.return_value = {"id": 123, "tags": [10, 20]}

        res = self.client.assign_post_tags(123, ["ai", "iot"])
        mock_update.assert_called_once_with(123, {"tags": [10, 20]})
        self.assertEqual(res["tags"], [10, 20])

    @patch("urllib.request.urlopen")
    def test_update_media_metadata(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"id": 44, "alt_text": "Diagram", "caption": "Gambar 1"}'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        res = self.client.update_media_metadata(44, alt_text="Diagram", caption="Gambar 1")
        self.assertEqual(res["id"], 44)
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.get_method(), "POST")
        self.assertIn("/media/44", req.full_url)
        body = json.loads(req.data.decode("utf-8"))
        self.assertEqual(body["alt_text"], "Diagram")
        self.assertEqual(body["caption"], "Gambar 1")

    @patch.object(WordPressClient, "update_post")
    def test_set_post_visibility(self, mock_update):
        mock_update.return_value = {"id": 101, "sticky": True, "password": "pass"}
        res = self.client.set_post_visibility(101, sticky=True, password="pass")
        mock_update.assert_called_once_with(101, {"sticky": True, "password": "pass"})
        self.assertTrue(res["sticky"])

    @patch("urllib.request.urlopen")
    def test_delete_media(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"deleted": true, "previous": {"id": 55}}'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        res = self.client.delete_media(55, force=True)
        self.assertTrue(res["deleted"])
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.get_method(), "DELETE")
        self.assertIn("/media/55?force=true", req.full_url)

    @patch.object(WordPressClient, "update_post")
    def test_update_post_excerpt(self, mock_update):
        mock_update.return_value = {"id": 105, "excerpt": "Ringkasan kurikulum baru."}
        res = self.client.update_post_excerpt(105, "Ringkasan kurikulum baru.")
        mock_update.assert_called_once_with(105, {"excerpt": "Ringkasan kurikulum baru."})
        self.assertEqual(res["excerpt"], "Ringkasan kurikulum baru.")

    @patch.object(WordPressClient, "update_post")
    def test_set_post_comment_status(self, mock_update):
        mock_update.return_value = {"id": 106, "comment_status": "open", "ping_status": "closed"}
        res = self.client.set_post_comment_status(106, allow_comments=True, allow_pings=False)
        mock_update.assert_called_once_with(106, {"comment_status": "open", "ping_status": "closed"})
        self.assertEqual(res["comment_status"], "open")
        self.assertEqual(res["ping_status"], "closed")

    @patch.object(WordPressClient, "update_post")
    def test_toggle_post_sticky(self, mock_update):
        mock_update.return_value = {"id": 107, "sticky": True}
        res = self.client.toggle_post_sticky(107, True)
        mock_update.assert_called_once_with(107, {"sticky": True})
        self.assertTrue(res["sticky"])

    @patch("urllib.request.urlopen")
    def test_list_media_by_mime_type(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'[{"id": 1, "mime_type": "image/jpeg"}, {"id": 2, "mime_type": "application/pdf"}]'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        # Filter image/
        images = self.client.list_media_by_mime_type(mime_prefix="image/")
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0]["id"], 1)

        # No filter
        mock_resp.read.return_value = b'[{"id": 1, "mime_type": "image/jpeg"}, {"id": 2, "mime_type": "application/pdf"}]'
        all_media = self.client.list_media_by_mime_type(mime_prefix="")
        self.assertEqual(len(all_media), 2)

    @patch.object(WordPressClient, "delete_post")
    def test_batch_trash_posts(self, mock_delete):
        def side_effect(pid, force=False):
            if pid == 102:
                raise RuntimeError("Post 102 not found")
            return {"deleted": True, "id": pid}

        mock_delete.side_effect = side_effect
        res = self.client.batch_trash_posts([101, 102, 103], force=False)
        self.assertEqual(res["total"], 3)
        self.assertEqual(res["success"], [101, 103])
        self.assertEqual(len(res["failed"]), 1)
        self.assertEqual(res["failed"][0]["post_id"], 102)

    @patch("urllib.request.urlopen")
    def test_get_media_by_slug(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'[{"id": 42, "slug": "telkom-header", "source_url": "https://bif.telkom.ac.id/header.jpg"}]'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        media = self.client.get_media_by_slug("telkom-header")
        self.assertIsNotNone(media)
        self.assertEqual(media["id"], 42)
        self.assertEqual(media["slug"], "telkom-header")

        # Not found test
        mock_resp.read.return_value = b'[]'
        not_found = self.client.get_media_by_slug("non-existent")
        self.assertIsNone(not_found)

    @patch.object(WordPressClient, "update_post")
    def test_batch_update_post_categories(self, mock_update):
        def side_effect(pid, updates):
            if pid == 202:
                raise RuntimeError("Failed to update post 202")
            return {"id": pid, "categories": updates["categories"]}

        mock_update.side_effect = side_effect
        res = self.client.batch_update_post_categories([201, 202, 203], [5, 12])
        self.assertEqual(res["total"], 3)
        self.assertEqual(res["success"], [201, 203])
        self.assertEqual(len(res["failed"]), 1)
        self.assertEqual(res["failed"][0]["post_id"], 202)

    @patch("urllib.request.urlopen")
    def test_get_user_by_slug(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'[{"id": 7, "slug": "fatir-gibran", "name": "Fatir Gibran"}]'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        user = self.client.get_user_by_slug("fatir-gibran")
        self.assertIsNotNone(user)
        self.assertEqual(user["id"], 7)
        self.assertEqual(user["name"], "Fatir Gibran")

        # Not found test
        mock_resp.read.return_value = b'[]'
        not_found = self.client.get_user_by_slug("ghost-user")
        self.assertIsNone(not_found)

    @patch.object(WordPressClient, "update_post")
    def test_batch_update_post_tags(self, mock_update):
        def side_effect(pid, updates):
            if pid == 302:
                raise RuntimeError("Failed to update post 302")
            return {"id": pid, "tags": updates["tags"]}

        mock_update.side_effect = side_effect
        res = self.client.batch_update_post_tags([301, 302, 303], [14, 28])
        self.assertEqual(res["total"], 3)
        self.assertEqual(res["success"], [301, 303])
        self.assertEqual(len(res["failed"]), 1)
        self.assertEqual(res["failed"][0]["post_id"], 302)

    @patch("urllib.request.urlopen")
    def test_get_tag_by_slug(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'[{"id": 99, "slug": "kurikulum-merdeka", "name": "Kurikulum Merdeka"}]'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        tag = self.client.get_tag_by_slug("kurikulum-merdeka")
        self.assertIsNotNone(tag)
        self.assertEqual(tag["id"], 99)
        self.assertEqual(tag["name"], "Kurikulum Merdeka")

        # Not found test
        mock_resp.read.return_value = b'[]'
        not_found = self.client.get_tag_by_slug("tag-tidak-ada")
        self.assertIsNone(not_found)

    @patch("urllib.request.urlopen")
    def test_get_categories_by_parent(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'[{"id": 12, "name": "Praktikum Jaringan", "parent": 5}, {"id": 13, "name": "Praktikum Sinyal", "parent": 5}]'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        cats = self.client.get_categories_by_parent(5)
        self.assertEqual(len(cats), 2)
        self.assertEqual(cats[0]["name"], "Praktikum Jaringan")
        req = mock_urlopen.call_args[0][0]
        self.assertIn("/categories?parent=5&per_page=100", req.full_url)

    @patch("urllib.request.urlopen")
    def test_ping_api_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"id": 1, "name": "Admin Telematika", "slug": "admin"}'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        res = self.client.ping_api()
        self.assertEqual(res["status"], "ok")
        self.assertTrue(res["authenticated"])
        self.assertEqual(res["user_id"], 1)
        self.assertEqual(res["username"], "Admin Telematika")
        self.assertIn("latency_ms", res)

    @patch("urllib.request.urlopen")
    def test_ping_api_failure(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("Connection refused to WordPress host")

        res = self.client.ping_api()
        self.assertEqual(res["status"], "error")
        self.assertFalse(res["authenticated"])
        self.assertIn("Connection refused", res["error"])
        self.assertIn("latency_ms", res)

    @patch("urllib.request.urlopen")
    def test_get_media_by_id_found(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"id": 88, "title": {"rendered": "Bagan Kurikulum"}, "source_url": "https://example.com/bagan.png"}'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        media = self.client.get_media_by_id(88)
        self.assertIsNotNone(media)
        self.assertEqual(media["id"], 88)
        self.assertEqual(media["source_url"], "https://example.com/bagan.png")
        req = mock_urlopen.call_args[0][0]
        self.assertIn("/media/88", req.full_url)

    @patch("urllib.request.urlopen")
    def test_get_media_by_id_not_found(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("HTTP Error 404: Not Found")

        media = self.client.get_media_by_id(9999)
        self.assertIsNone(media)

    @patch("urllib.request.urlopen")
    def test_get_site_settings(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"title": "Prodi Teknik Telekomunikasi", "description": "Website Resmi", "timezone_string": "Asia/Jakarta"}'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        settings = self.client.get_site_settings()
        self.assertEqual(settings["title"], "Prodi Teknik Telekomunikasi")
        self.assertEqual(settings["timezone_string"], "Asia/Jakarta")
        req = mock_urlopen.call_args[0][0]
        self.assertIn("/settings", req.full_url)

    @patch("urllib.request.urlopen")
    def test_get_comments_by_post_id(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'[{"id": 10, "post": 101, "content": {"rendered": "Bagus sekali"}, "status": "approved"}]'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        comments = self.client.get_comments_by_post_id(101)
        self.assertEqual(len(comments), 1)
        self.assertEqual(comments[0]["id"], 10)
        self.assertEqual(comments[0]["post"], 101)
        req = mock_urlopen.call_args[0][0]
        self.assertIn("/comments?post=101&status=approved&per_page=100", req.full_url)

    @patch("urllib.request.urlopen")
    def test_create_tag(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"id": 42, "name": "5G NR", "slug": "5g-nr", "description": "Standar seluler 5G"}'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        tag = self.client.create_tag("5G NR", slug="5g-nr", description="Standar seluler 5G")
        self.assertEqual(tag["id"], 42)
        self.assertEqual(tag["name"], "5G NR")
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.get_method(), "POST")
        self.assertIn("/tags", req.full_url)

    @patch("urllib.request.urlopen")
    def test_get_posts_by_author(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'[{"id": 101, "author": 5, "title": {"rendered": "Penelitian Telekomunikasi"}}]'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        posts = self.client.get_posts_by_author(5, per_page=5, status="publish")
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]["id"], 101)
        self.assertEqual(posts[0]["author"], 5)
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.get_method(), "GET")
        self.assertIn("/posts?author=5&per_page=5&status=publish", req.full_url)

    @patch("urllib.request.urlopen")
    def test_delete_tag(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"deleted": true, "previous": {"id": 42, "name": "5G NR"}}'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        res = self.client.delete_tag(42, force=True)
        self.assertTrue(res["deleted"])
        self.assertEqual(res["previous"]["id"], 42)
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.get_method(), "DELETE")
        self.assertIn("/tags/42?force=true", req.full_url)

    @patch("urllib.request.urlopen")
    def test_search_media(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'[{"id": 55, "title": {"rendered": "Bagan Akreditasi"}, "source_url": "https://example.com/bagan.jpg"}]'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        media_items = self.client.search_media("akreditasi", per_page=5)
        self.assertEqual(len(media_items), 1)
        self.assertEqual(media_items[0]["id"], 55)
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.get_method(), "GET")
        self.assertIn("/media?search=akreditasi&per_page=5", req.full_url)

    @patch("urllib.request.urlopen")
    def test_update_comment_status(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"id": 88, "status": "approved"}'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        res = self.client.update_comment_status(88, status="approved")
        self.assertEqual(res["id"], 88)
        self.assertEqual(res["status"], "approved")
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.get_method(), "POST")
        self.assertIn("/comments/88", req.full_url)

    @patch("urllib.request.urlopen")
    def test_get_categories_with_counts(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'[{"id": 10, "name": "Telekomunikasi", "count": 15}, {"id": 11, "name": "IoT", "count": 8}]'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        categories = self.client.get_categories_with_counts(hide_empty=True, per_page=50)
        self.assertEqual(len(categories), 2)
        self.assertEqual(categories[0]["count"], 15)
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.get_method(), "GET")
        self.assertIn("/categories?hide_empty=true&per_page=50", req.full_url)

    @patch("urllib.request.urlopen")
    def test_get_users_by_role(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'[{"id": 3, "name": "Dr. Budi", "roles": ["author"]}]'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        users = self.client.get_users_by_role(role="author", per_page=20)
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]["name"], "Dr. Budi")
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.get_method(), "GET")
        self.assertIn("/users?roles=author&per_page=20", req.full_url)

    @patch("urllib.request.urlopen")
    def test_bulk_trash_posts(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"id": 101, "status": "trash"}'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        res = self.client.bulk_trash_posts([101, 102])
        self.assertEqual(res["total_requested"], 2)
        self.assertEqual(res["trashed_count"], 2)
        self.assertEqual(res["trashed_ids"], [101, 102])
        self.assertEqual(res["failed_count"], 0)

    @patch("urllib.request.urlopen")
    def test_get_site_settings(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"title": "S1 Teknik Telekomunikasi", "description": "Website Resmi Prodi", "timezone": "Asia/Jakarta"}'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        settings = self.client.get_site_settings()
        self.assertEqual(settings["title"], "S1 Teknik Telekomunikasi")
        self.assertEqual(settings["timezone"], "Asia/Jakarta")
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.get_method(), "GET")
        self.assertIn("/settings", req.full_url)

    @patch("urllib.request.urlopen")
    def test_get_post_media_attachments(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'[{"id": 401, "source_url": "https://example.com/antenna.jpg", "media_type": "image"}]'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        media = self.client.get_post_media_attachments(post_id=999, per_page=10)
        self.assertEqual(len(media), 1)
        self.assertEqual(media[0]["id"], 401)
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.get_method(), "GET")
        self.assertIn("/media?parent=999&per_page=10", req.full_url)

    @patch("urllib.request.urlopen")
    def test_set_post_sticky_status(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"id": 888, "sticky": true}'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        res = self.client.set_post_sticky_status(post_id=888, is_sticky=True)
        self.assertEqual(res["id"], 888)
        self.assertTrue(res["sticky"])
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.get_method(), "POST")
        self.assertIn("/posts/888", req.full_url)

    @patch("urllib.request.urlopen")
    def test_get_posts_by_status(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'[{"id": 201, "title": {"rendered": "Draf Riset Satelit"}, "status": "draft"}]'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        posts = self.client.get_posts_by_status(status="draft", page=2, per_page=10)
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]["id"], 201)
        self.assertEqual(posts[0]["status"], "draft")
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.get_method(), "GET")
        self.assertIn("/posts?status=draft&page=2&per_page=10", req.full_url)

    @patch("urllib.request.urlopen")
    def test_duplicate_post_as_draft(self, mock_urlopen):
        mock_get_resp = MagicMock()
        mock_get_resp.read.return_value = b'{"id": 105, "title": {"rendered": "Panduan Praktikum Antena"}, "content": {"rendered": "<p>Modul 1</p>"}, "categories": [1, 2], "tags": [3]}'

        mock_post_resp = MagicMock()
        mock_post_resp.read.return_value = b'{"id": 106, "title": {"rendered": "Panduan Praktikum Antena (Salinan)"}, "status": "draft"}'

        mock_urlopen.side_effect = [
            MagicMock(__enter__=MagicMock(return_value=mock_get_resp)),
            MagicMock(__enter__=MagicMock(return_value=mock_post_resp))
        ]

        cloned = self.client.duplicate_post_as_draft(post_id=105, title_suffix=" (Salinan)")
        self.assertEqual(cloned["id"], 106)
        self.assertIn("Salinan", cloned["title"]["rendered"])
        self.assertEqual(mock_urlopen.call_count, 2)



if __name__ == "__main__":
    unittest.main()







