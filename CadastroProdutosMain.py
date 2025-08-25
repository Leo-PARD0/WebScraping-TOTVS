# CadastroProdutos.py
from pathlib import Path
import sys, importlib
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException

def escolher_modulo_no_navegador(driver, mods, default_value=None):
    return driver.execute_async_script("""
      var cb = arguments[arguments.length - 1];
      var mods = arguments[0] || [];
      var def  = arguments[1] || '';
      var old = document.getElementById('gpt-modal-wrap'); if (old) old.remove();
      var wrap = document.createElement('div');
      wrap.id = 'gpt-modal-wrap';
      wrap.style = 'position:fixed;inset:0;background:rgba(0,0,0,.45);display:flex;align-items:center;justify-content:center;z-index:2147483647;';
      var box = document.createElement('div');
      box.style = 'background:#fff;padding:16px;border-radius:10px;min-width:320px;max-width:520px;box-shadow:0 10px 30px rgba(0,0,0,.3);font:14px system-ui,Segoe UI,Arial,sans-serif;';
      box.innerHTML = '<div style="margin-bottom:8px;font-size:16px">Escolha um módulo (CadastroProdutos/):</div>'
                    + '<div id="gpt-list" style="display:flex;flex-wrap:wrap;gap:8px;max-height:240px;overflow:auto;margin-bottom:10px"></div>'
                    + '<div style="display:flex;gap:8px;justify-content:space-between;align-items:center">'
                    + '  <input id="gpt-input" placeholder="ou digite um nome..." style="flex:1;padding:8px;border:1px solid #ccc;border-radius:8px">'
                    + '  <button id="gpt-ok" style="padding:8px 12px;border:1px solid #0a84ff;border-radius:8px;background:#0a84ff;color:#fff">OK</button>'
                    + '  <button id="gpt-cancel" style="padding:8px 12px;border:1px solid #bbb;border-radius:8px;background:#f5f5f5">Cancelar</button>'
                    + '</div>';
      wrap.appendChild(box);
      document.body.appendChild(wrap);
      var list = box.querySelector('#gpt-list');
      mods.forEach(function(m){
        var b = document.createElement('button');
        b.textContent = m;
        b.style = 'padding:6px 10px;border:1px solid #ddd;border-radius:8px;background:#fafafa;cursor:pointer';
        b.onclick = function(){ finish(m); };
        list.appendChild(b);
      });
      var input = box.querySelector('#gpt-input');
      input.value = def || (mods[0] || '');
      input.onkeydown = function(e){ if(e.key==='Enter') finish(input.value.trim()); if(e.key==='Escape') finish(null); };
      box.querySelector('#gpt-ok').onclick = function(){ finish(input.value.trim()); };
      box.querySelector('#gpt-cancel').onclick = function(){ finish(null); };
      var done=false;
      function finish(val){ if(done) return; done=true; try{ wrap.remove(); }catch(e){} cb(val); }
    """, mods, default_value)

def executar(driver):
    wait = WebDriverWait(driver, 20)

    # garantir que o menu grande está visível
    try:
        menus = driver.find_element(By.ID, "menus")
        if not menus.is_displayed():
            driver.find_element(By.ID, "newMenu").click()
    except Exception:
        pass

    # (opcional) esperar overlay sumir
    try:
        WebDriverWait(driver, 5).until(EC.invisibility_of_element_located((By.ID, "divLoading")))
    except TimeoutException:
        pass

    # 1) entrar no submenu Produto/Serviço
    path = "/Cadastros/ProdutoServico"
    sel  = f"#menus a[href='{path}'], ul#novoMenu a[href='{path}']"
    link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, sel)))
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", link)
    try:
        link.click()
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();", link)

    # confirmar que a tela abriu (ajuste se necessário)
    wait.until(EC.any_of(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "form#formProduto, #formProduto")),
        EC.visibility_of_element_located((By.XPATH, "//h1[contains(.,'Produto')]"))
    ))

    # 2) listar módulos da subpasta ./CadastroProdutos
    subpasta = Path(__file__).parent / "CadastroProdutos"
    mods = sorted([p.stem for p in subpasta.glob("*.py")
                   if p.stem not in ("__init__",) and not p.stem.startswith("_")])

    # 3) abrir modal e escolher módulo
    nome = escolher_modulo_no_navegador(driver, mods, (mods[0] if mods else "ExtrairNomes"))
    if not nome:
        return  # cancelou

    # 4) importar e executar o módulo escolhido usando o mesmo driver
    if str(subpasta) not in sys.path:
        sys.path.insert(0, str(subpasta))

    mod = importlib.import_module(nome)   # ex.: "ExtrairNomes"
    if not hasattr(mod, "executar"):
        raise RuntimeError(f"O módulo {nome}.py precisa ter a função executar(driver).")
    mod.executar(driver)
