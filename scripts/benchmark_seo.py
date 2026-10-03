import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from seo_validator import YoastSEOValidator
from sanitizer import HTMLSanitizer

def benchmark(iterations: int = 100) -> dict:
    """
    Measures latency and throughput of HTML sanitization and Yoast SEO evaluation.
    """
    html_file = PROJECT_ROOT / "articles" / "2026-09-28-webassembly-edge-computing-iot.html"
    if not html_file.exists():
        print(f"Error: Benchmark fixture {html_file} not found.")
        return {}

    html_content = html_file.read_text(encoding="utf-8")
    sample_meta = {
        "focus_keyphrase": "WebAssembly edge computing IoT",
        "seo_title": "WebAssembly Edge Computing IoT: Standar Komputasi Cepat",
        "slug": "webassembly-edge-computing-iot",
        "meta_description": "Pelajari integrasi WebAssembly edge computing IoT untuk efisiensi komputasi awan dan keamanan sensor pintar di Telkom University Purwokerto di sini."
    }

    print(f"Running benchmark with {iterations} iterations...")

    # Benchmark Sanitizer
    t0 = time.perf_counter()
    for _ in range(iterations):
        _ = HTMLSanitizer.sanitize(html_content)
    sanitizer_elapsed = time.perf_counter() - t0
    sanitizer_ops_per_sec = iterations / sanitizer_elapsed
    sanitizer_ms_per_op = (sanitizer_elapsed / iterations) * 1000

    # Benchmark SEO Validator
    t1 = time.perf_counter()
    for _ in range(iterations):
        _ = YoastSEOValidator.evaluate(sample_meta, html_content)
    seo_elapsed = time.perf_counter() - t1
    seo_ops_per_sec = iterations / seo_elapsed
    seo_ms_per_op = (seo_elapsed / iterations) * 1000

    print("=== Hasil Benchmark Kinerja ===")
    print(f"HTML Sanitizer : {sanitizer_ops_per_sec:.1f} ops/sec ({sanitizer_ms_per_op:.2f} ms/op)")
    print(f"Yoast SEO Eval : {seo_ops_per_sec:.1f} ops/sec ({seo_ms_per_op:.2f} ms/op)")

    return {
        "iterations": iterations,
        "sanitizer_ops_sec": round(sanitizer_ops_per_sec, 1),
        "sanitizer_ms_op": round(sanitizer_ms_per_op, 2),
        "seo_ops_sec": round(seo_ops_per_sec, 1),
        "seo_ms_op": round(seo_ms_per_op, 2)
    }

if __name__ == "__main__":
    benchmark(100)
