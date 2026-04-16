from fastapi.testclient import TestClient
from backend.app.main import app  # Importamos tu Orquestador desde tu archivo Calidad.py

# Creamos el "robot" que hará las peticiones
client = TestClient(app)

def test_camino_feliz_gerente():
    """Prueba 1: Datos correctos y regla de negocio (Sin acceso a CRM)"""
    datos = {
        "nombre": "Luis",
        "apellido": "Sarmiento",
        "dni": "70862399",
        "puesto": "Gerente"
    }
    respuesta = client.post("/iniciar-onboarding", json=datos)
    
    # Verificaciones (El robot comprueba que el sistema responda bien)
    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "Completado"
    assert "luis.sarmiento@empresa.com" == respuesta.json()["resultados"]["correo"]
    assert "CRM de Ventas" not in respuesta.json()["resultados"]["herramientas"]

def test_regla_de_negocio_ventas():
    """Prueba 2: Regla de negocio (Puesto de Ventas SÍ recibe CRM)"""
    datos = {
        "nombre": "Ana",
        "apellido": "Gomez",
        "dni": "11223344",
        "puesto": "Asesora de Ventas"
    }
    respuesta = client.post("/iniciar-onboarding", json=datos)
    
    assert respuesta.status_code == 200
    assert "CRM de Ventas" in respuesta.json()["resultados"]["herramientas"]

def test_seguridad_dni_invalido():
    """Prueba 3: Prueba de fallo (DNI de solo 3 números)"""
    datos = {
        "nombre": "Carlos",
        "apellido": "Perez",
        "dni": "123", # DNI intencionalmente corto
        "puesto": "Analista"
    }
    respuesta = client.post("/iniciar-onboarding", json=datos)
    
    # El robot espera un código 422 de rechazo. Si el sistema da un 200, la prueba falla.
    assert respuesta.status_code == 422