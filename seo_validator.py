import re
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from bs4 import BeautifulSoup

class YoastSEOValidator:
    """
    Comprehensive SEO evaluator following Yoast SEO Green Score criteria.
    """

    INDONESIAN_TRANSITION_WORDS = [
        "selain itu", "oleh karena itu", "namun", "meskipun demikian", "sehingga",
        "akibatnya", "dengan demikian", "sementara itu", "di samping itu", "sebagai contoh",
        "oleh sebab itu", "selanjutnya", "bahkan", "sebaliknya", "akan tetapi",
        "kendati demikian", "terlebih lagi", "selain", "tetapi", "kemudian", "juga"
    ]

    NON_PASSIVE_DI = {
        "dimensi", "dirinya", "diploma", "dini", "dinamika", "dialog", "diagram",
        "disiplin", "direktur", "digital", "distribusi", "divisi"
    }

    GENERIC_ANCHOR_PATTERNS = {
        "klik di sini", "di sini", "click here", "baca di sini",
        "link", "tautan", "baca selengkapnya", "selengkapnya", "disini"
    }


    @classmethod
    def is_passive_sentence(cls, sentence: str) -> bool:
        words = re.findall(r"\b[a-zA-Z]+\b", sentence.lower())
        for w in words:
            if w.startswith("di") and len(w) >= 5 and w not in cls.NON_PASSIVE_DI:
                return True
        return False

    @staticmethod
    def count_syllables_indonesian(word: str) -> int:
        """
        Estimates syllable count for Indonesian words based on vowel clusters.
        """
        clean_word = re.sub(r"[^a-zA-Z]", "", word.lower())
        if not clean_word:
            return 0
        vowels = "aiueo"
        count = sum(1 for char in clean_word if char in vowels)
        return max(1, count)

    @classmethod
    def audit_anchor_texts(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits all hyperlinks for generic, non-descriptive anchor texts that penalize SEO.
        """
        links = re.findall(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html_content, re.IGNORECASE | re.DOTALL)
        flagged_links = []
        for href, text in links:
            clean_text = re.sub(r'<[^>]+>', '', text).strip().lower()
            if clean_text in cls.GENERIC_ANCHOR_PATTERNS:
                flagged_links.append({"href": href, "anchor": clean_text})

        return {
            "total_links": len(links),
            "flagged_count": len(flagged_links),
            "flagged_links": flagged_links,
            "passed": len(flagged_links) == 0
        }

    @classmethod
    def check_keyword_cannibalization(cls, keyphrase: str, existing_keyphrases: List[str], threshold: float = 0.8) -> Dict[str, Any]:
        """
        Detects potential keyword cannibalization against existing published article keyphrases.
        """
        target_tokens = set(re.findall(r"\b\w+\b", keyphrase.lower()))
        if not target_tokens:
            return {"cannibalized": False, "conflicts": []}

        conflicts = []
        for existing in existing_keyphrases:
            norm_existing = existing.strip().lower()
            if not norm_existing:
                continue
            if norm_existing == keyphrase.strip().lower():
                conflicts.append({"keyphrase": existing, "similarity": 1.0, "exact": True})
                continue
            exist_tokens = set(re.findall(r"\b\w+\b", norm_existing))
            if not exist_tokens:
                continue
            intersection = target_tokens.intersection(exist_tokens)
            union = target_tokens.union(exist_tokens)
            jaccard = len(intersection) / len(union)
            if jaccard >= threshold:
                conflicts.append({"keyphrase": existing, "similarity": round(jaccard, 2), "exact": False})

        return {
            "cannibalized": len(conflicts) > 0,
            "conflicts": conflicts
        }

    @classmethod
    def evaluate_keyword_density(cls, keyphrase: str, text: str) -> Dict[str, Any]:
        """
        Evaluates focus keyphrase density against Yoast SEO optimal bounds (0.5% - 3.0%).
        """
        clean_text = text.lower()
        clean_fk = keyphrase.strip().lower()
        if not clean_fk or not clean_text:
            return {"count": 0, "density_percentage": 0.0, "is_optimal": False, "status": "red", "advice": "Kata kunci kosong"}

        words = clean_text.split()
        word_count = len(words)
        fk_words_len = len(clean_fk.split())
        fk_count = len(re.findall(rf"\b{re.escape(clean_fk)}\b", clean_text))

        density = (fk_count * fk_words_len / max(word_count, 1)) * 100
        is_optimal = 0.5 <= density <= 3.0
        status = "green" if is_optimal else ("orange" if density < 0.5 else "red")
        
        advice = "Kerapatan kata kunci optimal" if is_optimal else (
            "Kerapatan kata kunci terlalu rendah (disarankan >= 0.5%)" if density < 0.5 else
            "Peringatan keyword stuffing! Kerapatan kata kunci melebihi 3.0%"
        )

        return {
            "count": fk_count,
            "density_percentage": round(density, 2),
            "is_optimal": is_optimal,
            "status": status,
            "advice": advice
        }

    @classmethod
    def evaluate_paragraph_lengths(cls, html_content: str, max_words: int = 150) -> Dict[str, Any]:
        """
        Validates paragraph lengths against Yoast SEO threshold (maximum 150 words per paragraph).
        """
        paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html_content, re.DOTALL | re.IGNORECASE)
        flagged = []
        for idx, p in enumerate(paragraphs, start=1):
            text = cls.extract_text(p)
            wc = len(text.split())
            if wc > max_words:
                flagged.append({
                    "paragraph_index": idx,
                    "word_count": wc,
                    "preview": text[:80] + "..." if len(text) > 80 else text
                })

        return {
            "total_paragraphs": len(paragraphs),
            "max_words_allowed": max_words,
            "flagged_count": len(flagged),
            "flagged_paragraphs": flagged,
            "passed": len(flagged) == 0
        }

    @classmethod
    def evaluate_subheading_distribution(cls, html_content: str, max_words_per_section: int = 300) -> Dict[str, Any]:
        """
        Audits text sections between H2/H3 subheadings against the 300-word limit.
        Ensures content is visually structured with sufficient subheadings.
        """
        parts = re.split(r'<h[234][^>]*>.*?</h[234]>', html_content, flags=re.IGNORECASE | re.DOTALL)
        flagged_sections = []
        for idx, part in enumerate(parts, start=1):
            text = cls.extract_text(part)
            words = text.split()
            wc = len(words)
            if wc > max_words_per_section:
                flagged_sections.append({
                    "section_index": idx,
                    "word_count": wc,
                    "preview": " ".join(words[:15]) + "..."
                })

        return {
            "total_sections": len(parts),
            "max_words_allowed": max_words_per_section,
            "flagged_count": len(flagged_sections),
            "flagged_sections": flagged_sections,
            "passed": len(flagged_sections) == 0
        }

    @classmethod
    def audit_links_profile(cls, html_content: str, internal_domain: str = "telkomuniversity.ac.id") -> Dict[str, Any]:
        """
        Conducts a comprehensive audit of internal vs external link distribution and security headers.
        """
        raw_links = re.findall(r'<a\s+([^>]*href=["\'][^"\']+["\'][^>]*)>(.*?)</a>', html_content, re.IGNORECASE | re.DOTALL)
        internal_links = []
        external_links = []
        unsecured_external = []

        for attr_str, anchor_inner in raw_links:
            href_match = re.search(r'href=["\']([^"\']+)["\']', attr_str, re.IGNORECASE)
            if not href_match:
                continue
            href = href_match.group(1).strip()
            anchor_text = cls.extract_text(anchor_inner)

            is_internal = internal_domain in href.lower() or href.startswith("/") or href.startswith("#")
            link_record = {"href": href, "anchor": anchor_text}

            if is_internal:
                internal_links.append(link_record)
            else:
                external_links.append(link_record)
                if "noopener" not in attr_str.lower():
                    unsecured_external.append(link_record)

        has_internal = len(internal_links) >= 1
        has_external = len(external_links) >= 1
        is_secure = len(unsecured_external) == 0
        passed = has_internal and has_external and is_secure

        return {
            "total_links": len(raw_links),
            "internal_count": len(internal_links),
            "external_count": len(external_links),
            "unsecured_external_count": len(unsecured_external),
            "internal_links": internal_links,
            "external_links": external_links,
            "passed": passed
        }

    @classmethod
    def validate_h1_structure(cls, html_content: str) -> Dict[str, Any]:
        """
        Validates H1 heading usage in article content.
        Google and Yoast guidelines recommend at most one H1 per page to maintain clear topic hierarchy.
        """
        h1_tags = re.findall(r'<h1[^>]*>(.*?)</h1>', html_content, re.IGNORECASE | re.DOTALL)
        count = len(h1_tags)
        # Passing if 0 (theme handles it) or 1 (content has main title). Flagged if >= 2.
        passed = count <= 1
        return {
            "h1_count": count,
            "h1_texts": [cls.extract_text(h) for h in h1_tags],
            "passed": passed,
            "status": "green" if passed else "red",
            "message": "Struktur H1 optimal (maksimal 1 tag H1)" if passed else f"Terdeteksi {count} tag H1 (disarankan maksimal 1 tag H1 per artikel)"
        }

    @classmethod
    def evaluate_academic_title_style(cls, title: str) -> Dict[str, Any]:
        """
        Evaluates SEO title adherence to academic journalism style guides
        (structured subtitle and domain power terminology).
        """
        clean_title = title.strip()
        has_subtitle = any(sep in clean_title for sep in [":", " -- ", " - ", "|"])

        academic_power_terms = [
            "inovasi", "riset", "implementasi", "analisis", "optimalisasi",
            "arsitektur", "komputasi", "penerapan", "integrasi", "evaluasi",
            "perancangan", "sistem", "efisiensi", "keamanan", "prototipe"
        ]

        title_lower = clean_title.lower()
        matched_terms = [term for term in academic_power_terms if term in title_lower]

        score = 60
        if has_subtitle:
            score += 20
        if matched_terms:
            score += min(20, len(matched_terms) * 10)

        is_recommended = score >= 80
        return {
            "title": clean_title,
            "has_subtitle": has_subtitle,
            "power_terms_found": matched_terms,
            "score": score,
            "is_recommended": is_recommended
        }

    @classmethod
    def evaluate_stopword_ratio(cls, text: str) -> Dict[str, Any]:
        """
        Calculates stop word ratio to ensure information density without excessive grammatical filler.
        """
        clean_words = re.findall(r"\b[a-zA-Z]+\b", text.lower())
        total_words = len(clean_words)
        if total_words == 0:
            return {"total_words": 0, "stop_words_count": 0, "ratio_pct": 0.0, "is_balanced": True, "status": "green"}

        stop_words_set = {
            "yang", "untuk", "pada", "dengan", "adalah", "sebagai", "dalam", "dari",
            "ini", "itu", "dan", "atau", "oleh", "akan", "juga", "dapat", "secara",
            "antara", "karena", "bagi", "setelah", "saat", "lebih", "telah", "bisa",
            "ke", "di", "dari", "pada", "oleh", "sampai", "tentang", "maka", "lalu"
        }

        matched_stops = [w for w in clean_words if w in stop_words_set]
        ratio_pct = round((len(matched_stops) / total_words) * 100, 1)

        # Balanced range: 20% to 50%
        is_balanced = 15.0 <= ratio_pct <= 52.0
        status = "green" if is_balanced else ("orange" if ratio_pct < 15.0 else "red")
        advice = "Kepadatan konten dan rasio kata hubung optimal" if is_balanced else (
            "Teks sangat padat istilah teknis" if ratio_pct < 15.0 else
            "Rasio kata hubung/stop words terlalu tinggi, disarankan memperpadat konten informasi"
        )

        return {
            "total_words": total_words,
            "stop_words_count": len(matched_stops),
            "ratio_pct": ratio_pct,
            "is_balanced": is_balanced,
            "status": status,
            "advice": advice
        }

    @classmethod
    def evaluate_anchor_diversity(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits hyperlink anchor text diversity to detect excessive repetitive anchor phrasing.
        """
        links = re.findall(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html_content, re.IGNORECASE | re.DOTALL)
        if not links:
            return {"total_links": 0, "unique_anchors": 0, "diversity_ratio": 1.0, "is_diverse": True, "repeated": []}

        anchors: Dict[str, int] = {}
        for _, text in links:
            clean = cls.extract_text(text).strip().lower()
            if clean:
                anchors[clean] = anchors.get(clean, 0) + 1

        total = len(links)
        unique = len(anchors)
        ratio = round(unique / total, 2)

        # Repeated anchors (> 2 occurrences)
        repeated = [{"anchor": k, "count": v} for k, v in anchors.items() if v > 2]
        is_diverse = len(repeated) == 0

        return {
            "total_links": total,
            "unique_anchors": unique,
            "diversity_ratio": ratio,
            "is_diverse": is_diverse,
            "repeated": repeated
        }

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

        # 4b. SEO Title Length (30 - 65 characters)
        title_len = len(title)
        is_title_len_ok = 30 <= title_len <= 65
        results["checks"]["seo_title_length"] = {
            "status": "green" if is_title_len_ok else "red",
            "value": title_len,
            "target": "30 - 65 characters",
            "passed": is_title_len_ok
        }
        if not is_title_len_ok:
            results["errors"].append(f"SEO title length is {title_len} chars (optimal 30-65 chars).")

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

        # 14. Anchor text descriptive quality audit
        anchor_audit = cls.audit_anchor_texts(html_content)
        results["checks"]["anchor_texts"] = {
            "status": "green" if anchor_audit["passed"] else "orange",
            "passed": True,
            "total_links": anchor_audit["total_links"],
            "flagged_count": anchor_audit["flagged_count"]
        }
        if not anchor_audit["passed"]:
            results["warnings"].append(f"Ditemukan {anchor_audit['flagged_count']} tautan dengan anchor text generik.")

        results["readability"] = cls.analyze_readability(body_text)
        results["coleman_liau"] = cls.calculate_indonesian_coleman_liau(body_text)
        if results["readability"]["has_consecutive_duplicates"]:
            results["warnings"].append("Terdapat 3 atau lebih kalimat berurutan yang diawali kata yang sama.")

        all_passed = all(c["passed"] for c in results["checks"].values())
        results["is_all_green"] = all_passed
        results["score"] = 100 if all_passed else max(0, 100 - len(results["errors"]) * 10)

        return results

    @classmethod
    def analyze_readability(cls, text: str) -> Dict[str, Any]:
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        total_sentences = len(sentences)
        if total_sentences == 0:
            return {"total_sentences": 0, "avg_words_per_sentence": 0.0, "long_sentences_pct": 0.0, "is_readable": True}

        words_per_sentence = [len(s.split()) for s in sentences]
        long_sentences = [w for w in words_per_sentence if w > 20]
        long_pct = (len(long_sentences) / total_sentences) * 100
        avg_words = sum(words_per_sentence) / total_sentences

        first_words = [s.split()[0].lower() for s in sentences if s.split()]
        has_consecutive_duplicates = False
        for i in range(2, len(first_words)):
            if first_words[i] == first_words[i - 1] == first_words[i - 2]:
                has_consecutive_duplicates = True
                break

        transition_sentences = [
            s for s in sentences
            if any(re.search(r"\b" + re.escape(tw) + r"\b", s.lower()) for tw in cls.INDONESIAN_TRANSITION_WORDS)
        ]
        transition_pct = (len(transition_sentences) / total_sentences * 100) if total_sentences else 0.0

        passive_sentences = [s for s in sentences if cls.is_passive_sentence(s)]
        passive_pct = (len(passive_sentences) / total_sentences * 100) if total_sentences else 0.0

        total_words = sum(words_per_sentence)
        total_syllables = sum(cls.count_syllables_indonesian(w) for w in text.split())
        syllables_per_word = (total_syllables / total_words) if total_words else 0.0
        flesch_score = round(max(0.0, min(100.0, 206.84 - (1.015 * avg_words) - (30.0 * syllables_per_word))), 1)

        return {
            "total_sentences": total_sentences,
            "avg_words_per_sentence": round(avg_words, 1),
            "long_sentences_pct": round(long_pct, 1),
            "has_consecutive_duplicates": has_consecutive_duplicates,
            "syllables_per_word": round(syllables_per_word, 2),
            "reading_ease_score": flesch_score,
            "transition_words": {
                "count": len(transition_sentences),
                "percentage": round(transition_pct, 1),
                "is_optimal": transition_pct >= 20.0
            },
            "passive_voice": {
                "count": len(passive_sentences),
                "percentage": round(passive_pct, 1),
                "is_acceptable": passive_pct <= 25.0
            },
            "is_readable": (long_pct <= 30.0) and not has_consecutive_duplicates
        }

    @classmethod
    def validate_image_dimensions(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits image elements for explicit width and height attributes to prevent
        Cumulative Layout Shift (CLS) in Google Core Web Vitals.
        """
        img_tags = re.findall(r'<img\s+[^>]+>', html_content, re.IGNORECASE)
        total_images = len(img_tags)
        if total_images == 0:
            return {
                "total_images": 0,
                "images_with_dimensions": 0,
                "missing_dimensions_count": 0,
                "is_optimal": True,
                "warnings": []
            }

        with_dims = 0
        warnings = []
        for tag in img_tags:
            has_w = bool(re.search(r'\bwidth=["\']\d+(?:px)?["\']', tag, re.IGNORECASE))
            has_h = bool(re.search(r'\bheight=["\']\d+(?:px)?["\']', tag, re.IGNORECASE))
            has_aspect = bool(re.search(r'aspect-ratio', tag, re.IGNORECASE))
            if (has_w and has_h) or has_aspect:
                with_dims += 1
            else:
                warnings.append("Image element missing explicit width and height attributes.")

        missing = total_images - with_dims
        return {
            "total_images": total_images,
            "images_with_dimensions": with_dims,
            "missing_dimensions_count": missing,
            "is_optimal": missing == 0,
            "warnings": warnings
        }

    @classmethod
    def evaluate_keyphrase_distribution(cls, html_content: str, focus_keyphrase: str) -> Dict[str, Any]:
        """
        Evaluates whether the focus keyphrase is distributed evenly across the introductory,
        body, and concluding sections of the content.
        """
        text = cls.extract_text(html_content).lower()
        fk = focus_keyphrase.strip().lower()
        if not fk or not text:
            return {
                "total_occurrences": 0,
                "sections": {"intro": 0, "body": 0, "conclusion": 0},
                "sections_covered": 0,
                "is_uniform": False,
                "warning": "Focus keyphrase or content is empty."
            }

        words = text.split()
        total_words = len(words)
        third = total_words // 3

        sec1 = " ".join(words[:third])
        sec2 = " ".join(words[third:2 * third])
        sec3 = " ".join(words[2 * third:])

        c1 = sec1.count(fk)
        c2 = sec2.count(fk)
        c3 = sec3.count(fk)
        total = c1 + c2 + c3

        sections_present = sum(1 for c in (c1, c2, c3) if c > 0)
        is_uniform = (total >= 2 and sections_present >= 2) or (total == 1 and sections_present == 1)

        warning = ""
        if total == 0:
            warning = "Focus keyphrase tidak ditemukan di dalam isi teks."
        elif not is_uniform:
            warning = "Distribusi kata kunci tidak merata (terkonsentrasi pada satu bagian saja)."

        return {
            "total_occurrences": total,
            "sections": {
                "intro": c1,
                "body": c2,
                "conclusion": c3
            },
            "sections_covered": sections_present,
            "is_uniform": is_uniform,
            "warning": warning
        }

    @classmethod
    def evaluate_internal_link_structure(cls, html_content: str, base_domain: str = "telkomuniversity.ac.id") -> Dict[str, Any]:
        """
        Audits internal hyperlinks for academic information architecture depth,
        canonical structure, and absence of tracking queries.
        """
        links = re.findall(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>', html_content, re.IGNORECASE)
        internal_links = []
        for href in links:
            h = href.strip()
            if h.startswith("#") or h.startswith("mailto:") or h.startswith("tel:"):
                continue
            if base_domain in h.lower() or (h.startswith("/") and not h.startswith("//")):
                internal_links.append(h)

        if not internal_links:
            return {
                "total_internal_links": 0,
                "has_internal_links": False,
                "links": [],
                "warnings": ["Tidak ada tautan internal prodi/kampus dalam konten."]
            }

        warnings = []
        links_detail = []
        for link in internal_links:
            has_tracking = bool(re.search(r'\?(?:utm_|fbclid|gclid)', link, re.IGNORECASE))
            if has_tracking:
                warnings.append(f"Tautan internal '{link}' mengandung parameter tracking/query string.")

            path = link.split("?")[0].split("#")[0]
            if base_domain in path:
                path = path.split(base_domain, 1)[-1]
            segments = [s for s in path.strip("/").split("/") if s]
            depth = len(segments)
            if depth > 4:
                warnings.append(f"Kedalaman URL tautan '{link}' terlalu dalam (kedalaman {depth} > 4).")

            links_detail.append({"href": link, "depth": depth, "has_tracking": has_tracking})

        return {
            "total_internal_links": len(internal_links),
            "has_internal_links": len(internal_links) > 0,
            "links": links_detail,
            "warnings": warnings,
            "is_optimal": len(warnings) == 0
        }

    @classmethod
    def audit_outbound_links_security(cls, html_content: str, base_domain: str = "telkomuniversity.ac.id") -> Dict[str, Any]:
        """
        Audits all external hyperlinks to ensure they adhere to strict security
        requirements (target="_blank" and rel="noopener noreferrer").
        """
        external_tags = []
        for match in re.finditer(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>', html_content, re.IGNORECASE):
            full_tag = match.group(0)
            href = match.group(1).strip()
            if href.startswith("#") or (href.startswith("/") and not href.startswith("//")) or base_domain in href.lower() or href.startswith("mailto:") or href.startswith("tel:"):
                continue
            external_tags.append((full_tag, href))

        if not external_tags:
            return {
                "total_outbound_links": 0,
                "compliant_count": 0,
                "non_compliant_count": 0,
                "is_secure": True,
                "issues": []
            }

        issues = []
        compliant_count = 0
        for tag, href in external_tags:
            has_blank = bool(re.search(r'target=["\']_blank["\']', tag, re.IGNORECASE))
            rel_match = re.search(r'rel=["\']([^"\']*)["\']', tag, re.IGNORECASE)
            rel_tokens = set(rel_match.group(1).lower().split()) if rel_match else set()
            has_rel = "noopener" in rel_tokens and "noreferrer" in rel_tokens

            if has_blank and has_rel:
                compliant_count += 1
            else:
                missing = []
                if not has_blank:
                    missing.append('target="_blank"')
                if not has_rel:
                    missing.append('rel="noopener noreferrer"')
                issues.append(f"Tautan eksternal '{href}' tidak memiliki: {', '.join(missing)}.")

        return {
            "total_outbound_links": len(external_tags),
            "compliant_count": compliant_count,
            "non_compliant_count": len(issues),
            "is_secure": len(issues) == 0,
            "issues": issues
        }

    @staticmethod
    def evaluate_meta_and_og_alignment(
        seo_title: str,
        og_title: str,
        meta_description: str,
        og_description: str
    ) -> Dict[str, Any]:
        """
        Evaluates consistency between search engine meta tags and Open Graph social cards.
        Detects significant discrepancy or missing fields.
        """
        issues = []
        if not og_title:
            issues.append("Open Graph title (og:title) tidak didefinisikan.")
        elif len(og_title) > 95:
            issues.append(f"og:title terlalu panjang ({len(og_title)} karakter, batas wajar 95).")

        if not og_description:
            issues.append("Open Graph description (og:description) tidak didefinisikan.")
        elif len(og_description) > 200:
            issues.append(f"og:description terlalu panjang ({len(og_description)} karakter, batas wajar 200).")

        title_overlap = 1.0
        if seo_title and og_title:
            s_words = set(re.findall(r'\w+', seo_title.lower()))
            o_words = set(re.findall(r'\w+', og_title.lower()))
            if s_words and o_words:
                title_overlap = round(len(s_words & o_words) / len(s_words | o_words), 2)
                if title_overlap < 0.3:
                    issues.append(f"og:title memiliki korelasi rendah dengan seo_title (kemiripan: {title_overlap}).")

        return {
            "title_similarity": title_overlap,
            "is_aligned": len(issues) == 0,
            "issues": issues
        }

    @staticmethod
    def validate_academic_journal_references(html_content: str) -> Dict[str, Any]:
        """
        Validates academic journal links, DOIs, and citation indices (SINTA, Scopus, IEEE, ACM).
        Ensures DOIs use https://doi.org/ canonical format rather than dx.doi.org or raw strings.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        dois_found = []
        sinta_tiers = []
        issues = []

        doi_regex = re.compile(r'\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+\b')
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if "doi.org" in href.lower():
                if href.startswith("http://"):
                    issues.append(f"DOI link '{href}' menggunakan HTTP tidak aman; gunakan HTTPS.")
                elif "dx.doi.org" in href.lower():
                    issues.append(f"DOI link '{href}' menggunakan domain usang dx.doi.org; ganti ke https://doi.org/.")
                else:
                    dois_found.append(href)
            elif doi_regex.search(href):
                dois_found.append(href)

        text = soup.get_text()
        sinta_matches = re.findall(r'\bSINTA\s*([1-6])\b', text, re.IGNORECASE)
        for s in sinta_matches:
            tier = f"SINTA {s}"
            if tier not in sinta_tiers:
                sinta_tiers.append(tier)

        has_scopus = bool(re.search(r'\bScopus\b', text, re.IGNORECASE))
        has_wos = bool(re.search(r'\b(Web of Science|WoS)\b', text, re.IGNORECASE))

        return {
            "doi_count": len(dois_found),
            "dois": dois_found,
            "sinta_tiers": sorted(sinta_tiers),
            "has_scopus_mention": has_scopus,
            "has_wos_mention": has_wos,
            "issues": issues,
            "is_valid": len(issues) == 0
        }

    @staticmethod
    def audit_table_accessibility(html_content: str) -> Dict[str, Any]:
        """
        Audits HTML table structures for accessibility and search crawler clarity.
        Checks for presence of <caption> or aria-label/aria-describedby, and <th> elements with scope="col|row".
        """
        soup = BeautifulSoup(html_content, "html.parser")
        tables = soup.find_all("table")
        if not tables:
            return {
                "total_tables": 0,
                "accessible_tables": 0,
                "is_compliant": True,
                "issues": []
            }

        issues = []
        compliant_count = 0

        for idx, table in enumerate(tables, 1):
            table_issues = []
            has_caption = bool(table.find("caption") or table.get("aria-label") or table.get("aria-describedby"))
            if not has_caption:
                table_issues.append(f"Tabel #{idx} tidak memiliki <caption> atau atribut aria-label.")

            th_tags = table.find_all("th")
            if not th_tags:
                table_issues.append(f"Tabel #{idx} tidak memiliki elemen header <th>.")
            else:
                missing_scope = [th for th in th_tags if not th.get("scope")]
                if missing_scope:
                    table_issues.append(f"Tabel #{idx} memiliki {len(missing_scope)} tag <th> tanpa atribut 'scope'.")

            if table_issues:
                issues.extend(table_issues)
            else:
                compliant_count += 1

        return {
            "total_tables": len(tables),
            "accessible_tables": compliant_count,
            "is_compliant": len(issues) == 0,
            "issues": issues
        }

    @staticmethod
    def evaluate_content_freshness_discrepancy(
        html_content: str,
        publish_year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Evaluates temporal references in article body against the target publication year.
        Detects legacy date references (>5 years old) that might signal stale technical content.
        """
        if publish_year is None:
            publish_year = datetime.now().year

        soup = BeautifulSoup(html_content, "html.parser")
        text = soup.get_text()

        years_found = [int(y) for y in re.findall(r'\b(19\d{2}|20\d{2})\b', text)]
        if not years_found:
            return {
                "years_found": [],
                "target_year": publish_year,
                "stale_reference_count": 0,
                "is_fresh": True,
                "issues": []
            }

        stale_threshold = publish_year - 5
        stale_years = [y for y in years_found if y < stale_threshold]
        issues = []

        if stale_years:
            unique_stale = sorted(set(stale_years))
            issues.append(f"Ditemukan referensi tahun yang berpotensi usang (< {stale_threshold}): {unique_stale}.")

        future_years = [y for y in years_found if y > publish_year + 2]
        if future_years:
            issues.append(f"Ditemukan referensi tahun masa depan anomali: {sorted(set(future_years))}.")

        return {
            "years_found": sorted(set(years_found)),
            "target_year": publish_year,
            "stale_reference_count": len(stale_years),
            "is_fresh": len(issues) == 0,
            "issues": issues
        }

    @staticmethod
    def validate_breadcrumb_hierarchy(breadcrumbs: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Validates breadcrumb navigation trail structure for SEO hierarchy standards.
        """
        issues = []
        if not breadcrumbs or len(breadcrumbs) < 2:
            issues.append("Breadcrumb hierarchy must contain at least 2 levels.")
            return {
                "depth": len(breadcrumbs) if breadcrumbs else 0,
                "is_valid": False,
                "issues": issues
            }

        depth = len(breadcrumbs)
        for idx, item in enumerate(breadcrumbs):
            name = item.get("name", "").strip()
            url = item.get("url", "").strip()
            if not name:
                issues.append(f"Breadcrumb item at level {idx + 1} has empty name.")
            if idx == 0 and not (url == "/" or "telkomuniversity.ac.id" in url or "home" in name.lower() or "beranda" in name.lower()):
                issues.append("Root breadcrumb item must represent Home or site root.")

        return {
            "depth": depth,
            "is_valid": len(issues) == 0,
            "issues": issues
        }

    @staticmethod
    def audit_css_color_contrast(html_content: str) -> Dict[str, Any]:
        """
        Audits inline style color and background combinations against WCAG AA standards.
        """
        issues = []
        soup = BeautifulSoup(html_content, "html.parser")
        elements_with_style = soup.find_all(style=True)

        checked_count = 0
        for el in elements_with_style:
            style = el["style"].lower()
            fg_match = re.search(r'(?:^|;)\s*color\s*:\s*([^;]+)', style)
            bg_match = re.search(r'(?:^|;)\s*background(?:-color)?\s*:\s*([^;]+)', style)

            if fg_match and bg_match:
                checked_count += 1
                fg = fg_match.group(1).strip().replace(" ", "")
                bg = bg_match.group(1).strip().replace(" ", "")
                if fg == bg:
                    issues.append(f"Elemen <{el.name}> memiliki warna teks dan latar belakang yang identik: '{fg}'.")
                elif (fg in ("#fff", "#ffffff", "white") and bg in ("#fff", "#ffffff", "white")) or \
                     (fg in ("#000", "#000000", "black") and bg in ("#000", "#000000", "black")):
                    issues.append(f"Elemen <{el.name}> berisiko tidak terbaca (kontras nol).")

        return {
            "elements_audited": checked_count,
            "is_accessible": len(issues) == 0,
            "issues": issues
        }

    @staticmethod
    def validate_og_image_specifications(
        image_url: str,
        width: Optional[int] = None,
        height: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Validates Open Graph image URL and dimensions according to social platform standards.
        """
        issues = []
        if not image_url:
            issues.append("OG image URL tidak boleh kosong.")
            return {"is_valid": False, "issues": issues}

        if not image_url.startswith("https://"):
            issues.append("OG image URL harus menggunakan protokol HTTPS.")

        valid_exts = (".jpg", ".jpeg", ".png", ".webp")
        path_part = image_url.split("?")[0].lower()
        if not any(path_part.endswith(ext) for ext in valid_exts):
            issues.append(f"Format gambar OG harus berupa salah satu dari {valid_exts}.")

        if width is not None and height is not None:
            if width < 600 or height < 315:
                issues.append(f"Dimensi gambar OG ({width}x{height}) terlalu kecil (minimal 600x315, disarankan 1200x630).")
            aspect_ratio = round(width / height, 2) if height > 0 else 0
            if aspect_ratio < 1.0 or aspect_ratio > 2.2:
                issues.append(f"Aspek rasio gambar OG ({aspect_ratio}:1) di luar batas standar 1.91:1.")

        return {
            "image_url": image_url,
            "width": width,
            "height": height,
            "is_valid": len(issues) == 0,
            "issues": issues
        }

    @staticmethod
    def calculate_indonesian_coleman_liau(text: str) -> Dict[str, Any]:
        """
        Calculates Coleman-Liau Readability Index adapted for Indonesian prose.
        CLI = 0.0588 * L - 0.296 * S - 15.8
        """
        if not text:
            return {"grade_level": 0, "difficulty": "Tidak ada teks", "score": 0.0}

        clean = re.sub(r'<[^>]+>', ' ', text)
        words = re.findall(r'\b[A-Za-z0-9_-]+\b', clean)
        num_words = len(words)
        if num_words == 0:
            return {"grade_level": 0, "difficulty": "Tidak ada teks", "score": 0.0}

        num_letters = sum(len(w) for w in words)
        sentences = [s for s in re.split(r'[.!?]+', clean) if s.strip()]
        num_sentences = max(1, len(sentences))

        L = (num_letters / num_words) * 100.0
        S = (num_sentences / num_words) * 100.0

        cli_score = 0.0588 * L - 0.296 * S - 15.8
        grade_level = max(1, round(cli_score))

        if grade_level <= 6:
            difficulty = "Sangat Mudah (SD)"
        elif grade_level <= 9:
            difficulty = "Mudah (SMP)"
        elif grade_level <= 12:
            difficulty = "Menengah (SMA / Umum)"
        elif grade_level <= 16:
            difficulty = "Tinggi (Sarjana)"
        else:
            difficulty = "Sangat Spesifik / Akademik Lanjut"

        return {
            "score": round(cli_score, 2),
            "grade_level": grade_level,
            "difficulty": difficulty,
            "word_count": num_words,
            "sentence_count": num_sentences
        }

    @staticmethod
    def validate_hreflang_alternates(alternates: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Validates multilingual SEO hreflang annotations.
        """
        valid_langs = {"id", "en", "x-default", "id-id", "en-us", "en-gb"}
        issues = []
        if not alternates:
            return {"is_valid": False, "count": 0, "issues": ["Daftar hreflang alternate kosong."]}

        has_x_default = False
        for idx, alt in enumerate(alternates, 1):
            lang = alt.get("lang", "").strip().lower()
            href = alt.get("href", "").strip()

            if not lang:
                issues.append(f"Hreflang #{idx} tidak memiliki atribut 'lang'.")
            elif lang not in valid_langs:
                issues.append(f"Hreflang #{idx} menggunakan kode bahasa tidak standar: '{lang}'.")

            if lang == "x-default":
                has_x_default = True

            if not href.startswith("https://"):
                issues.append(f"Hreflang #{idx} ({lang}) harus menggunakan URL HTTPS absolut.")

        if not has_x_default:
            issues.append("Rekomendasi SEO internasional: tag 'x-default' fallback tidak ditemukan.")

        return {
            "is_valid": len([i for i in issues if "Rekomendasi" not in i]) == 0,
            "has_x_default": has_x_default,
            "count": len(alternates),
            "issues": issues
        }

    @staticmethod
    def audit_aria_landmarks(html_content: str) -> Dict[str, Any]:
        """
        Audits accessibility landmark regions and checks for accessible labelling.
        """
        issues = []
        soup = BeautifulSoup(html_content, "html.parser")

        has_main_or_article = bool(soup.find(["main", "article"]) or soup.find(attrs={"role": "main"}))
        if not has_main_or_article:
            issues.append("Dokumen tidak memiliki landmark semantik utama (<main>, <article>, atau role='main').")

        navs = soup.find_all(["nav", lambda el: el.has_attr("role") and el["role"] == "navigation"])
        unlabelled_navs = [n for n in navs if not (n.get("aria-label") or n.get("aria-labelledby"))]
        if unlabelled_navs:
            issues.append(f"{len(unlabelled_navs)} elemen navigasi (<nav>) tidak memiliki label aksesibilitas (aria-label).")

        return {
            "has_main": has_main_or_article,
            "total_navs": len(navs),
            "is_accessible": len(issues) == 0,
            "issues": issues
        }

    @staticmethod
    def validate_canonical_url(
        canonical_url: str,
        current_slug: str,
        domain: str = "bif-pwt.telkomuniversity.ac.id"
    ) -> Dict[str, Any]:
        """
        Validates canonical URL structure and ensures proper trailing slash and domain formatting.
        """
        issues = []
        if not canonical_url:
            return {"is_valid": False, "issues": ["URL kanonikal tidak boleh kosong."]}

        if not canonical_url.startswith("https://"):
            issues.append("URL kanonikal harus menggunakan protokol aman HTTPS.")

        if domain not in canonical_url:
            issues.append(f"URL kanonikal harus mengarah ke domain resmi prodi ({domain}).")

        if current_slug and current_slug not in canonical_url:
            issues.append(f"URL kanonikal tidak memuat slug artikel '{current_slug}'.")

        if "?" in canonical_url or "#" in canonical_url:
            issues.append("URL kanonikal tidak boleh memuat query parameter atau fragment hash.")

        if not canonical_url.endswith("/"):
            issues.append("URL kanonikal harus berakhiran trailing slash ('/') sesuai standar WordPress prodi.")

        return {
            "canonical_url": canonical_url,
            "is_valid": len(issues) == 0,
            "issues": issues
        }

    @staticmethod
    def audit_paragraph_rhythm(html_content: str, max_words_per_p: int = 120) -> Dict[str, Any]:
        """
        Audits paragraph lengths for editorial rhythm and scannability.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        paragraphs = soup.find_all("p")

        issues = []
        p_data = []
        for idx, p in enumerate(paragraphs, 1):
            text = p.get_text().strip()
            words = re.findall(r'\b[A-Za-z0-9_-]+\b', text)
            word_count = len(words)
            p_data.append(word_count)

            if word_count > max_words_per_p:
                issues.append(f"Paragraf #{idx} terlalu padat ({word_count} kata, maksimal {max_words_per_p} kata disarankan).")

        return {
            "total_paragraphs": len(paragraphs),
            "word_counts": p_data,
            "max_words": max(p_data) if p_data else 0,
            "avg_words": round(sum(p_data) / len(p_data), 1) if p_data else 0.0,
            "is_optimal": len(issues) == 0,
            "issues": issues
        }

    @staticmethod
    def audit_heading_hierarchy_skips(html_content: str) -> Dict[str, Any]:
        """
        Audits semantic heading hierarchy in article body for skipped levels (e.g. h2 to h4),
        missing h1/h2 tags, or multiple h1 declarations.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        headings = soup.find_all(re.compile(r"^h[1-6]$"))

        issues = []
        headings_seq = []
        last_level = 0
        h1_count = 0

        for h in headings:
            level = int(h.name[1])
            text = h.get_text().strip()
            headings_seq.append({"level": level, "text": text[:50]})

            if level == 1:
                h1_count += 1
                if h1_count > 1:
                    issues.append(f"Multiple <h1> tags detected; only one <h1> should be present per article (found: '{text[:40]}...').")

            if last_level > 0 and level > last_level + 1:
                issues.append(f"Heading level skipped from <h{last_level}> directly to <h{level}> without intermediate level (found: '{text[:40]}...').")

            last_level = level

        return {
            "total_headings": len(headings),
            "h1_count": h1_count,
            "headings_sequence": headings_seq,
            "is_valid": len(issues) == 0,
            "issues": issues
        }

    @staticmethod
    def check_indonesian_inflected_keyphrase(keyphrase: str, text: str) -> Dict[str, Any]:
        """
        Validates presence and frequency of keyphrase including Indonesian morphological
        inflections (prefixes: me-, mem-, men-, meng-, meny-, di-, ber-, ter-, pe-, per-,
        suffixes: -kan, -i, -an).
        """
        if not keyphrase or not text:
            return {
                "keyphrase": keyphrase,
                "exact_matches": 0,
                "inflected_matches": 0,
                "total_matches": 0,
                "found_forms": [],
                "is_present": False
            }

        clean_text = re.sub(r'<[^>]+>', ' ', text).lower()
        words = keyphrase.strip().lower().split()

        prefixes = r'(?:me(?:ng|m|n|ny)?|di|ber|ter|pe(?:ng|m|n|ny)?|per)?'
        suffixes = r'(?:kan|i|an)?'

        pattern_parts = []
        for w in words:
            pattern_parts.append(rf'\b{prefixes}{re.escape(w)}{suffixes}\b')

        pattern = re.compile(r'\s+'.join(pattern_parts), re.IGNORECASE)

        exact_matches = clean_text.count(keyphrase.strip().lower())
        all_matches = [m.group(0) for m in pattern.finditer(clean_text)]
        unique_forms = sorted(set(all_matches))
        inflected_count = len(all_matches) - exact_matches

        return {
            "keyphrase": keyphrase,
            "exact_matches": exact_matches,
            "inflected_matches": max(0, inflected_count),
            "total_matches": len(all_matches),
            "found_forms": unique_forms,
            "is_present": len(all_matches) > 0
        }

    @staticmethod
    def validate_twitter_card_meta(meta_tags_html: str) -> Dict[str, Any]:
        """
        Validates Twitter Card metadata markup (twitter:card, title, description, and image URL).
        """
        if not meta_tags_html:
            return {"is_valid": False, "issues": ["Meta tags HTML kosong."]}

        soup = BeautifulSoup(meta_tags_html, "html.parser")
        issues = []

        def get_meta_content(name: str) -> str:
            tag = soup.find("meta", attrs={"name": name}) or soup.find("meta", attrs={"property": name})
            return tag.get("content", "").strip() if tag else ""

        card = get_meta_content("twitter:card")
        title = get_meta_content("twitter:title")
        desc = get_meta_content("twitter:description")
        image = get_meta_content("twitter:image")

        if not card:
            issues.append("Tag 'twitter:card' tidak ditemukan.")
        elif card not in ("summary", "summary_large_image", "app", "player"):
            issues.append(f"Nilai 'twitter:card' tidak standar: '{card}'.")

        if not title:
            issues.append("Tag 'twitter:title' tidak ditemukan.")
        elif len(title) > 70:
            issues.append(f"Nilai 'twitter:title' terlalu panjang ({len(title)} chars, optimal <= 70).")

        if not desc:
            issues.append("Tag 'twitter:description' tidak ditemukan.")
        elif len(desc) > 200:
            issues.append(f"Nilai 'twitter:description' terlalu panjang ({len(desc)} chars, optimal <= 200).")

        if not image:
            issues.append("Tag 'twitter:image' tidak ditemukan.")
        elif not image.startswith("https://"):
            issues.append("Tag 'twitter:image' harus menggunakan URL absolut HTTPS.")

        return {
            "card": card,
            "title": title,
            "description": desc,
            "image": image,
            "is_valid": len(issues) == 0,
            "issues": issues
        }

    @staticmethod
    def check_consecutive_sentence_starts(text: str, threshold: int = 3) -> Dict[str, Any]:
        """
        Audits consecutive sentences starting with the same initial word (Yoast readability rule).
        Flags when threshold or more consecutive sentences begin with identical wording.
        """
        if not text:
            return {"consecutive_groups": [], "has_repetitive_starts": False, "total_sentences": 0}

        clean = re.sub(r'<[^>]+>', ' ', text)
        sentences = [s.strip() for s in re.split(r'[.!?]+', clean) if s.strip()]

        first_words = []
        for s in sentences:
            m = re.match(r'^[^\w]*([A-Za-z0-9_-]+)', s)
            if m:
                first_words.append((m.group(1).lower(), s[:40]))
            else:
                first_words.append(("", ""))

        consecutive_groups = []
        if len(first_words) >= threshold:
            current_word = None
            current_count = 0
            for w, snippet in first_words:
                if w and w == current_word:
                    current_count += 1
                else:
                    if current_count >= threshold:
                        consecutive_groups.append({
                            "word": current_word,
                            "occurrences": current_count
                        })
                    current_word = w if w else None
                    current_count = 1 if w else 0

            if current_count >= threshold:
                consecutive_groups.append({
                    "word": current_word,
                    "occurrences": current_count
                })

        return {
            "consecutive_groups": consecutive_groups,
            "has_repetitive_starts": len(consecutive_groups) > 0,
            "total_sentences": len(sentences)
        }

    @classmethod
    def evaluate_paragraph_transition_distribution(cls, html_content: str, min_ratio: float = 0.3) -> Dict[str, Any]:
        """
        Evaluates the distribution of Indonesian transitional markers across all content paragraphs.
        Ensures smooth reading flow where at least 30% of multi-sentence paragraphs feature transition words.
        """
        if not html_content:
            return {"total_paragraphs": 0, "paragraphs_with_transitions": 0, "ratio": 0.0, "is_optimal": False}

        soup = BeautifulSoup(html_content, "html.parser")
        paragraphs = soup.find_all("p")
        if not paragraphs:
            return {"total_paragraphs": 0, "paragraphs_with_transitions": 0, "ratio": 0.0, "is_optimal": True}

        with_transitions = 0
        details = []

        for idx, p in enumerate(paragraphs, 1):
            text = p.get_text().strip().lower()
            found_tw = [tw for tw in cls.INDONESIAN_TRANSITION_WORDS if re.search(r'\b' + re.escape(tw) + r'\b', text)]
            has_tw = len(found_tw) > 0
            if has_tw:
                with_transitions += 1
            details.append({"index": idx, "has_transition": has_tw, "transitions_found": found_tw[:3]})

        ratio = round(with_transitions / len(paragraphs), 2)
        is_optimal = ratio >= min_ratio

        return {
            "total_paragraphs": len(paragraphs),
            "paragraphs_with_transitions": with_transitions,
            "ratio": ratio,
            "percentage": round(ratio * 100, 1),
            "is_optimal": is_optimal,
            "details": details
        }

    @staticmethod
    def validate_meta_description_cta(meta_description: str) -> Dict[str, Any]:
        """
        Validates presence of call-to-action (CTA) engagement verbs in meta description.
        Encourages higher search engine result click-through rates (CTR).
        """
        if not meta_description:
            return {"has_cta": False, "matched_ctas": [], "is_optimal": False, "warning": "Meta description is empty."}

        clean = meta_description.strip().lower()
        cta_keywords = [
            "pelajari", "simak", "temukan", "baca", "daftar", "ketahui", "dapatkan",
            "lihat", "eksplorasi", "kunjungi", "pahami", "ikuti", "cek",
            "learn", "discover", "explore", "read", "check", "find"
        ]

        matched = []
        for kw in cta_keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', clean):
                matched.append(kw)

        has_cta = len(matched) > 0
        warning = "" if has_cta else "Meta description disarankan memuat ajakan bertindak (CTA seperti 'pelajari', 'simak', 'temukan')."

        return {
            "has_cta": has_cta,
            "matched_ctas": matched,
            "is_optimal": has_cta,
            "warning": warning
        }

    @staticmethod
    def validate_embedded_json_ld(html_content: str) -> Dict[str, Any]:
        """
        Parses and validates embedded Schema.org JSON-LD scripts in HTML content.
        Verifies valid JSON syntax, @context, @type, and schema-specific essential properties.
        """
        if not html_content:
            return {"total_schemas": 0, "schemas": [], "is_valid": True, "issues": []}

        soup = BeautifulSoup(html_content, "html.parser")
        scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
        if not scripts:
            return {"total_schemas": 0, "schemas": [], "is_valid": True, "issues": []}

        import json
        issues = []
        schemas_info = []

        for idx, s in enumerate(scripts, 1):
            raw_text = s.string or s.get_text() or ""
            if not raw_text.strip():
                issues.append(f"JSON-LD script #{idx} kosong.")
                continue

            try:
                data = json.loads(raw_text.strip())
            except Exception as e:
                issues.append(f"JSON-LD script #{idx} gagal diparse: {str(e)}.")
                continue

            context = data.get("@context", "")
            schema_type = data.get("@type", "")

            if not context or "schema.org" not in context.lower():
                issues.append(f"JSON-LD script #{idx} tidak memiliki @context 'https://schema.org'.")

            if not schema_type:
                issues.append(f"JSON-LD script #{idx} tidak memiliki properti '@type'.")

            if schema_type in ("Article", "ScholarlyArticle", "NewsArticle"):
                if not (data.get("headline") or data.get("name")):
                    issues.append(f"Schema {schema_type} #{idx} memerlukan properti 'headline' atau 'name'.")
            elif schema_type == "Course":
                if not data.get("name"):
                    issues.append(f"Schema Course #{idx} memerlukan properti 'name'.")
            elif schema_type in ("Event", "EducationEvent"):
                if not data.get("name") or not data.get("startDate"):
                    issues.append(f"Schema {schema_type} #{idx} memerlukan 'name' dan 'startDate'.")

            schemas_info.append({"index": idx, "type": schema_type, "context": context})

        return {
            "total_schemas": len(scripts),
            "schemas": schemas_info,
            "is_valid": len(issues) == 0,
            "issues": issues
        }

    @classmethod
    def calculate_gunning_fog_index(cls, text: str) -> Dict[str, Any]:
        """
        Calculates the Gunning Fog readability index adapted for Indonesian academic prose,
        classifying complex polysyllabic words (>= 4 syllables) and average sentence length.
        """
        if not text:
            return {"grade_level": 0.0, "total_words": 0, "total_sentences": 0, "complex_words": 0, "difficulty": "Tidak Cukup Data"}

        clean = re.sub(r'<[^>]+>', ' ', text)
        sentences = [s.strip() for s in re.split(r'[\.\?!]+', clean) if s.strip() and len(s.split()) >= 2]
        words = [w.strip() for w in re.findall(r'\b[a-zA-Z0-9_-]+\b', clean) if w.strip()]

        total_words = len(words)
        total_sentences = len(sentences)
        if total_words < 5 or total_sentences == 0:
            return {"grade_level": 0.0, "total_words": total_words, "total_sentences": total_sentences, "complex_words": 0, "difficulty": "Tidak Cukup Data"}

        complex_count = 0
        for w in words:
            if cls.count_syllables_indonesian(w) >= 4:
                complex_count += 1

        asl = total_words / total_sentences
        complex_pct = (complex_count / total_words) * 100.0
        fog = round(0.4 * (asl + complex_pct), 1)

        if fog <= 10.0:
            difficulty = "Mudah Dipahami (Pembaca Umum)"
        elif fog <= 14.0:
            difficulty = "Menengah (Mahasiswa Sarjana)"
        elif fog <= 18.0:
            difficulty = "Tinggi (Akademik & Jurnal Ilmiah)"
        else:
            difficulty = "Sangat Sulit (Pascasarjana / Spesialis)"

        return {
            "grade_level": fog,
            "total_words": total_words,
            "total_sentences": total_sentences,
            "complex_words": complex_count,
            "complex_percentage": round(complex_pct, 1),
            "difficulty": difficulty
        }

    @classmethod
    def audit_in_page_anchors(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits in-page hash anchor links (href="#...") against element id and name attributes
        to prevent dead intra-page navigational jumps and broken table-of-contents targets.
        """
        if not html_content:
            return {"total_anchors": 0, "valid_anchors": [], "broken_anchors": [], "is_valid": True, "warnings": []}

        soup = BeautifulSoup(html_content, "html.parser")
        existing_ids = set()
        for tag in soup.find_all(True):
            if tag.get("id"):
                existing_ids.add(tag["id"].strip())
            if tag.get("name"):
                existing_ids.add(tag["name"].strip())

        valid = []
        broken = []
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if href.startswith("#") and len(href) > 1:
                target_id = href[1:]
                if target_id in existing_ids:
                    valid.append(href)
                else:
                    broken.append(href)

        warnings = []
        if broken:
            warnings.append(f"Ditemukan {len(broken)} tautan jangkar internal tanpa elemen tujuan: {', '.join(broken)}")

        return {
            "total_anchors": len(valid) + len(broken),
            "valid_anchors": valid,
            "broken_anchors": broken,
            "is_valid": len(broken) == 0,
            "warnings": warnings
        }

    @classmethod
    def validate_author_academic_credentials(cls, author_name: str, bio_text: str = "") -> Dict[str, Any]:
        """
        Validates academic credentials, titles, and persistent researcher identifiers (ORCID)
        to reinforce Google E-E-A-T signals for university faculty authors.
        """
        combined = f"{author_name or ''} {bio_text or ''}".strip()
        if not combined:
            return {
                "has_credentials": False,
                "detected_titles": [],
                "has_orcid": False,
                "orcid_id": None,
                "is_authoritative": False
            }

        title_patterns = [
            r'\bProf(?:\.|\b)', r'\bDr(?:\.|\b)', r'\bPh\.?D\b',
            r'\bM\.?Kom\b\.?', r'\bS\.?Kom\b\.?', r'\bM\.?T\b\.?', r'\bS\.?T\b\.?',
            r'\bM\.?Sc\b\.?', r'\bB\.?Sc\b\.?', r'\bM\.?Si\b\.?', r'\bS\.?Si\b\.?',
            r'\bIr(?:\.|\b)'
        ]
        detected = []
        for pat in title_patterns:
            m = re.search(pat, combined, re.IGNORECASE)
            if m:
                detected.append(m.group(0).strip())

        orcid_match = re.search(r'\b(?:https?://orcid\.org/)?(000[0-9]-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X])\b', combined, re.IGNORECASE)
        orcid_id = orcid_match.group(1) if orcid_match else None

        has_cred = len(detected) > 0
        has_orcid = orcid_id is not None
        is_auth = has_cred or has_orcid

        return {
            "has_credentials": has_cred,
            "detected_titles": sorted(list(set(detected))),
            "has_orcid": has_orcid,
            "orcid_id": orcid_id,
            "is_authoritative": is_auth
        }

    @classmethod
    def validate_academic_open_access_disclaimer(cls, html_content: str) -> Dict[str, Any]:
        """
        Validates presence of Open Access licensing terms and Creative Commons notices
        for scholarly academic repository indexing and institutional compliance.
        """
        if not html_content:
            return {"has_license": False, "license_type": "None", "is_compliant": False, "warning": "Content is empty."}

        soup = BeautifulSoup(html_content, "html.parser")
        text = soup.get_text()

        cc_patterns = [
            (r'\b(?:CC[\s-]BY[\s-]NC[\s-]ND|Creative Commons Attribution-NonCommercial-NoDerivatives)\b', "CC BY-NC-ND"),
            (r'\b(?:CC[\s-]BY[\s-]NC[\s-]SA|Creative Commons Attribution-NonCommercial-ShareAlike)\b', "CC BY-NC-SA"),
            (r'\b(?:CC[\s-]BY[\s-]NC|Creative Commons Attribution-NonCommercial)\b', "CC BY-NC"),
            (r'\b(?:CC[\s-]BY[\s-]SA|Creative Commons Attribution-ShareAlike)\b', "CC BY-SA"),
            (r'\b(?:CC[\s-]BY|Creative Commons Attribution)\b', "CC BY"),
            (r'\b(?:Open Access|Akses Terbuka|Public Domain|CC0)\b', "Open Access / Public Domain")
        ]

        detected_license = None
        for pattern, lic_name in cc_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                detected_license = lic_name
                break

        if not detected_license:
            license_link = soup.find("a", rel=lambda r: r and "license" in r.lower())
            if license_link:
                detected_license = license_link.get_text().strip() or "Creative Commons License Link"

        has_lic = detected_license is not None
        warning = "" if has_lic else "Artikel ilmiah disarankan memuat pernyataan lisensi terbuka (Creative Commons / Open Access)."

        return {
            "has_license": has_lic,
            "license_type": detected_license or "None",
            "is_compliant": has_lic,
            "warning": warning
        }

    @staticmethod
    def calculate_coleman_liau_index(text: str) -> Dict[str, Any]:
        """
        Calculates Coleman-Liau Readability Index for Indonesian academic texts.
        Formula: CLI = 0.0588 * L - 0.296 * S - 15.8
        where L = letters per 100 words, S = sentences per 100 words.
        """
        if not text or not text.strip():
            return {
                "score": 0.0,
                "grade_level": "N/A",
                "difficulty": "Teks kosong",
                "letters_per_100_words": 0.0,
                "sentences_per_100_words": 0.0
            }

        # Clean HTML tags if present
        plain = re.sub(r'<[^>]+>', ' ', text)
        words = re.findall(r'\b[a-zA-Z0-9_-]+\b', plain)
        word_count = len(words)
        if word_count == 0:
            return {
                "score": 0.0,
                "grade_level": "N/A",
                "difficulty": "Tidak ada kata terdeteksi",
                "letters_per_100_words": 0.0,
                "sentences_per_100_words": 0.0
            }

        letter_count = sum(len(w) for w in words)
        sentences = [s.strip() for s in re.split(r'[.!?]+', plain) if s.strip()]
        sentence_count = max(1, len(sentences))

        l_val = (letter_count / word_count) * 100.0
        s_val = (sentence_count / word_count) * 100.0

        cli_score = round(0.0588 * l_val - 0.296 * s_val - 15.8, 1)

        if cli_score <= 6.0:
            diff = "Mudah dibaca (Tingkat Sekolah Dasar / Menengah)"
        elif cli_score <= 10.0:
            diff = "Menengah (Tingkat SMA / Populer)"
        elif cli_score <= 14.0:
            diff = "Akademik Standar (Tingkat Sarjana / S1)"
        else:
            diff = "Kompleksitas Tinggi (Pascasarjana / Peneliti Spesialis)"

        return {
            "score": cli_score,
            "grade_level": f"Tingkat {max(1, int(round(cli_score)))}",
            "difficulty": diff,
            "letters_per_100_words": round(l_val, 1),
            "sentences_per_100_words": round(s_val, 1)
        }

    @staticmethod
    def audit_heading_hierarchy_order(html_content: str) -> Dict[str, Any]:
        """
        Audits semantic heading hierarchy sequence to ensure logical heading progression
        without skipped levels (e.g. H2 jumping straight to H4 skipping H3, or duplicate H1).
        """
        if not html_content or not html_content.strip():
            return {
                "is_valid": True,
                "heading_count": 0,
                "headings_sequence": [],
                "issues": []
            }

        soup = BeautifulSoup(html_content, "html.parser")
        headings = soup.find_all(re.compile(r'^h[1-6]$', re.IGNORECASE))

        seq = []
        issues = []
        h1_count = 0
        prev_level = None

        for h in headings:
            lvl = int(h.name[1])
            txt = h.get_text().strip()
            seq.append({"level": lvl, "text": txt[:60]})

            if lvl == 1:
                h1_count += 1
                if h1_count > 1:
                    issues.append(f"Ditemukan lebih dari satu tag H1 ('{txt[:40]}...'). Halaman artikel hanya boleh memiliki satu H1 utama.")

            if prev_level is not None:
                # If moving deeper into subheadings, level can increase at most by 1
                if lvl > prev_level + 1:
                    issues.append(f"Lompatan hirarki subjudul tidak runtut: H{prev_level} langsung meloncat ke H{lvl} ('{txt[:40]}...'). Disarankan menggunakan H{prev_level + 1}.")

            prev_level = lvl

        return {
            "is_valid": len(issues) == 0,
            "heading_count": len(headings),
            "headings_sequence": seq,
            "issues": issues
        }

    @staticmethod
    def validate_research_grant_acknowledgment(html_content: str) -> Dict[str, Any]:
        """
        Validates academic research grant funding acknowledgments (e.g. Kemendikbudristek BIMA,
        Kedaireka Matching Fund, LPDP, or internal LPPM Telkom University grant schemes)
        and extracts grant contract/SPK numbers.
        """
        if not html_content or not html_content.strip():
            return {
                "has_acknowledgment": False,
                "funding_agency": "None",
                "contract_numbers": [],
                "is_compliant": False,
                "warning": "Artikel riset tidak memuat klausul ucapan terima kasih pendanaan (grant acknowledgment)."
            }

        soup = BeautifulSoup(html_content, "html.parser")
        text = soup.get_text()

        agency_patterns = [
            (r'\b(?:BIMA|Kemendikbud(?:ristek)?|Ditjen Diktiristek)\b', "Kemendikbudristek BIMA"),
            (r'\b(?:Kedaireka|Matching Fund)\b', "Kedaireka Matching Fund"),
            (r'\b(?:LPDP|Lembaga Pengelola Dana Pendidikan)\b', "LPDP"),
            (r'\b(?:BRIN|Badan Riset dan Inovasi Nasional)\b', "BRIN"),
            (r'\b(?:LPPM|Telkom University|Dana Internal Prodi)\b', "LPPM Telkom University")
        ]

        detected_agency = None
        for pattern, agency_name in agency_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                # Ensure context of grant/funding
                if re.search(r'\b(?:hibah|pendanaan|didanai|kontrak|grant|dibiayai|acknowledg(?:e?ment)?)\b', text, re.IGNORECASE):
                    detected_agency = agency_name
                    break

        # Extract contract numbers e.g., 045/E1/KS/2026, SPK-123/LPPM/2026
        contract_patterns = re.findall(r'(?:nomor\s+kontrak|no\.?\s*kontrak|nomor|no\.?|kontrak|spk)\s*[:=]?\s*([A-Za-z0-9/_.-]{5,35})', text, re.IGNORECASE)
        clean_contracts = [c.strip(".,;: ") for c in contract_patterns if any(char.isdigit() for char in c)]

        has_ack = detected_agency is not None
        warning = "" if has_ack else "Artikel publikasi hasil riset disarankan memuat acknowledgment sumber pendanaan hibah dan nomor kontrak."

        return {
            "has_acknowledgment": has_ack,
            "funding_agency": detected_agency or "None",
            "contract_numbers": clean_contracts,
            "is_compliant": has_ack,
            "warning": warning
        }

    @staticmethod
    def audit_image_accessibility_and_dimensions(html_content: str) -> Dict[str, Any]:
        """
        Audits images for WCAG accessibility compliance (informative vs decorative alt text)
        and layout shift stability (explicit width/height attributes or aspect-ratio styles
        to prevent Cumulative Layout Shift / CLS).
        """
        if not html_content or not html_content.strip():
            return {
                "total_images": 0,
                "has_issues": False,
                "missing_alt_count": 0,
                "missing_dimensions_count": 0,
                "issues": []
            }

        soup = BeautifulSoup(html_content, "html.parser")
        images = soup.find_all("img")

        issues = []
        missing_alt = 0
        missing_dims = 0

        for idx, img in enumerate(images, 1):
            src = img.get("src", f"image_{idx}")
            alt = img.get("alt")

            # Check alt attribute presence
            if alt is None:
                missing_alt += 1
                issues.append(f"Gambar #{idx} ('{src[:30]}...') tidak memiliki atribut 'alt'.")
            elif not alt.strip() and img.get("role") != "presentation":
                issues.append(f"Gambar #{idx} memiliki alt kosong tanpa role='presentation'.")
            else:
                alt_clean = alt.strip().lower()
                if alt_clean in {"gambar", "foto", "image", "picture", "screenshot", "img"}:
                    issues.append(f"Gambar #{idx} memiliki teks alt generik yang tidak deskriptif: '{alt}'.")

            # Check dimensions / CLS prevention
            has_w = bool(img.get("width"))
            has_h = bool(img.get("height"))
            style = img.get("style", "").lower()
            has_aspect_ratio = "aspect-ratio" in style

            if not (has_w and has_h) and not has_aspect_ratio:
                missing_dims += 1
                issues.append(f"Gambar #{idx} tidak memiliki dimensi lebar/tinggi eksplisit (width/height atau aspect-ratio), berpotensi memicu Cumulative Layout Shift (CLS).")

        return {
            "total_images": len(images),
            "has_issues": len(issues) > 0,
            "missing_alt_count": missing_alt,
            "missing_dimensions_count": missing_dims,
            "issues": issues
        }

    @staticmethod
    def audit_duplicate_element_ids(html_content: str) -> Dict[str, Any]:
        """
        Audits HTML content for duplicate element ID attributes which break W3C validation,
        screen reader accessibility landmarks, and internal hash navigation.
        """
        if not html_content:
            return {"total_ids": 0, "has_duplicates": False, "duplicate_ids": [], "issues": []}

        soup = BeautifulSoup(html_content, "html.parser")
        elements_with_id = soup.find_all(attrs={"id": True})

        id_counts: Dict[str, int] = {}
        for el in elements_with_id:
            val = el["id"].strip()
            if val:
                id_counts[val] = id_counts.get(val, 0) + 1

        duplicates = [id_val for id_val, count in id_counts.items() if count > 1]
        issues = [f"ID '{dup}' digunakan {id_counts[dup]} kali di dalam dokumen." for dup in duplicates]

        return {
            "total_ids": len(id_counts),
            "has_duplicates": len(duplicates) > 0,
            "duplicate_ids": duplicates,
            "issues": issues
        }

    @staticmethod
    def detect_sinta_accreditation(text: str) -> Dict[str, Any]:
        """
        Detects Indonesian national scientific journal accreditation (ARJUNA / SINTA) rank
        and accreditation decree (Surat Keputusan / SK) mentions in editorial text.
        """
        if not text:
            return {
                "has_sinta": False,
                "sinta_rank": None,
                "sk_number": "",
                "accreditation_level": "",
                "confidence": "none"
            }

        clean = text.strip()

        sinta_match = re.search(r'\b(?:sinta|peringkat)\s*([1-6])\b', clean, re.IGNORECASE)
        rank = int(sinta_match.group(1)) if sinta_match else None

        sk_match = re.search(r'\b(?:sk|nomor\s*sk|surat\s*keputusan)\s*(?:no\.?|nomor)?\s*([0-9A-Za-z\/\.\-]+)', clean, re.IGNORECASE)
        sk_number = sk_match.group(1).strip() if sk_match else ""

        descriptions = {
            1: "SINTA 1 (Akreditasi Nasional Peringkat 1 / Terindeks Scopus)",
            2: "SINTA 2 (Akreditasi Nasional Peringkat 2 / Sangat Baik)",
            3: "SINTA 3 (Akreditasi Nasional Peringkat 3 / Baik Sekali)",
            4: "SINTA 4 (Akreditasi Nasional Peringkat 4 / Baik)",
            5: "SINTA 5 (Akreditasi Nasional Peringkat 5)",
            6: "SINTA 6 (Akreditasi Nasional Peringkat 6)"
        }

        has_sinta = rank is not None
        level_desc = descriptions.get(rank, "")
        confidence = "high" if (rank and sk_number) else ("medium" if rank else "none")

        return {
            "has_sinta": has_sinta,
            "sinta_rank": rank,
            "sk_number": sk_number,
            "accreditation_level": level_desc,
            "confidence": confidence
        }

    @staticmethod
    def audit_meta_robots_directives(meta: Dict[str, Any]) -> Dict[str, Any]:
        """
        Audits meta robots indexing and follow directives for search engine crawlers.
        Validates presence of canonical indexing instructions (index, follow, max-snippet).
        """
        robots_str = meta.get("meta_robots", meta.get("robots", "index, follow")).strip().lower()
        directives = [d.strip() for d in re.split(r'[,;\s]+', robots_str) if d.strip()]

        is_noindex = "noindex" in directives
        is_nofollow = "nofollow" in directives
        is_index = "index" in directives or (not is_noindex)
        is_follow = "follow" in directives or (not is_nofollow)

        warnings: List[str] = []
        if is_noindex:
            warnings.append("Halaman disetel 'noindex', mesin pencari (Google/Bing) tidak akan mengindeks artikel ini.")
        if is_nofollow:
            warnings.append("Halaman disetel 'nofollow', crawler tidak akan menelusuri hyperlink internal/eksternal.")

        has_max_snippet = any("max-snippet" in d for d in directives)
        has_max_image = any("max-image-preview" in d for d in directives)

        is_optimal = bool(not is_noindex and not is_nofollow)

        return {
            "raw_directives": robots_str,
            "directives_list": directives,
            "is_indexable": bool(is_index and not is_noindex),
            "is_followable": bool(is_follow and not is_nofollow),
            "has_snippet_controls": bool(has_max_snippet or has_max_image),
            "is_optimal": is_optimal,
            "warnings": warnings
        }

    @staticmethod
    def audit_social_meta_readiness(meta: Dict[str, Any]) -> Dict[str, Any]:
        """
        Audits completeness and quality of Open Graph (Facebook/LinkedIn) and
        Twitter Card social share metadata.
        """
        issues: List[str] = []
        score = 100

        title = meta.get("og_title", meta.get("seo_title", "")).strip()
        if not title:
            score -= 25
            issues.append("Judul sosial (og:title / seo_title) tidak ditemukan.")
        elif len(title) < 20 or len(title) > 90:
            score -= 10
            issues.append(f"Panjang judul sosial ({len(title)} karakter) di luar rentang optimal (20-90 karakter).")

        desc = meta.get("og_description", meta.get("meta_description", "")).strip()
        if not desc:
            score -= 25
            issues.append("Deskripsi sosial (og:description / meta_description) tidak ditemukan.")
        elif len(desc) < 50 or len(desc) > 200:
            score -= 10
            issues.append(f"Panjang deskripsi sosial ({len(desc)} karakter) di luar rentang optimal (50-200 karakter).")

        img = meta.get("og_image", meta.get("image_url", "")).strip()
        if not img:
            score -= 25
            issues.append("Gambar thumbnail sosial (og:image / image_url) tidak ditemukan.")
        elif not re.search(r'\.(?:jpe?g|png|webp)(?:\?.*)?$', img, re.IGNORECASE):
            score -= 10
            issues.append("Format gambar sosial disarankan menggunakan format standar web (.jpg, .png, .webp).")

        card_type = meta.get("twitter_card", "summary_large_image").strip().lower()
        if card_type not in {"summary", "summary_large_image", "player", "app"}:
            score -= 10
            issues.append("Tipe twitter:card tidak standar.")

        final_score = max(0, score)
        return {
            "readiness_score": final_score,
            "is_ready": bool(final_score >= 75),
            "has_title": bool(title),
            "has_description": bool(desc),
            "has_image": bool(img),
            "twitter_card": card_type,
            "issues": issues
        }

    @staticmethod
    def audit_media_transcripts(html_content: str) -> Dict[str, Any]:
        """
        Audits audio and video media elements for WCAG 2.1 accessibility compliance.
        Verifies presence of closed captions (<track kind="captions|subtitles">)
        or accompanying textual transcript containers (.tu-transcript / .tu-media-transcript).
        """
        soup = BeautifulSoup(html_content, "html.parser")
        media_elements = soup.find_all(["audio", "video"])
        if not media_elements:
            return {
                "total_media": 0,
                "accessible_media": 0,
                "is_compliant": True,
                "issues": []
            }

        issues = []
        compliant_count = 0
        has_page_transcript = bool(soup.find(class_=re.compile(r'\btu-(?:media-)?transcript\b', re.IGNORECASE)))

        for idx, media in enumerate(media_elements, 1):
            tag_name = media.name
            tracks = media.find_all("track")
            has_caption_track = any(
                t.get("kind", "").strip().lower() in ("captions", "subtitles") and t.get("src")
                for t in tracks
            )

            if has_caption_track or has_page_transcript:
                compliant_count += 1
            else:
                issues.append(f"Elemen <{tag_name}> #{idx} tidak memiliki track teks takarir (<track kind='subtitles'>) atau blok transkrip.")

        return {
            "total_media": len(media_elements),
            "accessible_media": compliant_count,
            "is_compliant": len(issues) == 0,
            "issues": issues
        }

    @staticmethod
    def detect_scimago_sjr_ranking(text: str) -> Dict[str, Any]:
        """
        Detects SCImago Journal Rank (SJR) and Scopus quartile indicators (Q1, Q2, Q3, Q4)
        along with H-Index and SJR metric score in scientific references and metadata.
        """
        clean = text.strip()
        quartile_matches = re.findall(r'\b(?:Scopus|SCImago|SJR)\s*(?:Quartile\s*)?(Q[1-4])\b|\b(Q[1-4])\s*(?:Scopus|SJR)\b', clean, re.IGNORECASE)
        quartiles = []
        for m in quartile_matches:
            q = m[0] or m[1]
            if q and q.upper() not in quartiles:
                quartiles.append(q.upper())

        sjr_score_m = re.search(r'\bSJR\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)\b', clean, re.IGNORECASE)
        sjr_score = float(sjr_score_m.group(1)) if sjr_score_m else None

        h_index_m = re.search(r'\bh-?index\s*[:=]?\s*(\d+)\b', clean, re.IGNORECASE)
        h_index = int(h_index_m.group(1)) if h_index_m else None

        has_scopus = bool(re.search(r'\b(?:scopus|scimago)\b', clean, re.IGNORECASE))
        best_quartile = quartiles[0] if quartiles else None

        return {
            "has_scopus_indexing": has_scopus or bool(quartiles),
            "best_quartile": best_quartile,
            "quartiles_found": quartiles,
            "sjr_score": sjr_score,
            "h_index": h_index
        }

    @staticmethod
    def audit_hreflang_multilingual_tags(html_content: str) -> Dict[str, Any]:
        """
        Audits multilingual alternate hreflang tags (<link rel="alternate" hreflang="..." href="...">)
        ensuring valid BCP 47 language codes and reciprocal/canonical consistency.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        hreflang_tags = soup.find_all("link", rel=lambda r: r and "alternate" in r.lower() if isinstance(r, str) else (r and "alternate" in r))
        links = [t for t in hreflang_tags if t.get("hreflang")]

        if not links:
            return {
                "has_hreflang": False,
                "languages_found": [],
                "is_valid": True,
                "issues": []
            }

        valid_pattern = re.compile(r'^(?:[a-z]{2}(?:-[A-Za-z]{2,4})?|x-default)$', re.IGNORECASE)
        languages = []
        issues = []

        has_x_default = False
        has_id = False
        has_en = False

        for l in links:
            hl = l.get("hreflang", "").strip().lower()
            href = l.get("href", "").strip()

            if not valid_pattern.match(hl):
                issues.append(f"Format hreflang '{hl}' tidak memenuhi standar BCP 47.")
            else:
                languages.append(hl)

            if hl == "x-default":
                has_x_default = True
            elif hl.startswith("id"):
                has_id = True
            elif hl.startswith("en"):
                has_en = True

            if not href:
                issues.append(f"Tag hreflang '{hl}' tidak memiliki atribut href target.")

        if (has_id or has_en) and not has_x_default:
            issues.append("Disarankan menyertakan hreflang='x-default' untuk fallback bahasa pengguna global.")

        return {
            "has_hreflang": True,
            "languages_found": sorted(set(languages)),
            "has_x_default": has_x_default,
            "is_valid": len(issues) == 0,
            "issues": issues
        }

    @staticmethod
    def audit_breadcrumb_hierarchy(
        html_content: str,
        breadcrumb_items: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Audits semantic breadcrumb trail hierarchy and schema depth for academic navigation clarity.
        Verifies minimum 2-level depth (Home > Category > Article), continuous positional indexing,
        and non-empty entity labels.
        """
        items: List[Dict[str, Any]] = []

        if breadcrumb_items:
            items = breadcrumb_items
        else:
            soup = BeautifulSoup(html_content, "html.parser")
            nav = soup.find("nav", attrs={"aria-label": re.compile(r'breadcrumb', re.IGNORECASE)}) or soup.find(class_=re.compile(r'\bbreadcrumb\b', re.IGNORECASE))
            if nav:
                for idx, li in enumerate(nav.find_all("li"), 1):
                    a_tag = li.find("a")
                    name = li.get_text().strip()
                    url = a_tag.get("href", "").strip() if a_tag else ""
                    items.append({
                        "position": idx,
                        "name": name,
                        "item": url
                    })

        issues = []
        if not items:
            return {
                "has_breadcrumbs": False,
                "depth": 0,
                "trail": [],
                "has_home_root": False,
                "is_valid": False,
                "issues": ["Navigasi breadcrumb tidak ditemukan dalam struktur dokumen."]
            }

        depth = len(items)
        if depth < 2:
            issues.append(f"Kedalaman breadcrumb terlalu dangkal ({depth} level). Disarankan minimal 2 level (misal: Beranda > Kategori > Judul).")

        # Check root level
        root_name = items[0].get("name", "").lower()
        has_home_root = bool(re.search(r'\b(?:beranda|home|utama|index)\b', root_name))
        if not has_home_root:
            issues.append(f"Level awal breadcrumb ('{items[0].get('name', '')}') sebaiknya merujuk ke Beranda / Home.")

        # Check position sequence
        for expected_pos, item in enumerate(items, 1):
            pos = item.get("position", expected_pos)
            if pos != expected_pos:
                issues.append(f"Urutan posisi breadcrumb tidak berurutan pada item '{item.get('name')}' (posisi: {pos}, diharapkan: {expected_pos}).")
            if not item.get("name", "").strip():
                issues.append(f"Label nama breadcrumb pada posisi #{expected_pos} kosong.")

        trail = [item.get("name", "").strip() for item in items if item.get("name")]

        return {
            "has_breadcrumbs": True,
            "depth": depth,
            "trail": trail,
            "has_home_root": has_home_root,
            "is_valid": len(issues) == 0,
            "issues": issues
        }

    @staticmethod
    def calculate_content_freshness_decay(
        publish_date: str,
        modified_date: Optional[str] = None,
        field_velocity: str = "fast",
        current_date_str: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculates content freshness decay score and flags editorial staleness.
        Field velocity half-life:
          - 'fast' (AI, 5G, Cybersecurity): 365 days
          - 'medium' (General Computing, Web Dev): 730 days
          - 'slow' (Theoretical Foundations, Mathematics): 1460 days
        """
        from datetime import datetime, date
        half_life_map = {"fast": 365, "medium": 730, "slow": 1460}
        half_life = half_life_map.get(field_velocity.lower(), 365)

        ref_str = (modified_date or publish_date or "").strip()[:10]
        if not ref_str:
            return {
                "freshness_score": 0.0,
                "days_elapsed": 0,
                "status": "UNKNOWN",
                "is_stale": True,
                "warning": "Tanggal publikasi tidak valid atau kosong."
            }

        try:
            ref_dt = datetime.strptime(ref_str, "%Y-%m-%d").date()
        except ValueError:
            return {
                "freshness_score": 0.0,
                "days_elapsed": 0,
                "status": "UNKNOWN",
                "is_stale": True,
                "warning": f"Format tanggal '{ref_str}' tidak sesuai ISO YYYY-MM-DD."
            }

        now_dt = datetime.strptime(current_date_str[:10], "%Y-%m-%d").date() if current_date_str else date.today()
        days_elapsed = max(0, (now_dt - ref_dt).days)

        import math
        decay_factor = math.pow(0.5, days_elapsed / half_life)
        score = round(decay_factor * 100.0, 1)

        if score >= 75.0:
            status = "FRESH"
            is_stale = False
            warning = ""
        elif score >= 50.0:
            status = "MODERATE"
            is_stale = False
            warning = "Konten mendekati siklus review tahunan."
        elif score >= 25.0:
            status = "NEEDS_UPDATE"
            is_stale = True
            warning = f"Konten sudah berumur {days_elapsed} hari. Disarankan pembaruan referensi atau kurikulum."
        else:
            status = "ARCHIVE_STALE"
            is_stale = True
            warning = f"Konten kadaluarsa ({days_elapsed} hari tanpa revisi). Perlu peninjauan editorial mendalam."

        return {
            "freshness_score": score,
            "days_elapsed": days_elapsed,
            "field_velocity": field_velocity,
            "status": status,
            "is_stale": is_stale,
            "warning": warning
        }

    @staticmethod
    def detect_academic_conference_tier(text: str) -> Dict[str, Any]:
        """
        Detects international computing and telecommunications conference ranking (CORE Portal: A*, A, B, C)
        and major indexing sponsorship (IEEE, ACM, Springer, Elsevier).
        """
        if not text:
            return {
                "has_conference": False,
                "conference_name": "",
                "acronym": "",
                "core_tier": "Unranked",
                "publisher_sponsor": "",
                "is_prestigious": False
            }

        clean = text.strip()

        core_m = re.search(r'\b(?:CORE\s*(?:Rank|Peringkat)?\s*([A-C]\*?))\b', clean, re.IGNORECASE)
        detected_tier = core_m.group(1).upper() if core_m else None

        core_a_star = {"SIGCOMM", "INFOCOM", "ICSE", "FSE", "CVPR", "ICCV", "NeurIPS", "ICLR", "MobiCom", "OSDI", "SOSP"}
        core_a = {"ICC", "GLOBECOM", "WCNC", "PerCom", "SECON", "ICNP", "CoNEXT", "IMC", "ASE", "ISSTA"}
        core_b = {"APCC", "ICACT", "Tencon", "COMPSAC", "ICCE", "HealthCom", "CSCloud"}
        core_c = {"ICAIT", "ICITACEE", "ICITISEE", "ICRAMET", "ISESD"}

        matched_conf = None
        matched_tier = detected_tier

        for acr in core_a_star:
            if re.search(r'\b' + re.escape(acr) + r'\b', clean):
                matched_conf = acr
                if not matched_tier:
                    matched_tier = "A*"
                break

        if not matched_conf:
            for acr in core_a:
                if re.search(r'\b' + re.escape(acr) + r'\b', clean):
                    matched_conf = acr
                    if not matched_tier:
                        matched_tier = "A"
                    break

        if not matched_conf:
            for acr in core_b:
                if re.search(r'\b' + re.escape(acr) + r'\b', clean):
                    matched_conf = acr
                    if not matched_tier:
                        matched_tier = "B"
                    break

        if not matched_conf:
            for acr in core_c:
                if re.search(r'\b' + re.escape(acr) + r'\b', clean):
                    matched_conf = acr
                    if not matched_tier:
                        matched_tier = "C"
                    break

        sponsor = ""
        if re.search(r'\bIEEE\b', clean):
            sponsor = "IEEE Xplore"
        elif re.search(r'\bACM\b', clean):
            sponsor = "ACM Digital Library"
        elif re.search(r'\bSpringer\b', clean):
            sponsor = "Springer LNCS"
        elif re.search(r'\bElsevier\b', clean):
            sponsor = "Elsevier Procedia"

        final_tier = matched_tier or "Unranked"
        is_prestigious = final_tier in ("A*", "A", "B")

        return {
            "has_conference": bool(matched_conf or detected_tier or sponsor),
            "conference_name": matched_conf or "",
            "acronym": matched_conf or "",
            "core_tier": final_tier,
            "publisher_sponsor": sponsor,
            "is_prestigious": is_prestigious
        }

    @staticmethod
    def audit_table_of_contents_anchor_integrity(html_content: str) -> Dict[str, Any]:
        """
        Audits Table of Contents (TOC) links against section heading anchors (H2, H3)
        to ensure bidirectional navigation integrity and prevent dead jumps.
        """
        if not html_content:
            return {
                "has_toc": False,
                "toc_links_count": 0,
                "valid_targets": 0,
                "broken_targets": [],
                "unlinked_headings": [],
                "is_valid": True,
                "issues": []
            }

        soup = BeautifulSoup(html_content, "html.parser")
        toc = soup.find(class_=re.compile(r'\b(?:tu-toc|toc|table-of-contents)\b', re.IGNORECASE)) or soup.find("nav", attrs={"aria-label": re.compile(r'daftar\s+isi|table\s+of\s+contents', re.IGNORECASE)})

        if not toc:
            return {
                "has_toc": False,
                "toc_links_count": 0,
                "valid_targets": 0,
                "broken_targets": [],
                "unlinked_headings": [],
                "is_valid": True,
                "issues": []
            }

        existing_heading_ids = set()
        for h in soup.find_all(re.compile(r'^h[2-6]$', re.IGNORECASE)):
            hid = h.get("id")
            if hid:
                existing_heading_ids.add(hid.strip())

        toc_anchors = []
        broken_targets = []
        valid_targets = []

        for a in toc.find_all("a", href=True):
            href = a["href"].strip()
            if href.startswith("#"):
                anchor_id = href[1:]
                toc_anchors.append(anchor_id)
                if anchor_id in existing_heading_ids:
                    valid_targets.append(anchor_id)
                else:
                    broken_targets.append(anchor_id)

        unlinked = [hid for hid in existing_heading_ids if hid not in toc_anchors]

        issues = []
        if broken_targets:
            issues.append(f"Ditemukan {len(broken_targets)} tautan Daftar Isi tanpa heading tujuan: {', '.join(broken_targets)}.")
        if len(toc_anchors) == 0:
            issues.append("Elemen Daftar Isi (TOC) tidak memuat tautan jangkar internal.")

        return {
            "has_toc": True,
            "toc_links_count": len(toc_anchors),
            "valid_targets": len(valid_targets),
            "broken_targets": broken_targets,
            "unlinked_headings": unlinked,
            "is_valid": len(issues) == 0,
            "issues": issues
        }

    @staticmethod
    def audit_math_latex_notation_accessibility(html_content: str) -> Dict[str, Any]:
        """
        Audits LaTeX mathematical notation delimiters ($...$, $$...$$, \(...\), \[...\])
        and accessibility labeling (aria-label, role='math', katex/mathjax wrappers).
        Ensures delimiter balance and flags raw unescaped currency dollars.
        """
        if not html_content:
            return {
                "total_equations": 0,
                "inline_count": 0,
                "display_count": 0,
                "is_balanced": True,
                "has_accessible_markup": True,
                "issues": []
            }

        soup = BeautifulSoup(html_content, "html.parser")
        clean_text = soup.get_text()

        issues = []

        display_dollars = re.findall(r'\$\$([\s\S]+?)\$\$', clean_text)
        display_brackets = re.findall(r'\\\[([\s\S]+?)\\\]', clean_text)
        display_count = len(display_dollars) + len(display_brackets)

        text_no_display = re.sub(r'\$\$[\s\S]+?\$\$', ' ', clean_text)
        text_no_display = re.sub(r'\\\[[\s\S]+?\\\]', ' ', text_no_display)

        inline_parens = re.findall(r'\\\(([\s\S]+?)\\\)', text_no_display)
        inline_dollars = re.findall(r'(?<!\\)\$([^\$\n]+?)(?<!\\)\$', text_no_display)
        inline_count = len(inline_parens) + len(inline_dollars)
        total_equations = display_count + inline_count

        dollar_count = clean_text.count("$") - (len(display_dollars) * 4)
        if dollar_count % 2 != 0:
            issues.append(f"Tanda pembatas math inline LaTeX '$' tidak berpasangan (ditemukan {dollar_count} tanda dollar ganjil).")

        math_elements = soup.find_all(attrs={"role": "math"}) or soup.find_all(class_=re.compile(r'\b(?:katex|mathjax|tu-math)\b', re.IGNORECASE))
        has_accessible_markup = True
        if total_equations > 0 and len(math_elements) == 0:
            has_accessible_markup = False
            issues.append(f"Ditemukan {total_equations} notasi matematika tanpa pembungkus semantik ramah aksesibilitas (class 'katex', 'tu-math', atau role='math').")

        return {
            "total_equations": total_equations,
            "inline_count": inline_count,
            "display_count": display_count,
            "is_balanced": len(issues) == 0,
            "has_accessible_markup": has_accessible_markup,
            "issues": issues
        }

    @classmethod
    def audit_sinta_author_metadata(
        cls,
        author_name: str,
        sinta_id: str,
        sinta_score_overall: float,
        sinta_score_3yr: float,
        profile_url: str = ""
    ) -> Dict[str, Any]:
        """
        Audits faculty SINTA author metadata, identifier formatting, and profile URL accuracy.
        """
        issues = []
        name = author_name.strip()
        clean_id = str(sinta_id).strip()

        if not re.match(r'^\d{5,9}$', clean_id):
            issues.append(f"Format SINTA ID '{clean_id}' tidak valid (harus berupa 5-9 digit angka).")

        overall = float(sinta_score_overall)
        score_3yr = float(sinta_score_3yr)

        if overall < 0 or score_3yr < 0:
            issues.append("Skor SINTA tidak boleh bernilai negatif.")
        elif score_3yr > overall:
            issues.append(f"Skor SINTA 3 tahun ({score_3yr}) tidak boleh lebih besar dari skor SINTA keseluruhan ({overall}).")

        expected_url = f"https://sinta.kemdikbud.go.id/authors/profile/{clean_id}"
        canonical_url = profile_url.strip() if profile_url.strip() else expected_url

        if profile_url.strip():
            if not profile_url.startswith("https://sinta.kemdikbud.go.id/"):
                issues.append("Tautan profil SINTA harus menggunakan protokol HTTPS resmi sinta.kemdikbud.go.id.")
            elif clean_id not in profile_url:
                issues.append(f"Tautan profil SINTA tidak memuat SINTA ID yang cocok ({clean_id}).")

        return {
            "author_name": name,
            "sinta_id": clean_id,
            "sinta_score_overall": overall,
            "sinta_score_3yr": score_3yr,
            "canonical_profile_url": canonical_url,
            "is_valid": len(issues) == 0,
            "issues": issues
        }

    @classmethod
    def audit_heading_hierarchy_skipping(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits semantic heading structure according to WCAG 2.1 H42 ensuring no skipped heading levels.
        """
        if not html_content:
            return {"is_valid": True, "heading_sequence": [], "skipped_transitions": [], "total_headings": 0}

        soup = BeautifulSoup(html_content, "html.parser")
        headings = soup.find_all(re.compile(r'^h[1-6]$', re.IGNORECASE))
        if not headings:
            return {"is_valid": True, "heading_sequence": [], "skipped_transitions": [], "total_headings": 0}

        sequence = []
        skipped = []
        prev_level = None

        for h in headings:
            level = int(h.name[1])
            text_snippet = h.get_text().strip()[:50]
            sequence.append({"level": level, "tag": h.name.lower(), "text": text_snippet})

            if prev_level is not None:
                if level > prev_level + 1:
                    skipped.append({
                        "from_level": prev_level,
                        "to_level": level,
                        "text": text_snippet,
                        "issue": f"Lonjakan tingkat heading dari h{prev_level} langsung ke h{level} melewati h{prev_level + 1}."
                    })
            prev_level = level

        return {
            "is_valid": len(skipped) == 0,
            "total_headings": len(headings),
            "heading_sequence": [h["tag"] for h in sequence],
            "skipped_transitions": skipped
        }

    @classmethod
    def audit_open_graph_multimedia_tags(cls, og_tags: Dict[str, str]) -> Dict[str, Any]:
        """
        Audits Open Graph audio and video metadata tags for secure HTTPS endpoints and valid MIME types.
        """
        issues = []
        video_url = og_tags.get("og:video", "").strip()
        video_secure = og_tags.get("og:video:secure_url", "").strip()
        video_type = og_tags.get("og:video:type", "").strip()

        audio_url = og_tags.get("og:audio", "").strip()
        audio_secure = og_tags.get("og:audio:secure_url", "").strip()
        audio_type = og_tags.get("og:audio:type", "").strip()

        valid_video_types = {"video/mp4", "video/webm", "video/ogg", "application/x-shockwave-flash"}
        valid_audio_types = {"audio/mpeg", "audio/ogg", "audio/wav", "audio/mp4", "audio/aac"}

        has_video = bool(video_url)
        has_audio = bool(audio_url)

        if has_video:
            if not video_url.startswith("https://") and not video_secure:
                issues.append("Tag og:video tidak menggunakan HTTPS dan tidak menyediakan og:video:secure_url.")
            if not video_type:
                issues.append("Tag og:video disertakan tanpa og:video:type yang mendefinisikan tipe MIME.")
            elif video_type.lower() not in valid_video_types:
                issues.append(f"MIME type video '{video_type}' tidak umum atau tidak didukung Open Graph.")

        if has_audio:
            if not audio_url.startswith("https://") and not audio_secure:
                issues.append("Tag og:audio tidak menggunakan HTTPS dan tidak menyediakan og:audio:secure_url.")
            if not audio_type:
                issues.append("Tag og:audio disertakan tanpa og:audio:type yang mendefinisikan tipe MIME.")
            elif audio_type.lower() not in valid_audio_types:
                issues.append(f"MIME type audio '{audio_type}' tidak umum atau tidak didukung Open Graph.")

        return {
            "has_multimedia": has_video or has_audio,
            "has_video": has_video,
            "has_audio": has_audio,
            "is_valid": len(issues) == 0,
            "issues": issues
        }

    @classmethod
    def audit_table_summary_and_caption_accessibility(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits HTML table elements for accessibility compliance including caption, aria descriptions, and headers.
        """
        if not html_content:
            return {"is_accessible": True, "total_tables": 0, "accessible_tables": 0, "issues": []}

        soup = BeautifulSoup(html_content, "html.parser")
        tables = soup.find_all("table")
        if not tables:
            return {"is_accessible": True, "total_tables": 0, "accessible_tables": 0, "issues": []}

        issues = []
        accessible_count = 0

        for idx, tbl in enumerate(tables, 1):
            has_caption = tbl.find("caption") is not None and bool(tbl.find("caption").get_text().strip())
            has_aria = bool(tbl.get("aria-label")) or bool(tbl.get("aria-labelledby"))
            has_summary = bool(tbl.get("summary", "").strip())
            has_accessible_name = has_caption or has_aria or has_summary

            th_tags = tbl.find_all("th")
            has_headers = len(th_tags) > 0

            tbl_issues = []
            if not has_accessible_name:
                tbl_issues.append(f"Tabel #{idx} tidak memiliki elemen <caption> atau atribut aria-label/summary untuk pembaca layar.")
            if not has_headers:
                tbl_issues.append(f"Tabel #{idx} tidak memiliki sel judul kolom/baris (<th>).")

            if has_accessible_name and has_headers:
                accessible_count += 1
            else:
                issues.extend(tbl_issues)

        return {
            "total_tables": len(tables),
            "accessible_tables": accessible_count,
            "is_accessible": len(issues) == 0,
            "issues": issues
        }

    @staticmethod
    def audit_duplicate_meta(target_title: str, target_desc: str, existing_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Audits candidate SEO title and meta description against database records to prevent duplicate SERP snippets.
        """
        norm_title = target_title.strip().lower()
        norm_desc = target_desc.strip().lower()

        conflicting_titles: List[Dict[str, Any]] = []
        conflicting_descriptions: List[Dict[str, Any]] = []

        for rec in existing_records:
            rec_id = rec.get("id")
            rec_slug = rec.get("slug", "")
            rec_title = (rec.get("seo_title") or rec.get("topic") or "").strip().lower()
            rec_desc = (rec.get("meta_description") or "").strip().lower()

            if rec_title and (rec_title == norm_title or (len(norm_title) > 10 and norm_title in rec_title)):
                conflicting_titles.append({"id": rec_id, "slug": rec_slug, "title": rec.get("seo_title")})

            if rec_desc and (rec_desc == norm_desc or (len(norm_desc) > 30 and norm_desc in rec_desc)):
                conflicting_descriptions.append({"id": rec_id, "slug": rec_slug, "description": rec.get("meta_description")})

        has_title_conflict = len(conflicting_titles) > 0
        has_desc_conflict = len(conflicting_descriptions) > 0
        is_clean = not has_title_conflict and not has_desc_conflict

        return {
            "is_clean": is_clean,
            "has_title_conflict": has_title_conflict,
            "has_desc_conflict": has_desc_conflict,
            "conflicting_titles": conflicting_titles,
            "conflicting_descriptions": conflicting_descriptions
        }

    @staticmethod
    def audit_robots_meta_directives(html_content: str) -> Dict[str, Any]:
        """
        Audits HTML robots and googlebot meta directives for indexing safety and search snippet optimization.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        robots_tags = soup.find_all("meta", attrs={"name": lambda n: n and n.lower() in {"robots", "googlebot", "bingbot"}})

        directives: List[str] = []
        is_indexable = True
        is_followable = True
        has_snippet_control = False
        blocking_reasons: List[str] = []

        for tag in robots_tags:
            content = tag.get("content", "")
            tokens = [t.strip().lower() for t in content.split(",") if t.strip()]
            directives.extend(tokens)

            for token in tokens:
                if token in {"noindex", "none"}:
                    is_indexable = False
                    blocking_reasons.append(f"Directive '{token}' prevents search indexing.")
                if token in {"nofollow", "none"}:
                    is_followable = False
                    blocking_reasons.append(f"Directive '{token}' blocks link equity transfer.")
                if "max-snippet" in token or "max-image-preview" in token:
                    has_snippet_control = True

        return {
            "has_robots_meta": len(robots_tags) > 0,
            "directives": list(set(directives)),
            "is_indexable": is_indexable,
            "is_followable": is_followable,
            "has_snippet_control": has_snippet_control,
            "blocking_reasons": blocking_reasons
        }

    @staticmethod
    def audit_video_accessibility(html_content: str) -> Dict[str, Any]:
        """
        Audits HTML5 video elements for accessibility compliance (closed caption tracks, labels, fallback text).
        """
        soup = BeautifulSoup(html_content, "html.parser")
        video_tags = soup.find_all("video")

        if not video_tags:
            return {
                "has_video": False,
                "total_videos": 0,
                "accessible_videos": 0,
                "is_accessible": True,
                "issues": []
            }

        issues: List[str] = []
        accessible_count = 0

        for idx, video in enumerate(video_tags, 1):
            vid_issues: List[str] = []
            tracks = video.find_all("track")
            has_captions = any(t.get("kind", "").lower() in {"captions", "subtitles"} for t in tracks)
            if not has_captions:
                vid_issues.append(f"Video #{idx} does not have a captions or subtitles <track>.")

            has_label = bool(video.get("aria-label") or video.get("aria-labelledby") or video.get("title"))
            if not has_label:
                vid_issues.append(f"Video #{idx} lacks an accessible label (title or aria-label).")

            fallback_text = "".join(video.find_all(string=True)).strip()
            if not fallback_text and not video.find("a"):
                vid_issues.append(f"Video #{idx} lacks fallback text or link for unsupported browsers.")

            if not vid_issues:
                accessible_count += 1
            else:
                issues.extend(vid_issues)

        return {
            "has_video": True,
            "total_videos": len(video_tags),
            "accessible_videos": accessible_count,
            "is_accessible": len(issues) == 0,
            "issues": issues
        }

    @staticmethod
    def calculate_text_to_code_ratio(html_content: str) -> Dict[str, Any]:
        """
        Calculates visible text to HTML markup ratio to detect DOM bloat and ensure content substance.
        """
        if not html_content:
            return {
                "text_length": 0,
                "html_length": 0,
                "ratio_percent": 0.0,
                "status": "empty",
                "is_optimal": False
            }

        soup = BeautifulSoup(html_content, "html.parser")
        for s in soup(["script", "style"]):
            s.decompose()

        visible_text = soup.get_text(separator=" ", strip=True)
        text_length = len(visible_text)
        html_length = len(html_content.strip())

        ratio = (text_length / html_length * 100.0) if html_length > 0 else 0.0

        if ratio >= 15.0:
            status = "optimal"
            is_optimal = True
        elif ratio >= 10.0:
            status = "moderate"
            is_optimal = True
        else:
            status = "low_content"
            is_optimal = False

        return {
            "text_length": text_length,
            "html_length": html_length,
            "ratio_percent": round(ratio, 2),
            "status": status,
            "is_optimal": is_optimal
        }

    @staticmethod
    def audit_audio_accessibility(html_content: str) -> Dict[str, Any]:
        """
        Audits HTML5 <audio> podcast elements for accessibility compliance (controls, labels, and text transcripts).
        """
        if not html_content:
            return {
                "has_audio": False,
                "total_audios": 0,
                "accessible_audios": 0,
                "is_accessible": True,
                "issues": []
            }

        soup = BeautifulSoup(html_content, "html.parser")
        audio_tags = soup.find_all("audio")
        if not audio_tags:
            return {
                "has_audio": False,
                "total_audios": 0,
                "accessible_audios": 0,
                "is_accessible": True,
                "issues": []
            }

        issues = []
        accessible_count = 0

        for idx, audio in enumerate(audio_tags, start=1):
            aud_issues = []
            if not audio.has_attr("controls"):
                aud_issues.append(f"Audio #{idx} lacks 'controls' attribute for user playback control.")

            has_label = bool(audio.get("aria-label") or audio.get("aria-labelledby") or audio.get("title"))
            if not has_label:
                aud_issues.append(f"Audio #{idx} lacks an accessible label (title, aria-label, or aria-labelledby).")

            # Check for transcript link or adjacent transcript container
            has_transcript = False
            if audio.get("aria-describedby"):
                desc_id = audio.get("aria-describedby")
                if soup.find(id=desc_id):
                    has_transcript = True

            parent = audio.parent
            if parent:
                trans_link = parent.find("a", string=re.compile(r'transkrip|transcript', re.IGNORECASE))
                trans_div = parent.find(class_=re.compile(r'transcript|transkrip', re.IGNORECASE))
                if trans_link or trans_div:
                    has_transcript = True

            if not has_transcript:
                aud_issues.append(f"Audio #{idx} lacks companion text transcript or transcript link.")

            if not aud_issues:
                accessible_count += 1
            else:
                issues.extend(aud_issues)

        return {
            "has_audio": True,
            "total_audios": len(audio_tags),
            "accessible_audios": accessible_count,
            "is_accessible": len(issues) == 0,
            "issues": issues
        }

    @staticmethod
    def audit_hreflang_tags(html_content: str, current_url: str = "") -> Dict[str, Any]:
        """
        Audits multilingual <link rel="alternate" hreflang="..."> annotations for international SEO.
        """
        if not html_content:
            return {
                "has_hreflang": False,
                "total_tags": 0,
                "languages_detected": [],
                "has_x_default": False,
                "is_valid": True,
                "issues": []
            }

        soup = BeautifulSoup(html_content, "html.parser")
        alt_links = [
            l for l in soup.find_all("link")
            if l.get("rel") and "alternate" in l.get("rel") and l.has_attr("hreflang")
        ]

        if not alt_links:
            return {
                "has_hreflang": False,
                "total_tags": 0,
                "languages_detected": [],
                "has_x_default": False,
                "is_valid": True,
                "issues": []
            }

        issues = []
        languages = []
        has_x_default = False
        lang_regex = re.compile(r'^[a-zA-Z]{2}(?:-[a-zA-Z]{2})?$|^x-default$', re.IGNORECASE)

        for idx, link in enumerate(alt_links, start=1):
            lang = link.get("hreflang", "").strip()
            href = link.get("href", "").strip()

            if not lang_regex.match(lang):
                issues.append(f"Hreflang #{idx} has invalid language code '{lang}'. Expected ISO 639-1 or 'x-default'.")
            else:
                languages.append(lang.lower())
                if lang.lower() == "x-default":
                    has_x_default = True

            if not href or not href.startswith(("http://", "https://")):
                issues.append(f"Hreflang #{idx} href '{href}' must be a fully qualified absolute URL.")

        if len(languages) > 1 and not has_x_default:
            issues.append("Multilingual alternate links lack an 'x-default' fallback entry.")

        if current_url:
            clean_curr = current_url.strip().rstrip("/")
            has_self = any(l.get("href", "").strip().rstrip("/") == clean_curr for l in alt_links)
            if not has_self:
                issues.append(f"Missing self-referencing hreflang tag pointing back to current URL '{current_url}'.")

        return {
            "has_hreflang": True,
            "total_tags": len(alt_links),
            "languages_detected": languages,
            "has_x_default": has_x_default,
            "is_valid": len(issues) == 0,
            "issues": issues
        }

    @staticmethod
    def audit_iframe_performance(html_content: str) -> Dict[str, Any]:
        """
        Audits <iframe> elements (e.g. YouTube embeds, interactive campus maps) for performance and accessibility.
        """
        if not html_content:
            return {
                "has_iframes": False,
                "total_iframes": 0,
                "optimized_iframes": 0,
                "is_compliant": True,
                "issues": []
            }

        soup = BeautifulSoup(html_content, "html.parser")
        iframes = soup.find_all("iframe")
        if not iframes:
            return {
                "has_iframes": False,
                "total_iframes": 0,
                "optimized_iframes": 0,
                "is_compliant": True,
                "issues": []
            }

        issues = []
        optimized_count = 0

        for idx, iframe in enumerate(iframes, start=1):
            frame_issues = []
            loading = iframe.get("loading", "").strip().lower()
            if loading != "lazy":
                frame_issues.append(f"Iframe #{idx} lacks loading='lazy' attribute.")

            title = iframe.get("title", "").strip()
            if not title:
                frame_issues.append(f"Iframe #{idx} lacks an accessible 'title' attribute for screen readers.")

            src = iframe.get("src", "").strip()
            if src and not src.startswith("https://"):
                frame_issues.append(f"Iframe #{idx} source '{src}' does not use secure HTTPS protocol.")

            if not frame_issues:
                optimized_count += 1
            else:
                issues.extend(frame_issues)

        return {
            "has_iframes": True,
            "total_iframes": len(iframes),
            "optimized_iframes": optimized_count,
            "is_compliant": len(issues) == 0,
            "issues": issues
        }

    @staticmethod
    def audit_figure_figcaption_structure(html_content: str) -> Dict[str, Any]:
        """
        Audits semantic <figure> and <figcaption> structure for HTML5 and SEO compliance.
        """
        if not html_content:
            return {
                "has_figures": False,
                "total_figures": 0,
                "valid_figures": 0,
                "is_compliant": True,
                "issues": []
            }

        soup = BeautifulSoup(html_content, "html.parser")
        figures = soup.find_all("figure")
        if not figures:
            return {
                "has_figures": False,
                "total_figures": 0,
                "valid_figures": 0,
                "is_compliant": True,
                "issues": []
            }

        issues = []
        valid_count = 0

        for idx, fig in enumerate(figures, start=1):
            fig_issues = []
            captions = fig.find_all("figcaption")
            if len(captions) > 1:
                fig_issues.append(f"Figure #{idx} contains multiple ({len(captions)}) <figcaption> elements. Maximum 1 allowed.")

            child_elements = [c for c in fig.children if getattr(c, "name", None)]
            if captions:
                cap = captions[0]
                if child_elements and cap != child_elements[0] and cap != child_elements[-1]:
                    fig_issues.append(f"Figure #{idx} <figcaption> must be either the first or last child of <figure>.")

            has_media = bool(fig.find(["img", "svg", "table", "pre", "video", "audio", "canvas"]))
            if not has_media:
                fig_issues.append(f"Figure #{idx} does not contain standard visual media or data element (img, svg, table, pre, video).")

            if not fig_issues:
                valid_count += 1
            else:
                issues.extend(fig_issues)

        return {
            "has_figures": True,
            "total_figures": len(figures),
            "valid_figures": valid_count,
            "is_compliant": len(issues) == 0,
            "issues": issues
        }

    @classmethod
    def audit_table_accessibility(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits <table> elements for WCAG 2.1 accessibility compliance.
        Checks for caption or aria-label/aria-labelledby, table headers (<th>),
        and header scope attributes (scope="col" or scope="row").
        """
        soup = BeautifulSoup(html_content, "html.parser")
        tables = soup.find_all("table")

        if not tables:
            return {
                "has_tables": False,
                "total_tables": 0,
                "accessible_tables": 0,
                "is_compliant": True,
                "issues": []
            }

        issues: List[str] = []
        accessible_count = 0

        for idx, table in enumerate(tables, start=1):
            tbl_issues = []
            has_caption = bool(table.find("caption"))
            has_aria_label = bool(table.get("aria-label") or table.get("aria-labelledby"))
            if not has_caption and not has_aria_label:
                tbl_issues.append(f"Table #{idx} lacks an accessible description (missing <caption> or aria-label).")

            headers = table.find_all("th")
            if not headers:
                tbl_issues.append(f"Table #{idx} has no header cells (<th>) defining data relationships.")
            else:
                missing_scope = sum(1 for th in headers if not th.get("scope"))
                if missing_scope > 0:
                    tbl_issues.append(f"Table #{idx} has {missing_scope} header cell(s) without a scope attribute (col/row).")

            if not tbl_issues:
                accessible_count += 1
            else:
                issues.extend(tbl_issues)

        return {
            "has_tables": True,
            "total_tables": len(tables),
            "accessible_tables": accessible_count,
            "is_compliant": len(issues) == 0,
            "issues": issues
        }

    @classmethod
    def audit_form_labels_and_autocomplete(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits form control elements (<input>, <select>, <textarea>) for accessible label association
        (via matching <label for="...">, parent <label>, or aria-label/aria-labelledby) and autocomplete usage.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        controls = soup.find_all(["input", "select", "textarea"])

        interactive_controls = [
            c for c in controls
            if c.name in ("select", "textarea") or c.get("type", "text").lower() not in ("hidden", "submit", "button", "reset", "image")
        ]

        if not interactive_controls:
            return {
                "has_form_controls": False,
                "total_controls": 0,
                "labeled_controls": 0,
                "is_compliant": True,
                "issues": []
            }

        issues: List[str] = []
        labeled_count = 0

        for idx, ctrl in enumerate(interactive_controls, start=1):
            ctrl_id = ctrl.get("id")
            ctrl_type = ctrl.get("type", "text") if ctrl.name == "input" else ctrl.name

            has_aria = bool(ctrl.get("aria-label") or ctrl.get("aria-labelledby"))
            has_explicit_label = bool(ctrl_id and soup.find("label", attrs={"for": ctrl_id}))
            has_parent_label = bool(ctrl.find_parent("label"))

            if has_aria or has_explicit_label or has_parent_label:
                labeled_count += 1
            else:
                issues.append(f"Form control #{idx} (<{ctrl.name} type='{ctrl_type}'>) lacks an associated <label> or aria-label.")

            if ctrl.name == "input" and ctrl_type in ("email", "tel", "password", "username") and not ctrl.get("autocomplete"):
                issues.append(f"Identity input #{idx} (type='{ctrl_type}') lacks an 'autocomplete' attribute.")

        return {
            "has_form_controls": True,
            "total_controls": len(interactive_controls),
            "labeled_controls": labeled_count,
            "is_compliant": len(issues) == 0,
            "issues": issues
        }

    @classmethod
    def audit_content_language_and_direction(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits root and content block language declarations (lang / xml:lang) and text directionality (dir).
        Ensures search engines and screen readers can identify the spoken language and rendering direction.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        issues: List[str] = []

        root = soup.find(["html", "div", "article", "section"])
        declared_lang = None
        declared_dir = None

        if root:
            declared_lang = root.get("lang") or root.get("xml:lang")
            declared_dir = root.get("dir")

        if not declared_lang:
            any_lang_el = soup.find(attrs={"lang": True})
            if any_lang_el:
                declared_lang = any_lang_el.get("lang")

        if not declared_lang:
            issues.append("Document or primary container lacks a declared 'lang' attribute (e.g. lang='id' or lang='en').")
        else:
            lang_clean = declared_lang.strip().lower()
            if not re.match(r'^[a-z]{2,3}(?:-[a-z0-9]+)?$', lang_clean):
                issues.append(f"Declared language '{declared_lang}' does not conform to ISO 639-1 / BCP 47 standard.")

        if declared_dir:
            dir_clean = declared_dir.strip().lower()
            if dir_clean not in ("ltr", "rtl", "auto"):
                issues.append(f"Text directionality dir='{declared_dir}' is invalid; must be 'ltr', 'rtl', or 'auto'.")

        return {
            "declared_lang": declared_lang,
            "declared_dir": declared_dir or "ltr",
            "is_compliant": len(issues) == 0,
            "issues": issues
        }

    @classmethod
    def audit_svg_accessibility(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits inline <svg> graphics for WCAG accessibility compliance.
        Ensures SVGs either have aria-hidden='true' (if purely decorative) or have
        accessible naming via <title>, <desc>, aria-label, or role='img'.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        svgs = soup.find_all("svg")

        if not svgs:
            return {
                "has_svgs": False,
                "total_svgs": 0,
                "accessible_svgs": 0,
                "is_compliant": True,
                "issues": []
            }

        issues: List[str] = []
        accessible_count = 0

        for idx, svg in enumerate(svgs, start=1):
            is_hidden = svg.get("aria-hidden", "").lower() in ("true", "1")
            has_title = bool(svg.find("title"))
            has_desc = bool(svg.find("desc"))
            has_aria = bool(svg.get("aria-label") or svg.get("aria-labelledby"))
            has_img_role = svg.get("role", "").lower() == "img"

            if is_hidden:
                accessible_count += 1
            elif (has_title or has_desc or has_aria) and (has_img_role or has_title or has_aria):
                accessible_count += 1
            else:
                issues.append(f"Inline SVG #{idx} lacks accessible labeling (missing <title>, aria-label, or aria-hidden='true' for decorative graphics).")

        return {
            "has_svgs": True,
            "total_svgs": len(svgs),
            "accessible_svgs": accessible_count,
            "is_compliant": len(issues) == 0,
            "issues": issues
        }

    @classmethod
    def audit_breadcrumb_accessibility(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits breadcrumb navigation markup for WCAG 2.1 accessibility and semantic hierarchy.
        Verifies nav landmark labeling (aria-label="breadcrumb"), ordered list structure (<ol>),
        and aria-current="page" on the terminal active page item.
        """
        if not html_content or "<nav" not in html_content.lower():
            return {
                "has_breadcrumb": False,
                "is_compliant": True,
                "issues": []
            }

        soup = BeautifulSoup(html_content, "html.parser")
        # Locate breadcrumb navigation container
        breadcrumb_nav = None
        for nav in soup.find_all("nav"):
            aria_lbl = (nav.get("aria-label") or "").strip().lower()
            cls_name = " ".join(nav.get("class") or []).lower()
            if "breadcrumb" in aria_lbl or "breadcrumb" in cls_name:
                breadcrumb_nav = nav
                break

        if not breadcrumb_nav:
            return {
                "has_breadcrumb": False,
                "is_compliant": True,
                "issues": []
            }

        issues: List[str] = []
        # Check aria-label="breadcrumb"
        aria_label = (breadcrumb_nav.get("aria-label") or "").strip().lower()
        if aria_label != "breadcrumb" and "breadcrumb" not in aria_label:
            issues.append("Navigasi breadcrumb disarankan memiliki atribut aria-label='breadcrumb'.")

        # Check list structure (<ol> or <ul>)
        list_container = breadcrumb_nav.find(["ol", "ul"])
        if not list_container:
            issues.append("Breadcrumb harus menstrukturkan tautan hierarki di dalam elemen daftar semantik (<ol> atau <ul>).")
            crumbs = breadcrumb_nav.find_all("a")
        else:
            crumbs = list_container.find_all("li")

        if not crumbs:
            issues.append("Breadcrumb tidak memuat item tautan hierarki navigasi.")
        else:
            # Check last crumb for aria-current="page"
            last_crumb = crumbs[-1]
            has_aria_current = (
                last_crumb.get("aria-current") == "page" or
                bool(last_crumb.find(attrs={"aria-current": "page"}))
            )
            if not has_aria_current:
                issues.append("Item breadcrumb terakhir (halaman aktif) harus menyertakan atribut aria-current='page'.")

        return {
            "has_breadcrumb": True,
            "total_crumbs": len(crumbs) if crumbs else 0,
            "is_compliant": len(issues) == 0,
            "issues": issues
        }

    @classmethod
    def audit_video_media_accessibility(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits embedded HTML5 <video> elements for WCAG 2.1 multimedia accessibility compliance.
        Checks for player controls, poster placeholder preview, text track captions, and fallback content.
        """
        if not html_content or "<video" not in html_content.lower():
            return {
                "has_videos": False,
                "total_videos": 0,
                "compliant_videos": 0,
                "is_compliant": True,
                "issues": []
            }

        soup = BeautifulSoup(html_content, "html.parser")
        videos = soup.find_all("video")
        if not videos:
            return {
                "has_videos": False,
                "total_videos": 0,
                "compliant_videos": 0,
                "is_compliant": True,
                "issues": []
            }

        issues: List[str] = []
        compliant_count = 0

        for idx, vid in enumerate(videos, start=1):
            vid_issues = []
            if not vid.has_attr("controls"):
                vid_issues.append(f"Elemen video #{idx} tidak memiliki atribut 'controls' untuk navigasi pengguna.")
            if not vid.get("poster"):
                vid_issues.append(f"Elemen video #{idx} belum menetapkan atribut 'poster' untuk gambar pratinjau pemuatan.")

            # Check for caption or subtitle track
            tracks = vid.find_all("track")
            has_captions = any(t.get("kind", "").lower() in ("captions", "subtitles") for t in tracks)
            if not has_captions:
                vid_issues.append(f"Elemen video #{idx} belum menyediakan elemen <track kind='captions'> atau subtitles.")

            if not vid_issues:
                compliant_count += 1
            else:
                issues.extend(vid_issues)

        return {
            "has_videos": True,
            "total_videos": len(videos),
            "compliant_videos": compliant_count,
            "is_compliant": len(issues) == 0,
            "issues": issues
        }

    @classmethod
    def audit_external_links_security(cls, html_content: str, internal_domain: str = "telkomuniversity.ac.id") -> Dict[str, Any]:
        """
        Audits outbound hyperlinks targeting external websites with target="_blank" for security compliance.
        Ensures rel attributes feature 'noopener' and 'noreferrer' to prevent reverse tab-nabbing security risks.
        """
        if not html_content or "<a" not in html_content.lower():
            return {
                "total_links": 0,
                "external_links": 0,
                "secure_links": 0,
                "is_compliant": True,
                "issues": []
            }

        soup = BeautifulSoup(html_content, "html.parser")
        links = soup.find_all("a", href=True)
        if not links:
            return {
                "total_links": 0,
                "external_links": 0,
                "secure_links": 0,
                "is_compliant": True,
                "issues": []
            }

        domain_clean = internal_domain.strip().lower()
        external_count = 0
        secure_count = 0
        issues: List[str] = []

        for idx, a in enumerate(links, start=1):
            href = a["href"].strip().lower()
            if not href.startswith(("http://", "https://")):
                continue

            # Check if domain is external
            if domain_clean in href:
                continue

            external_count += 1
            target = (a.get("target") or "").strip().lower()
            rel = (a.get("rel") or [])
            if isinstance(rel, str):
                rel_tokens = set(rel.lower().split())
            else:
                rel_tokens = set(t.lower() for t in rel)

            if target == "_blank":
                has_noopener = "noopener" in rel_tokens
                if not has_noopener:
                    issues.append(f"Tautan eksternal #{idx} ({href[:40]}...) menggunakan target='_blank' tanpa atribut rel='noopener'.")
                else:
                    secure_count += 1
            else:
                secure_count += 1

        return {
            "total_links": len(links),
            "external_links": external_count,
            "secure_links": secure_count,
            "is_compliant": len(issues) == 0,
            "issues": issues
        }

    @classmethod
    def audit_blockquote_citations(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits <blockquote> elements in academic editorial content for appropriate attribution.
        Ensures presence of either a semantic <cite> element or a cite="..." source reference attribute.
        """
        if not html_content or "<blockquote" not in html_content.lower():
            return {
                "total_blockquotes": 0,
                "attributed_quotes": 0,
                "is_compliant": True,
                "issues": []
            }

        soup = BeautifulSoup(html_content, "html.parser")
        quotes = soup.find_all("blockquote")
        if not quotes:
            return {
                "total_blockquotes": 0,
                "attributed_quotes": 0,
                "is_compliant": True,
                "issues": []
            }

        issues: List[str] = []
        attributed_count = 0

        for idx, bq in enumerate(quotes, start=1):
            has_cite_attr = bool(bq.get("cite"))
            has_cite_elem = bool(bq.find("cite"))
            text = bq.get_text().strip()

            if not text:
                issues.append(f"Kutipan blockquote #{idx} kosong tanpa konten teks.")
            elif not (has_cite_attr or has_cite_elem):
                issues.append(f"Kutipan blockquote #{idx} ({text[:35]}...) tidak menyertakan sumber atribusi (<cite> atau atribut cite).")
            else:
                attributed_count += 1

        return {
            "total_blockquotes": len(quotes),
            "attributed_quotes": attributed_count,
            "is_compliant": len(issues) == 0,
            "issues": issues
        }

    @classmethod
    def audit_audio_accessibility_controls(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits <audio> elements for WCAG 2.1 accessibility compliance.
        Verifies presence of user controls, absence of disruptive autoplay, and availability
        of text transcripts or caption tracks for speech accessibility.
        """
        if not html_content or "<audio" not in html_content.lower():
            return {
                "total_audio": 0,
                "accessible_audio": 0,
                "is_compliant": True,
                "issues": []
            }

        soup = BeautifulSoup(html_content, "html.parser")
        audio_tags = soup.find_all("audio")
        if not audio_tags:
            return {
                "total_audio": 0,
                "accessible_audio": 0,
                "is_compliant": True,
                "issues": []
            }

        issues: List[str] = []
        accessible_count = 0

        for idx, a in enumerate(audio_tags, start=1):
            has_controls = a.has_attr("controls")
            has_autoplay = a.has_attr("autoplay")
            has_track = bool(a.find("track", kind=lambda k: k and k.lower() in ("captions", "subtitles", "descriptions")))

            # Check next siblings or parent container for transcript link
            parent = a.parent
            has_transcript_link = False
            if parent:
                for link in parent.find_all("a", href=True):
                    txt = link.get_text().lower()
                    if "transkrip" in txt or "transcript" in txt or "teks" in txt:
                        has_transcript_link = True
                        break

            item_issues = []
            if not has_controls:
                item_issues.append(f"Elemen audio #{idx} tidak memiliki atribut 'controls'.")
            if has_autoplay:
                item_issues.append(f"Elemen audio #{idx} mengaktifkan 'autoplay' yang mengganggu pengguna.")
            if not has_track and not has_transcript_link:
                item_issues.append(f"Elemen audio #{idx} tidak menyertakan track subtitle atau tautan transkrip teks pendamping.")

            if item_issues:
                issues.extend(item_issues)
            else:
                accessible_count += 1

        return {
            "total_audio": len(audio_tags),
            "accessible_audio": accessible_count,
            "is_compliant": len(issues) == 0,
            "issues": issues
        }

    @classmethod
    def audit_semantic_definition_lists(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits semantic HTML <dl> definition lists for telecommunication glossaries and formulas.
        Verifies proper term (<dt>) and description (<dd>) structure, prevents orphaned terms,
        and enforces non-empty content in technical documentation.
        """
        if not html_content or "<dl" not in html_content.lower():
            return {
                "total_dl": 0,
                "valid_dl": 0,
                "is_compliant": True,
                "issues": []
            }

        soup = BeautifulSoup(html_content, "html.parser")
        dl_tags = soup.find_all("dl")
        if not dl_tags:
            return {
                "total_dl": 0,
                "valid_dl": 0,
                "is_compliant": True,
                "issues": []
            }

        issues: List[str] = []
        valid_count = 0

        for idx, dl in enumerate(dl_tags, start=1):
            dts = dl.find_all("dt")
            dds = dl.find_all("dd")

            dl_issues = []
            if not dts and not dds:
                dl_issues.append(f"Daftar definisi <dl> #{idx} kosong tanpa elemen <dt> dan <dd>.")
            elif not dts:
                dl_issues.append(f"Daftar definisi <dl> #{idx} memiliki <dd> tetapi tidak memiliki istilah <dt>.")
            elif not dds:
                dl_issues.append(f"Daftar definisi <dl> #{idx} memiliki <dt> tetapi tidak memiliki penjelasan <dd>.")
            else:
                for dt in dts:
                    if not dt.get_text().strip():
                        dl_issues.append(f"Elemen istilah <dt> pada <dl> #{idx} kosong tanpa teks.")
                for dd in dds:
                    if not dd.get_text().strip():
                        dl_issues.append(f"Elemen deskripsi <dd> pada <dl> #{idx} kosong tanpa teks.")

            if dl_issues:
                issues.extend(dl_issues)
            else:
                valid_count += 1

        return {
            "total_dl": len(dl_tags),
            "valid_dl": valid_count,
            "is_compliant": len(issues) == 0,
            "issues": issues
        }

    @classmethod
    def audit_image_cls_dimensions(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits <img> tags for explicit width and height attributes to prevent layout instability
        and Cumulative Layout Shift (CLS), upholding Google Core Web Vitals performance benchmarks.
        """
        if not html_content or "<img" not in html_content.lower():
            return {
                "total_images": 0,
                "sized_images": 0,
                "is_compliant": True,
                "issues": []
            }

        soup = BeautifulSoup(html_content, "html.parser")
        images = soup.find_all("img")
        if not images:
            return {
                "total_images": 0,
                "sized_images": 0,
                "is_compliant": True,
                "issues": []
            }

        issues: List[str] = []
        sized_count = 0

        for idx, img in enumerate(images, start=1):
            src = img.get("src", f"image-{idx}")
            has_w = img.has_attr("width") and bool(img.get("width", "").strip())
            has_h = img.has_attr("height") and bool(img.get("height", "").strip())

            if not has_w or not has_h:
                missing = []
                if not has_w:
                    missing.append("width")
                if not has_h:
                    missing.append("height")
                issues.append(f"Gambar #{idx} ('{src[:35]}') tidak memiliki atribut eksplisit: {', '.join(missing)}.")
            else:
                sized_count += 1

        return {
            "total_images": len(images),
            "sized_images": sized_count,
            "is_compliant": len(issues) == 0,
            "issues": issues
        }

    @classmethod
    def audit_mathml_accessibility(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits MathML <math> elements used for mathematical and RF engineering formulas.
        Verifies display attributes (inline vs block) and alt text annotations (alttext or <annotation>)
        for screen reader accessibility and semantic search engine indexing.
        """
        if not html_content or "<math" not in html_content.lower():
            return {
                "total_math": 0,
                "accessible_math": 0,
                "is_compliant": True,
                "issues": []
            }

        soup = BeautifulSoup(html_content, "html.parser")
        math_tags = soup.find_all("math")
        if not math_tags:
            return {
                "total_math": 0,
                "accessible_math": 0,
                "is_compliant": True,
                "issues": []
            }

        issues: List[str] = []
        accessible_count = 0

        for idx, m in enumerate(math_tags, start=1):
            has_alttext = bool(m.get("alttext", "").strip())
            has_aria_label = bool(m.get("aria-label", "").strip())
            has_annotation = bool(m.find("annotation"))
            display_mode = m.get("display", "inline").strip().lower()

            item_issues = []
            if display_mode not in ("inline", "block"):
                item_issues.append(f"Elemen MathML #{idx} memiliki atribut display '{display_mode}' yang tidak standar (gunakan 'inline' atau 'block').")

            if not (has_alttext or has_aria_label or has_annotation):
                item_issues.append(f"Elemen MathML #{idx} tidak memiliki anotasi teks aksesibel (alttext, aria-label, atau <annotation>).")

            if item_issues:
                issues.extend(item_issues)
            else:
                accessible_count += 1

        return {
            "total_math": len(math_tags),
            "accessible_math": accessible_count,
            "is_compliant": len(issues) == 0,
            "issues": issues
        }

    @classmethod
    def audit_inp_script_accessibility(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits Interaction to Next Paint (INP) bottlenecks caused by render-blocking scripts
        and legacy inline event handlers that trigger long tasks on the main browser thread.
        """
        if not html_content:
            return {
                "total_scripts": 0,
                "render_blocking_scripts": 0,
                "async_or_deferred_scripts": 0,
                "inline_event_handlers": 0,
                "is_inp_optimized": True,
                "issues": []
            }

        soup = BeautifulSoup(html_content, "html.parser")
        scripts = soup.find_all("script")
        render_blocking = 0
        async_or_deferred = 0
        issues: List[str] = []

        for idx, s in enumerate(scripts, start=1):
            src = s.get("src", "").strip()
            if src:
                has_defer = s.has_attr("defer")
                has_async = s.has_attr("async")
                if has_defer or has_async:
                    async_or_deferred += 1
                else:
                    render_blocking += 1
                    issues.append(f"Script eksternal #{idx} ({src}) tidak memiliki atribut 'defer' atau 'async' yang memblokir rendering dan memperburuk skor INP.")

        # Check for inline event handler attributes on all tags
        inline_handlers = 0
        for tag in soup.find_all(True):
            for attr in tag.attrs:
                if attr.lower().startswith("on") and len(attr) > 2:
                    inline_handlers += 1
                    issues.append(f"Elemen <{tag.name}> memiliki inline event handler '{attr}' yang berpotensi memicu long task dan degradasi INP.")

        return {
            "total_scripts": len(scripts),
            "render_blocking_scripts": render_blocking,
            "async_or_deferred_scripts": async_or_deferred,
            "inline_event_handlers": inline_handlers,
            "is_inp_optimized": (render_blocking == 0 and inline_handlers == 0),
            "issues": issues
        }

    @classmethod
    def audit_rich_media_opengraph(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits OpenGraph video and audio rich media tags for social graph interoperability.
        Validates secure HTTPS endpoints, MIME formats, and player dimensions.
        """
        if not html_content:
            return {
                "has_video_og": False,
                "has_audio_og": False,
                "video_data": {},
                "audio_data": {},
                "is_compliant": True,
                "issues": []
            }

        soup = BeautifulSoup(html_content, "html.parser")
        meta_tags = soup.find_all("meta")

        og_dict = {}
        for m in meta_tags:
            prop = m.get("property") or m.get("name")
            if prop and prop.startswith("og:"):
                og_dict[prop.lower()] = m.get("content", "").strip()

        video_url = og_dict.get("og:video") or og_dict.get("og:video:url", "")
        video_sec = og_dict.get("og:video:secure_url", "")
        video_type = og_dict.get("og:video:type", "")
        video_w = og_dict.get("og:video:width", "")
        video_h = og_dict.get("og:video:height", "")

        audio_url = og_dict.get("og:audio") or og_dict.get("og:audio:url", "")
        audio_sec = og_dict.get("og:audio:secure_url", "")
        audio_type = og_dict.get("og:audio:type", "")

        has_video = bool(video_url or video_sec)
        has_audio = bool(audio_url or audio_sec)
        issues: List[str] = []

        video_data = {}
        if has_video:
            video_data = {
                "url": video_url,
                "secure_url": video_sec,
                "type": video_type,
                "width": video_w,
                "height": video_h
            }
            target_url = video_sec or video_url
            if not target_url.startswith("https://"):
                issues.append("URL og:video harus menggunakan protokol terenkripsi HTTPS.")
            if not video_type:
                issues.append("Tag og:video wajib menyertakan atribut og:video:type (misal video/mp4).")
            if video_w and not video_w.isdigit():
                issues.append("Nilai og:video:width harus berupa bilangan bulat piksel positif.")
            if video_h and not video_h.isdigit():
                issues.append("Nilai og:video:height harus berupa bilangan bulat piksel positif.")

        audio_data = {}
        if has_audio:
            audio_data = {
                "url": audio_url,
                "secure_url": audio_sec,
                "type": audio_type
            }
            target_a_url = audio_sec or audio_url
            if not target_a_url.startswith("https://"):
                issues.append("URL og:audio harus menggunakan protokol terenkripsi HTTPS.")
            if not audio_type:
                issues.append("Tag og:audio wajib menyertakan atribut og:audio:type (misal audio/mpeg).")

        return {
            "has_video_og": has_video,
            "has_audio_og": has_audio,
            "video_data": video_data,
            "audio_data": audio_data,
            "is_compliant": len(issues) == 0,
            "issues": issues
        }

    @classmethod
    def audit_picture_source_fallbacks(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits HTML5 <picture> responsive image containers to ensure next-gen image format
        negotiation (AVIF/WebP) and reliable fallback <img> accessibility tags.
        """
        if not html_content or "<picture" not in html_content.lower():
            return {
                "total_pictures": 0,
                "valid_pictures": 0,
                "missing_fallback_img": 0,
                "missing_alt_img": 0,
                "is_compliant": True,
                "issues": []
            }

        soup = BeautifulSoup(html_content, "html.parser")
        pictures = soup.find_all("picture")
        if not pictures:
            return {
                "total_pictures": 0,
                "valid_pictures": 0,
                "missing_fallback_img": 0,
                "missing_alt_img": 0,
                "is_compliant": True,
                "issues": []
            }

        issues: List[str] = []
        valid_count = 0
        missing_fallback = 0
        missing_alt = 0

        for idx, pic in enumerate(pictures, start=1):
            pic_issues = []
            img_tag = pic.find("img")
            if not img_tag:
                missing_fallback += 1
                pic_issues.append(f"Elemen <picture> #{idx} tidak memiliki elemen fallback <img>.")
            else:
                alt = img_tag.get("alt", "").strip()
                if not alt:
                    missing_alt += 1
                    pic_issues.append(f"Elemen fallback <img> pada <picture> #{idx} kehilangan atribut 'alt'.")
                if not img_tag.get("src", "").strip():
                    pic_issues.append(f"Elemen fallback <img> pada <picture> #{idx} kehilangan atribut 'src'.")

            sources = pic.find_all("source")
            for s_idx, s in enumerate(sources, start=1):
                if not s.get("srcset", "").strip():
                    pic_issues.append(f"Elemen <source> #{s_idx} pada <picture> #{idx} kehilangan atribut 'srcset'.")

            if pic_issues:
                issues.extend(pic_issues)
            else:
                valid_count += 1

        return {
            "total_pictures": len(pictures),
            "valid_pictures": valid_count,
            "missing_fallback_img": missing_fallback,
            "missing_alt_img": missing_alt,
            "is_compliant": len(issues) == 0,
            "issues": issues
        }

    @classmethod
    def audit_semantic_landmark_regions(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits HTML5 semantic landmark regions (<main>, <nav>, <header>, <footer>, <aside>)
        and ARIA landmarks according to WCAG 2.1 SC 1.3.1 and SC 2.4.1 for screen reader navigation.
        """
        if not html_content:
            return {
                "has_main": False,
                "main_count": 0,
                "nav_count": 0,
                "aside_count": 0,
                "header_count": 0,
                "footer_count": 0,
                "is_compliant": False,
                "issues": ["Dokumen HTML kosong atau tidak memiliki konten landmark."]
            }

        soup = BeautifulSoup(html_content, "html.parser")
        main_tags = soup.find_all("main")
        main_roles = soup.find_all(attrs={"role": "main"})
        total_main = len(main_tags) + len([m for m in main_roles if m.name != "main"])

        nav_tags = soup.find_all("nav")
        aside_tags = soup.find_all("aside")
        header_tags = soup.find_all("header")
        footer_tags = soup.find_all("footer")

        issues: List[str] = []
        if total_main == 0:
            issues.append("Halaman tidak memiliki landmark konten utama (<main> atau role='main').")
        elif total_main > 1:
            issues.append(f"Halaman memiliki {total_main} elemen <main>; standar WCAG mensyaratkan tepat satu konten utama aktif.")

        if len(nav_tags) > 1:
            unlabeled_navs = [n for n in nav_tags if not n.get("aria-label") and not n.get("aria-labelledby")]
            if unlabeled_navs:
                issues.append(f"Terdapat {len(unlabeled_navs)} elemen <nav> tanpa atribut 'aria-label' atau 'aria-labelledby' untuk membedakan navigasi.")

        return {
            "has_main": total_main == 1,
            "main_count": total_main,
            "nav_count": len(nav_tags),
            "aside_count": len(aside_tags),
            "header_count": len(header_tags),
            "footer_count": len(footer_tags),
            "is_compliant": len(issues) == 0,
            "issues": issues
        }

    @classmethod
    def audit_font_display_and_preload(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits webfont loading performance (FOIT/FOUT prevention) and Core Web Vitals LCP optimization.
        Checks crossorigin on font preloads and enforces font-display swap/optional in @font-face rules.
        """
        if not html_content:
            return {
                "font_preloads_count": 0,
                "missing_crossorigin_count": 0,
                "has_font_face": False,
                "font_display_optimized": True,
                "is_compliant": True,
                "issues": []
            }

        soup = BeautifulSoup(html_content, "html.parser")
        issues: List[str] = []

        # Audit font preload link tags
        links = soup.find_all("link")
        font_preloads = [l for l in links if "preload" in (l.get("rel") or []) and l.get("as") == "font"]
        missing_crossorigin = 0

        for idx, l in enumerate(font_preloads, start=1):
            if not l.has_attr("crossorigin"):
                missing_crossorigin += 1
                issues.append(f"Font preload #{idx} ({l.get('href', '')}) tidak memiliki atribut 'crossorigin' yang diwajibkan spesifikasi W3C.")
            if not l.get("type"):
                issues.append(f"Font preload #{idx} disarankan menyertakan atribut 'type' (misal type='font/woff2').")

        # Audit @font-face rules in inline style blocks
        style_tags = soup.find_all("style")
        combined_css = " ".join(s.get_text() for s in style_tags)
        has_font_face = "@font-face" in combined_css.lower()
        font_display_optimized = True

        if has_font_face:
            font_faces = re.findall(r'@font-face\s*\{([^}]+)\}', combined_css, flags=re.IGNORECASE)
            for idx, ff in enumerate(font_faces, start=1):
                if not re.search(r'font-display\s*:\s*(?:swap|optional|fallback)\b', ff, flags=re.IGNORECASE):
                    font_display_optimized = False
                    issues.append(f"Deklarasi @font-face #{idx} tidak menggunakan 'font-display: swap' atau 'optional', berisiko memicu FOIT pada LCP.")

        return {
            "font_preloads_count": len(font_preloads),
            "missing_crossorigin_count": missing_crossorigin,
            "has_font_face": has_font_face,
            "font_display_optimized": font_display_optimized,
            "is_compliant": len(issues) == 0,
            "issues": issues
        }

    @classmethod
    def audit_opengraph_article_metadata(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits OpenGraph article schema tags (article:published_time, modified_time, author, section)
        for news feeds, social crawlers, and Google Discover indexing compliance.
        """
        if not html_content:
            return {
                "has_article_og": False,
                "published_time": "",
                "modified_time": "",
                "author": "",
                "section": "",
                "is_compliant": True,
                "issues": []
            }

        soup = BeautifulSoup(html_content, "html.parser")
        meta_tags = soup.find_all("meta")

        og_dict = {}
        for m in meta_tags:
            prop = m.get("property") or m.get("name")
            if prop:
                og_dict[prop.lower()] = m.get("content", "").strip()

        og_type = og_dict.get("og:type", "").lower()
        pub_time = og_dict.get("article:published_time", "")
        mod_time = og_dict.get("article:modified_time", "")
        author = og_dict.get("article:author", "")
        section = og_dict.get("article:section", "")

        has_article_og = bool(og_type == "article" or pub_time or author)
        issues: List[str] = []

        if has_article_og:
            if og_type != "article":
                issues.append("Tag og:type harus dideklarasikan sebagai 'article' ketika menyertakan metadata artikel.")

            if not pub_time:
                issues.append("Tag meta 'article:published_time' wajib disediakan untuk pengindeksan artikel temporal.")
            else:
                # Basic ISO 8601 validation check
                if not re.match(r'^\d{4}-\d{2}-\d{2}', pub_time):
                    issues.append(f"Format 'article:published_time' ({pub_time}) tidak memenuhi format standar ISO 8601.")

            if not author:
                issues.append("Tag meta 'article:author' wajib disediakan untuk atribusi kredibilitas penulis akademik.")

        return {
            "has_article_og": has_article_og,
            "published_time": pub_time,
            "modified_time": mod_time,
            "author": author,
            "section": section,
            "is_compliant": len(issues) == 0,
            "issues": issues
        }

    @classmethod
    def audit_details_summary_accessibility(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits HTML5 <details> and <summary> disclosure widgets according to WCAG 2.1 SC 4.1.2.
        Verifies direct summary child, non-empty labels, and prevents nested interactive controls.
        """
        if not html_content or "<details" not in html_content.lower():
            return {
                "total_details": 0,
                "valid_details": 0,
                "missing_summary_count": 0,
                "nested_interactive_count": 0,
                "is_compliant": True,
                "issues": []
            }

        soup = BeautifulSoup(html_content, "html.parser")
        details_list = soup.find_all("details")
        if not details_list:
            return {
                "total_details": 0,
                "valid_details": 0,
                "missing_summary_count": 0,
                "nested_interactive_count": 0,
                "is_compliant": True,
                "issues": []
            }

        issues: List[str] = []
        valid_count = 0
        missing_summary = 0
        nested_interactive = 0

        for idx, det in enumerate(details_list, start=1):
            det_issues = []
            summary = det.find("summary", recursive=False)
            if not summary:
                missing_summary += 1
                det_issues.append(f"Elemen <details> #{idx} tidak memiliki elemen anak langsung <summary> sebagai kontrol pembuka.")
            else:
                summary_text = summary.get_text().strip()
                if not summary_text:
                    det_issues.append(f"Elemen <summary> pada <details> #{idx} kosong tanpa deskripsi aksesibel.")

                # Check for nested interactive tags inside summary
                interactive_children = summary.find_all(["a", "button", "input", "select", "textarea"])
                if interactive_children:
                    nested_interactive += 1
                    tags_str = ", ".join(f"<{t.name}>" for t in interactive_children)
                    det_issues.append(f"Elemen <summary> pada <details> #{idx} memuat kontrol interaktif bertingkat ({tags_str}) yang melanggar WCAG 4.1.2.")

            if det_issues:
                issues.extend(det_issues)
            else:
                valid_count += 1

        return {
            "total_details": len(details_list),
            "valid_details": valid_count,
            "missing_summary_count": missing_summary,
            "nested_interactive_count": nested_interactive,
            "is_compliant": len(issues) == 0,
            "issues": issues
        }

    @classmethod
    def audit_touch_target_accessibility(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits interactive controls (buttons, links, form triggers) against mobile touch target size
        and separation guidelines specified in WCAG 2.1 SC 2.5.5 and WCAG 2.2 SC 2.5.8.
        """
        if not html_content:
            return {
                "total_targets": 0,
                "accessible_targets": 0,
                "unlabeled_targets": 0,
                "cramped_targets": 0,
                "is_compliant": True,
                "issues": []
            }

        soup = BeautifulSoup(html_content, "html.parser")
        targets = soup.find_all(["a", "button", "input"])
        interactive_targets = []
        for t in targets:
            if t.name == "input" and t.get("type", "").lower() not in ("button", "submit", "reset"):
                continue
            interactive_targets.append(t)

        if not interactive_targets:
            return {
                "total_targets": 0,
                "accessible_targets": 0,
                "unlabeled_targets": 0,
                "cramped_targets": 0,
                "is_compliant": True,
                "issues": []
            }

        issues: List[str] = []
        unlabeled_count = 0
        cramped_count = 0
        accessible_count = 0

        for idx, elem in enumerate(interactive_targets, start=1):
            elem_issues = []
            text_val = elem.get_text().strip()
            aria_label = elem.get("aria-label", "").strip()
            title_val = elem.get("title", "").strip()
            img_child = elem.find("img")
            img_alt = img_child.get("alt", "").strip() if img_child else ""

            has_label = bool(text_val or aria_label or title_val or img_alt)
            if not has_label:
                unlabeled_count += 1
                elem_issues.append(f"Elemen target sentuh #{idx} (<{elem.name}>) tidak memiliki label nama aksesibel.")

            style_val = elem.get("style", "").lower()
            if "font-size: 8px" in style_val or "font-size: 9px" in style_val:
                cramped_count += 1
                elem_issues.append(f"Elemen target sentuh #{idx} memiliki ukuran font mikro (< 10px) yang menyulitkan aktivasi sentuhan.")

            if elem_issues:
                issues.extend(elem_issues)
            else:
                accessible_count += 1

        return {
            "total_targets": len(interactive_targets),
            "accessible_targets": accessible_count,
            "unlabeled_targets": unlabeled_count,
            "cramped_targets": cramped_count,
            "is_compliant": len(issues) == 0,
            "issues": issues
        }

    @staticmethod
    def audit_av_transcripts_and_captions(html_content: str) -> Dict[str, Any]:
        """
        Audits HTML5 <video> and <audio> media elements for WCAG 2.1 AA captions and transcripts.
        Checks for:
          - <track kind="captions"> or kind="subtitles" inside <video>
          - Text transcript containers (.tu-media-transcript or region with transcript label)
        """
        if not html_content:
            return {
                "total_media": 0,
                "video_count": 0,
                "audio_count": 0,
                "captioned_videos": 0,
                "transcripts_found": 0,
                "is_compliant": True,
                "issues": []
            }

        soup = BeautifulSoup(html_content, "html.parser")
        videos = soup.find_all("video")
        audios = soup.find_all("audio")
        total_media = len(videos) + len(audios)

        if total_media == 0:
            return {
                "total_media": 0,
                "video_count": 0,
                "audio_count": 0,
                "captioned_videos": 0,
                "transcripts_found": 0,
                "is_compliant": True,
                "issues": []
            }

        issues = []
        captioned_videos = 0
        for idx, vid in enumerate(videos, 1):
            tracks = vid.find_all("track")
            has_caption = any(t.get("kind", "").lower() in {"captions", "subtitles"} and t.get("src") for t in tracks)
            if has_caption:
                captioned_videos += 1
            else:
                issues.append(f"Elemen video #{idx} tidak memiliki track takarir/teks terjemahan (<track kind='captions'>).")

        transcripts = soup.find_all(class_=re.compile(r'\b(?:tu-media-transcript|media-transcript|tu-transcript)\b', re.IGNORECASE))
        transcript_regions = soup.find_all(attrs={"role": "region", "aria-label": re.compile(r'transkrip|transcript', re.IGNORECASE)})
        total_transcripts = len(transcripts) + len(transcript_regions)

        if total_media > 0 and total_transcripts == 0:
            issues.append(f"Ditemukan {total_media} media audio/video tanpa wadah transkrip teks alternatif (.tu-media-transcript).")

        return {
            "total_media": total_media,
            "video_count": len(videos),
            "audio_count": len(audios),
            "captioned_videos": captioned_videos,
            "transcripts_found": total_transcripts,
            "is_compliant": len(issues) == 0,
            "issues": issues
        }

    @staticmethod
    def audit_rel_canonical_urls(html_content: str, expected_domain: str = "ittelkom-pwt.ac.id") -> Dict[str, Any]:
        """
        Audits <link rel="canonical" href="..."> tags for SEO canonization integrity:
        - Ensures exactly one canonical tag exists.
        - Validates absolute HTTPS URL scheme.
        - Flags tracking parameters (utm_*, fbclid, etc.) or relative paths.
        - Checks match against expected academic domain.
        """
        if not html_content:
            return {
                "has_canonical": False,
                "canonical_url": "",
                "is_https": False,
                "has_tracking_params": False,
                "is_domain_match": False,
                "is_valid": False,
                "issues": ["Konten HTML kosong."]
            }

        soup = BeautifulSoup(html_content, "html.parser")
        canonicals = soup.find_all("link", rel=lambda r: r and "canonical" in [x.lower() for x in (r if isinstance(r, list) else [r])])

        issues = []
        if len(canonicals) == 0:
            return {
                "has_canonical": False,
                "canonical_url": "",
                "is_https": False,
                "has_tracking_params": False,
                "is_domain_match": False,
                "is_valid": False,
                "issues": ["Tag kanonisasi <link rel='canonical'> tidak ditemukan."]
            }

        if len(canonicals) > 1:
            issues.append(f"Ditemukan {len(canonicals)} tag canonical ganda. Tag canonical harus bersifat unik.")

        href = canonicals[0].get("href", "").strip()
        is_https = href.startswith("https://")
        if not is_https:
            issues.append(f"URL canonical ('{href}') harus menggunakan protokol aman HTTPS.")

        has_tracking = bool(re.search(r'[?&](?:utm_|fbclid|gclid|ref=)', href, re.IGNORECASE))
        if has_tracking:
            issues.append("URL canonical memuat parameter pelacak (tracking query params) yang tidak boleh ada pada link kanonis.")

        is_domain_match = expected_domain.lower() in href.lower()
        if not is_domain_match:
            issues.append(f"Domain canonical ('{href}') tidak sesuai dengan domain resmi ('{expected_domain}').")

        return {
            "has_canonical": True,
            "canonical_url": href,
            "is_https": is_https,
            "has_tracking_params": has_tracking,
            "is_domain_match": is_domain_match,
            "is_valid": len(issues) == 0,
            "issues": issues
        }

    @staticmethod
    def audit_breadcrumb_navigation_schema(html_content: str) -> Dict[str, Any]:
        """
        Audits breadcrumb navigation markup for WCAG 2.1 accessibility and Schema.org BreadcrumbList microdata:
        - Checks <nav aria-label="breadcrumb"> container.
        - Checks ordered list <ol> structure.
        - Checks Schema.org BreadcrumbList item scope / itemprop itemListElement or JSON-LD.
        - Checks aria-current="page" on terminal active breadcrumb item.
        """
        if not html_content:
            return {
                "has_breadcrumb": False,
                "item_count": 0,
                "has_schema_markup": False,
                "has_aria_current": False,
                "is_valid": False,
                "issues": ["Konten HTML kosong."]
            }

        soup = BeautifulSoup(html_content, "html.parser")
        breadcrumb_nav = soup.find(lambda e: e.name == "nav" and (e.get("aria-label", "").lower() in {"breadcrumb", "remah roti"} or (e.get("class") and any("breadcrumb" in c.lower() for c in e.get("class")))))

        issues = []
        if not breadcrumb_nav:
            return {
                "has_breadcrumb": False,
                "item_count": 0,
                "has_schema_markup": False,
                "has_aria_current": False,
                "is_valid": False,
                "issues": ["Elemen navigasi breadcrumb (<nav aria-label='breadcrumb'>) tidak ditemukan."]
            }

        items = breadcrumb_nav.find_all("li")
        item_count = len(items)

        if item_count < 2:
            issues.append("Struktur breadcrumb harus memiliki sekurang-kurangnya 2 level hirarki (misal: Beranda > Kategori).")

        has_schema = bool(
            breadcrumb_nav.find(attrs={"itemtype": re.compile(r'schema\.org/BreadcrumbList', re.IGNORECASE)}) or
            breadcrumb_nav.find(attrs={"itemprop": "itemListElement"}) or
            soup.find("script", type="application/ld+json", string=re.compile(r'BreadcrumbList', re.IGNORECASE))
        )
        if not has_schema:
            issues.append("Navigasi breadcrumb belum memuat markup microdata atau JSON-LD Schema.org 'BreadcrumbList'.")

        has_aria_current = bool(breadcrumb_nav.find(attrs={"aria-current": "page"}))
        if not has_aria_current:
            issues.append("Item breadcrumb terakhir belum diberi penanda aksesibel aria-current='page'.")

        return {
            "has_breadcrumb": True,
            "item_count": item_count,
            "has_schema_markup": has_schema,
            "has_aria_current": has_aria_current,
            "is_valid": len(issues) == 0,
            "issues": issues
        }

    @staticmethod
    def audit_cls_media_aspect_ratios(html_content: str) -> Dict[str, Any]:
        """
        Audits visual media elements (<img>, <video>, <canvas>, <iframe>) for explicit dimensions
        or CSS aspect-ratio properties to eliminate Cumulative Layout Shift (CLS).
        """
        if not html_content:
            return {
                "total_media_elements": 0,
                "dimensioned_elements": 0,
                "missing_dimensions_count": 0,
                "is_cls_safe": True,
                "issues": []
            }

        soup = BeautifulSoup(html_content, "html.parser")
        media_tags = soup.find_all(["img", "video", "canvas", "iframe"])

        if not media_tags:
            return {
                "total_media_elements": 0,
                "dimensioned_elements": 0,
                "missing_dimensions_count": 0,
                "is_cls_safe": True,
                "issues": []
            }

        dimensioned = 0
        missing = 0
        issues = []

        for idx, tag in enumerate(media_tags, 1):
            has_w = bool(tag.get("width"))
            has_h = bool(tag.get("height"))
            style_str = tag.get("style", "").lower()
            has_aspect_ratio = "aspect-ratio" in style_str

            if (has_w and has_h) or has_aspect_ratio:
                dimensioned += 1
            else:
                missing += 1
                tag_name = tag.name
                src = tag.get("src", "")[:30]
                issues.append(f"Elemen <{tag_name}> #{idx} ({src}) tidak memiliki atribut width/height atau CSS aspect-ratio (potensi CLS).")

        return {
            "total_media_elements": len(media_tags),
            "dimensioned_elements": dimensioned,
            "missing_dimensions_count": missing,
            "is_cls_safe": missing == 0,
            "issues": issues
        }

    @staticmethod
    def audit_hreflang_localization_tags(html_content: str, current_lang: str = "id") -> Dict[str, Any]:
        """
        Audits multi-language hreflang alternate links (<link rel="alternate" hreflang="..." href="...">):
        - Checks for valid BCP 47 language codes.
        - Verifies self-referential hreflang match with current_lang.
        - Ensures presence of 'x-default' fallback link.
        - Enforces absolute HTTPS alternate URLs.
        """
        if not html_content:
            return {
                "has_hreflang": False,
                "total_hreflang_tags": 0,
                "has_self_ref": False,
                "has_x_default": False,
                "is_compliant": False,
                "issues": ["Konten HTML kosong."]
            }

        soup = BeautifulSoup(html_content, "html.parser")
        links = soup.find_all("link", rel=lambda r: r and "alternate" in [x.lower() for x in (r if isinstance(r, list) else [r])])
        hreflang_links = [l for l in links if l.get("hreflang")]

        if not hreflang_links:
            return {
                "has_hreflang": False,
                "total_hreflang_tags": 0,
                "has_self_ref": False,
                "has_x_default": False,
                "is_compliant": False,
                "issues": ["Tag alternatif bahasa (<link rel='alternate' hreflang='...'>) tidak ditemukan."]
            }

        issues = []
        has_self_ref = False
        has_x_default = False
        valid_bcp47 = re.compile(r'^(?:x-default|[a-z]{2}(?:-[A-Za-z0-9]{2,8})?)$', re.IGNORECASE)

        for l in hreflang_links:
            hl = l["hreflang"].strip()
            href = l.get("href", "").strip()

            if not valid_bcp47.match(hl):
                issues.append(f"Format kode bahasa hreflang '{hl}' tidak valid standar BCP 47.")

            if hl.lower() == "x-default":
                has_x_default = True
            elif hl.lower() == current_lang.lower():
                has_self_ref = True

            if not href.startswith("https://"):
                issues.append(f"URL alternatif hreflang ('{href}') harus berupa URL absolut HTTPS.")

        if not has_self_ref:
            issues.append(f"Tidak ditemukan tag hreflang self-referential untuk bahasa aktif saat ini ('{current_lang}').")
        if not has_x_default:
            issues.append("Tidak ditemukan fallback hreflang='x-default' untuk penanganan wilayah global.")

        return {
            "has_hreflang": True,
            "total_hreflang_tags": len(hreflang_links),
            "has_self_ref": has_self_ref,
            "has_x_default": has_x_default,
            "is_compliant": len(issues) == 0,
            "issues": issues
        }

    @staticmethod
    def audit_robots_meta_directives(html_content: str, is_production: bool = True) -> Dict[str, Any]:
        """
        Audits search engine robots indexing meta directives (<meta name="robots" content="...">):
        - Prevents accidental 'noindex' or 'none' on production publication pages.
        - Ensures directives do not unintentionally block snippets ('nosnippet').
        - Verifies recommended directives for rich snippet previews ('max-image-preview:large').
        """
        if not html_content:
            return {
                "has_robots_meta": False,
                "is_indexable": True,
                "directives": [],
                "is_compliant": True,
                "issues": []
            }

        soup = BeautifulSoup(html_content, "html.parser")
        robots_tags = soup.find_all("meta", attrs={"name": re.compile(r'^(?:robots|googlebot)$', re.IGNORECASE)})

        if not robots_tags:
            return {
                "has_robots_meta": False,
                "is_indexable": True,
                "directives": ["index", "follow"],
                "is_compliant": True,
                "issues": []
            }

        issues = []
        all_directives = []
        is_indexable = True

        for tag in robots_tags:
            content = tag.get("content", "").lower()
            tokens = [t.strip() for t in content.split(",") if t.strip()]
            all_directives.extend(tokens)

            if "noindex" in tokens or "none" in tokens:
                is_indexable = False
                if is_production:
                    issues.append("Ditemukan direktif 'noindex' atau 'none' yang mencegah mesin pencari mengindeks halaman produksi.")

            if "nofollow" in tokens and is_production:
                issues.append("Ditemukan direktif 'nofollow' yang menghalangi perayapan tautan internal oleh robot perayap.")

        return {
            "has_robots_meta": True,
            "is_indexable": is_indexable,
            "directives": list(set(all_directives)),
            "is_compliant": len(issues) == 0,
            "issues": issues
        }

    @staticmethod
    def audit_faqpage_schema_markup(html_content: str) -> Dict[str, Any]:
        """
        Audits FAQ section for Schema.org FAQPage structured data (JSON-LD or microdata):
        - Detects FAQ questions in accordion (<details>/<summary>) or headings.
        - Verifies Schema.org @type: FAQPage with mainEntity Questions and Answers.
        """
        if not html_content:
            return {
                "detected_faq_count": 0,
                "has_faqpage_schema": False,
                "schema_question_count": 0,
                "is_compliant": True,
                "issues": []
            }

        soup = BeautifulSoup(html_content, "html.parser")
        details = soup.find_all("details")
        faq_items = [d for d in details if d.find("summary")]

        has_schema = False
        schema_questions = 0
        json_ld_scripts = soup.find_all("script", type="application/ld+json")
        for s in json_ld_scripts:
            try:
                raw_text = s.get_text().strip()
                data = json.loads(raw_text or "{}")
                if isinstance(data, dict):
                    if data.get("@type") == "FAQPage":
                        has_schema = True
                        entities = data.get("mainEntity", [])
                        schema_questions = len(entities) if isinstance(entities, list) else 1
            except Exception:
                pass

        if not has_schema:
            faq_microdata = soup.find(attrs={"itemtype": re.compile(r'schema\.org/FAQPage', re.IGNORECASE)})
            if faq_microdata:
                has_schema = True
                schema_questions = len(faq_microdata.find_all(attrs={"itemprop": "mainEntity"}))

        issues = []
        if len(faq_items) >= 2 and not has_schema:
            issues.append(f"Ditemukan {len(faq_items)} butir FAQ tanya-jawab tanpa markup terstruktur Schema.org 'FAQPage' untuk Google Rich Snippet.")

        return {
            "detected_faq_count": len(faq_items),
            "has_faqpage_schema": has_schema,
            "schema_question_count": schema_questions,
            "is_compliant": len(issues) == 0,
            "issues": issues
        }

    @staticmethod
    def audit_table_caption_and_headers(html_content: str) -> Dict[str, Any]:
        """
        Audits <table> elements for WCAG 2.1 AA tabular data accessibility (SC 1.3.1):
        - Enforces semantic <caption> describing the dataset purpose.
        - Verifies that <th> header cells define explicit scope attributes ('col' or 'row').
        """
        if not html_content:
            return {
                "total_tables": 0,
                "captioned_tables": 0,
                "total_headers": 0,
                "scoped_headers": 0,
                "is_compliant": True,
                "issues": []
            }

        soup = BeautifulSoup(html_content, "html.parser")
        tables = soup.find_all("table")

        if not tables:
            return {
                "total_tables": 0,
                "captioned_tables": 0,
                "total_headers": 0,
                "scoped_headers": 0,
                "is_compliant": True,
                "issues": []
            }

        issues = []
        captioned_count = 0
        scoped_headers = 0
        total_headers = 0

        for idx, tbl in enumerate(tables, 1):
            caption = tbl.find("caption")
            if caption and caption.get_text().strip():
                captioned_count += 1
            else:
                issues.append(f"Tabel #{idx} tidak memiliki elemen <caption> deskriptif.")

            ths = tbl.find_all("th")
            total_headers += len(ths)
            for th in ths:
                scope = th.get("scope", "").strip().lower()
                if scope in {"col", "row", "colgroup", "rowgroup"}:
                    scoped_headers += 1

        if total_headers > 0 and scoped_headers < total_headers:
            unscoped = total_headers - scoped_headers
            issues.append(f"Ditemukan {unscoped} sel header <th> tanpa atribut 'scope' ('col' atau 'row').")

        return {
            "total_tables": len(tables),
            "captioned_tables": captioned_count,
            "total_headers": total_headers,
            "scoped_headers": scoped_headers,
            "is_compliant": len(issues) == 0,
            "issues": issues
        }

    @classmethod
    def audit_web_app_manifest_and_pwa(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits progressive web app (PWA) manifest link declarations, theme color meta tags,
        and touch icon references to ensure mobile browser discoverability.
        """
        if not html_content:
            return {
                "has_manifest": False,
                "manifest_url": "",
                "has_theme_color": False,
                "theme_color": "",
                "has_apple_touch_icon": False,
                "is_pwa_ready": False,
                "issues": ["Konten HTML kosong."]
            }

        soup = BeautifulSoup(html_content, "html.parser")
        issues = []

        manifest_tag = soup.find("link", rel=lambda r: r and "manifest" in r.lower().split())
        manifest_url = manifest_tag["href"].strip() if manifest_tag and manifest_tag.get("href") else ""
        has_manifest = bool(manifest_url)
        if not has_manifest:
            issues.append("Tag <link rel='manifest'> tidak ditemukan.")

        theme_tag = soup.find("meta", attrs={"name": lambda n: n and n.lower() == "theme-color"})
        theme_color = theme_tag["content"].strip() if theme_tag and theme_tag.get("content") else ""
        has_theme_color = bool(theme_color)
        if not has_theme_color:
            issues.append("Tag <meta name='theme-color'> tidak ditemukan.")

        icon_tag = soup.find("link", rel=lambda r: r and "apple-touch-icon" in r.lower().split())
        has_apple_icon = bool(icon_tag and icon_tag.get("href"))
        if not has_apple_icon:
            issues.append("Tag <link rel='apple-touch-icon'> tidak ditemukan.")

        is_pwa_ready = has_manifest and has_theme_color

        return {
            "has_manifest": has_manifest,
            "manifest_url": manifest_url,
            "has_theme_color": has_theme_color,
            "theme_color": theme_color,
            "has_apple_touch_icon": has_apple_icon,
            "is_pwa_ready": is_pwa_ready,
            "issues": issues
        }

    @classmethod
    def audit_pagination_rel_links(cls, html_content: str, current_url: str = "") -> Dict[str, Any]:
        """
        Audits relational pagination links (rel="prev" and rel="next") in link elements or anchors
        to ensure proper crawler sequence traversal without circular loops or self-referential traps.
        """
        if not html_content:
            return {
                "has_pagination": False,
                "has_prev": False,
                "has_next": False,
                "prev_url": None,
                "next_url": None,
                "is_valid": True,
                "issues": []
            }

        soup = BeautifulSoup(html_content, "html.parser")
        issues = []

        # Find in <link rel="..."> or <a rel="...">
        prev_tag = soup.find(lambda t: t.name in ("link", "a") and t.get("rel") and any(r.lower() == "prev" for r in (t["rel"] if isinstance(t["rel"], list) else t["rel"].split())))
        next_tag = soup.find(lambda t: t.name in ("link", "a") and t.get("rel") and any(r.lower() == "next" for r in (t["rel"] if isinstance(t["rel"], list) else t["rel"].split())))

        prev_url = prev_tag["href"].strip() if prev_tag and prev_tag.get("href") else None
        next_url = next_tag["href"].strip() if next_tag and next_tag.get("href") else None

        has_prev = prev_url is not None
        has_next = next_url is not None
        has_pagination = has_prev or has_next

        if has_prev and has_next and prev_url == next_url:
            issues.append(f"Tautan rel='prev' dan rel='next' merujuk ke URL yang identik: '{prev_url}'.")

        if current_url:
            c_clean = current_url.strip()
            if prev_url and prev_url == c_clean:
                issues.append("Tautan rel='prev' merujuk ke halaman saat ini (self-referential).")
            if next_url and next_url == c_clean:
                issues.append("Tautan rel='next' merujuk ke halaman saat ini (self-referential).")

        return {
            "has_pagination": has_pagination,
            "has_prev": has_prev,
            "has_next": has_next,
            "prev_url": prev_url,
            "next_url": next_url,
            "is_valid": len(issues) == 0,
            "issues": issues
        }

    @classmethod
    def audit_howto_schema_markup(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits Schema.org HowTo structured data markup in JSON-LD and Microdata formats,
        verifying guide title, step count, and step descriptions for Google HowTo rich snippets.
        """
        if not html_content:
            return {
                "has_howto_schema": False,
                "has_name": False,
                "step_count": 0,
                "is_compliant": False,
                "issues": ["Konten HTML kosong."]
            }

        soup = BeautifulSoup(html_content, "html.parser")
        issues = []
        has_howto = False
        has_name = False
        step_count = 0

        # Check JSON-LD scripts
        for script in soup.find_all("script", type=lambda t: t and "ld+json" in t.lower()):
            try:
                data = json.loads(script.get_text().strip())
                items = data if isinstance(data, list) else [data]
                for item in items:
                    t = item.get("@type", "")
                    types = t if isinstance(t, list) else [t]
                    if any("howto" in str(x).lower() for x in types):
                        has_howto = True
                        if item.get("name"):
                            has_name = True
                        steps = item.get("step") or item.get("itemListElement") or []
                        if isinstance(steps, list):
                            step_count = max(step_count, len(steps))
            except Exception:
                continue

        # Check Microdata if not found in JSON-LD
        if not has_howto:
            micro = soup.find(attrs={"itemtype": lambda v: v and "schema.org/howto" in v.lower()})
            if micro:
                has_howto = True
                name_elem = micro.find(attrs={"itemprop": "name"})
                if name_elem:
                    has_name = True
                steps = micro.find_all(attrs={"itemprop": "step"})
                step_count = len(steps)

        if not has_howto:
            issues.append("Struktur Schema.org HowTo tidak ditemukan.")
        else:
            if not has_name:
                issues.append("Schema HowTo tidak memiliki nama judul panduan (name).")
            if step_count == 0:
                issues.append("Schema HowTo tidak memiliki elemen tahapan langkah (step).")

        return {
            "has_howto_schema": has_howto,
            "has_name": has_name,
            "step_count": step_count,
            "is_compliant": has_howto and has_name and step_count > 0,
            "issues": issues
        }

    @classmethod
    def audit_multimedia_audio_descriptions(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits video elements for audio description tracks (<track kind="descriptions">)
        or accessible companion descriptions per WCAG 2.1 AAA Success Criterion 1.2.5.
        """
        if not html_content:
            return {
                "total_videos": 0,
                "described_videos": 0,
                "is_compliant": True,
                "issues": []
            }

        soup = BeautifulSoup(html_content, "html.parser")
        issues = []
        videos = soup.find_all("video")
        if not videos:
            return {
                "total_videos": 0,
                "described_videos": 0,
                "is_compliant": True,
                "issues": []
            }

        described_count = 0
        for idx, video in enumerate(videos, 1):
            has_desc_track = bool(video.find("track", kind=lambda k: k and k.lower() == "descriptions"))
            has_aria_desc = bool(video.get("aria-describedby") and soup.find(id=video["aria-describedby"].strip()))
            has_companion_desc = bool(
                video.find_next_sibling(class_=lambda c: c and any(cls_name in c for cls_name in ("tu-audio-description", "tu-media-transcript", "tu-transcript")))
            )

            if has_desc_track or has_aria_desc or has_companion_desc:
                described_count += 1
            else:
                issues.append(f"Elemen <video> #{idx} tidak memiliki track audio description atau teks deskripsi pendamping.")

        is_compliant = described_count == len(videos)

        return {
            "total_videos": len(videos),
            "described_videos": described_count,
            "is_compliant": is_compliant,
            "issues": issues
        }

    @classmethod
    def audit_course_schema_markup(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits presence and completeness of Schema.org Course structured data markup (JSON-LD or Microdata)
        for academic curriculum modules and syllabus accreditation.
        """
        if not html_content:
            return {"has_course_schema": False, "is_valid": False, "issues": ["Konten HTML kosong."]}

        soup = BeautifulSoup(html_content, "html.parser")
        issues = []
        found_courses = []

        # Check JSON-LD
        for script in soup.find_all("script", type=lambda t: t and "ld+json" in t.lower()):
            try:
                data = json.loads(script.string or "{}")
                items = data if isinstance(data, list) else [data]
                for item in items:
                    t = item.get("@type", "")
                    if (isinstance(t, str) and t.lower() == "course") or (isinstance(t, list) and any(x.lower() == "course" for x in t)):
                        found_courses.append(item)
            except Exception:
                continue

        # Check Microdata
        for el in soup.find_all(attrs={"itemtype": re.compile(r'schema\.org/Course', re.IGNORECASE)}):
            name_el = el.find(attrs={"itemprop": "name"})
            desc_el = el.find(attrs={"itemprop": "description"})
            found_courses.append({
                "name": name_el.get_text().strip() if name_el else "",
                "description": desc_el.get_text().strip() if desc_el else ""
            })

        if not found_courses:
            return {
                "has_course_schema": False,
                "is_valid": False,
                "issues": ["Tidak ditemukan penanda data terstruktur Schema.org Course (JSON-LD atau Microdata)."]
            }

        valid_count = 0
        for idx, course in enumerate(found_courses, 1):
            name = course.get("name")
            desc = course.get("description")
            if not name:
                issues.append(f"Skema Course #{idx} tidak memiliki properti wajib 'name'.")
            if not desc:
                issues.append(f"Skema Course #{idx} tidak memiliki properti wajib 'description'.")
            if name and desc:
                valid_count += 1

        return {
            "has_course_schema": True,
            "total_courses": len(found_courses),
            "valid_courses": valid_count,
            "is_valid": len(issues) == 0 and valid_count > 0,
            "issues": issues
        }

    @classmethod
    def audit_rss_atom_autodiscovery_links(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits presence and validity of RSS 2.0 and Atom autodiscovery feed link elements
        (<link rel="alternate" type="application/rss+xml" ...>) for syndication and SEO crawler discovery.
        """
        if not html_content:
            return {"has_feed_links": False, "is_valid": False, "issues": ["Konten HTML kosong."]}

        soup = BeautifulSoup(html_content, "html.parser")
        issues = []
        found_feeds = []

        links = soup.find_all("link", rel=lambda r: r and "alternate" in (r if isinstance(r, list) else [r]))
        for link in links:
            feed_type = (link.get("type") or "").strip().lower()
            if feed_type in ("application/rss+xml", "application/atom+xml"):
                href = (link.get("href") or "").strip()
                title = (link.get("title") or "").strip()
                found_feeds.append({
                    "type": feed_type,
                    "href": href,
                    "title": title
                })

        if not found_feeds:
            return {
                "has_feed_links": False,
                "total_feeds": 0,
                "is_valid": False,
                "issues": ["Tidak ditemukan link autodiscovery feed RSS atau Atom (<link rel='alternate' type='application/rss+xml'>)."]
            }

        valid_count = 0
        for idx, feed in enumerate(found_feeds, 1):
            if not feed["href"]:
                issues.append(f"Feed autodiscovery #{idx} tidak memiliki atribut 'href'.")
            elif not (feed["href"].startswith("http://") or feed["href"].startswith("https://") or feed["href"].startswith("/")):
                issues.append(f"Feed autodiscovery #{idx} memiliki URL href yang tidak valid: {feed['href']}")
            else:
                valid_count += 1

        return {
            "has_feed_links": True,
            "total_feeds": len(found_feeds),
            "valid_feeds": valid_count,
            "feed_types": [f["type"] for f in found_feeds],
            "is_valid": len(issues) == 0 and valid_count > 0,
            "issues": issues
        }

    @classmethod
    def audit_csp_meta_directive(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits presence and security strength of Content-Security-Policy (CSP) meta directives
        (<meta http-equiv="Content-Security-Policy" content="...">) for XSS prevention and HTTPS hardening.
        """
        if not html_content:
            return {"has_csp": False, "is_secure": False, "issues": ["Konten HTML kosong."]}

        soup = BeautifulSoup(html_content, "html.parser")
        issues = []
        warnings = []

        csp_meta = soup.find("meta", attrs={"http-equiv": lambda h: h and h.lower() == "content-security-policy"})
        if not csp_meta or not csp_meta.get("content"):
            return {
                "has_csp": False,
                "is_secure": False,
                "issues": ["Tidak ditemukan tag meta Content-Security-Policy (<meta http-equiv='Content-Security-Policy'>)."],
                "warnings": warnings
            }

        content = csp_meta["content"].strip()
        directives = {}
        for part in content.split(";"):
            part = part.strip()
            if not part:
                continue
            tokens = part.split()
            dir_name = tokens[0].lower()
            dir_values = tokens[1:] if len(tokens) > 1 else []
            directives[dir_name] = dir_values

        if "default-src" not in directives and "script-src" not in directives:
            issues.append("CSP tidak mendefinisikan direktif 'default-src' atau 'script-src'.")

        script_sources = directives.get("script-src", directives.get("default-src", []))
        if "'unsafe-inline'" in script_sources and not any(s.startswith("'nonce-") or s.startswith("'sha256-") for s in script_sources):
            issues.append("Direktif script-src mengizinkan 'unsafe-inline' tanpa nonce atau sha256 hash (rentan XSS).")

        if "object-src" not in directives or "'none'" not in directives["object-src"]:
            warnings.append("Direktif 'object-src' disarankan disetel ke 'none' untuk menonaktifkan Flash/Java plugins.")

        if "*" in script_sources:
            issues.append("Direktif script-src tidak boleh menggunakan wildcard '*' tanpa batas.")

        is_secure = len(issues) == 0

        return {
            "has_csp": True,
            "directives_count": len(directives),
            "directives": list(directives.keys()),
            "is_secure": is_secure,
            "issues": issues,
            "warnings": warnings
        }

    @classmethod
    def audit_resource_hints_prefetch_preconnect(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits performance resource hints (<link rel="preconnect"> and <link rel="dns-prefetch">)
        for critical third-party CDN/Font connections to optimize Core Web Vitals (LCP/FCP).
        """
        if not html_content:
            return {"has_resource_hints": False, "is_valid": False, "issues": ["Konten HTML kosong."]}

        soup = BeautifulSoup(html_content, "html.parser")
        issues = []
        warnings = []
        found_hints = []

        valid_rels = {"preconnect", "dns-prefetch"}
        links = soup.find_all("link", rel=True)
        for link in links:
            rels = link.get("rel")
            rels_list = rels if isinstance(rels, list) else [rels]
            matching = [r.lower() for r in rels_list if r.lower() in valid_rels]
            if matching:
                href = (link.get("href") or "").strip()
                crossorigin = link.get("crossorigin")
                found_hints.append({
                    "rel": matching[0],
                    "href": href,
                    "crossorigin": crossorigin is not None
                })

        if not found_hints:
            return {
                "has_resource_hints": False,
                "total_hints": 0,
                "is_valid": True,
                "warnings": ["Tidak ada tag resource hints preconnect atau dns-prefetch yang dideklarasikan."]
            }

        valid_count = 0
        for idx, hint in enumerate(found_hints, 1):
            href = hint["href"]
            if not href:
                issues.append(f"Resource hint #{idx} ({hint['rel']}) tidak memiliki atribut 'href'.")
            elif not (href.startswith("http://") or href.startswith("https://") or href.startswith("//")):
                issues.append(f"Resource hint #{idx} memiliki URL href yang tidak valid: {href}")
            else:
                if "fonts.gstatic.com" in href and not hint["crossorigin"]:
                    warnings.append("Preconnect ke fonts.gstatic.com sebaiknya menyertakan atribut crossorigin.")
                valid_count += 1

        return {
            "has_resource_hints": True,
            "total_hints": len(found_hints),
            "valid_hints": valid_count,
            "hints": found_hints,
            "is_valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }

    @classmethod
    def audit_person_schema_markup(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits presence and completeness of Schema.org Person structured data markup (JSON-LD or Microdata)
        for academic faculty members, researchers, and author profiles to enhance Google E-E-A-T signals.
        """
        if not html_content:
            return {"has_person_schema": False, "is_valid": False, "issues": ["Konten HTML kosong."]}

        soup = BeautifulSoup(html_content, "html.parser")
        issues = []
        found_persons = []

        # Check JSON-LD
        for script in soup.find_all("script", type=lambda t: t and "ld+json" in t.lower()):
            try:
                data = json.loads(script.string or "{}")
                items = data if isinstance(data, list) else [data]
                for item in items:
                    t = item.get("@type", "")
                    if (isinstance(t, str) and t.lower() == "person") or (isinstance(t, list) and any(x.lower() == "person" for x in t)):
                        found_persons.append(item)
            except Exception:
                continue

        # Check Microdata
        for el in soup.find_all(attrs={"itemtype": re.compile(r'schema\.org/Person', re.IGNORECASE)}):
            name_el = el.find(attrs={"itemprop": "name"})
            job_el = el.find(attrs={"itemprop": "jobTitle"})
            found_persons.append({
                "name": name_el.get_text().strip() if name_el else "",
                "jobTitle": job_el.get_text().strip() if job_el else ""
            })

        if not found_persons:
            return {
                "has_person_schema": False,
                "is_valid": False,
                "issues": ["Tidak ditemukan penanda data terstruktur Schema.org Person (JSON-LD atau Microdata)."]
            }

        valid_count = 0
        for idx, person in enumerate(found_persons, 1):
            name = person.get("name")
            if not name:
                issues.append(f"Skema Person #{idx} tidak memiliki properti wajib 'name'.")
            else:
                valid_count += 1

        return {
            "has_person_schema": True,
            "total_persons": len(found_persons),
            "valid_persons": valid_count,
            "is_valid": len(issues) == 0 and valid_count > 0,
            "issues": issues
        }

    @classmethod
    def audit_open_graph_image_dimensions(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits Open Graph image metadata tags (og:image, og:image:width, og:image:height, og:image:alt)
        for social share rich snippet previews and high-DPI social media card display.
        """
        if not html_content:
            return {"has_og_image": False, "is_valid": False, "issues": ["Konten HTML kosong."]}

        soup = BeautifulSoup(html_content, "html.parser")
        issues = []
        warnings = []

        og_img = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "og:image"})
        if not og_img or not og_img.get("content"):
            return {
                "has_og_image": False,
                "is_valid": False,
                "issues": ["Tidak ditemukan tag meta Open Graph gambar (<meta property='og:image'>)."]
            }

        img_url = og_img["content"].strip()
        width_tag = soup.find("meta", property="og:image:width")
        height_tag = soup.find("meta", property="og:image:height")
        alt_tag = soup.find("meta", property="og:image:alt")

        width = int(width_tag["content"].strip()) if width_tag and width_tag.get("content", "").isdigit() else None
        height = int(height_tag["content"].strip()) if height_tag and height_tag.get("content", "").isdigit() else None

        if width is None or height is None:
            warnings.append("Disarankan mendeklarasikan 'og:image:width' dan 'og:image:height' secara eksplisit untuk mencegah lag render pertama.")
        else:
            if width < 600 or height < 315:
                issues.append(f"Dimensi gambar Open Graph ({width}x{height}) terlalu kecil (rekomendasi minimal 1200x630 px).")
            ratio = width / height if height > 0 else 0
            if not (1.8 <= ratio <= 2.0):
                warnings.append(f"Rasio aspek gambar ({ratio:.2f}:1) menyimpang dari standar ideal 1.91:1 (1200x630).")

        if not alt_tag or not alt_tag.get("content"):
            warnings.append("Disarankan menambahkan tag 'og:image:alt' untuk aksesibilitas pratinjau media sosial.")

        is_valid = len(issues) == 0

        return {
            "has_og_image": True,
            "image_url": img_url,
            "width": width,
            "height": height,
            "has_alt": bool(alt_tag and alt_tag.get("content")),
            "is_valid": is_valid,
            "issues": issues,
            "warnings": warnings
        }

    @classmethod
    def audit_viewport_scalable_accessibility(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits mobile viewport meta tags against WCAG 2.1 Success Criterion 1.4.4 (Resize Text)
        ensuring that user zooming is not disabled via user-scalable=no, user-scalable=0, or maximum-scale=1.0.
        """
        if not html_content:
            return {"has_viewport": False, "is_accessible": False, "issues": ["Konten HTML kosong."]}

        soup = BeautifulSoup(html_content, "html.parser")
        issues = []
        warnings = []

        viewport_tag = soup.find("meta", attrs={"name": lambda n: n and n.lower() == "viewport"})
        if not viewport_tag or not viewport_tag.get("content"):
            return {
                "has_viewport": False,
                "is_accessible": False,
                "issues": ["Tidak ditemukan tag meta viewport (<meta name='viewport'>)."]
            }

        content = viewport_tag["content"].strip().lower()
        parts = [p.strip() for p in content.split(",") if p.strip()]
        params = {}
        for part in parts:
            if "=" in part:
                k, v = part.split("=", 1)
                params[k.strip()] = v.strip()

        if params.get("user-scalable") in ("no", "0"):
            issues.append("Tag meta viewport menonaktifkan zoom pengguna ('user-scalable=no' atau '0') yang melanggar WCAG 2.1 SC 1.4.4.")

        if "maximum-scale" in params:
            try:
                max_scale = float(params["maximum-scale"])
                if max_scale <= 1.0:
                    issues.append(f"Tag meta viewport membatasi maximum-scale ke {max_scale}, mencegah pembesaran teks oleh pengguna disabilitas netra.")
                elif max_scale < 2.0:
                    warnings.append(f"Disarankan mengizinkan pembesaran minimal hingga 2.0 (saat ini {max_scale}).")
            except ValueError:
                pass

        if params.get("width") != "device-width":
            warnings.append("Disarankan menggunakan 'width=device-width' pada deklarasi meta viewport.")

        is_accessible = len(issues) == 0

        return {
            "has_viewport": True,
            "viewport_content": viewport_tag["content"].strip(),
            "is_accessible": is_accessible,
            "issues": issues,
            "warnings": warnings
        }

    @classmethod
    def audit_subresource_integrity_sri(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits external third-party scripts and stylesheets for Subresource Integrity (SRI) hashes
        (integrity="sha384-..." and crossorigin="anonymous") to protect against CDN compromise and supply chain tampering.
        """
        if not html_content:
            return {"total_external_resources": 0, "is_secure": True, "issues": []}

        soup = BeautifulSoup(html_content, "html.parser")
        issues = []
        warnings = []
        external_resources = []

        # Check external scripts
        for script in soup.find_all("script", src=True):
            src = script["src"].strip()
            if src.startswith(("http://", "https://", "//")):
                external_resources.append({"type": "script", "url": src, "element": script})

        # Check external stylesheets
        for link in soup.find_all("link", rel=lambda r: r and "stylesheet" in (r if isinstance(r, list) else [r])):
            href = (link.get("href") or "").strip()
            if href.startswith(("http://", "https://", "//")):
                external_resources.append({"type": "stylesheet", "url": href, "element": link})

        if not external_resources:
            return {
                "total_external_resources": 0,
                "verified_resources": 0,
                "is_secure": True,
                "issues": [],
                "warnings": warnings
            }

        verified_count = 0
        for item in external_resources:
            el = item["element"]
            integrity = el.get("integrity", "").strip()
            crossorigin = el.get("crossorigin", "").strip()

            has_valid_hash = bool(re.match(r'^(?:sha256|sha384|sha512)-[A-Za-z0-9+/=]+$', integrity))
            if not integrity:
                issues.append(f"Aset eksternal {item['type']} '{item['url']}' tidak memiliki atribut 'integrity' (SRI).")
            elif not has_valid_hash:
                issues.append(f"Aset eksternal {item['type']} '{item['url']}' memiliki format hash integrity yang tidak valid: {integrity}")
            elif not crossorigin:
                warnings.append(f"Aset eksternal {item['type']} '{item['url']}' sebaiknya menyertakan atribut crossorigin='anonymous' saat menggunakan SRI.")
            else:
                verified_count += 1

        is_secure = len(issues) == 0

        return {
            "total_external_resources": len(external_resources),
            "verified_resources": verified_count,
            "is_secure": is_secure,
            "issues": issues,
            "warnings": warnings
        }

    @classmethod
    def audit_educational_credential_schema(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits presence and completeness of Schema.org EducationalOccupationalCredential structured data
        markup (JSON-LD or Microdata) for academic degrees, BNSP certifications, and professional competencies.
        """
        if not html_content:
            return {"has_credential_schema": False, "is_valid": False, "issues": ["Konten HTML kosong."]}

        soup = BeautifulSoup(html_content, "html.parser")
        issues = []
        found_credentials = []

        # Check JSON-LD
        for script in soup.find_all("script", type=lambda t: t and "ld+json" in t.lower()):
            try:
                data = json.loads(script.string or "{}")
                items = data if isinstance(data, list) else [data]
                for item in items:
                    t = item.get("@type", "")
                    if (isinstance(t, str) and t.lower() == "educationaloccupationalcredential") or (isinstance(t, list) and any(x.lower() == "educationaloccupationalcredential" for x in t)):
                        found_credentials.append(item)
            except Exception:
                continue

        # Check Microdata
        for el in soup.find_all(attrs={"itemtype": re.compile(r'schema\.org/EducationalOccupationalCredential', re.IGNORECASE)}):
            name_el = el.find(attrs={"itemprop": "name"})
            cat_el = el.find(attrs={"itemprop": "credentialCategory"})
            found_credentials.append({
                "name": name_el.get_text().strip() if name_el else "",
                "credentialCategory": cat_el.get_text().strip() if cat_el else ""
            })

        if not found_credentials:
            return {
                "has_credential_schema": False,
                "is_valid": False,
                "issues": ["Tidak ditemukan penanda data terstruktur Schema.org EducationalOccupationalCredential (JSON-LD atau Microdata)."]
            }

        valid_count = 0
        for idx, cred in enumerate(found_credentials, 1):
            name = cred.get("name")
            if not name:
                issues.append(f"Skema Kredensial #{idx} tidak memiliki properti wajib 'name'.")
            else:
                valid_count += 1

        return {
            "has_credential_schema": True,
            "total_credentials": len(found_credentials),
            "valid_credentials": valid_count,
            "is_valid": len(issues) == 0 and valid_count > 0,
            "issues": issues
        }

    @classmethod
    def audit_web_app_manifest_and_theme(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits Web App Manifest link and theme-color meta tag for Progressive Web App (PWA) readiness,
        mobile browser chrome theming, and modern mobile installation UX.
        """
        if not html_content:
            return {"has_manifest": False, "has_theme_color": False, "is_valid": False, "issues": ["Konten HTML kosong."]}

        soup = BeautifulSoup(html_content, "html.parser")
        issues = []
        warnings = []

        manifest_link = soup.find("link", rel=lambda r: r and "manifest" in (r if isinstance(r, list) else [r]))
        manifest_url = manifest_link.get("href", "").strip() if manifest_link else ""

        theme_meta = soup.find("meta", attrs={"name": lambda n: n and n.lower() == "theme-color"})
        theme_color = theme_meta.get("content", "").strip() if theme_meta else ""

        if not manifest_link:
            issues.append("Tag <link rel='manifest'> tidak ditemukan dalam header dokumen.")
        elif not manifest_url:
            issues.append("Tag manifest tidak memiliki atribut 'href'.")

        if not theme_meta:
            warnings.append("Tag meta <meta name='theme-color'> sebaiknya disertakan untuk branding address bar peramban mobile.")
        elif not re.match(r'^(?:#[0-9a-fA-F]{3,8}|rgb\([^)]+\)|hsl\([^)]+\))$', theme_color):
            warnings.append(f"Format nilai theme-color '{theme_color}' tidak standar (disarankan format hex, rgb, atau hsl).")

        return {
            "has_manifest": bool(manifest_link and manifest_url),
            "has_theme_color": bool(theme_meta and theme_color),
            "manifest_url": manifest_url,
            "theme_color": theme_color,
            "is_valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }

    @classmethod
    def audit_aria_landmarks_and_headings(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits semantic ARIA landmarks (<main>, <nav>, <header>, <footer>, <aside>) and heading distribution
        against WCAG 2.1 Success Criterion 1.3.1 (Info and Relationships) for accessible screen reader navigation.
        """
        if not html_content:
            return {"has_main": False, "is_accessible": False, "issues": ["Konten HTML kosong."]}

        soup = BeautifulSoup(html_content, "html.parser")
        issues = []
        warnings = []

        mains = soup.find_all(lambda el: el.name == "main" or el.get("role") == "main")
        navs = soup.find_all(lambda el: el.name == "nav" or el.get("role") == "navigation")
        headers = soup.find_all(lambda el: el.name == "header" or el.get("role") == "banner")
        footers = soup.find_all(lambda el: el.name == "footer" or el.get("role") == "contentinfo")
        h1s = soup.find_all("h1")

        if len(mains) == 0:
            issues.append("Dokumen tidak memiliki landmark utama (<main> atau role='main') untuk orientasi pembaca layar.")
        elif len(mains) > 1:
            warnings.append(f"Ditemukan {len(mains)} landmark <main>. Disarankan hanya memiliki satu landmark <main> per halaman.")

        if len(h1s) == 0:
            issues.append("Dokumen tidak memiliki judul tingkat utama (<h1>) sebagai titik awal hierarki konten.")
        elif len(h1s) > 1:
            warnings.append(f"Ditemukan {len(h1s)} tag <h1>. Disarankan menggunakan satu tag <h1> per artikel untuk struktur outline yang jelas.")

        if len(navs) == 0:
            warnings.append("Dokumen sebaiknya memiliki elemen navigasi (<nav> atau role='navigation').")

        return {
            "has_main": len(mains) > 0,
            "has_nav": len(navs) > 0,
            "has_header": len(headers) > 0,
            "has_footer": len(footers) > 0,
            "h1_count": len(h1s),
            "is_accessible": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }

    @classmethod
    def audit_font_preload_cors(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits <link rel="preload" as="font"> tags to ensure the 'crossorigin' attribute is declared.
        According to W3C Preload specs, font preloads without crossorigin are discarded and fetched twice,
        harming Core Web Vitals (Largest Contentful Paint) and triggering browser CORS warnings.
        """
        if not html_content:
            return {"total_font_preloads": 0, "is_valid": True, "issues": []}

        soup = BeautifulSoup(html_content, "html.parser")
        issues = []
        warnings = []
        font_preloads = []

        for link in soup.find_all("link", rel=lambda r: r and "preload" in (r if isinstance(r, list) else [r])):
            if link.get("as") == "font":
                font_preloads.append(link)

        if not font_preloads:
            return {
                "total_font_preloads": 0,
                "valid_font_preloads": 0,
                "is_valid": True,
                "issues": [],
                "warnings": warnings
            }

        valid_count = 0
        for idx, fp in enumerate(font_preloads, 1):
            href = fp.get("href", "").strip()
            crossorigin = fp.get("crossorigin")

            if not href:
                issues.append(f"Font preload #{idx} tidak memiliki atribut 'href'.")
            elif crossorigin is None:
                issues.append(f"Font preload #{idx} ('{href}') tidak memiliki atribut 'crossorigin' (wajib untuk font preload agar tidak di-fetch ganda).")
            else:
                valid_count += 1

        return {
            "total_font_preloads": len(font_preloads),
            "valid_font_preloads": valid_count,
            "is_valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }

    @classmethod
    def audit_scholarly_article_schema(cls, html_content: str) -> Dict[str, Any]:
        """
        Audits Schema.org 'ScholarlyArticle', 'TechArticle', or academic research paper
        metadata markup in JSON-LD or Microdata format to boost scientific E-E-A-T indexing.
        """
        if not html_content:
            return {"has_scholarly_schema": False, "is_valid": False, "issues": ["Konten HTML kosong."]}

        soup = BeautifulSoup(html_content, "html.parser")
        issues = []
        warnings = []
        found_scholarly = False
        valid_count = 0

        # 1. Audit JSON-LD
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "{}")
                items = data if isinstance(data, list) else data.get("@graph", [data])
                for item in items:
                    stype = item.get("@type", "")
                    if isinstance(stype, list):
                        stypes = stype
                    else:
                        stypes = [stype]
                    if any(t in ("ScholarlyArticle", "TechArticle", "MedicalScholarlyArticle") for t in stypes):
                        found_scholarly = True
                        if not item.get("headline") and not item.get("name"):
                            issues.append("ScholarlyArticle JSON-LD wajib memiliki properti 'headline' atau 'name'.")
                        if not item.get("author"):
                            issues.append("ScholarlyArticle JSON-LD wajib mencantumkan properti 'author' peneliti/penulis.")
                        if not item.get("datePublished"):
                            warnings.append("Disarankan mencantumkan tanggal publikasi artikel 'datePublished'.")
                        if not item.get("abstract") and not item.get("description"):
                            warnings.append("Disarankan mencantumkan ringkasan riset 'abstract' atau 'description'.")
                        if len(issues) == 0:
                            valid_count += 1
            except Exception as e:
                issues.append(f"Gagal mem-parsing blok JSON-LD: {str(e)}")

        # 2. Audit Microdata itemtype
        for el in soup.find_all(attrs={"itemtype": True}):
            itype = el.get("itemtype", "")
            if any(t in itype for t in ("ScholarlyArticle", "TechArticle")):
                found_scholarly = True
                valid_count += 1

        if not found_scholarly:
            issues.append("Tidak ditemukan penanda data terstruktur Schema.org ScholarlyArticle atau TechArticle.")

        return {
            "has_scholarly_schema": found_scholarly,
            "valid_count": valid_count,
            "is_valid": found_scholarly and len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }








































































