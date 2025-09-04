from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from core._ui import dialog_input
import time


def selecionar_datas_popup(driver, data_ini: str, data_fim: str, timeout=20):
    wait = WebDriverWait(driver, timeout)

    print("Aguardando modal de filtros...")
    wait.until(EC.visibility_of_element_located(
        (By.XPATH, "//h4[contains(@class,'modal-title') and contains(.,'Filtros')]")
    ))

    # Entra no iframe só para preencher as datas e clicar no botão
    frames = driver.find_elements(By.TAG_NAME, "iframe")
    if frames:
        driver.switch_to.frame(frames[0])
        print("DEBUG: Switched to iframe.")

    # Preenche data inicial
    campo_ini = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[starts-with(@id, 'pDtIni_')]")))
    campo_ini.click()
    campo_ini.clear()
    campo_ini.send_keys(data_ini)
    print(f"Data inicial selecionada: {data_ini}")

    # Preenche data final
    campo_fim = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[starts-with(@id, 'pDtFim_')]")))
    campo_fim.click()
    campo_fim.clear()
    campo_fim.send_keys(data_fim)
    print(f"Data final selecionada: {data_fim}")

    time.sleep(1)  # Pequeno delay para garantir renderização

    print("DEBUG: Listando todos os botões DENTRO do iframe...")
    botoes = driver.find_elements(By.TAG_NAME, "button")
    for btn in botoes:
        print(btn.get_attribute("outerHTML"))

    # Tenta clicar no botão "Filtrar" ainda dentro do iframe
    botao_filtrar = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(@class, 'btn-yellow')]")
    ))
    driver.execute_script("arguments[0].scrollIntoView(true);", botao_filtrar)
    botao_filtrar.click()
    print("Botão de filtrar clicado!")

    # Agora sim, volte para o contexto principal
    driver.switch_to.default_content()
    print("DEBUG: Voltou para o contexto principal.")