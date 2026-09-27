import re
from typing import Dict, Any, List

class YoastSEOValidator:
    """
    Comprehensive SEO evaluator following Yoast SEO Green Score criteria.
    """

    @staticmethod
    def extract_text(html: str) -> str:
        # Remove style and script tags
        clean = re.sub(r"<(style|script)[^>]*>.*?</\1>", " ", html, flags=re.DOTALL | re.IGNORECASE)
        # Remove all other HTML tags
        clean = re.sub(r"<[^>]+>", " ", clean)
        # Normalize whitespace
        return " ".join(clean.split())

    @classmethod
    def evaluate(cls, metadata: Dict[str, Any], html_content: str) -> Dict[str, Any]:
        results: Dict[str, Any] = {
            "is_all_green": True,
            "score": 100,
            "checks": {},
            "warnings": [],
            "errors": []
        }

        fk = metadata.get("focus_keyphrase", "").strip().lower()
        title = metadata.get("seo_title", "").strip()
        slug = metadata.get("slug", "").strip().lower()
        meta_desc = metadata.get("meta_description", "").strip()
        body_text = cls.extract_text(html_content).lower()
        words = body_text.split()
        word_count = len(words)

        # 1. Word Count Check
        is_word_count_ok = word_count >= 300
        results["checks"]["word_count"] = {
            "status": "green" if is_word_count_ok else "red",
            "value": word_count,
            "target": ">= 300 words",
            "passed": is_word_count_ok
        }
        if not is_word_count_ok:
            results["errors"].append(f"Word count ({word_count}) is below minimum 300 words.")

        # 2. Meta Description Length (140 - 156 characters)
        meta_len = len(meta_desc)
        is_meta_len_ok = 140 <= meta_len <= 156
        results["checks"]["meta_description_length"] = {
            "status": "green" if is_meta_len_ok else "red",
            "value": meta_len,
            "target": "140 - 156 characters",
            "passed": is_meta_len_ok
        }
        if not is_meta_len_ok:
            results["errors"].append(f"Meta description length is {meta_len} chars (must be 140-156).")

        # 3. Focus Keyphrase in Meta Description
        is_fk_in_meta = bool(fk and fk in meta_desc.lower())
        results["checks"]["keyphrase_in_meta"] = {
            "status": "green" if is_fk_in_meta else "red",
            "passed": is_fk_in_meta
        }
        if not is_fk_in_meta:
            results["errors"].append("Focus keyphrase is missing from meta description.")

        # 4. Focus Keyphrase in SEO Title (At the beginning)
        title_lower = title.lower()
        is_fk_in_title_start = bool(fk and title_lower.startswith(fk))
        results["checks"]["keyphrase_in_title_start"] = {
            "status": "green" if is_fk_in_title_start else "red",
            "passed": is_fk_in_title_start
        }
        if not is_fk_in_title_start:
            results["errors"].append("SEO title must start with the focus keyphrase.")

        # 5. Focus Keyphrase in Slug
        expected_slug = fk.replace(" ", "-")
        is_fk_in_slug = bool(fk and (expected_slug in slug or all(w in slug for w in fk.split())))
        results["checks"]["keyphrase_in_slug"] = {
            "status": "green" if is_fk_in_slug else "red",
            "passed": is_fk_in_slug
        }
        if not is_fk_in_slug:
            results["errors"].append("Slug does not contain the focus keyphrase.")

        # 6. Focus Keyphrase in First Paragraph
        first_p_match = re.search(r"<p[^>]*class=[\"'].*?lead.*?[\"'][^>]*>(.*?)</p>", html_content, re.DOTALL | re.IGNORECASE)
        if not first_p_match:
            first_p_match = re.search(r"<p[^>]*>(.*?)</p>", html_content, re.DOTALL | re.IGNORECASE)
        
        first_p_text = cls.extract_text(first_p_match.group(1)).lower() if first_p_match else ""
        is_fk_in_intro = bool(fk and fk in first_p_text)
        results["checks"]["keyphrase_in_introduction"] = {
            "status": "green" if is_fk_in_intro else "red",
            "passed": is_fk_in_intro
        }
        if not is_fk_in_intro:
            results["errors"].append("Focus keyphrase missing from introductory paragraph.")

        # 7. Focus Keyphrase in Subheading H2
        h2_headings = re.findall(r"<h2[^>]*>(.*?)</h2>", html_content, re.DOTALL | re.IGNORECASE)
        is_fk_in_h2 = any(fk in cls.extract_text(h).lower() for h in h2_headings)
        results["checks"]["keyphrase_in_h2"] = {
            "status": "green" if is_fk_in_h2 else "red",
            "passed": is_fk_in_h2
        }
        if not is_fk_in_h2:
            results["errors"].append("At least one H2 subheading must contain the focus keyphrase.")

        # 8. Focus Keyphrase in Image Alt
        alt_tags = re.findall(r"<img[^>]+alt=[\"'](.*?)[\"']", html_content, re.IGNORECASE)
        is_fk_in_alt = any(fk in alt.lower() for alt in alt_tags)
        results["checks"]["keyphrase_in_image_alt"] = {
            "status": "green" if is_fk_in_alt else "red",
            "passed": is_fk_in_alt
        }
        if not is_fk_in_alt:
            results["errors"].append("Image alt attribute must contain the focus keyphrase.")

        # 9. Internal Link
        internal_links = re.findall(r"href=[\"'](https?://bif-pwt\.telkomuniversity\.ac\.id[^\s\"']*)[\"']", html_content, re.IGNORECASE)
        has_internal_link = len(internal_links) >= 1
        results["checks"]["internal_link"] = {
            "status": "green" if has_internal_link else "red",
            "count": len(internal_links),
            "passed": has_internal_link
        }
        if not has_internal_link:
            results["errors"].append("At least one internal link to bif-pwt.telkomuniversity.ac.id is required.")

        # 10. Outbound Link with security attributes
        outbound_links = re.findall(
            r"<a\s+[^>]*href=[\"'](https?://(?!bif-pwt\.telkomuniversity\.ac\.id)[^\s\"']+)[\"'][^>]*>",
            html_content,
            re.IGNORECASE
        )
        has_outbound_link = len(outbound_links) >= 1
        has_rel_noopener = bool(re.search(r"rel=[\"'][^\"']*noopener[^\"']*[\"']", html_content, re.IGNORECASE))
        results["checks"]["outbound_link"] = {
            "status": "green" if has_outbound_link and has_rel_noopener else "red",
            "count": len(outbound_links),
            "has_noopener": has_rel_noopener,
            "passed": has_outbound_link and has_rel_noopener
        }
        if not (has_outbound_link and has_rel_noopener):
            results["errors"].append("Valid outbound link with rel='noopener noreferrer' is required.")

        # Keyphrase density calculation
        fk_count = body_text.count(fk) if fk else 0
        fk_word_count = len(fk.split()) if fk else 1
        density = (fk_count * fk_word_count / max(word_count, 1)) * 100
        results["keyphrase_density"] = {
            "count": fk_count,
            "density_percentage": round(density, 2),
            "optimal": 0.5 <= density <= 3.0
        }

        all_passed = all(c["passed"] for c in results["checks"].values())
        results["is_all_green"] = all_passed
        results["score"] = 100 if all_passed else max(0, 100 - len(results["errors"]) * 10)

        return results
