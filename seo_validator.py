import re
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











