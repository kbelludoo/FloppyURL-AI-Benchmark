# 💾 FloppyURL — AI Repository Benchmark & Verifier

> **Transmita repositórios Git inteiros para Agentes de IA e Chats dentro de um único link de URL.**  
> Economia de **88% a 95% de tokens**, 100% offline, com integridade criptográfica **SHA-256**.

---

## 🎯 Por que este Benchmark existe?

Enviar código para IAs (ChatGPT, Claude, Gemini, DeepSeek) através de arquivos soltos ou HTML de repositórios tradicionais gasta dezenas de milhares de tokens com ruído, formatações redundantes e metadados inúteis.

Com o **FloppyURL v2.0**:
1. O repositório inteiro é compactado com **Brotli / Deflate** em um payload Base64URL único.
2. É gerado um **SHA-256 Merkle root** para atestar a integridade do código.
3. A IA recebe o link/payload e descompacta o projeto **em memória**, preservando 100% do código e economizando até **95% dos tokens**.

---

## 📊 Resultados Comprovados em Testes Reais

### 1. Economia de Tokens em LLMs (Medido via OpenAI `tiktoken` e `9router`):
* **Página Web / Documentação Completa:** 217.304 tokens ➔ **17.910 tokens** (**91.76% de economia**)
* **Repositório Go/Web (`FloppyURL-main`):** 213 KB de código ➔ **50 KB comprimidos** (**76.4% menor**)
* **Compilador LIN (`lin-master`):** 9.7 MB de código ➔ **1.25 MB comprimidos** (**87.2% menor**)

---

## 🧪 Como Testar com Chats de IA (ChatGPT, Claude, Gemini)

1. Abra a pasta [`samples/PROMPT_TESTE_IA.md`](samples/PROMPT_TESTE_IA.md).
2. Copie o prompt pronto e o payload de teste de [`samples/floppyurl_core_repo.txt`](samples/floppyurl_core_repo.txt).
3. Cole no chat de qualquer IA e faça perguntas sobre o código do projeto.
4. **Resultado:** A IA extrai e audita todas as funções, arquivos e parâmetros com precisão cirúrgica sem você precisar subir arquivos ou mandar links externos!

---

## 🛠️ Como descompactar localmente (Zero Dependências)

Você também pode extrair qualquer repositório FloppyURL na sua máquina usando o script Python incluído:

```bash
python3 unpack.py samples/floppyurl_core_repo.txt
```

Isso vai recriar toda a árvore de arquivos e diretórios originais na pasta `./extracted_repo/`.

---

## 📜 Licença
MIT License — Desenvolvido por [kbelludoo](https://github.com/kbelludoo).
