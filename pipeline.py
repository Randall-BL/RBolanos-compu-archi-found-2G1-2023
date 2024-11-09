import pygame

# Configuración inicial de Pygame
WIDTH, HEIGHT = 900, 600
BG_COLOR = (30, 30, 30)  # Fondo gris oscuro
FONT_COLOR = (255, 255, 255)  # Texto blanco
ACTIVE_COLOR = (50, 150, 50)  # Verde para etapas activas
INACTIVE_COLOR = (100, 100, 100)  # Gris para etapas vacías
FONT_SIZE = 20
PIPELINE_START_Y = 50
REGISTER_START_Y = 250
MEMORY_START_Y = 400

def initialize_pygame():
    """Inicializa Pygame y retorna la ventana y la fuente."""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Simulación del Procesador")
    font = pygame.font.Font(None, FONT_SIZE)
    return screen, font

def draw_pipeline(screen, font, pipeline):
    """Dibuja el estado del pipeline en la pantalla con colores dinámicos."""
    stages = ["IF", "ID", "EX", "MEM", "WB"]
    y = PIPELINE_START_Y
    block_width = 160
    block_height = 50
    spacing = 20

    for i, stage in enumerate(stages):
        instruction = pipeline.get(stage, None)
        color = ACTIVE_COLOR if instruction else INACTIVE_COLOR
        x = 20 + i * (block_width + spacing)
        pygame.draw.rect(screen, color, (x, y, block_width, block_height))

        # Mostrar el contenido de la etapa
        text = f"{stage}: {instruction['opcode'] if instruction else 'Vacío'}"
        render_text = font.render(text, True, FONT_COLOR)
        screen.blit(render_text, (x + 10, y + 15))

def draw_registers(screen, font, registers):
    """Dibuja los valores de los registros."""
    y = REGISTER_START_Y
    x_start = 50
    spacing_x = 150
    spacing_y = 30

    text = "Registros:"
    render_text = font.render(text, True, FONT_COLOR)
    screen.blit(render_text, (x_start, y))

    for i, value in enumerate(registers):
        text = f"R{i}: {value}"
        render_text = font.render(text, True, FONT_COLOR)
        screen.blit(render_text, (x_start + (i % 4) * spacing_x, y + 30 + (i // 4) * spacing_y))

def draw_memory(screen, font, memory, start=0, end=8):
    """Dibuja un segmento de la memoria."""
    y = MEMORY_START_Y
    x_start = 50
    spacing_x = 150
    spacing_y = 30

    text = f"Memoria (Direcciones {start}-{end - 1}):"
    render_text = font.render(text, True, FONT_COLOR)
    screen.blit(render_text, (x_start, y))

    for i in range(start, min(end, len(memory))):
        text = f"[{i}]: {memory[i]}"
        render_text = font.render(text, True, FONT_COLOR)
        screen.blit(render_text, (x_start + (i % 4) * spacing_x, y + 30 + (i // 4) * spacing_y))

def initialize_pipeline():
    """Inicializa el pipeline vacío y el contador del programa."""
    pipeline = {"IF": None, "ID": None, "EX": None, "MEM": None, "WB": None}
    program_counter = 0
    return pipeline, program_counter

def execute_cycle(program, registers, memory, pipeline, program_counter):
    """
    Simula un ciclo del pipeline.
    Parámetros:
    - program: Lista de instrucciones.
    - registers: Lista de registros.
    - memory: Lista que representa la memoria.
    - pipeline: Diccionario que representa el estado del pipeline.
    - program_counter: Contador del programa.

    Retorna:
    - program_counter actualizado.
    """
    # Write Back (WB)
    if pipeline["WB"]:
        instr = pipeline["WB"]
        if instr["opcode"] == "ADD":
            registers[instr["dest"]] = instr["result"]
        elif instr["opcode"] == "SUB":
            registers[instr["dest"]] = instr["result"]
        print(f"WB - Escribiendo en R{instr['dest']}: {registers[instr['dest']]}")
        pipeline["WB"] = None  # Limpiar la etapa WB

    # Memory Access (MEM)
    if pipeline["MEM"]:
        instr = pipeline["MEM"]
        pipeline["WB"] = instr
        print(f"MEM - Pasando a WB: {instr}")
        pipeline["MEM"] = None

    # Execution (EX)
    if pipeline["EX"]:
        instr = pipeline["EX"]
        if instr["opcode"] == "ADD":
            instr["result"] = registers[instr["src1"]] + registers[instr["src2"]]
            print(f"EX - Calculando: R{instr['src1']}({registers[instr['src1']]}) + R{instr['src2']}({registers[instr['src2']]}) = {instr['result']}")
        elif instr["opcode"] == "SUB":
            instr["result"] = registers[instr["src1"]] - registers[instr["src2"]]
            print(f"EX - Calculando: R{instr['src1']}({registers[instr['src1']]}) - R{instr['src2']}({registers[instr['src2']]}) = {instr['result']}")
        pipeline["MEM"] = instr
        print(f"EX - Pasando a MEM: {instr}")
        pipeline["EX"] = None

    # Instruction Decode (ID)
    if pipeline["ID"]:
        instr = pipeline["ID"]
        pipeline["EX"] = instr
        print(f"ID - Pasando a EX: {instr}")
        pipeline["ID"] = None

    # Instruction Fetch (IF)
    if pipeline["IF"] is None and program_counter < len(program):
        pipeline["IF"] = program[program_counter]
        print(f"IF - Cargando instrucción: {pipeline['IF']}")
        program_counter += 1

    # Mover la instrucción de IF a ID solo después de un ciclo
    if pipeline["IF"] and pipeline["ID"] is None and "delay" not in pipeline["IF"]:
        pipeline["IF"]["delay"] = True  # Introducir un retraso
    elif pipeline["IF"] and "delay" in pipeline["IF"]:
        pipeline["ID"] = pipeline["IF"]
        print(f"IF - Pasando a ID: {pipeline['IF']}")
        pipeline["IF"] = None

    print(f"Estado del pipeline: {pipeline}")
    print(f"Registros: {registers}\n")
    return program_counter