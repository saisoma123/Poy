import math
import random
import operator as op
import sys
import gc
import psutil
from collections import deque
from io import IOBase
Symbol = str    
Integer = int
Float = float     # A Joy Number is implemented as a Python int or float
Boolean = bool
File = IOBase
Atom   = (Symbol, Integer, Float, Boolean) # A Joy Atom is a Symbol or Number
Stack = deque # A Joy Stack is implemented with deque with O(1) complexity
Set = set #A Joy set is just a Python set
List   = list             # A Joy List is implemented as a Python list
Exp    = (Atom, List)     # A Joy expression is an Atom or List
Env    = dict             # A Joy environment (defined below) 

def tokenize(chars: str) -> list:
    return chars.split(" ")

def parse(program: str) -> Exp:
    "Read a Scheme expression from a string."
    return read_from_tokens(tokenize(program))

def read_from_tokens(tokens: list) -> Exp:
    "Read an expression from a sequence of tokens."
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF')
    token = tokens.pop(0)
    if token == '(':
        L = []
        while tokens[0] != ')':
            L.append(read_from_tokens(tokens))
        tokens.pop(0) # pop off ')'
        return L
    elif token == ')':
        raise SyntaxError('unexpected )')
    else:
        return atom(token)

def atom(token: str) -> Atom:
    "Numbers become numbers; every other token is a symbol."
    try: return int(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return Symbol(token)

def standard_env() -> Env:
    "An environment with some Joy standard procedures."
    env = Env()
    env.update(vars(math)) # sin, cos, sqrt, pi, ...
    env.update({
        '+':op.add, '-':op.sub, '*':op.mul, '/':op.truediv, 
        '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq, 
        'abort': sys.exit,
        'abs':     abs,
        'and': lambda x, y: x.intersection(y),
        'append':  op.add,  
        'apply':   lambda proc, args: proc(*args),
        'begin':   lambda *x: x[-1],
        'car':     lambda x: x[0],
        'cdr':     lambda x: x[1:], 
        'char': lambda x: True if len(x) == 1 else False,
        'character': lambda x: x[0],
        'clock': psutil.cpu_percent(),
        'cons': lambda x,y: [x] + y,
        'echo': lambda text: "echo '{}' | iconv ...".format(text),
        'eq?':     op.is_, 
        'equal?':  op.eq, 
        'false': False,
        'file' : lambda x: isinstance(x, File),
        'float': lambda x: isinstance(x, Float),
        "gc": gc.enable(),
        'id': '',
        'integer': lambda x: isinstance(x, Integer),
        'leaf': lambda x: not isinstance(x, List),
        'length':  len, 
        'list type':    lambda *x: List(x), #Edit later
        'list':   lambda x: isinstance(x, List), 
        'map':     map,
        'max':     max,
        'min':     min,
        'not':     op.not_,
        'null?':   lambda x: x == [],  
        'or': lambda x, y: x.union(y),
        'pow':    pow,
		'print':   print,
        'procedure?': callable,
        'putchars': lambda x: print(x),
        'quit' : exit,
        'random': random.randint,
        'round':   round,
        'set': lambda x: isinstance(x, Set),
        'string': lambda x: isinstance(x, Symbol),
        'strtod': lambda x: float(x),
        'true': True,
        'user': lambda x: isinstance(x, ),
        'xor': lambda x,y: x.symmetric_difference(y)
    })
    return env

class Env(dict):
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer
        
    # Find the innermost Env where var appears.
    def find(self, var):
        return self if (var in self) else self.outer.find(var)

class Procedure(object):
    "A user-defined Scheme procedure."
    def __init__(self, parms, body, env):
        self.parms, self.body, self.env = parms, body, env
    def __call__(self, *args): 
        return eval(self.body, Env(self.parms, args, self.env))


global_env = standard_env()

def eval(x, env=global_env):
    "Evaluate an expression in an environment."
    if isinstance(x, Symbol):    # variable reference
        return env.find(x)[x]
    elif not isinstance(x, List):# constant 
        return x   
    op, *args = x       
    if op == 'quote':            # quotation
        return args[0]
    elif op == 'if':             # conditional
        (test, conseq, alt) = args
        exp = (conseq if eval(test, env) else alt)
        return eval(exp, env)
    elif op == 'define':         # definition
        (symbol, exp) = args
        env[symbol] = eval(exp, env)
    elif op == 'set!':           # assignment
        (symbol, exp) = args
        env.find(symbol)[symbol] = eval(exp, env)
    elif op == 'lambda':         # procedure
        (parms, body) = args
        return Procedure(parms, body, env)
    else:                        # procedure call
        proc = eval(op, env)
        vals = [eval(arg, env) for arg in args]
        return proc(*vals)

def repl(prompt='lis.py> '):
    "A prompt-read-eval-print loop."
    while True:
        val = eval(parse(input(prompt)))
        if val is not None: 
            print(joystr(val))

def joystr(exp):
    "Convert a Python object back into a Scheme-readable string."
    if isinstance(exp, List):
        return '(' + ' '.join(map(joystr, exp)) + ')' 
    else:
        return str(exp)
take = input()
print(tokenize(take))
#x = input()
#print(eval(parse("(begin (define r 10) (* pi (* r r)))")))