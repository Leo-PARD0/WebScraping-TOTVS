# `core/__init__.py` — Guia de uso

Este documento explica **o papel** do `core/__init__.py` no projeto, **como ele funciona** no Python e **qual implementação recomendamos** para o WebScraping-TOTVS neste momento.

---

## 1) O que é o `__init__.py`?

No Python, um diretório só é reconhecido como **pacote** se contiver um arquivo `__init__.py`.  
Ao importar o pacote (por exemplo, `import core`), o interpretador executa o conteúdo de `core/__init__.py` **antes** de disponibilizar os submódulos (como `core.browser`, `core.auth`, etc.).

### Funções típicas do `__init__.py`
- **Marcar o diretório como pacote** (uso mais comum).
- **Expor uma API pública** do pacote com `__all__` ou imports de conveniência.
- **Executar configuração inicial** do pacote (ex.: preparar logging, variáveis globais, leitura de configs).

> ⚠️ **Boa prática:** manter o `__init__.py` **enxuto**. Configurações pesadas ou lógicas complexas podem causar efeitos colaterais inesperados no momento da importação.

---

## 2) Recomendações para este projeto

Neste estágio, queremos o `core/__init__.py` **mínimo e descritivo**, sem lógica de execução.  
Isso mantém o **acoplamento baixo** e evita side-effects quando scripts importarem `core` apenas para acessar submódulos.

### Implementação recomendada (atual)
```python
"""Core do WebScraping-TOTVS.

Contém os módulos centrais:
- launcher: ponto de entrada do sistema
- auth: autenticação e seleção de domínio
- browser: configuração do WebDriver
- utils: funções auxiliares
- locators.yaml: seletores centralizados (CSS/XPath)
"""
```

Salve esse conteúdo em `core/__init__.py`.

---

## 3) Opções avançadas (para o futuro)

Caso, no futuro, você queira facilitar os imports (ex.: `from core import build_driver, login`), é possível **expor** funções-chave aqui.

### 3.1) API pública via imports de conveniência
```python
# core/__init__.py
from .browser import build_driver  # exemplo: função a ser exposta
from .auth import login, selecionar_dominio

__all__ = ["build_driver", "login", "selecionar_dominio"]
```
**Prós:** ergonomia — menos texto ao importar.  
**Contras:** aumenta o acoplamento entre arquivos; qualquer mudança em `browser/auth` pode afetar o `__init__.py`.

### 3.2) Imports atrasados (lazy) para evitar custo de import
Se o pacote crescer, você pode **atrasar** algumas importações para quando forem realmente usadas:
```python
# core/__init__.py (exemplo ilustrativo)
def __getattr__(name):
    if name == "build_driver":
        from .browser import build_driver
        return build_driver
    if name in {"login", "selecionar_dominio"}:
        from .auth import login, selecionar_dominio
        return {"login": login, "selecionar_dominio": selecionar_dominio}[name]
    raise AttributeError(name)
```
> Útil quando módulos têm importações pesadas (não é o caso agora).

### 3.3) Configuração de logging (com cautela)
Se decidir configurar **logging** aqui, mantenha **mínimo**:
```python
# core/__init__.py (exemplo)
import logging

logger = logging.getLogger("core")
if not logger.handlers:  # evita handlers duplicados em re-imports
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
```
> ⚠️ Prefira centralizar logging no `launcher.py` para controle global do processo.

---

## 4) Como isso impacta os demais arquivos do core?

- **`core/launcher.py`**: é quem orquestra a execução. Ele importa diretamente `core.browser`, `core.auth` e `core.utils`.  
  Como o `__init__.py` não tem lógica, não cria overhead na inicialização.

- **`core/browser.py`**, **`core/auth.py`**, **`core/utils.py`**: permanecem **independentes**.  
  Nada no `__init__.py` impede que você os importe diretamente quando precisar.

---

## 5) Testes rápidos para validar o pacote

No Python REPL (ou em um script temporário na raiz do projeto):
```python
import core
import core.browser
import core.auth
import core.utils

print(core.__file__)          # deve apontar para core/__init__.py
print(core.browser.__file__)  # deve apontar para core/browser.py
```
Se isso funcionar sem erros, o pacote `core` está corretamente estruturado.

---

## 6) Erros comuns (e como evitar)

- **Colocar lógica pesada no `__init__.py`**  
  *Evite.* Prefira que o `launcher.py` coordene a inicialização e o logging.

- **Imports circulares**  
  Se o `__init__.py` importar submódulos e esses submódulos importarem `core` de volta, você pode criar um ciclo.  
  *Sinal de alerta:* `ImportError: cannot import name ...` durante a importação.

- **Duplicação de handlers de logging**  
  Ao executar múltiplas vezes em ambientes interativos, verifique `if not logger.handlers:` antes de adicionar handlers.

---

## 7) TL;DR

- `__init__.py` marca o diretório como **pacote** e roda ao importar `core`.
- **Agora**: mantenha-o **mínimo** (apenas docstring).
- **Depois** (opcional): exponha uma **API pública** ou logging leve, se fizer sentido.
- Evite side-effects; deixe o `launcher.py` coordenar a inicialização do app.

---

### Versão recomendada para já colocar no projeto

```python
"""Core do WebScraping-TOTVS.

Contém os módulos centrais:
- launcher: ponto de entrada do sistema
- auth: autenticação e seleção de domínio
- browser: configuração do WebDriver
- utils: funções auxiliares
- locators.yaml: seletores centralizados (CSS/XPath)
"""
```
