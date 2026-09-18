from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from backend.main import create_app
import backend.config as config


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


def test_root_serves_index_html(client):
    """Testa se a raiz serve o index.html com status 200 e tipo text/html."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "Voxa" in response.text


@pytest.mark.parametrize(
    "asset_path",
    [
        "/assets/logo.svg",
        "/css/style.css",
        "/js/api.js",
        "/js/state.js",
        "/js/components/toast.js",
        "/js/components/modal.js",
        "/js/components/log-drawer.js",
        "/js/pages/narrate.js",
        "/js/pages/voices.js",
        "/js/pages/history.js",
        "/js/pages/settings.js",
        "/js/app.js",
    ],
)
def test_static_assets_accessible(client, asset_path):
    """Testa se todos os arquivos estáticos de CSS, JS e SVG são acessíveis com status 200."""
    response = client.get(asset_path)
    assert response.status_code == 200, f"Falha ao carregar asset: {asset_path} (Status: {response.status_code})"


def test_index_html_has_expected_references(client):
    """Testa se o index.html possui referências aos arquivos CSS, JS e SVG corretos."""
    response = client.get("/")
    assert response.status_code == 200
    html = response.text

    assert "style.css" in html
    assert "app.js" in html
    assert "logo.svg" in html
    assert 'id="app"' in html or 'id="main-content"' in html
    assert "#narrate" in html
    assert "#voices" in html
    assert "#history" in html
    assert "#settings" in html


def test_index_html_has_log_drawer_elements(client):
    """Testa se o index.html contém os elementos do botão flutuante e do drawer de logs."""
    response = client.get("/")
    assert response.status_code == 200
    html = response.text

    assert 'id="btn-toggle-logs"' in html
    assert 'id="log-error-badge"' in html
    assert 'id="log-drawer"' in html
    assert 'id="log-drawer-resize-handle"' in html
    assert 'id="metric-cpu"' in html
    assert 'id="metric-ram"' in html
    assert 'id="log-level-filter"' in html
    assert 'id="log-search-input"' in html
    assert 'id="btn-autoscroll"' in html
    assert 'id="btn-clear-logs"' in html
    assert 'id="btn-close-drawer"' in html
    assert 'id="log-entries-container"' in html


def test_app_js_initializes_log_drawer(client):
    """Testa se app.js importa e inicializa o componente log-drawer."""
    response = client.get("/js/app.js")
    assert response.status_code == 200
    js_text = response.text
    assert "log-drawer" in js_text
    assert "initLogDrawer" in js_text

