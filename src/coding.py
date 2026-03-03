# from detection import GestureEngine
# from interpreter import transpile, coding_interpreter

# def code_edit(engine_a):
#     program = []
#     confirmed = False
#     print("Welcome to Hand++")
#     while not confirmed:
#         line = engine_a.detect("code")
#         match line[0]:
#             case "CANCEL":
#                 print("Are you sure you want to Cancel?")
#                 confirmed = engine_a.detect("confirm")
#                 if confirmed:
#                     print("returning to main menu")
#                 else:
#                     print("Continue Programming")
#             case "RUN":
#                 print("Are you Sure you want to run your program?")
#                 confirmed = engine_a.detect("confirm")
#                 if confirmed:
#                     print("Running your program...")
#                     print("\n\n\n")
#                     print(coding_interpreter(transpile(program)))
#                     print("\n\n\n")
#                     break
#                 else:
#                     continue
#             case "LINE":
#                 values = line[1:4]
#                 for value in values:
#                     print(value, end = " ")
#                 print()
#                 program.append((line[1:4]))
#             case _:
#                 continue

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