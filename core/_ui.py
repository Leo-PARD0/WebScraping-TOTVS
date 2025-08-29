# ui.py
"""
UI helpers para interação direta no navegador via Selenium/JS.

Principais funções:
- escolher_modulo_no_navegador(driver, mods, default_value=None) -> str|None
- confirmar(driver, mensagem, ok_text='OK', cancel_text='Cancelar') -> bool
- toast(driver, mensagem, ms=2000) -> None
"""

from __future__ import annotations
from typing import List, Optional
from selenium.webdriver.remote.webdriver import WebDriver


def escolher_modulo_no_navegador(
    driver: WebDriver,
    mods: List[str],
    default_value: Optional[str] = None,
) -> Optional[str]:
    """
    Abre um modal simples no navegador para escolher um submódulo.
    - mods: lista de nomes de módulos (p.ex.: ["extrair_aliquota"])
    - default_value: valor sugerido no input
    Retorna o nome escolhido (str) ou None se o usuário cancelar.
    """
    return driver.execute_async_script(
        """
        const cb = arguments[arguments.length - 1];
        const mods = arguments[0] || [];
        const defV = arguments[1] || '';

        // Remove modal anterior, se existir
        const old = document.getElementById('gpt-modal-wrap');
        if (old) old.remove();

        // Wrapper
        const wrap = document.createElement('div');
        wrap.id = 'gpt-modal-wrap';
        wrap.style.cssText = [
          'position:fixed','inset:0','background:rgba(0,0,0,.45)',
          'display:flex','align-items:center','justify-content:center',
          'z-index:2147483647'
        ].join(';');

        // Caixa
        const box = document.createElement('div');
        box.style.cssText = [
          'background:#fff','padding:16px','border-radius:12px',
          'min-width:360px','max-width:640px',
          'box-shadow:0 10px 30px rgba(0,0,0,.3)',
          'font:14px system-ui,Segoe UI,Arial,sans-serif'
        ].join(';');

        box.innerHTML = `
          <div style="margin-bottom:8px;font-size:16px;font-weight:600">
            Escolha um submódulo (cadastro_produtos/submods/)
          </div>
          <div id="gpt-list" style="display:flex;flex-wrap:wrap;gap:8px;max-height:260px;overflow:auto;margin-bottom:10px"></div>
          <div style="display:flex;gap:8px;align-items:center">
            <input id="gpt-input" placeholder="ou digite um nome..." style="flex:1;padding:8px;border:1px solid #ccc;border-radius:8px">
            <button id="gpt-ok" style="padding:8px 12px;border:1px solid #0a84ff;border-radius:8px;background:#0a84ff;color:#fff">OK</button>
            <button id="gpt-cancel" style="padding:8px 12px;border:1px solid #bbb;border-radius:8px;background:#f5f5f5">Cancelar</button>
          </div>
        `;

        wrap.appendChild(box);
        document.body.appendChild(wrap);

        const list = box.querySelector('#gpt-list');
        mods.forEach((m) => {
          const b = document.createElement('button');
          b.textContent = m;
          b.style.cssText = 'padding:6px 10px;border:1px solid #ddd;border-radius:8px;background:#fafafa;cursor:pointer';
          b.onclick = () => finish(m);
          list.appendChild(b);
        });

        const input = box.querySelector('#gpt-input');
        input.value = defV || (mods[0] || '');
        input.onkeydown = (e) => {
          if (e.key === 'Enter') finish(input.value.trim());
          if (e.key === 'Escape') finish(null);
        };

        box.querySelector('#gpt-ok').onclick = () => finish(input.value.trim());
        box.querySelector('#gpt-cancel').onclick = () => finish(null);

        let done = false;
        function finish(val){
          if (done) return;
          done = true;
          try { wrap.remove(); } catch (e) {}
          cb(val || null);
        }
        """,
        mods,
        default_value,
    )


def confirmar(
    driver: WebDriver,
    mensagem: str,
    ok_text: str = "OK",
    cancel_text: str = "Cancelar",
) -> bool:
    """
    Mostra um dialog simples de confirmação dentro do navegador.
    Retorna True se OK, False se cancelar.
    """
    return bool(
        driver.execute_async_script(
            """
            const cb = arguments[arguments.length - 1];
            const msg = arguments[0] || '';
            const okT = arguments[1] || 'OK';
            const cancelT = arguments[2] || 'Cancelar';

            const old = document.getElementById('gpt-confirm-wrap');
            if (old) old.remove();

            const wrap = document.createElement('div');
            wrap.id = 'gpt-confirm-wrap';
            wrap.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,.45);display:flex;align-items:center;justify-content:center;z-index:2147483647';

            const box = document.createElement('div');
            box.style.cssText = 'background:#fff;padding:16px;border-radius:12px;min-width:300px;max-width:540px;box-shadow:0 10px 30px rgba(0,0,0,.3);font:14px system-ui,Segoe UI,Arial,sans-serif';

            box.innerHTML = `
              <div style="margin-bottom:12px;font-size:15px">${msg.replace(/</g,'&lt;').replace(/>/g,'&gt;')}</div>
              <div style="display:flex;gap:8px;justify-content:flex-end">
                <button id="gpt-no"  style="padding:8px 12px;border:1px solid #bbb;border-radius:8px;background:#f5f5f5">${cancelT}</button>
                <button id="gpt-yes" style="padding:8px 12px;border:1px solid #0a84ff;border-radius:8px;background:#0a84ff;color:#fff">${okT}</button>
              </div>
            `;

            wrap.appendChild(box);
            document.body.appendChild(wrap);

            const yes = box.querySelector('#gpt-yes');
            const no  = box.querySelector('#gpt-no');

            function finish(val){
              try { wrap.remove(); } catch(e) {}
              cb(!!val);
            }

            yes.onclick = () => finish(true);
            no.onclick  = () => finish(false);

            // Esc/Enter
            wrap.onkeydown = (e) => {
              if (e.key === 'Escape') finish(false);
              if (e.key === 'Enter')  finish(true);
            };
            wrap.tabIndex = -1;
            wrap.focus();
            """,
            mensagem,
            ok_text,
            cancel_text,
        )
    )


