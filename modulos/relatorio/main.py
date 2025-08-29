"""
Módulo: relatorio
Abre o menu de relatórios no sistema.
"""

from core import utils
from modulos.cadastro_produtos._navigate import abrir_menu_principal, _clicar_item_menu_por_href

def executar(driver, sub_name=None):
    utils.log.info("Abrindo menu principal (relatório)...")
    abrir_menu_principal(driver)
    utils.log.info("Clicando no item de menu Relatório...")
    _clicar_item_menu_por_href(driver, href="/Relatorios/Relatorio")
    utils.log.info("Menu de relatório aberto com sucesso!")