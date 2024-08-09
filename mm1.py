# Objetivo: Construir un simulador de una cola M/M/1 basado en 
# el algoritmo de simulación de eventos discretos, y comparar las
# medidas de rendimientos teóricas con las medidas de rendimiento
# que entrega la simulación.

# Autores:
# - Diego Valdés Fernández
# - Valentina Campos Olguín

# Fecha: 09/08/2024

# Importación de librerías
import numpy as np
import getopt
import sys

# Configuración de parámetros de la simulación

# Descripción: Función que se encarga de parsear los argumentos de la línea de comandos.
# Retorna una tupla con los valores de los argumentos.
def parse_arguments():
    arrival_rate = None
    service_rate = None
    end_time = None

    try:
        opts, args = getopt.getopt(sys.argv[1:], "a:d:t:", ["arrival_rate=", "service_rate=", "end_time="])
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)
    
    for opt, arg in opts:
        if opt in ("-a", "--arrival_rate"):
            arrival_rate = float(arg)
        elif opt in ("-d", "--service_rate"):
            service_rate = float(arg)
        elif opt in ("-t", "--end_time"):
            end_time = float(arg)
        else:
            assert False, "Unhandled option"
    
    return arrival_rate, service_rate, end_time

arrival_rate, service_rate, end_time = parse_arguments()

# Definición de variables de estado
Ak = 0 # Tiempo de arribo del job k
Sk = 0 # Tiempo de servicio del job k
Qk = 0 # Suma de tiempos durante el cual la cola ha sido de largo k

# Definición de otras variables
Na = 0 # Número de clientes que han llegado
Nd = 0 # Número de clientes que han salido del sistema
t = 0 # Tiempo de simulación
queue = [] # Cola de clientes
max_queue_length = 0 # Máximo largo de la cola
Q0 = 0 # Tiempo total de cola vacía
Ls = 0 # Servidor ocupado o no ocupado
sum_Sk = 0 # Suma de tiempos de servicio
sum_kQk = 0 # Suma de k * Qk
QT_time = 0 # Tiempo total en que la cola tiene el largo máximo
last_time = 0 # Marca de tiempo del último evento

# Generación de eventos de arribo
def generate_event_time(rate):
    return -np.log(1.0 - np.random.uniform())/rate

next_arrival = generate_event_time(arrival_rate)
end_simulation = end_time

# Simulación de eventos discretos
current_time = 0
next_departure = float('inf')

# Mientras no se cumpla la condición de término
while current_time < end_simulation:
    time_elapsed = current_time - last_time

    if len(queue) == max_queue_length:
        QT_time += time_elapsed

    if(len(queue) == 0):
        Q0 += time_elapsed
    
    last_time = current_time

    # Si el próximo evento es un arribo
    if next_arrival <= next_departure: 
        current_time = next_arrival
        # Si el servidor no está ocupado
        if Ls == 0:
            # Se actualiza el servidor a ocupado
            Ls = 1
            # Se genera un tiempo de servicio y se programa la nueva salida
            Sk = generate_event_time(service_rate)
            next_departure = current_time + Sk
            # Se actualiza el tiempo de servicio total
            sum_Sk += Sk
        # Si el servidor está ocupado
        else:
            # Se agrega el tiempo a la cola
            queue.append(current_time)
            # Se actualiza el largo máximo de la cola
            max_queue_length = max(max_queue_length, len(queue))

        # Se genera un nuevo tiempo de arribo
        Ak = generate_event_time(arrival_rate)
        next_arrival = current_time + Ak
        Na += 1


    # Si el próximo evento es una salida
    else:
        current_time = next_departure
        if len(queue) > 0:
            arrival_time = queue.pop(0)
            # Se saca el primer elemento de la cola
            Qk += (current_time - arrival_time)
            # Se genera un tiempo de servicio y se programa la nueva salida
            Sk = generate_event_time(service_rate)
            next_departure = current_time + Sk

            # Se actualiza el tiempo de servicio total
            sum_Sk += Sk

            # Se calcula la suma de k * Qk
            sum_kQk += len(queue) * (current_time - last_time)

        else:
            # Se actualiza el servidor a desocupado
            Ls = 0
            next_departure = float('inf')
        Nd += 1

    # Se actualiza el tiempo de simulación
    current_time = min(next_arrival, next_departure)

QT = QT_time

if QT > 0:
    U = 1 - (Q0 / QT)
    E_X = sum_kQk / QT
else:
    U = 0
    E_X = 0

if Nd > 0:
    E_S = sum_Sk / Nd
else:
    E_S = 0

print(f"Numero de jobs que llegaron: {Na}")
print(f"Numero de jobs que salieron: {Nd}")
print(f"Tiempo total de cola vacía: {Q0}")
print(f"Largo máximo de la cola: {max_queue_length}")
print(f"Tiempo total de la cola con largo máximo: {Qk}")
print(f"Utilización computada: {U}") #VERIFICAR
print(f"Utilización teórica: {1 - (arrival_rate / service_rate)}")
print(f"Largo promedio computado de la cola: {E_X}") #VERIFICAR 
print(f"Largo promedio teórico de la cola: {arrival_rate**2 / (service_rate**2 - arrival_rate**2)}")
print(f"Tiempo promedio computado de residencia: {E_S}")
print(f"Tiempo promedio teórico de residencia: {1 / service_rate}")

