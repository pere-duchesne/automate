#!/usr/bin/env python3
"""
pdf_cleaner.py
Convierte PDFs (texto o escaneos) a texto plano limpio.
Lleva registro de qué ya fue procesado para no repetir trabajo.

Uso:
    python3 pdf_cleaner.py --input ~/pdfs --output ~/knowledge-cartographer/pure-text
    python3 pdf_cleaner.py --input ~/pdfs --output ~/knowledge-cartographer/pure-text --force  # reprocesa todo
"""

import os
import re
import json
import hashlib
import argparse
import sys
from pathlib import Path
from collections import Counter

# --- Dependencias opcionales con mensajes claros ---
try:
    import pdfplumber
except ImportError:
    print("ERROR: falta pdfplumber. Corré: pip install pdfplumber")
    sys.exit(1)

try:
    import fitz  # pymupdf
except ImportError:
    print("ERROR: falta pymupdf. Corré: pip install pymupdf")
    sys.exit(1)

try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("AVISO: pytesseract o pillow no disponibles. PDFs de imagen no podrán procesarse.")


# =============================================================
# DETECCIÓN: ¿texto o escaneo?
# =============================================================

def is_scanned(pdf_path: Path, sample_pages: int = 5) -> bool:
    """
    Detecta si un PDF es un escaneo (imagen) o tiene texto seleccionable.
    Muestrea las primeras N páginas para decidir.
    """
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


# =============================================================
# LIMPIEZA DE TEXTO
# =============================================================

def detect_repeated_lines(pages_text: list[str], threshold: float = 0.4) -> set[str]:
    """
    Detecta headers y footers: líneas que aparecen en más del X% de las páginas.
    Estas son las que vamos a eliminar (números de página, títulos repetidos, etc.)
    """
    line_counter = Counter()
    total_pages = len(pages_text)

    for page_text in pages_text:
        lines = set(page_text.strip().splitlines())
        for line in lines:
            stripped = line.strip()
            if stripped:
                line_counter[stripped] += 1

    # Líneas que aparecen en más del threshold% de páginas
    repeated = {
        line for line, count in line_counter.items()
        if count / total_pages >= threshold
    }
    return repeated


def clean_page(text: str, repeated_lines: set[str]) -> str:
    """
    Limpia una página de texto:
    - Elimina headers/footers repetidos
    - Elimina números de página solos
    - Colapsa espacios y líneas en blanco excesivas
    - Elimina líneas cortísimas (artefactos de OCR o layout)
    """
    lines = text.splitlines()
    cleaned = []

    for line in lines:
        stripped = line.strip()

        # Saltar líneas vacías (se reintroducen controladas después)
        if not stripped:
            cleaned.append("")
            continue

        # Saltar si es una línea repetida (header/footer)
        if stripped in repeated_lines:
            continue

        # Saltar números de página solos (1, 2, - 3 -, [4], etc.)
        if re.match(r'^[\[\-\s]*\d{1,4}[\]\-\s]*$', stripped):
            continue

        # Saltar líneas muy cortas que son probablemente artefactos
        # (menos de 4 caracteres y no son puntuación significativa)
        if len(stripped) < 4 and not re.match(r'^[A-ZÁÉÍÓÚÑ]', stripped):
            continue

        cleaned.append(stripped)

    # Colapsar múltiples líneas en blanco a máximo 2
    result = re.sub(r'\n{3,}', '\n\n', '\n'.join(cleaned))
    return result.strip()


def join_hyphenated_words(text: str) -> str:
    """
    Reagrupa palabras partidas con guión al final de línea.
    Común en libros escaneados y PDFs con justificación.
    """
    # "pala-\nbra" → "palabra"
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
    return text


# =============================================================
# EXTRACCIÓN: PDF de texto
# =============================================================

def extract_text_pdf(pdf_path: Path) -> str:
    """Extrae texto de un PDF con texto seleccionable usando pdfplumber."""
    pages_text = []

    with pdfplumber.open(pdf_path) as pdf:
        # Saltear primeras 2 páginas (portada, copyright) y última (índice a veces)
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

    # Detectar y eliminar headers/footers
    repeated = detect_repeated_lines(pages_text)

    cleaned_pages = []
    for page_text in pages_text:
        cleaned = clean_page(page_text, repeated)
        if cleaned:
            cleaned_pages.append(cleaned)

    full_text = '\n\n'.join(cleaned_pages)
    full_text = join_hyphenated_words(full_text)
    return full_text


# =============================================================
# EXTRACCIÓN: PDF escaneo (OCR)
# =============================================================

