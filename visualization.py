import pygame
import threading
import time
import threading

from hazard_unit import Hazard_Unit

# visualization.py
# Configuración de la ventana
WINDOW_WIDTH, WINDOW_HEIGHT = 900, 620
BG_COLOR = (30, 30, 30)  # Fondo gris oscuro
FONT_COLOR = (255, 255, 255)  # Texto blanco
FONT_SIZE = 24

ACTIVE_COLOR = (50, 150, 50)  # Verde para etapas activas
INACTIVE_COLOR = (100, 100, 100)  # Gris para etapas vacías

BUTTON_COLOR = (100, 100, 255)
BUTTON_HOVER_COLOR = (150, 150, 255)
BUTTON_TEXT_COLOR = (255, 255, 255)

# Constantes del tamaño de los botones
MODE_BUTTON_WIDTH = 200
MODE_BUTTON_HEIGHT = 30
MODE_BUTTON_COLOR = (100, 100, 255)
MODE_BUTTON_HOVER_COLOR = (150, 150, 255)

# Dimensiones del botón
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 50
BUTTON_SPACING = 20

selected_instruction = None  # Inicialmente ninguna instruccion esta seleccionada

def initialize_pygame():
    """
    Inicializa Pygame y configura la ventana y fuente.
    """
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Simulación del Procesador")
    font = pygame.font.Font(None, FONT_SIZE)
    return screen, font

def draw_buttons(screen, font, buttons):
    """
    Dibuja los botones distribuidos en múltiples filas y asegura que cada botón tenga un rectángulo asignado.
    """
    x_start = 20  # Coordenada X inicial de los botones
    y = WINDOW_HEIGHT - 150  # Coordenada Y inicial de los botones (un poco más arriba)
    max_buttons_per_row = 5  # Número máximo de botones por fila (ajústalo según el espacio)
    buttons_in_row = 0  # Contador de botones en la fila actual

    for button in buttons:
        # Crear el rectángulo del botón si no existe
        rect = pygame.Rect(x_start, y, BUTTON_WIDTH, BUTTON_HEIGHT)
        button["rect"] = rect

        # Determinar el color según si está en hover
        color = BUTTON_HOVER_COLOR if button.get("hover", False) else BUTTON_COLOR

        # Dibujar el botón
        pygame.draw.rect(screen, color, rect)
        text = font.render(button["label"], True, BUTTON_TEXT_COLOR)
        screen.blit(text, (x_start + 20, y + 15))

        # Ajustar la posición para el próximo botón
        x_start += BUTTON_WIDTH + BUTTON_SPACING
        buttons_in_row += 1

        # Si alcanzamos el máximo por fila, pasar a la siguiente fila
        if buttons_in_row >= max_buttons_per_row:
            x_start = 20  # Reiniciar X para la nueva fila
            y += BUTTON_HEIGHT + 10  # Mover hacia abajo (nueva fila)
            buttons_in_row = 0

def draw_mode_buttons(screen, font, mode_buttons, current_mode):
    """
    Dibuja los botones de modo del procesador
    """
    for btn in mode_buttons:
        # Determinar el color del botón
        color = MODE_BUTTON_HOVER_COLOR if btn["hover"] else MODE_BUTTON_COLOR
        if btn["label"] == current_mode:
            color = (50, 200, 50)  # Verde para el modo activo
        
        # Dibujar el botón
        pygame.draw.rect(screen, color, btn["rect"])
        
        # Dibujar el texto del botón
        text = font.render(btn["label"], True, BUTTON_TEXT_COLOR)
        text_rect = text.get_rect(center=btn["rect"].center)
        screen.blit(text, text_rect)

def draw_header(screen, font, cycle, start_time, registers):
    """
    Dibuja el encabezado con ciclo, tiempo transcurrido y PC (R8).
    """
    current_time = time.time() - start_time
    header_texts = [
        f"Ciclo: {cycle}",
        f"Tiempo: {current_time:.2f} segundos",
        f"PC (R8): {registers[8]}"  # Obtener el valor del registro R8
    ]

    y = 10
    for text in header_texts:
        render = font.render(text, True, FONT_COLOR)
        screen.blit(render, (10, y))
        y += 30