def toast(driver: WebDriver, mensagem: str, ms: int = 2000) -> None:
    """
    Exibe um 'toast' (notificação temporária) no canto superior direito.
    Não bloqueia o fluxo.
    """
    driver.execute_script(
        """
        const msg = arguments[0] || '';
        const ms  = arguments[1] || 2000;

        // container
        let cont = document.getElementById('gpt-toast-cont');
        if (!cont) {
          cont = document.createElement('div');
          cont.id = 'gpt-toast-cont';
          cont.style.cssText = 'position:fixed;top:16px;right:16px;z-index:2147483647;display:flex;flex-direction:column;gap:8px';
          document.body.appendChild(cont);
        }

        // toast
        const t = document.createElement('div');
        t.style.cssText = 'background:#333;color:#fff;padding:8px 12px;border-radius:10px;box-shadow:0 6px 18px rgba(0,0,0,.25);max-width:420px;font:13px system-ui,Segoe UI,Arial,sans-serif;opacity:0;transform:translateY(-6px);transition:all .2s ease';
        t.innerHTML = msg.replace(/</g,'&lt;').replace(/>/g,'&gt;');
        cont.appendChild(t);

        // anima
        requestAnimationFrame(() => {
          t.style.opacity = '1';
          t.style.transform = 'translateY(0)';
        });

        setTimeout(() => {
          t.style.opacity = '0';
          t.style.transform = 'translateY(-6px)';
          setTimeout(() => t.remove(), 200);
        }, ms);
        """,
        mensagem,
        ms,
    )


def prompt_paginas_extracao(driver, mensagem="Quantas páginas deseja extrair?", ok_text="OK", all_text="Extrair tudo", cancel_text="Cancelar"):
    """
    Mostra um dialog para o usuário informar o número de páginas a extrair ou escolher 'Extrair tudo'.
    Retorna:
      - int: número de páginas
      - True: se escolher 'Extrair tudo'
      - None: se cancelar
    """
    return driver.execute_async_script(
        """
        const cb = arguments[arguments.length - 1];
        const msg = arguments[0] || '';
        const okT = arguments[1] || 'OK';
        const allT = arguments[2] || 'Extrair tudo';
        const cancelT = arguments[3] || 'Cancelar';

        // Remove modal anterior
        const old = document.getElementById('gpt-paginas-wrap');
        if (old) old.remove();

        // Wrapper
        const wrap = document.createElement('div');
        wrap.id = 'gpt-paginas-wrap';
        wrap.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,.45);display:flex;align-items:center;justify-content:center;z-index:2147483647';

        // Caixa
        const box = document.createElement('div');
        box.style.cssText = 'background:#fff;padding:16px;border-radius:12px;min-width:320px;max-width:480px;box-shadow:0 10px 30px rgba(0,0,0,.3);font:14px system-ui,Segoe UI,Arial,sans-serif';

        box.innerHTML = `
          <div style="margin-bottom:10px;font-size:15px">${msg.replace(/</g,'&lt;').replace(/>/g,'&gt;')}</div>
          <input id="gpt-pg-input" type="number" min="1" step="1" style="width:120px;padding:8px;border:1px solid #ccc;border-radius:8px;margin-bottom:12px" placeholder="Ex: 5">
          <div style="display:flex;gap:8px;justify-content:flex-end">
            <button id="gpt-all" style="padding:8px 12px;border:1px solid #0a84ff;border-radius:8px;background:#0a84ff;color:#fff">${allT}</button>
            <button id="gpt-ok" style="padding:8px 12px;border:1px solid #0a84ff;border-radius:8px;background:#fff;color:#0a84ff">${okT}</button>
            <button id="gpt-cancel" style="padding:8px 12px;border:1px solid #bbb;border-radius:8px;background:#f5f5f5">${cancelT}</button>
          </div>
        `;

        wrap.appendChild(box);
        document.body.appendChild(wrap);

        const input = box.querySelector('#gpt-pg-input');
        input.focus();

        box.querySelector('#gpt-ok').onclick = () => {
          const val = parseInt(input.value, 10);
          finish(Number.isFinite(val) && val > 0 ? val : null);
        };
        box.querySelector('#gpt-all').onclick = () => finish(true);
        box.querySelector('#gpt-cancel').onclick = () => finish(null);

        input.onkeydown = (e) => {
          if (e.key === 'Enter') box.querySelector('#gpt-ok').click();
          if (e.key === 'Escape') box.querySelector('#gpt-cancel').click();
        };

        let done = false;
        function finish(val){
          if (done) return;
          done = true;
          try { wrap.remove(); } catch(e) {}
          cb(val);
        }
        """,
        mensagem,
        ok_text,
        all_text,
        cancel_text,
    )
