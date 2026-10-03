#!/usr/bin/env python3
"""
Notifies search engines (Google, Bing, IndexNow) when sitemap.xml is updated.
"""

import sys
import urllib.request
import urllib.parse
from typing import Dict, Any


SEARCH_ENGINE_PING_URLS = {
    "Google": "https://www.google.com/ping?sitemap={sitemap_url}",
    "Bing": "https://www.bing.com/ping?sitemap={sitemap_url}",
}


def ping_sitemap(sitemap_url: str, timeout: int = 10) -> Dict[str, Any]:
    encoded_url = urllib.parse.quote(sitemap_url, safe=":/")
    results = {}

    for engine, template in SEARCH_ENGINE_PING_URLS.items():
        ping_target = template.format(sitemap_url=encoded_url)
        req = urllib.request.Request(
            ping_target,
            headers={"User-Agent": "TelkomPurwokertoEditorialBot/1.0"}
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                results[engine] = {
                    "status_code": resp.status,
                    "success": 200 <= resp.status < 400,
                    "target_url": ping_target
                }
        except Exception as e:
            results[engine] = {
                "status_code": getattr(e, "code", 0),
                "success": False,
                "error": str(e),
                "target_url": ping_target
            }

    return results


def main():
    sitemap = sys.argv[1] if len(sys.argv) > 1 else "https://bif-pwt.telkomuniversity.ac.id/sitemap.xml"
    print(f"Mengirim notifikasi sitemap: {sitemap}")
    results = ping_sitemap(sitemap)
    for engine, res in results.items():
        icon = "✅" if res["success"] else "⚠️"
        err = f" ({res.get('error')})" if not res["success"] else ""
        print(f" {icon} {engine}: HTTP {res['status_code']}{err}")


if __name__ == "__main__":
    main()
