
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from abc import ABC, abstractmethod
from datetime import datetime
from functools import reduce
from hashlib import pbkdf2_hmac
from os import urandom
from uuid import uuid4


# ==========================================================
# 1. PARADIGMA ESTRUCTURADO: funciones de validación
# ==========================================================

def validar_texto(valor, campo):
    """Comprueba que un campo contenga texto no vacío."""
    if not valor or not valor.strip():
        raise ValueError(f"El campo {campo} es obligatorio.")
    return valor.strip()


def validar_dni(dni):
    """Valida un DNI ficticio de ocho dígitos."""
    dni = dni.strip()
    if not dni.isdigit() or len(dni) != 8:
        raise ValueError("El DNI debe contener exactamente 8 dígitos.")
    return dni


def generar_codigo(prefijo):
    """Genera un identificador interno para cada registro."""
    return f"{prefijo}-{uuid4().hex[:8].upper()}"


def resumir_dni(dni):
    """Oculta parte del DNI al mostrarlo en pantalla."""
    return "*" * 4 + dni[-4:]


def crear_hash(clave, salt=None):
    """Genera un hash de contraseña; nunca se guarda la clave en texto plano."""
    salt = salt or urandom(16)
    resultado = pbkdf2_hmac("sha256", clave.encode("utf-8"), salt, 200_000)
    return salt, resultado


# ==========================================================
# 2. PARADIGMA ORIENTADO A OBJETOS: clases y encapsulamiento
# ==========================================================

class Persona(ABC):
    """Clase abstracta con los datos comunes de una persona."""

    def __init__(self, nombre, dni, telefono):
        self._nombre = validar_texto(nombre, "nombre")
        self._dni = validar_dni(dni)
        self._telefono = validar_texto(telefono, "teléfono")

    @property
    def nombre(self):
        return self._nombre

    @property
    def dni_protegido(self):
        return resumir_dni(self._dni)

    @abstractmethod
    def tipo(self):
        pass


class Paciente(Persona):
    """Representa a un paciente del establecimiento."""

    def __init__(self, nombre, dni, telefono):
        super().__init__(nombre, dni, telefono)
        self.__codigo = generar_codigo("PAC")

    @property
    def codigo(self):
        return self.__codigo

    def tipo(self):
        return "Paciente"


class Usuario(Persona):
    """Representa al personal autorizado para ingresar al sistema."""

    def __init__(self, nombre, dni, telefono, usuario, clave, rol="Personal de salud"):
        super().__init__(nombre, dni, telefono)
        self.__usuario = validar_texto(usuario, "usuario")
        self.__salt, self.__hash = crear_hash(clave)
        self.__rol = rol

    @property
    def usuario(self):
        return self.__usuario

    @property
    def rol(self):
        return self.__rol

    def autenticar(self, clave):
        _, hash_ingresado = crear_hash(clave, self.__salt)
        return hash_ingresado == self.__hash

    def tipo(self):
        return "Usuario"


class Cita:
    """Almacena una cita médica asociada a un paciente."""

    def __init__(self, paciente, fecha, motivo):
        self.codigo = generar_codigo("CIT")
        self.paciente = paciente
        self.fecha = validar_texto(fecha, "fecha")
        self.motivo = validar_texto(motivo, "motivo")
        self.estado = "Programada"

    def cancelar(self):
        self.estado = "Cancelada"


class Atencion:
    """Registra la atención brindada a un paciente."""

    def __init__(self, paciente, diagnostico, tratamiento):
        self.codigo = generar_codigo("ATE")
        self.paciente = paciente
        self.diagnostico = validar_texto(diagnostico, "diagnóstico")
        self.tratamiento = validar_texto(tratamiento, "tratamiento")
        self.fecha = datetime.now().strftime("%d/%m/%Y %H:%M")


class Reporte:
    """Objeto que representa un reporte estadístico."""

    def __init__(self, titulo, contenido):
        self.titulo = titulo
        self.contenido = contenido

    def generar(self):
        return f"{self.titulo}\n\n{self.contenido}"


class ReporteFactory:
    """Patrón Factory: centraliza la creación de reportes."""

    @staticmethod
    def crear_reporte(tipo, pacientes, citas, atenciones):
        if tipo == "general":
            contenido = (
                f"Total de pacientes: {len(pacientes)}\n"
                f"Total de citas: {len(citas)}\n"
                f"Total de atenciones: {len(atenciones)}"
            )
            return Reporte("Reporte general", contenido)

        if tipo == "citas":
            programadas = list(filter(lambda c: c.estado == "Programada", citas))
            contenido = f"Citas programadas: {len(programadas)}"
            return Reporte("Reporte de citas", contenido)

        total = reduce(lambda acumulado, _item: acumulado + 1, atenciones, 0)
        return Reporte("Reporte de atenciones", f"Atenciones registradas: {total}")


