from ply import lex,yacc

op = {
    'mov' : 'MOV',
    'write' : 'WRITE',
    'read' : 'READ',
    'jmp' : 'JMP'
}



tokens = ['LABEL', 'REG', 'COND', 'NUM', 'MATH_OP', 'NEWLINE'] \
    + list(op.values())

literals = "#[],:"

t_REG = r'ax|bx|cx|dx|pc'
t_COND = r'je|jne|jlt|jle|jgt|jge'
t_MATH_OP = r'add|sub|mul|div'
t_ignore = ' \t'

def t_LABEL(t):
    r'[a-zA-Z][a-zA-Z0-9]*'
    if t.value in op.keys():
        t.type = op.get(t.value)
    elif t.value in t_REG:
        t.type = 'REG'
    elif t.value in t_COND:
        t.type = 'COND'
    elif t.value in t_MATH_OP:
        t.type = 'MATH_OP'

    return t
def t_COMMENT(t):
    r'//.*'
    pass

def t_NUM(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t

def t_NEWLINE(t):
    r'\n'
    return t

def t_error(t):
    print("Illegal character '{0}'".format(t.value[0]))
    t.lexer.skip(1)

def p_error(p):
    print("Syntax error with token: " + str(p))
    yacc.errok()

def p_mov_reg_const(p):
    "mov : MOV REG ',' NUM"

    dest = Arg('reg', p[2])
    src = Arg('const', p[4])
    p[0] = Inst('move', 'mov', (dest, src))

def p_mov_reg_reg(p):
    "mov : MOV REG ',' REG"

    dest = Arg('reg', p[2])
    src = Arg('reg', p[4])
    p[0] = Inst('move', 'mov', (dest, src))

def p_mov_reg_ref(p):
    "mov : MOV REG ',' '[' REG ']'"

    dest = Arg('reg', p[2])
    src = Arg('ref', p[5])
    p[0] = Inst('move', 'mov', (dest, src))

def p_mov_ref_reg(p):
    '''
    mov : MOV '[' REG ']' ',' REG
    '''
    dest = Arg('ref', p[3])
    src = Arg('reg', p[6])
    p[0] = Inst('move', 'mov', (dest, src))

def p_add(p):
    '''
    math : MATH_OP REG ',' REG
    '''
    dest = Arg('reg', p[2])
    src = Arg('reg', p[4])
    p[0] = Inst('math', p[1], (dest, src))

def p_no_cond_jmp(p):
    "jmp : JMP LABEL"
    p[0] = Inst('jump', p[1], (Arg('label', p[2]),))

def p_cond_jmp(p):
    '''
    jmp : COND REG ',' LABEL
    '''

    p[0] = Inst('jump', p[1], (Arg('reg', p[2]), \
                               Arg('label', p[4])))
    
def p_io_write(p):
    "io : WRITE REG"
    p[0] = Inst('io', 'write', (Arg('reg', p[2]),))


def p_io_read(p):
    "io : READ REG"
    p[0] = Inst('io', 'read', (Arg('reg', p[2]),))

def p_insts1(p):
    "insts : insts inst NEWLINE"

    if p[2]:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = p[1]

def p_insts2(p):
    "insts : inst NEWLINE"
    
    if p[1]:
        p[0] = [p[1]]
    else:
        p[0] = []


def p_inst(p):
    '''
    inst : mov
         | math
         | io
         | jmp
         | LABEL ':' inst
         |
    '''
    global label, loaction
    
    if len(p) == 2:
        p[0] = p[1]
        loaction += 1
    elif len(p) == 4:
        p[0] = p[3]
        if p[3]:
            label[p[1]] = loaction
        else:
            label[p[1]] = loaction + 1
    else:
        p[0] = None


class Arg(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value
    def __str__(self):
        return '{0} {1}'.format(self.type, self.value)
    def __repr__(self):
        return self.__str__()

class Inst(object):
    def __init__(self, type, op, args):
        self.type = type
        self.op = op
        self.args = args
    def __str__(self):
        return "{0} {1} {2}".format(self.type, self.op, self.args)
    
    def __repr__(self):
        return self.__str__()


label = {}
loaction = -1
lexer = lex.lex()
parser = yacc.yacc(start='insts')

def label_to_loaction(rom):
    for inst in rom:
        if inst.type == 'jump':
            try:
                if len(inst.args) == 1:
                    label_name = inst.args[0].value
                    inst.args[0].value = label[label_name]
                else:
                    label_name = inst.args[1].value
                    inst.args[1].value = label[label_name]
            except KeyError:
                raise SyntaxError("label '{0}' does not exsits".format(label_name))

def load_rom(s):
    rom = parser.parse(s)
    label_to_loaction(rom)
    return rom
	



