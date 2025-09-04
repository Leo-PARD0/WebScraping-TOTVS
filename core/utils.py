"""Funções utilitárias do WebScraping-TOTVS."""

from __future__ import annotations

import csv
import json
import importlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

import yaml
from selenium.webdriver.support.ui import WebDriverWait

log = logging.getLogger("utils")

# Diretórios-base do projeto
BASE_DIR = Path(__file__).resolve().parents[1]
MOD_DIR = BASE_DIR / "modulos"
ARTIFACTS = BASE_DIR / "artifacts"
LOCATORS_FILE = BASE_DIR / "core" / "locators.yaml"

# Garante a pasta artifacts/
ARTIFACTS.mkdir(exist_ok=True, parents=True)


# ============================
# Captura de evidências
# ============================
def screenshot(driver, name_prefix: str) -> Path:
    """
    Salva screenshot da tela atual em artifacts/ com timestamp.
    Retorna o Path do arquivo salvo.
    """
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = ARTIFACTS / f"{name_prefix}_{ts}.png"
    driver.save_screenshot(str(path))
    log.info("Screenshot salvo em %s", path)
    return path


# ============================
# Leitura de seletores (YAML)
# ============================
def load_locators(section: str) -> dict:
    """
    Carrega os seletores de uma seção do locators.yaml.
    Ex.: load_locators("login") -> dict com chaves/seletores da seção.
    """
    try:
        with open(LOCATORS_FILE, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data.get(section, {})
    except FileNotFoundError:
        log.error("Arquivo locators.yaml não encontrado em %s", LOCATORS_FILE)
        return {}
    except Exception as e:
        log.error("Erro ao carregar locators.yaml: %s", e)
        return {}


# ============================
# Descoberta/Seleção de módulos
# ============================

log = logging.getLogger("utils")
BASE_DIR = Path(__file__).resolve().parents[1]
MOD_DIR = BASE_DIR / "modulos"

def _importar_executar(mod_qualname: str) -> Optional[Callable]:
    """
    Tenta importar `mod_qualname` e retornar a função pública `executar`.
    Ex.: "modulos.cadastro_produtos" ou "modulos.teste"
    """
    try:
        mod = importlib.import_module(mod_qualname)
        func = getattr(mod, "executar", None)
        return func if callable(func) else None
    except Exception as e:
        log.warning("Falha importando %s: %s", mod_qualname, e)
        return None

def listar_modulos() -> list[tuple[str, Callable]]:
    """
    Lista módulos de alto nível em `modulos/`, aceitando:
      - arquivos .py que exponham executar()
      - pacotes (pastas com __init__.py) que reexportem executar()
    Retorna lista: [(nome_curto, func_executar), ...]
    """
    mods: list[tuple[str, Callable]] = []

    # 1) Arquivos .py
    for p in sorted(MOD_DIR.glob("*.py")):
        if p.name.startswith("_"):
            continue
        qual = f"modulos.{p.stem}"
        func = _importar_executar(qual)
        if func:
            mods.append((p.stem, func))

    # 2) Pacotes (pastas com __init__.py)
    for d in sorted([x for x in MOD_DIR.iterdir() if x.is_dir()]):
        if (d / "__init__.py").exists():
            qual = f"modulos.{d.name}"
            func = _importar_executar(qual)
            if func:
                mods.append((d.name, func))

    return mods

def escolher_modulo(mods: list[tuple[str, Callable]]):
    """
    Se houver só 1 módulo, seleciona automaticamente (sem prompt).
    Caso contrário, mostra um menu no console.
    """
    if not mods:
        log.error("Nenhum módulo válido encontrado em %s", MOD_DIR)
        return None

    if len(mods) == 1:
        name, func = mods[0]
        log.info("Selecionando módulo único automaticamente: %s", name)
        return mods[0]

    print("\nMódulos disponíveis:")
    for i, (name, _) in enumerate(mods, 1):
        print(f" {i}. {name}")

    while True:
        sel = input("Escolha um módulo (número): ").strip()
        if sel.isdigit() and 1 <= int(sel) <= len(mods):
            return mods[int(sel) - 1]
        print("Opção inválida.")


# ============================
# Exportação de dados
# ============================
def _ensure_output_dir() -> Path:
    """
    Garante e retorna a pasta artifacts/output.
    """
    output_dir = ARTIFACTS / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

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


def salvar_json(nome: str, dados: list[dict], indent: int = 2) -> Path:
    """
    Salva lista de dicts em JSON dentro de artifacts/output/.

    Parâmetros:
      - nome: base do nome do arquivo (sem extensão), ex.: "aliquotas"
      - dados: lista de dicionários
      - indent: indentação do JSON (padrão: 2)

    Retorna:
      - Path do arquivo salvo
    """
    output_dir = _ensure_output_dir()
    caminho = output_dir / f"{nome}.json"

    with caminho.open("w", encoding="utf-8") as f:
        json.dump(dados, f, indent=indent, ensure_ascii=False)

    log.info("JSON salvo em %s (linhas: %d)", caminho, len(dados))
    return caminho


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


def salvar_csv_modular(driver, registros, prefixo="saida"):
    """
    Salva registros em artifacts/output/<prefixo>_<YYYYMMDD-HHMMSS>.csv
    Usa prompt se já existir.
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    nome_arquivo = f"{prefixo}_{timestamp}.csv"
    saida_default = ARTIFACTS / "output" / nome_arquivo
    saida_default.parent.mkdir(parents=True, exist_ok=True)
    return salvar_csv_com_prompt(driver, saida_default, registros)


__all__ = [
    "BASE_DIR",
    "MOD_DIR",
    "ARTIFACTS",
    "LOCATORS_FILE",
    "screenshot",
    "load_locators",
    "listar_modulos",
    "escolher_modulo",
    "salvar_csv",
    "salvar_json",
]
