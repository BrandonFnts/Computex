import sympy as sp
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Flask, render_template, request

app = Flask(__name__)

def encontrar_maximos_minimos(funcion, variable, limite1, limite2):
    x = sp.symbols(variable)

    # Reemplazar '^' por '**' en la expresión de la función
    funcion = funcion.replace('^', '**')

    expr = sp.sympify(funcion)

    primera_derivada = sp.diff(expr, x)
    segunda_derivada = sp.diff(primera_derivada, x)

    puntos_criticos = sp.solve(primera_derivada, x)

    # Obtener la parte real de la segunda derivada
    segunda_derivada_real = sp.re(segunda_derivada)

    # Filtrar las soluciones reales para la segunda derivada
    puntos_criticos_reales = [punto for punto in puntos_criticos if segunda_derivada_real.subs(x, punto).is_real]

    puntos_inflexion = []

    puntos_clasificados = []
    for punto in puntos_criticos_reales:
        segunda_derivada_evaluada = segunda_derivada_real.subs(x, punto)

        if segunda_derivada_evaluada == 0:
            puntos_inflexion.append((punto, "punto de inflexión"))
        elif segunda_derivada_evaluada > 0:
            puntos_clasificados.append((punto, "mínimo"))
        else:
            puntos_clasificados.append((punto, "máximo"))

    coordenadas_puntos = [(punto, expr.subs(x, punto)) for punto, _ in puntos_clasificados]

    x_vals = np.linspace(float(limite1), float(limite2), 500)

    # Utilizar numpy.vectorize para manejar números complejos
    funcion_vectorizada = np.vectorize(lambda val: np.real(expr.subs(x, val)))
    y_vals = funcion_vectorizada(x_vals)

    plt.figure()
    plt.plot(x_vals, y_vals, label="Función")

    for punto, tipo_punto in puntos_clasificados:
        y_val = expr.subs(x, punto)
        etiqueta = f"{tipo_punto} ({punto}, {y_val})"
        plt.scatter(punto, np.real(y_val), color='red', label=etiqueta)

    for punto, _ in puntos_inflexion:
        y_val = expr.subs(x, punto)
        etiqueta = f"punto de inflexión ({punto}, {y_val})"
        plt.scatter(punto, np.real(y_val), color='green', label=etiqueta)

    plt.legend()
    plt.xlabel(variable)
    plt.ylabel("y")
    plt.title("Gráfica de la función: " + funcion)
    plt.grid(True)

    plt.savefig("static/grafica.png")
    plt.close()

    return puntos_clasificados, coordenadas_puntos, puntos_inflexion

@app.route('/', methods=['GET', 'POST'])
def index():
    maximo = ""
    minimo = ""
    inflexion = ""
    imagen = False

    if request.method == 'POST':
        funcion = request.form['funcion']
        variable = "x"
        limite1 = request.form['limite1']
        limite2 = request.form['limite2']

        try:
            puntos_clasificados, _, puntos_inflexion = encontrar_maximos_minimos(funcion, variable, limite1, limite2)

            for punto, tipo_punto in puntos_clasificados:
                if tipo_punto == "máximo":
                    maximo = f"{punto}, {sp.sympify(funcion).subs(sp.symbols(variable), punto)}"
                elif tipo_punto == "mínimo":
                    minimo = f"{punto}, {sp.sympify(funcion).subs(sp.symbols(variable), punto)}"

            if puntos_inflexion:
                inflexion = ", ".join([f"{punto} ({sp.sympify(funcion).subs(sp.symbols(variable), punto)})" for punto, _ in puntos_inflexion])

            imagen = True
        except (sp.SympifyError, ValueError):
            # Si hay un error en la función ingresada o los límites no son numéricos
            error_msg = "Error: La función ingresada no es válida o los límites no son numéricos."
            return render_template('index.html', error_msg=error_msg)

    # Asignar "N/A" si no hay valores para maximo, minimo o inflexion
    maximo = maximo if maximo else "N/A"
    minimo = minimo if minimo else "N/A"
    inflexion = inflexion if inflexion else "N/A"

    return render_template('index.html', maximo=maximo, minimo=minimo, inflexion=inflexion, imagen=imagen)

if __name__ == '__main__':
    app.run()