import tkinter as tk
from tkinter import messagebox
import random
import string
from collections import defaultdict
import time

def cargar_palabras(archivo):
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            return set(line.strip().lower() for line in f)
    except FileNotFoundError:
        messagebox.showerror("Error", f"No se encontró el archivo: {archivo}")
        return set()

def generar_letras_validas():
    """Genera 7 letras únicas con al menos 2 vocales."""
    while True:
        letras = random.sample(string.ascii_uppercase, 7)
        vocales = [l for l in letras if l in "AEIOU"]
        if len(vocales) >= 2:
            return letras

def calcular_puntos(palabra):
    longitud = len(palabra)
    if longitud == 3:
        return 1
    elif longitud == 4:
        return 2
    elif longitud >= 5:
        return longitud
    return 0

def es_palabra_valida(palabra):
    return (
        palabra in diccionario_palabras and
        letra_central in palabra and
        len(palabra) >= 3 and
        all(letra in letras_disponibles_lower for letra in palabra)
    )

def agregar_letra(letra):
    global palabra_actual
    palabra_actual += letra
    palabra_label.config(text=palabra_actual)

def borrar_letra():
    global palabra_actual
    palabra_actual = palabra_actual[:-1]
    palabra_label.config(text=palabra_actual)

def verificar_palabra():
    global palabra_actual, heptacracks_encontrados, puntuacion

    palabra = palabra_actual.lower()

    if palabra in palabras_encontradas:
        resultado_label.config(text="❗", fg="orange", font=("Helvetica", 20))
        root.after(1500, lambda: resultado_label.config(text=""))
    elif es_palabra_valida(palabra):
        resultado_label.config(text="✔", fg="green", font=("Helvetica", 20))
        root.after(1500, lambda: resultado_label.config(text=""))

        palabras_encontradas.add(palabra)
        puntos = calcular_puntos(palabra)
        puntuacion += puntos
        actualizar_marcador()
        if len(palabra) == 7 and all(letra in palabra for letra in letras_disponibles_lower):
            puntuacion += 10
            heptacracks_encontrados += 1
            actualizar_marcador_heptacracks()
    else:
        resultado_label.config(text="❌", fg="red", font=("Helvetica", 20))
        root.after(1500, lambda: resultado_label.config(text=""))

    palabra_actual = ""
    palabra_label.config(text="")

def encontrar_heptacracks_posibles():
    return {
        palabra for palabra in diccionario_palabras
        if len(palabra) == 7 and all(letra in palabra for letra in letras_disponibles_lower) and letra_central in palabra
    }

def encontrar_todas_las_validas():
    return {
        palabra for palabra in diccionario_palabras
        if letra_central in palabra and
           len(palabra) >= 3 and
           all(letra in letras_disponibles_lower for letra in palabra)
    }

def actualizar_marcador():
    total = len(palabras_validas)
    encontradas = len(palabras_encontradas)
    texto_marcador.set(f"Tus palabras: {encontradas} / {total} ({(encontradas/total)*100:.2f}%) - Puntos: {puntuacion} - Tiempo: {formatear_tiempo(tiempo_transcurrido)}")

    # Actualiza contador por letra inicial
    for letra in letra_por_inicio:
        validas = letra_por_inicio[letra]
        encontradas_inicial = [p for p in palabras_encontradas if p.startswith(letra.lower())]
        textos_por_inicio[letra].set(f"Empiezan por: {letra}  {len(encontradas_inicial)} / {len(validas)}")

def actualizar_marcador_heptacracks():
    texto_heptacracks.set(f"Heptacracks\t{heptacracks_encontrados} / {total_heptacracks_posibles}")

def mostrar_todas_palabras():
    top_level = tk.Toplevel(root)
    top_level.title("Todas las palabras válidas")
    text_area = tk.Text(top_level, width=40, height=20)
    text_area.pack(padx=10, pady=10)
    palabras_ordenadas = sorted(list(palabras_validas))
    text_area.insert(tk.END, "\n".join(palabras_ordenadas))
    text_area.config(state=tk.DISABLED)

