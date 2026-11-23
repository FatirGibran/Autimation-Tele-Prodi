import base64
import json
import logging
import time
import urllib.request
import urllib.error
import urllib.parse
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class WordPressClient:
    def __init__(
        self,
        api_url: str,
        username: str,
        app_password: str,
        max_retries: int = 3,
        retry_delay: float = 0.5
    ):
        self.api_url = api_url.rstrip("/")
        self.username = username
        self.app_password = app_password
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def _get_headers(self) -> Dict[str, str]:
        auth_str = f"{self.username}:{self.app_password}"
        b64_auth = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")
        return {
            "Authorization": f"Basic {b64_auth}",
            "Content-Type": "application/json",
            "User-Agent": "TelkomPurwokertoEditorialBot/1.0"
        }

    def _send_request(self, req: urllib.request.Request) -> Dict[str, Any]:
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    response_data = resp.read().decode("utf-8")
                    return json.loads(response_data)
            except urllib.error.HTTPError as e:
                # 4xx client errors should not be retried
                if 400 <= e.code < 500:
                    error_body = e.read().decode("utf-8")
                    raise RuntimeError(f"WordPress API error HTTP {e.code}: {error_body}")
                last_exception = e
            except urllib.error.URLError as e:
                last_exception = e

            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay * (2 ** attempt))

        raise RuntimeError(f"WordPress API request failed after {self.max_retries} attempts: {last_exception}")

    def create_post(
        self,
        title: str,
        content: str,
        slug: str,
        status: str = "draft",
        categories: Optional[list] = None,
        yoast_meta: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        endpoint = f"{self.api_url}/posts"
        payload: Dict[str, Any] = {
            "title": title,
            "content": content,
            "slug": slug,
            "status": status,
        }
        if categories:
            payload["categories"] = categories

        if yoast_meta:
            payload["meta"] = {
                "_yoast_wpseo_focuskw": yoast_meta.get("focus_keyphrase", ""),
                "_yoast_wpseo_title": yoast_meta.get("seo_title", ""),
                "_yoast_wpseo_metadesc": yoast_meta.get("meta_description", ""),
            }

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            endpoint,
            data=data_bytes,
            headers=self._get_headers(),
            method="POST"
        )
        return self._send_request(req)

    def get_post(self, post_id: int) -> Dict[str, Any]:
        endpoint = f"{self.api_url}/posts/{post_id}"
        req = urllib.request.Request(
            endpoint,
            headers=self._get_headers(),
            method="GET"
        )
        return self._send_request(req)

    def get_or_create_category(self, name: str) -> int:
        clean_name = name.strip()
        encoded = urllib.parse.quote(clean_name)
        endpoint = f"{self.api_url}/categories?search={encoded}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        results = self._send_request(req)
        if isinstance(results, list):
            for cat in results:
                if cat.get("name", "").strip().lower() == clean_name.lower():
                    return cat["id"]

        create_endpoint = f"{self.api_url}/categories"
        payload = {"name": clean_name}
        data_bytes = json.dumps(payload).encode("utf-8")
        req_post = urllib.request.Request(create_endpoint, data=data_bytes, headers=self._get_headers(), method="POST")
        created = self._send_request(req_post)
        return created["id"]

    def get_or_create_tag(self, name: str) -> int:
        clean_name = name.strip()
        encoded = urllib.parse.quote(clean_name)
        endpoint = f"{self.api_url}/tags?search={encoded}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        results = self._send_request(req)
        if isinstance(results, list):
            for tag in results:
                if tag.get("name", "").strip().lower() == clean_name.lower():
                    return tag["id"]

        create_endpoint = f"{self.api_url}/tags"
        payload = {"name": clean_name}
        data_bytes = json.dumps(payload).encode("utf-8")
        req_post = urllib.request.Request(create_endpoint, data=data_bytes, headers=self._get_headers(), method="POST")
        created = self._send_request(req_post)
        return created["id"]

    def update_post(self, post_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates an existing WordPress post using PATCH/POST.
        """
        endpoint = f"{self.api_url}/posts/{post_id}"
        data_bytes = json.dumps(updates).encode("utf-8")
        req = urllib.request.Request(
            endpoint,
            data=data_bytes,
            headers=self._get_headers(),
            method="POST"
        )
        return self._send_request(req)

    def delete_post(self, post_id: int, force: bool = False) -> Dict[str, Any]:
        """
        Deletes or trashes a WordPress post via the REST API.
        """
        endpoint = f"{self.api_url}/posts/{post_id}?force={'true' if force else 'false'}"
        req = urllib.request.Request(
            endpoint,
            headers=self._get_headers(),
            method="DELETE"
        )
        return self._send_request(req)

    def upload_media(
        self,
        file_bytes: bytes,
        filename: str,
        mime_type: str = "image/jpeg",
        alt_text: str = ""
    ) -> Dict[str, Any]:
        """
        Uploads an image or document binary to the WordPress Media Library via REST API.
        """
        endpoint = f"{self.api_url}/media"
        headers = self._get_headers()
        headers["Content-Type"] = mime_type
        headers["Content-Disposition"] = f'attachment; filename="{filename}"'

        req = urllib.request.Request(
            endpoint,
            data=file_bytes,
            headers=headers,
            method="POST"
        )
        result = self._send_request(req)
        if alt_text and isinstance(result, dict) and "id" in result:
            try:
                self.update_media(result["id"], {"alt_text": alt_text})
            except Exception:
                pass
        return result

    def update_media(self, media_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates metadata or description of an uploaded media object.
        """
        endpoint = f"{self.api_url}/media/{media_id}"
        data_bytes = json.dumps(updates).encode("utf-8")
        req = urllib.request.Request(
            endpoint,
            data=data_bytes,
            headers=self._get_headers(),
            method="POST"
        )
        return self._send_request(req)

    def check_connection(self) -> Dict[str, Any]:
        """
        Pings the WordPress REST API users/me endpoint and verifies authentication status.
        """
        endpoint = f"{self.api_url}/users/me"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        try:
            data = self._send_request(req)
            return {
                "ok": True,
                "user_id": data.get("id"),
                "username": data.get("slug") or data.get("name"),
                "status_message": "Authentication successful",
            }
        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
                "status_message": "Connection or authentication failed",
            }

    def batch_update_post_status(self, post_ids: List[int], status: str) -> Dict[str, Any]:
        """
        Updates post status across multiple WordPress post IDs in batch.
        Returns aggregate result counts with lists of succeeded and failed IDs.
        """
        succeeded: List[int] = []
        failed: List[Dict[str, Any]] = []

        for pid in post_ids:
            try:
                self.update_post(pid, {"status": status})
                succeeded.append(pid)
            except Exception as e:
                failed.append({"id": pid, "error": str(e)})

        return {
            "total": len(post_ids),
            "succeeded": succeeded,
            "failed": failed,
            "all_success": len(failed) == 0,
        }

    def get_post_revisions(self, post_id: int) -> List[Dict[str, Any]]:
        """
        Retrieves remote revision history for a WordPress post.
        """
        endpoint = f"{self.api_url}/posts/{post_id}/revisions"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        results = self._send_request(req)
        return results if isinstance(results, list) else []

    def schedule_post(self, post_id: int, publish_date_iso: str) -> Dict[str, Any]:
        """
        Schedules a WordPress post for future publication by setting status to 'future' and target date.
        """
        payload = {
            "status": "future",
            "date": publish_date_iso.strip()
        }
        return self.update_post(post_id, payload)

    def assign_post_tags(self, post_id: int, tag_names: List[str]) -> Dict[str, Any]:
        """
        Resolves tag names to WordPress tag IDs and assigns them to the specified post.
        """
        tag_ids = []
        for name in tag_names:
            clean = name.strip()
            if clean:
                t_id = self.get_or_create_tag(clean)
                tag_ids.append(t_id)

        return self.update_post(post_id, {"tags": tag_ids})

    def update_media_metadata(
        self,
        media_id: int,
        alt_text: Optional[str] = None,
        caption: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Updates metadata fields (alt text, caption, description) on an existing WordPress media attachment.
        """
        endpoint = f"{self.api_url}/media/{media_id}"
        payload: Dict[str, Any] = {}
        if alt_text is not None:
            payload["alt_text"] = alt_text
        if caption is not None:
            payload["caption"] = caption
        if description is not None:
            payload["description"] = description

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            endpoint,
            data=data_bytes,
            headers=self._get_headers(),
            method="POST"
        )
        return self._send_request(req)

    def set_post_visibility(
        self,
        post_id: int,
        sticky: bool = False,
        password: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Updates sticky status and password protection on a WordPress post.
        """
        payload: Dict[str, Any] = {"sticky": sticky}
        if password is not None:
            payload["password"] = password
        return self.update_post(post_id, payload)

    def delete_media(self, media_id: int, force: bool = True) -> Dict[str, Any]:
        """
        Deletes a media item by ID. When force is True, the media is permanently deleted.
        """
        endpoint = f"{self.api_url}/media/{media_id}?force={'true' if force else 'false'}"
        req = urllib.request.Request(
            endpoint,
            headers=self._get_headers(),
            method="DELETE"
        )
        return self._send_request(req)

    def update_post_excerpt(self, post_id: int, excerpt: str) -> Dict[str, Any]:
        """
        Updates the editorial summary excerpt for a WordPress post.
        """
        return self.update_post(post_id, {"excerpt": excerpt.strip()})

    def set_post_comment_status(
        self,
        post_id: int,
        allow_comments: bool = True,
        allow_pings: bool = True
    ) -> Dict[str, Any]:
        """
        Configures comment and ping status ('open' or 'closed') on a WordPress post.
        """
        payload = {
            "comment_status": "open" if allow_comments else "closed",
            "ping_status": "open" if allow_pings else "closed"
        }
        return self.update_post(post_id, payload)

    def toggle_post_sticky(self, post_id: int, is_sticky: bool) -> Dict[str, Any]:
        """
        Toggles the sticky (pinned) attribute on a WordPress post.
        """
        return self.update_post(post_id, {"sticky": bool(is_sticky)})

    def list_media_by_mime_type(self, mime_prefix: str = "image/", per_page: int = 20) -> List[Dict[str, Any]]:
        """
        Retrieves WordPress media items filtered by media_type or MIME prefix.
        """
        endpoint = f"{self.api_url}/media?per_page={per_page}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        results = self._send_request(req)
        if not isinstance(results, list):
            return []
        if not mime_prefix:
            return results
        prefix = mime_prefix.lower()
        return [m for m in results if m.get("mime_type", "").lower().startswith(prefix)]

    def batch_trash_posts(self, post_ids: List[int], force: bool = False) -> Dict[str, Any]:
        """
        Trashes or permanently deletes a batch of WordPress posts sequentially.
        """
        success = []
        failed = []
        for pid in post_ids:
            try:
                self.delete_post(pid, force=force)
                success.append(pid)
            except Exception as e:
                failed.append({"post_id": pid, "error": str(e)})

        return {
            "success": success,
            "failed": failed,
            "total": len(post_ids)
        }

    def get_media_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single WordPress media item matching the given slug, or None if not found.
        """
        clean_slug = urllib.parse.quote(slug.strip().lower())
        endpoint = f"{self.api_url}/media?slug={clean_slug}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        results = self._send_request(req)
        if isinstance(results, list) and len(results) > 0:
            return results[0]
        return None

    def batch_update_post_categories(self, post_ids: List[int], category_ids: List[int]) -> Dict[str, Any]:
        """
        Bulk updates categories for multiple WordPress posts in batch.
        """
        success = []
        failed = []
        for pid in post_ids:
            try:
                self.update_post(pid, {"categories": category_ids})
                success.append(pid)
            except Exception as e:
                failed.append({"post_id": pid, "error": str(e)})

        return {
            "success": success,
            "failed": failed,
            "total": len(post_ids)
        }

    def get_user_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a WordPress user author matching the given slug, or None if not found.
        """
        clean_slug = urllib.parse.quote(slug.strip().lower())
        endpoint = f"{self.api_url}/users?slug={clean_slug}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        results = self._send_request(req)
        if isinstance(results, list) and len(results) > 0:
            return results[0]
        return None

    def batch_update_post_tags(self, post_ids: List[int], tag_ids: List[int]) -> Dict[str, Any]:
        """
        Bulk updates tags for multiple WordPress posts in batch.
        """
        success = []
        failed = []
        for pid in post_ids:
            try:
                self.update_post(pid, {"tags": tag_ids})
                success.append(pid)
            except Exception as e:
                failed.append({"post_id": pid, "error": str(e)})

        return {
            "success": success,
            "failed": failed,
            "total": len(post_ids)
        }

    def get_tag_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a WordPress tag matching the given slug, or None if not found.
        """
        clean_slug = urllib.parse.quote(slug.strip().lower())
        endpoint = f"{self.api_url}/tags?slug={clean_slug}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        results = self._send_request(req)
        if isinstance(results, list) and len(results) > 0:
            return results[0]
        return None

    def get_tag_by_id(self, tag_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves a WordPress tag by its numeric tag ID.
        """
        endpoint = f"{self.api_url}/tags/{int(tag_id)}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        try:
            res = self._send_request(req)
            if isinstance(res, dict) and "id" in res:
                return res
            return None
        except Exception:
            return None

    def get_categories_by_parent(self, parent_id: int) -> List[Dict[str, Any]]:
        """
        Retrieves all child categories belonging to a parent category ID.
        """
        endpoint = f"{self.api_url}/categories?parent={int(parent_id)}&per_page=100"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        results = self._send_request(req)
        if isinstance(results, list):
            return results
        return []

    def get_category_by_id(self, category_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves a WordPress category by its numeric category ID.
        """
        endpoint = f"{self.api_url}/categories/{int(category_id)}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        try:
            res = self._send_request(req)
            if isinstance(res, dict) and "id" in res:
                return res
            return None
        except Exception:
            return None

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves user/author profile details from /users/{id} endpoint by numeric user ID.
        """
        endpoint = f"{self.api_url}/users/{int(user_id)}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        try:
            res = self._send_request(req)
            if isinstance(res, dict) and "id" in res:
                return res
            return None
        except Exception:
            return None

    def ping_api(self) -> Dict[str, Any]:
        """
        Pings WordPress REST API endpoint to verify connectivity and authentication status.
        """
        endpoint = f"{self.api_url}/users/me"
        start_time = time.time()
        try:
            req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
            user_data = self._send_request(req)
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            return {
                "status": "ok",
                "authenticated": True,
                "latency_ms": elapsed_ms,
                "user_id": user_data.get("id"),
                "username": user_data.get("name") or user_data.get("slug")
            }
        except Exception as e:
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            return {
                "status": "error",
                "authenticated": False,
                "latency_ms": elapsed_ms,
                "error": str(e)
            }

    def get_media_by_id(self, media_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single WordPress media attachment by its numeric ID, or None if not found.
        """
        endpoint = f"{self.api_url}/media/{int(media_id)}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        try:
            return self._send_request(req)
        except Exception:
            return None

    def get_media_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single WordPress media attachment by its slug, or None if not found.
        """
        clean_slug = urllib.parse.quote(slug.strip().lower())
        endpoint = f"{self.api_url}/media?slug={clean_slug}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        try:
            results = self._send_request(req)
            if isinstance(results, list) and len(results) > 0:
                return results[0]
            return None
        except Exception:
            return None

    def get_site_settings(self) -> Dict[str, Any]:
        """
        Retrieves global WordPress site settings including title, description, timezone, and language.
        """
        endpoint = f"{self.api_url}/settings"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        return self._send_request(req)

    def get_comments_by_post_id(self, post_id: int, status: str = "approved") -> List[Dict[str, Any]]:
        """
        Retrieves comments associated with a WordPress post ID, optionally filtered by status.
        """
        clean_status = urllib.parse.quote(status.strip().lower())
        endpoint = f"{self.api_url}/comments?post={int(post_id)}&status={clean_status}&per_page=100"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        results = self._send_request(req)
        if isinstance(results, list):
            return results
        return []

    def create_tag(self, name: str, slug: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Creates a new WordPress tag with optional slug and description.
        """
        endpoint = f"{self.api_url}/tags"
        payload: Dict[str, Any] = {"name": name.strip()}
        if slug:
            payload["slug"] = slug.strip().lower()
        if description:
            payload["description"] = description.strip()

        data_bytes = json.dumps(payload).encode("utf-8")
        headers = self._get_headers()
        headers["Content-Type"] = "application/json"
        req = urllib.request.Request(endpoint, data=data_bytes, headers=headers, method="POST")
        return self._send_request(req)

    def get_posts_by_author(self, author_id: int, per_page: int = 10, status: str = "publish") -> List[Dict[str, Any]]:
        """
        Retrieves posts authored by a specific WordPress user ID, filtered by status.
        """
        clean_status = urllib.parse.quote(status.strip().lower())
        endpoint = f"{self.api_url}/posts?author={int(author_id)}&per_page={int(per_page)}&status={clean_status}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        results = self._send_request(req)
        if isinstance(results, list):
            return results
        return []

    def delete_tag(self, tag_id: int, force: bool = True) -> Dict[str, Any]:
        """
        Deletes a WordPress tag by its numeric ID.
        """
        force_str = "true" if force else "false"
        endpoint = f"{self.api_url}/tags/{int(tag_id)}?force={force_str}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="DELETE")
        return self._send_request(req)

    def search_media(self, query: str, per_page: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieves WordPress media items matching a search query keyword.
        """
        clean_query = urllib.parse.quote(query.strip())
        endpoint = f"{self.api_url}/media?search={clean_query}&per_page={int(per_page)}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        results = self._send_request(req)
        if isinstance(results, list):
            return results
        return []

    def update_comment_status(self, comment_id: int, status: str = "approved") -> Dict[str, Any]:
        """
        Updates moderation status of a WordPress comment (approved, hold, spam, trash).
        """
        endpoint = f"{self.api_url}/comments/{int(comment_id)}"
        payload = {"status": status.strip().lower()}
        data_bytes = json.dumps(payload).encode("utf-8")
        headers = self._get_headers()
        headers["Content-Type"] = "application/json"
        req = urllib.request.Request(endpoint, data=data_bytes, headers=headers, method="POST")
        return self._send_request(req)

    def get_categories_with_counts(self, hide_empty: bool = True, per_page: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieves WordPress categories including their post count metrics.
        """
        hide_empty_str = "true" if hide_empty else "false"
        endpoint = f"{self.api_url}/categories?hide_empty={hide_empty_str}&per_page={int(per_page)}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        results = self._send_request(req)
        if isinstance(results, list):
            return results
        return []

    def get_users_by_role(self, role: str = "author", per_page: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieves WordPress users filtered by a specific role (administrator, editor, author, contributor, subscriber).
        """
        clean_role = urllib.parse.quote(role.strip().lower())
        endpoint = f"{self.api_url}/users?roles={clean_role}&per_page={int(per_page)}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        results = self._send_request(req)
        if isinstance(results, list):
            return results
        return []

    def bulk_trash_posts(self, post_ids: List[int]) -> Dict[str, Any]:
        """
        Moves multiple WordPress posts to the trash in bulk by calling DELETE on /posts/<id>.
        Returns summary dictionary containing trashed_count, trashed_ids, and any errors.
        """
        trashed_ids: List[int] = []
        errors: Dict[int, str] = {}
        for pid in post_ids:
            try:
                endpoint = f"{self.api_url}/posts/{int(pid)}"
                req = urllib.request.Request(endpoint, headers=self._get_headers(), method="DELETE")
                self._send_request(req)
                trashed_ids.append(int(pid))
            except Exception as e:
                errors[int(pid)] = str(e)

        return {
            "total_requested": len(post_ids),
            "trashed_count": len(trashed_ids),
            "trashed_ids": trashed_ids,
            "failed_count": len(errors),
            "errors": errors
        }

    def get_site_settings(self) -> Dict[str, Any]:
        """
        Retrieves site settings from /settings endpoint (site title, tagline, timezone, date_format, url, etc.).
        """
        endpoint = f"{self.api_url}/settings"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        results = self._send_request(req)
        if isinstance(results, dict):
            return results
        return {}

    def get_post_media_attachments(self, post_id: int, per_page: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieves all uploaded media attachments associated with a specific WordPress post parent ID.
        """
        endpoint = f"{self.api_url}/media?parent={int(post_id)}&per_page={max(1, int(per_page))}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        results = self._send_request(req)
        if isinstance(results, list):
            return results
        return []

    def set_post_sticky_status(self, post_id: int, is_sticky: bool = True) -> Dict[str, Any]:
        """
        Sets or unsets a WordPress post's sticky feature status (featured pinned editorial headline).
        """
        endpoint = f"{self.api_url}/posts/{int(post_id)}"
        payload = {"sticky": bool(is_sticky)}
        data_bytes = json.dumps(payload).encode("utf-8")
        headers = self._get_headers()
        headers["Content-Type"] = "application/json"
        req = urllib.request.Request(endpoint, data=data_bytes, headers=headers, method="POST")
        return self._send_request(req)

    def get_posts_by_status(self, status: str = "draft", page: int = 1, per_page: int = 20) -> List[Dict[str, Any]]:
        """
        Retrieves WordPress posts filtered by lifecycle status (publish, draft, pending, future, trash) with pagination.
        """
        st = status.strip().lower()
        p = max(1, int(page))
        pp = max(1, min(100, int(per_page)))
        endpoint = f"{self.api_url}/posts?status={st}&page={p}&per_page={pp}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        results = self._send_request(req)
        if isinstance(results, list):
            return results
        return []

    def duplicate_post_as_draft(self, post_id: int, title_suffix: str = " (Salinan)") -> Dict[str, Any]:
        """
        Clones an existing published or draft WordPress post into a new draft post with an amended title.
        """
        source_post = self.get_post(post_id)
        raw_title = source_post.get("title", {})
        if isinstance(raw_title, dict):
            orig_title = raw_title.get("rendered", "")
        else:
            orig_title = str(raw_title)

        raw_content = source_post.get("content", {})
        if isinstance(raw_content, dict):
            orig_content = raw_content.get("rendered", "")
        else:
            orig_content = str(raw_content)

        new_title = f"{orig_title}{title_suffix}".strip()
        orig_slug = source_post.get("slug", "")
        new_slug = f"{orig_slug}-salinan".strip("-")
        return self.create_post(
            title=new_title,
            content=orig_content,
            slug=new_slug,
            status="draft",
            categories=source_post.get("categories", [])
        )

    def get_post_revisions(self, post_id: int) -> List[Dict[str, Any]]:
        """
        Retrieves historical revisions of a WordPress post by post ID.
        """
        endpoint = f"{self.api_url}/posts/{int(post_id)}/revisions"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        res = self._send_request(req)
        return res if isinstance(res, list) else []

    def restore_post_revision(self, post_id: int, revision_id: int) -> Dict[str, Any]:
        """
        Restores a specific historical revision to the active post by retrieving the revision snapshot
        and updating the post title, content, and excerpt.
        """
        rev_endpoint = f"{self.api_url}/posts/{int(post_id)}/revisions/{int(revision_id)}"
        req = urllib.request.Request(rev_endpoint, headers=self._get_headers(), method="GET")
        rev = self._send_request(req)

        updates: Dict[str, Any] = {}
        if "title" in rev:
            updates["title"] = rev["title"].get("rendered", rev["title"]) if isinstance(rev["title"], dict) else rev["title"]
        if "content" in rev:
            updates["content"] = rev["content"].get("rendered", rev["content"]) if isinstance(rev["content"], dict) else rev["content"]
        if "excerpt" in rev:
            updates["excerpt"] = rev["excerpt"].get("rendered", rev["excerpt"]) if isinstance(rev["excerpt"], dict) else rev["excerpt"]

        return self.update_post(post_id, updates)

    def get_users_by_role(self, role: str = "author", page: int = 1, per_page: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieves users from WordPress filtered by user role (e.g. author, editor, administrator).
        """
        clean_role = role.strip().lower()
        endpoint = f"{self.api_url}/users?roles={clean_role}&page={max(1, int(page))}&per_page={max(1, min(100, int(per_page)))}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        res = self._send_request(req)
        return res if isinstance(res, list) else []

    def assign_post_author(self, post_id: int, author_id: int) -> Dict[str, Any]:
        """
        Assigns or transfers the designated author ID of an existing WordPress post.
        """
        return self.update_post(post_id=post_id, updates={"author": int(author_id)})

    def get_post_comments(self, post_id: int, status: str = "approve", page: int = 1, per_page: int = 20) -> List[Dict[str, Any]]:
        """
        Retrieves comments associated with a specific WordPress post ID, filtered by moderation status.
        """
        clean_status = status.strip().lower()
        endpoint = f"{self.api_url}/comments?post={int(post_id)}&status={clean_status}&page={max(1, int(page))}&per_page={max(1, min(100, int(per_page)))}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        res = self._send_request(req)
        return res if isinstance(res, list) else []

    def create_post_comment(
        self,
        post_id: int,
        content: str,
        author_name: str = "",
        author_email: str = "",
        parent_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Creates a new comment or threaded reply on a WordPress post via the REST API.
        """
        endpoint = f"{self.api_url}/comments"
        payload: Dict[str, Any] = {
            "post": int(post_id),
            "content": content.strip()
        }
        if author_name:
            payload["author_name"] = author_name.strip()
        if author_email:
            payload["author_email"] = author_email.strip()
        if parent_id is not None:
            payload["parent"] = int(parent_id)

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(endpoint, data=data, headers=self._get_headers(), method="POST")
        return self._send_request(req)

    def get_page_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a static WordPress page matching the given slug, or None if not found.
        """
        clean_slug = urllib.parse.quote(slug.strip().lower())
        endpoint = f"{self.api_url}/pages?slug={clean_slug}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        results = self._send_request(req)
        if isinstance(results, list) and len(results) > 0:
            return results[0]
        return None

    def get_page_by_id(self, page_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves a static WordPress page by its unique numeric page ID.
        """
        endpoint = f"{self.api_url}/pages/{int(page_id)}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        try:
            res = self._send_request(req)
            if isinstance(res, dict) and "id" in res:
                return res
            return None
        except Exception:
            return None

    def create_page(
        self,
        title: str,
        content: str,
        slug: Optional[str] = None,
        status: str = "publish",
        parent_id: Optional[int] = None,
        menu_order: int = 0
    ) -> Dict[str, Any]:
        """
        Creates a new static WordPress page via REST API (/wp/v2/pages).
        """
        endpoint = f"{self.api_url}/pages"
        payload = {
            "title": title.strip(),
            "content": content,
            "status": status,
            "menu_order": int(menu_order)
        }
        if slug:
            payload["slug"] = slug.strip().lower()
        if parent_id is not None:
            payload["parent"] = int(parent_id)

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(endpoint, data=data, headers=self._get_headers(), method="POST")
        return self._send_request(req)

    def delete_page(self, page_id: int, force: bool = True) -> Dict[str, Any]:
        """
        Deletes a static WordPress page by its unique numeric page ID via REST API (/wp/v2/pages/{id}).
        """
        force_param = "true" if force else "false"
        endpoint = f"{self.api_url}/pages/{int(page_id)}?force={force_param}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="DELETE")
        return self._send_request(req)

    def get_site_settings(self) -> Dict[str, Any]:
        """
        Retrieves global WordPress site configuration settings via REST API (/wp/v2/settings).
        """
        endpoint = f"{self.api_url}/settings"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        return self._send_request(req)

    def update_site_settings(self, settings_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates global WordPress site configuration settings via REST API (/wp/v2/settings).
        """
        endpoint = f"{self.api_url}/settings"
        data = json.dumps(settings_data).encode("utf-8")
        req = urllib.request.Request(endpoint, data=data, headers=self._get_headers(), method="POST")
        return self._send_request(req)

    def get_comments_by_status(
        self,
        status: str = "hold",
        page: int = 1,
        per_page: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Retrieves comments across all posts filtered by moderation status (approve, hold, spam, trash) via REST API (/wp/v2/comments).
        """
        clean_status = urllib.parse.quote(status.strip().lower())
        endpoint = f"{self.api_url}/comments?status={clean_status}&page={max(1, int(page))}&per_page={max(1, min(100, int(per_page)))}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        results = self._send_request(req)
        return results if isinstance(results, list) else []

    def bulk_update_comment_status(
        self,
        comment_ids: List[int],
        status: str = "approve"
    ) -> Dict[str, Any]:
        """
        Bulk updates moderation status for multiple comments in batch via REST API (/wp/v2/comments/{id}).
        """
        success = []
        failed = []
        for cid in comment_ids:
            try:
                self.update_comment_status(int(cid), status.strip())
                success.append(int(cid))
            except Exception as e:
                failed.append({"comment_id": int(cid), "error": str(e)})

        return {
            "success": success,
            "failed": failed,
            "total": len(comment_ids),
            "status": status.strip()
        }

    def get_comments_by_author_email(
        self,
        author_email: str,
        page: int = 1,
        per_page: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Retrieves comments filtered by author email via REST API (/wp/v2/comments?author_email=...).
        """
        clean_email = urllib.parse.quote(author_email.strip())
        endpoint = f"{self.api_url}/comments?author_email={clean_email}&page={max(1, int(page))}&per_page={max(1, min(100, int(per_page)))}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        results = self._send_request(req)
        return results if isinstance(results, list) else []

    def batch_delete_comments(
        self,
        comment_ids: List[int],
        force: bool = True
    ) -> Dict[str, Any]:
        """
        Batch deletes multiple comments permanently or moves them to trash via REST API (/wp/v2/comments/{id}?force=...).
        """
        deleted = []
        failed = []
        for cid in comment_ids:
            try:
                endpoint = f"{self.api_url}/comments/{int(cid)}?force={'true' if force else 'false'}"
                req = urllib.request.Request(endpoint, headers=self._get_headers(), method="DELETE")
                self._send_request(req)
                deleted.append(int(cid))
            except Exception as e:
                failed.append({"comment_id": int(cid), "error": str(e)})

        return {
            "deleted": deleted,
            "failed": failed,
            "total": len(comment_ids),
            "force": force
        }

    def get_categories_by_parent(self, parent_id: int, page: int = 1, per_page: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieves all child categories belonging to a specified parent category ID.
        """
        endpoint = f"{self.api_url}/categories?parent={int(parent_id)}&page={max(1, int(page))}&per_page={max(1, min(100, int(per_page)))}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        try:
            res = self._send_request(req)
            if isinstance(res, list):
                return res
            return []
        except Exception as e:
            logger.warning(f"Failed to fetch categories for parent {parent_id}: {e}")
            return []

    def batch_trash_posts(self, post_ids: List[int]) -> Dict[str, Any]:
        """
        Soft-deletes (moves to trash) a batch of WordPress posts by IDs.
        """
        trashed = []
        failed = []
        for pid in post_ids:
            try:
                res = self.delete_post(post_id=int(pid), force=False)
                if res and (res.get("status") == "trash" or "id" in res):
                    trashed.append(int(pid))
                else:
                    trashed.append(int(pid))
            except Exception as e:
                failed.append({"post_id": int(pid), "error": str(e)})

        return {
            "trashed": trashed,
            "failed": failed,
            "total": len(post_ids)
        }

    def get_tags_by_ids(self, tag_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Retrieves WordPress tags by a list of numeric tag IDs via /wp/v2/tags?include=...
        """
        if not tag_ids:
            return []
        valid_ids = [str(int(t)) for t in tag_ids if int(t) > 0]
        if not valid_ids:
            return []
        include_str = ",".join(valid_ids)
        endpoint = f"{self.api_url}/tags?include={include_str}&per_page={len(valid_ids)}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        try:
            res = self._send_request(req)
            return res if isinstance(res, list) else []
        except Exception as e:
            logger.warning(f"Failed to fetch tags for ids {include_str}: {e}")
            return []

    def batch_restore_posts(self, post_ids: List[int], target_status: str = "draft") -> Dict[str, Any]:
        """
        Restores a batch of trashed posts back to draft or published state.
        """
        restored = []
        failed = []
        for pid in post_ids:
            try:
                endpoint = f"{self.api_url}/posts/{int(pid)}"
                payload = json.dumps({"status": target_status}).encode("utf-8")
                req = urllib.request.Request(endpoint, data=payload, headers=self._get_headers(), method="POST")
                res = self._send_request(req)
                restored.append(int(pid))
            except Exception as e:
                failed.append({"post_id": int(pid), "error": str(e)})

        return {
            "restored": restored,
            "failed": failed,
            "total": len(post_ids),
            "target_status": target_status
        }

    def get_media_by_ids(self, media_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Retrieves WordPress media attachments by a list of numeric media IDs via /wp/v2/media?include=...
        """
        if not media_ids:
            return []
        valid_ids = [str(int(m)) for m in media_ids if int(m) > 0]
        if not valid_ids:
            return []
        include_str = ",".join(valid_ids)
        endpoint = f"{self.api_url}/media?include={include_str}&per_page={len(valid_ids)}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        try:
            res = self._send_request(req)
            return res if isinstance(res, list) else []
        except Exception as e:
            logger.warning(f"Failed to fetch media for ids {include_str}: {e}")
            return []

    def batch_update_media_captions(self, media_updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Batch updates alt text and captions for WordPress media attachments by numeric IDs.
        """
        updated = []
        failed = []
        for item in media_updates:
            media_id = item.get("id") or item.get("media_id")
            if not media_id:
                continue
            try:
                endpoint = f"{self.api_url}/media/{int(media_id)}"
                payload: Dict[str, Any] = {}
                if "alt_text" in item:
                    payload["alt_text"] = item["alt_text"]
                if "caption" in item:
                    payload["caption"] = item["caption"]
                if "description" in item:
                    payload["description"] = item["description"]

                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(endpoint, data=data, headers=self._get_headers(), method="POST")
                res = self._send_request(req)
                updated.append(int(media_id))
            except Exception as e:
                failed.append({"media_id": int(media_id), "error": str(e)})

        return {
            "updated": updated,
            "failed": failed,
            "total": len(media_updates)
        }

    def get_users_by_ids(self, user_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Retrieves multiple WordPress user profiles matching a list of numeric IDs via REST API.
        """
        valid_ids = [int(i) for i in user_ids if str(i).isdigit() and int(i) > 0]
        if not valid_ids:
            return []

        ids_param = ",".join(str(i) for i in sorted(list(set(valid_ids))))
        endpoint = f"{self.api_url}/users?include={ids_param}&per_page=100"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        results = self._send_request(req)
        return results if isinstance(results, list) else []

    def batch_update_post_categories(self, post_category_map: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Batch updates category associations for multiple WordPress posts by IDs.
        """
        updated = []
        failed = []
        for item in post_category_map:
            post_id = item.get("id") or item.get("post_id")
            categories = item.get("categories", [])
            if not post_id or not isinstance(categories, list):
                continue
            try:
                endpoint = f"{self.api_url}/posts/{int(post_id)}"
                payload = {"categories": [int(c) for c in categories if str(c).isdigit()]}
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(endpoint, data=data, headers=self._get_headers(), method="POST")
                self._send_request(req)
                updated.append(int(post_id))
            except Exception as e:
                failed.append({"post_id": int(post_id), "error": str(e)})

        return {
            "updated": updated,
            "failed": failed,
            "total": len(post_category_map)
        }

    def get_comments_by_ids(self, comment_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Retrieves a list of WordPress comments by their numeric IDs using the /wp/v2/comments endpoint.
        """
        if not comment_ids:
            return []

        clean_ids = [int(cid) for cid in comment_ids if str(cid).isdigit() and int(cid) > 0]
        if not clean_ids:
            return []

        all_comments = []
        chunk_size = 100
        for i in range(0, len(clean_ids), chunk_size):
            chunk = clean_ids[i:i + chunk_size]
            include_param = ",".join(str(cid) for cid in chunk)
            endpoint = f"{self.api_url}/comments?include={include_param}&per_page={len(chunk)}"
            req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
            try:
                res = self._send_request(req)
                if isinstance(res, list):
                    all_comments.extend(res)
            except Exception:
                pass

        return all_comments

    def batch_update_comment_status(
        self,
        comment_status_map: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Batch updates moderation statuses for multiple comments via POST /wp/v2/comments/{id}.
        Each item in comment_status_map should be a dict with 'id' (or 'comment_id') and 'status' ('approved', 'hold', 'spam', 'trash').
        """
        valid_statuses = {"approved", "hold", "spam", "trash"}
        updated = []
        failed = []

        for item in comment_status_map:
            cid = item.get("id") or item.get("comment_id")
            st = str(item.get("status", "")).strip().lower()
            if not cid or st not in valid_statuses:
                continue

            try:
                endpoint = f"{self.api_url}/comments/{int(cid)}"
                payload = {"status": st}
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(endpoint, data=data, headers=self._get_headers(), method="POST")
                self._send_request(req)
                updated.append(int(cid))
            except Exception as e:
                failed.append({"comment_id": int(cid), "error": str(e)})

        return {
            "updated": updated,
            "failed": failed,
            "total": len(comment_status_map)
        }

    def get_categories_by_ids(self, category_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Fetches category details for a list of category IDs via GET /wp/v2/categories?include=id1,id2,...
        Returns an empty list if category_ids is empty.
        """
        if not category_ids:
            return []
        valid_ids = [str(int(cid)) for cid in category_ids if cid]
        if not valid_ids:
            return []
        include_param = ",".join(valid_ids)
        endpoint = f"{self.api_url}/categories?include={include_param}&per_page={len(valid_ids)}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        res = self._send_request(req)
        return res if isinstance(res, list) else []


    def batch_update_tag_descriptions(
        self,
        tag_descriptions_map: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Batch updates descriptions for multiple tags via POST /wp/v2/tags/{id}.
        Each item in tag_descriptions_map should be a dict with 'id' (or 'tag_id') and 'description'.
        """
        updated = []
        failed = []

        for item in tag_descriptions_map:
            tid = item.get("id") or item.get("tag_id")
            desc = str(item.get("description", "")).strip()
            if not tid:
                continue

            try:
                endpoint = f"{self.api_url}/tags/{int(tid)}"
                payload = {"description": desc}
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(endpoint, data=data, headers=self._get_headers(), method="POST")
                self._send_request(req)
                updated.append(int(tid))
            except Exception as e:
                failed.append({"tag_id": int(tid), "error": str(e)})

        return {
            "updated": updated,
            "failed": failed,
            "total": len(tag_descriptions_map)
        }

    def get_tags_by_ids(self, tag_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Fetches tag details for a list of tag IDs via GET /wp/v2/tags?include=id1,id2,...
        Returns an empty list if tag_ids is empty.
        """
        if not tag_ids:
            return []
        valid_ids = [str(int(tid)) for tid in tag_ids if tid]
        if not valid_ids:
            return []
        include_param = ",".join(valid_ids)
        endpoint = f"{self.api_url}/tags?include={include_param}&per_page={len(valid_ids)}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        res = self._send_request(req)
        return res if isinstance(res, list) else []

    def batch_update_category_descriptions(
        self,
        category_descriptions_map: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Batch updates descriptions for multiple categories via POST /wp/v2/categories/{id}.
        Each item in category_descriptions_map should be a dict with 'id' (or 'category_id') and 'description'.
        """
        updated = []
        failed = []

        for item in category_descriptions_map:
            cid = item.get("id") or item.get("category_id")
            desc = str(item.get("description", "")).strip()
            if not cid:
                continue

            try:
                endpoint = f"{self.api_url}/categories/{int(cid)}"
                payload = {"description": desc}
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(endpoint, data=data, headers=self._get_headers(), method="POST")
                self._send_request(req)
                updated.append(int(cid))
            except Exception as e:
                failed.append({"category_id": int(cid), "error": str(e)})

        return {
            "updated": updated,
            "failed": failed,
            "total": len(category_descriptions_map)
        }

    def get_media_by_ids(self, media_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Retrieves multiple media items by their numeric IDs using /wp/v2/media?include=...
        """
        if not media_ids:
            return []
        ids_str = ",".join(str(int(i)) for i in media_ids)
        endpoint = f"{self.api_url}/media?include={ids_str}&per_page={min(100, len(media_ids))}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        try:
            res = self._send_request(req)
            if isinstance(res, list):
                return res
            return []
        except Exception:
            return []

    def batch_update_tag_slugs(
        self,
        tag_slugs_map: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Batch updates URL slugs for multiple tags via POST /wp/v2/tags/{id}.
        Each item in tag_slugs_map should be a dict with 'id' (or 'tag_id') and 'slug'.
        """
        updated = []
        failed = []

        for item in tag_slugs_map:
            tid = item.get("id") or item.get("tag_id")
            slug = str(item.get("slug", "")).strip()
            if not tid or not slug:
                continue

            try:
                endpoint = f"{self.api_url}/tags/{int(tid)}"
                payload = {"slug": slug}
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(endpoint, data=data, headers=self._get_headers(), method="POST")
                self._send_request(req)
                updated.append(int(tid))
            except Exception as e:
                failed.append({"tag_id": int(tid), "error": str(e)})

        return {
            "updated": updated,
            "failed": failed,
            "total": len(tag_slugs_map)
        }

    def get_users_by_roles(
        self,
        roles: List[str],
        page: int = 1,
        per_page: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Retrieves WordPress users filtered by user roles (e.g. administrator, editor, author)
        via GET /wp/v2/users?roles=...
        """
        if not roles:
            return []
        try:
            roles_str = ",".join(r.strip() for r in roles if r.strip())
            endpoint = f"{self.api_url}/users?roles={urllib.parse.quote(roles_str)}&page={int(page)}&per_page={int(per_page)}"
            req = urllib.request.Request(endpoint, headers=self._get_headers())
            res = self._send_request(req)
            if isinstance(res, list):
                return res
            return []
        except Exception:
            return []

    def batch_update_media_alt_texts(
        self,
        media_alt_map: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Batch updates accessibility alternative texts for multiple media library items via POST /wp/v2/media/{id}.
        Each item in media_alt_map should contain 'id' (or 'media_id') and 'alt_text'.
        """
        updated = []
        failed = []

        for item in media_alt_map:
            mid = item.get("id") or item.get("media_id")
            alt_text = str(item.get("alt_text", "")).strip()
            if not mid:
                continue

            try:
                endpoint = f"{self.api_url}/media/{int(mid)}"
                payload = {"alt_text": alt_text}
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(endpoint, data=data, headers=self._get_headers(), method="POST")
                self._send_request(req)
                updated.append(int(mid))
            except Exception as e:
                failed.append({"media_id": int(mid), "error": str(e)})

        return {
            "updated": updated,
            "failed": failed,
            "total": len(media_alt_map)
        }

    def get_posts_by_taxonomies(
        self,
        category_ids: Optional[List[int]] = None,
        tag_ids: Optional[List[int]] = None,
        page: int = 1,
        per_page: int = 10,
        status: str = "publish"
    ) -> List[Dict[str, Any]]:
        """
        Retrieves WordPress posts filtered by multiple categories and tags with pagination support.
        """
        query_params: Dict[str, Any] = {
            "page": max(1, int(page)),
            "per_page": max(1, min(100, int(per_page))),
            "status": str(status).strip() or "publish"
        }
        if category_ids:
            clean_cats = [str(int(c)) for c in category_ids if str(c).isdigit() and int(c) > 0]
            if clean_cats:
                query_params["categories"] = ",".join(clean_cats)
        if tag_ids:
            clean_tags = [str(int(t)) for t in tag_ids if str(t).isdigit() and int(t) > 0]
            if clean_tags:
                query_params["tags"] = ",".join(clean_tags)

        endpoint = f"{self.api_url}/posts?{urllib.parse.urlencode(query_params)}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        try:
            results = self._send_request(req)
            return results if isinstance(results, list) else []
        except Exception as e:
            logger.warning(f"Failed to fetch posts by taxonomies: {e}")
            return []

    def batch_update_post_featured_media(
        self,
        post_media_map: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Batch updates featured media IDs for multiple WordPress posts via POST /wp/v2/posts/{id}.
        Each item in post_media_map should contain 'id' (or 'post_id') and 'featured_media'.
        """
        updated = []
        failed = []

        for item in post_media_map:
            pid = item.get("id") or item.get("post_id")
            media_id = item.get("featured_media")
            if not pid or media_id is None:
                continue

            try:
                endpoint = f"{self.api_url}/posts/{int(pid)}"
                payload = {"featured_media": int(media_id)}
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(endpoint, data=data, headers=self._get_headers(), method="POST")
                self._send_request(req)
                updated.append(int(pid))
            except Exception as e:
                failed.append({"post_id": int(pid), "error": str(e)})

        return {
            "updated": updated,
            "failed": failed,
            "total": len(post_media_map)
        }

    def get_posts_by_date_range(
        self,
        after_date: str,
        before_date: str,
        page: int = 1,
        per_page: int = 10,
        status: str = "publish"
    ) -> List[Dict[str, Any]]:
        """
        Retrieves WordPress posts published within an ISO 8601 date range (after_date to before_date).
        """
        params = {
            "after": after_date.strip(),
            "before": before_date.strip(),
            "page": max(1, int(page)),
            "per_page": min(100, max(1, int(per_page))),
            "status": status.strip()
        }
        query_string = urllib.parse.urlencode(params)
        endpoint = f"{self.api_url}/posts?{query_string}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        try:
            return self._send_request(req)
        except Exception:
            return []

    def batch_update_post_status(self, post_status_map: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Updates the publication status for multiple WordPress posts in batch.
        Each item in post_status_map should contain 'id' (or 'post_id') and 'status' (e.g. 'publish', 'draft', 'pending').
        """
        updated = []
        failed = []

        for item in post_status_map:
            pid = item.get("id") or item.get("post_id")
            new_status = item.get("status")
            if not pid or not new_status:
                continue

            try:
                endpoint = f"{self.api_url}/posts/{int(pid)}"
                payload = {"status": str(new_status).strip()}
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(endpoint, data=data, headers=self._get_headers(), method="POST")
                self._send_request(req)
                updated.append(int(pid))
            except Exception as e:
                failed.append({"post_id": int(pid), "error": str(e)})

        return {
            "updated": updated,
            "failed": failed,
            "total": len(post_status_map)
        }

    def get_revisions_by_post_id(
        self,
        post_id: int,
        page: int = 1,
        per_page: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieves paginated historical revisions for a WordPress post by post ID.
        """
        endpoint = f"{self.api_url}/posts/{int(post_id)}/revisions?page={max(1, int(page))}&per_page={max(1, min(100, int(per_page)))}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        res = self._send_request(req)
        return res if isinstance(res, list) else []

    def compare_post_revisions(
        self,
        post_id: int,
        from_revision_id: int,
        to_revision_id: int
    ) -> Dict[str, Any]:
        """
        Compares two historical revisions of a WordPress post and returns the structural difference.
        """
        from_endpoint = f"{self.api_url}/posts/{int(post_id)}/revisions/{int(from_revision_id)}"
        to_endpoint = f"{self.api_url}/posts/{int(post_id)}/revisions/{int(to_revision_id)}"

        req_from = urllib.request.Request(from_endpoint, headers=self._get_headers(), method="GET")
        req_to = urllib.request.Request(to_endpoint, headers=self._get_headers(), method="GET")

        rev_from = self._send_request(req_from)
        rev_to = self._send_request(req_to)

        title_from = rev_from.get("title", {}).get("rendered", "") if isinstance(rev_from.get("title"), dict) else str(rev_from.get("title", ""))
        title_to = rev_to.get("title", {}).get("rendered", "") if isinstance(rev_to.get("title"), dict) else str(rev_to.get("title", ""))

        content_from = rev_from.get("content", {}).get("rendered", "") if isinstance(rev_from.get("content"), dict) else str(rev_from.get("content", ""))
        content_to = rev_to.get("content", {}).get("rendered", "") if isinstance(rev_to.get("content"), dict) else str(rev_to.get("content", ""))

        words_from = len(content_from.split())
        words_to = len(content_to.split())

        return {
            "post_id": int(post_id),
            "from_revision_id": int(from_revision_id),
            "to_revision_id": int(to_revision_id),
            "title_changed": title_from != title_to,
            "title_from": title_from,
            "title_to": title_to,
            "words_from": words_from,
            "words_to": words_to,
            "word_count_delta": words_to - words_from,
            "content_changed": content_from != content_to
        }

    diff_post_revisions = compare_post_revisions

    def get_media_by_mime_type(
        self,
        mime_type: str = "image/png",
        page: int = 1,
        per_page: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Queries WordPress REST API media endpoint filtered by exact MIME type with pagination.
        """
        clean_mime = urllib.parse.quote(mime_type.strip().lower())
        p = max(1, int(page))
        pp = max(1, min(100, int(per_page)))
        endpoint = f"{self.api_url}/media?mime_type={clean_mime}&page={p}&per_page={pp}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        results = self._send_request(req)
        return results if isinstance(results, list) else []

    def get_post_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a published or draft WordPress post matching the given slug, or None if not found.
        """
        clean_slug = urllib.parse.quote(slug.strip().lower())
        endpoint = f"{self.api_url}/posts?slug={clean_slug}"
        req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
        results = self._send_request(req)
        if isinstance(results, list) and len(results) > 0:
            return results[0]
        return None

    find_post_by_slug = get_post_by_slug

    def get_posts_by_category_slug(
        self,
        category_slug: str,
        page: int = 1,
        per_page: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieves published WordPress posts assigned to the category identified by slug.
        """
        clean_slug = urllib.parse.quote(category_slug.strip().lower())
        cat_req = urllib.request.Request(
            f"{self.api_url}/categories?slug={clean_slug}",
            headers=self._get_headers(),
            method="GET"
        )
        cat_results = self._send_request(cat_req)
        if not isinstance(cat_results, list) or len(cat_results) == 0:
            return []
        cat_id = cat_results[0].get("id")
        if not cat_id:
            return []

        p = max(1, int(page))
        pp = max(1, min(100, int(per_page)))
        posts_req = urllib.request.Request(
            f"{self.api_url}/posts?categories={cat_id}&page={p}&per_page={pp}",
            headers=self._get_headers(),
            method="GET"
        )
        results = self._send_request(posts_req)
        return results if isinstance(results, list) else []








































