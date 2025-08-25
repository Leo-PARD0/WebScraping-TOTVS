# CadastroProdutos/ExtrairAliquota.py
# importar dependencias
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pathlib import Path
import csv
import time

MAX_PAGES = 140  # limite de páginas a varrer

# ==============================
# helpers de overlay / waitpanel
# ==============================
def _overlay_visivel(driver):
    """True se o underlay/overlay do Dojo (WaitPanel) estiver ativo bloqueando cliques."""
    try:
        return driver.execute_script("""
            function vis(el){
              if(!el) return false;
              var s = getComputedStyle(el);
              if (s.display === 'none' || s.visibility === 'hidden') return false;
              return !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
            }
            // wrapper do underlay
            var wrap = document.querySelector('[id^="dijit_DialogUnderlay_"]') ||
                       document.getElementById('dijit_DialogUnderlay_0');
            // underlay interno
            var ul = document.getElementById('WaitPanelDialog_underlay') ||
                     (wrap ? wrap.querySelector('.dijitDialogUnderlay, ._underlay') : null);
            // diálogo (redundância)
            var dlg = document.getElementById('WaitPanelDialog');

            // estado dojo, se exposto
            var dojoOpen = false;
            try {
              if (window.dijit && dijit.byId) {
                var w = dijit.byId('WaitPanelDialog');
                if (w && typeof w.get === 'function') dojoOpen = !!w.get('open');
              }
            } catch(e){}

            return dojoOpen || vis(wrap) || vis(ul) || vis(dlg);
        """)
    except Exception:
        return False

def waitingpanel(driver, timeout=250, tag=""):
    """Espera até timeout o underlay desaparecer. Continua mesmo que estoure."""
    print(f"DEBUG: aguardando WAITPANEL {tag} sumir (até {timeout}s)…")
    fim = time.time() + timeout
    ultimo = None
    while time.time() < fim:
        ativo = _overlay_visivel(driver)
        if ativo != ultimo:
            print(f"DEBUG: WAITPANEL {tag} -> {'ATIVO' if ativo else 'OCULTO'}")
            ultimo = ativo
        if not ativo:
            return True
        time.sleep(0.10)
    print(f"DEBUG: WAITPANEL {tag} ainda ativo ao fim; seguindo assim mesmo…")
    return False

# ======================
# resultado / edição UI
# ======================
def esperar_resultado_visivel(driver, timeout=20):
    """Garante que a aba de RESULTADO está visível (edição fechada)."""
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script(
            "var e=document.getElementById('tabPanelEdition'), r=document.getElementById('tabPanelResult');"
            "return e && getComputedStyle(e).display=='none' && r && getComputedStyle(r).display!='none';"
        )
    )

def esperar_edicao_visivel(driver, timeout=20):
    """Garante que a aba de EDIÇÃO está visível (edit form aberto)."""
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script(
            "var e=document.getElementById('tabPanelEdition');"
            "return e && getComputedStyle(e).display!='none';"
        )
    )
    WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.ID, "tabPanelEditionContainer")))

# ===================================
# continuar driver / garantir a tela
# ===================================
def continua_drive(driver, timeout=20):
    """continua com o navegador já logado/aberto, garantindo a aba de resultados."""
    WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((By.ID, "tabPanelResultContainer"))
    )
    # pelo menos 1 linha carregada
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("""
            var rc = document.getElementById('tabPanelResultContainer');
            if (!rc) return false;
            var tbl = rc.querySelector('.dxgvTable,[id^="dataGrid_DXMainTable"]');
            if (!tbl) return false;
            var rows = tbl.querySelectorAll('tr[id^="dataGrid_DXDataRow"], tr.dxgvDataRow');
            return rows.length >= 1;
        """)
    )

