# `modulos/cadastro_produtos/__init__.py` — Guia de uso

## 1) Objetivo do arquivo
O `__init__.py` marca a pasta **`cadastro_produtos/`** como um **pacote Python**.  
Além disso, ele reexporta a função principal `executar()` definida em `main.py`, facilitando a importação do módulo inteiro.

Com isso, é possível rodar o fluxo de cadastro de produtos chamando:

```python
import modulos.cadastro_produtos as cp

cp.executar(driver)
```

em vez de precisar fazer:

```python
from modulos.cadastro_produtos.main import executar
```

---

## 2) Estrutura do diretório

```
modulos/cadastro_produtos/
├─ __init__.py        # Reexporta executar()
├─ main.py            # Abre menu e chama submódulos
├─ _ui.py             # Modal de seleção no navegador
├─ _navigate.py       # Funções de navegação Selenium
└─ submods/           # Submódulos específicos (ex.: extrair_aliquota.py)
```

---

## 3) Conteúdo do arquivo

```python
from .main import executar

__all__ = ["executar"]
```

- **`from .main import executar`**  
  Importa a função `executar()` do `main.py`.

- **`__all__ = ["executar"]`**  
  Define explicitamente o que será exposto quando alguém usar `from modulos.cadastro_produtos import *`.  
  Garante clareza: o único ponto de entrada público é o `executar()`.

---

## 4) Papel dentro do projeto
- **Centraliza a interface pública** do pacote.  
- Permite que o **launcher** (`core/launcher.py`) e outros módulos chamem `modulos.cadastro_produtos.executar(driver)` sem se preocupar com a estrutura interna.  
- Mantém o código **magro e coeso**, alinhado com a ideia de modularização:  
  - Navegação → `_navigate.py`  
  - UI → `_ui.py`  
  - Fluxo principal → `main.py`  
  - Submódulos → `submods/*.py`  

---

## 5) TL;DR
- `__init__.py` = **porta de entrada do pacote**.  
- Reexporta `executar()` para simplificar importações.  
- Garante que `cadastro_produtos/` funcione como um módulo limpo e reutilizável.  
