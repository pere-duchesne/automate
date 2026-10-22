#!/usr/bin/env python3
"""
pdf_cleaner.py
Transform PDFs (text or image) into plain text.
Keeps record of what was already transformed.

Use:
    python3 pdf_cleaner.py --input ./pdf --output ./text
    python3 pdf_cleaner.py --input ./pdf --output ./text --force  # reprocess
"""

import os
import re
import json
import hashlib
import argparse
import sys
from pathlib import Path
from collections import Counter
import pdfplumber
import fitz
import pytesseract
from PIL import Image

OCR_AVAILABLE = True

def is_scanned(pdf_path: Path, sample_pages: int = 5) -> bool:
    try:
        with pdfplumber.open(pdf_path) as pdf:
            pages_to_check = min(sample_pages, len(pdf.pages))
            total_chars = 0
            for i in range(pages_to_check):
                text = pdf.pages[i].extract_text() or ""
                total_chars += len(text.strip())
            # Si hay menos de 100 chars en las primeras páginas, es escaneo
            avg_chars = total_chars / pages_to_check if pages_to_check > 0 else 0
            return avg_chars < 100
    except Exception:
        return False

def detect_repeated_lines(pages_text: list[str], threshold: float = 0.4) -> set[str]:
    line_counter = Counter()
    total_pages = len(pages_text)
    for page_text in pages_text:
        lines = set(page_text.strip().splitlines())
        for line in lines:
            stripped = line.strip()
            if stripped:
                line_counter[stripped] += 1
    repeated = {
        line for line, count in line_counter.items()
        if count / total_pages >= threshold
    }
    return repeated


def clean_page(text: str, repeated_lines: set[str]) -> str:
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            cleaned.append("")
            continue
        if stripped in repeated_lines:
            continue
        if re.match(r'^[\[\-\s]*\d{1,4}[\]\-\s]*$', stripped):
            continue
        if len(stripped) < 4 and not re.match(r'^[A-ZÁÉÍÓÚÑ]', stripped):
            continue
        cleaned.append(stripped)
    result = re.sub(r'\n{3,}', '\n\n', '\n'.join(cleaned))
    return result.strip()

def join_hyphenated_words(text: str) -> str:
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
    return text

def extract_text_pdf(pdf_path: Path) -> str:
    pages_text = []

    with pdfplumber.open(pdf_path) as pdf:
        start = min(2, len(pdf.pages))
        pages = pdf.pages[start:]
        for page in pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)
            else:
                pages_text.append("")
    if not pages_text:
        return ""
    repeated = detect_repeated_lines(pages_text)
    cleaned_pages = []
    for page_text in pages_text:
        cleaned = clean_page(page_text, repeated)
        if cleaned:
            cleaned_pages.append(cleaned)
    full_text = '\n\n'.join(cleaned_pages)
    full_text = join_hyphenated_words(full_text)
    return full_text

def extract_scanned_pdf(pdf_path: Path, lang: str = "spa+eng") -> str:

    if not OCR_AVAILABLE:
        return f"[ERROR: OCR unavailable. Install pytesseract and pillow to process {pdf_path.name}]"
    doc = fitz.open(str(pdf_path))
    pages_text = []
    start = min(2, len(doc))
    for page_num in range(start, len(doc)):
        page = doc[page_num]
        mat = fitz.Matrix(300/72, 300/72)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        try:
            text = pytesseract.image_to_string(img, lang=lang)
            pages_text.append(text)
        except Exception as e:
            pages_text.append(f"[ERROR OCR pag. {page_num}: {e}]")
    doc.close()

    if not pages_text:
        return ""

    repeated = detect_repeated_lines(pages_text)

    cleaned_pages = []
    for page_text in pages_text:
        cleaned = clean_page(page_text, repeated)
        if cleaned:
            cleaned_pages.append(cleaned)

    full_text = '\n\n'.join(cleaned_pages)
    full_text = join_hyphenated_words(full_text)
    return full_text

def load_registry(registry_path: Path) -> dict:
    if registry_path.exists():
        with open(registry_path) as f:
            return json.load(f)
    return {}

def save_registry(registry_path: Path, registry: dict):
    with open(registry_path, 'w') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)


def file_hash(path: Path) -> str:
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

def process_directory(input_dir: Path, output_dir: Path, force: bool = False, lang: str = "spa+eng"):
    output_dir.mkdir(parents=True, exist_ok=True)
    registry_path = output_dir / "converted.json"
    registry = load_registry(registry_path)
    pdfs = sorted(input_dir.glob("*.pdf"))
    if not pdfs:
        print(f"No PDFs found in {input_dir}")
        return
    print(f"📂 {len(pdfs)} PDFs found {input_dir}")
    converted = 0
    skipped = 0
    errors = 0
    for pdf_path in pdfs:
        file_id = pdf_path.name
        current_hash = file_hash(pdf_path)
        if not force and file_id in registry:
            if registry[file_id].get("hash") == current_hash:
                print(f"  ⏭️  {file_id} — already converted, skipping...")
                skipped += 1
                continue
        print(f"  📄 {file_id} — processing...", end=" ", flush=True)
        try:
            scanned = is_scanned(pdf_path)
            method = "ocr" if scanned else "text"
            print(f"[{method}]", end=" ", flush=True)
            if scanned:
                text = extract_scanned_pdf(pdf_path, lang=lang)
            else:
                text = extract_text_pdf(pdf_path)

            if not text.strip():
                print("⚠️  no text to process")
                registry[file_id] = {
                    "hash": current_hash,
                    "method": method,
                    "status": "empty",
                    "output": None
                }
                errors += 1
                continue
            output_name = pdf_path.stem + ".txt"
            output_path = output_dir / output_name
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"# {pdf_path.stem}\n")
                f.write(f"# Source: {pdf_path.name} | Method: {method}\n\n")
                f.write(text)
            print(f"✅ → {output_name} ({len(text):,} chars)")
            registry[file_id] = {
                "hash": current_hash,
                "method": method,
                "status": "ok",
                "output": output_name,
                "chars": len(text)
            }
            converted += 1
        except Exception as e:
            print(f"❌ error: {e}")
            registry[file_id] = {
                "hash": current_hash,
                "status": "error",
                "error": str(e)
            }
            errors += 1
        save_registry(registry_path, registry)

    print(f"\n{'='*50}")
    print(f"✅ Converted: {converted} | ⏭️  Skipped: {skipped} | ❌ Errors: {errors}")
    print(f"📁 Recorded in: {registry_path}")


def main():
    parser = argparse.ArgumentParser(description="Transforms PDFs into plain text")
    parser.add_argument("--input", "-i", required=True, help="PDFs folder")
    parser.add_argument("--output", "-o", required=True, help=".txt output folder")
    parser.add_argument("--force", "-f", action="store_true", help="Reprocess eve already converted")
    parser.add_argument("--lang", default="spa+eng", help="Languages (default: spa+eng). Ej: spa+eng+deu")
    args = parser.parse_args()
    input_dir = Path(args.input).expanduser().resolve()
    output_dir = Path(args.output).expanduser().resolve()
    if not input_dir.exists():
        print(f"ERROR: input folder does not exist: {input_dir}")
        sys.exit(1)
    process_directory(input_dir, output_dir, force=args.force, lang=args.lang)


if __name__ == "__main__":
    main()
