# Caso 1. Grupo 1: Transferencia de calor en un sistema de refrigeración líquida para CPU
#
# Simulador interactivo (con controles deslizantes) pensado para presentar en clase:
# al mover los controles se recalcula y redibuja en vivo la evolución de temperatura
# del sistema y su temperatura de equilibrio, sin necesidad de escribir nada por teclado.
#
# Modelo (nodo térmico único), igual al de RefrigeracionCPU.py:
#   Q = m*c*DeltaT          (calor sensible almacenado)
#   Qpunto = h*A*DeltaT     (transferencia de calor convectiva simplificada)
#   m*c*dT/dt = P - h*A*(T - T_amb)
#   T_eq = T_amb + P/(h*A)  (temperatura de equilibrio; no depende de m ni c)
#
# Uso en clase:
#   1. Ejecutar: python SimuladorInteractivoCPU.py  -> abre una ventana con controles.
#   2. Mover los deslizadores para cambiar Potencia, Masa/caudal, T. ambiente y h*A.
#   3. Usar los botones para saltar a la Configuración A (estable) o B (sobrecalienta),
#      volver al estado inicial, o guardar una captura de la vista actual.
#
# NOTA: requiere matplotlib. Instalar con: pip install matplotlib

try:
    import matplotlib.pyplot as plt
    from matplotlib.widgets import Slider, Button
except ImportError:
    print("Este programa requiere la librería matplotlib.")
    print("Instálela con: pip install matplotlib")
    raise SystemExit(1)

C_AGUA = 4186.0
T_TOTAL = 3600.0
DT = 2.0
T_CRITICA = 90.0
HA_MIN, HA_MAX, HA_PASO = 0.3, 6.0, 0.05

CONFIG_A = {"P": 150.0, "m": 0.25, "hA": 3.0, "T_amb": 25.0}
CONFIG_B = {"P": 150.0, "m": 0.25, "hA": 1.2, "T_amb": 25.0}


# ---------------------------------------------------------------------------
# Modelo físico
# ---------------------------------------------------------------------------

def calcular_temperatura_equilibrio(P, hA, T_amb):
    return T_amb + P / hA


def calcular_constante_tiempo(m, c, hA):
    return m * c / hA


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


def generar_valores_hA(hA_min, hA_max, paso):
    valores = []
    hA = hA_min
    while hA <= hA_max:
        valores.append(hA)
        hA = hA + paso
    return valores


VALORES_HA_BARRIDO = generar_valores_hA(HA_MIN, HA_MAX, HA_PASO)

# ---------------------------------------------------------------------------
# Construcción de la figura
# ---------------------------------------------------------------------------

fig = plt.figure(figsize=(12, 7.5))
fig.suptitle("Caso 1 - Grupo 1: Refrigeración líquida para CPU", fontsize=14, fontweight="bold")

ax_temp = fig.add_axes([0.07, 0.38, 0.41, 0.46])
ax_sweep = fig.add_axes([0.56, 0.38, 0.41, 0.46])

ax_temp.set_xlabel("Tiempo (s)")
ax_temp.set_ylabel("Temperatura (°C)")
ax_temp.set_title("Temperatura del sistema vs tiempo")
ax_temp.grid(True)

ax_sweep.set_xlabel("Coeficiente global de enfriamiento h*A (W/K)")
ax_sweep.set_ylabel("Temperatura de equilibrio (°C)")
ax_sweep.set_title("Temperatura de equilibrio vs h*A")
ax_sweep.grid(True)
ax_sweep.set_xlim(HA_MIN, HA_MAX)

# Curvas de referencia fijas (Configuración A y B) para comparar visualmente
for config, color, nombre in ((CONFIG_A, "tab:blue", "Config. A: radiador eficiente"),
                               (CONFIG_B, "tab:orange", "Config. B: radiador degradado")):
    t_ref, T_ref = simular_euler(config["T_amb"], config["T_amb"], config["P"], config["hA"],
                                  config["m"], C_AGUA, T_TOTAL, DT)
    ax_temp.plot(t_ref, T_ref, "--", color=color, alpha=0.4, linewidth=1.5,
                 label="{} (referencia)".format(nombre))

ax_temp.axhline(T_CRITICA, color="red", linestyle="--",
                label="Temperatura crítica ({:.0f}°C)".format(T_CRITICA))

linea_actual, = ax_temp.plot([], [], color="black", linewidth=2.5, label="Configuración actual")
ax_temp.legend(loc="upper right", fontsize=8)

linea_barrido, = ax_sweep.plot([], [], color="tab:blue", label="T_eq(h*A)")
ax_sweep.axhline(T_CRITICA, color="red", linestyle="--", label="Temperatura crítica")

hA_critico_inicial = CONFIG_A["P"] / (T_CRITICA - CONFIG_A["T_amb"])
linea_hA_critico = ax_sweep.axvline(hA_critico_inicial, color="green", linestyle=":",
                                     label="h*A crítico")

