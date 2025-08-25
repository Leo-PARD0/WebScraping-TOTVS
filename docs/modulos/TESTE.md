# `modulos/teste.py` — Guia de uso (Smoke Test)

Este documento descreve o módulo **`teste.py`**, usado como *smoke test* para validar o fluxo principal (login → domínio → execução de módulo).

---

## 1) Objetivo

- Verificar rapidamente se o **login** foi concluído.  
- Confirmar se a **seleção de domínio** ocorreu (quando aplicável).  
- Garantir que o **framework de módulos** está funcionando (descoberta e execução).

Este módulo **não altera dados** no TOTVS — apenas realiza checagens leves e imprime mensagens no terminal.

---

## 2) Requisitos

- Ter o projeto configurado e executando o launcher com sucesso:  
  ```bash
  python -m core.launcher
  ```
- Ter os seletores corretos no `core/locators.yaml` (seções `login` e `dominio`).

---

## 3) Implementação sugerida

Crie o arquivo `modulos/teste.py` com o conteúdo abaixo:

```python
# modulos/teste.py
"""
Módulo de teste básico (smoke test).
- Verifica se há indícios de pós-login.
- Verifica (opcionalmente) se o domínio foi confirmado.
- Não faz alterações no sistema.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from core.utils import load_locators

def executar(driver, **kwargs):
    wait = WebDriverWait(driver, 20)
    loc_login = load_locators("login") or {}
    loc_dom   = load_locators("dominio") or {}

    ok_login = False
    ok_dom   = False

    # 1) Checagem de pós-login
    after_login_sel = loc_login.get("after_login", "ul#novoMenu")
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, after_login_sel)))
        ok_login = True
        print("[OK] Elemento de pós-login detectado:", after_login_sel)
    except Exception:
        print("[!] Não foi possível confirmar pós-login via seletor:", after_login_sel)

    # 2) Checagem de domínio (se definido no YAML)
    confirmado_sel = loc_dom.get("confirmado")
    if confirmado_sel:
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, confirmado_sel)))
            ok_dom = True
            print("[OK] Domínio confirmado via seletor:", confirmado_sel)
        except Exception:
            print("[!] Não foi possível confirmar domínio via seletor:", confirmado_sel)
    else:
        ok_dom = ok_login  # se não houver seletor de confirmação, considere login suficiente

    # 3) Resultado geral
    if ok_login and ok_dom:
        print("✅ Módulo de teste executado com sucesso (login + domínio parecem OK).");
    elif ok_login:
        print("⚠️ Login parece OK, mas não confirmamos domínio.");
    else:
        print("❌ Não conseguimos confirmar nem login nem domínio. Revise os seletores em core/locators.yaml.");
```

---

## 4) Como executar

1. Rode o launcher:
   ```bash
   python -m core.launcher
   ```
2. Na lista de módulos, selecione **`teste`**.  
3. Observe as mensagens no terminal indicando o status do login e do domínio.

---

## 5) Saídas esperadas

Mensagens no terminal como:
```
[OK] Elemento de pós-login detectado: #navbar .current-domain
[OK] Domínio confirmado via seletor: ul#novoMenu
✅ Módulo de teste executado com sucesso (login + domínio parecem OK).
```

---

## 6) Solução de problemas

- **Timeout nas checagens**: atualize os seletores em `core/locators.yaml` (`login.after_login` e `dominio.confirmado`).  
- **Módulo não aparece na lista**: verifique se o arquivo está em `modulos/` e se a função `executar` existe.  
- **Erro de import**: certifique-se de que existe `modulos/__init__.py` e que você está rodando com `python -m core.launcher`.  

---

## 7) TL;DR

- `teste.py` valida o pipeline sem alterar dados.  
- Requer locators corretos.  
- Ajuda a isolar problemas de login/domínio antes de implementar módulos de negócio.
