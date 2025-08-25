"""Launcher do WebScraping-TOTVS.

- Lê configurações de .env ou ENV.
- Cria o driver configurado.
- Faz login e seleção de domínio.
- Lista e executa módulos disponíveis em `modulos/`.
"""

import importlib
import logging
import sys
import traceback
from pathlib import Path
from dataclasses import dataclass
from getpass import getpass

from dotenv import load_dotenv

# --- imports do stdlib aqui em cima ---
import importlib
import logging
import sys
import traceback
from pathlib import Path
from dataclasses import dataclass
from getpass import getpass

# Tente importar como pacote (execução via: python -m core.launcher)
try:
    from .browser import build_driver
    from .auth import login, selecionar_dominio
    from .utils import listar_modulos, escolher_modulo, screenshot
# Se falhar, ajuste o sys.path e importe absoluto (execução via: python core/launcher.py)
except ImportError:
    BASE_DIR = Path(__file__).resolve().parents[1]
    if str(BASE_DIR) not in sys.path:
        sys.path.append(str(BASE_DIR))
    from core.browser import build_driver
    from core.auth import login, selecionar_dominio
    from core.utils import listar_modulos, escolher_modulo, screenshot

from .browser import build_driver
from .auth import login, selecionar_dominio
from .utils import listar_modulos, escolher_modulo, screenshot



log = logging.getLogger("launcher")

BASE_DIR = Path(__file__).resolve().parents[1]
ARTIFACTS = BASE_DIR / "artifacts"
ARTIFACTS.mkdir(exist_ok=True, parents=True)

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


def get_config() -> Config:
    """
    Lê credenciais de variáveis de ambiente/.env.
    Se qualquer uma (URL/USER/PASS) não existir, pergunta interativamente
    e oferece salvar em um arquivo `.env` na raiz do projeto.
    """
    import os

    env_url = os.getenv("TOTVS_URL")
    env_user = os.getenv("TOTVS_USER")
    env_pass = os.getenv("TOTVS_PASS")
    headless = (os.getenv("HEADLESS", "false").lower() == "true")
    user_data_dir = os.getenv("CHROME_USER_DATA_DIR") or None

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
                # Valores opcionais padrão — ajuste depois conforme preferir
                f.write("HEADLESS=false\n")
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


# ---------- Main ----------

def main():
    cfg = get_config()
    driver = None
    try:
        driver = build_driver(cfg)
        login(driver, cfg)
        selecionar_dominio(driver)

        mods = listar_modulos()
        escolhido = escolher_modulo(mods)
        if not escolhido:
            return
        nome, func = escolhido
        log.info("Executando módulo: %s", nome)
        func(driver)
        log.info("Módulo %s concluído.", nome)

    except Exception as e:
        log.error("Erro: %s", e)
        traceback.print_exc()
        if driver:
            screenshot(driver, "erro_launcher")
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    main()
