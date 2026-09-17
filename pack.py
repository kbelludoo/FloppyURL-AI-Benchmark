#!/usr/bin/env python3
"""
FloppyURL Packer v2.1 — Empacota árvores de arquivos em payloads FloppyURL v2.0
Suporte a exclusões inteligentes (--exclude), limites de tamanho e compressão Brotli/Deflate.
"""
import sys
import os
import json
import base64
import zlib
import hashlib
import argparse
import fnmatch

DEFAULT_EXCLUDES = {
    '.git', 'node_modules', 'vendor', '__pycache__', '.idea', '.vscode',
    'dist', 'build', 'disks', '.gemini', 'base64', '*.wasm', '*.bin',
    '*.png', '*.jpg', '*.jpeg', '*.gif', '*.zip', '*.tar', '*.gz', '*.sqlite'
}

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def is_excluded(rel_path: str, user_excludes: set) -> bool:
    parts = rel_path.split(os.sep)
    for part in parts:
        if part in DEFAULT_EXCLUDES or part in user_excludes:
            return True
    for pattern in DEFAULT_EXCLUDES.union(user_excludes):
        if fnmatch.fnmatch(rel_path, pattern):
            return True
    return False

def pack_directory(dir_path: str, algo: str = "brotli", max_kb: int = 500, user_excludes: set = None) -> dict:
    user_excludes = user_excludes or set()
    dir_path = os.path.abspath(dir_path)
    proj_name = os.path.basename(dir_path)
    
    files_tree = {}
    total_raw_bytes = 0

    for root, dirs, files in os.walk(dir_path):
        dirs[:] = [d for d in dirs if not is_excluded(os.path.relpath(os.path.join(root, d), dir_path), user_excludes)]
        for file in files:
            full = os.path.join(root, file)
            rel = os.path.relpath(full, dir_path)
            if is_excluded(rel, user_excludes):
                continue
            try:
                size_kb = os.path.getsize(full) / 1024
                if size_kb > max_kb:
                    continue
                with open(full, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    files_tree[rel] = content
                    total_raw_bytes += len(content.encode('utf-8'))
            except:
                pass

    json_data = json.dumps(files_tree)
    template_html = f"""<!DOCTYPE html><html><head><title>{proj_name}</title></head><body><script>const projectData = {json_data};\n  const fileList = Object.keys(projectData);</script></body></html>"""
    raw_payload_bytes = template_html.encode('utf-8')

    # Compressão
    if algo == "brotli":
        import brotli
        compressed = brotli.compress(raw_payload_bytes, quality=11)
    elif algo == "deflate":
        # Raw deflate level 9
        c_obj = zlib.compressobj(level=9, method=zlib.DEFLATED, wbits=-zlib.MAX_WBITS)
        compressed = c_obj.compress(raw_payload_bytes) + c_obj.flush()
    else:
        compressed = zlib.compress(raw_payload_bytes, level=9)

    b64_payload = base64.urlsafe_b64encode(compressed).decode('utf-8').rstrip("=")
    # O SHA-256 no formato v2 é estritamente sobre o texto Base64
    chunk_sha = sha256_text(b64_payload)

    floppy_hash = f"v2;{algo};[1/1];{chunk_sha};{chunk_sha};{b64_payload}"
    boot_url = f"https://kbelludoo.github.io/FloppyURL/#{floppy_hash}"

    return {
        "project": proj_name,
        "files_count": len(files_tree),
        "raw_bytes": total_raw_bytes,
        "compressed_bytes": len(compressed),
        "encoded_chars": len(b64_payload),
        "reduction_pct": round((1.0 - (len(compressed) / (total_raw_bytes or 1))) * 100.0, 2),
        "sha256": chunk_sha,
        "floppy_hash": floppy_hash,
        "boot_url": boot_url
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FloppyURL Packer v2.1")
    parser.add_argument("dir", nargs="?", default=".", help="Diretório para empacotar")
    parser.add_argument("--algo", default="brotli", choices=["brotli", "deflate", "gzip"])
    parser.add_argument("--exclude", action="append", default=[], help="Excluir arquivo/padrão")
    parser.add_argument("--max-kb", type=int, default=500, help="Ignorar arquivos maiores que X KB")
    parser.add_argument("-o", "--output", help="Salvar payload em arquivo")

    args = parser.parse_args()
    res = pack_directory(args.dir, algo=args.algo, max_kb=args.max_kb, user_excludes=set(args.exclude))

    print("="*65)
    print(f"📦 PROJETO EMPACOTADO: {res['project']}")
    print("="*65)
    print(f"Arquivos incluídos:   {res['files_count']}")
    print(f"Código Bruto:         {res['raw_bytes']:,} bytes ({res['raw_bytes']/1024:.1f} KB)")
    print(f"Comprimido ({args.algo}): {res['compressed_bytes']:,} bytes ({res['compressed_bytes']/1024:.1f} KB)")
    print(f"Redução de Dados:     {res['reduction_pct']}% MENOR")
    print(f"Caracteres na URL:    {res['encoded_chars']:,} chars")
    print(f"SHA-256 (Base64):     {res['sha256']}")
    print("-"*65)
    print("🔗 URL DIRETA DO FLOPPYURL:")
    print(res['boot_url'])
    print("="*65)

    if args.output:
        with open(args.output, "w") as f:
            f.write(res['floppy_hash'])
        print(f"✓ Payload salvo em: {args.output}")
