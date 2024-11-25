from registers import initialize_registers, initialize_memory
from pipeline import initialize_pipeline, execute_cycle
from instructions import program
from visualization import visualize_with_pygame
# main.py

def main():
    # Inicialización de registros, memoria y pipeline
    print("Inicializando registros, memoria y pipeline...")
    registers = initialize_registers()  # Inicializar registros
    memory = initialize_memory()  # Inicializar memoria
    pipeline, program_counter = initialize_pipeline()  # Inicializar pipeline

    # Botones con instrucciones
    buttons = [
        {"label": "ADD", "instruction": {"opcode": "ADD", "dest": 1, "src1": 2, "src2": 3}, "hover": False},
        {"label": "SUB", "instruction": {"opcode": "SUB", "dest": 4, "src1": 5, "src2": 6}, "hover": False},
        {"label": "MUL", "instruction": {"opcode": "MUL", "dest": 7, "src1": 0, "src2": 1}, "hover": False},
        {"label": "DIV", "instruction": {"opcode": "DIV", "dest": 2, "src1": 5, "src2": 6}, "hover": False},  # Botón para DIV
        {"label": "MOD", "instruction": {"opcode": "MOD", "dest": 3, "src1": 5, "src2": 6}, "hover": False},  # Botón para MOD
        {"label": "STORE", "instruction": {"opcode": "STORE", "dest": 3, "src1": 4}, "hover": False},
        {"label": "LOAD", "instruction": {"opcode": "LOAD", "dest": 7, "src1": 3}, "hover": False},
        {"label": "SWAP", "instruction": {"opcode": "SWAP", "dest": 1, "src1": 2}, "hover": False},  # Botón para SWAP
        {"label": "BNE", "instruction": {"opcode": "BNE", "src1": 1, "src2": 2, "offset": 2}, "hover": False},  # Botón para BNE
        {"label": "BEQ", "instruction": {"opcode": "BEQ", "src1": 3, "src2": 4, "offset": 4}, "hover": False},  # Botón para BEQ
    ]

    # Parámetros de simulación
    visualize_during_simulation = True  # Alternar entre simulación con o sin visualización en tiempo real

    if visualize_during_simulation:
        # Simulación con visualización interactiva
        print("\nIniciando simulación con visualización interactiva...\n")
        visualize_with_pygame(
            program, registers, memory, pipeline, execute_cycle, buttons
        )
    else:
        # Simulación segmentada para pruebas
        print("\nIniciando simulación segmentada para pruebas...\n")
        run_segmented_simulation(program, registers, memory, pipeline)

def run_segmented_simulation(program, registers, memory, pipeline):
    """
    Ejecuta una simulación segmentada (sin interacción gráfica) para pruebas.
    """
    program_counter = 0
    cycles_to_run = 10  # Ciclos a ejecutar para completar el programa

    for cycle in range(cycles_to_run):
        print(f"\nCiclo {cycle + 1}")
        program_counter = execute_cycle(program, registers, memory, pipeline, program_counter)

        # Mostrar el estado del pipeline y registros
        print(f"Pipeline: {pipeline}")
        print(f"Registros: {registers}")

    print("\n--- Simulación Finalizada ---")
    print(f"Registros finales: {registers}")

if __name__ == "__main__":
    main()
