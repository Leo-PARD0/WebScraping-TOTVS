"""
Módulo: sample
Exemplo base para novos módulos: abre o menu principal e mostra mensagem de sucesso.
"""

from core import utils
from modulos.cadastro_produtos._navigate import abrir_menu_principal

def executar(driver, sub_name=None):
    print("Sample rodou com sucesso!")
    utils.log.info("Abrindo menu principal (sample)...")
    abrir_menu_principal(driver)
    utils.log.info("Menu principal aberto (sample).")