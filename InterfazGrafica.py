"""Interfaz grafica de escritorio: registros manuales y resultados."""

from datetime import datetime
from math import isfinite
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from BackendExcel import BackendExcel
from Configuracio_ambiental import ConfiguracionAmbiental
from Cultivo import Cultivo
from Medicion import Medicion
from sistema_monitoreo import SistemaMonitoreo


class InterfazGrafica:
    def __init__(self, ventana):
        self.ventana = ventana
        self.backend = BackendExcel()
        self.id_cultivo = None
        self.id_medicion = None
        self._cargar_modelo()

        ventana.title("Sistema de Monitoreo para cultivos")
        ventana.geometry("1050x730")
        ventana.minsize(800, 610)
        ventana.configure(bg="#f5f9f6")

        estilo = ttk.Style()
        if "clam" in estilo.theme_names():
            estilo.theme_use("clam")
        estilo.configure("Treeview", rowheight=27, font=("Arial", 10))
        estilo.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        estilo.configure("TNotebook.Tab", padding=(14, 8), font=("Arial", 10))
        estilo.configure("TLabelframe.Label", font=("Arial", 10, "bold"))

        menu = tk.Menu(ventana)
        archivo = tk.Menu(menu, tearoff=0)
        archivo.add_command(label="Exportar copia del Excel", command=self.exportar_excel)
        archivo.add_separator()
        archivo.add_command(label="Salir", command=ventana.destroy)
        menu.add_cascade(label="Archivo", menu=archivo)
        ventana.config(menu=menu)

        contenedor = ttk.Frame(ventana, padding=15)
        contenedor.pack(fill="both", expand=True)
        ttk.Label(contenedor, text="SISTEMA DE MONITOREO PARA CULTIVOS",
                  font=("Arial", 18, "bold"), foreground="#1b6b4e").pack(anchor="w")
        ttk.Label(contenedor,
                  text="Registro manual de cultivos, mediciones, alertas y recomendaciones").pack(
            anchor="w", pady=(4, 12))

        self.pestanas = ttk.Notebook(contenedor)
        self.pestanas.pack(fill="both", expand=True)
        self.tab_cultivos = ttk.Frame(self.pestanas, padding=12)
        self.tab_mediciones = ttk.Frame(self.pestanas, padding=12)
        self.tab_configuracion = ttk.Frame(self.pestanas, padding=12)
        self.tab_resumen = ttk.Frame(self.pestanas, padding=12)
        for titulo, pagina in (
            ("Cultivos", self.tab_cultivos),
            ("Mediciones", self.tab_mediciones),
            ("Rangos", self.tab_configuracion),
            ("Resumen", self.tab_resumen),
        ):
            self.pestanas.add(pagina, text=titulo)

        self._crear_cultivos()
        self._crear_mediciones()
        self._crear_configuracion()
        self._crear_resumen()
        self.pestanas.bind("<<NotebookTabChanged>>", lambda evento: self.actualizar_resumen())
        self.actualizar_tablas()

    def _cargar_modelo(self):
        rangos = self.backend.leer_configuracion()
        self.configuracion = (
            ConfiguracionAmbiental(
                rangos["temperatura_min"], rangos["temperatura_max"],
                rangos["humedad_min"], rangos["humedad_max"])
            if rangos else None
        )
        self.sistema = SistemaMonitoreo(self.configuracion)
        for registro in self.backend.listar_cultivos():
            self.sistema.registrar_cultivo(Cultivo(
                registro["id"], registro["nombre"],
                registro["tipo_planta"], registro["ubicacion"]))
        for registro in self.backend.listar_mediciones():
            self.sistema.registrar_medicion(
                registro["id_cultivo"],
                Medicion(registro["temperatura"], registro["humedad"], registro["fecha_hora"]))

    @staticmethod
    def _entrada(padre, titulo, fila, columna=0):
        ttk.Label(padre, text=titulo).grid(row=fila, column=columna, padx=5, pady=6, sticky="w")
        entrada = ttk.Entry(padre, width=24)
        entrada.grid(row=fila, column=columna + 1, padx=5, pady=6, sticky="w")
        return entrada

    @staticmethod
    def _tabla(padre, columnas, titulos, altura=10):
        tabla = ttk.Treeview(padre, columns=columnas, show="headings", height=altura)
        for columna, titulo in zip(columnas, titulos):
            tabla.heading(columna, text=titulo)
            tabla.column(columna, width=100 if columna != "fecha" else 155)
        tabla.pack(fill="both", expand=True, pady=8)
        return tabla

    def _crear_cultivos(self):
        formulario = ttk.LabelFrame(self.tab_cultivos, text="Datos del cultivo", padding=10)
        formulario.pack(fill="x")
        self.nombre = self._entrada(formulario, "Nombre:", 0)
        self.tipo = self._entrada(formulario, "Tipo de planta:", 0, 2)
        self.ubicacion = self._entrada(formulario, "Ubicacion:", 1)
        formulario.columnconfigure(1, weight=1)
        formulario.columnconfigure(3, weight=1)

        acciones = ttk.Frame(self.tab_cultivos)
        acciones.pack(fill="x", pady=8)
        for titulo, accion in (
            ("Registrar", self.registrar_cultivo),
            ("Guardar cambios", self.editar_cultivo),
            ("Eliminar", self.eliminar_cultivo),
            ("Ver detalle", self.ver_detalle),
            ("Limpiar", self.limpiar_cultivo),
        ):
            ttk.Button(acciones, text=titulo, command=accion).pack(side="left", padx=3)
        ttk.Label(self.tab_cultivos, text="Selecciona una fila para modificarla:").pack(anchor="w")
        self.tabla_cultivos = self._tabla(
            self.tab_cultivos, ("id", "nombre", "tipo", "ubicacion"),
            ("ID", "Cultivo", "Tipo", "Ubicacion"))
        self.tabla_cultivos.bind("<<TreeviewSelect>>", self.seleccionar_cultivo)

    def _crear_mediciones(self):
        formulario = ttk.LabelFrame(self.tab_mediciones, text="Nueva medicion manual", padding=10)
        formulario.pack(fill="x")
        ttk.Label(formulario, text="Cultivo:").grid(row=0, column=0, sticky="w", padx=5)
        self.cultivo_combo = ttk.Combobox(formulario, state="readonly", width=30)
        self.cultivo_combo.grid(row=0, column=1, sticky="w", padx=5, pady=6)
        self.temperatura = self._entrada(formulario, "Temperatura (°C):", 1)
        self.humedad = self._entrada(formulario, "Humedad (%):", 1, 2)
        formulario.columnconfigure(1, weight=1)
        formulario.columnconfigure(3, weight=1)

        acciones = ttk.Frame(self.tab_mediciones)
        acciones.pack(fill="x", pady=8)
        for titulo, accion in (
            ("Registrar medicion", self.registrar_medicion),
            ("Actualizar", self.editar_medicion),
            ("Eliminar", self.eliminar_medicion),
            ("Limpiar", self.limpiar_medicion),
        ):
            ttk.Button(acciones, text=titulo, command=accion).pack(side="left", padx=3)
        self.solo_alertas = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.tab_mediciones, text="Mostrar solo mediciones en alerta",
                        variable=self.solo_alertas, command=self.actualizar_mediciones).pack(
            anchor="w", pady=5)
        self.tabla_mediciones = self._tabla(
            self.tab_mediciones, ("id", "cultivo", "temperatura", "humedad", "fecha", "estado"),
            ("ID", "Cultivo", "Temp (°C)", "Humedad (%)", "Fecha", "Estado"))
        self.tabla_mediciones.tag_configure("ALERTA", background="#fff0ee", foreground="#9c2424")
        self.tabla_mediciones.tag_configure("NORMAL", background="#eaf7ee", foreground="#17673e")
        self.tabla_mediciones.tag_configure("SIN RANGOS", background="#fff6dd", foreground="#856018")
        self.tabla_mediciones.bind("<<TreeviewSelect>>", self.seleccionar_medicion)

    def _crear_configuracion(self):
        ttk.Label(self.tab_configuracion,
                  text="Ingresa los limites de tu cultivo;",
                  wraplength=750).pack(anchor="w", pady=12)
        formulario = ttk.LabelFrame(self.tab_configuracion, text="Rangos ambientales", padding=12)
        formulario.pack(fill="x")
        self.temp_min = self._entrada(formulario, "Temperatura minima:", 0)
        self.temp_max = self._entrada(formulario, "Temperatura maxima:", 1)
        self.hum_min = self._entrada(formulario, "Humedad minima:", 2)
        self.hum_max = self._entrada(formulario, "Humedad maxima:", 3)
        ttk.Button(self.tab_configuracion, text="Guardar rangos en Excel",
                   command=self.guardar_rangos).pack(anchor="w", pady=12)
        ttk.Label(self.tab_configuracion,
                  text="Importante: el usuario debe definir rangos adecuados para su cultivo.").pack(anchor="w")
        if self.configuracion:
            valores = (*self.configuracion.consultar_temperatura(),
                       *self.configuracion.consultar_humedad())
            for entrada, valor in zip(
                (self.temp_min, self.temp_max, self.hum_min, self.hum_max), valores
            ):
                entrada.insert(0, str(valor))

    def _crear_resumen(self):
        tarjetas = ttk.Frame(self.tab_resumen)
        tarjetas.pack(fill="x", pady=(3, 13))
        self.indicadores = {}
        for clave, titulo, fondo, texto in (
            ("cultivos", "CULTIVOS REGISTRADOS", "#e4f3eb", "#21684b"),
            ("mediciones", "MEDICIONES GUARDADAS", "#e7f1fc", "#215f92"),
            ("alertas", "ALERTAS REGISTRADAS", "#fdebe9", "#a52d2c"),
        ):
            tarjeta = tk.Frame(tarjetas, bg=fondo, padx=15, pady=9)
            tarjeta.pack(side="left", fill="both", expand=True, padx=5)
            tk.Label(tarjeta, text=titulo, bg=fondo, fg=texto,
                     font=("Arial", 9, "bold")).pack(anchor="w")
            numero = tk.Label(tarjeta, text="0", bg=fondo, fg=texto,
                              font=("Arial", 25, "bold"))
            numero.pack(anchor="w", pady=(2, 0))
            self.indicadores[clave] = numero

        filtros = ttk.Frame(self.tab_resumen)
        filtros.pack(fill="x", pady=(0, 9))
        ttk.Label(filtros, text="Visualizar mediciones de:").pack(side="left", padx=(0, 9))
        self.selector_grafica = ttk.Combobox(filtros, state="readonly", width=35)
        self.selector_grafica.pack(side="left")
        self.selector_grafica.bind("<<ComboboxSelected>>",
                                    lambda evento: self.dibujar_grafica())
        self.opciones_grafica = {"Todos los cultivos": None}

        ttk.Label(self.tab_resumen, text="EVOLUCION DE TEMPERATURA Y HUMEDAD",
                  font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.grafica = tk.Canvas(self.tab_resumen, bg="white", height=250,
                                 highlightbackground="#dce8e1", highlightthickness=1)
        self.grafica.pack(fill="x", pady=(0, 12))
        self.grafica.bind("<Configure>", lambda evento: self.dibujar_grafica())
        ttk.Label(self.tab_resumen, text="ALERTAS DEL SISTEMA",
                  font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.tabla_alertas = self._tabla(self.tab_resumen, ("cultivo", "alerta"),
                                        ("Cultivo", "Descripcion de alerta"), altura=6)
        self.tabla_alertas.tag_configure("alerta", background="#fff0ee", foreground="#9c2424")
        self.tabla_alertas.tag_configure("normal", background="#eaf7ee", foreground="#17673e")

    @staticmethod
    def _numero(entrada, titulo):
        try:
            numero = float(entrada.get().strip().replace(",", "."))
            if not isfinite(numero):
                raise ValueError()
            return numero
        except ValueError as error:
            raise ValueError(f"{titulo}: ingresa un numero valido.") from error

    def _datos_cultivo(self):
        datos = (self.nombre.get().strip(), self.tipo.get().strip(),
                 self.ubicacion.get().strip())
        if not all(datos):
            raise ValueError("Debes completar todos los campos del cultivo.")
        return datos

    def registrar_cultivo(self):
        try:
            identificador = self.backend.agregar_cultivo(*self._datos_cultivo())
            self.actualizar_tablas()
            self.limpiar_cultivo()
            messagebox.showinfo("Registro exitoso", f"Cultivo agregado con ID {identificador}.")
        except (ValueError, OSError) as error:
            messagebox.showerror("Error", str(error))

    def editar_cultivo(self):
        if self.id_cultivo is None:
            messagebox.showwarning("Seleccion", "Selecciona un cultivo de la tabla.")
            return
        try:
            self.backend.actualizar_cultivo(self.id_cultivo, *self._datos_cultivo())
            self.actualizar_tablas()
            messagebox.showinfo("Actualizado", "Cambios guardados en Excel.")
        except (ValueError, OSError) as error:
            messagebox.showerror("Error", str(error))

    def eliminar_cultivo(self):
        if self.id_cultivo is None:
            messagebox.showwarning("Seleccion", "Selecciona un cultivo de la tabla.")
            return
        if not messagebox.askyesno("Confirmacion",
                                   "Se borrara el cultivo y sus mediciones. ¿Continuar?"):
            return
        try:
            self.backend.eliminar_cultivo(self.id_cultivo)
            self.actualizar_tablas()
            self.limpiar_cultivo()
        except (ValueError, OSError) as error:
            messagebox.showerror("Error", str(error))

    def limpiar_cultivo(self):
        self.id_cultivo = None
        for entrada in (self.nombre, self.tipo, self.ubicacion):
            entrada.delete(0, tk.END)
        for fila in self.tabla_cultivos.selection():
            self.tabla_cultivos.selection_remove(fila)

    def seleccionar_cultivo(self, evento=None):
        seleccion = self.tabla_cultivos.selection()
        if not seleccion:
            return
        datos = self.tabla_cultivos.item(seleccion[0], "values")
        self.id_cultivo = int(datos[0])
        for entrada, valor in zip((self.nombre, self.tipo, self.ubicacion), datos[1:]):
            entrada.delete(0, tk.END)
            entrada.insert(0, valor)

    def ver_detalle(self):
        if self.id_cultivo is None:
            messagebox.showwarning("Seleccion", "Selecciona un cultivo.")
            return
        cultivo = self.sistema.buscar_cultivo(self.id_cultivo)
        secundaria = tk.Toplevel(self.ventana)
        secundaria.title("Detalle del cultivo")
        secundaria.geometry("390x240")
        for texto in (
            f"Cultivo: {cultivo.consultar_nombre()}",
            f"Ubicacion: {cultivo.consultar_ubicacion()}",
            f"Mediciones: {len(cultivo.consultar_historial())}",
            f"Alertas: {len(cultivo.consultar_alertas())}",
        ):
            ttk.Label(secundaria, text=texto, font=("Arial", 11)).pack(anchor="w", padx=20, pady=8)
        ttk.Button(secundaria, text="Cerrar", command=secundaria.destroy).pack(pady=9)

    def _id_combo(self):
        texto = self.cultivo_combo.get()
        if texto not in self.opciones_cultivos:
            raise ValueError("Primero selecciona un cultivo registrado.")
        return self.opciones_cultivos[texto]

    def _medicion_desde_formulario(self):
        return Medicion(self._numero(self.temperatura, "Temperatura"),
                        self._numero(self.humedad, "Humedad"))

    def registrar_medicion(self):
        try:
            if self.configuracion is None:
                raise ValueError("Primero guarda los rangos en la pestana Rangos.")
            id_cultivo = self._id_combo()
            medicion = self._medicion_desde_formulario()
            self.backend.agregar_medicion(
                id_cultivo, medicion.consultar_temperatura(), medicion.consultar_humedad())
            resultado = self.sistema.evaluar_medicion(medicion)
            self.actualizar_tablas()
            self.limpiar_medicion()
            texto = (f"Temperatura: {resultado['temperatura']}\n"
                     f"Humedad: {resultado['humedad']}\n")
            if "ADECUADA" != resultado["temperatura"]:
                texto += "\nRecomendacion: revisar la temperatura del cultivo."
            if "ADECUADA" != resultado["humedad"]:
                texto += "\nRecomendacion: revisar las condiciones de humedad."
            if all(valor == "ADECUADA" for valor in resultado.values()):
                texto += "\nRecomendacion: mantener el monitoreo habitual."
            messagebox.showinfo("Resultado del analisis", texto)
        except (ValueError, OSError) as error:
            messagebox.showerror("Error de medicion", str(error))

    def editar_medicion(self):
        if self.id_medicion is None:
            messagebox.showwarning("Seleccion", "Selecciona una medicion.")
            return
        try:
            medicion = self._medicion_desde_formulario()
            self.backend.actualizar_medicion(
                self.id_medicion, medicion.consultar_temperatura(),
                medicion.consultar_humedad())
            self.actualizar_tablas()
            messagebox.showinfo("Actualizado", "Medicion actualizada en Excel.")
        except (ValueError, OSError) as error:
            messagebox.showerror("Error", str(error))

    def eliminar_medicion(self):
        if self.id_medicion is None:
            messagebox.showwarning("Seleccion", "Selecciona una medicion.")
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar esta medicion?"):
            return
        try:
            self.backend.eliminar_medicion(self.id_medicion)
            self.actualizar_tablas()
            self.limpiar_medicion()
        except (ValueError, OSError) as error:
            messagebox.showerror("Error", str(error))

    def limpiar_medicion(self):
        self.id_medicion = None
        for entrada in (self.temperatura, self.humedad):
            entrada.delete(0, tk.END)
        for fila in self.tabla_mediciones.selection():
            self.tabla_mediciones.selection_remove(fila)

    def seleccionar_medicion(self, evento=None):
        seleccion = self.tabla_mediciones.selection()
        if not seleccion:
            return
        datos = self.tabla_mediciones.item(seleccion[0], "values")
        self.id_medicion = int(datos[0])
        for entrada, valor in zip((self.temperatura, self.humedad), datos[2:4]):
            entrada.delete(0, tk.END)
            entrada.insert(0, valor)
        registro = next(m for m in self.backend.listar_mediciones()
                        if m["id"] == self.id_medicion)
        for nombre_combo, id_cultivo in self.opciones_cultivos.items():
            if id_cultivo == registro["id_cultivo"]:
                self.cultivo_combo.set(nombre_combo)
                break

    def guardar_rangos(self):
        try:
            valores = [
                self._numero(campo, titulo) for campo, titulo in (
                    (self.temp_min, "Temperatura minima"),
                    (self.temp_max, "Temperatura maxima"),
                    (self.hum_min, "Humedad minima"),
                    (self.hum_max, "Humedad maxima"),
                )
            ]
            ConfiguracionAmbiental(*valores)
            self.backend.guardar_configuracion(*valores)
            self.actualizar_tablas()
            messagebox.showinfo("Configuracion", "Rangos guardados en Excel.")
        except (ValueError, OSError) as error:
            messagebox.showerror("Error de configuracion", str(error))

    def actualizar_tablas(self):
        self._cargar_modelo()
        cultivos = self.backend.listar_cultivos()
        self.opciones_cultivos = {
            f"{c['id']} - {c['nombre']}": c["id"] for c in cultivos
        }
        opcion_previa = self.cultivo_combo.get()
        self.cultivo_combo["values"] = list(self.opciones_cultivos)
        if opcion_previa in self.opciones_cultivos:
            self.cultivo_combo.set(opcion_previa)
        elif self.opciones_cultivos:
            self.cultivo_combo.current(0)
        else:
            self.cultivo_combo.set("")

        self._actualizar_opciones_grafica(cultivos)
        self.tabla_cultivos.delete(*self.tabla_cultivos.get_children())
        for c in cultivos:
            self.tabla_cultivos.insert(
                "", "end", values=(c["id"], c["nombre"], c["tipo_planta"], c["ubicacion"]))
        self.id_cultivo = None
        self.actualizar_mediciones()
        self.actualizar_resumen()

    def _actualizar_opciones_grafica(self, cultivos):
        # Mantiene la seleccion por ID incluso cuando el cultivo cambia de nombre.
        seleccion_anterior = self.opciones_grafica.get(self.selector_grafica.get())
        self.opciones_grafica = {"Todos los cultivos": None}
        self.opciones_grafica.update({
            f"{cultivo['id']} - {cultivo['nombre']}": cultivo["id"]
            for cultivo in cultivos
        })
        self.selector_grafica["values"] = list(self.opciones_grafica)
        opcion = next(
            (nombre for nombre, identificador in self.opciones_grafica.items()
             if identificador == seleccion_anterior),
            "Todos los cultivos",
        )
        self.selector_grafica.set(opcion)

    def _estado(self, registro):
        if self.configuracion is None:
            return "SIN RANGOS"
        medicion = Medicion(registro["temperatura"], registro["humedad"])
        resultado = self.sistema.evaluar_medicion(medicion)
        return "NORMAL" if all(x == "ADECUADA" for x in resultado.values()) else "ALERTA"

    def actualizar_mediciones(self):
        self.tabla_mediciones.delete(*self.tabla_mediciones.get_children())
        nombres = {c["id"]: c["nombre"] for c in self.backend.listar_cultivos()}
        for m in self.backend.listar_mediciones():
            estado = self._estado(m)
            if self.solo_alertas.get() and estado != "ALERTA":
                continue
            fecha = m["fecha_hora"]
            texto_fecha = fecha.strftime("%d/%m/%Y %H:%M") if isinstance(
                fecha, datetime) else str(fecha)
            self.tabla_mediciones.insert("", "end", tags=(estado,), values=(
                m["id"], nombres.get(m["id_cultivo"], "Sin cultivo"),
                m["temperatura"], m["humedad"], texto_fecha, estado))
        self.id_medicion = None

    def actualizar_resumen(self):
        cultivos = self.sistema.consultar_cultivos()
        total_alertas = sum(len(c.consultar_alertas()) for c in cultivos)
        self.indicadores["cultivos"].configure(text=str(len(cultivos)))
        self.indicadores["mediciones"].configure(text=str(len(self.backend.listar_mediciones())))
        self.indicadores["alertas"].configure(text=str(total_alertas))
        self.tabla_alertas.delete(*self.tabla_alertas.get_children())
        for cultivo in cultivos:
            for alerta in cultivo.consultar_alertas():
                self.tabla_alertas.insert("", "end", tags=("alerta",), values=(
                    cultivo.consultar_nombre(), alerta.consultar_mensaje()))
        if total_alertas == 0:
            descripcion = ("Sin alertas en el historial." if self.configuracion else
                           "Configura los rangos para activar el analisis.")
            self.tabla_alertas.insert("", "end", tags=("normal",),
                                     values=("Sin alertas", descripcion))
        self.dibujar_grafica()

    def dibujar_grafica(self):
        lienzo = self.grafica
        lienzo.delete("all")
        ancho = max(lienzo.winfo_width(), 650)
        id_cultivo = self.opciones_grafica.get(self.selector_grafica.get())
        datos = self.backend.listar_mediciones(id_cultivo)[-12:]
        if not datos:
            mensaje = ("Selecciona otro cultivo o registra su primera medicion."
                       if id_cultivo is not None else
                       "Registra mediciones para ver la evolucion de los cultivos.")
            lienzo.create_text(ancho / 2, 125,
                              text=mensaje,
                              fill="#667b70", font=("Arial", 11))
            return

        nombres = {c["id"]: c["nombre"] for c in self.backend.listar_cultivos()}
        varios_cultivos = len({d["id_cultivo"] for d in datos}) > 1
        texto_cantidad = f"{len(datos)} medicion(es) registrada(s)"
        if len(datos) == 1:
            texto_cantidad += " - registra otra para ver la tendencia"
        elif id_cultivo is None and varios_cultivos:
            texto_cantidad += " - lineas independientes por cultivo"
        lienzo.create_text(ancho - 20, 15, text=texto_cantidad,
                          anchor="e", fill="#62746d", font=("Arial", 9))

        for banda, (clave, titulo, color) in enumerate((
            ("temperatura", "Temperatura (°C)", "#cc6d30"),
            ("humedad", "Humedad (%)", "#277bb7"),
        )):
            arriba = 43 + 113 * banda
            abajo = arriba + 58
            valores = [float(d[clave]) for d in datos]
            minimo, maximo = min(valores), max(valores)
            margen = max((maximo - minimo) * .20, 1)
            minimo -= margen
            maximo += margen
            lienzo.create_text(16, arriba - 22, text=titulo, fill=color,
                              anchor="w", font=("Arial", 10, "bold"))
            for altura in (arriba, (arriba + abajo) / 2, abajo):
                lienzo.create_line(67, altura, ancho - 24, altura,
                                  fill="#e7ece8", dash=(3, 4))
            lienzo.create_text(58, arriba, text=f"{maximo:.1f}", anchor="e", fill="#69746d")
            lienzo.create_text(58, abajo, text=f"{minimo:.1f}", anchor="e", fill="#69746d")
            puntos = []
            puntos_por_cultivo = {}
            for indice, valor in enumerate(valores):
                x = (ancho / 2 if len(valores) == 1 else
                     88 + indice * (ancho - 160) / (len(valores) - 1))
                y = abajo - (valor - minimo) / (maximo - minimo) * (abajo - arriba)
                puntos.extend((x, y))
                puntos_por_cultivo.setdefault(datos[indice]["id_cultivo"], []).extend((x, y))
            # Nunca unir valores de cultivos diferentes con una misma linea.
            for puntos_del_cultivo in puntos_por_cultivo.values():
                if len(puntos_del_cultivo) >= 4:
                    lienzo.create_line(*puntos_del_cultivo, fill=color, width=3,
                                      smooth=False)
            for indice, valor in enumerate(valores):
                x, y = puntos[2 * indice:2 * indice + 2]
                lienzo.create_oval(x - 4, y - 4, x + 4, y + 4,
                                  fill=color, outline="white", width=1)
                # Etiquetar los puntos sin saturar la grafica con demasiados numeros.
                if len(valores) <= 6 or indice in (0, len(valores) - 1):
                    unidad = "°C" if clave == "temperatura" else "%"
                    etiqueta_y = y + 20 if y < arriba + 24 else y - 12
                    lienzo.create_text(x, etiqueta_y, text=f"{valor:.1f} {unidad}",
                                      fill=color, font=("Arial", 9, "bold"))

                # En la vista general se identifica a que cultivo pertenece cada punto.
                if (banda == 1 and id_cultivo is None and varios_cultivos and
                        (len(datos) <= 6 or indice in (0, len(datos) - 1))):
                    nombre = nombres.get(datos[indice]["id_cultivo"], "Cultivo")
                    lienzo.create_text(x, 230, text=nombre[:15], fill="#5c6d65",
                                      font=("Arial", 8))

        if datos:
            ultima_fecha = datos[-1]["fecha_hora"]
            if isinstance(ultima_fecha, datetime):
                texto_fecha = ultima_fecha.strftime("Ultima medicion: %d/%m/%Y %H:%M")
                lienzo.create_text(ancho - 20, 244, text=texto_fecha, anchor="e",
                                  fill="#667b70", font=("Arial", 9))

    def exportar_excel(self):
        ruta = filedialog.asksaveasfilename(
            title="Exportar copia", defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")], initialfile="copia_datos_cultivos.xlsx")
        if ruta:
            try:
                self.backend.exportar_copia(ruta)
                messagebox.showinfo("Exportacion", "Se guardo la copia del Excel.")
            except (ValueError, OSError) as error:
                messagebox.showerror("Error", str(error))
