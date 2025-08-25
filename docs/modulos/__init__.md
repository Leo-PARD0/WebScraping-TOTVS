# `modulos/__init__.py` — Guia de uso

Este documento explica o papel do arquivo `modulos/__init__.py` no projeto WebScraping-TOTVS.

---

## 1) Objetivo

O `__init__.py` transforma a pasta `modulos/` em um **pacote Python**.  
Isso permite que o `launcher.py` e outras partes do sistema importem os módulos dinamicamente.

---

## 2) Conteúdo recomendado

Normalmente, o `__init__.py` em `modulos/` não precisa de lógica.  
Ele serve apenas para marcar a pasta como pacote.

Exemplo sugerido:

```python
"""Pacote de módulos de automação do WebScraping-TOTVS.

Cada arquivo .py aqui deve conter a função executar(driver, **kwargs).
"""
```

---

## 3) Boas práticas

- Não coloque lógica dentro do `__init__.py`.  
- Use-o apenas como documentação mínima.  
- A função `listar_modulos()` em `core/utils.py` já faz o trabalho de varrer a pasta.  

---

## 4) TL;DR

- `modulos/__init__.py` marca a pasta como pacote.  
- Não precisa de código além de uma docstring.  
- Garante que os imports dinâmicos funcionem.  
