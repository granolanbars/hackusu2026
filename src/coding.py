welcome_message = "Welcome to Hand++!"  




def bf_set_literal(n: int) -> str:
    return "[-]" + ("+" * n)


def transpile(instructions):
    """
    instructions: list of (left, right, literal)
    literal is ignored except in Victory mode
    """
    bf = []

    for left, right, literal in instructions:

        # -------------------------
        # LITERAL MODE (Victory)
        # -------------------------
        if left == "Victory":
            if literal is None:
                raise ValueError("Literal mode requires a measured value")
            bf.append(bf_set_literal(literal))
            continue

        # -------------------------
        # BANK A — Open_Palm
        # -------------------------
        if left == "Open_Palm":

            if right == "Closed_Fist":
                bf.append("+")
            elif right == "Open_Palm":
                bf.append("-")
            elif right == "Pointing_Up":
                bf.append(">")
            elif right == "Thumb_Down":
                bf.append("<")
            elif right == "Victory":
                bf.append(".")
            elif right == "ILoveYou":
                bf.append(",")
            # None or anything else = NOP
            continue

        # -------------------------
        # BANK B — Open_Fist
        # -------------------------
        if left == "Open_Fist":

            if right == "Open_Fist":
                bf.append("[")
            elif right == "Close_Fist":
                bf.append("]")
            # everything else = NOP
            continue

        # Unknown left-hand gesture
        raise ValueError(f"Unknown left-hand gesture: {left}")

    return "".join(bf)

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