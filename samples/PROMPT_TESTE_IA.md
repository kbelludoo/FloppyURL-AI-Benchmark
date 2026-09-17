# 🧪 Teste Cego para Chats de IA (ChatGPT, Claude, Gemini, DeepSeek)

Copie o prompt abaixo e cole no seu chat de IA favorito para testar a capacidade de auditar repositórios completos transmitidos via FloppyURL:

---

### 📋 Copie o Prompt abaixo:

> Você é um engenheiro de software sênior e auditor de código.
> Eu empacotei um repositório Git completo em um único pacote serializado com integridade SHA-256 usando a tecnologia **FloppyURL v2.0**.
>
> Abaixo está o script Python de descompactação e o payload base64 comprimido:
> 
> ```python
> # Para extrair e auditar:
> import base64, subprocess, json
> payload = "COLE_AQUI_O_CONTEUDO_DE_floppyurl_core_repo.txt"
> parts = payload.split(";")
> b64_data = parts[5]
> raw = base64.urlsafe_b64decode(b64_data + "==")
> html = subprocess.run(["brotli", "-d", "--stdout"], input=raw, capture_output=True).stdout.decode('utf-8')
> start = html.find("const projectData = ") + len("const projectData = ")
> end = html.find(";\n  const fileList", start)
> files = json.loads(html[start:end].strip())
> ```
> 
> Com base nos arquivos extraídos deste repositório, responda:
> 1. Quais são todos os arquivos presentes na raiz e nas subpastas?
> 2. No arquivo `main.go`, quais são os algoritmos suportados na flag `-algo`?
> 3. No arquivo `descompressor.go`, qual é a função registrada no objeto `window` do navegador para execução via WebAssembly?
> 4. Qual é a assinatura de integridade SHA-256 que consta no cabeçalho do payload?
---