def extract_scanned_pdf(pdf_path: Path, lang: str = "spa+eng") -> str:
    """
    Extrae texto de un PDF escaneo usando pymupdf para renderizar
    y tesseract para OCR.
    """
    if not OCR_AVAILABLE:
        return f"[ERROR: OCR no disponible. Instalá pytesseract y pillow para procesar {pdf_path.name}]"

    doc = fitz.open(str(pdf_path))
    pages_text = []

    # Saltear primeras 2 páginas
    start = min(2, len(doc))

    for page_num in range(start, len(doc)):
        page = doc[page_num]
        # Renderizar a imagen de alta resolución (300dpi)
        mat = fitz.Matrix(300/72, 300/72)
        pix = page.get_pixmap(matrix=mat)

        # Convertir a PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # OCR con tesseract
        try:
            text = pytesseract.image_to_string(img, lang=lang)
            pages_text.append(text)
        except Exception as e:
            pages_text.append(f"[ERROR OCR página {page_num}: {e}]")

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


# =============================================================
# REGISTRO: qué ya fue procesado
# =============================================================

def load_registry(registry_path: Path) -> dict:
    if registry_path.exists():
        with open(registry_path) as f:
            return json.load(f)
    return {}


def save_registry(registry_path: Path, registry: dict):
    with open(registry_path, 'w') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)


def file_hash(path: Path) -> str:
    """Hash MD5 del archivo para detectar si cambió."""
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


# =============================================================
# MAIN
# =============================================================

def process_directory(input_dir: Path, output_dir: Path, force: bool = False, lang: str = "spa+eng"):
    output_dir.mkdir(parents=True, exist_ok=True)
    registry_path = output_dir / "converted.json"
    registry = load_registry(registry_path)

    pdfs = sorted(input_dir.glob("*.pdf"))
    if not pdfs:
        print(f"No se encontraron PDFs en {input_dir}")
        return

    print(f"📂 {len(pdfs)} PDFs encontrados en {input_dir}")
    converted = 0
    skipped = 0
    errors = 0

    for pdf_path in pdfs:
        file_id = pdf_path.name
        current_hash = file_hash(pdf_path)

        # Verificar si ya fue procesado y no cambió
        if not force and file_id in registry:
            if registry[file_id].get("hash") == current_hash:
                print(f"  ⏭️  {file_id} — ya convertido, salteando")
                skipped += 1
                continue

        print(f"  📄 {file_id} — procesando...", end=" ", flush=True)

        try:
            # Detectar tipo
            scanned = is_scanned(pdf_path)
            method = "ocr" if scanned else "text"
            print(f"[{method}]", end=" ", flush=True)

            # Extraer
            if scanned:
                text = extract_scanned_pdf(pdf_path, lang=lang)
            else:
                text = extract_text_pdf(pdf_path)

            if not text.strip():
                print("⚠️  sin texto extraíble")
                registry[file_id] = {
                    "hash": current_hash,
                    "method": method,
                    "status": "empty",
                    "output": None
                }
                errors += 1
                continue

            # Guardar
            output_name = pdf_path.stem + ".txt"
            output_path = output_dir / output_name
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"# {pdf_path.stem}\n")
                f.write(f"# Fuente: {pdf_path.name} | Método: {method}\n\n")
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

        # Guardar registro después de cada archivo (no perder progreso)
        save_registry(registry_path, registry)

    print(f"\n{'='*50}")
    print(f"✅ Convertidos: {converted} | ⏭️  Salteados: {skipped} | ❌ Errores: {errors}")
    print(f"📁 Registro guardado en: {registry_path}")


def main():
    parser = argparse.ArgumentParser(description="Convierte PDFs a texto plano limpio")
    parser.add_argument("--input", "-i", required=True, help="Directorio con PDFs")
    parser.add_argument("--output", "-o", required=True, help="Directorio de salida para .txt")
    parser.add_argument("--force", "-f", action="store_true", help="Reprocesar aunque ya esté convertido")
    parser.add_argument("--lang", default="spa+eng", help="Idiomas para OCR (default: spa+eng). Ej: spa+eng+deu")
    args = parser.parse_args()

    input_dir = Path(args.input).expanduser().resolve()
    output_dir = Path(args.output).expanduser().resolve()

    if not input_dir.exists():
        print(f"ERROR: el directorio de entrada no existe: {input_dir}")
        sys.exit(1)

    process_directory(input_dir, output_dir, force=args.force, lang=args.lang)


if __name__ == "__main__":
    main()
