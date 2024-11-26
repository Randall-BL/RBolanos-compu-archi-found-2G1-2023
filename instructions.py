# instructions.py
# Configuración de las instrucciones del programa 10 instrucciones.
def program():
    return [
        {"opcode": "ADD", "dest": 1, "src1": 2, "src2": 3},  # ADD R1, R2, R3
        {"opcode": "SUB", "dest": 4, "src1": 5, "src2": 6},  # SUB R4, R5, R6
        {"opcode": "MUL", "dest": 7, "src1": 0, "src2": 1},  # MUL R7, R0, R1
        {"opcode": "LOAD", "dest": 7, "src1": 3},            # LOAD R7, MEM[3]
        {"opcode": "STORE", "dest": 3, "src1": 4},           # STORE MEM[3], R4
        {"opcode": "DIV", "dest": 3, "src1": 5, "src2": 6},  # DIV R3, R5, R6
        {"opcode": "MOD", "dest": 3, "src1": 5, "src2": 6},  # MOD R3, R5, R6
        {"opcode": "SWAP", "dest": 1, "src1": 2},            # SWAP R1, R2
        {"opcode": "BNE", "src1": 1, "src2": 2, "offset": 2},# BNE R1, R2, skip next 2
        {"opcode": "BEQ", "src1": 3, "src2": 4, "offset": 4} # BEQ R3, R4, skip next 1
    ]
