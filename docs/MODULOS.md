# `modulos/` — Guia de uso

Este documento explica o papel da pasta `modulos/` no projeto WebScraping-TOTVS, como ela se integra ao `launcher.py` e como criar novos módulos.

---

## 1) Objetivo da pasta `modulos/`

A pasta `modulos/` contém todos os **módulos de automação** disponíveis para execução.  
Cada módulo é um arquivo `.py` que implementa obrigatoriamente a função:

```python
def executar(driver, **kwargs):
    ...
```

O `launcher.py` descobre automaticamente todos os arquivos `.py` dentro de `modulos/` que tenham essa função e apresenta uma lista para o usuário escolher qual executar.

---

## 2) Estrutura esperada

```
modulos/
├─ __init__.py
├─ teste.py
├─ cadastro_produtos.py
└─ exportar_relatorios.py
```

- `__init__.py`: marca a pasta como pacote Python.  
- `teste.py`: exemplo de módulo básico.  
- `cadastro_produtos.py`: exemplo de automação real.  
- `exportar_relatorios.py`: outro exemplo.

---

## 3) Regras para criar módulos

1. **Nome**: use `snake_case.py` (`nome_do_modulo.py`).  
2. **Função obrigatória**:
   ```python
   def executar(driver, **kwargs):
       # sua lógica aqui
   ```
3. **Imports permitidos**:
   - Selenium (`By`, `WebDriverWait`, `EC`)  
   - Utilidades do `core.utils` (ex.: `load_locators`)  
4. **Saídas**:
   - Se exportar dados, salve em `output/`  
   - Se gerar prints ou logs, use `artifacts/`  

---

## 4) Exemplo de módulo de teste (`modulos/teste.py`)

```python
def executar(driver, **kwargs):
    print("✅ Módulo de teste executado com sucesso!")
```

---

## 5) Fluxo de execução

1. O usuário roda `python -m core.launcher`.  
2. Faz login no TOTVS.  
3. O `launcher` lista todos os módulos em `modulos/`.  
4. O usuário escolhe um.  
5. O `launcher` chama `executar(driver)` do módulo escolhido.  

---

## 6) TL;DR

- `modulos/` = repositório de automações.  
- Cada arquivo = um módulo com função `executar`.  
- `launcher.py` lista e executa automaticamente.  
- Saídas vão para `output/`, prints e logs para `artifacts/`.  
