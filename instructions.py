# Programa de ejemplo
def program():
    return [
        {"opcode": "ADD", "dest": 1, "src1": 2, "src2": 3},  # ADD R1, R2, R3
        {"opcode": "SUB", "dest": 4, "src1": 5, "src2": 6},  # SUB R4, R5, R6
        {"opcode": "MUL", "dest": 7, "src1": 0, "src2": 1},  # MUL R7, R0, R1
    ]