# ============================
# modal (Sim/Não) robusto
# ============================
def clicar_botao_modal(driver, *rotulos):
    """
    Clica em um botão/ancora com texto entre 'rotulos' dentro da ÚLTIMA modal visível.
    Ex.: clicar_botao_modal(driver, 'Sim', 'Yes', 'OK', 'Confirmar')
    """
    roots = [
        "//div[contains(@class,'bootbox') and contains(@class,'modal') and (contains(@class,'in') or contains(@style,'display: block'))][last()]",
        "//div[contains(@class,'modal') and (contains(@class,'in') or contains(@style,'display: block'))][last()]",
        "//body"
    ]
    for root in roots:
        for rot in rotulos:
            xp = (
                f"{root}//*[self::button or self::a]"
                f"[normalize-space()='{rot}' or "
                f" contains(translate(.,"
                f"'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÀÂÃÉÊÍÓÔÕÚÇ',"
                f"'abcdefghijklmnopqrstuvwxyzáàâãéêíóôõúç'),"
                f" '{rot.lower()}')]"
            )
            try:
                WebDriverWait(driver, 6).until(EC.element_to_be_clickable((By.XPATH, xp))).click()
                return True
            except Exception:
                pass
    return False

# ============================
# resolutores / click helpers
# ============================
def nisclickable(driver, n, g=None, timeout=12):
    """verifica se 'n' está clicável (True/False)."""
    try:
        if n.lower() in ("linha", "linha da grid"):
            driver.execute_script(
                "try{ if(window.dataGrid){ dataGrid.SetFocusedRowIndex(arguments[0]); } }catch(e){}",
                int(g)
            )
            return True
        if n.lower() in ("editar", "btn editar"):
            return True
        by, sel = _resolver_locator(n)
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, sel)))
        return True
    except Exception:
        return False

def _resolver_locator(n):
    n_low = (n or "").strip().lower()
    if n_low in ("editar", "btn editar"):
        return (By.CSS_SELECTOR, "#toolBarResult #toolBarEditItem, #toolBarEditItem")
    if n_low in ("dados fiscais", "dadosfiscais", "aba dados fiscais"):
        return (By.CSS_SELECTOR, "a[href='#dadosFiscais'], [data-target='#dadosFiscais']")
    if n_low in ("cancelar", "btn cancelar"):
        return (By.ID, "toolBarCancelItem")
    raise ValueError(f"Alvo '{n}' não mapeado para locator direto.")

def clicar(driver, n, g=None, timeout=15):
    """
    Clica/aciona o alvo 'n'.
    - 'linha': foca via API (evita stale). Opcionalmente tenta clicar o <tr>.
    - 'editar': foca g e dispara runInSession('editItem()').
    - demais: usa locator + clique normal/JS.
    """
    n_low = (n or "").strip().lower()
    waitingpanel(driver, timeout=min(12, timeout), tag=f"antes-de-clicar-{n}")

    if n_low in ("linha", "linha da grid"):
        try:
            driver.execute_script(
                "try{ if(window.dataGrid){"
                " dataGrid.SetFocusedRowIndex(arguments[0]);"
                " if(dataGrid.SelectRow) dataGrid.SelectRow(arguments[0]);"
                "}}catch(e){}",
                int(g)
            )
        except Exception:
            pass
        try:
            row = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.ID, f"dataGrid_DXDataRow{int(g)}"))
            )
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", row)
            try:
                row.find_element(By.XPATH, "./td[1]").click()
            except Exception:
                try:
                    row.click()
                except Exception:
                    pass
        except Exception:
            pass
        return

    if n_low in ("editar", "btn editar"):
        try:
            if g is not None:
                driver.execute_script(
                    "try{ if(window.dataGrid){ dataGrid.SetFocusedRowIndex(arguments[0]); } }catch(e){}",
                    int(g)
                )
            driver.execute_script("try { runInSession('editItem()'); } catch(e) {}")
            return
        except Exception:
            pass

    by, sel = _resolver_locator(n_low)
    elem = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, sel)))
    try:
        try:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", elem)
        except Exception:
            pass
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((by, sel))).click()
    except Exception:
        try:
            driver.execute_script("arguments[0].click();", elem)
        except Exception:
            try:
                elem.send_keys("\n")
            except Exception:
                pass

