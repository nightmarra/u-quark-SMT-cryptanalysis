# runtime configuration HERE #
# input length in whole bytes
INPUT_LENGTH = 2
OUTPUT_STR = 'bc78f0e1c2850a152a55aa54a952a44890'
ROUNDS_U = 1
PARALLEL = True
WRITE_MODEL_TO_FILE = True
##############################

from time import time
from z3 import *


CAPACITY = 16
RATE = 1
WIDTH = 17
DIGEST = WIDTH
MAXDIGEST = 48

if PARALLEL:
    set_param('parallel.enable', True)
INPUT_LENGTH *= 8
print(f'- output: {OUTPUT_STR.upper()}')
OUTPUT_STR = bytes.fromhex(OUTPUT_STR)


def get_state(x):
    string = ''
    buf = 0
    for i in range(8 * WIDTH):
        buf ^= (1 & x[i]) << (7 - (i % 8))
        if ((i % 8) == 7) and i:
            to_add = ''.join(x for x in hex(buf)[2:])
            if len(to_add) == 1:
                string += '0'
            string += to_add
            buf = 0
    res = list(bytes.fromhex(string))
    return res


input1 = BitVec('input1', INPUT_LENGTH)
input2 = BitVec('input2', INPUT_LENGTH)
key1 = [BitVec(f'j{i}', 8) for i in range(8*WIDTH)]
key2 = [BitVec(f'k{i}', 8) for i in range(8*WIDTH)]

output = [None] * 8*WIDTH
for i in range(8 * WIDTH):
    output[i] = (OUTPUT_STR[int(i / 8)] >> (7-(i % 8))) & 1
output = get_state(output)


def permute(x):
    N_LEN_U = 68
    L_LEN_U = 10

    X = [None] * (N_LEN_U + ROUNDS_U)
    Y = [None] * (N_LEN_U + ROUNDS_U)
    L = [None] * (L_LEN_U + ROUNDS_U)

    for i in range(N_LEN_U):
        X[i] = x[i]
        Y[i] = x[i+N_LEN_U]

    for i in range(L_LEN_U):
        L[i] = 0xFFFFFFFF

    for i in range(ROUNDS_U):
        X[N_LEN_U+i]  = X[i] ^ Y[i]
        X[N_LEN_U+i] ^= (X[i+9] ^ X[i+14] ^ X[i+21] ^ X[i+28] ^ X[i+33] ^ X[i+37] ^ X[i+45] ^ X[i+52] ^ X[i+55] ^ X[i+50] ^
                        ( X[i+59] & X[i+55] ) ^ ( X[i+37] & X[i+33] ) ^ ( X[i+15] & X[i+9] ) ^
                        ( X[i+55] & X[i+52] & X[i+45] ) ^ ( X[i+33] & X[i+28] & X[i+21] ) ^
                        ( X[i+59] & X[i+45] & X[i+28] & X[i+9] ) ^
                        ( X[i+55] & X[i+52] & X[i+37] & X[i+33] ) ^
                        ( X[i+59] & X[i+55] & X[i+21] & X[i+15] ) ^
                        ( X[i+59] & X[i+55] & X[i+52] & X[i+45] & X[i+37] ) ^
                        ( X[i+33] & X[i+28] & X[i+21] & X[i+15] & X[i+9] ) ^
                        ( X[i+52] & X[i+45] & X[i+37] & X[i+33] & X[i+28] & X[i+21] ))
        
        Y[N_LEN_U+i]  = Y[i];
        Y[N_LEN_U+i] ^= (Y[i+7] ^ Y[i+16] ^ Y[i+20] ^ Y[i+30] ^
                        Y[i+35]  ^ Y[i+37] ^ Y[i+42] ^ Y[i+51] ^ Y[i+54] ^  Y[i+49] ^
                        ( Y[i+58] & Y[i+54] ) ^ ( Y[i+37] & Y[i+35] ) ^ ( Y[i+15] & Y[i+7] ) ^
                        ( Y[i+54] & Y[i+51] & Y[i+42] ) ^ ( Y[i+35] & Y[i+30] & Y[i+20] ) ^
                        ( Y[i+58] & Y[i+42] & Y[i+30] & Y[i+7] ) ^
                        ( Y[i+54] & Y[i+51] & Y[i+37] & Y[i+35] ) ^
                        ( Y[i+58] & Y[i+54] & Y[i+20] & Y[i+15] ) ^
                        ( Y[i+58] & Y[i+54] & Y[i+51] & Y[i+42] & Y[i+37] ) ^
                        ( Y[i+35] & Y[i+30] & Y[i+20] & Y[i+15] & Y[i+7] ) ^
                        ( Y[i+51] & Y[i+42] & Y[i+37] & Y[i+35] & Y[i+30] & Y[i+20] ))
        
        L[L_LEN_U+i]  = L[i]
        L[L_LEN_U+i] ^= L[i+3]

        h = (X[i+25] ^ Y[i+59] ^ ( Y[i+3] & X[i+55] ) ^ ( X[i+46] & X[i+55] ) ^ ( X[i+55] & Y[i+59] ) ^
        ( Y[i+3] & X[i+25] & X[i+46] ) ^ ( Y[i+3] & X[i+46] & X[i+55] ) ^ ( Y[i+3] & X[i+46] & Y[i+59] ) ^
        ( X[i+25] & X[i+46] & Y[i+59] & L[i] ) ^ ( X[i+25] & L[i] ))
        h ^= X[i+1] ^ Y[i+2] ^ X[i+4] ^ Y[i+10] ^ X[i+31] ^ Y[i+43] ^ X[i+56] ^ L[i]

        X[N_LEN_U+i] ^= h
        Y[N_LEN_U+i] ^= h

    res = [None] * 8*WIDTH
    for i in range(N_LEN_U):
        res[i] = X[ROUNDS_U+i] & 1
        res[i+N_LEN_U] = Y[ROUNDS_U+i] & 1
    return res


