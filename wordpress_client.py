import base64
import json
import time
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

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
