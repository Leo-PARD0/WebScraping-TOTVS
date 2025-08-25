import importlib
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# =========================
# util: listar módulos .py
# =========================
def listar_modulos(pasta=None):
    base_dir = Path(pasta) if pasta else Path(__file__).parent
    mods = []
    for p in base_dir.glob("*.py"):
        name = p.stem
        if name not in ("gpt_selenium", "__init__") and not name.startswith("_"):
            mods.append(name)
    return sorted(mods)

# =========================
# .base (carregar/salvar)
# =========================
BASE_FILE = Path(__file__).parent / ".base"

def _parse_base_text(text: str):
    creds = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            creds[k.strip().upper()] = v.strip().strip('"').strip("'")
    return creds

def carregar_base():
    if not BASE_FILE.exists():
        return None
    try:
        creds = _parse_base_text(BASE_FILE.read_text(encoding="utf-8"))
        url  = creds.get("URL") or ""
        user = creds.get("USER") or ""
        pw   = creds.get("PASS") or ""
        if url and user and pw:
            return {"URL": url, "USER": user, "PASS": pw}
    except Exception:
        pass
    return None

def salvar_base(url, user, pw):
    try:
        BASE_FILE.write_text(
            f"URL={url}\nUSER={user}\nPASS={pw}\n",
            encoding="utf-8"
        )
        return True
    except Exception:
        return False

# =========================================
# diálogos no navegador (inputs e seleção)
# =========================================
def pedir_credenciais_no_navegador(driver, defaults=None):
    """Abre uma página em branco e exibe um modal com inputs de URL/USER/PASS.
       Retorna (url, user, pass, salvar_em_base: bool) ou (None, None, None, False) se cancelar."""
    if defaults is None:
        defaults = {"URL": "", "USER": "", "PASS": ""}

    driver.get("data:text/html;charset=utf-8,<title>Setup</title><body></body>")
    return driver.execute_async_script("""
      var cb = arguments[arguments.length - 1];
      var defs = arguments[0] || {};

      var wrap = document.createElement('div');
      wrap.style = 'position:fixed;inset:0;background:rgba(0,0,0,.45);display:flex;align-items:center;justify-content:center;z-index:2147483647;font:14px system-ui,Segoe UI,Arial,sans-serif;';
      var box = document.createElement('div');
      box.style = 'background:#fff;padding:16px;border-radius:12px;min-width:360px;max-width:560px;box-shadow:0 10px 30px rgba(0,0,0,.3)';

      box.innerHTML =
        '<div style="font-size:16px;margin-bottom:8px">Credenciais do sistema</div>'
      + '<label style="display:block;margin:8px 0 4px">URL</label>'
      + '<input id="in-url" placeholder="https://..." style="width:100%;padding:8px;border:1px solid #ccc;border-radius:8px">'
      + '<label style="display:block;margin:12px 0 4px">Usuário</label>'
      + '<input id="in-user" placeholder="seu usuário" style="width:100%;padding:8px;border:1px solid #ccc;border-radius:8px">'
      + '<label style="display:block;margin:12px 0 4px">Senha</label>'
      + '<input id="in-pass" type="password" placeholder="sua senha" style="width:100%;padding:8px;border:1px solid #ccc;border-radius:8px">'
      + '<label style="display:flex;gap:8px;align-items:center;margin:12px 0 8px;user-select:none;cursor:pointer">'
      + '  <input id="in-save" type="checkbox"> <span>Salvar em .base (no disco)</span>'
      + '</label>'
      + '<div style="display:flex;gap:8px;justify-content:flex-end;margin-top:8px">'
      + '  <button id="btn-ok" style="padding:8px 12px;border:1px solid #0a84ff;border-radius:8px;background:#0a84ff;color:#fff">OK</button>'
      + '  <button id="btn-cancel" style="padding:8px 12px;border:1px solid #bbb;border-radius:8px;background:#f5f5f5">Cancelar</button>'
      + '</div>';

      wrap.appendChild(box);
      document.body.appendChild(wrap);

      var inUrl  = box.querySelector('#in-url');
      var inUser = box.querySelector('#in-user');
      var inPass = box.querySelector('#in-pass');
      var inSave = box.querySelector('#in-save');

      inUrl.value  = (defs.URL  || '');
      inUser.value = (defs.USER || '');
      inPass.value = (defs.PASS || '');

      function finish(res){
        try { wrap.remove(); } catch(e){}
        cb(res);
      }

      box.querySelector('#btn-ok').onclick = function(){
        var url  = inUrl.value.trim();
        var usr  = inUser.value.trim();
        var pw   = inPass.value;
        var sav  = !!inSave.checked;
        if(!url || !usr || !pw){ alert('Preencha URL, usuário e senha.'); return; }
        finish([url, usr, pw, sav]);
      };
      box.querySelector('#btn-cancel').onclick = function(){ finish([null, null, null, false]); };

      inPass.addEventListener('keydown', function(e){
        if(e.key === 'Enter'){ box.querySelector('#btn-ok').click(); }
      });
    """, defaults)

