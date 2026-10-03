import re
from typing import Dict, Any, List

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



