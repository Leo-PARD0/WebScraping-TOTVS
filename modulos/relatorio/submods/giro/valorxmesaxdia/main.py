from ..utils_popup import selecionar_datas_popup
from core._ui import toast, dialog_input
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta

def formatar_data(data_str):
    data_str = data_str.strip().replace("/", "")
    if len(data_str) == 8 and data_str.isdigit():
        return f"{data_str[:2]}/{data_str[2:4]}/{data_str[4:]}"
    return data_str

def executar(driver, **kwargs):
    print("VALOR X MESA X DIA executado com sucesso")

    wait = WebDriverWait(driver, 20)
    try:
        wait.until_not(EC.visibility_of_element_located((By.CSS_SELECTOR, "#divLoading, .loading-panel")))
    except Exception:
        pass

    # Aguarda o título "Filtros" ficar visível
    wait.until(EC.visibility_of_element_located((By.XPATH, "//h4[@class='modal-title' and contains(.,'Filtros')]")))

    # Solicita data inicial e final
    while True:
        data_ini = formatar_data(dialog_input(driver, "Digite a DATA INICIAL (formato ddmmaaaa ou dd/mm/aaaa):"))
        data_fim = formatar_data(dialog_input(driver, "Digite a DATA FINAL (formato ddmmaaaa ou dd/mm/aaaa):"))
        try:
            dt_ini = datetime.strptime(data_ini, "%d/%m/%Y")
            dt_fim = datetime.strptime(data_fim, "%d/%m/%Y")
            if dt_fim < dt_ini:
                toast(driver, "Data final não pode ser menor que a inicial!", ms=2500)
                continue
            break
        except Exception:
            toast(driver, "Datas inválidas! Use o formato ddmmaaaa ou dd/mm/aaaa.", ms=2500)

    # Cria lista de datas do período
    lista_datas = []
    atual = dt_ini
    while atual <= dt_fim:
        lista_datas.append(atual.strftime("%d/%m/%Y"))
        atual += timedelta(days=1)

    print(f"Lista de datas: {lista_datas}")

    # Usa a primeira data como parâmetro para o utils_popup
    data = lista_datas[0]
    print(f"Vou chamar o utils_popup para o dia {data}")
    selecionar_datas_popup(driver, data, data)

    print(f"Data inicial selecionada: {data}")
    print(f"Data final selecionada: {data}")
    toast(driver, f"Datas selecionadas: {data}", ms=2500)

    # Após fechar o filtro, aguarda o carregamento dos dados
    wait = WebDriverWait(driver, 30)
    print("Aguardando carregamento dos dados...")
    input("Pressione Enter para continuar...")

    # Aguarda sumir todos os loadings conhecidos
    def nenhum_loading_visivel(driver):
        seletores = [
            "#divLoading",
            ".loading-panel",
            ".bootbox.modal.bematech-modal-wait.in[style*='display: block']"
        ]
        for sel in seletores:
            try:
                el = driver.find_element(By.CSS_SELECTOR, sel)
                if el.is_displayed():
                    return False
            except:
                continue
        return True

    wait.until(nenhum_loading_visivel)

    # Agora aguarda o botão "Atualizar" ficar clicável
    print("Procurando botão de Atualizar para reabrir o filtro...")
    botao_atualizar = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(@onclick, 'showFilters')]")
    ))
    driver.execute_script("arguments[0].scrollIntoView(true);", botao_atualizar)
    botao_atualizar.click()
    print("Botão de Atualizar clicado!")

    input("Pressione Enter para continuar...")