def escolher_modulo_no_navegador(driver, mods, default_value=None):
    return driver.execute_async_script("""
      var cb = arguments[arguments.length - 1];
      var mods = arguments[0] || [];
      var def  = arguments[1] || '';
      var wrap = document.createElement('div');
      wrap.style = 'position:fixed;inset:0;background:rgba(0,0,0,.45);display:flex;align-items:center;justify-content:center;z-index:2147483647;font:14px system-ui,Segoe UI,Arial,sans-serif;';
      var box = document.createElement('div');
      box.style = 'background:#fff;padding:16px;border-radius:12px;min-width:360px;max-width:560px;box-shadow:0 10px 30px rgba(0,0,0,.3)';
      box.innerHTML =
        '<div style="font-size:16px;margin-bottom:8px">Escolha um módulo</div>'
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

# =========================
# Chrome & fluxo principal
# =========================
def main():
    # Chrome
    opts = Options()
    opts.add_experimental_option("detach", True)  # deixa o Chrome aberto ao terminar
    driver = webdriver.Chrome(options=opts)
    wait = WebDriverWait(driver, 20)

    # 1) Carregar .base ou pedir credenciais
    creds = carregar_base()
    if creds:
        URL = creds["URL"]; USER = creds["USER"]; PASS = creds["PASS"]
    else:
        url, user, pw, salvar = pedir_credenciais_no_navegador(driver)
        if not url:
            print("Execução cancelada pelo usuário (credenciais).")
            return
        URL, USER, PASS = url, user, pw
        if salvar:
            ok = salvar_base(URL, USER, PASS)
            print(".base salvo." if ok else "Falha ao salvar .base (sem impactar a execução).")

    # 2) Navegar e logar
    driver.get(URL)
    driver.maximize_window()

    user_el = wait.until(EC.visibility_of_element_located((By.ID, "UserName")))
    pwd_el  = driver.find_element(By.ID, "Senha")
    btn_el  = driver.find_element(By.ID, "btnLogin")

    user_el.clear(); user_el.send_keys(USER)
    pwd_el.send_keys(PASS)
    btn_el.click()

    # 3) Pós-login: domínio e entrar
    wait.until(EC.visibility_of_element_located((By.ID, "divDomain")))
    chosen_box = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#comboBoxDomain_chosen")))
    chosen_box.click()
    primeira_opcao = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#comboBoxDomain_chosen .chosen-results li.active-result")))
    primeira_opcao.click()
    wait.until(EC.element_to_be_clickable((By.ID, "btnEntrar"))).click()

    # 4) Esperar home
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#navbar .current-domain")))
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "ul#novoMenu")))

    # 5) Escolher módulo
    mods = listar_modulos()
    nome_modulo = escolher_modulo_no_navegador(driver, mods, (mods[0] if mods else ""))

    if not nome_modulo:
        print("Execução cancelada pelo usuário (módulo).")
        return

    # 6) Importar e rodar módulo escolhido (precisa de executar(driver))
    nome_modulo = nome_modulo.strip()
    try:
        modulo = importlib.import_module(nome_modulo)
        if hasattr(modulo, "executar"):
            modulo.executar(driver)
        else:
            print(f"O arquivo {nome_modulo}.py precisa ter a função executar(driver).")
    except ModuleNotFoundError:
        print(f"Não achei {nome_modulo}.py no mesmo diretório do gpt_selenium.py.")

if __name__ == "__main__":
    main()
