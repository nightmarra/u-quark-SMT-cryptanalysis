# runtime configuration HERE #
# input length allowed only in whole bytes
INPUT = 'FFFFFFFFFFFFFFFFFFFF'
KEY = 'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF'

ROUNDS_U = 1
##############################

CAPACITY = 16
RATE = 1
WIDTH = 17
DIGEST = WIDTH

assert len(INPUT) % 2 == 0 


class hashState:
    def __init__(self, pos, x):
        self.pos = pos
        self.x = x

iv = []
def convert_output_to_iv(key: str):
    hex_char = ''
    for i in range(len(key)):
        hex_char += key[i]
        if i % 2 != 0:
            iv.append((int(hex_char, 16)))
            hex_char = ''
convert_output_to_iv(KEY)

# initial state used in original u-Quark implementation
# iv = [0xd8,0xda,0xca,0x44,0x41,0x4a,0x09,0x97,0x19,0xc8,0x0a,0xa3,0xaf,0x06,0x56,0x44,0xdb]


def show_state(x: list):
    buf = 0
    for i in range(8*WIDTH):
        buf ^= (1 & x[i]) << (7 - (i % 8))
        if ((i % 8) == 7) and i:
            to_print = ''.join(x for x in hex(buf)[2:])
            if len(to_print) == 1:
                print('0', end='')
            print(to_print, end='')
            buf = 0
    print()


def permute_u(x: list):
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
        
        Y[N_LEN_U+i]  = Y[i]
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

    for i in range(N_LEN_U):
        x[i] = X[ROUNDS_U+i]
        x[i+N_LEN_U] = Y[ROUNDS_U+i]


def permute(x: list):
    print('state entering permute:', end='\n\t')
    show_state(x)
    permute_u(x)
    print('permute done', end='\n\t')
    show_state(x)


def init(state: hashState):
    print('enter init')
    for i in range(8 * WIDTH):
        state.x[i] = (iv[int(i / 8)] >> (7-(i % 8))) & 1
    state.pos = 0
    print('init done')
    show_state(state.x)


def update(state: hashState, data: list, data_byte_len: int):
    print('enter update')

    data_index = 0
    while data_byte_len > 0:
        print(f'state.pos = {state.pos}')
        u = data[data_index]
        print(u)
        print(f'get byte {hex(u)} at pos {state.pos}')

        for i in range(8*state.pos, 8*state.pos+8):
            state.x[8*(WIDTH - RATE) + i] ^= (u>>(i % 8)) & 1
        
        data_index += 1
        data_byte_len -= 1
        state.pos += 1

        if state.pos == RATE:
            permute(state.x)
            state.pos = 0

    print('update done')


def final(state: hashState, out: list):
    outbytes = 0
    print('enter final')
    state.x[8*(WIDTH - RATE) + state.pos*8] ^= 1
    permute(state.x)

    for i in range(DIGEST):
        out[i] = 0
    
    while outbytes < DIGEST:
        for i in range(8):
            u = state.x[8*(WIDTH - RATE) + i + 8*(outbytes % RATE)] & 1
            out[outbytes] ^= ( u << ( 7-i ) )
        print(f'extracted byte {out[outbytes]}, ({outbytes})')
        print('\n')

        outbytes += 1
        if outbytes == DIGEST:
            break

        if not (outbytes % RATE):
            permute(state.x)
    print('final done')


def quark(out: list, input: str):
    input_arr = list(bytearray.fromhex(input))
    print(input_arr)

    state = hashState(x=[None]*8*WIDTH, pos=0)
    init(state)
    update(state, input_arr, len(input_arr))
    final(state, out)

    input = str(input)
    if len(input) == 1:
        x = input
        input = '0x0' + x
    print(f'\nthe hashed version of {input} is: ')
    for i in range(DIGEST):
        to_print = ''.join(x for x in hex(out[i])[2:])
        if len(to_print) == 1:
            print('0', end='')
        print(to_print, end='')
    print()


MAXDIGEST = 48
def main():
    out = [None] * MAXDIGEST
    prefix = 'u'
    print(f'{prefix}-Quark')

    input = INPUT
    quark(out, input)
    i = 0
    while out[i] != None:
        print(out[i], end=' ')
        i += 1

if __name__ == '__main__':
    main()