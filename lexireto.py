import tkinter as tk
from tkinter import messagebox
import random
import string
from collections import defaultdict
import time

class LexiRetoGame:
    def __init__(self, root, archivo_palabras="castellano sin tildes.txt"):
        self.root = root
        self.root.title("Juego de Palabras")
        self.root.geometry("750x700")
        self.hex_color = "#f4c842"

        self.archivo_palabras = archivo_palabras
        self.diccionario_palabras = self.cargar_palabras()

        self.palabra_actual = ""
        self.palabras_encontradas = set()
        self.heptacracks_encontrados = 0
        self.puntuacion = 0
        self.tiempo_inicio = 0.0
        self.tiempo_transcurrido = 0.0
        self.running = False

        self.letras_disponibles = self.generar_letras_validas()
        self.letras_disponibles_lower = [l.lower() for l in self.letras_disponibles]
        self.letra_central = self.letras_disponibles[3].lower()

        self.palabras_validas = self.encontrar_todas_las_validas()
        self.total_heptacracks_posibles = len(self.encontrar_heptacracks_posibles())

        self.letra_por_inicio = defaultdict(list)
        for palabra in self.palabras_validas:
            letra_inicial = palabra[0].upper()
            self.letra_por_inicio[letra_inicial].append(palabra)

        self.botones_letras = {}
        self.textos_por_inicio = {}

        self.setup_gui()
        self.iniciar_temporizador()

    def cargar_palabras(self):
        try:
            with open(self.archivo_palabras, "r", encoding="utf-8") as f:
                return set(line.strip().lower() for line in f)
        except FileNotFoundError:
            messagebox.showerror("Error", f"No se encontró el archivo: {self.archivo_palabras}")
            return set()

    def generar_letras_validas(self):
        while True:
            letras = random.sample(string.ascii_uppercase, 7)
            vocales = [l for l in letras if l in "AEIOU"]
            if len(vocales) >= 2:
                return letras

    def calcular_puntos(self, palabra):
        longitud = len(palabra)
        if longitud == 3:
            return 1
        elif longitud == 4:
            return 2
        elif longitud >= 5:
            return longitud
        return 0

    def es_palabra_valida(self, palabra):
        return (
            palabra in self.diccionario_palabras and
            self.letra_central in palabra and
            len(palabra) >= 3 and
            all(letra in self.letras_disponibles_lower for letra in palabra)
        )

    def agregar_letra(self, letra):
        self.palabra_actual += letra
        self.palabra_label.config(text=self.palabra_actual)

    def borrar_letra(self):
        self.palabra_actual = self.palabra_actual[:-1]
        self.palabra_label.config(text=self.palabra_actual)

    def verificar_palabra(self):
        palabra = self.palabra_actual.lower()

        if palabra in self.palabras_encontradas:
            self.resultado_label.config(text="❗", fg="orange")
        elif self.es_palabra_valida(palabra):
            self.resultado_label.config(text="✔", fg="green")
            self.palabras_encontradas.add(palabra)
            puntos = self.calcular_puntos(palabra)
            self.puntuacion += puntos
            if len(palabra) == 7 and all(letra in palabra for letra in self.letras_disponibles_lower):
                self.puntuacion += 10
                self.heptacracks_encontrados += 1
                self.actualizar_marcador_heptacracks()
        else:
            self.resultado_label.config(text="❌", fg="red")

        self.root.after(1500, lambda: self.resultado_label.config(text=""))
        self.palabra_actual = ""
        self.palabra_label.config(text="")
        self.actualizar_marcador()

    def encontrar_heptacracks_posibles(self):
        return {
            palabra for palabra in self.diccionario_palabras
            if len(palabra) == 7 and all(letra in palabra for letra in self.letras_disponibles_lower)
            and self.letra_central in palabra
        }

    def encontrar_todas_las_validas(self):
        return {
            palabra for palabra in self.diccionario_palabras
            if self.letra_central in palabra and
               len(palabra) >= 3 and
               all(letra in self.letras_disponibles_lower for letra in palabra)
        }

    def actualizar_marcador(self):
        total = len(self.palabras_validas)
        encontradas = len(self.palabras_encontradas)
        self.texto_marcador.set(f"Tus palabras: {encontradas} / {total} ({(encontradas/total)*100:.2f}%) - "
                                 f"Puntos: {self.puntuacion} - Tiempo: {self.formatear_tiempo(self.tiempo_transcurrido)}")

        for letra in self.letra_por_inicio:
            validas = self.letra_por_inicio[letra]
            encontradas_inicial = [p for p in self.palabras_encontradas if p.startswith(letra.lower())]
            self.textos_por_inicio[letra].set(f"Empiezan por: {letra}  {len(encontradas_inicial)} / {len(validas)}")

    def actualizar_marcador_heptacracks(self):
        self.texto_heptacracks.set(f"Heptacracks\t{self.heptacracks_encontrados} / {self.total_heptacracks_posibles}")

    def mostrar_todas_palabras(self):
        top_level = tk.Toplevel(self.root)
        top_level.title("Todas las palabras válidas")
        text_area = tk.Text(top_level, width=40, height=20)
        text_area.pack(padx=10, pady=10)
        palabras_ordenadas = sorted(list(self.palabras_validas))
        text_area.insert(tk.END, "\n".join(palabras_ordenadas))
        text_area.config(state=tk.DISABLED)

    def mostrar_como_jugar(self):
        instrucciones = """
        ¡Bienvenido al Lexi Reto!

        Cómo jugar:
        - Forma palabras de al menos 3 letras utilizando las 7 letras mostradas.
        - Cada palabra debe incluir la letra central (resaltada).
        - Puedes repetir las letras cuantas veces quieras dentro de una palabra.
        - No se admiten nombres propios, plurales ni formas verbales conjugadas (solo infinitivos).

        Puntuación:
        - Palabras de 3 letras: 1 punto
        - Palabras de 4 letras: 2 puntos
        - Palabras de 5 o más letras: Tantos puntos como letras tenga la palabra.
        - ¡Heptacracks! (palabras que usan las 7 letras): 10 puntos extra.
        """
        messagebox.showinfo("Cómo se juega", instrucciones)

    def formatear_tiempo(self, segundos):
        minutos = int(segundos // 60)
        segundos_restantes = int(segundos % 60)
        return f"{minutos:02d}:{segundos_restantes:02d}"

    def actualizar_tiempo(self):
        if self.running:
            self.tiempo_transcurrido = time.time() - self.tiempo_inicio
            self.actualizar_marcador()
        self.root.after(1000, self.actualizar_tiempo)

    def iniciar_temporizador(self):
        self.tiempo_inicio = time.time()
        self.running = True
        self.actualizar_tiempo()

    def setup_gui(self):
        posiciones = [
            (1, 1), (1, 2),
            (2, 0), (2, 1), (2, 2),
            (3, 0), (3, 1)
        ]

        for idx, (r, c) in enumerate(posiciones):
            letra = self.letras_disponibles[idx]
            color = self.hex_color if letra.lower() == self.letra_central else "white"
            button = tk.Button(self.root, text=letra, width=6, height=3, bg=color,
                               font=("Helvetica", 16), command=lambda l=letra: self.agregar_letra(l))
            button.grid(row=r, column=c, padx=5, pady=5)
            self.botones_letras[(r, c)] = button

        palabra_frame = tk.Frame(self.root)
        palabra_frame.grid(row=4, column=0, columnspan=3, pady=10)

        self.palabra_label = tk.Label(palabra_frame, text="", font=("Helvetica", 18))
        self.palabra_label.pack(side="left")

        self.resultado_label = tk.Label(palabra_frame, text="", width=2)
        self.resultado_label.pack(side="right")

        botones_accion_frame = tk.Frame(self.root)
        botones_accion_frame.grid(row=5, column=0, columnspan=3, pady=10)
        tk.Button(botones_accion_frame, text="Borrar", width=10, command=self.borrar_letra).pack(side="left")
        tk.Button(botones_accion_frame, text="⟳", width=5, state="disabled").pack(side="left")
        tk.Button(botones_accion_frame, text="Aplicar", width=10, command=self.verificar_palabra).pack(side="left")

        marcador_frame = tk.Frame(self.root)
        marcador_frame.grid(row=0, column=4, rowspan=7, padx=30, sticky="n")

        tk.Label(marcador_frame, text="MARCADOR", font=("Helvetica", 12, "bold")).pack(pady=10)
        self.texto_marcador = tk.StringVar()
        self.texto_marcador.set(f"Tus palabras: 0 / {len(self.palabras_validas)} (0.00%) - Puntos: 0 - Tiempo: 00:00")
        tk.Label(marcador_frame, textvariable=self.texto_marcador).pack()

        self.texto_heptacracks = tk.StringVar()
        self.texto_heptacracks.set(f"Heptacracks\t0 / {self.total_heptacracks_posibles}")
        tk.Label(marcador_frame, textvariable=self.texto_heptacracks).pack()

        for letra in sorted(self.letra_por_inicio.keys()):
            var = tk.StringVar()
            var.set(f"Empiezan por: {letra}  0 / {len(self.letra_por_inicio[letra])}")
            self.textos_por_inicio[letra] = var
            tk.Label(marcador_frame, textvariable=var).pack(anchor="w")

        tk.Button(self.root, text="Cómo se juega", command=self.mostrar_como_jugar).grid(row=6, column=1, pady=10)
        tk.Button(self.root, text="Revelar Palabras", command=self.mostrar_todas_palabras).grid(row=7, column=1, pady=10)

# -------- EJECUCIÓN --------
if __name__ == "__main__":
    root = tk.Tk()
    app = LexiRetoGame(root)
    root.mainloop()
