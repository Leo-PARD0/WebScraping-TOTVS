# `core/launcher.py` — Guia de uso (versão atualizada)

Este documento descreve o papel e funcionamento do `launcher.py` atualizado.

---

## 1) Objetivo

O `launcher.py` é o **ponto de entrada** do WebScraping-TOTVS.  
Ele coordena todo o fluxo principal:

1. Lê configurações de credenciais e parâmetros (via `.env`, variáveis de ambiente ou entrada interativa).  
2. Cria o driver (`browser.py`).  
3. Faz login (`auth.py`).  
4. Seleciona domínio, se necessário (`auth.py`).  
5. Lista e executa módulos em `modulos/`.  
6. Trata erros e salva prints em `artifacts/`.  

---

## 2) Principais mudanças desta versão

- **Fallback de import**: agora aceita rodar tanto como pacote (`python -m core.launcher`) quanto diretamente (`python core/launcher.py`).  
- **Salvamento opcional em `.env`**: ao informar credenciais manualmente, o usuário pode optar por salvá-las em `.env` para não precisar digitar novamente.  
- **Dataclass `Config`** centraliza as configs (url, usuário, senha, timeouts, etc).  
- **Tratamento de exceções** robusto: salva screenshot e loga o erro antes de encerrar o driver.  

---

## 3) Estrutura principal

### Configuração (`Config` e `get_config()`)
- Primeiro tenta ler do `.env`/variáveis.  
- Se faltar alguma credencial, pergunta no console (`input`/`getpass`).  
- Pergunta se deseja salvar em `.env`.  

### Execução (`main()`)
1. Cria o driver com `build_driver(cfg)`.  
2. Chama `login(driver, cfg)` e depois `selecionar_dominio(driver)`.  
3. Lista módulos (`listar_modulos`).  
4. Permite escolher (`escolher_modulo`).  
5. Executa o módulo escolhido.  
6. Em caso de erro → loga, printa, encerra driver.

---

## 4) Boas práticas de uso

- Sempre rodar da raiz do projeto com:
  ```bash
  python -m core.launcher
  ```
- Se preferir execução direta (`python core/launcher.py`), o fallback garante funcionamento.  
- Não versionar o `.env` com credenciais (já está no `.gitignore`).  
- Adicionar novos módulos em `modulos/` com função `executar(driver, **kwargs)`.  

---

## 5) TL;DR

- Launcher é o orquestrador.  
- Agora suporta fallback de import.  
- Pergunta se quer salvar credenciais em `.env`.  
- Lista módulos e executa automaticamente.  
