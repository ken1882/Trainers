import _G, utils
import os
from collections import deque

# Windows
if os.name == 'nt':
    import msvcrt

# Posix (Linux, OS X)
else:
    import sys
    import termios
    import atexit
    import fcntl
    from select import select


class KBHit:
    '''
    A Python class implementing KBHIT, the standard keyboard-interrupt poller.
    Works transparently on Windows and Posix (Linux, Mac OS X).  Doesn't work
    with IDLE.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    '''
    def __init__(self, non_block=False):
        '''Creates a KBHit object that you can call to do various keyboard things.
        '''

        if os.name == 'nt':
            pass
        else:
            # Save the terminal settings
            self.fd = sys.stdin.fileno()
            self.new_term = termios.tcgetattr(self.fd)
            self.old_term = termios.tcgetattr(self.fd)

            # New terminal setting unbuffered
            self.new_term[3] = (self.new_term[3] & ~termios.ICANON & ~termios.ECHO)
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)

            # Support normal-terminal reset at exit
            atexit.register(self.set_normal_term)

            if non_block:
                self.set_nonblock(self.fd)


    def set_normal_term(self):
        ''' Resets to normal terminal.  On Windows this is a no-op.
        '''

        if os.name == 'nt':
            pass
        else:
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)


    def getch(self):
        ''' Returns a keyboard character after kbhit() has been called.
            Should not be called in the same program as getarrow().
        '''
        ch = None
        try:
            if os.name == 'nt':
                if msvcrt.kbhit():
                    ch = msvcrt.getch()
                    return ch.decode('utf-8')
            else:
                return sys.stdin.read(1)
        except IOError:
            pass
        except UnicodeDecodeError:
            return ch

    def set_nonblock(self, fd):
        ''' Set the file description of the given file descriptor to non-blocking.
        '''
        flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        flags = flags | os.O_NONBLOCK
        fcntl.fcntl(fd, fcntl.F_SETFL, flags)

    def getarrow(self):
        ''' Returns an arrow-key code after kbhit() has been called. Codes are
        0 : up
        1 : right
        2 : down
        3 : left
        Should not be called in the same program as getch().
        '''

        if os.name == 'nt':
            msvcrt.getch() # skip 0xE0
            c = msvcrt.getch()
            vals = [72, 77, 80, 75]
        else:
            c = sys.stdin.read(3)[2]
            vals = [65, 67, 66, 68]

        return vals.index(ord(c.decode('utf-8')))


    def kbhit(self):
        ''' Returns True if keyboard character was hit, False otherwise.
        '''
        if os.name == 'nt':
            return msvcrt.kbhit()
        else:
            dr,dw,de = select([sys.stdin], [], [], 0)
            return dr != []

