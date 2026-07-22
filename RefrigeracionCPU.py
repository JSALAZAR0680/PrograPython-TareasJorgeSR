# Caso 1. Grupo 1: Transferencia de calor en un sistema de refrigeración líquida para CPU
#
# Modelo: nodo térmico único (bloque de CPU + refrigerante tratados como una sola masa
# térmica), con las dos ecuaciones dadas en el enunciado:
#   Q = m*c*DeltaT          (calor sensible almacenado)
#   Qpunto = h*A*DeltaT     (transferencia de calor convectiva simplificada)
#
# Balance de energía del sistema: m*c*dT/dt = P - h*A*(T - T_amb)
# Condición de equilibrio (dT/dt = 0): T_eq = T_amb + P/(h*A)
#
# NOTA: este script requiere matplotlib. Instalar con: pip install matplotlib

try:
    import matplotlib.pyplot as plt
except ImportError:
    print("Este programa requiere la librería matplotlib.")
    print("Instálela con: pip install matplotlib")
    raise SystemExit(1)

import math

CONFIG_A = {
    "nombre": "Configuración A (radiador eficiente)",
    "P": 150.0,
    "m": 0.25,
    "c": 4186.0,
    "T_amb": 25.0,
    "hA": 3.0,
    "T0": 25.0,
}

CONFIG_B = {
    "nombre": "Configuración B (radiador degradado)",
    "P": 150.0,
    "m": 0.25,
    "c": 4186.0,
    "T_amb": 25.0,
    "hA": 1.2,
    "T0": 25.0,
}

T_CRITICA_DEFECTO = 90.0
T_TOTAL_DEFECTO = 3600.0
DT_DEFECTO = 1.0
HA_MIN_DEFECTO = 0.5
HA_MAX_DEFECTO = 5.0
HA_PASO_DEFECTO = 0.1


# ---------------------------------------------------------------------------
# Modelo físico
# ---------------------------------------------------------------------------

def calcular_temperatura_equilibrio(P, hA, T_amb):
    return T_amb + P / hA


def calcular_constante_tiempo(m, c, hA):
    return m * c / hA


def temperatura_analitica(t, T0, T_amb, P, hA, m, c):
    T_eq = calcular_temperatura_equilibrio(P, hA, T_amb)
    tau = calcular_constante_tiempo(m, c, hA)
    return T_eq + (T0 - T_eq) * math.exp(-t / tau)


def simular_euler(T0, T_amb, P, hA, m, c, t_total, dt):
    tiempos = [0.0]
    temperaturas = [T0]

    T = T0
    t = 0.0
    n_pasos = int(t_total / dt)

    for _ in range(n_pasos):
        dTdt = (P - hA * (T - T_amb)) / (m * c)
        T = T + dTdt * dt
        t = t + dt
        tiempos.append(t)
        temperaturas.append(T)

    return tiempos, temperaturas


def clasificar_condicion(T_eq, T_critica):
    if T_eq < T_critica:
        return "Estable"
    return "Sobrecalentamiento"


# ---------------------------------------------------------------------------
# Entrada de datos
# ---------------------------------------------------------------------------

def leer_flotante(mensaje, valor_por_defecto):
    texto = input("{} [{}]: ".format(mensaje, valor_por_defecto))
    if texto.strip() == "":
        return valor_por_defecto
    return float(texto)


def leer_coeficiente_global(hA_defecto, h_defecto, A_defecto):
    print("¿Cómo desea ingresar la capacidad de disipación del radiador?")
    print("1. Directamente como coeficiente global h*A (W/K)")
    print("2. Por separado: coeficiente h (W/m2K) y área efectiva A (m2)")
    opcion = input("Seleccione una opción [1]: ").strip()

    if opcion == "2":
        h = leer_flotante("Coeficiente de transferencia de calor h (W/m2K)", h_defecto)
        A = leer_flotante("Área efectiva del radiador A (m2)", A_defecto)
        return h * A

    return leer_flotante("Coeficiente global h*A (W/K)", hA_defecto)