def draw_pipeline(screen, font, pipeline):
    """
    Dibuja el estado del pipeline con colores dinámicos.
    """
    stages = ["IF", "ID", "EX", "MEM", "WB"]
    x_start = 50
    y = 100
    block_width = 120
    block_height = 50
    spacing = 20

    for i, stage in enumerate(stages):
        instruction = pipeline.get(stage, None)
        color = ACTIVE_COLOR if instruction else INACTIVE_COLOR
        pygame.draw.rect(screen, color, (x_start + i * (block_width + spacing), y, block_width, block_height))
        text = f"{stage}: {instruction['opcode'] if instruction else 'Vacío'}"
        render = font.render(text, True, FONT_COLOR)
        screen.blit(render, (x_start + i * (block_width + spacing) + 10, y + 15))

def draw_registers(screen, font, registers):
    """
    Dibuja el estado de los registros en forma de tabla.
    """
    x_start = 50
    y_start = 200
    spacing_x = 150
    spacing_y = 30

    for i, value in enumerate(registers):
        text = f"R{i}: {value}"
        render = font.render(text, True, FONT_COLOR)
        screen.blit(render, (x_start + (i % 4) * spacing_x, y_start + (i // 4) * spacing_y))

def draw_memory(screen, font, memory, start=0, end=8):
    """
    Dibuja un segmento de la memoria.
    """
    x_start = 50
    y_start = 350
    spacing_x = 150
    spacing_y = 30

    for i in range(start, min(end, len(memory))):
        text = f"[{i}]: {memory[i]}"
        render = font.render(text, True, FONT_COLOR)
        screen.blit(render, (x_start + (i % 4) * spacing_x, y_start + (i // 4) * spacing_y))

def draw_interface(screen, font, pipeline, registers, memory, buttons, cycle, start_time):
    """
    Dibuja todos los elementos en la interfaz gráfica.
    """
    # Limpiar la pantalla
    screen.fill(BG_COLOR)

    # Dibujar todos los elementos visuales
    draw_header(screen, font, cycle, start_time, registers)  # Obtener PC desde registers[8]
    draw_pipeline(screen, font, pipeline)
    draw_registers(screen, font, registers)
    draw_memory(screen, font, memory)
    draw_buttons(screen, font, buttons)

def execute_pipeline_in_thread(program, registers, memory, pipeline, program_counter, execute_cycle, screen, font, buttons, cycle, start_time):
    """
    Ejecuta el pipeline en un hilo separado para no bloquear la interfaz gráfica.
    """
    for i in range(6):  # Seis ciclos para que la instrucción pase por todas las etapas
        # Dibujar la interfaz después de cada ciclo
        draw_interface(screen, font, pipeline, registers, memory, buttons, cycle + i, start_time)
        pygame.display.flip()

        # Ejecutar un ciclo del pipeline
        program_counter = execute_cycle(program, registers, memory, pipeline, program_counter)

        # Mostrar el estado actualizado después de ejecutar el ciclo
        draw_interface(screen, font, pipeline, registers, memory, buttons, cycle + i, start_time)
        pygame.display.flip()

        # Retrasar para visualizar claramente cada ciclo
        time.sleep(0.5)

def execute_pipeline_completa(program, registers, memory, pipeline, program_counter, execute_cycle, screen, font, buttons, cycle, start_time, num_instrucciones, hazard_unit=None):
    """
    Ejecuta el pipeline de forma segmentada, permitiendo múltiples instrucciones simultáneas.
    """
    def run_pipeline():
        nonlocal program_counter
        total_cycles = len(program) + 4 + num_instrucciones
        
        print(f"\nIniciando ejecución segmentada con {len(program)} instrucciones")
        print(f"Ciclos totales necesarios: {total_cycles}")
        print(f"Modo de ejecución: {'Con unidad de riesgos' if hazard_unit else 'Básico'}")
        
        for i in range(total_cycles):
            print(f"\nCiclo global {i + 1} de {total_cycles}")
            
            # Actualizar la interfaz
            draw_interface(screen, font, pipeline, registers, memory, buttons, cycle + i, start_time)
            
            # Mostrar estadísticas de la unidad de riesgos si está activa
            if hazard_unit:
                stats = hazard_unit.get_statistics()
                y_pos = 180
                for stat_name, value in stats.items():
                    text = font.render(f"{stat_name}: {value}", True, FONT_COLOR)
                    screen.blit(text, (WINDOW_WIDTH - 200, y_pos))
                    y_pos += 25
            
            pygame.display.flip()

            # Ejecutar un ciclo del pipeline con la unidad de riesgos
            program_counter = execute_cycle(program, registers, memory, pipeline, program_counter, hazard_unit)
            
            # Mostrar estado actual del pipeline
            print("Estado del pipeline:")
            for stage, instr in pipeline.items():
                print(f"{stage}: {instr if instr else 'vacío'}")
            
            # Actualizar la interfaz después del ciclo
            draw_interface(screen, font, pipeline, registers, memory, buttons, cycle + i, start_time)
            
            # Mostrar estadísticas actualizadas
            if hazard_unit:
                stats = hazard_unit.get_statistics()
                y_pos = 180
                for stat_name, value in stats.items():
                    text = font.render(f"{stat_name}: {value}", True, FONT_COLOR)
                    screen.blit(text, (WINDOW_WIDTH - 200, y_pos))
                    y_pos += 25
            
            pygame.display.flip()
            
            if is_pipeline_empty(pipeline) and i >= len(program):
                print("Pipeline vacío y todas las instrucciones completadas")
                break
            
            time.sleep(0.5)

        print(f"\nEjecución segmentada completada después de {total_cycles} ciclos")
        if hazard_unit:
            print("Estadísticas finales de la unidad de riesgos:")
            for stat_name, value in hazard_unit.get_statistics().items():
                print(f"{stat_name}: {value}")

    pipeline_thread = threading.Thread(target=run_pipeline)
    pipeline_thread.start()
    pipeline_thread.join()


def is_pipeline_empty(pipeline):
    return all(stage is None for stage in pipeline.values())

def execute_pipeline_step(program, registers, memory, pipeline, program_counter, current_stage):
    """
    Ejecuta solo una etapa específica del pipeline para la instrucción dada.
    """
    stages = ["IF", "ID", "EX", "MEM", "WB"]
    if current_stage < len(stages):
        stage = stages[current_stage]
        print(f"\n---- Ejecutando etapa: {stage} ----")

def execute_pipeline_step(program, registers, memory, pipeline, program_counter, current_stage):
    stages = ["IF", "ID", "EX", "MEM", "WB"]
    if current_stage < len(stages):
        stage = stages[current_stage]
        print(f"\n---- Ejecutando etapa: {stage} ----")

        if stage == "IF":
            # Instruction Fetch (IF)
            if pipeline["IF"] is None and program_counter < len(program):
                pipeline["IF"] = program[program_counter]
                pipeline["IF"]["delay"] = True  # Mantener en IF un ciclo
                print(f"IF - Cargando instrucción: {pipeline['IF']}")
                program_counter += 1

            # Registrar el PC en un registro especial
            registers[8] = program_counter

            if pipeline["IF"] and "delay" in pipeline["IF"]:
                del pipeline["IF"]["delay"]
                print("IF - Delay eliminado, listo para mover a ID")
            elif pipeline["IF"] and pipeline["ID"] is None:
                pipeline["ID"] = pipeline["IF"]
                print(f"IF - Pasando instrucción a ID: {pipeline['ID']}")
                pipeline["IF"] = None

        elif stage == "ID":
            if pipeline["ID"]:
                instr = pipeline["ID"]
                pipeline["EX"] = instr
                print(f"ID - Pasando a EX: {instr}")
                pipeline["ID"] = None  # Limpiar ID

        elif stage == "EX":
            if pipeline["EX"]:
                instr = pipeline["EX"]
                if instr["opcode"] == "ADD":
                    instr["result"] = registers[instr["src1"]] + registers[instr["src2"]]
                    print(f"EX - Calculando: R{instr['src1']}({registers[instr['src1']]}) + R{instr['src2']}({registers[instr['src2']]}) = {instr['result']}")
                elif instr["opcode"] == "SUB":
                    instr["result"] = registers[instr["src1"]] - registers[instr["src2"]]
                    print(f"EX - Calculando: R{instr['src1']}({registers[instr['src1']]}) - R{instr['src2']}({registers[instr['src2']]}) = {instr['result']}")
                elif instr["opcode"] == "MUL":
                    instr["result"] = registers[instr["src1"]] * registers[instr["src2"]]
                    print(f"EX - Calculando: R{instr['src1']}({registers[instr['src1']]}) * R{instr['src2']}({registers[instr['src2']]}) = {instr['result']}")
                elif instr["opcode"] == "DIV":
                    instr["result"] = registers[instr["src1"]] // registers[instr["src2"]] if registers[instr["src2"]] != 0 else 0
                    print(f"EX - Calculando: R{instr['src1']}({registers[instr['src1']]}) / R{instr['src2']}({registers[instr['src2']]}) = {instr['result']}")
                elif instr["opcode"] == "MOD":
                    instr["result"] = registers[instr["src1"]] % registers[instr["src2"]] if registers[instr["src2"]] != 0 else 0
                    print(f"EX - Calculando: R{instr['src1']}({registers[instr['src1']]}) % R{instr['src2']}({registers[instr['src2']]}) = {instr['result']}")
                elif instr["opcode"] == "BNE":
                    if registers[instr["src1"]] != registers[instr["src2"]]:
                        program_counter += instr["offset"]
                        print(f"EX - BNE tomado, salto a la dirección {program_counter}.")
                    else:
                        print("EX - BNE no tomado.")
                elif instr["opcode"] == "BEQ":
                    if registers[instr["src1"]] == registers[instr["src2"]]:
                        program_counter += instr["offset"]
                        print(f"EX - BEQ tomado, salto a la dirección {program_counter}.")
                    else:
                        print("EX - BEQ no tomado.")
                elif instr["opcode"] == "SWAP":
                    registers[instr["dest"]], registers[instr["src1"]] = registers[instr["src1"]], registers[instr["dest"]]
                    print(f"EX - SWAP: R{instr['dest']}({registers[instr['dest']]}) <-> R{instr['src1']}({registers[instr['src1']]})")
                pipeline["MEM"] = instr
                print(f"EX - Pasando a MEM: {instr}")
                pipeline["EX"] = None  # Limpiar EX

        elif stage == "MEM":
            if pipeline["MEM"]:
                instr = pipeline["MEM"]
                if instr["opcode"] == "LOAD":
                    value = memory[instr["src1"]]  # Obtener el valor en memoria
                    instr["result"] = value
                    memory[instr["src1"]] = 0  # Limpiar memoria después de cargar
                    print(f"LOAD - Cargando desde memoria[{instr['src1']}] a R{instr['dest']}: {instr['result']}")
                    print(f"LOAD - Memoria[{instr['src1']}] se ha puesto a 0")
                elif instr["opcode"] == "STORE":
                    memory[instr["dest"]] = registers[instr["src1"]]  # Guardar en memoria
                    print(f"STORE - Guardando R{instr['src1']}({registers[instr['src1']]}) en memoria[{instr['dest']}]")
                pipeline["WB"] = instr
                print(f"MEM - Pasando a WB: {instr}")
                pipeline["MEM"] = None  # Limpiar MEM después de pasar a WB

        elif stage == "WB":
            if pipeline["WB"]:
                instr = pipeline["WB"]
                if instr["opcode"] in ["ADD", "SUB", "MUL", "DIV", "MOD"]:
                    registers[instr["dest"]] = instr["result"]
                    print(f"WB - Escribiendo en R{instr['dest']}: {registers[instr['dest']]}")
                elif instr["opcode"] == "LOAD":
                    registers[instr["dest"]] = instr["result"]
                    print(f"WB - Cargando desde memoria[{instr['src1']}] a R{instr['dest']}: {instr['result']}")
                elif instr["opcode"] == "STORE":
                    print(f"WB - STORE completado, no hay cambios en registros.")
                elif instr["opcode"] == "SWAP":
                    print(f"WB - SWAP completado entre R{instr['dest']} y R{instr['src1']}.")
                pipeline["WB"] = None  # Limpiar la etapa WB

        # Mostrar estado actual del pipeline
        print_pipeline_state(pipeline, registers, memory, program_counter)
    else:
        print("\n--- Todas las etapas completadas ---")
        print_pipeline_state(pipeline, registers, memory, program_counter)

    if is_pipeline_empty(pipeline) and program_counter >= len(program):
        print("\n--- Pipeline vacío y programa completado. ---")
        return program_counter

    return program_counter

def print_pipeline_state(pipeline, registers, memory, program_counter):
    """
    Muestra el estado actual del pipeline.
    """
    print("\n--- Estado actual del pipeline ---")
    for stage, instr in pipeline.items():
        print(f"{stage}: {instr}")
    print(f"Estado del pipeline: {pipeline}")
    print(f"Registros: {registers}\n")
    print(f"Program Counter (PC): {program_counter}")


# Ejecución del pipeline a un ritmo constante
def draw_input_box(screen, font, input_box, input_text, active):
    color = pygame.Color('dodgerblue2') if active else pygame.Color('lightskyblue3')
    pygame.draw.rect(screen, color, input_box, 2)
    label = font.render("Tiempo de ciclo(s):", True, pygame.Color('white'))
    screen.blit(label, (input_box.x, input_box.y - 20))
    text_surface = font.render(input_text, True, pygame.Color('white'))
    screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))

def handle_text_input(event, input_text, input_active, input_box, mouse_pos):
    if event.type == pygame.MOUSEBUTTONDOWN:
        input_active = input_box.collidepoint(mouse_pos)
    
    if event.type == pygame.KEYDOWN and input_active:
        if event.key == pygame.K_RETURN:
            return input_text, False
        elif event.key == pygame.K_BACKSPACE:
            input_text = input_text[:-1]
        else:
            if event.unicode.replace('.', '').isdigit():
                input_text += event.unicode
    
    return input_text, input_active

def execute_pipeline_with_timing(program, registers, memory, pipeline, execute_cycle, cycle_time,screen,font,buttons,start_time):
    program_counter = 0
    cycle = 0

    while not is_pipeline_empty(pipeline) or program_counter < len(program):
        for i in range(6):  # Seis ciclos para que la instrucción pase por todas las etapas
            print(f"\nCiclo {cycle + i}")
            # Mostrar el estado actualizado después de ejecutar el ciclo
            draw_interface(screen, font, pipeline, registers, memory, buttons, cycle + i, start_time)
            pygame.display.flip()
            program_counter = execute_cycle(program, registers, memory, pipeline, program_counter)
            print_pipeline_state(pipeline, registers, memory, program_counter)
            # Mostrar el estado actualizado después de ejecutar el ciclo
            draw_interface(screen, font, pipeline, registers, memory, buttons, cycle + i, start_time)
            pygame.display.flip()
            time.sleep(cycle_time)
            cycle += 1

    print("\n--- Simulación Finalizada ---")
    print(f"Registros finales: {registers}")

def visualize_with_pygame(program, registers, memory, pipeline, execute_cycle, buttons):
    global selected_instruction

    buttons.append({"label": "Ejecutar", "instruction": None, "rect": None, "hover": False})
    buttons.append({"label": "Step-by-Step", "instruction": None, "rect": None, "hover": False})
    buttons.append({"label": "En tiempo", "instruction": None, "rect": None, "hover": False})
    buttons.append({"label": "Completa", "instruction": None, "rect": None, "hover": False})

    # Botones de modo
    mode_buttons = [
        {
            "label": "Modo Básico",
            "rect": pygame.Rect(WINDOW_WIDTH - 220, 10, MODE_BUTTON_WIDTH, MODE_BUTTON_HEIGHT),
            "hazard_config": None,
            "hover": False
        },
        {
            "label": "Con Forwarding",
            "rect": pygame.Rect(WINDOW_WIDTH - 220, 50, MODE_BUTTON_WIDTH, MODE_BUTTON_HEIGHT),
            "hazard_config": {"forwarding": True, "prediction": False},
            "hover": False
        },
        {
            "label": "Con Predicción",
            "rect": pygame.Rect(WINDOW_WIDTH - 220, 90, MODE_BUTTON_WIDTH, MODE_BUTTON_HEIGHT),
            "hazard_config": {"forwarding": False, "prediction": True},
            "hover": False
        },
        {
            "label": "Modo Completo",
            "rect": pygame.Rect(WINDOW_WIDTH - 220, 130, MODE_BUTTON_WIDTH, MODE_BUTTON_HEIGHT),
            "hazard_config": {"forwarding": True, "prediction": True},
            "hover": False
        }
    ]

    screen, font = initialize_pygame()
    clock = pygame.time.Clock()

    program_counter = 0
    cycle = 1
    start_time = time.time()

    current_stage = 0
    stages = ["IF", "ID", "EX", "MEM", "WB"]

    draw_buttons(screen, font, buttons)
    running = True

    # Ejecución con tiempo
    input_active = False
    input_text = "0.1"
    cycle_time = 0.1
    input_box = pygame.Rect(screen.get_width() - 140, 60, 100, 32)

    # Ejecución completa
    program_queue = []  # Nueva lista para almacenar todas las instrucciones seleccionadas

    current_mode = "Modo Básico"
    hazard_unit = None
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for btn in mode_buttons:
                    if btn["rect"].collidepoint(mouse_pos):
                        current_mode = btn["label"]
                        if btn["hazard_config"] is None:
                            hazard_unit = None
                        else:
                            hazard_unit = Hazard_Unit(
                                forwarding_enabled=btn["hazard_config"]["forwarding"],
                                branch_prediction_enabled=btn["hazard_config"]["prediction"]
                            )
                        print(f"Cambiado a {current_mode}")
                        break
                for button in buttons:
                    if button["rect"].collidepoint(mouse_pos):
                        if button["label"] == "Ejecutar":
                            if selected_instruction:
                                execute_pipeline_in_thread([selected_instruction], registers, memory, pipeline, program_counter,
                                    execute_cycle, screen, font, buttons, 
                                    cycle, start_time)
                                selected_instruction = None
                            else:
                                print("Primero selecciona una instrucción")
                        elif button["label"] == "Step-by-Step":
                            if selected_instruction:
                                program_counter = execute_pipeline_step(
                                    [selected_instruction], registers, memory, pipeline, 
                                    program_counter, current_stage)
                                program_queue.clear()  # Limpiar el programa después de la ejecución
                                current_stage += 1
                                if current_stage >= 6:
                                    current_stage = 0
                                    selected_instruction = None
                                    if is_pipeline_empty(pipeline):
                                        program_counter = 0
                                        pipeline = {stage: None for stage in stages}
                            else:
                                print("Primero selecciona una instrucción para Step-by-Step")
                        elif button["label"] == "En tiempo":
                            if 0.01 <= cycle_time <= 0.1 and selected_instruction:
                                execute_pipeline_with_timing(
                                    [selected_instruction], registers, memory, pipeline, execute_cycle, cycle_time,screen,
                                    font,buttons,start_time)
                                selected_instruction = None
                                program_queue.clear()  # Limpiar el programa después de la ejecución
                            else:
                                print("Tiempo inválido o no hay instrucción seleccionada")
                        elif button["label"] == "Completa":
                            if 0 < len(program_queue):
                                print(f"\nIniciando ejecución segmentada con {len(program_queue)} instrucciones")
                                instructions_to_execute = program_queue.copy()  # Hacer una copia de las instrucciones
                                
                                # Ejecutar todas las instrucciones en modo pipeline
                                execute_pipeline_completa(
                                    instructions_to_execute,
                                    registers, 
                                    memory, 
                                    pipeline, 
                                    program_counter, 
                                    execute_cycle, 
                                    screen, 
                                    font, 
                                    buttons, 
                                    cycle, 
                                    start_time,
                                    num_instrucciones=len(instructions_to_execute),
                                    hazard_unit=hazard_unit
                                )
                                
                                # Limpiar la cola solo después de que todas las instrucciones hayan terminado
                                program_queue.clear()
                                print("\nTodas las instrucciones han sido ejecutadas")
                            else:
                                print("Seleccione al menos una instrucción para ejecutar")
                        else:
                            selected_instruction = button["instruction"]
                            program_queue.append(selected_instruction)
                            current_stage = 0
                            print(f"Instrucción seleccionada: {selected_instruction}")
                        

            input_text, input_active = handle_text_input(event, input_text, input_active, input_box, mouse_pos)
            try:
                cycle_time = float(input_text)
            except ValueError:
                pass

        for button in buttons:
            if "rect" in button:
                button["hover"] = button["rect"].collidepoint(mouse_pos)
        draw_interface(screen, font, pipeline, registers, memory, buttons, cycle, start_time)
        draw_input_box(screen, font, input_box, input_text, input_active)
        
        draw_mode_buttons(screen, font, mode_buttons, current_mode)
        if hazard_unit:
            stats = hazard_unit.get_statistics()
            y_pos = 180
            for stat_name, value in stats.items():
                text = font.render(f"{stat_name}: {value}", True, FONT_COLOR)
                screen.blit(text, (WINDOW_WIDTH - 200, y_pos))
                y_pos += 25
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


