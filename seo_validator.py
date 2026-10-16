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






























