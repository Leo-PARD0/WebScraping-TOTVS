# `ui.py` — Guia de uso

## 1) Objetivo do arquivo
O `ui.py` contém **utilitários de interface gráfica** que rodam diretamente no navegador via Selenium + JavaScript.  
Ele permite interações amigáveis com o usuário durante a execução, sem depender do console.

---

## 2) Estrutura do diretório

```
modulos/cadastro_produtos/
├─ __init__.py
├─ main.py
├─ navigate.py
├─ ui.py            # ESTE ARQUIVO
└─ submods/
```

---

## 3) Principais funções

### `escolher_modulo_no_navegador(driver, mods, default_value=None)`
- Abre um **modal interativo** no navegador listando os submódulos disponíveis.
- Permite clicar em um botão ou digitar manualmente o nome.
- Retorna o nome do módulo escolhido (string) ou `None` se cancelado.

### `confirmar(driver, mensagem, ok_text="OK", cancel_text="Cancelar")`
- Exibe uma **caixa de diálogo** simples de confirmação.
- Retorna `True` se o usuário clicar em OK, `False` em Cancelar.

### `toast(driver, mensagem, ms=2000)`
- Mostra uma **notificação temporária** (“toast”) no canto superior direito.
- Desaparece automaticamente após o tempo configurado (padrão: 2 segundos).
- Não bloqueia a execução.

---

## 4) Papel dentro do projeto
- **Substitui o input de console** por interações gráficas dentro do próprio navegador.
- Garante que o operador consiga **escolher módulos** e **confirmar ações** sem precisar alternar para o terminal.
- Mantém a experiência de uso mais fluida e profissional.

---

## 5) TL;DR
- `ui.py` = **camada de interface no navegador**.  
- Inclui modais, caixas de confirmação e notificações rápidas.  
- Torna a execução dos módulos interativa e amigável.  
