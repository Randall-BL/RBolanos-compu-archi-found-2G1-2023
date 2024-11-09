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

    # Carga del programa con las instrucciones
    current_program = program()

    # Parámetros de simulación
    cycles_to_run = 10  # Número de ciclos a simular
    visualize_during_simulation = True  # Alternar entre simulación con o sin visualización en tiempo real

    # Simulación del pipeline
    print("\nIniciando simulación del pipeline...\n")
    if visualize_during_simulation:
        # Visualización en tiempo real
        visualize_with_pygame(
            current_program, registers, memory, pipeline, 
            lambda p, r, m, pl, pc: execute_cycle(p, r, m, pl, pc)
        )
    else:
        # Simulación solo en consola
        for cycle in range(cycles_to_run):
            print(f"\nCiclo {cycle + 1}")
            program_counter = execute_cycle(current_program, registers, memory, pipeline, program_counter)

            # Imprimir el estado actual en consola
            print(f"Pipeline: {pipeline}")
            print(f"Registros: {registers}")

        # Visualización final con Pygame
        print("\nMostrando visualización gráfica final...")
        visualize_with_pygame(pipeline, registers, memory, duration=10)  # Visualizar por 10 segundos

if __name__ == "__main__":
    main()
