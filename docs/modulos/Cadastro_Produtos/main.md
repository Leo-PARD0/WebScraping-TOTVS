# `main.py` — Guia de uso

## 1) Objetivo do arquivo
O `main.py` é o **ponto de entrada** do módulo `cadastro_produtos`.  
Ele orquestra o fluxo principal:

1. Abre o menu do TOTVS.  
2. Entra em **Cadastros ▸ Produto/Serviço**.  
3. Lista os submódulos em `submods/`.  
4. Permite ao usuário escolher um submódulo via modal no navegador.  
5. Importa e executa o submódulo escolhido.  

---

## 2) Estrutura do diretório

```
modulos/cadastro_produtos/
├─ __init__.py
├─ main.py          # ESTE ARQUIVO
├─ navigate.py
├─ ui.py
└─ submods/
   └─ extrair_aliquota.py
```

---

## 3) Principais funções

### `executar(driver)`
- **Ponto de entrada** do módulo.
- Garante que o menu principal esteja visível (`abrir_menu_principal`).
- Navega até a tela de Produto/Serviço (`ir_para_produto_servico`).
- Lista os submódulos em `submods/`.
- Abre um modal de seleção (`escolher_modulo_no_navegador`).
- Importa e executa o submódulo escolhido.
- Exibe notificações (`toast`) de início e fim da execução.

### Funções auxiliares
- `_listar_submodulos()` → varre `submods/` em busca de arquivos `.py` válidos.  
- `_escolher_submodulo(driver, mods)` → abre o modal de escolha (default: `extrair_aliquota`).  
- `_importar_submodulo(nome)` → importa dinamicamente o submódulo escolhido.  

---

## 4) Papel dentro do projeto
- É o **hub central** do pacote `cadastro_produtos`.  
- Faz a ponte entre a **navegação Selenium** (em `navigate.py`) e a **UI de seleção** (em `ui.py`).  
- Garante que todos os submódulos sigam o mesmo padrão de execução (`executar(driver)`).  
- Mantém o fluxo **organizado e extensível**: novos submódulos podem ser adicionados em `submods/` sem alterar este arquivo.

---

## 5) TL;DR
- `main.py` = **ponto de entrada do cadastro_produtos**.  
- Abre menu → entra em Produto/Serviço → lista submódulos → executa o escolhido.  
- Centraliza a lógica e mantém o projeto modular.  
