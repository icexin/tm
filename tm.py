#!/usr/bin/env python

import loader
import sys

class Machine(object):
    def __init__(self, ram_size = 1024, rom_size = 1024):
        self.ram_size = ram_size
        self.rom_size = rom_size
        self.regs = {'ax':0, 'bx':0, 'cx':0, 'dx':0, 'si':0, 'di':0, 'pc':0}
        self.ram = [0] * ram_size
        self.rom = None
        self.status = 'run'


    def step(self):
    
        if self.regs['pc'] > self.rom_size:
            print("out of rom")
            return
        inst = self.rom[self.regs['pc']]
        if inst.type == 'move':
            self.domove(inst.args)
        elif inst.type == 'math':
            self.domath(inst.op, inst.args)
        elif inst.type == 'io':
            self.doio(inst.op, inst.args)
        elif inst.type == 'jump':
            self.dojump(inst.op, inst.args)
        elif inst.type == 'halt':
            self.status = 'halt'
        else:
            raise ValueError('unknow instruction')

    def domove(self, args):
        dest = args[0]
        src = args[1]
        if dest.type == 'ref': #mov [bx], ax
            self.ram[self.regs[dest.value]] = self.regs[src.value]
        elif src.type == 'const':
            self.regs[dest.value] = src.value
        elif src.type == 'reg':
            self.regs[dest.value] = self.regs[src.value]
        elif src.type == 'ref':
            self.regs[dest.value] = self.ram[self.regs[src.value]]
        else:
            raise ValueError('move error')
        self.regs['pc'] += 1

    def domath(self, op, args):
        dest = args[0].value
        src = args[1].value
        if op == 'add':
            self.regs[dest] += self.regs[src]
        elif op == 'sub':
            self.regs[dest] -= self.regs[src]
        elif op == 'mul':
            self.regs[dest] *= self.regs[src]
        elif op == 'div':
            self.regs[dest] /= self.regs[src]
        else:
            raise ValueError('math error')
        self.regs['pc'] += 1
    
    
    def doio(self, op, arg):
        if op == 'write':
            print(self.regs[arg[0].value])
        else:
            self.regs[arg[0].value] = int(input('input: '))
        self.regs['pc'] += 1
        
    def dojump(self, op, arg):

        jump = False
        if op == 'jmp':
            jump = True
            pos = arg[0].value
        else:
            reg = arg[0].value
            pos = arg[1].value
            if op == 'je':
                jump = self.regs[reg] == 0
            elif op == 'jne':
                jump = self.regs[reg] != 0
            elif op == 'jlt':
                jump = self.regs[reg] < 0
            elif op == 'jle':
                jump = self.regs[reg] <= 0
            elif op == 'jgt':
                jump = self.regs[reg] > 0
            elif op == 'jge':
                jump = self.regs[reg] >= 0
            else:
                raise ValueError('jump error')
        if jump:
            self.regs['pc'] = pos
        else:
            self.regs['pc'] += 1
    
    def load_rom(self, s): 
        t = loader.load_rom(s)
        self.rom = t + [loader.Inst('halt', None, None)] * (self.ram_size - len(t))

    def run(self):
        while self.status != 'halt':
            self.step()
            
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("usage app file")
    else:
        s = open(sys.argv[1]).read()
        machine = Machine()
        machine.load_rom(s)
        machine.run()

