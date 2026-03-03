

def interpret_code(program, mem_size=30000):
    tape = [0] * mem_size
    ptr = 0
    line = 0
    loop_x_times = []
    output = []

    program_len = len(program)

    

    def inc_cell():
        tape[ptr] = (tape[ptr] + 1) % 256

    def dec_cell():
        tape[ptr] = (tape[ptr] - 1) % 256

    def inc_ptr():
        nonlocal ptr
        ptr += 1

    def dec_ptr():
        nonlocal ptr
        ptr -= 1

    def do_output():
        print('Sending to output', chr(tape[ptr]))
        output.append(chr(tape[ptr]))

    def do_input():
        nonlocal ptr
        ch = input("Input a character: ")
        if ch:
            tape[ptr] = ord(ch[0]) & 0x7F
        else:
            tape[ptr] = 0

    def start_loop():
        print("loop started, ptr:", ptr, "line:", line+1)
        loop_x_times.append((ptr, line + 1))
        return False

    def end_loop():
        nonlocal line
        cell_ptr, jump_to = loop_x_times[-1]
        if tape[cell_ptr] == 0:
            loop_x_times.pop()
            return False
        
        line = jump_to
        return True
    def set_literal():
        tape[ptr] = literal
    
    def get_value():
        output.append(int(tape[ptr]))

    
        


    command_dict = {
        'Closed_Fist': {
            'Thumb_Up': inc_cell,
            'Thumb_Down': dec_cell,
            'Open_Palm': inc_ptr,
            'Closed_Fist': dec_ptr,
            'Victory': do_input,
            'Pointing_Up': do_output,
        },

        'Open_Palm': {
            'Open_Palm': start_loop,
            'Closed_Fist': end_loop,
        },

        'ILoveYou': {
            'ILoveYou': set_literal,
            'Pointing_Up': get_value,
        }
    }

    while line < program_len:
        left, right, literal = program[line]
        

        try:
            fn = command_dict[left][right]
        
        except KeyError:
            print("unrecognized command: ", left, right)
            line+=1
            continue


        
        jumped = fn()
        if jumped:
            continue
        
        
        line += 1

    return "".join(str(x) for x in output)