def leer_parametros_configuracion(nombre, defecto):
    print("\n--- Parámetros de {} ---".format(nombre))
    P = leer_flotante("Potencia térmica disipada por el CPU (W)", defecto["P"])
    m = leer_flotante("Masa efectiva del refrigerante + bloque (kg)", defecto["m"])
    c = leer_flotante("Calor específico del fluido (J/kg*K)", defecto["c"])
    T_amb = leer_flotante("Temperatura ambiente (°C)", defecto["T_amb"])
    hA = leer_coeficiente_global(defecto["hA"], defecto["hA"] / 0.05, 0.05)
    T0 = leer_flotante("Temperatura inicial del sistema (°C)", T_amb)

    while m <= 0 or c <= 0 or hA <= 0:
        print("La masa, el calor específico y h*A deben ser mayores que cero. Intente de nuevo.")
        m = leer_flotante("Masa efectiva del refrigerante + bloque (kg)", defecto["m"])
        c = leer_flotante("Calor específico del fluido (J/kg*K)", defecto["c"])
        hA = leer_coeficiente_global(defecto["hA"], defecto["hA"] / 0.05, 0.05)

    return {"nombre": nombre, "P": P, "m": m, "c": c, "T_amb": T_amb, "hA": hA, "T0": T0}


# ---------------------------------------------------------------------------
# Reportes
# ---------------------------------------------------------------------------

def imprimir_justificacion_equilibrio(config, T_eq, T_critica, tau):
    condicion = clasificar_condicion(T_eq, T_critica)

    print("\nTemperatura de equilibrio (T_eq = T_amb + P/(h*A)): {:.2f} °C".format(T_eq))
    print("Constante de tiempo (tau = m*c/(h*A)): {:.1f} s".format(tau))
    print("Clasificación (T_crítica = {:.1f} °C): {}".format(T_critica, condicion))

    print("\nJustificación física:")
    print("La potencia del CPU (P) es constante, mientras que la pérdida de calor por")
    print("convección (h*A*(T-T_amb)) crece de forma lineal a medida que el sistema se")
    print("calienta. Por eso ambos términos terminan igualándose en T_eq, punto en el que")
    print("dT/dt = 0 y la temperatura deja de cambiar. Nótese que T_eq no depende de la")
    print("masa ni del calor específico del fluido: m y c solo determinan qué tan rápido")
    print("(tau) se alcanza el equilibrio, no el valor al que se llega.")

    if condicion == "Estable":
        print("Como T_eq está por debajo de la temperatura crítica, el sistema alcanza un")
        print("equilibrio térmico seguro para el CPU.")
    else:
        print("Como T_eq supera la temperatura crítica, el radiador no logra disipar toda")
        print("la potencia generada antes de llegar a una temperatura peligrosa: en la")
        print("práctica el CPU haría throttling o se apagaría antes de alcanzar ese")
        print("equilibrio matemático.")

    return condicion


def guardar_resultado_en_archivo(texto):
    with open('resultados_refrigeracion.txt', 'a') as archivo:
        archivo.write(texto + "\n")


# ---------------------------------------------------------------------------
# Gráficas
# ---------------------------------------------------------------------------

def mostrar_o_guardar_figura(nombre_archivo):
    plt.savefig(nombre_archivo, bbox_inches="tight")
    print("Gráfica guardada en: {}".format(nombre_archivo))
    try:
        plt.show()
    except Exception:
        pass
    plt.close()


def graficar_comparacion(series, T_critica, titulo, nombre_archivo):
    plt.figure()

    for tiempos, temperaturas, etiqueta in series:
        plt.plot(tiempos, temperaturas, label=etiqueta)

    plt.axhline(T_critica, color="red", linestyle="--",
                label="Temperatura crítica ({:.1f}°C)".format(T_critica))

    plt.xlabel("Tiempo (s)")
    plt.ylabel("Temperatura (°C)")
    plt.title(titulo)
    plt.legend()
    plt.grid(True)

    mostrar_o_guardar_figura(nombre_archivo)


def generar_valores_hA(hA_min, hA_max, paso):
    valores = []
    hA = hA_min
    while hA <= hA_max:
        valores.append(hA)
        hA = hA + paso
    return valores


