import os
from game import Game


def enable_colors():
    if os.name == "nt":
        import ctypes

        kernel32 = ctypes.windll.kernel32
        kernel32.GetStdHandle.restype = ctypes.c_void_p

        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint()

        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)


if __name__ == "__main__":
    enable_colors()

    game = Game()
    game.run()
