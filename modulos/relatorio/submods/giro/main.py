from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from core.scroll_utils import centralizar_elemento_na_tela
from core._ui import escolher_modulo_no_navegador, confirmar
import importlib
import os
import time

from core._ui import escolher_modulo_no_navegador
from core._ui import confirmar

def executar(driver, sub_name=None, **kwargs):
    # Se sub_name vier como "giro.teste", pega só o subsubmodulo
    if sub_name and "." in sub_name:
        _, sub_name = sub_name.split(".", 1)
        print (f"DEBUG: sub_name ajustado para '{sub_name}'")

    # 1. Executa o fluxo padrão do giro (abrir grid, selecionar relatório, clicar em executar)
    wait = WebDriverWait(driver, 20)
    while True:
        try:
            wait.until_not(EC.visibility_of_element_located((By.CSS_SELECTOR, "#divLoading, .loading-panel")))
        except Exception:
            pass
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#gridRelatorios, .relatorio-grid")))
        scrollar_grid_ate_carregar_tudo(driver)
        linhas = driver.find_elements(By.CSS_SELECTOR, "table#gridRelatorios tbody tr")
        print(f"DEBUG: {len(linhas)} linhas encontradas na grid de relatórios")
        idx_giro = None
        for idx, linha in enumerate(linhas):
            try:
                centralizar_elemento_na_tela(driver, linha)
                tds = linha.find_elements(By.TAG_NAME, "td")
                if len(tds) > 2:
                    codigo = tds[1].text.strip()
                    nome = tds[2].text.strip()
                    if codigo == "48" and "giro" in nome.lower():
                        print(f"DEBUG: Linha {idx}: codigo={codigo}, nome={nome}")
                        idx_giro = idx
                        break
            except Exception:
                continue
        if idx_giro is not None:
            break  # Achou, sai do loop
        # Não achou, pergunta se quer tentar de novo
        if not confirmar(driver, "Relatório Giro de Mesas (código 48) não encontrado na grid.\nDeseja tentar novamente?"):
            raise Exception("Relatório Giro de Mesas (código 48) não encontrado na grid.")
    linhas = driver.find_elements(By.CSS_SELECTOR, "table#gridRelatorios tbody tr")
    linha_giro = linhas[idx_giro]
    centralizar_elemento_na_tela(driver, linha_giro)
    time.sleep(0.3)
    linha_giro.click()
    btn_executar = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Executar')]")))
    btn_executar.click()
    print("Relatório Giro de Mesas executado com sucesso!")

    # 2. Troca para a nova aba
    time.sleep(1)
    abas = driver.window_handles
    newtab = None
    if len(abas) > 1:
        driver.switch_to.window(abas[-1])
        newtab = "Estamos em uma nova aba"
        print(newtab)
    else:
        print("DEBUG: Nenhuma nova aba detectada.")

    # 3. Espera o body da nova aba carregar
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    # 4. Só agora pergunta/interage com o sub-submódulo
    if newtab == "Estamos em uma nova aba":
        if not sub_name:
            # Lista sub-submódulos disponíveis (pastas com main.py)
            print("DEBUG: Listando sub-submódulos disponíveis...")
            pasta = os.path.dirname(__file__)
            opcoes = []
            for nome in os.listdir(pasta):
                subpasta = os.path.join(pasta, nome)
                if os.path.isdir(subpasta) and os.path.isfile(os.path.join(subpasta, "main.py")):
                    opcoes.append(nome)
            if not opcoes:
                print("Nenhuma ação disponível.")
                input("Pressione Enter para continuar...")
                return
            sub_name = escolher_modulo_no_navegador(
                driver, opcoes, mensagem="Escolha a ação desejada para o relatório Giro de Mesas:"
            )
            if not sub_name:
                print("Execução cancelada pelo usuário.")
                return
    else:
        print("DEBUG: Parece que não estamos em uma nova aba.")
        if confirmar(driver, "Não foi possível detectar a nova aba do relatório.\nDeseja tentar novamente?"):
            # Volta para o início do fluxo (recarrega a grid e tenta de novo)
            return executar(driver, sub_name=sub_name, **kwargs)
        else:
            print("Execução cancelada pelo usuário.")
            return

    # 5. Executa o sub-submódulo
    if sub_name:
        try:
            mod = importlib.import_module(f"modulos.relatorio.submods.giro.{sub_name}.main")
            if hasattr(mod, "executar"):
                return mod.executar(driver, **kwargs)
            else:
                raise Exception(f"O sub-submódulo '{sub_name}' não possui função 'executar'.")
        except ModuleNotFoundError:
            raise Exception(f"Sub-submódulo '{sub_name}' não encontrado em 'giro'.")

def scrollar_grid_ate_carregar_tudo(driver, grid_selector="#gridRelatorios", delay=0.7, max_iter=30):
    grid = driver.find_element(By.CSS_SELECTOR, grid_selector)
    last_height = driver.execute_script("return arguments[0].scrollHeight", grid)
    for _ in range(max_iter):
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", grid)
        time.sleep(delay)
        new_height = driver.execute_script("return arguments[0].scrollHeight", grid)
        if new_height == last_height:
            break
        last_height = new_height