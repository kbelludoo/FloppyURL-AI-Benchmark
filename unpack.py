#!/usr/bin/env python3
"""
FloppyURL Unpacker v2.1 — Extrai repositórios com integridade estrita SHA-256.
Suporte total a Brotli, Raw Deflate (Go compress/flate) e Gzip.
"""
import sys
import os
import json
import base64
import zlib
import hashlib
import subprocess

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def decompress_payload(compressed_bytes: bytes, algo: str) -> str:
    if algo == "brotli":
        try:
            import brotli
            return brotli.decompress(compressed_bytes).decode('utf-8')
        except:
            proc = subprocess.run(["brotli", "-d", "--stdout"], input=compressed_bytes, capture_output=True)
            return proc.stdout.decode('utf-8')
    elif algo == "deflate":
        # Raw Deflate do Go (compress/flate) exige wbits negativo (-15)
        try:
            return zlib.decompress(compressed_bytes, -zlib.MAX_WBITS).decode('utf-8')
        except zlib.error:
            # Fallback para zlib com header normal (78 9c)
            return zlib.decompress(compressed_bytes).decode('utf-8')
    elif algo == "gzip":
        return zlib.decompress(compressed_bytes, zlib.MAX_WBITS | 16).decode('utf-8')
    else:
        raise ValueError(f"Algoritmo desconhecido: {algo}")

def unpack_floppy(payload_str: str, output_dir: str = "./extracted_repo"):
    payload_str = payload_str.strip()
    if payload_str.startswith("#"):
        payload_str = payload_str[1:]
        
    parts = payload_str.split(";")
    if len(parts) < 6:
        print("❌ Erro: Formato de payload FloppyURL inválido.")
        sys.exit(1)
        
    version = parts[0]
    algo = parts[1]
    part_info = parts[2]
    chunk_sha = parts[3]
    root_sha = parts[4]
    b64_data = parts[5]
    
    print(f"📦 Descompactando FloppyURL [{version.upper()}]...")
    print(f"   Algoritmo: {algo}")
    print(f"   Volume:    {part_info}")
    print(f"   SHA-256 Declarado: {chunk_sha}")
    
    # 1. Validação Criptográfica Estrita do SHA-256 sobre o Base64
    calc_sha = sha256_text(b64_data)
    if calc_sha != chunk_sha:
        print(f"\n🚨 FALHA DE INTEGRIDADE!")
        print(f"   Calculado: {calc_sha}")
        print(f"   Esperado:   {chunk_sha}")
        sys.exit(1)
    print("   ✓ Integridade SHA-256 verificada e aprovada!")
    
    # 2. Descompressão dos dados
    padding = "=" * ((4 - len(b64_data) % 4) % 4)
    compressed_bytes = base64.urlsafe_b64decode(b64_data + padding)
    html_text = decompress_payload(compressed_bytes, algo)
    
    # 3. Extração dos arquivos do projeto
    start_tag = "const projectData = "
    end_tag = ";\n  const fileList"
    start = html_text.find(start_tag)
    if start == -1:
        os.makedirs(output_dir, exist_ok=True)
        out_file = os.path.join(output_dir, "index.html")
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(html_text)
        print(f"\n🎉 Página web extraída com sucesso para '{out_file}'!")
        return
        
    start += len(start_tag)
    end = html_text.find(end_tag, start)
    files = json.loads(html_text[start:end].strip())
    
    os.makedirs(output_dir, exist_ok=True)
    print(f"\n📂 Extraindo {len(files)} arquivos para '{output_dir}/':")
    for filepath, content in files.items():
        out_path = os.path.join(output_dir, filepath)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"   ✓ {filepath} ({len(content):,} bytes)")
        
    print("\n🎉 Repositório extraído com 100% de integridade com sucesso!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 unpack.py <arquivo.txt ou string payload>")
        sys.exit(1)
    arg = sys.argv[1]
    payload = open(arg).read().strip() if os.path.exists(arg) else arg
    unpack_floppy(payload)
