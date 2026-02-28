
Instructions = "Instructions: Welcome to HandScrew!\n "

def coding_interpreter(code, input_data=""):
    tape = [0] * 30000
    ptr = 0
    ip = 0  # instruction pointer
    input_ptr = 0
    output = []

    # Precompute matching brackets for fast jumping
    stack = []
    brackets = {}
    for i, c in enumerate(code):
        if c == "[":
            stack.append(i)
        elif c == "]":
            start = stack.pop()
            brackets[start] = i
            brackets[i] = start

    while ip < len(code):
        cmd = code[ip]

        if cmd == ">":
            ptr += 1
        elif cmd == "<":
            ptr -= 1
        elif cmd == "+":
            tape[ptr] = (tape[ptr] + 1) % 256
        elif cmd == "-":
            tape[ptr] = (tape[ptr] - 1) % 256
        elif cmd == ".":
            output.append(chr(tape[ptr]))
        elif cmd == ",":
            if input_ptr < len(input_data):
                tape[ptr] = ord(input_data[input_ptr])
                input_ptr += 1
            else:
                tape[ptr] = 0
        elif cmd == "[":
            if tape[ptr] == 0:
                ip = brackets[ip]
        elif cmd == "]":
            if tape[ptr] != 0:
                ip = brackets[ip]

        ip += 1

    return "".join(output)