def mostrar_como_jugar():
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

    ¡Diviértete encontrando todas las palabras posibles!
    """
    messagebox.showinfo("Cómo se juega", instrucciones)

def formatear_tiempo(segundos):
    minutos = int(segundos // 60)
    segundos_restantes = int(segundos % 60)
    return f"{minutos:02d}:{segundos_restantes:02d}"

def actualizar_tiempo():
    global tiempo_inicio, tiempo_transcurrido, running
    if running:
        tiempo_transcurrido = time.time() - tiempo_inicio
        actualizar_marcador()
    root.after(1000, actualizar_tiempo) # Actualizar cada segundo

def iniciar_temporizador():
    global tiempo_inicio, running
    tiempo_inicio = time.time()
    running = True
    actualizar_tiempo()

def detener_temporizador():
    global running
    running = False

# ---------------- CONFIGURACIÓN INICIAL ---------------- #

archivo_palabras = "castellano sin tildes.txt"
diccionario_palabras = cargar_palabras(archivo_palabras)
palabra_actual = ""
palabras_encontradas = set()
heptacracks_encontrados = 0
puntuacion = 0
tiempo_inicio = 0.0
tiempo_transcurrido = 0.0
running = False

root = tk.Tk()
root.title("Juego de Palabras")
root.geometry("750x700") # Volver a la altura original si no necesitas espacio extra
hex_color = "#f4c842"
letras_disponibles = generar_letras_validas()
letras_disponibles_lower = [l.lower() for l in letras_disponibles]
letra_central = letras_disponibles[3].lower()  # Letra obligatoria

palabras_validas = encontrar_todas_las_validas()
total_heptacracks_posibles = len(encontrar_heptacracks_posibles())

# Clasifica palabras válidas por letra inicial
letra_por_inicio = defaultdict(list)
for palabra in palabras_validas:
    letra_inicial = palabra[0].upper()
    letra_por_inicio[letra_inicial].append(palabra)

# Distribución tipo panal
posiciones = [
    (1, 1), (1, 2),
    (2, 0), (2, 1), (2, 2),
    (3, 0), (3, 1)
]

botones_letras = {}
for idx, (r, c) in enumerate(posiciones):
    letra = letras_disponibles[idx]
    color = hex_color if letra.lower() == letra_central else "white"
    button = tk.Button(root, text=letra, width=6, height=3,
                       bg=color, relief="raised", font=("Helvetica", 16),
                       command=lambda l=letra: agregar_letra(l))
    button.grid(row=r, column=c, padx=5, pady=5)
    botones_letras[(r, c)] = button

# Palabra actual
palabra_frame = tk.Frame(root)
palabra_frame.grid(row=4, column=0, columnspan=3, pady=10)

palabra_label = tk.Label(palabra_frame, text="", font=("Helvetica", 18))
palabra_label.pack(side="left")

resultado_label = tk.Label(palabra_frame, text="", width=2)
resultado_label.pack(side="right")

# Botones de acción
botones_accion_frame = tk.Frame(root)
botones_accion_frame.grid(row=5, column=0, columnspan=3, pady=10)

tk.Button(botones_accion_frame, text="Borrar", width=10, command=borrar_letra).pack(side="left", padx=(0, 5))
tk.Button(botones_accion_frame, text="⟳", width=5, state="disabled").pack(side="left", padx=5)
tk.Button(botones_accion_frame, text="Aplicar", width=10, command=verificar_palabra).pack(side="left", padx=(5, 0))

# Marcador general
marcador_frame = tk.Frame(root)
marcador_frame.grid(row=0, column=4, rowspan=7, padx=30, sticky="n") # Volver al rowspan original

tk.Label(marcador_frame, text="MARCADOR", font=("Helvetica", 12, "bold")).pack(pady=10)
texto_marcador = tk.StringVar()
texto_marcador.set(f"Tus palabras: 0 / {len(palabras_validas)} (0.00%) - Puntos: {puntuacion} - Tiempo: 00:00")
tk.Label(marcador_frame, textvariable=texto_marcador, anchor="w", justify="left").pack(fill="x")

# Marcador Heptacracks
texto_heptacracks = tk.StringVar()
texto_heptacracks.set(f"Heptacracks\t{heptacracks_encontrados} / {total_heptacracks_posibles}")
tk.Label(marcador_frame, textvariable=texto_heptacracks, anchor="w", justify="left").pack(fill="x")

# Letras por inicio
textos_por_inicio = {}
for letra in sorted(letra_por_inicio.keys()):
    var = tk.StringVar()
    var.set(f"Empiezan por: {letra}  0 / {len(letra_por_inicio[letra])}")
    textos_por_inicio[letra] = var
    tk.Label(marcador_frame, textvariable=var, anchor="w", justify="left").pack(fill="x")

# Botón ayuda
tk.Button(root, text="Cómo se juega", command=mostrar_como_jugar).grid(row=6, column=1, pady=10)

# Botón Revelar Palabras
tk.Button(root, text="Revelar Palabras", command=mostrar_todas_palabras).grid(row=7, column=1, pady=10)

# Iniciar temporizador al inicio del juego
iniciar_temporizador()

root.mainloop()