# `extrair_aliquota.py` — Guia de uso

## 1) Objetivo do arquivo
O `extrair_aliquota.py` é um **submódulo** do pacote `cadastro_produtos`.  
Sua função é **coletar dados de alíquotas fiscais** dos produtos na tela de **Cadastros ▸ Produto/Serviço** do TOTVS e exportá-los em formatos reutilizáveis.

---

## 2) Estrutura do diretório

```
modulos/cadastro_produtos/
└─ submods/
   ├─ __init__.py
   └─ extrair_aliquota.py   # ESTE ARQUIVO
```

---

## 3) Fluxo principal

1. Assume que o `main.py` já navegou até a tela de **Produto/Serviço**.  
2. Localiza a grid de produtos (`#gridProdutos` ou `table#gridProdutos`).  
3. Extrai os cabeçalhos (`thead th`) e cada linha da tabela (`tbody tr > td`).  
4. Monta uma lista de dicionários com as colunas e valores.  
5. Exporta os dados em:
   - `artifacts/output/aliquotas.csv`
   - `artifacts/output/aliquotas.json`  

---

## 4) Principais funções

### `_coletar_dados_tabela(driver, timeout=20)`
- Espera a grid de produtos carregar.  
- Extrai cabeçalhos e linhas.  
- Retorna lista de `dict` → cada item é um produto com suas colunas.  

### `executar(driver)`
- Função pública exigida de todo submódulo.  
- Chama `_coletar_dados_tabela`.  
- Em caso de falha: loga erro + tira screenshot (`erro_extrair_aliquota.png`).  
- Em caso de sucesso: salva CSV/JSON usando `utils.salvar_csv` e `utils.salvar_json`.  

---

## 5) Papel dentro do projeto
- É um **submódulo especializado**: foca apenas na extração de alíquotas.  
- Reutiliza infraestrutura do projeto:
  - `navigate.py` para garantir navegação (feito pelo `main.py`).
  - `utils.py` para exportação, logs e screenshots.  
- Mantém o código **magro e coeso**, isolando a lógica de scraping fiscal.  

---

## 6) TL;DR
- `extrair_aliquota.py` = submódulo que **lê a tabela de produtos e exporta alíquotas**.  
- Entrada: driver já posicionado na tela de Produto/Serviço.  
- Saída: arquivos `aliquotas.csv` e `aliquotas.json` em `artifacts/output/`.  
