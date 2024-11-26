class HazardType:
    RAW = "Read After Write"
    WAW = "Write After Write"
    WAR = "Write After Read"
    CONTROL = "Control Hazard"
    STRUCTURAL = "Structural Hazard"

class Hazard_Unit:
    def __init__(self, forwarding_enabled=False, branch_prediction_enabled=False):
        # Configuración
        self.forwarding_enabled = forwarding_enabled
        self.branch_prediction_enabled = branch_prediction_enabled
        self.stall_pipeline = False
        
        # Estadísticas
        self.stats = {
            "raw_hazards": 0,
            "waw_hazards": 0,
            "war_hazards": 0,
            "control_hazards": 0,
            "structural_hazards": 0,
            "stalls": 0,
            "correct_predictions": 0,
            "incorrect_predictions": 0
        }
        
        # Estado actual
        self.current_hazard = None
        self.forwarding_source = None
        self.forwarding_dest = None
        self.last_prediction = False
        self.branch_history = {}

    def predict_branch(self, instruction):
        """
        Predice si un salto será tomado o no.
        """
        if not self.branch_prediction_enabled or not instruction:
            return False

        if instruction['opcode'] not in ['BEQ', 'BNE']:
            return False

        prediction = True  # Predicción simple: siempre predice tomado
        self.last_prediction = prediction
        return prediction

    def update_branch_prediction(self, actual_result):
        """
        Actualiza las estadísticas de predicción
        """
        if self.last_prediction is not None:
            if self.last_prediction == actual_result:
                self.stats['correct_predictions'] += 1
                print("Predicción correcta")
            else:
                self.stats['incorrect_predictions'] += 1
                print("Predicción incorrecta")
        self.last_prediction = None

    def flush_pipeline(self, pipeline):
        """
        Limpia el pipeline cuando hay una predicción incorrecta
        """
        pipeline["IF"] = None
        pipeline["ID"] = None
        self.stats['control_hazards'] += 1
        print("Pipeline flushed debido a predicción incorrecta")

    def check_data_hazards(self, pipeline):
        """
        Detecta riesgos de datos entre instrucciones en el pipeline
        """
        if not pipeline['EX'] or not pipeline['ID']:
            return False

        ex_instr = pipeline['EX']
        id_instr = pipeline['ID']
        hazard_detected = False

        # Verificar RAW (Read After Write)
        if 'dest' in ex_instr:
            if ('src1' in id_instr and id_instr['src1'] == ex_instr['dest']) or \
               ('src2' in id_instr and id_instr['src2'] == ex_instr['dest']):
                self.current_hazard = HazardType.RAW
                self.stats["raw_hazards"] += 1
                hazard_detected = True

        # Verificar WAW (Write After Write)
        if 'dest' in ex_instr and 'dest' in id_instr:
            if ex_instr['dest'] == id_instr['dest']:
                self.current_hazard = HazardType.WAW
                self.stats["waw_hazards"] += 1
                hazard_detected = True

        return hazard_detected

    def check_control_hazards(self, pipeline):
        """
        Detecta riesgos de control
        """
        if not pipeline['EX']:
            return False

        ex_instr = pipeline['EX']
        if ex_instr['opcode'] in ['BEQ', 'BNE']:
            self.current_hazard = HazardType.CONTROL
            self.stats["control_hazards"] += 1
            return True
        return False

    def handle_hazards(self, pipeline):
        """
        Maneja los riesgos detectados según la configuración
        """
        hazard_detected = False

        # Si hay forwarding habilitado, intentar primero eso
        if self.forwarding_enabled:
            if self.handle_forwarding(pipeline):
                return False  # No necesitamos stall si el forwarding funciona

        # Verificar riesgos de datos
        if self.check_data_hazards(pipeline):
            hazard_detected = True
            if not self.forwarding_enabled:
                self.stall_pipeline = True
                self.stats["stalls"] += 1

        # Verificar riesgos de control solo si no hay predicción
        if not self.branch_prediction_enabled and self.check_control_hazards(pipeline):
            hazard_detected = True
            self.stall_pipeline = True
            self.stats["stalls"] += 1

        if not hazard_detected:
            self.stall_pipeline = False
            self.current_hazard = None

        return hazard_detected

    def handle_forwarding(self, pipeline):
        """
        Implementa el forwarding de datos
        """
        if not self.forwarding_enabled or not pipeline['ID']:
            return False

        forwarding_performed = False
        id_instr = pipeline['ID']

        # Forwarding desde EX
        if pipeline['EX'] and 'result' in pipeline['EX']:
            ex_instr = pipeline['EX']
            if 'src1' in id_instr and id_instr['src1'] == ex_instr.get('dest'):
                id_instr['forward_src1'] = ex_instr['result']
                print(f"Forwarding: EX.result -> ID.src1 (R{ex_instr['dest']})")
                forwarding_performed = True

            if 'src2' in id_instr and id_instr['src2'] == ex_instr.get('dest'):
                id_instr['forward_src2'] = ex_instr['result']
                print(f"Forwarding: EX.result -> ID.src2 (R{ex_instr['dest']})")
                forwarding_performed = True

        # Forwarding desde MEM
        if pipeline['MEM'] and 'result' in pipeline['MEM']:
            mem_instr = pipeline['MEM']
            if 'src1' in id_instr and id_instr['src1'] == mem_instr.get('dest'):
                id_instr['forward_src1'] = mem_instr['result']
                print(f"Forwarding: MEM.result -> ID.src1 (R{mem_instr['dest']})")
                forwarding_performed = True

            if 'src2' in id_instr and id_instr['src2'] == mem_instr.get('dest'):
                id_instr['forward_src2'] = mem_instr['result']
                print(f"Forwarding: MEM.result -> ID.src2 (R{mem_instr['dest']})")
                forwarding_performed = True

        return forwarding_performed

    def handle_branch_prediction(self, pipeline):
        """
        Maneja la predicción de saltos
        """
        if not pipeline['EX']:
            return False

        ex_instr = pipeline['EX']
        if ex_instr['opcode'] not in ['BEQ', 'BNE']:
            return False

        prediction = self.last_prediction
        actual_taken = False

        if ex_instr['opcode'] == 'BEQ':
            actual_taken = (ex_instr['src1'] == ex_instr['src2'])
        elif ex_instr['opcode'] == 'BNE':
            actual_taken = (ex_instr['src1'] != ex_instr['src2'])

        self.update_branch_prediction(actual_taken)
        
        if prediction != actual_taken:
            self.flush_pipeline(pipeline)
            return True

        return False

    def get_statistics(self):
        """
        Retorna las estadísticas
        """
        return self.stats

    def reset_statistics(self):
        """
        Reinicia las estadísticas
        """
        for key in self.stats:
            self.stats[key] = 0