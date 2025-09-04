import time

def centralizar_elemento_na_tela(driver, elemento, delay: float = 0.3):
    """
    Centraliza o elemento na tela usando window.scrollTo.
    """
    driver.execute_script("""
        const el = arguments[0];
        const rect = el.getBoundingClientRect();
        window.scrollTo({
            top: rect.top + window.scrollY - (window.innerHeight / 2) + (rect.height / 2),
            behavior: 'smooth'
        });
    """, elemento)
    time.sleep(delay)