# `core/auth.py` — Guia de uso (versão atualizada)

Este documento descreve o papel e funcionamento do `auth.py` atualizado.

---

## 1) Objetivo

O `auth.py` cuida da **autenticação** e da **seleção de domínio** no TOTVS.  
Ele garante que, após o login, o usuário esteja pronto para executar módulos.

---

## 2) Principais mudanças desta versão

- **Espera inteligente no login**: após clicar em "Entrar", aguarda **OU** o seletor de pós-login (`login.after_login`) **OU** a tela de domínio (`dominio.container`).  
- **Seleção de domínio aprimorada**: identifica tela de domínio, abre combo, escolhe opção (preferida ou primeira), clica em confirmar e valida entrada.  
- **Logs detalhados**: registra se caiu direto na home ou se precisou escolher domínio.  
- **Screenshots em erros**: salva em `artifacts/` para facilitar debug.  

---

## 3) Estrutura principal

### `login(driver, cfg)`
1. Acessa a URL do TOTVS.  
2. Preenche usuário e senha (do `Config`).  
3. Submete o formulário.  
4. Aguarda aparecer **pós-login** ou **tela de domínio**.  
5. Se não encontrar nenhum → timeout + screenshot.

### `selecionar_dominio(driver, preferido=None, timeout=25)`
1. Verifica se existe a tela de seleção de domínio.  
   - Se não existir, prossegue direto.  
2. Se existir:  
   - Abre combo (se presente).  
   - Seleciona a opção (preferida se informada, senão a primeira).  
   - Clica em confirmar (`entrar`).  
   - Aguarda elemento de confirmação (`confirmado`).  
3. Em caso de falha, salva screenshot.  

---

## 4) Dependência de seletores (`locators.yaml`)

Necessário configurar corretamente os seletores no arquivo `core/locators.yaml`.  
Exemplo:

```yaml
login:
  user: "#UserName"
  password: "#Senha"
  submit: "#btnLogin"
  after_login: "#navbar .current-domain"

dominio:
  container: "#divDomain"
  combo: "#comboBoxDomain_chosen"
  opcao: "#comboBoxDomain_chosen .chosen-results li.active-result"
  entrar: "#btnEntrar"
  confirmado: "ul#novoMenu"
```

---

## 5) TL;DR

- `auth.py` faz login e seleciona domínio.  
- Agora espera "home" **ou** "tela de domínio".  
- Se necessário, seleciona domínio automaticamente.  
- Salva screenshot em erros para facilitar debug.  
