# Inicializa los registros y la memoria
def initialize_registers():
    registers = [0] * 9  # Incluye R8 como el registro del PC


    # Valores iniciales para ADD
    registers[2] = 10  # R2
    registers[3] = 45  # R3
    registers[4] = 45  # R4

    # Valores iniciales para SUB
    registers[5] = 50  # R5
    registers[6] = 30  # R6

    # Valores iniciales para MUL
    registers[0] = 5   # R0
    registers[1] = 4   # R1
    registers[8] = 0  # Inicializa el PC en 0
    
    return registers

def initialize_memory(size=256):
    return [0] * size  # Memoria con 256 posiciones

# Muestra el estado actual de los registros
def show_registers(registers):
    print(f"Registros: {registers}")
