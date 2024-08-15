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

# Configuración de la semilla para garantizar la reproducibilidad de los resultados
#np.random.seed(0)

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

# Parseo de los argumentos de la línea de comandos
arrival_rate, service_rate, end_time = parse_arguments()

# Función para generar tiempos de eventos (arribo o salida) usando la distribución exponencial
def generate_event_time(rate):
    return -np.log(1.0 - np.random.uniform())/rate

# Validación de los parámetros
if arrival_rate is None or service_rate is None or end_time is None:
    print("Error: Todos los parámetros (arrival_rate, service_rate, end_time) deben ser proporcionados.")
    sys.exit(1)

if arrival_rate <= 0 or service_rate <= 0 or end_time <= 0:
    print("Error: Los parámetros deben ser números positivos.")
    sys.exit(1)

if arrival_rate >= service_rate:
    print("Error: La tasa de servicio debe ser mayor que la tasa de arribo para garantizar la estabilidad del sistema.")
    sys.exit(1)

# Definición de variables de estado
Ak = 0 # Tiempo de arribo del job k
Sk = 0 # Tiempo de servicio del job k

# Definición de otras variables
Na = 0 # Número de clientes que han llegado
Nd = 0 # Número de clientes que han salido del sistema

# Definición de otras variables
queue = [] # Cola de clientes
queuetime=0 # Tiempos de cola suma de k * Qk
max_queue_length = 0 # Máximo largo de la cola
Q0 = 0 # Tiempo total de cola vacía
Ls = 0 # Servidor ocupado o no ocupado
sum_Sk = 0 # Suma de tiempos de servicio
sum_QN = {} # Suma de QN
QT = end_time # Tiempo total en que la cola tiene el largo máximo
last_time = 0 # Marca de tiempo del último evento

# Simulación de eventos discretos
current_time = 0 # Tiempo actual en la simulación
next_departure = float('inf') # Tiempo de la siguiente salida, inicializado en infinito
next_arrival = 0 # Sigueiente arribo inicial 
end_simulation = end_time # Tiempo de fin de la simulación


# Mientras no se cumpla la condición de término
while current_time < end_simulation:
    # Si el próximo evento es un arribo
    if next_arrival <= next_departure: 
        current_time = next_arrival
        # Si el servidor no está ocupado
        if Ls == 0:
            Ls = 1   # Se actualiza el servidor a ocupado
            Sk = generate_event_time(service_rate) # Genera tiempo de servicio
            next_departure = current_time + Sk   # Programa la siguiente salida
            sum_Sk += Sk # Acumula el tiempo de servicio
            
        # Si el servidor está ocupado, el cliente se agrega a la cola
        else:
            partial_service_time = current_time - (next_departure - Sk)
            sum_Sk += partial_service_time
            queue.append(current_time)  # Se agrega el tiempo a la cola
            max_queue_length = max(max_queue_length, len(queue)) # Se actualiza el largo máximo de la cola


        # Se genera un nuevo tiempo de arribo
        Ak = generate_event_time(arrival_rate)
        next_arrival = current_time + Ak
        Na += 1 # Incrementa el contador de arribos

    # Si el próximo evento es una salida
    else:
        current_time = next_departure
        if len(queue) > 0:
            arrival_time = queue.pop(0) # Saca al primer cliente de la cola
            sum_Sk += current_time - arrival_time  # Calcula y acumula el tiempo de residencia del cliente
            Sk = generate_event_time(service_rate) # Genera tiempo de servicio para el siguiente cliente en la cola
            next_departure = current_time + Sk

        else:
            Ls = 0  # Se actualiza el servidor a desocupado
            next_departure = float('inf') # Se programa la próxima salida como infinito

        Nd += 1  # Incrementa el contador de salidas

    # Se actualiza el tiempo de simulación
    current_time = min(next_arrival, next_departure)

    # Captura del tiempo transcurrido antes de actualizar current_time
    time_elapsed = current_time - last_time

    # Calcular cuando la cola esta vacía
    if(len(queue) == 0) :
        Q0 += time_elapsed

    # Se calcula la suma de k * Qk
    queuetime = queuetime +  len(queue) *  time_elapsed

    # Tiempo de la cola con su largo máximo
    # Si el largo de la cola no está en el diccionario, se agrega
    if len(queue) not in sum_QN:
        sum_QN[len(queue)] = 0  
    
    #Se suma el tiempo que la cola estuvo con largo k al diccionario
    sum_QN[len(queue)]=sum_QN[len(queue)]+(current_time - last_time)

    last_time = current_time # Actualiza la marca de tiempo del último evento

# Calcular cuando la cola esta vacía
if(len(queue) == 0) :
    Q0 += end_simulation - last_time


# MEDIDAS DE RENDIMIENTO
#Utilización y largo promedio de la cola
if Q0> QT:
    U = 0
    E_X=0
else:
    U = 1 - (Q0 / QT) # Utilización calculada

    E_X = queuetime / QT # Largo promedio de la cola

# Tiempo promedio de residencia
if Nd > 0:
    E_S = sum_Sk / Nd
else:
    E_S = 0

#ECUACIONES DE LITTLE

# Utilización teórica
UT = arrival_rate / service_rate

# Largo promedio teórico de la cola
LCT = arrival_rate**2 / (service_rate**2 - arrival_rate*service_rate)

# Tiempo promedio teórico de residencia 
TRT = 1 / (service_rate - arrival_rate)

#SALIDAS
print(f"Numero de jobs que llegaron: {Na}")
print(f"Numero de jobs que salieron: {Nd}")
print(f"Tiempo total de cola vacía: {Q0}")
print(f"Largo máximo de la cola: {max_queue_length}")
print(f"Tiempo total de la cola con largo máximo: {sum_QN[max_queue_length]}")
print(f"Utilización computada: {U}") 
print(f"Utilización teórica: {UT}")
print(f"Largo promedio computado de la cola: {E_X}")  
print(f"Largo promedio teórico de la cola: {LCT}")
print(f"Tiempo promedio computado de residencia: {E_S}")
print(f"Tiempo promedio teórico de residencia: {TRT}")

