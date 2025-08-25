# `requirements.txt` — Guia de uso

Este documento explica o papel do arquivo `requirements.txt` no projeto WebScraping-TOTVS, sua função e como utilizá-lo.

---

## 1) Objetivo do `requirements.txt`

O arquivo `requirements.txt` lista todas as **dependências externas** necessárias para rodar o projeto.  
Ele permite que qualquer pessoa configure o ambiente de forma padronizada apenas rodando:

```bash
pip install -r requirements.txt
```

---

## 2) Localização

O `requirements.txt` deve estar na **raiz do projeto**, no mesmo nível de `README.md`, `.gitignore` e pastas principais (`core/`, `modulos/`, etc.).

Estrutura de exemplo:

```
WebScraping-TOTVS/
├─ core/
├─ modulos/
├─ artifacts/
├─ output/
├─ docs/
├─ .env.example
├─ .gitignore
├─ README.md
└─ requirements.txt   👈 aqui
```

---

## 3) Conteúdo recomendado

```txt
selenium>=4.23
python-dotenv>=1.0
webdriver-manager>=4.0
pyyaml>=6.0
pandas>=2.2
```

### Explicação de cada dependência

- **selenium** → Biblioteca principal de automação de navegador.  
- **python-dotenv** → Carrega variáveis de ambiente do arquivo `.env`.  
- **webdriver-manager** → Faz download automático do ChromeDriver compatível com sua versão do Chrome.  
- **pyyaml** → Permite ler arquivos YAML, como o `core/locators.yaml`.  
- **pandas** (opcional, mas recomendado) → Facilita manipulação e exportação de dados (CSV/Excel).  

---

## 4) Como instalar

Com a venv ativada, rode:

```bash
pip install -r requirements.txt
```

Isso instalará todas as dependências listadas.

---

## 5) Boas práticas

- **Fixar versões mínimas** (`>=`) garante compatibilidade sem travar upgrades.  
- **Não inclua pacotes desnecessários** → mantenha o arquivo limpo.  
- Se um módulo específico precisar de libs extras, documente em seu `docs/` correspondente.  
- Se começar a usar bibliotecas pesadas (como `openpyxl` ou `requests`), adicione aqui.  

---

## 6) TL;DR

- `requirements.txt` deve ficar na raiz.  
- Contém todas as dependências do projeto.  
- Instalação: `pip install -r requirements.txt`.  
- Mantém o setup do ambiente simples e replicável.  