class CentroSalud:
    """Administra las colecciones principales del establecimiento."""

    def __init__(self, nombre):
        self.nombre = nombre
        self.pacientes = []
        self.citas = []
        self.atenciones = []
        self.usuarios = []

    def registrar_paciente(self, paciente):
        self.pacientes.append(paciente)

    def buscar_paciente(self, codigo):
        return next((p for p in self.pacientes if p.codigo == codigo), None)

    def registrar_cita(self, cita):
        self.citas.append(cita)

    def registrar_atencion(self, atencion):
        self.atenciones.append(atencion)

    def agregar_usuario(self, usuario):
        self.usuarios.append(usuario)


class GestorSistema:
    """Patrón Singleton: mantiene una única instancia del gestor."""

    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia.centro = CentroSalud("SistemaRural-PE")
            cls._instancia.usuario_actual = None
            cls._instancia._inicializado = False
        return cls._instancia

    def inicializar_demo(self):
        if self._inicializado:
            return
        # Cuenta demostrativa. Cambiar la clave antes de cualquier uso real.
        demo = Usuario("Administrador", "00000000", "000000000",
                       "admin", "Rural2026!", "Administrador")
        self.centro.agregar_usuario(demo)
        self._inicializado = True


# ==========================================================
# 3. PARADIGMA FUNCIONAL: map, filter y reduce
# ==========================================================

def obtener_nombres_pacientes(pacientes):
    """map transforma la colección de pacientes en nombres."""
    return list(map(lambda paciente: paciente.nombre, pacientes))


def obtener_citas_programadas(citas):
    """filter selecciona únicamente las citas programadas."""
    return list(filter(lambda cita: cita.estado == "Programada", citas))


def contar_atenciones(atenciones):
    """reduce calcula el total de atenciones registradas."""
    return reduce(lambda total, _atencion: total + 1, atenciones, 0)


# ==========================================================
# 4. PARADIGMA ORIENTADO A EVENTOS: interfaz Tkinter
# ==========================================================