# ============================
# Lê "Não exibir no cardápio"
# ============================
def ler_nao_exibir_no_cardapio(driver):
    """
    Retorna 'sim' ou 'não' conforme o checkbox/dojo 'NaoExibirNoCardapio'.
    Tenta várias formas: widget Dojo, input.checked, aria-checked, classe do contêiner, atributo 'checked'.
    """
    try:
        return driver.execute_script("""
            // tenta input por id/name
            var input = document.getElementById('NaoExibirNoCardapio') ||
                        document.querySelector("input[name='NaoExibirNoCardapio']");
            var cont = input ? (input.closest('.dijitCheckBox') || input.parentElement) : null;

            // 1) Dojo (dijit)
            try {
                if (window.dijit && dijit.byId) {
                    var w = dijit.byId('NaoExibirNoCardapio');
                    if (w && typeof w.get === 'function') {
                        return w.get('checked') ? 'sim' : 'não';
                    }
                }
            } catch(e) {}

            // 2) Propriedade checked do input
            if (input && typeof input.checked !== 'undefined')
                return input.checked ? 'sim' : 'não';

            // 3) Atributo aria-checked
            if (input) {
                var ac = (input.getAttribute('aria-checked') || '').toLowerCase();
                if (ac === 'true')  return 'sim';
                if (ac === 'false') return 'não';
            }

            // 4) Classe do container Dojo
            if (cont && /\bdijitCheckBoxChecked\b/.test(cont.className))
                return 'sim';

            // 5) Atributo "checked" puro
            if (input && input.getAttribute('checked') !== null)
                return 'sim';

            return 'não';
        """)
    except Exception:
        return 'não'

# ============================
# Classe extrairProduto (dados)
# ============================
class ExtrairProduto:
    """conjunto de funções para extrair os dados do produto."""
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)

    def codigois(self):
        try:
            el = self.wait.until(EC.visibility_of_element_located((By.ID, "CodigoProduto")))
        except TimeoutException:
            try:
                el = self.driver.find_element(By.NAME, "CodigoProduto")
            except Exception:
                el = None
        return ((el.get_attribute("value") if el else "") or (el.text if el else "") or "").strip()

    def nameis(self):
        el = self.wait.until(EC.visibility_of_element_located((By.ID, "NomeProduto")))
        return (el.get_attribute("value") or el.text or "").strip()

    def aliquotais(self):
        # garante que está na aba Dados Fiscais
        if nisclickable(self.driver, "Dados Fiscais", timeout=5):
            clicar(self.driver, "Dados Fiscais", timeout=10)
            waitingpanel(self.driver, timeout=6, tag="dados-fiscais")

        inp = None
        try:
            base = self.driver.find_element(By.ID, "AliquotaIcmsEfetivo")
            inp = base if base.tag_name.lower() == "input" else None
            if not inp:
                try:
                    inp = base.find_element(By.CSS_SELECTOR, "input, .dxeEditArea, input[id^='AliquotaIcmsEfetivo']")
                except Exception:
                    pass
        except Exception:
            pass
        if not inp:
            try:
                inp = self.driver.find_element(By.CSS_SELECTOR, "input#AliquotaIcmsEfetivo, input[id^='AliquotaIcmsEfetivo'], input[name*='AliquotaIcmsEfetivo']")
            except Exception:
                inp = None
        val = (inp.get_attribute("value") if inp else "") or (inp.text if inp else "") or ""
        return val.strip()

    def extrair_produto(self):
        """Extrai campos e retorna à lista. Confirma 'Sim' no modal de cancelamento."""
        codigo = self.codigois()
        nome   = self.nameis()
        aliquo = self.aliquotais()
        nao_exibir = ler_nao_exibir_no_cardapio(self.driver)

        # Cancelar + confirmar 'Sim' no modal (quando existir)
        try:
            if nisclickable(self.driver, "cancelar", timeout=6):
                clicar(self.driver, "cancelar", timeout=6)
                clicar_botao_modal(self.driver, "Sim", "Yes", "OK", "Confirmar")
        except Exception:
            pass

        # Espera voltar à lista
        try:
            esperar_resultado_visivel(self.driver, timeout=20)
        except Exception:
            waitingpanel(self.driver, timeout=12, tag="pos-cancelar")

        return codigo, nome, aliquo, nao_exibir

