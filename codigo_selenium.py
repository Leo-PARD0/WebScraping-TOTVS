from selenium import webdriver
import time

# Abrir o navegador
navegador = webdriver.Chrome()

# acessar o site
navegador.get("https://chefwebcloud.chef.totvs.com.br/")

# colocar o navegador em tela cheia
navegador.maximize_window()

# Selecionar um elemento na tela de login
UserName = navegador.find_element("id", "UserName")
Senha = navegador.find_element("id", "Senha")
Botao_Login = navegador.find_element("id", "btnLogin")

# Clicar em um elemento
UserName.click()

# Escrever no Formulário
UserName.send_keys("LEO14")
Senha.send_keys("Tm3mm!3r4n3C")
Botao_Login.click()

#escolher Loja
navegador.find_element("id", "comboBoxDomain").click()


time.sleep(1000)