class AplicacionSistema:
    def __init__(self, root):
        self.root = root
        self.root.title("SistemaRural-PE | Gestión de salud")
        self.root.geometry("900x620")
        self.root.minsize(760, 520)
        self.gestor = GestorSistema()
        self.gestor.inicializar_demo()
        self.mostrar_login()

    def limpiar(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def mostrar_login(self):
        self.limpiar()
        marco = ttk.Frame(self.root, padding=35)
        marco.pack(expand=True)

        ttk.Label(marco, text="SistemaRural-PE",
                  font=("Arial", 22, "bold")).pack(pady=10)
        ttk.Label(marco, text="Gestión de establecimientos de salud").pack(pady=5)

        ttk.Label(marco, text="Usuario").pack(anchor="w", pady=(18, 3))
        entrada_usuario = ttk.Entry(marco, width=32)
        entrada_usuario.pack()

        ttk.Label(marco, text="Contraseña").pack(anchor="w", pady=(12, 3))
        entrada_clave = ttk.Entry(marco, width=32, show="*")
        entrada_clave.pack()

        def iniciar_sesion():
            usuario = next(
                (u for u in self.gestor.centro.usuarios
                 if u.usuario == entrada_usuario.get().strip()),
                None
            )
            if usuario and usuario.autenticar(entrada_clave.get()):
                self.gestor.usuario_actual = usuario
                self.mostrar_panel()
            else:
                messagebox.showerror("Acceso denegado", "Usuario o contraseña incorrectos.")

        ttk.Button(marco, text="Iniciar sesión",
                   command=iniciar_sesion).pack(pady=20, fill="x")
        ttk.Label(marco, text="Cuenta demostrativa: admin / Rural2026!",
                  foreground="gray").pack()

    def mostrar_panel(self):
        self.limpiar()
        centro = self.gestor.centro

        encabezado = ttk.Frame(self.root, padding=18)
        encabezado.pack(fill="x")
        ttk.Label(encabezado, text="SistemaRural-PE",
                  font=("Arial", 20, "bold")).pack(side="left")
        usuario = self.gestor.usuario_actual
        ttk.Label(encabezado, text=f"Sesión: {usuario.usuario} ({usuario.rol})"
                  ).pack(side="right")

        ttk.Label(self.root, text="Panel principal",
                  font=("Arial", 14, "bold")).pack(anchor="w", padx=22, pady=8)

        panel = ttk.Frame(self.root, padding=15)
        panel.pack(fill="both", expand=True)

        modulos = [
            ("Pacientes", "Registro y búsqueda", self.modulo_pacientes),
            ("Citas médicas", "Programación y control", self.modulo_citas),
            ("Atenciones", "Registro de consultas", self.modulo_atenciones),
            ("Reportes", "Estadísticas", self.modulo_reportes),
            ("Usuarios", "Acceso al sistema", self.modulo_usuarios),
            ("Cerrar sesión", "Salir de la cuenta", self.cerrar_sesion),
        ]

        for indice, (titulo, descripcion, accion) in enumerate(modulos):
            fila, columna = divmod(indice, 2)
            tarjeta = ttk.LabelFrame(panel, text=titulo, padding=18)
            tarjeta.grid(row=fila, column=columna, padx=9, pady=9,
                         sticky="nsew")
            ttk.Label(tarjeta, text=descripcion).pack(anchor="w", pady=5)
            ttk.Button(tarjeta, text="Abrir módulo",
                       command=accion).pack(anchor="w", pady=5)

        panel.columnconfigure(0, weight=1)
        panel.columnconfigure(1, weight=1)
        for fila in range(3):
            panel.rowconfigure(fila, weight=1)

        ttk.Label(self.root, text="Prototipo académico. Utiliza datos ficticios.",
                  foreground="gray").pack(pady=8)

    def ventana_modulo(self, titulo):
        ventana = tk.Toplevel(self.root)
        ventana.title(titulo)
        ventana.geometry("720x480")
        ventana.transient(self.root)
        return ventana

    def modulo_pacientes(self):
        ventana = self.ventana_modulo("Pacientes")
        ttk.Label(ventana, text="Registro de pacientes",
                  font=("Arial", 16, "bold")).pack(pady=10)

        formulario = ttk.Frame(ventana, padding=10)
        formulario.pack(fill="x")
        campos = {}
        for etiqueta in ("Nombre", "DNI (8 dígitos)", "Teléfono"):
            ttk.Label(formulario, text=etiqueta).pack(anchor="w")
            entrada = ttk.Entry(formulario)
            entrada.pack(fill="x", pady=3)
            campos[etiqueta] = entrada

        tabla = ttk.Treeview(ventana, columns=("codigo", "nombre", "dni"),
                             show="headings", height=8)
        for columna, titulo in (("codigo", "Código"), ("nombre", "Nombre"),
                                ("dni", "DNI protegido")):
            tabla.heading(columna, text=titulo)
        tabla.pack(fill="both", expand=True, padx=12, pady=8)

        def actualizar_tabla():
            tabla.delete(*tabla.get_children())
            for p in self.gestor.centro.pacientes:
                tabla.insert("", "end", values=(p.codigo, p.nombre, p.dni_protegido))

        def guardar():
            try:
                paciente = Paciente(
                    campos["Nombre"].get(),
                    campos["DNI (8 dígitos)"].get(),
                    campos["Teléfono"].get()
                )
                self.gestor.centro.registrar_paciente(paciente)
                actualizar_tabla()
                for entrada in campos.values():
                    entrada.delete(0, "end")
                messagebox.showinfo("Correcto", "Paciente registrado.")
            except ValueError as error:
                messagebox.showerror("Validación", str(error))

        ttk.Button(formulario, text="Registrar paciente",
                   command=guardar).pack(pady=8)
        actualizar_tabla()

    def modulo_citas(self):
        ventana = self.ventana_modulo("Citas médicas")
        ttk.Label(ventana, text="Programación de citas",
                  font=("Arial", 16, "bold")).pack(pady=12)

        pacientes = self.gestor.centro.pacientes
        if not pacientes:
            ttk.Label(ventana, text="Primero debe registrar un paciente.").pack(pady=20)
            return

        nombres = [f"{p.codigo} | {p.nombre}" for p in pacientes]
        seleccion = tk.StringVar(value=nombres[0])
        ttk.Label(ventana, text="Paciente").pack(anchor="w", padx=20)
        ttk.Combobox(ventana, textvariable=seleccion, values=nombres,
                     state="readonly").pack(fill="x", padx=20, pady=5)

        ttk.Label(ventana, text="Fecha y hora (ej. 20/11/2026 09:00)").pack(
            anchor="w", padx=20)
        fecha = ttk.Entry(ventana)
        fecha.pack(fill="x", padx=20, pady=5)

        ttk.Label(ventana, text="Motivo de la cita").pack(anchor="w", padx=20)
        motivo = ttk.Entry(ventana)
        motivo.pack(fill="x", padx=20, pady=5)

        tabla = ttk.Treeview(ventana, columns=("paciente", "fecha", "estado"),
                             show="headings")
        for col, texto in (("paciente", "Paciente"), ("fecha", "Fecha"),
                           ("estado", "Estado")):
            tabla.heading(col, text=texto)
        tabla.pack(fill="both", expand=True, padx=15, pady=10)

        def actualizar():
            tabla.delete(*tabla.get_children())
            for c in self.gestor.centro.citas:
                tabla.insert("", "end", values=(c.paciente.nombre, c.fecha, c.estado))

        def guardar():
            try:
                elegido = next(p for p in pacientes if seleccion.get().startswith(p.codigo))
                cita = Cita(elegido, fecha.get(), motivo.get())
                self.gestor.centro.registrar_cita(cita)
                actualizar()
                messagebox.showinfo("Correcto", "Cita registrada.")
            except (ValueError, StopIteration) as error:
                messagebox.showerror("Validación", str(error) or "Seleccione un paciente.")

        ttk.Button(ventana, text="Registrar cita", command=guardar).pack(pady=5)
        actualizar()

    def modulo_atenciones(self):
        ventana = self.ventana_modulo("Atenciones")
        ttk.Label(ventana, text="Registro de atenciones",
                  font=("Arial", 16, "bold")).pack(pady=12)

        pacientes = self.gestor.centro.pacientes
        if not pacientes:
            ttk.Label(ventana, text="Primero debe registrar un paciente.").pack(pady=20)
            return

        opciones = [f"{p.codigo} | {p.nombre}" for p in pacientes]
        seleccionado = tk.StringVar(value=opciones[0])
        ttk.Label(ventana, text="Paciente").pack(anchor="w", padx=20)
        ttk.Combobox(ventana, textvariable=seleccionado, values=opciones,
                     state="readonly").pack(fill="x", padx=20, pady=5)

        ttk.Label(ventana, text="Diagnóstico").pack(anchor="w", padx=20)
        diagnostico = ttk.Entry(ventana)
        diagnostico.pack(fill="x", padx=20, pady=5)

        ttk.Label(ventana, text="Tratamiento").pack(anchor="w", padx=20)
        tratamiento = ttk.Entry(ventana)
        tratamiento.pack(fill="x", padx=20, pady=5)

        def guardar():
            try:
                paciente = next(p for p in pacientes
                                if seleccionado.get().startswith(p.codigo))
                atencion = Atencion(paciente, diagnostico.get(), tratamiento.get())
                self.gestor.centro.registrar_atencion(atencion)
                messagebox.showinfo("Correcto", "Atención registrada.")
                diagnostico.delete(0, "end")
                tratamiento.delete(0, "end")
            except (ValueError, StopIteration) as error:
                messagebox.showerror("Validación", str(error) or "Seleccione un paciente.")

        ttk.Button(ventana, text="Guardar atención", command=guardar).pack(pady=15)

    def modulo_reportes(self):
        ventana = self.ventana_modulo("Reportes")
        centro = self.gestor.centro
        ttk.Label(ventana, text="Reportes estadísticos",
                  font=("Arial", 16, "bold")).pack(pady=12)

        # map, filter y reduce se aplican a colecciones del sistema.
        nombres = obtener_nombres_pacientes(centro.pacientes)
        citas_programadas = obtener_citas_programadas(centro.citas)
        total_atenciones = contar_atenciones(centro.atenciones)

        texto = (
            f"Establecimiento: {centro.nombre}\n\n"
            f"Pacientes registrados: {len(nombres)}\n"
            f"Citas programadas: {len(citas_programadas)}\n"
            f"Atenciones registradas: {total_atenciones}\n\n"
            "Pacientes:\n" + ("\n".join(nombres) if nombres else "Sin registros")
        )
        ttk.Label(ventana, text=texto, justify="left").pack(
            anchor="w", padx=25, pady=15)

        reporte = ReporteFactory.crear_reporte(
            "general", centro.pacientes, centro.citas, centro.atenciones
        )
        ttk.Button(ventana, text="Mostrar reporte general",
                   command=lambda: messagebox.showinfo(
                       reporte.titulo, reporte.generar()
                   )).pack(pady=10)

    def modulo_usuarios(self):
        ventana = self.ventana_modulo("Usuarios")
        ttk.Label(ventana, text="Usuarios del sistema",
                  font=("Arial", 16, "bold")).pack(pady=12)

        tabla = ttk.Treeview(ventana, columns=("usuario", "rol"),
                             show="headings")
        tabla.heading("usuario", text="Usuario")
        tabla.heading("rol", text="Rol")
        tabla.pack(fill="both", expand=True, padx=20, pady=15)

        for usuario in self.gestor.centro.usuarios:
            tabla.insert("", "end", values=(usuario.usuario, usuario.rol))

        ttk.Label(ventana, text="Las contraseñas no se muestran ni se almacenan en texto plano.",
                  foreground="gray").pack(pady=8)

    def cerrar_sesion(self):
        if messagebox.askyesno("Cerrar sesión", "¿Desea salir de su cuenta?"):
            self.gestor.usuario_actual = None
            self.mostrar_login()


def main():
    """Punto de entrada del programa."""
    try:
        root = tk.Tk()
        AplicacionSistema(root)
        root.mainloop()
    except tk.TclError as error:
        print(f"No se pudo iniciar la interfaz gráfica: {error}")


if __name__ == "__main__":
    main()