# ===================
# Paginacao (NextPage)
# ===================
def nextPage(driver, p_atual, timeout=30):
    """Vai para a próxima página do grid. Retorna (ok, p_novo)."""
    ok = driver.execute_script("""
        try {
            var root = document.querySelector('#tabPanelResultContainer') || document;
            var pager = root.querySelector('[id*="_DXPagerBottom"], .dxgvPagerBottom, .dxpLite') || root;
            var curEl = pager.querySelector('.dxp-current');
            var cur = curEl ? parseInt(curEl.textContent.trim(), 10) : NaN;
            if (!isNaN(cur)) {
                var targetText = String(cur + 1);
                var links = pager.querySelectorAll('a.dxp-num');
                for (var i = 0; i < links.length; i++) {
                    if (links[i].textContent.trim() === targetText) {
                        links[i].click();
                        return true;
                    }
                }
                if (window.ASPx && ASPx.GVPagerOnClick) {
                    ASPx.GVPagerOnClick('dataGrid', 'PN' + (cur)); // cur=1 => PN1 (vai pra 2)
                    return true;
                }
            }
        } catch(e) {}
        return false;
    """)
    if not ok:
        return False, p_atual

    waitingpanel(driver, timeout=timeout, tag="paginacao")
    # garantir alguma linha
    WebDriverWait(driver, 20).until(
        lambda d: d.execute_script("""
            var rc = document.getElementById('tabPanelResultContainer');
            if (!rc) return false;
            var tbl = rc.querySelector('.dxgvTable,[id^="dataGrid_DXMainTable"]');
            if (!tbl) return false;
            var rows = tbl.querySelectorAll('tr[id^="dataGrid_DXDataRow"], tr.dxgvDataRow');
            return rows.length >= 1;
        """)
    )
    return True, p_atual + 1

