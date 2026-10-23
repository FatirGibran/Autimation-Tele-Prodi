import base64
import json
import time
import urllib.request
import urllib.error
import urllib.parse
from typing import Dict, Any, Optional, List


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





