def graficar_barrido_hA(valores_hA, valores_T_eq, T_critica, hA_critico, nombre_archivo):
    plt.figure()

    plt.plot(valores_hA, valores_T_eq, label="Temperatura de equilibrio")
    plt.axhline(T_critica, color="red", linestyle="--", label="Temperatura crítica")
    plt.axvline(hA_critico, color="green", linestyle=":",
                label="h*A crítico ({:.2f} W/K)".format(hA_critico))

    plt.xlabel("Coeficiente global de enfriamiento h*A (W/K)")
    plt.ylabel("Temperatura de equilibrio (°C)")
    plt.title("Temperatura de equilibrio del sistema vs coeficiente de enfriamiento del radiador")
    plt.legend()
    plt.grid(True)

    mostrar_o_guardar_figura(nombre_archivo)


# ---------------------------------------------------------------------------
# Opciones del menú
# ---------------------------------------------------------------------------

def opcion_simulacion_personalizada():
    config = leer_parametros_configuracion("la simulación", CONFIG_A)
    t_total = leer_flotante("Tiempo total de simulación (s)", T_TOTAL_DEFECTO)
    dt = leer_flotante("Paso de tiempo (s)", DT_DEFECTO)
    T_critica = leer_flotante("Temperatura crítica del CPU (°C)", T_CRITICA_DEFECTO)

    while dt <= 0:
        print("El paso de tiempo debe ser mayor que cero.")
        dt = leer_flotante("Paso de tiempo (s)", DT_DEFECTO)

    tiempos, temperaturas = simular_euler(
        config["T0"], config["T_amb"], config["P"], config["hA"],
        config["m"], config["c"], t_total, dt)

    T_eq = calcular_temperatura_equilibrio(config["P"], config["hA"], config["T_amb"])
    tau = calcular_constante_tiempo(config["m"], config["c"], config["hA"])
    T_final_analitico = temperatura_analitica(
        t_total, config["T0"], config["T_amb"], config["P"], config["hA"],
        config["m"], config["c"])

    print("\nTemperatura final (Euler): {:.2f} °C".format(temperaturas[-1]))
    print("Temperatura final (solución analítica): {:.2f} °C".format(T_final_analitico))
    print("Diferencia Euler vs analítica: {:.4f} °C".format(
        abs(temperaturas[-1] - T_final_analitico)))

    condicion = imprimir_justificacion_equilibrio(config, T_eq, T_critica, tau)

    guardar_resultado_en_archivo(
        "Simulación personalizada: P={}W, hA={}W/K, T_eq={:.2f}C, condicion={}".format(
            config["P"], config["hA"], T_eq, condicion))

    graficar_comparacion(
        [(tiempos, temperaturas, "Simulación (h*A = {} W/K)".format(config["hA"]))],
        T_critica,
        "Evolución de la temperatura del sistema de refrigeración",
        "temperatura_vs_tiempo.png")