# ==========================================
# Escolha do nome do arquivo (prompt HTML)
# ==========================================
def escolher_caminho_saida(driver, caminho_padrao: Path):
    """
    Se o arquivo padrão já existir, abre uma aba com opções:
    - Substituir
    - Salvar como… (com input do nome)
    - Cancelar

    Retorna:
      (Path selecionado, overwrite_bool)
      ou (None, False) se cancelado.
    """
    if not caminho_padrao.exists():
        return caminho_padrao, False  # não existe: segue direto

    from urllib.parse import quote, unquote

    html = f"""<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<title>Escolha</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body {{ margin:0; font:14px system-ui,Segoe UI,Arial,sans-serif; }}
.wrap {{ min-height:100vh; display:flex; align-items:center; justify-content:center; background:#f6f7f9; }}
.box  {{ background:#fff; padding:18px; border-radius:12px; width:min(520px, calc(100vw - 32px));
        box-shadow:0 10px 30px rgba(0,0,0,.18); }}
h1    {{ font-size:16px; margin:0 0 8px; }}
.file {{ color:#555; word-break:break-all; margin-bottom:12px; }}
.row  {{ display:flex; gap:8px; flex-wrap:wrap; align-items:center; }}
button{{ padding:9px 14px; border-radius:10px; border:1px solid #bbb; background:#f2f2f2; cursor:pointer; }}
.pri  {{ background:#0a84ff; border-color:#0a84ff; color:#fff; }}
.ok   {{ background:#0a84ff; border-color:#0a84ff; color:#fff; }}
input {{ flex:1; padding:9px 10px; border:1px solid #ccc; border-radius:10px; min-width:180px; }}
.rename{{ display:none; margin-top:10px; }}
.muted{{ color:#777; font-size:12px; margin-top:6px; }}
</style>
</head>
<body>
<div class="wrap">
  <div class="box">
    <h1>O arquivo já existe</h1>
    <div class="file">Arquivo: <b>{caminho_padrao.name}</b></div>
    <div class="row">
      <button id="btn-over" class="pri">Substituir</button>
      <button id="btn-rename">Salvar como…</button>
      <button id="btn-cancel">Cancelar</button>
    </div>
    <div id="rename-row" class="rename">
      <div class="row" style="margin-top:8px;">
        <input id="name" placeholder="novo_arquivo.csv" />
        <button id="btn-ok" class="ok" disabled>OK</button>
      </div>
      <div class="muted">Caracteres inválidos serão substituídos por “_”.</div>
    </div>
  </div>
</div>
<script>
function finish(s){{ document.title = s; }}
const over   = document.getElementById('btn-over');
const cancel = document.getElementById('btn-cancel');
const rename = document.getElementById('btn-rename');
const row    = document.getElementById('rename-row');
const nameEl = document.getElementById('name');
const ok     = document.getElementById('btn-ok');
over.onclick   = () => finish('RES:OVERWRITE');
cancel.onclick = () => finish('RES:CANCEL');
rename.onclick = () => {{ row.style.display='block'; nameEl.focus(); }};
nameEl.addEventListener('input', () => {{
  const v = nameEl.value.trim();
  ok.disabled = !v;
}});
ok.onclick = () => {{
  let v = (nameEl.value||'').trim();
  if (!v) return;
  v = v.replace(/[\\\\/:*?"<>|]/g, '_');
  if (!/\\.csv$/i.test(v)) v += '.csv';
  finish('RES:RENAME:' + encodeURIComponent(v));
}};
</script>
</body>
</html>"""

    original = driver.current_window_handle
    driver.switch_to.new_window('tab')
    driver.get("data:text/html;charset=utf-8," + quote(html))
    WebDriverWait(driver, 600).until(lambda d: d.title.startswith("RES:"))
    res = driver.title
    driver.close()
    driver.switch_to.window(original)

    if res == "RES:CANCEL":
        return None, False
    elif res == "RES:OVERWRITE":
        return caminho_padrao, True
    elif res.startswith("RES:RENAME:"):
        from urllib.parse import unquote
        novo_nome = unquote(res[len("RES:RENAME:"):]).strip()
        # sanitiza e garante extensão
        novo_nome = "".join("_" if c in "\\/:*?\"<>|" else c for c in novo_nome)
        if not novo_nome.lower().endswith(".csv"):
            novo_nome += ".csv"
        return caminho_padrao.with_name(novo_nome), False
    else:
        return caminho_padrao, False

# ======================
# CSV helpers (salvar)
# ======================
def salvar_csv(caminho: Path, registros, escrever_cabecalho: bool, overwrite: bool):
    """
    Escreve codigo|nome|aliquota|nao_exibir_no_cardapio em 'caminho'.
    - Se overwrite=True, apaga o arquivo antes.
    - Se escrever_cabecalho=True, escreve o header.
    """
    if overwrite and caminho.exists():
        try:
            caminho.unlink()
        except Exception:
            pass

    mode = "a"
    if overwrite or not caminho.exists():
        mode = "w"

    with caminho.open(mode, newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter="|")
        if escrever_cabecalho or mode == "w":
            w.writerow(["codigo", "nome", "aliquota", "nao_exibir_no_cardapio"])
        for (codigo, nome, aliq, nao_exibir) in registros:
            w.writerow([codigo, nome, aliq, nao_exibir])

