# runtime configuration HERE #
PARALLEL = False
##############################

from time import time
from z3 import *


if PARALLEL:
    set_param('parallel.enable', True)


time_start = time()
print('\nModelling...')
s = Solver()

try:
    s.add(parse_smt2_file('smtfile.smt2'))
except z3types.Z3Exception:
    print('Incorrect syntax or missing file. Exiting now.')
    exit(0)

print('Finished modelling.\n')
print('Checking...')
evaluation = s.check()
print(('SATISFIABLE' if evaluation == sat else 'UNSATISFIABLE'))
time_end1 = time()-time_start


if evaluation == sat:
    m = s.model()
    input = [(str(d), int(str(m[d]))) for d in m if str(d) == 'input1' or str(d) == 'input2']
    input.sort()
    print(f'- input_1 = {str(hex(int(str(input[0][1]))))[2:].upper()}')
    print(f'- input_2 = {str(hex(int(str(input[1][1]))))[2:].upper()}')

    output1 = [(int(str(d)[1:]), int(str(m[d]))) for d in m if str(d)[0] == 'j']
    output1.sort()
    res = ''
    for tuple in output1:
        res += str(tuple[1])
    key_str = str(hex(int(res, 2)))[2:].upper()
    if len(key_str) != 34:
        temp = '0'
        temp += key_str
        key_str = temp
    print(f'- state_1 = {key_str}')

    output1 = [(int(str(d)[1:]), int(str(m[d]))) for d in m if str(d)[0] == 'k']
    output1.sort()
    res = ''
    for tuple in output1:
        res += str(tuple[1])
    key_str = str(hex(int(res, 2)))[2:].upper()
    if len(key_str) != 34:
        temp = '0'
        temp += key_str
        key_str = temp
    print(f'- state_2 = {key_str}')


time_end2 = time()-time_start
print(f'\nSolving took {round(time_end1, 5)} seconds, total execution time was {round(time_end2, 5)} seconds.')