def opcion_comparar_configuraciones():
    T_critica = leer_flotante("Temperatura crítica del CPU (°C)", T_CRITICA_DEFECTO)
    t_total = leer_flotante("Tiempo total de simulación (s)", T_TOTAL_DEFECTO)
    dt = leer_flotante("Paso de tiempo (s)", DT_DEFECTO)

    print("\n¿Qué configuraciones desea comparar?")
    print("1. Usar las configuraciones predefinidas (A y B)")
    print("2. Ingresar dos configuraciones propias")
    opcion = input("Seleccione una opción [1]: ").strip()

    if opcion == "2":
        config1 = leer_parametros_configuracion("Configuración 1", CONFIG_A)
        config2 = leer_parametros_configuracion("Configuración 2", CONFIG_B)
    else:
        config1 = CONFIG_A
        config2 = CONFIG_B

    series = []
    resultados = []

    for config in (config1, config2):
        tiempos, temperaturas = simular_euler(
            config["T0"], config["T_amb"], config["P"], config["hA"],
            config["m"], config["c"], t_total, dt)

        T_eq = calcular_temperatura_equilibrio(config["P"], config["hA"], config["T_amb"])
        tau = calcular_constante_tiempo(config["m"], config["c"], config["hA"])

        print("\n=== {} ===".format(config["nombre"]))
        condicion = imprimir_justificacion_equilibrio(config, T_eq, T_critica, tau)

        series.append((tiempos, temperaturas,
                        "{} (h*A={} W/K, T_eq={:.1f}°C)".format(
                            config["nombre"], config["hA"], T_eq)))
        resultados.append({"config": config, "T_eq": T_eq, "condicion": condicion})

        guardar_resultado_en_archivo(
            "{}: P={}W, hA={}W/K, T_eq={:.2f}C, condicion={}".format(
                config["nombre"], config["P"], config["hA"], T_eq, condicion))

    print("\nValidación física:")
    if config1["P"] == config2["P"] and config1["T_amb"] == config2["T_amb"]:
        mayor_hA = resultados[0] if config1["hA"] >= config2["hA"] else resultados[1]
        menor_hA = resultados[1] if mayor_hA is resultados[0] else resultados[0]

        assert mayor_hA["T_eq"] <= menor_hA["T_eq"], (
            "La configuración con mayor h*A debería alcanzar una temperatura de "
            "equilibrio menor o igual.")
        print("Se confirma que al aumentar h*A ({} -> {} W/K), la temperatura de "
              "equilibrio disminuye ({:.1f} -> {:.1f} °C).".format(
                  menor_hA["config"]["hA"], mayor_hA["config"]["hA"],
                  menor_hA["T_eq"], mayor_hA["T_eq"]))
    else:
        print("Las configuraciones difieren en más que h*A; se omite la verificación "
              "automática, pero puede comparar visualmente ambas curvas en la gráfica.")

    graficar_comparacion(series, T_critica,
                          "Comparación de configuraciones de enfriamiento",
                          "comparacion_configuraciones.png")


def opcion_barrido_equilibrio():
    P = leer_flotante("Potencia térmica disipada por el CPU (W)", CONFIG_A["P"])
    T_amb = leer_flotante("Temperatura ambiente (°C)", CONFIG_A["T_amb"])
    T_critica = leer_flotante("Temperatura crítica del CPU (°C)", T_CRITICA_DEFECTO)
    hA_min = leer_flotante("Valor mínimo de h*A a evaluar (W/K)", HA_MIN_DEFECTO)
    hA_max = leer_flotante("Valor máximo de h*A a evaluar (W/K)", HA_MAX_DEFECTO)
    paso = leer_flotante("Paso de h*A (W/K)", HA_PASO_DEFECTO)

    hA_critico = P / (T_critica - T_amb)

    valores_hA = generar_valores_hA(hA_min, hA_max, paso)
    valores_T_eq = [calcular_temperatura_equilibrio(P, hA, T_amb) for hA in valores_hA]

    print("\nh*A crítico (a partir del cual T_eq = T_crítica): {:.2f} W/K".format(hA_critico))
    print("A medida que h*A aumenta, la temperatura de equilibrio disminuye:")
    print("  h*A = {:.2f} W/K -> T_eq = {:.2f} °C".format(valores_hA[0], valores_T_eq[0]))
    print("  h*A = {:.2f} W/K -> T_eq = {:.2f} °C".format(valores_hA[-1], valores_T_eq[-1]))

    graficar_barrido_hA(valores_hA, valores_T_eq, T_critica, hA_critico,
                         "temperatura_equilibrio_vs_hA.png")


# ---------------------------------------------------------------------------
# Menú principal
# ---------------------------------------------------------------------------

def mostrar_menu():
    print("\n=== Simulación de refrigeración líquida para CPU ===")
    print("Caso 1 - Grupo 1: Transferencia de calor en un sistema de refrigeración líquida para CPU")
    print()
    print("1. Simular con parámetros personalizados")
    print("2. Comparar configuraciones de enfriamiento (predefinidas o propias)")
    print("3. Graficar temperatura de equilibrio vs coeficiente de enfriamiento (h*A)")
    print("0. Salir")


while True:
    mostrar_menu()
    opcion = int(input("Seleccione una opción: "))

    if opcion == 0:
        break
    elif opcion == 1:
        opcion_simulacion_personalizada()
    elif opcion == 2:
        opcion_comparar_configuraciones()
    elif opcion == 3:
        opcion_barrido_equilibrio()
    else:
        print("Opción no válida.")
