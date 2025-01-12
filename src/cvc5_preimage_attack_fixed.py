# runtime configuration HERE #
# input length in whole bytes
INPUT_LENGTH = 64
OUTPUT_STR = '848ee5bfe92365fdb812612365b12256d5'
ROUNDS_U = 5
GET_INITIAL_STATE = False
WRITE_MODEL_TO_FILE = False
##############################

from time import time
from cvc5.pythonic import *


CAPACITY = 16
RATE = 1
WIDTH = 17
DIGEST = WIDTH
MAXDIGEST = 48

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


input = BitVec('input', INPUT_LENGTH)
key = [1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1,
         1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1,
           0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0,
             0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1,
               1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1,
                 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1, 1,
                   1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1,
                    0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1, 1]

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
s.add([process(key, input)[i] == output[i] for i in range(DIGEST)])
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
    print(f'- input = {str(hex(int(str(m[input])))).upper()[2:]}')


time_end2 = time()-time_start
print(f'\nSolving took {round(time_end1, 5)} seconds, total execution time was {round(time_end2, 5)} seconds.')