def finalize(x):
    x[8*(WIDTH - RATE)] ^= 1

    out = [0] * MAXDIGEST
    outbytes = 0
    for _ in range(17):
        x = permute(x)
        for i in range(8):
            u = x[8*(WIDTH - RATE) + i + 8*(outbytes % RATE)] & 1
            out[outbytes] ^= (u << (7 - i))
        outbytes += 1
    return out

def process(x, input):
    pos = 0
    state = []
    for i in range(len(x)):
        state.append(x[i])
    for i in range(INPUT_LENGTH // 8):
        input_part = Extract(INPUT_LENGTH-8*i-1, INPUT_LENGTH-8*i-8, input)
        for j in range(8*pos, 8*pos + 8):
            # shift_with = (LShR(input, i) & 1)
            shift_with = (input_part >> j & 1)
            state[8*(WIDTH - RATE) + j] ^= shift_with
        state = permute(state)
    return finalize(state)


time_start = time()
print('\nModelling...')
s = Solver()
s.add([process(key1, input1)[i] == output[i] for i in range(DIGEST)])
s.add([process(key2, input2)[i] == output[i] for i in range(DIGEST)])
s.add(input1 != input2)
print('Finished modelling.\n')

if WRITE_MODEL_TO_FILE:
    with open('smtfile.smt2', '+w') as f:
        f.write(s.sexpr())

print('Checking...')
evaluation = s.check()
print(('SATISFIABLE' if evaluation == sat else 'UNSATISFIABLE'))
time_end1 = time()-time_start


if evaluation == sat:
    m = s.model()
    input1_string = str(hex(int(str(m[input1])))).upper()[2:]
    if len(input1_string) % 2 != 0:
        input1_string = '0' + input1_string
    input2_string = str(hex(int(str(m[input2])))).upper()[2:]
    if len(input2_string) % 2 != 0:
        input2_string = '0' + input2_string
    print(f'- input_1 = {input1_string}')
    print(f'- input_2 = {input2_string}')

    key1_output = [(int(str(d)[1:]), int(str(m[d]))) for d in m if (str(d)[0] == 'j')]
    key1_output.sort()
    key2_output = [(int(str(d)[1:]), int(str(m[d]))) for d in m if (str(d)[0] == 'k')]
    key2_output.sort()

    res = ''
    for tuple in key1_output:
        res += str(tuple[1])
    key1_str = str(hex(int(res, 2)))[2:].upper()
    if len(key1_str) != 34:
        temp = '0'
        temp += key1_str
        key1_str = temp
    print(f'- state_1 = {key1_str}')
    
    res = ''
    for tuple in key2_output:
        res += str(tuple[1])
    key2_str = str(hex(int(res, 2)))[2:].upper()
    if len(key2_str) != 34:
        temp = '0'
        temp += key2_str
        key2_str = temp
    print(f'- state_2 = {key2_str}')

time_end2 = time()-time_start
print(f'\nSolving took {round(time_end1, 5)} seconds, total execution time was {round(time_end2, 5)} seconds.')