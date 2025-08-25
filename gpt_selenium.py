# gpt_selenium.py
"""
Launcher do Selenium sem credenciais hardcoded.
- Pede URL / usuário / senha ao usuário via modal no navegador (fallback para console).
- Faz login e seleção de domínio (primeira opção).
- Depois mostra um seletor de módulo (arquivo .py no mesmo diretório) e chama executar(driver).

Segurança:
- Não imprime senha.
- Suporta variáveis de ambiente: TOTVS_URL, TOTVS_USER, TOTVS_PASS (opcional).
"""

import importlib
import os
import sys
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# ---------------------------
# Util: listar módulos locais
# ---------------------------
def listar_modulos(pasta=None):
    base_dir = Path(pasta) if pasta else Path(__file__).parent
    mods = []
    for p in base_dir.glob("*.py"):
        name = p.stem
        if name not in ("gpt_selenium", "__init__") and not name.startswith("_"):
            mods.append(name)
    return sorted(mods)


# ---------------------------------------------------
# UI no navegador: pedir credenciais (URL/USER/PASS)
# ---------------------------------------------------
def pedir_credenciais_no_navegador(driver, default_url="", default_user=""):
    """
    Abre um overlay simples na página atual (about:blank serve) e pede:
    - URL
    - Usuário
    - Senha (type=password)

    Retorna (url, user, pwd) ou (None, None, None) se cancelar.
    """
    return driver.execute_async_script(
        """
    var cb   = arguments[arguments.length - 1];
    var dURL = arguments[0] || "";
    var dUSR = arguments[1] || "";

    // remove overlay antigo se existir
    var old = document.getElementById('gpt-cred-wrap'); if (old) old.remove();

    // cria overlay
    var wrap = document.createElement('div');
    wrap.id = 'gpt-cred-wrap';
    wrap.style = 'position:fixed;inset:0;background:rgba(0,0,0,.45);display:flex;align-items:center;justify-content:center;z-index:2147483647;font:14px system-ui,Segoe UI,Arial,sans-serif;';
    var box = document.createElement('div');
    box.style = 'background:#fff;padding:16px 16px 12px;border-radius:12px;min-width:360px;max-width:560px;box-shadow:0 10px 30px rgba(0,0,0,.3);';
    box.innerHTML =
      '<div style="font-size:16px;margin-bottom:10px">Preencha para entrar</div>' +
      '<div style="display:flex;flex-direction:column;gap:8px">' +
      '  <label>URL do sistema<br><input id="gpt-url" placeholder="https://seu-endereco..." style="width:100%;padding:8px;border:1px solid #ccc;border-radius:8px"></label>' +
      '  <label>Usuário<br><input id="gpt-user" placeholder="USUARIO" style="width:100%;padding:8px;border:1px solid #ccc;border-radius:8px"></label>' +
      '  <label>Senha<br><input id="gpt-pass" type="password" placeholder="••••••••" style="width:100%;padding:8px;border:1px solid #ccc;border-radius:8px"></label>' +
      '</div>' +
      '<div style="display:flex;gap:8px;justify-content:flex-end;margin-top:12px">' +
      '  <button id="gpt-cancel" style="padding:8px 12px;border:1px solid #bbb;border-radius:8px;background:#f5f5f5">Cancelar</button>' +
      '  <button id="gpt-ok" style="padding:8px 12px;border:1px solid #0a84ff;border-radius:8px;background:#0a84ff;color:#fff">Entrar</button>' +
      '</div>';
    wrap.appendChild(box);
    document.body.appendChild(wrap);

    var url  = box.querySelector('#gpt-url');
    var user = box.querySelector('#gpt-user');
    var pwd  = box.querySelector('#gpt-pass');

    if (dURL) url.value = dURL;
    if (dUSR) user.value = dUSR;

    function finish(vals){
      try { wrap.remove(); } catch(e){}
      cb(vals);
    }

    box.querySelector('#gpt-ok').onclick = function(){
      var u = (url.value||'').trim();
      var n = (user.value||'').trim();
      var p = (pwd.value||'').trim();
      if(!u || !n || !p){ alert('Preencha URL, usuário e senha.'); return; }
      finish([u, n, p]);
    };
    box.querySelector('#gpt-cancel').onclick = function(){ finish(null); };

    // enter envia, esc cancela
    [url, user, pwd].forEach(function(el){
      el.addEventListener('keydown', function(e){
        if(e.key==='Enter') { box.querySelector('#gpt-ok').click(); }
        if(e.key==='Escape') { box.querySelector('#gpt-cancel').click(); }
      });
    });

    """,
        default_url,
        default_user,
    )


