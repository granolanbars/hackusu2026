

from detection import GestureEngine
from my_interpreterv2 import interpret_code
from colors import c, RED, GREEN, YELLOW, CYAN, MAGENTA

def code_edit(engine_a):
    program = []
    confirmed = False

    print(c("Welcome to Hand++", CYAN))

    while not confirmed:
        line = engine_a.detect("code")

        match line[0]:

            case "CANCEL":
                print(c("Are you sure you want to Cancel?", YELLOW))
                confirmed = engine_a.detect("confirm")

                if confirmed:
                    print(c("Returning to main menu", RED))
                else:
                    print(c("Continue Programming", CYAN))

            case "RUN":
                print(c("Are you sure you want to run your program?", YELLOW))
                confirmed = engine_a.detect("confirm")

                if confirmed:
                    print(c("Running your program...", GREEN))
                    print("\n\n")
                    print(interpret_code(program))
                    print("\n\n")
                    break
                else:
                    continue

            case "LINE":
                left, right, literal = line[1:4]
                program.append((left, right, literal))
                print(c(left+right+str(literal), MAGENTA))
                

            case _:
                continue