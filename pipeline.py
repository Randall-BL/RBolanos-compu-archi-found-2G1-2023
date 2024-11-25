import pygame
from memory_instructions import load_instruction, store_instruction
from hazard_unit import Hazard_Unit

#pipeline.py
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
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
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

def execute_cycle(program, registers, memory, pipeline, program_counter, hazard_unit=None):
    """
    Simula un ciclo del pipeline con soporte para unidad de riesgos.
    """
    # Verificar riesgos al inicio del ciclo
    if hazard_unit:
        if hazard_unit.handle_hazards(pipeline):
            if hazard_unit.stall_pipeline:
                print("Pipeline stalled debido a riesgo detectado")
                return program_counter

    # Write Back (WB)
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
        pipeline["WB"] = None

    # Memory Access (MEM)
    if pipeline["MEM"]:
        instr = pipeline["MEM"]
        if instr["opcode"] == "LOAD":
            value = memory[instr["src1"]]
            instr["result"] = value
            memory[instr["src1"]] = 0
            print(f"LOAD - Cargando desde memoria[{instr['src1']}] a R{instr['dest']}: {instr['result']}")
            print(f"LOAD - Memoria[{instr['src1']}] se ha puesto a 0")
        elif instr["opcode"] == "STORE":
            memory[instr["dest"]] = registers[instr["src1"]]
            print(f"STORE - Guardando R{instr['src1']}({registers[instr['src1']]}) en memoria[{instr['dest']}]")
        pipeline["WB"] = instr
        print(f"MEM - Pasando a WB: {instr}")
        pipeline["MEM"] = None

    # Execution (EX)
    if pipeline["EX"]:
        instr = pipeline["EX"]
        # Usar valores forwarded si están disponibles y la unidad de riesgos está activa
        if hazard_unit and hazard_unit.forwarding_enabled:
            src1_val = instr.get('forward_src1', registers[instr["src1"]])
            src2_val = instr.get('forward_src2', registers[instr["src2"]]) if "src2" in instr else None

            if instr["opcode"] == "ADD":
                instr["result"] = src1_val + src2_val
            elif instr["opcode"] == "SUB":
                instr["result"] = src1_val - src2_val
            elif instr["opcode"] == "MUL":
                instr["result"] = src1_val * src2_val
            elif instr["opcode"] == "DIV":
                instr["result"] = src1_val // src2_val if src2_val != 0 else 0
            elif instr["opcode"] == "MOD":
                instr["result"] = src1_val % src2_val if src2_val != 0 else 0
        else:
            # Comportamiento original sin forwarding
            if instr["opcode"] == "ADD":
                instr["result"] = registers[instr["src1"]] + registers[instr["src2"]]
            elif instr["opcode"] == "SUB":
                instr["result"] = registers[instr["src1"]] - registers[instr["src2"]]
            elif instr["opcode"] == "MUL":
                instr["result"] = registers[instr["src1"]] * registers[instr["src2"]]
            elif instr["opcode"] == "DIV":
                instr["result"] = registers[instr["src1"]] // registers[instr["src2"]] if registers[instr["src2"]] != 0 else 0
            elif instr["opcode"] == "MOD":
                instr["result"] = registers[instr["src1"]] % registers[instr["src2"]] if registers[instr["src2"]] != 0 else 0

        # Manejo de saltos con predicción si está habilitada
        if instr["opcode"] in ["BEQ", "BNE"]:
            taken = False
            if instr["opcode"] == "BEQ":
                taken = registers[instr["src1"]] == registers[instr["src2"]]
            elif instr["opcode"] == "BNE":
                taken = registers[instr["src1"]] != registers[instr["src2"]]

            if taken:
                if hazard_unit and hazard_unit.branch_prediction_enabled:
                    if not hazard_unit.last_prediction:
                        # Predicción incorrecta
                        program_counter += instr["offset"]
                        hazard_unit.flush_pipeline(pipeline)
                else:
                    program_counter += instr["offset"]
                print(f"EX - {instr['opcode']} tomado, salto a la dirección {program_counter}.")
            else:
                print(f"EX - {instr['opcode']} no tomado.")

        elif instr["opcode"] == "SWAP":
            registers[instr["dest"]], registers[instr["src1"]] = registers[instr["src1"]], registers[instr["dest"]]
            print(f"EX - SWAP: R{instr['dest']}({registers[instr['dest']]}) <-> R{instr['src1']}({registers[instr['src1']]})")

        pipeline["MEM"] = instr
        print(f"EX - Pasando a MEM: {instr}")
        pipeline["EX"] = None

    # Instruction Decode (ID)
    if pipeline["ID"]:
        instr = pipeline["ID"]
        if not (hazard_unit and hazard_unit.stall_pipeline):
            pipeline["EX"] = instr
            print(f"ID - Pasando a EX: {instr}")
            pipeline["ID"] = None

    # Instruction Fetch (IF)
    if pipeline["IF"] is None and program_counter < len(program):
        next_instr = program[program_counter].copy()
        
        # Predicción de saltos si está habilitada
        if hazard_unit and hazard_unit.branch_prediction_enabled:
            if next_instr["opcode"] in ["BEQ", "BNE"]:
                prediction = hazard_unit.predict_branch(next_instr)
                next_instr["predicted_taken"] = prediction
                if prediction:
                    program_counter += next_instr["offset"]
        
        pipeline["IF"] = next_instr
        pipeline["IF"]["delay"] = True
        print(f"IF - Cargando instrucción: {pipeline['IF']}")
        program_counter += 1

    # Actualizar PC y manejar delay
    registers[8] = program_counter
    
    if pipeline["IF"] and "delay" in pipeline["IF"]:
        del pipeline["IF"]["delay"]
    elif pipeline["IF"] and pipeline["ID"] is None and not (hazard_unit and hazard_unit.stall_pipeline):
        pipeline["ID"] = pipeline["IF"]
        pipeline["IF"] = None

    # Mostrar estado actual
    print(f"Estado del pipeline: {pipeline}")
    print(f"Registros: {registers}\n")
    if hazard_unit:
        print(f"Estadísticas de riesgos: {hazard_unit.get_statistics()}")
    print(f"Program Counter (PC): {program_counter}")

    return program_counter

def execute_instruction(instr, registers):
    """Ejecuta la instrucción dada y devuelve el resultado."""
    if instr["opcode"] == "ADD":
        return registers[instr["src1"]] + registers[instr["src2"]]
    elif instr["opcode"] == "SUB":
        return registers[instr["src1"]] - registers[instr["src2"]]
    elif instr["opcode"] == "MUL":
        return registers[instr["src1"]] * registers[instr["src2"]]
    elif instr["opcode"] == "DIV":
        return registers[instr["src1"]] // registers[instr["src2"]] if registers[instr["src2"]] != 0 else 0

def instruction_summary(instr, registers):
    """Devuelve un resumen en texto de la instrucción y sus operandos para mostrar en consola."""
    if instr["opcode"] in ["ADD", "SUB", "MUL", "DIV"]:
        return f"R{instr['src1']}({registers[instr['src1']]}) {instr['opcode']} R{instr['src2']}({registers[instr['src2']]})"
