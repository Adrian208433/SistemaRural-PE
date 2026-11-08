import pytest
from datetime import datetime

# Importamos las clases y funciones del proyecto principal
from SistemaRural_PE import (
    validar_texto,
    validar_dni,
    generar_codigo,
    resumir_dni,
    crear_hash,
    Persona,
    Paciente,
    Usuario,
    Cita,
    Atencion,
    Reporte,
    ReporteFactory,
    CentroSalud,
    obtener_nombres_pacientes,
    obtener_citas_programadas,
    contar_atenciones
)


# ==========================================
# 1. PRUEBAS DE VALIDACIÓN
# ==========================================

def test_validar_texto_correcto():
    assert validar_texto("Juan Perez", "nombre") == "Juan Perez"


def test_validar_texto_vacio():
    with pytest.raises(ValueError):
        validar_texto("", "nombre")


def test_validar_dni_correcto():
    assert validar_dni("12345678") == "12345678"


def test_validar_dni_incorrecto():
    with pytest.raises(ValueError):
        validar_dni("12345")


def test_validar_dni_con_letras():
    with pytest.raises(ValueError):
        validar_dni("1234ABCD")


# ==========================================
# 2. PRUEBAS DE PACIENTES
# ==========================================

def test_registrar_paciente():
    paciente = Paciente("Carlos Perez", "12345678", "987654321")

    assert paciente.nombre == "Carlos Perez"
    assert paciente.codigo.startswith("PAC-")


def test_dni_protegido():
    paciente = Paciente("Ana Torres", "12345678", "987654321")

    assert paciente.dni_protegido == "****5678"


def test_generar_codigo_unico():
    codigo1 = generar_codigo("PAC")
    codigo2 = generar_codigo("PAC")

    assert codigo1 != codigo2


# ==========================================
# 3. PRUEBAS DE SEGURIDAD
# ==========================================

def test_hash_contrasena():
    salt, hash_clave = crear_hash("ClaveSegura123")

    assert len(salt) == 16
    assert len(hash_clave) == 32


def test_autenticacion_correcta():
    usuario = Usuario(
        "Administrador",
        "12345678",
        "987654321",
        "admin",
        "ClaveSegura123"
    )

    assert usuario.autenticar("ClaveSegura123") is True


def test_autenticacion_incorrecta():
    usuario = Usuario(
        "Administrador",
        "12345678",
        "987654321",
        "admin",
        "ClaveSegura123"
    )

    assert usuario.autenticar("ClaveIncorrecta") is False


# ==========================================
# 4. PRUEBAS DE CITAS Y ATENCIONES
# ==========================================

@pytest.fixture
def paciente():
    return Paciente("Maria Lopez", "87654321", "987654321")


def test_registrar_cita(paciente):
    cita = Cita(paciente, "20/11/2026 09:00", "Consulta general")

    assert cita.paciente == paciente
    assert cita.estado == "Programada"


def test_cancelar_cita(paciente):
    cita = Cita(paciente, "20/11/2026 09:00", "Consulta general")

    cita.cancelar()

    assert cita.estado == "Cancelada"


def test_registrar_atencion(paciente):
    atencion = Atencion(
        paciente,
        "Gripe",
        "Reposo y medicamentos"
    )

    assert atencion.paciente == paciente
    assert atencion.diagnostico == "Gripe"
    assert atencion.tratamiento == "Reposo y medicamentos"


# ==========================================
# 5. PRUEBAS DEL CENTRO DE SALUD
# ==========================================

def test_registrar_y_buscar_paciente(paciente):
    centro = CentroSalud("Centro de Salud Rural")

    centro.registrar_paciente(paciente)

    resultado = centro.buscar_paciente(paciente.codigo)

    assert resultado == paciente


def test_buscar_paciente_inexistente():
    centro = CentroSalud("Centro de Salud Rural")

    assert centro.buscar_paciente("PAC-INEXISTENTE") is None


# ==========================================
# 6. PRUEBAS DE PROGRAMACIÓN FUNCIONAL
# ==========================================

def test_obtener_nombres_pacientes():
    pacientes = [
        Paciente("Carlos Perez", "12345678", "987654321"),
        Paciente("Ana Torres", "87654321", "912345678")
    ]

    nombres = obtener_nombres_pacientes(pacientes)

    assert nombres == ["Carlos Perez", "Ana Torres"]


def test_obtener_citas_programadas(paciente):
    cita1 = Cita(paciente, "20/11/2026", "Consulta")
    cita2 = Cita(paciente, "21/11/2026", "Control")

    cita2.cancelar()

    resultado = obtener_citas_programadas([cita1, cita2])

    assert len(resultado) == 1
    assert resultado[0] == cita1


def test_contar_atenciones(paciente):
    atenciones = [
        Atencion(paciente, "Gripe", "Reposo"),
        Atencion(paciente, "Fiebre", "Medicamentos")
    ]

    assert contar_atenciones(atenciones) == 2


def test_contar_atenciones_vacias():
    assert contar_atenciones([]) == 0


# ==========================================
# 7. PRUEBAS DE REPORTES
# ==========================================

def test_generar_reporte_general(paciente):
    centro = CentroSalud("Centro Rural")
    centro.registrar_paciente(paciente)

    reporte = ReporteFactory.crear_reporte(
        "general",
        centro.pacientes,
        centro.citas,
        centro.atenciones
    )

    assert reporte.titulo == "Reporte general"
    assert "Total de pacientes: 1" in reporte.contenido


def test_generar_reporte_citas(paciente):
    cita = Cita(paciente, "20/11/2026", "Consulta")

    reporte = ReporteFactory.crear_reporte(
        "citas",
        [paciente],
        [cita],
        []
    )

    assert "Citas programadas: 1" in reporte.contenido


def test_generar_reporte_atenciones(paciente):
    atencion = Atencion(paciente, "Gripe", "Reposo")

    reporte = ReporteFactory.crear_reporte(
        "atenciones",
        [paciente],
        [],
        [atencion]
    )

    assert "Atenciones registradas: 1" in reporte.contenido


# ==========================================
# FIN DE LAS PRUEBAS
# ==========================================
