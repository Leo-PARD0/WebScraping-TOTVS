# `core/locators.yaml` — Guia de uso

Este documento explica o papel do arquivo `core/locators.yaml` no projeto WebScraping-TOTVS, sua função na arquitetura e a forma recomendada de manutenção.

---

## 1) Objetivo do `locators.yaml`

O arquivo `locators.yaml` centraliza todos os **seletores CSS/XPath** utilizados nas automações.  
Em vez de espalhar strings de seletores dentro do código Python, concentramos tudo em um único lugar.

**Benefícios:**
- **Centralização:** alterações no front-end exigem mudanças apenas neste arquivo.  
- **Legibilidade:** código Python fica mais limpo, sem seletores enormes.  
- **Reuso:** diferentes módulos podem usar os mesmos seletores.  
- **Manutenção simples:** basta atualizar este YAML se o TOTVS mudar IDs/classes.  

---

## 2) Estrutura do arquivo

Organizamos o `locators.yaml` em **seções**, cada uma representando uma tela ou contexto do sistema.

### Exemplo inicial

```yaml
# core/locators.yaml
# Todos os seletores usados no WebScraping-TOTVS.

login:
  user: "#user"                 # campo usuário
  password: "#password"         # campo senha
  submit: "button[type=submit]" # botão entrar
  after_login: "#menuHome"      # elemento que só aparece após login

dominio:
  lista: "#listaDominios"       # container da lista de domínios
  opcao: "li"                   # item individual da lista
  primeiro: "li:first-child"    # seleciona o primeiro item
```

---

## 3) Como carregar os seletores

A leitura é feita por uma função auxiliar em `core/utils.py`:

```python
import yaml
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
LOCATORS_FILE = BASE_DIR / "core" / "locators.yaml"

def load_locators(section: str) -> dict:
    """Carrega os seletores de uma seção do locators.yaml."""
    with open(LOCATORS_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get(section, {})
```

Uso em `auth.py`:

```python
loc = load_locators("login")
user_el = driver.find_element(By.CSS_SELECTOR, loc["user"])
```

---

## 4) Boas práticas

- Prefira **CSS selectors** (mais curtos e legíveis).  
- Use **atributos estáveis** (`id`, `name`, `data-*`) quando disponíveis.  
- Só use **XPath** em último caso (menus complexos, ausência de IDs).  
- Nomeie chaves de forma **clara e curta** (`user`, `password`, `submit`).  
- Separe bem as seções (`login:`, `dominio:`, `cadastro_produto:`).  
- Evite dependência de textos dinâmicos (`//button[text()='Entrar']`).  

---

## 5) Erros comuns

- **Chave não encontrada:** tentar acessar `loc["x"]` quando ela não existe → verifique se a seção está definida.  
- **Seletores desatualizados:** se o TOTVS mudar o HTML → atualizar `locators.yaml`.  
- **Indentação incorreta no YAML:** YAML é sensível a espaços → sempre use 2 espaços por nível.  

---

## 6) TL;DR

- `locators.yaml` guarda todos os seletores do projeto.  
- Alterou o front do TOTVS → só ajusta aqui.  
- Carregado pelo `utils.load_locators(section)`.  
- Mantém o código limpo e a manutenção simples.

