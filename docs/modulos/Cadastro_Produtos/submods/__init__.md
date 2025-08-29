# `__init__.py` (submods) — Guia de uso

## 1) Objetivo do arquivo
O `__init__.py` dentro da pasta `submods/` tem como principal função **marcar a pasta como um pacote Python**.  
Isso permite que os submódulos sejam importados dinamicamente pelo `main.py`.

---

## 2) Estrutura do diretório

```
modulos/cadastro_produtos/
└─ submods/
   ├─ __init__.py       # ESTE ARQUIVO
   └─ extrair_aliquota.py
```

---

## 3) Conteúdo do arquivo

```python
# __init__.py
"""
Pacote de submódulos do cadastro_produtos.

Cada arquivo .py aqui deve representar um fluxo específico,
com uma função pública obrigatória:

    def executar(driver) -> None

Exemplo: extrair_aliquota.py
"""
```

---

## 4) Papel dentro do projeto
- Permite que `main.py` trate `submods/` como um pacote Python.  
- Define a **convenção de implementação**: todo submódulo precisa expor `executar(driver)`.  
- Mantém a documentação clara sobre como novos fluxos devem ser adicionados.  

---

## 5) TL;DR
- `__init__.py` em `submods/` = **marca a pasta como pacote**.  
- Garante que submódulos possam ser importados.  
- Explica que cada submódulo precisa implementar `executar(driver)`.  
