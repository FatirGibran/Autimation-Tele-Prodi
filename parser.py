import re
from typing import Dict, Any, Optional

def parse_telegram_input(raw_text: str) -> Dict[str, Any]:
    """
    Parses structured Telegram text trigger into a dictionary.
    Expected format:
    Topik: ...
    Tanggal: ...
    Kategori: ...
    Image URL: ...
    Poin Utama:
    - ...
    """
    lines = raw_text.strip().splitlines()
    data = {
        "topik": "",
        "tanggal": "",
        "kategori": "",
        "image_url": "",
        "poin_utama": []
    }
    
    current_key = None
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
            
        lower_line = line_clean.lower()
        if lower_line.startswith("topik:"):
            data["topik"] = line_clean.split(":", 1)[1].strip()
            current_key = "topik"
        elif lower_line.startswith("tanggal:"):
            data["tanggal"] = line_clean.split(":", 1)[1].strip()
            current_key = "tanggal"
        elif lower_line.startswith("kategori:"):
            data["kategori"] = line_clean.split(":", 1)[1].strip()
            current_key = "kategori"
        elif lower_line.startswith("image url:") or lower_line.startswith("image:"):
            raw_url = line_clean.split(":", 1)[1].strip()
            # Clean markdown link wrapping if present e.g. [url](url)
            match = re.search(r'\((https?://[^\)]+)\)', raw_url)
            data["image_url"] = match.group(1) if match else raw_url
            current_key = "image_url"
        elif lower_line.startswith("poin utama:"):
            current_key = "poin_utama"
        elif current_key == "poin_utama":
            cleaned_bullet = re.sub(r'^[\-\*\•\d\.]+\s*', '', line_clean)
            if cleaned_bullet:
                data["poin_utama"].append(cleaned_bullet)
                
    return data

def parse_llm_response(response_text: str) -> Dict[str, Any]:
    """
    Extracts Yoast SEO metadata and HTML block from LLM output.
    """
    result = {
        "focus_keyphrase": "",
        "seo_title": "",
        "slug": "",
        "meta_description": "",
        "html_code": ""
    }
    
    # Extract metadata fields
    fk_match = re.search(r"Focus Keyphrase:\s*(.+)", response_text, re.IGNORECASE)
    if fk_match:
        result["focus_keyphrase"] = fk_match.group(1).strip()
        
    title_match = re.search(r"SEO Title:\s*(.+)", response_text, re.IGNORECASE)
    if title_match:
        result["seo_title"] = title_match.group(1).strip()
        
    slug_match = re.search(r"Slug:\s*(.+)", response_text, re.IGNORECASE)
    if slug_match:
        result["slug"] = slug_match.group(1).strip()
        
    meta_match = re.search(r"Meta Description:\s*(.+)", response_text, re.IGNORECASE)
    if meta_match:
        result["meta_description"] = meta_match.group(1).strip()
        
    # Extract HTML code block
    html_match = re.search(r"```(?:html)?\s*(<div class=\"tu-editorial-container\".*?</div>)\s*```", response_text, re.DOTALL)
    if html_match:
        result["html_code"] = html_match.group(1).strip()
    else:
        # Fallback if markdown block wasn't fenced
        raw_div = re.search(r"(<div class=\"tu-editorial-container\".*?</div>)", response_text, re.DOTALL)
        if raw_div:
            result["html_code"] = raw_div.group(1).strip()

    return result

def validate_yoast_seo(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates green score criteria according to Yoast SEO guidelines.
    """
    report = {"passed": True, "checks": {}}
    meta_len = len(data.get("meta_description", ""))
    report["checks"]["meta_description_length"] = {
        "value": meta_len,
        "valid": 140 <= meta_len <= 156,
        "detail": f"{meta_len} chars (target: 140-156)"
    }
    
    fk = data.get("focus_keyphrase", "").lower()
    report["checks"]["keyphrase_in_title"] = {
        "valid": bool(fk and data.get("seo_title", "").lower().startswith(fk)),
        "detail": "Focus keyphrase at start of SEO Title"
    }
    report["checks"]["keyphrase_in_slug"] = {
        "valid": bool(fk and fk.replace(" ", "-") in data.get("slug", "").lower()),
        "detail": "Focus keyphrase present in slug"
    }
    
    report["passed"] = all(c["valid"] for c in report["checks"].values())
    return report
