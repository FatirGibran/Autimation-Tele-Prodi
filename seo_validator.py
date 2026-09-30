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