def obter_credenciais(driver):
    """
    Busca credenciais desta forma (nessa ordem):
    1) Variáveis de ambiente TOTVS_URL, TOTVS_USER, TOTVS_PASS (se existirem)
    2) Janela modal no navegador (about:blank)
    3) Fallback console (input / getpass) se o modal for cancelado
    """
    # 1) ENV
    env_url = os.environ.get("TOTVS_URL", "").strip()
    env_usr = os.environ.get("TOTVS_USER", "").strip()
    env_pwd = os.environ.get("TOTVS_PASS", "").strip()
    if env_url and env_usr and env_pwd:
        return env_url, env_usr, env_pwd

    # 2) Modal no navegador
    try:
        driver.get("about:blank")
        creds = pedir_credenciais_no_navegador(driver, default_url="", default_user="")
        if creds and len(creds) == 3:
            return creds[0], creds[1], creds[2]
    except Exception:
        pass

    # 3) Fallback console
    try:
        import getpass

        url = input("URL do sistema: ").strip()
        usr = input("Usuário: ").strip()
        pwd = getpass.getpass("Senha: ").strip()
        if url and usr and pwd:
            return url, usr, pwd
    except KeyboardInterrupt:
        pass

    print("Credenciais não fornecidas. Encerrando.")
    sys.exit(1)


# -----------------------------------------------------------
# UI no navegador: escolher qual módulo (.py) você quer rodar
# -----------------------------------------------------------
def escolher_modulo_no_navegador(driver, mods, default_value=None):
    return driver.execute_async_script(
        """
      var cb = arguments[arguments.length - 1];
      var mods = arguments[0] || [];
      var def  = arguments[1] || '';

      var old = document.getElementById('gpt-modal-wrap'); if (old) old.remove();
      var wrap = document.createElement('div');
      wrap.id = 'gpt-modal-wrap';
      wrap.style = 'position:fixed;inset:0;background:rgba(0,0,0,.45);display:flex;align-items:center;justify-content:center;z-index:2147483647;';
      var box = document.createElement('div');
      box.style = 'background:#fff;padding:16px;border-radius:10px;min-width:320px;max-width:520px;box-shadow:0 10px 30px rgba(0,0,0,.3);font:14px system-ui,Segoe UI,Arial,sans-serif;';
      box.innerHTML = '<div style="margin-bottom:8px;font-size:16px">Escolha um módulo:</div>'
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
    """,
        mods,
        default_value,
    )


# -----------
# Main script
# -----------
def main():
    # Chrome options
    opts = Options()
    opts.add_experimental_option("detach", True)  # mantém o Chrome aberto após o script encerrar
    driver = webdriver.Chrome(options=opts)

    # 1) Pega credenciais de forma segura
    URL, USER, PASS = obter_credenciais(driver)

    # 2) Navega e faz login
    driver.get(URL)
    driver.maximize_window()
    wait = WebDriverWait(driver, 20)

    # --- LOGIN ---
    user = wait.until(EC.visibility_of_element_located((By.ID, "UserName")))
    pwd = driver.find_element(By.ID, "Senha")
    btn = driver.find_element(By.ID, "btnLogin")

    user.clear()
    user.send_keys(USER)
    pwd.send_keys(PASS)
    btn.click()

    # --- ESPERA A TELA DE DOMÍNIO (divDomain) APARECER ---
    wait.until(EC.visibility_of_element_located((By.ID, "divDomain")))

    # O Chosen cria um container #comboBoxDomain_chosen (o select original fica oculto)
    chosen_box = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#comboBoxDomain_chosen")))
    chosen_box.click()

    # Abre a lista e clica na primeira opção disponível
    primeira_opcao = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#comboBoxDomain_chosen .chosen-results li.active-result"))
    )
    primeira_opcao.click()

    # Clica em "Entrar"
    wait.until(EC.element_to_be_clickable((By.ID, "btnEntrar"))).click()

    # Espera sinais confiáveis de pós-login
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#navbar .current-domain")))
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "ul#novoMenu")))

    # 3) Selecionar e executar módulo
    mods = listar_modulos()
    nome_modulo = escolher_modulo_no_navegador(driver, mods, (mods[0] if mods else ""))

    if not nome_modulo:
        print("Execução cancelada pelo usuário.")
        return

    nome_modulo = nome_modulo.strip()
    try:
        modulo = importlib.import_module(nome_modulo)  # ex.: ExtrairAliquota.py -> "ExtrairAliquota"
        if hasattr(modulo, "executar"):
            modulo.executar(driver)  # usa o mesmo driver logado
        else:
            print(f"O arquivo {nome_modulo}.py precisa ter a função executar(driver).")
    except ModuleNotFoundError:
        print(f"Não achei {nome_modulo}.py no mesmo diretório do gpt_selenium.py.")
    except Exception as e:
        print(f"Erro ao executar o módulo {nome_modulo}: {e}")


if __name__ == "__main__":
    main()
