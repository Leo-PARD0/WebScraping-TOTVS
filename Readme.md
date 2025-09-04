# WebScraping-TOTVS

Automação de extração e cadastro de dados no sistema TOTVS ChefWeb Cloud utilizando Selenium WebDriver.

## Objetivo

Automatizar tarefas repetitivas no TOTVS ChefWeb Cloud, como:
- Extração de relatórios e dados (ex: giro de mesas, valor x mesa x dia)
- Cadastro e atualização de terminais e produtos
- Navegação automatizada por menus e popups
- Manipulação de filtros, grids e formulários

## Principais Funcionalidades

- **Automação de relatórios:** Seleção de datas, aplicação de filtros, extração de dados de grids.
- **Cadastro de terminais:** Navegação até o menu de cadastro, preenchimento e envio de formulários.
- **Utilitários de interface:** Funções para aguardar carregamento, clicar em botões, preencher campos, manipular popups e iframes.
- **Estrutura modular:** Cada funcionalidade está separada em módulos e submódulos para facilitar manutenção e expansão.

## Estrutura do Projeto

```
core/
    _ui.py
    launcher.py
    scroll_utils.py
    utils.py
modulos/
    cadastro_produtos/
        grid_utils.py
        main.py
        submods/
            extrair_aliquota.py
    relatorio/
        main.py
        submods/
            giro/
                main.py
                utils_popup.py
                valorxmesaxdia/
                    main.py
    TERMINAIS_X_ESTOQUE/
        main.py
        __init__.py
```

## Requisitos

- Python 3.8+
- Google Chrome (recomendado)
- [ChromeDriver](https://chromedriver.chromium.org/downloads) compatível com sua versão do Chrome
- Selenium (`pip install selenium`)
- VS Code (opcional, recomendado para desenvolvimento)

## Instalação

1. Clone o repositório:
    ```
    git clone https://github.com/Leo-PARD0/WebScraping-TOTVS.git
    ```
2. Crie e ative um ambiente virtual:
    ```
    python -m venv .venv
    .venv\Scripts\activate
    ```
3. Instale as dependências:
    ```
    pip install selenium
    ```

## Como usar

1. Configure o caminho do ChromeDriver em `core/launcher.py` se necessário.
2. Execute o launcher:
    ```
    python core/launcher.py
    ```
3. Siga as instruções no terminal para selecionar o módulo desejado e informar parâmetros (datas, filtros, etc).

## Exemplos de Uso

### Extração de Relatório Valor x Mesa x Dia

- O sistema solicita data inicial e final.
- Para cada dia do período, aplica o filtro e extrai os dados do grid.

### Cadastro de Terminais

- Navega até o menu de cadastro de terminais.
- Preenche os campos necessários e salva o registro.

## Dicas

- Use o modo desenvolvedor do navegador para inspecionar elementos e ajustar seletores.
- Adicione novos módulos em `modulos/` conforme novas necessidades de automação.
- Utilize os utilitários de espera e clique para garantir robustez contra popups e carregamentos.

## Contribuição

Pull requests são bem-vindos!  
Abra issues para sugestões, dúvidas ou problemas encontrados.

## Licença

MIT

---

**Desenvolvido por Leo Pardo e colaboradores.**