class NeoConsole(KBHit):

    WINDOWS_FUNCTION_CHAR = {
        'H': 'UP',
        'P': 'DOWN',
        'K': 'LEFT',
        'M': 'RIGHT',
        'S': 'DEL',
        'G': 'HOME',
        'O': 'END',
        'I': 'PAGE_UP',
        'Q': 'PAGE_DOWN',
        'R': 'INSERT',
    }

    UNIX_FUNCTION_CHAR = {
        'A': 'UP',
        'B': 'DOWN',
        'D': 'LEFT',
        'C': 'RIGHT',
        '3': 'DEL',
        'H': 'HOME',
        'F': 'END',
        '5': 'PAGE_UP',
        '6': 'PAGE_DOWN',
        '2': 'INSERT',
    }

    def __init__(self, nonblock=True, globals={}, locals={}):
        super().__init__(nonblock)
        self.console_buffer = ''
        self.line_buffer = ''
        self.cursor_pos = 0
        self.line_history = deque(maxlen=50)
        self.history_pos = 0
        self.exec_namespace = {**globals, **locals}
        print('''
----------------------------------------------
Welcome to NeopetAssistant interactive console!
Press ESC to exit.
Press Insert to execute commands.
Press Enter to line break.
Press PageUp to show entered command buffer.
Ctrl+C to clear buffer.
Use `__ret__` to return value.
----------------------------------------------
>>> ''', end='', flush=True)

    def update(self):
        ch = None
        try:
            ch = self.getch()
        except KeyboardInterrupt:
            self.console_buffer = ''
            self.line_buffer = ''
            self.mouse_pos = 0
            print("KeyboardInterrupt\n>>> ", end='', flush=True)
        if ch and type(ch) == str:
            if ord(ch) == 27: # ESC
                self.process_escape()
            elif ord(ch) in [10, 13]: # Enter
                self.process_linewrap()
            elif ord(ch) in [8, 127]: # Backspace
                self.process_backspace()
            else:
                self.line_buffer = self.line_buffer[:self.cursor_pos] + ch + self.line_buffer[self.cursor_pos:]
                self.cursor_pos += 1
                self.history_pos = 0
                if self.cursor_pos == len(self.line_buffer)+1:
                    print(ch, end='', flush=True)
                else:
                    self.refresh_line()
        elif ch:
            if ord(ch) == 224: # function keys in windows
                return self.process_function_keys(self.getch())

    def execute(self):
        _G.log_info("Executing command:\n" + self.console_buffer.rstrip() + '\n---\n')
        if self.console_buffer:
            try:
                self.exec_namespace['__ret__'] = None
                self.exec_namespace = {**globals(), **locals(), **self.exec_namespace}
                exec(self.console_buffer, self.exec_namespace, self.exec_namespace)
                print("\n<<< " + str(self.exec_namespace['__ret__']))
            except Exception as e:
                utils.handle_exception(e)
        self.console_buffer = ''
        self.line_buffer = ''
        self.cursor_pos = 0
        self.refresh_line()

    def process_function_keys(self, key):
        func = None
        if os.name == 'nt':
            func = NeoConsole.WINDOWS_FUNCTION_CHAR.get(key)
        else:
            func = NeoConsole.UNIX_FUNCTION_CHAR.get(key)
        if func == 'UP':
            self.process_arrow_up()
        elif func == 'DOWN':
            self.process_arrow_down()
        elif func == 'LEFT':
            self.process_arrow_left()
        elif func == 'RIGHT':
            self.process_arrow_right()
        elif func == 'HOME':
            self.process_line_home()
        elif func == 'END':
            self.process_line_end()
        elif func == 'DEL':
            self.process_delete()
        elif func == 'PAGE_UP':
            self.process_page_up()
        elif func == 'PAGE_DOWN':
            self.process_page_down()
        elif func == 'INSERT':
            self.execute()
        self.getch() # Skip the second key

    def process_escape(self):
        if os.name == 'nt':
            raise KeyboardInterrupt
        else:
            if self.getch() == '[':  # May be function key in Unix
                self.process_function_keys(self.getch())
            else:
                raise KeyboardInterrupt

    def reset(self):
        self.console_buffer = ''
        self.line_buffer = ''
        self.cursor_pos = 0
        self.history_pos = 0
        self.refresh_line()

    def process_linewrap(self):
        self.console_buffer += self.line_buffer + '\n'
        self.line_history.appendleft(self.line_buffer)
        self.line_buffer = ''
        self.cursor_pos = 0
        print('\n>>> ', end='', flush=True)

    def process_backspace(self):
        if self.cursor_pos > 0:
            self.line_buffer = self.line_buffer[:self.cursor_pos - 1] + self.line_buffer[self.cursor_pos:]
            self.cursor_pos -= 1
            self.refresh_line()

    def process_delete(self):
        if self.cursor_pos < len(self.line_buffer):
            self.line_buffer = self.line_buffer[:self.cursor_pos] + self.line_buffer[self.cursor_pos + 1:]
            self.refresh_line()

    def process_arrow_left(self):
        if self.cursor_pos > 0:
            self.cursor_pos -= 1
            print('\b', end='', flush=True)

    def process_arrow_right(self):
        if self.cursor_pos < len(self.line_buffer):
            print(self.line_buffer[self.cursor_pos], end='', flush=True)
            self.cursor_pos += 1

    def process_line_home(self):
        while self.cursor_pos > 0:
            self.process_arrow_left()

    def process_line_end(self):
        while self.cursor_pos < len(self.line_buffer):
            self.process_arrow_right()

    def process_arrow_up(self):
        if self.history_pos < len(self.line_history):
            tr = len(self.line_buffer)
            self.line_buffer = self.line_history[self.history_pos]
            tr -= len(self.line_buffer)
            self.history_pos = min(len(self.line_history)-1, self.history_pos + 1)
            self.cursor_pos = len(self.line_buffer)
            self.refresh_line(max(0, tr))

    def process_arrow_down(self):
        if self.history_pos > 0:
            self.history_pos = max(0, self.history_pos - 1)
            tr = len(self.line_buffer)
            self.line_buffer = self.line_history[self.history_pos] if self.history_pos < len(self.line_history) else ''
            tr -= len(self.line_buffer)
            self.cursor_pos = len(self.line_buffer)
            self.refresh_line(max(0, tr))

    def refresh_line(self, trailing_space=0):
        line  = f"\r>>> {self.line_buffer} " + ' ' * trailing_space
        line += ' ' * (len(self.line_buffer) - self.cursor_pos)
        line += f"\r>>> {self.line_buffer[:self.cursor_pos]}"
        print(line, end='', flush=True)

    def process_page_up(self):
        print("\nCommand buffer:\n", self.console_buffer.rstrip(), '\n>>> ', end='', sep='', flush=True)

    def process_page_down(self):
        pass  # No function for now


if __name__ == '__main__':
    console = NeoConsole()
    try:
        while True:
            console.update()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        console.set_normal_term()
