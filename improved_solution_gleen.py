import operator


INTEGER_ARITHMETIC_OPERATORS = {
    '+': operator.add, 
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.floordiv
}

STACK_MANIPULATIONS = {'DUP', 'DROP', 'SWAP', 'OVER'}


class StackUnderflowError(Exception):
    """Exception raised when an operation attempts to remove more items from the stack than are available."""
    pass


class Stack(list):
    """
    A stack implementation extending Python's built-in list, providing stack operations like pop, push, and peek.
    """
    def pop(self, num=1):
        """
        Removes and returns the top 'num' elements from the stack. Raises StackUnderflowError if there aren't enough elements.
        
        :param num: The number of items to pop from the stack.
        :return: The last 'num' elements from the stack.
        """
        if len(self) < num:
            raise StackUnderflowError('Insufficient number of items in stack')
        values = self[-num:]
        del self[-num:]
        return values if num > 1 else values[0]
    def push(self, *items):
        """
        Pushes multiple items onto the top of the stack.

        :param items: An unpacked tuple of items to be pushed onto the stack.
        """
        for item in items:
            self.append(item)
    def peek(self):
        """
        Returns the top element of the stack without removing it.

        :return: The last element of the stack.
        """
        val = self.pop()
        self.push(val)
        return val

def evaluate(input_data):
    """
    Evaluates a list of Forth-like language commands, manipulating the stack and defining/using macros accordingly.

    :param input_data: A list of strings, each representing a Forth-like language command.
    :return: The stack after processing all commands.
    """
    stack = Stack()
    macros = dict()
    for cmd in input_data:
        words = cmd.upper().split()
        while len(words) > 0:
            command = words.pop(0)
            if is_number(command):
                stack.push(int(command))
            elif command in macros:
                words = macros[command] + words
            elif command == ':':
                record_macro(words, macros)
                del words[:]
            elif command in INTEGER_ARITHMETIC_OPERATORS:
                binary_op(stack, INTEGER_ARITHMETIC_OPERATORS[command])
            elif command in STACK_MANIPULATIONS:
                process_stack_manipulation(stack, command)
            else:
                raise ValueError('undefined operation')
    return stack

def process_stack_manipulation(stack, command):
    """
    Processes stack manipulation commands like DUP, DROP, SWAP, and OVER.

    :param stack: The stack to perform the operations on.
    :param word: The stack manipulation command to execute.
    """
    if command == 'DUP':
        a = stack.pop()
        stack.push(a, a)
    elif command == 'DROP':
        stack.pop()
    elif command == 'SWAP':
        a, b = stack.pop(num=2)
        stack.push(b, a)
    elif command == 'OVER':
        a, b = stack.pop(num=2)
        stack.push(a, b, a)

def is_number(command):
    """
    Checks if the given string is a number.

    :param word: The string to check.
    :return: True if the string is a number, False otherwise.
    """
    return command.lstrip('-').isdigit()

def binary_op(stack, func):
    """
    Performs a binary arithmetic operation on the top two elements of the stack.

    :param stack: The stack to perform the operation on.
    :param func: The binary function to apply to the top two elements of the stack.
    """
    if len(stack) > 0 and stack.peek() == 0:
        # Check div by zero
        raise ZeroDivisionError('divide by zero')
    a, b = stack.pop(num=2)
    stack.push(func(a, b))

def record_macro(words, macros):
    """
    Records a new macro definition into the macros dictionary.

    :param words: A list of words forming the macro definition.
    :param macros: The dictionary to store the macro definition.
    """
    name = words.pop(0)
    if is_number(name):
        raise ValueError('illegal operation')
    if words[-1] != ';':
        raise ValueError('macro not terminated with ;')
    words.pop()
    # macros definitions can contain macros. Expand them.
    while True:
        has_expanded, words = expand_macros_in_defn(words, macros)
        if not has_expanded:
            break
    macros[name] = words[:]  # copy

def expand_macros_in_defn(words, macros):
    """
    Expands macros within a macro definition based on the provided macro dictionary.

    :param words: A list of words forming the macro definition.
    :param macros: A dictionary mapping macro keys to their expansions.
    :return: A tuple (has_expanded, new_words) indicating whether expansion occurred and the resulting words list.
    """
    new_words = [macros[word] if word in macros else [word] for word in words]
    has_expanded = any(word in macros for word in words)
    # Flatten new_words in case of expansion
    new_words = [item for sublist in new_words for item in (sublist if isinstance(sublist, list) else [sublist])]

    return has_expanded, new_words
