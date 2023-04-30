import math

def suma(numeros):
    return sum(numeros)

def resta(num1, num2):
    return num1 - num2

def multiplicacion(numeros):
    result = 1
    for num in numeros:
        result *= num
    return result

def division(num1, num2):
    return num1 / num2

def factorial(num):
    return math.factorial(num)

def potencia(num1, num2):
    return num1 ** num2

def guardar_operacion_en_archivo(operacion, resultado):
    with open('resultados.txt', 'a') as archivo:
        archivo.write("{} = {}\n".format(operacion, resultado))

print("Bienvenido a la calculadora")

while True:
    print("Por favor seleccione una operación:")
    print("1. Suma")
    print("2. Resta")
    print("3. Multiplicación")
    print("4. División")
    print("5. Factorial")
    print("6. Potencia")
    print("0. Salir")

    opcion = int(input())

    if opcion == 0:
        break

    elif opcion == 1:
        n = int(input("Ingrese el número de valores a sumar: "))
        numeros = []
        for i in range(n):
            numeros.append(float(input("Ingrese el valor número {}: ".format(i+1))))
        resultado = suma(numeros)
        print("La suma de los números es: {}".format(resultado))
        guardar_operacion_en_archivo("{} = {}".format("+".join(map(str, numeros)), resultado))

    elif opcion == 2:
        num1 = float(input("Ingrese el primer número: "))
        num2 = float(input("Ingrese el segundo número: "))
        resultado = resta(num1, num2)
        print("La resta de los números es: {}".format(resultado))
        guardar_operacion_en_archivo("{} - {} = {}".format(num1, num2, resultado))

    elif opcion == 3:
        n = int(input("Ingrese el número de valores a multiplicar: "))
        numeros = []
        for i in range(n):
            numeros.append(float(input("Ingrese el valor número {}: ".format(i+1))))
        resultado = multiplicacion(numeros)
        print("El resultado de la multiplicación es: {}".format(resultado))
        guardar_operacion_en_archivo("{} = {}".format("*".join(map(str, numeros)), resultado))

    elif opcion == 4:
        num1 = float(input("Ingrese el primer número: "))
        num2 = float(input("Ingrese el segundo número: "))
        if num2 == 0:
            print("La división por cero no está permitida")
        else:
            resultado = division(num1, num2)
            print("El resultado de la división es: {}".format(resultado))
            guardar_operacion_en_archivo("{} / {} = {}".format(num1, num2, resultado))

    elif opcion == 5:
        num = int(input("Ingrese el número para calcular su factorial: "))
        resultado = factorial(num)
        print("El factorial de {} es: {}".format(num, resultado))
        guardar_operacion_en_archivo("{}! = {}".format(num, resultado))

    elif opcion == 6:
        num1 = float(input("Ingrese la base: "))
        num2 = float(input("Ingrese el exponente: "))
        resultado = potencia(num1, num2)
        print("El resultado de la potencia es: {}".format)

