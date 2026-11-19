"""La presentación real, con API doblada y datos inventados: nunca toca producción."""
import json
import threading
from functools import partial
from http.server import ThreadingHTTPServer
from urllib.parse import urlparse

import pytest
from playwright.sync_api import sync_playwright
from tools.serve_v2 import ManejadorSPA, RAIZ


def closed_panel():
    scores = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
    return {'terminado': True, 'grupos_f1': [
        {'grupo': f'Equipo {i+1}', 'puesto': i+1, 'puntos': score,
         'personas': [{'nombre': f'Persona {i+1}', 'puesto': i+1, 'puntos': score}]}
        for i, score in enumerate(scores)]}


@pytest.fixture(scope='module')
def local_server():
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(ManejadorSPA, directory=str(RAIZ)))
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    yield f'http://localhost:{server.server_port}'
    server.shutdown(); server.server_close(); thread.join()


@pytest.fixture(scope='module')
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        yield browser
        browser.close()


def open_results(browser, local_server, panels, reduced_motion='no-preference', viewport=None):
    context = browser.new_context(viewport=viewport or {'width': 1440, 'height': 900}, reduced_motion=reduced_motion)
    calls = []
    def route(request):
        url = request.request.url
        if '/rest/v1/rpc/' in url:
            function = url.rsplit('/', 1)[-1]; calls.append(function)
            assert function == 'tablero_del_evento', 'La presentación nunca escribe'
            payload = panels[min(len(calls)-1, len(panels)-1)]
            request.fulfill(status=503 if payload is None else 200, content_type='application/json',
                            body=json.dumps(payload if payload is not None else {'message': 'sin red'}))
        elif url.startswith('https://cdn.jsdelivr.net/'):
            request.fulfill(content_type='text/javascript', body="""export const createClient = origin => ({rpc: async (fn,args) => {
                const r=await fetch(origin+'/rest/v1/rpc/'+fn,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(args)});
                const body=await r.json(); return r.ok?{data:body,error:null}:{data:null,error:body};}});""")
        elif urlparse(url).netloc == urlparse(local_server).netloc:
            request.continue_()
        else:
            request.fulfill(body='', content_type='text/css')
    context.route('**/*', route)
    page = context.new_page(); page.goto(local_server+'/2/evento/resultados')
    return context, page, calls


# @scenarios ruta-independiente, comienza-en-cero, reparte-en-orden-inverso, retrocede-y-reinicia, presenta-sin-desbordes
# @scenarios anima-el-podio
def test_presenta_por_teclado_y_botones_sin_scroll_y_sin_escrituras(browser, local_server):
    context, page, calls = open_results(browser, local_server, [closed_panel()])
    try:
        page.wait_for_selector('.er .team')
        assert page.locator('.team').count() == 10
        assert not page.locator('.cabecera').count()
        page.locator('[data-er-action="next"]').click()
        assert page.locator('.award-name').inner_text() == 'Persona 10'
        page.keyboard.press('ArrowRight')
        assert page.locator('.award-name').inner_text() == 'Persona 9'
        page.keyboard.press('ArrowLeft')
        assert page.locator('.award-name').inner_text() == 'Persona 10'
        page.locator('[data-er-action="reset"]').click()
        page.locator('body').click(position={'x': 1, 'y': 1})
        page.keyboard.press('Space')
        assert page.locator('.award-name').inner_text() == 'Persona 10'
        for _ in range(7): page.keyboard.press('ArrowRight')
        assert page.locator('.award-points').inner_text() == '+15'
        assert page.locator('.award-points').evaluate('(e)=>e.getAnimations().length') > 0
        page.keyboard.press('ArrowRight'); page.keyboard.press('ArrowRight')
        assert page.locator('.spark').count() > 0
        assert page.locator('[data-er-action="next"]').is_disabled()
        assert page.locator('[data-er="progress-label"]').inner_text() == '101 de 101 puntos repartidos'
        assert page.evaluate('document.documentElement.scrollHeight') <= 900
        page.keyboard.press('ArrowLeft'); assert page.locator('.spark').count() == 0
        page.locator('[data-er-action="reset"]').click(); assert page.locator('.spark').count() == 0
        assert calls == ['tablero_del_evento']
    finally:
        context.close()


# @scenarios espera-al-cierre, reintenta-la-lectura
def test_espera_y_reintenta_el_borde_hasta_el_cierre(browser, local_server):
    context, page, calls = open_results(browser, local_server, [None, {**closed_panel(), 'terminado': False}, closed_panel()])
    try:
        page.get_by_role('button', name='Reintentar').wait_for()
        assert not page.locator('.team').count()
        page.get_by_role('button', name='Reintentar').click()
        page.get_by_text('Los resultados se desvelan cuando termine el evento.').wait_for()
        assert not page.locator('.award-name').count()
        page.wait_for_selector('.team', timeout=6000)
        assert len(calls) >= 3
    finally:
        context.close()


# @scenarios anima-el-podio, presenta-sin-desbordes
def test_movimiento_reducido_y_movil(browser, local_server):
    context, page, _ = open_results(browser, local_server, [closed_panel()], reduced_motion='reduce', viewport={'width':390,'height':844})
    try:
        page.wait_for_selector('.team')
        for _ in range(10): page.keyboard.press('ArrowRight')
        assert page.locator('.spark').count() == 0
        assert page.locator('.award-points').evaluate('(e)=>e.getAnimations().length') == 0
        assert page.evaluate('document.documentElement.scrollWidth') <= 390
    finally:
        context.close()


# @scenarios conserva-los-empates, presenta-sin-desbordes
def test_diez_empatados_conservan_controles_visibles(browser, local_server):
    panel = closed_panel()
    for group in panel['grupos_f1']:
        group['puesto'] = 1
        group['puntos'] = 10.1
        group['personas'][0].update(puesto=1, puntos=10.1)
    context, page, _ = open_results(browser, local_server, [panel], reduced_motion='reduce')
    try:
        page.wait_for_selector('.team')
        page.keyboard.press('ArrowRight')
        assert page.locator('.award-name').count() == 10
        assert page.locator('.rank').all_inner_texts() == ['1'] * 10
        assert page.locator('[data-er-action="previous"]').bounding_box()['y'] < 850
        assert page.evaluate('document.documentElement.scrollHeight') <= 900
        assert page.locator('[data-er="progress-label"]').inner_text() == '101 de 101 puntos repartidos'
    finally:
        context.close()
