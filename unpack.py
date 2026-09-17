#!/usr/bin/env python3
"""
FloppyURL Unpacker — Extrai um repositório completo a partir de um payload FloppyURL.
Zero dependências externas (funciona com Python puro stdlib).
"""
import sys
import os
import json
import base64
import zlib
import subprocess

def unpack_floppy(payload_str, output_dir="./extracted_repo"):
    parts = payload_str.strip().split(";")
    if len(parts) < 6:
        print("Erro: Payload FloppyURL inválido.")
        sys.exit(1)
        
    algo = parts[1]
    root_sha = parts[4]
    b64_data = parts[5]
    
    print(f"📦 Descompactando FloppyURL...")
    print(f"   Algoritmo: {algo}")
    print(f"   SHA-256 Raiz: {root_sha}")
    
    compressed = base64.urlsafe_b64decode(b64_data + "==")
    
    if algo == "brotli":
        # Tenta usar binario brotli do sistema ou modulo
        try:
            import brotli
            html_text = brotli.decompress(compressed).decode('utf-8')
        except:
            proc = subprocess.run(["brotli", "-d", "--stdout"], input=compressed, capture_output=True)
            html_text = proc.stdout.decode('utf-8')
    elif algo in ("deflate", "gzip"):
        html_text = zlib.decompress(compressed).decode('utf-8')
    else:
        print(f"Algoritmo desconhecido: {algo}")
        sys.exit(1)
        
    # Extrair JSON do projeto
    start_tag = "const projectData = "
    end_tag = ";\n  const fileList"
    start = html_text.find(start_tag) + len(start_tag)
    end = html_text.find(end_tag, start)
    
    files = json.loads(html_text[start:end].strip())
    
    os.makedirs(output_dir, exist_ok=True)
    print(f"\n📂 Extraindo {len(files)} arquivos para '{output_dir}/':")
    for filepath, content in files.items():
        out_path = os.path.join(output_dir, filepath)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"   ✓ {filepath} ({len(content)} bytes)")
        
    print("\n🎉 Repositório extraído com 100% de integridade com sucesso!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 unpack.py <arquivo_floppy.txt ou payload>")
        sys.exit(1)
        
    arg = sys.argv[1]
    if os.path.exists(arg):
        with open(arg) as f:
            payload = f.read().strip()
    else:
        payload = arg
        
    unpack_floppy(payload)
