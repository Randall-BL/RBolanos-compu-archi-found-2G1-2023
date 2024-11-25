# hazard_unit.py

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

    def check_data_hazards(self, pipeline):
        """
        Detecta riesgos de datos entre instrucciones en el pipeline
        """
        if not pipeline['EX'] or not pipeline['ID']:
            return False

        ex_instr = pipeline['EX']
        id_instr = pipeline['ID']

        # Verificar RAW (Read After Write)
        if 'dest' in ex_instr:
            if ('src1' in id_instr and id_instr['src1'] == ex_instr['dest']) or \
               ('src2' in id_instr and id_instr['src2'] == ex_instr['dest']):
                self.current_hazard = HazardType.RAW
                self.stats["raw_hazards"] += 1
                return True

        # Verificar WAW (Write After Write)
        if 'dest' in ex_instr and 'dest' in id_instr:
            if ex_instr['dest'] == id_instr['dest']:
                self.current_hazard = HazardType.WAW
                self.stats["waw_hazards"] += 1
                return True

        return False

    def check_control_hazards(self, pipeline):
        """
        Detecta riesgos de control (saltos)
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
        if self.check_data_hazards(pipeline):
            if self.forwarding_enabled:
                return self.handle_forwarding(pipeline)
            else:
                self.stall_pipeline = True
                self.stats["stalls"] += 1
                return True

        if self.check_control_hazards(pipeline):
            if self.branch_prediction_enabled:
                return self.handle_branch_prediction(pipeline)
            else:
                self.stall_pipeline = True
                self.stats["stalls"] += 1
                return True

        self.stall_pipeline = False
        self.current_hazard = None
        return False

    def handle_forwarding(self, pipeline):
        """
        Implementa el forwarding de datos
        """
        if not pipeline['EX'] or not pipeline['ID']:
            return False

        ex_instr = pipeline['EX']
        id_instr = pipeline['ID']

        if 'result' in ex_instr:
            if 'src1' in id_instr and id_instr['src1'] == ex_instr['dest']:
                self.forwarding_source = f"EX.result"
                self.forwarding_dest = f"ID.src1"
                id_instr['forward_src1'] = ex_instr['result']
                return True

            if 'src2' in id_instr and id_instr['src2'] == ex_instr['dest']:
                self.forwarding_source = f"EX.result"
                self.forwarding_dest = f"ID.src2"
                id_instr['forward_src2'] = ex_instr['result']
                return True

        return False

    def handle_branch_prediction(self, pipeline):
        """
        Implementa la predicción de saltos
        """
        if not pipeline['EX']:
            return False

        ex_instr = pipeline['EX']
        if ex_instr['opcode'] not in ['BEQ', 'BNE']:
            return False

        # Predicción simple: predecir no tomado
        prediction = False
        self.last_prediction = prediction

        # Verificar si la predicción fue correcta
        actual_taken = False
        if ex_instr['opcode'] == 'BEQ':
            actual_taken = (ex_instr['src1'] == ex_instr['src2'])
        elif ex_instr['opcode'] == 'BNE':
            actual_taken = (ex_instr['src1'] != ex_instr['src2'])

        if prediction == actual_taken:
            self.stats["correct_predictions"] += 1
        else:
            self.stats["incorrect_predictions"] += 1
            self.flush_pipeline(pipeline)

        return True

    def flush_pipeline(self, pipeline):
        """
        Limpia el pipeline después de una predicción incorrecta
        """
        pipeline['IF'] = None
        pipeline['ID'] = None

    def get_statistics(self):
        """
        Retorna las estadísticas actuales
        """
        return self.stats

    def reset_statistics(self):
        """
        Reinicia las estadísticas
        """
        for key in self.stats:
            self.stats[key] = 0