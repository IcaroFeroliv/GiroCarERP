import requests

FIPE_BASE_URL = "https://parallelum.com.br/fipe/api/v1/carros"
FIPE_HEADERS = {"User-Agent": "GiroCarERP/1.0"}

def _fipe_get(caminho):
    """Faz GET na API FIPE e devolve o JSON (ou None se falhar)."""
    try:
        req = requests.get(f"{FIPE_BASE_URL}/{caminho}", headers=FIPE_HEADERS)
        return req.json() if req.status_code == 200 else None
    except Exception:
        return None