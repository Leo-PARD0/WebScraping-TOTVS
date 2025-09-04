"""Launcher do WebScraping-TOTVS.

- Lê configurações de .env ou ENV.
- Cria o driver configurado.
- Faz login e seleção de domínio.
- Lista e executa módulos disponíveis em `modulos/` (inclui pacotes).
- Permite escolher o módulo por CLI (--mod) ou ENV (APP_MODULE).
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
import traceback
from dataclasses import dataclass
from getpass import getpass
from pathlib import Path
from typing import Optional, Tuple
import importlib


from dotenv import load_dotenv



# Import preferindo modo pacote: `python -m core.launcher`
try:
    from .browser import build_driver
    from .auth import login, selecionar_dominio
    from .utils import listar_modulos, escolher_modulo, screenshot
    from core._ui import escolher_modulo_no_navegador, toast 
except ImportError:
    # Fallback para execução direta: `python core/launcher.py`
    BASE_DIR = Path(__file__).resolve().parents[1]
    if str(BASE_DIR) not in sys.path:
        sys.path.append(str(BASE_DIR))
    from core.browser import build_driver
    from core.auth import login, selecionar_dominio
    from core.utils import listar_modulos, escolher_modulo, screenshot
    from core._ui import escolher_modulo_no_navegador 

log = logging.getLogger("launcher")

BASE_DIR = Path(__file__).resolve().parents[1]
ARTIFACTS = BASE_DIR / "artifacts"
ARTIFACTS.mkdir(exist_ok=True, parents=True)

# Carrega .env da raiz (se existir)
load_dotenv(BASE_DIR / ".env")


# ---------- Config ----------

@dataclass
class Config:
    url: str
    user: str
    password: str
    headless: bool = False
    page_load_timeout: int = 60
    explicit_timeout: int = 25
    user_data_dir: str | None = None


def _parse_cli() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Launcher WebScraping-TOTVS")
    p.add_argument("--mod", help="Nome do módulo em modulos/ (ex.: cadastro_produtos)")
    p.add_argument("--sub", help="Nome do submódulo em modulos/<mod>/submods/ (ex.: extrair_aliquota)")  # <-- NOVO
    p.add_argument("--headless", action="store_true", help="Força navegador headless")
    p.add_argument("--log", default=os.getenv("APP_LOG_LEVEL", "INFO"), help="Nivel de log (DEBUG, INFO, WARNING)")
    p.add_argument('--retomar', action='store_true', help='Retomar extração do último checkpoint')
    return p.parse_args()


def _setup_logging(level_name: str) -> None:
    level = getattr(logging, level_name.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s %(name)s | %(message)s",
    )
    # Reduz verbosidade de libs ruidosas
    logging.getLogger("selenium").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_config(args: argparse.Namespace) -> Config:
    """
    Lê credenciais de variáveis de ambiente/.env.
    Pergunta interativamente o que faltar e oferece salvar em `.env`.
    `--headless` (CLI) sobrescreve HEADLESS do .env/ENV.
    """
    env_url = os.getenv("TOTVS_URL")
    env_user = os.getenv("TOTVS_USER")
    env_pass = os.getenv("TOTVS_PASS")
    env_headless = (os.getenv("HEADLESS", "false").lower() == "true")
    user_data_dir = os.getenv("CHROME_USER_DATA_DIR") or None

    headless = args.headless or env_headless

    # Se todas as variáveis existem, usa direto
    if env_url and env_user and env_pass:
        return Config(
            url=env_url,
            user=env_user,
            password=env_pass,
            headless=headless,
            user_data_dir=user_data_dir,
        )

    # Caso contrário, pergunta interativamente
    url = env_url or input("URL do TOTVS: ").strip()
    user = env_user or input("Usuário: ").strip()
    password = env_pass or getpass("Senha: ")

    # Oferece salvar em .env
    try:
        salvar = input("Deseja salvar essas credenciais em .env? (s/n): ").strip().lower()
    except KeyboardInterrupt:
        print("\nOperação cancelada.")
        raise

    if salvar == "s":
        env_path = BASE_DIR / ".env"
        try:
            with open(env_path, "w", encoding="utf-8") as f:
                f.write(f"TOTVS_URL={url}\n")
                f.write(f"TOTVS_USER={user}\n")
                f.write(f"TOTVS_PASS={password}\n")
                f.write(f"HEADLESS={'true' if headless else 'false'}\n")
                f.write("CHROME_USER_DATA_DIR=\n")
            print(f"Credenciais salvas em {env_path}")
        except Exception as e:
            print(f"Não foi possível salvar o .env ({e}). A execução continuará normalmente.")

    return Config(
        url=url,
        user=user,
        password=password,
        headless=headless,
        user_data_dir=user_data_dir,
    )


# ---------- Execução ----------

def _listar_submods(mod_name: str) -> list[str]:
    subdir = BASE_DIR / "modulos" / mod_name / "submods"
    if not subdir.exists():
        return []
    submods = []
    # Arquivos .py (exceto __init__)
    submods += [
        p.stem
        for p in subdir.glob("*.py")
        if p.is_file() and p.stem != "__init__"
    ]
    # Pastas com __init__.py (pacotes)
    submods += [
        p.name
        for p in subdir.iterdir()
        if p.is_dir() and (p / "__init__.py").exists()
    ]
    return submods


def _resolver_modulo(driver, preferido: Optional[str]) -> Tuple[str, callable]:
    """
    Escolhe o módulo a executar (aceita arquivos .py e pacotes com __init__.py).
    Se `preferido` (CLI/ENV) vier, usa direto; senão tenta escolher via UI no navegador.
    Cai para o menu do console se estiver em headless ou se a UI falhar.
    """
    mods = listar_modulos()
    if not mods:
        raise SystemExit("[ERRO] Nenhum módulo válido encontrado em modulos/.")

    if preferido:
        candidatos = [(n, f) for (n, f) in mods if n == preferido]
        if not candidatos:
            nomes = ", ".join(n for n, _ in mods) or "<nenhum>"
            raise SystemExit(f"[ERRO] Módulo '{preferido}' não encontrado. Disponíveis: {nomes}")
        return candidatos[0]

    if len(mods) == 1:
        n, f = mods[0]
        log.info("Selecionando módulo único automaticamente: %s", n)
        return mods[0]
    
    def _listar_submods(mod_name: str) -> list[str]:
        subdir = BASE_DIR / "modulos" / mod_name / "submods"
        if not subdir.exists():
            return []
        return [p.stem for p in subdir.glob("*.py") if p.is_file() and p.stem != "__init__"]


    nomes = [n for (n, _) in mods]

    # Heurística simples para headless
    is_headless = os.getenv("HEADLESS", "false").lower() == "true"

    if not is_headless:
        try:
            default_value = "cadastro_produtos" if "cadastro_produtos" in nomes else (nomes[0] if nomes else None)
            escolha_nome = escolher_modulo_no_navegador(driver, nomes, default_value=default_value)
            if escolha_nome:
                for (n, f) in mods:
                    if n == escolha_nome:
                        return (n, f)
            raise SystemExit("[ERRO] Nenhum módulo selecionado (cancelado na UI).")
        except Exception as e:
            log.warning("Falha ao selecionar via UI no navegador (%s). Caindo para menu no console.", e)

    escolha = escolher_modulo(mods)
    if not escolha:
        raise SystemExit("[ERRO] Nenhum módulo selecionado.")
    return escolha


def main():
    args = _parse_cli()
    _setup_logging(args.log)

    # NOVO: Suporte a --sub giro.teste
    submod = args.sub
    subsubmod = None
    if args.sub and '.' in args.sub:
        submod, subsubmod = args.sub.split('.', 1)
        args.sub = submod  # para as validações continuarem funcionando

    preferido = args.mod or os.getenv("APP_MODULE")
    cfg = get_config(args)

    driver = None
    try:
        driver = build_driver(cfg)
        login(driver, cfg)
        selecionar_dominio(driver)

        # ===== Execução direta via CLI: --mod + --sub =====
        if args.mod and args.sub:
            mods = listar_modulos()
            nomes_mod = {n for (n, _) in mods}
            if args.mod not in nomes_mod:
                opcoes = ", ".join(sorted(nomes_mod)) or "<nenhum>"
                raise SystemExit(f"[ERRO] Módulo '{args.mod}' não encontrado. Disponíveis: {opcoes}")

            subs = _listar_submods(args.mod)
            if args.sub not in subs:
                opcoes = ", ".join(sorted(subs)) or "<nenhum>"
                raise SystemExit(f"[ERRO] Submódulo '{args.sub}' não encontrado em '{args.mod}'. Submódulos: {opcoes}")

            pkg_main = importlib.import_module(f"modulos.{args.mod}.main")
            if not hasattr(pkg_main, "executar"):
                raise SystemExit(f"[ERRO] Módulo '{args.mod}' não possui função main.executar(driver, sub_name=None).")

            log.info("Executando módulo: %s (sub=%s)", args.mod, args.sub)
            # Aqui passa o subsubmodulo (se houver) para o main.py do submódulo
            sub_name_full = args.sub
            if subsubmod:
                sub_name_full = f"{submod}.{subsubmod}"
            pkg_main.executar(driver, sub_name=sub_name_full, retomar=args.retomar)
            return
        
        # ===== Execução normal (sem --sub) =====
        mod_name, _ = _resolver_modulo(driver, preferido)
        pkg_main = importlib.import_module(f"modulos.{mod_name}.main")
        if not hasattr(pkg_main, "executar"):
            raise SystemExit(f"[ERRO] Módulo '{mod_name}' não possui função main.executar(driver, sub_name=None).")
        log.info("Executando módulo: %s", mod_name)
        pkg_main.executar(driver, sub_name=None)
        return


    except SystemExit as e:
        log.error(str(e))
        raise
    except Exception as e:
        log.error("Erro: %s", e)
        traceback.print_exc()
        if driver:
            try:
                screenshot(driver, "erro_launcher")
            except Exception:
                pass
        raise
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


if __name__ == "__main__":
    main()