def salvar_csv_com_prompt(driver, caminho_padrao: Path, registros):
    """
    Se o arquivo padrão não existir: salva direto com header.
    Se existir: pergunta se substitui, renomeia ou cancela.
    Retorna o Path salvo ou None se cancelado.
    """
    overwrite = False
    destino = caminho_padrao
    escrever_cabecalho = not destino.exists()

    if destino.exists():
        sel, over = escolher_caminho_saida(driver, destino)
        if sel is None:
            print("Operação cancelada pelo usuário. CSV não salvo.")
            return None
        destino = sel
        overwrite = over
        escrever_cabecalho = overwrite or (not destino.exists())

    salvar_csv(destino, registros, escrever_cabecalho, overwrite)
    print(f"OK! Salvei {len(registros)} linhas em: {destino.resolve()}")
    return destino

# ======================
# Execução principal
# ======================
def executar(driver):
    saida_default = Path(__file__).parent / "aliquotas.csv"
    registros = []

    try:
        # 1) garantir tela pronta
        continua_drive(driver)
        waitingpanel(driver, 4, "ini")

        # inferir índice global inicial e página
        base = driver.execute_script(r"""
            var rc  = document.getElementById('tabPanelResultContainer');
            if (!rc) return 0;
            var rows = rc.querySelectorAll('tr[id^="dataGrid_DXDataRow"]');
            var minIdx = null;
            for (var i = 0; i < rows.length; i++) {
                var id = rows[i].id || "";
                var m  = id.match(/DXDataRow(\d+)$/);
                if (m) {
                    var v = parseInt(m[1], 10);
                    if (minIdx === null || v < minIdx) minIdx = v;
                }
            }
            return (minIdx === null ? 0 : minIdx);
        """) or 0

        g = int(base)         # índice GLOBAL atual
        p = (g // 10) + 1     # página atual (1-based)

        # percorre até MAX_PAGES (ou até o pager acabar)
        while p <= MAX_PAGES:
            c = g - 10 * (p - 1) + 1  # 1..10 dentro da página
            print(f"\n===== P{p} ITEM {c-1} / 9 (g={g}) =====")

            # focar linha & abrir edição
            if not nisclickable(driver, "linha", g=g, timeout=12):
                print(f"DEBUG: não consegui focar a linha g={g}, tentando assim mesmo…")
            clicar(driver, "linha", g=g, timeout=12)
            clicar(driver, "editar", g=g, timeout=12)

            # garantir que a EDIÇÃO abriu mesmo (retry leve)
            try:
                esperar_edicao_visivel(driver, timeout=20)
            except TimeoutException:
                driver.execute_script("try { runInSession('editItem()'); } catch(e) {}")
                waitingpanel(driver, timeout=8, tag="retry-editar")
                esperar_edicao_visivel(driver, timeout=15)

            # extrair + cancelar + confirmar 'Sim'
            prod = ExtrairProduto(driver)
            codigo, nome, aliquota, nao_exibir = prod.extrair_produto()
            registros.append((codigo, nome, aliquota, nao_exibir))

            # garantir overlay sumido
            waitingpanel(driver, timeout=10, tag="pos-extrair")

            # virar de página quando completar 10 itens
            if c == 10:
                ok, p = nextPage(driver, p_atual=p)
                if not ok:
                    print("DEBUG: Não há próxima página; encerrando.")
                    break
                g = g + 1  # IDs são globais: 9->10, 19->20, ...
                time.sleep(0.2)
            else:
                g += 1

        # salvamento normal (com prompt se existir)
        salvar_csv_com_prompt(driver, saida_default, registros)

    except Exception as e:
        # >>> SE DER ERRO, SALVA O QUE JÁ TEMOS (com prompt) <<<
        try:
            if registros:
                salvar_csv_com_prompt(driver, saida_default, registros)
            else:
                print("\nATENÇÃO: Erro antes de coletar qualquer linha; nada foi salvo.")
        except Exception as e2:
            print(f"\nERRO ao salvar CSV parcial: {e2}")
        print(f"\nMotivo do erro: {type(e).__name__}: {e}")
        raise

    input("Pressione Enter para fechar...")
