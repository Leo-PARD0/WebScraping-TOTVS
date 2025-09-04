from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def abrir_produto_na_grid(driver, criterio: dict):
    """
    Busca a linha da grid que bate com o critério, centraliza na tela e clica no primeiro <td>.
    Exemplo de critério: {"codigo": "123"}, {"nome": "Produto X"}
    """
    linhas = driver.find_elements(By.CSS_SELECTOR, 'tr[id^="dataGrid_DXDataRow"]')
    for linha in linhas:
        tds = linha.find_elements(By.TAG_NAME, "td")
        if not tds:
            continue
        codigo = tds[0].text.strip()
        nome = tds[1].text.strip() if len(tds) > 1 else ""
        if ("codigo" in criterio and criterio["codigo"] == codigo) or \
           ("nome" in criterio and criterio["nome"].lower() in nome.lower()):
            # Centraliza a célula na tela antes de clicar
            driver.execute_script("""
                const el = arguments[0];
                const rect = el.getBoundingClientRect();
                window.scrollTo({
                    top: rect.top + window.scrollY - (window.innerHeight / 2) + (rect.height / 2),
                    behavior: 'smooth'
                });
            """, tds[0])
            import time
            time.sleep(0.2)
            tds[0].click()
            return True
    return False

def aguardar_overlay_sumir(driver, timeout=10):
    try:
        WebDriverWait(driver, timeout).until_not(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".dxgvLoadingPanel, .loading, .overlay"))
        )
    except Exception:
        pass

def selecionar_linha_por_indice(driver, indice_global: int) -> bool:
    try:
        aguardar_overlay_sumir(driver)
        driver.execute_script(
            "try{ if(window.dataGrid){"
            " dataGrid.SetFocusedRowIndex(arguments[0]);"
            " if(dataGrid.SelectRow) dataGrid.SelectRow(arguments[0]);"
            "}}catch(e){}",
            int(indice_global)
        )
        try:
            row = driver.find_element(By.ID, f"dataGrid_DXDataRow{indice_global}")
            print("Linha encontrada:", row)
        except Exception as e:
            print(f"Linha {indice_global} não encontrada:", e)
            return False
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", row)
        WebDriverWait(driver, 5).until(
            lambda d: "dxgvSelectedRow" in row.get_attribute("class")
        )
        return True
    except Exception as e:
        print("Erro ao selecionar linha:", e)
    return False