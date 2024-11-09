from registers import initialize_registers, initialize_memory
from pipeline import initialize_pipeline, execute_cycle
from instructions import program
from visualization import visualize_with_pygame

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
    ]

    # Parámetros de simulación
    visualize_during_simulation = True  # Alternar entre simulación con o sin visualización en tiempo real

    # Simulación con visualización interactiva
    print("\nIniciando simulación con visualización interactiva...\n")
    if visualize_during_simulation:
        # Visualización interactiva con botones y ciclos impresos en consola
        visualize_with_pygame(
            program, registers, memory, pipeline, execute_cycle, buttons
        )

if __name__ == "__main__":
    main()
