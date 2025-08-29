# `navigate.py` — Guia de uso

## 1) Objetivo do arquivo
O `navigate.py` concentra todas as **funções de navegação Selenium** específicas do fluxo de **Cadastro de Produtos**.  
Ele abstrai as ações repetitivas de abrir o menu principal do TOTVS e acessar a tela **Cadastros ▸ Produto/Serviço**.

Isso garante que outros arquivos (`main.py`, submódulos etc.) fiquem mais enxutos e reutilizem sempre a mesma lógica de navegação.

---

## 2) Estrutura do diretório

```
modulos/cadastro_produtos/
├─ __init__.py
├─ main.py
├─ _ui.py
├─ navigate.py       # ESTE ARQUIVO
└─ submods/
```

---

## 3) Principais funções

### `abrir_menu_principal(driver, timeout=20)`
- Garante que o **menu principal** esteja visível.
- Se o menu não estiver aberto, tenta clicar em toggles conhecidos (`newMenu`, `btnMenu`, etc.).
- Aguarda overlays de carregamento sumirem (`divLoading`, `loading`, etc.).

### `ir_para_produto_servico(driver, timeout=20)`
- Navega até o item de menu **Cadastros ▸ Produto/Serviço**.
- Testa múltiplos `href` conhecidos:
  - `/Cadastros/ProdutoServico`
  - `/Cadastros/Produtos`
  - `/ProdutoServico`
- Confirma que a tela foi carregada verificando:
  - `form#formProduto`
  - `<h1>` ou `<h2>` contendo a palavra "Produto".

### Funções auxiliares
- `_primeiro_visivel(...)` → retorna o primeiro elemento visível de uma lista de candidatos.  
- `_clicar_com_fallback(...)` → tenta `click()`, se falhar usa `execute_script("click")`.  
- `_esperar_overlays_sumirem(...)` → aguarda desaparecimento de sobreposições de carregamento.  
- `_clicar_item_menu_por_href(...)` → clica em um item de menu com base no `href`.  
- `_esperar_tela_produto(...)` → valida que a tela de produto carregou.

---

## 4) Papel dentro do projeto
- **Centraliza a lógica de navegação** para o TOTVS.  
- Garante **resiliência** quando os IDs/paths mudam entre versões (usa múltiplos candidatos).  
- Reduz **duplicação de código**: submódulos e `main.py` não precisam reimplementar a navegação.  
- Mantém o projeto **magro e modular**, alinhado à filosofia de separar responsabilidades.

---

## 5) TL;DR
- `navigate.py` = **atalhos de navegação Selenium**.  
- Reúne funções reutilizáveis para abrir menu e entrar em Produto/Serviço.  
- Ajuda a manter o código limpo, reduzindo repetição entre módulos.  