punto_actual, = ax_sweep.plot([], [], "o", color="black", markersize=9, label="Punto actual")
ax_sweep.legend(loc="upper right", fontsize=8)

texto_estado = fig.text(0.5, 0.90, "", ha="center", va="center", fontsize=13, fontweight="bold")

# ---------------------------------------------------------------------------
# Controles deslizantes y botones
# ---------------------------------------------------------------------------

ax_slider_P = fig.add_axes([0.12, 0.285, 0.76, 0.025])
ax_slider_m = fig.add_axes([0.12, 0.245, 0.76, 0.025])
ax_slider_Tamb = fig.add_axes([0.12, 0.205, 0.76, 0.025])
ax_slider_hA = fig.add_axes([0.12, 0.165, 0.76, 0.025])

slider_P = Slider(ax_slider_P, "Potencia CPU (W)", 20.0, 300.0, valinit=CONFIG_A["P"])
slider_m = Slider(ax_slider_m, "Masa/caudal efectivo (kg)", 0.05, 1.0, valinit=CONFIG_A["m"])
slider_Tamb = Slider(ax_slider_Tamb, "T. ambiente (°C)", 10.0, 45.0, valinit=CONFIG_A["T_amb"])
slider_hA = Slider(ax_slider_hA, "Coef. enfriamiento h*A (W/K)", HA_MIN, HA_MAX, valinit=CONFIG_A["hA"])

ax_btn_a = fig.add_axes([0.08, 0.06, 0.2025, 0.05])
ax_btn_b = fig.add_axes([0.3025, 0.06, 0.2025, 0.05])
ax_btn_reset = fig.add_axes([0.525, 0.06, 0.2025, 0.05])
ax_btn_guardar = fig.add_axes([0.7475, 0.06, 0.2025, 0.05])

btn_config_a = Button(ax_btn_a, "Config. A (estable)")
btn_config_b = Button(ax_btn_b, "Config. B (sobrecalienta)")
btn_reset = Button(ax_btn_reset, "Reiniciar")
btn_guardar = Button(ax_btn_guardar, "Guardar imagen")


def actualizar(_=None):
    P = slider_P.val
    m = slider_m.val
    T_amb = slider_Tamb.val
    hA = slider_hA.val

    T0 = T_amb
    tiempos, temperaturas = simular_euler(T0, T_amb, P, hA, m, C_AGUA, T_TOTAL, DT)

    T_eq = calcular_temperatura_equilibrio(P, hA, T_amb)
    tau = calcular_constante_tiempo(m, C_AGUA, hA)
    condicion = clasificar_condicion(T_eq, T_CRITICA)
    color = "tab:green" if condicion == "Estable" else "tab:red"

    linea_actual.set_data(tiempos, temperaturas)
    linea_actual.set_color(color)
    ax_temp.relim()
    ax_temp.autoscale_view()

    valores_T_eq = [calcular_temperatura_equilibrio(P, hA_i, T_amb) for hA_i in VALORES_HA_BARRIDO]
    linea_barrido.set_data(VALORES_HA_BARRIDO, valores_T_eq)

    if T_CRITICA > T_amb:
        hA_critico = P / (T_CRITICA - T_amb)
        if HA_MIN <= hA_critico <= HA_MAX:
            linea_hA_critico.set_xdata([hA_critico, hA_critico])

    punto_actual.set_data([hA], [T_eq])
    punto_actual.set_color(color)
    ax_sweep.relim()
    ax_sweep.autoscale_view(scalex=False, scaley=True)

    texto_estado.set_text(
        "T_eq = {:.1f} °C   |   tau = {:.0f} s   |   Estado: {}".format(T_eq, tau, condicion))
    texto_estado.set_color(color)

    fig.canvas.draw_idle()


def aplicar_config(config):
    slider_P.set_val(config["P"])
    slider_m.set_val(config["m"])
    slider_Tamb.set_val(config["T_amb"])
    slider_hA.set_val(config["hA"])


def al_hacer_click_config_a(_):
    aplicar_config(CONFIG_A)


def al_hacer_click_config_b(_):
    aplicar_config(CONFIG_B)


def al_hacer_click_reset(_):
    aplicar_config(CONFIG_A)


def al_hacer_click_guardar(_):
    fig.savefig("captura_simulador.png", bbox_inches="tight")
    print("Imagen guardada en: captura_simulador.png")


slider_P.on_changed(actualizar)
slider_m.on_changed(actualizar)
slider_Tamb.on_changed(actualizar)
slider_hA.on_changed(actualizar)

btn_config_a.on_clicked(al_hacer_click_config_a)
btn_config_b.on_clicked(al_hacer_click_config_b)
btn_reset.on_clicked(al_hacer_click_reset)
btn_guardar.on_clicked(al_hacer_click_guardar)

actualizar()

plt.show()
