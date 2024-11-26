# memory_instructions.py

def load_instruction(instr, registers, memory):
    """Simula la operación LOAD: Carga un valor de memoria en un registro."""
    address = registers[instr["src1"]]  # Dirección en memoria, desde el registro fuente
    registers[instr["dest"]] = memory[address]  # Cargar valor en el registro destino
    print(f"LOAD - Cargando desde memoria[{address}] a R{instr['dest']}: {registers[instr['dest']]}")

def store_instruction(instr, registers, memory):
    """Simula la operación STORE: Guarda un valor de un registro en memoria."""
    address = registers[instr["src1"]]  # Dirección en memoria, desde el registro fuente
    memory[address] = registers[instr["dest"]]  # Guardar valor en la dirección especificada
    print(f"STORE - Guardando R{instr['dest']}({registers[instr['dest']]}) en memoria[{address}]")
