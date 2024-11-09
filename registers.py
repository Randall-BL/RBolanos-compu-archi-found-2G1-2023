# Inicializa los registros y la memoria
def initialize_registers():
    registers = [0] * 8
    registers[2] = 10  # Inicializamos R2
    registers[3] = 20  # Inicializamos R3
    return registers

def initialize_memory(size=256):
    return [0] * size  # Memoria con 256 posiciones

# Muestra el estado actual de los registros
def show_registers(registers):
    print(f"Registros: {registers}")
