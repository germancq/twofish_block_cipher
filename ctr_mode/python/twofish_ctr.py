#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : twofish_ctr.py
# Author            : German C.Quiveu <germancq@dte.us.es>
# Date              : 17.06.2026
# Last Modified Date: 17.06.2026
# Last Modified By  : German C.Quiveu <germancq@dte.us.es>

import math
import struct

'''
key 128 bits
'''

MDS = [[0x01, 0xef, 0x5b, 0x5b],
       [0x5b, 0xef, 0xef, 0x01],
       [0xef, 0x5b, 0x01, 0xef],
       [0xef, 0x01, 0xef, 0x5b]]

RS = [[0x01, 0xa4, 0x55, 0x87, 0x5a, 0x58, 0xdb, 0x9e],
      [0xa4, 0x56, 0x82, 0xf3, 0x1e, 0xc6, 0x68, 0xe5],
      [0x02, 0xa1, 0xfc, 0xc1, 0x47, 0xae, 0x3d, 0x19],
      [0xa4, 0x55, 0x87, 0x5a, 0x58, 0xdb, 0x9e, 0x03]]

Sbox_q0 = [[0x8, 0x1, 0x7, 0xD, 0x6, 0xF, 0x3, 0x2, 0x0, 0xB, 0x5, 0x9, 0xE, 0xC, 0xA, 0x4],
           [0xE, 0xC, 0xB, 0x8, 0x1, 0x2, 0x3, 0x5,
               0xF, 0x4, 0xA, 0x6, 0x7, 0x0, 0x9, 0xD],
           [0xB, 0xA, 0x5, 0xE, 0x6, 0xD, 0x9, 0x0,
               0xC, 0x8, 0xF, 0x3, 0x2, 0x4, 0x7, 0x1],
           [0xD, 0x7, 0xF, 0x4, 0x1, 0x2, 0x6, 0xE, 0x9, 0xB, 0x3, 0x0, 0x8, 0x5, 0xC, 0xA]]

Sbox_q1 = [[0x2, 0x8, 0xB, 0xD, 0xF, 0x7, 0x6, 0xE, 0x3, 0x1, 0x9, 0x4, 0x0, 0xA, 0xC, 0x5],
           [0x1, 0xE, 0x2, 0xB, 0x4, 0xC, 0x3, 0x7,
               0x6, 0xD, 0xA, 0x5, 0xF, 0x9, 0x0, 0x8],
           [0x4, 0xC, 0x7, 0x5, 0x1, 0x6, 0x9, 0xA,
               0x0, 0xE, 0xD, 0x8, 0x2, 0xB, 0x3, 0xF],
           [0xB, 0x9, 0x5, 0x1, 0xC, 0x3, 0xD, 0xE, 0x6, 0x4, 0x7, 0xF, 0x2, 0x0, 0x8, 0xA]]


class Twofish_CTR:

    def __init__(self, key, iv):
        k = key_schedule(key)
        self.iv = iv
        self.M_e = k[0]
        self.M_o = k[1]
        self.S_i = k[2]

    def encryption_decryption(self, text, block_number):
        '''
        plaintext_3 = swap32(plaintext & (2**32 - 1))
        plaintext_2 = swap32((plaintext>>32) & (2**32 - 1))
        plaintext_1 = swap32((plaintext>>64) & (2**32 - 1))
        plaintext_0 = swap32((plaintext>>96) & (2**32 - 1))
        '''
        plaintext = self.iv + block_number
        plaintext_0 = plaintext & (2**32 - 1)
        plaintext_1 = (plaintext >> 32) & (2**32 - 1)
        plaintext_2 = (plaintext >> 64) & (2**32 - 1)
        plaintext_3 = (plaintext >> 96) & (2**32 - 1)
        # print(hex(plaintext_0))
        # print(hex(plaintext_1))
        # print(hex(plaintext_2))
        # print(hex(plaintext_3))

        k_0 = generate_K_values(0, self.M_e, self.M_o)
        # print(hex(k_0[0]))
        # print(hex(k_0[1]))

        k_1 = generate_K_values(1, self.M_e, self.M_o)

        # print(hex(k_1[0]))
        # print(hex(k_1[1]))

        R_0 = plaintext_0 ^ k_0[0]
        R_1 = plaintext_1 ^ k_0[1]
        R_2 = plaintext_2 ^ k_1[0]
        R_3 = plaintext_3 ^ k_1[1]

        for i in range(0, 16):
            '''
            print(i)
            print("R_values")
            print(hex(R_0))
            print(hex(R_1))
            print(hex(R_2))
            print(hex(R_3))
            '''
            '''
            aux_0 = R_0
            aux_1 = R_1
            f = function_F(R_0,R_1,i,self.M_e,self.M_o,self.S_i)
            
            R_0 = ROR(f[0] ^ R_2, 1, 32)      
            R_1 = ROL(R_3,1,32) ^ f[1]  
            R_2 = aux_0
            R_3 = aux_1
            '''
            R_values = enc_stage(R_0, R_1, R_2, R_3,
                                 self.M_e, self.M_o, self.S_i, i)
            R_0 = R_values[0]
            R_1 = R_values[1]
            R_2 = R_values[2]
            R_3 = R_values[3]

        k_2 = generate_K_values(2, self.M_e, self.M_o)
        # print(hex(k_2[0]))
        # print(hex(k_2[1]))
        k_3 = generate_K_values(3, self.M_e, self.M_o)
        # print(hex(k_3[0]))
        # print(hex(k_3[1]))
        #
        '''
        print("16") 
        print(hex(R_0))
        print(hex(R_1))
        print(hex(R_2))
        print(hex(R_3))   
        '''
        C_0 = R_2 ^ k_2[0]
        C_1 = R_3 ^ k_2[1]
        C_2 = R_0 ^ k_3[0]
        C_3 = R_1 ^ k_3[1]
        '''
        print(hex(C_0))
        print(hex(C_1))
        print(hex(C_2))
        print(hex(C_3))
        '''
        enc_value = (C_3 << 96) + (C_2 << 64) + (C_1 << 32) + C_0
        return enc_value ^ text

    '''
    def decrypt(self,ciphertext):
        ciphertext_0 = ciphertext & (2**32 - 1)
        ciphertext_1 = (ciphertext>>32) & (2**32 - 1)
        ciphertext_2 = (ciphertext>>64) & (2**32 - 1)
        ciphertext_3 = (ciphertext>>96) & (2**32 - 1)
        #print(hex(ciphertext_0))
        #print(hex(ciphertext_1))
        #print(hex(ciphertext_2))
        #print(hex(ciphertext_3))

        k_2 = generate_K_values(2,self.M_e,self.M_o)   
        k_3 = generate_K_values(3,self.M_e,self.M_o)

        R_0 = ciphertext_0 ^ k_2[0]
        R_1 = ciphertext_1 ^ k_2[1]
        R_2 = ciphertext_2 ^ k_3[0]
        R_3 = ciphertext_3 ^ k_3[1]

        for i in range(0,16):
            j = 15-i
            
            R_values = dec_stage(R_0,R_1,R_2,R_3,self.M_e,self.M_o,self.S_i,j)
            R_0 = R_values[0]
            R_1 = R_values[1]
            R_2 = R_values[2]
            R_3 = R_values[3]

        #print("-1") 
        #print(hex(R_0))
        #print(hex(R_1))
        #print(hex(R_2))
        #print(hex(R_3))


        k_0 = generate_K_values(0,self.M_e,self.M_o)
        k_1 = generate_K_values(1,self.M_e,self.M_o)
            
        C_0 = R_2 ^ k_0[0]
        C_1 = R_3 ^ k_0[1]
        C_2 = R_0 ^ k_1[0]
        C_3 = R_1 ^ k_1[1]
        #print(hex(C_0))
        #print(hex(C_1))
        #print(hex(C_2))
        #print(hex(C_3))


        return (C_3 << 96) + (C_2 << 64) + (C_1 << 32) + C_0 
    '''


def enc_stage(R_0, R_1, R_2, R_3, M_e, M_o, S_i, i):
    aux_0 = R_0
    aux_1 = R_1
    f = function_F(R_0, R_1, i, M_e, M_o, S_i)

    R_0 = ROR(f[0] ^ R_2, 1, 32)
    R_1 = ROL(R_3, 1, 32) ^ f[1]
    R_2 = aux_0
    R_3 = aux_1
    return (R_0, R_1, R_2, R_3)


def dec_stage(R_0, R_1, R_2, R_3, M_e, M_o, S_i, j):
    aux_0 = R_0
    aux_1 = R_1
    f = function_F(R_0, R_1, j, M_e, M_o, S_i)

    R_0 = ROL(R_2, 1, 32) ^ f[0]
    # R_0 = ROR(f[0] ^ R_2, 1, 32)
    R_1 = ROR(f[1] ^ R_3, 1, 32)
    # R_1 = ROL(R_3,1,32) ^ f[1]
    R_2 = aux_0
    R_3 = aux_1
    return (R_0, R_1, R_2, R_3)


def function_F(x, y, round, M_e, M_o, S_i):

    T0 = function_g(x, S_i)
    y = ROL(y, 8, 32)
    T1 = function_g(y, S_i)
    K_r = generate_K_values(round+4, M_e, M_o)
    # print("T_values")
    # print(round)

    # print(hex(T0))
    # print(hex(T1))
    F0 = (T0 + T1 + K_r[0]) & (2**32 - 1)
    F1 = (T0 + (T1 << 1) + K_r[1]) & (2**32 - 1)
    return (F0, F1)


def function_g(x, S_i):

    return function_h(x, S_i)


def key_schedule(key):
    '''
    m_i = [[] for i in range(8)]
    M_i = []
    S_i = []
    for i in range(0,2):
        for j in range(0,8):
            m_i[i].append((key>>(8*(i+j))) & 0xFF)
        r = matrix_multiplication_GF256(RS,m_i[i],0x169)

        S_i.append((r[3][0]<<24) + (r[2][0]<<16) + (r[1][0]<<8) + r[0][0])

    for i in range(0,8) :
        M_i.append((key >> 32*i) & 0xFFFFFFFF)
    '''
    m_i = [[] for i in range(8)]
    S_i = []
    s_i = []
    for i in range(0, 2):
        for j in range(0, 8):
            x = (key >> (64*i)) & 0xFFFFFFFFFFFFFFFF
            x = (x >> (j*8)) & 0xFF
            m_i[i].append(x)

        r = matrix_multiplication_GF256(RS, m_i[i], 0x14D)

        s_i.append((r[3][0] << 24) + (r[2][0] << 16) +
                   (r[1][0] << 8) + r[0][0])

    key_0 = key & (2**32 - 1)
    key_1 = (key >> 32) & (2**32 - 1)
    key_2 = (key >> 64) & (2**32 - 1)
    key_3 = (key >> 96) & (2**32 - 1)

    M_e = [key_0, key_2]
    M_o = [key_1, key_3]
    S_i = [s_i[1], s_i[0]]

    '''
    print("KEY VALUES")
    print(hex(key_0))
    print(hex(key_1))
    print(hex(key_2))
    print(hex(key_3))
    print(hex(S_i[0]))
    print(hex(S_i[1]))
    print("END KEY VALUES")
    '''

    return (M_e, M_o, S_i)


def swap32(x):
    return (((x << 24) & 0xFF000000) |
            ((x << 8) & 0x00FF0000) |
            ((x >> 8) & 0x0000FF00) |
            ((x >> 24) & 0x000000FF))


def function_h(X, L):
    # print("start function_h")
    # print(hex(X))
    # print(L)

    selected_boxes = [[0, 1, 0, 1],
                      [0, 0, 1, 1],
                      [1, 0, 1, 0]]
    input_x = X
    y = 0
    for i in range(0, 3):
        x_0 = input_x & 0xFF
        x_1 = (input_x >> 8) & 0xFF
        x_2 = (input_x >> 16) & 0xFF
        x_3 = (input_x >> 24) & 0xFF

        y_0 = generate_q_output(selected_boxes[i][0], x_0)
        y_1 = generate_q_output(selected_boxes[i][1], x_1)
        y_2 = generate_q_output(selected_boxes[i][2], x_2)
        y_3 = generate_q_output(selected_boxes[i][3], x_3)

        y = ((y_3 << 24) + (y_2 << 16) + (y_1 << 8) + y_0)
        # print(hex(y))

        if (i != 2):
            input_x = y ^ L[1-i]

        # y = y & (2**32 - 1)

    # print(hex(y))
    z_matrix = matrix_multiplication_GF256(MDS, [y_0, y_1, y_2, y_3], 0x169)

    # print(hex(z_matrix[3][0]))
    # print(hex(z_matrix[2][0]))
    # print(hex(z_matrix[1][0]))
    # print(hex(z_matrix[0][0]))

    z_3 = z_matrix[3][0] & 0xFF
    z_2 = z_matrix[2][0] & 0xFF
    z_1 = z_matrix[1][0] & 0xFF
    z_0 = z_matrix[0][0] & 0xFF

    z = ((z_3 << 24) +
         (z_2 << 16) +
         (z_1 << 8) +
         (z_0))

    # print("end function_h")

    return z


def generate_q_output(q_i, x):

    t_box = Sbox_q0
    if (q_i == 1):
        t_box = Sbox_q1

    a0 = x >> 4 & 0xf
    b0 = x & 0xf
    a1 = a0 ^ b0
    b1 = a0 ^ ROR(b0, 1, 4) ^ ((a0 << 3) & 0xF)
    a2 = t_box[0][a1]
    b2 = t_box[1][b1]
    a3 = a2 ^ b2
    b3 = a2 ^ ROR(b2, 1, 4) ^ ((a2 << 3) & 0xF)
    a4 = t_box[2][a3]
    b4 = t_box[3][b3]

    z = (b4 << 4) + a4

    return z & 0xFF


def generate_K_values(i, M_e, M_o):
    # print(i)
    p = 2**24 + 2**16 + 2**8 + 2**0
    # print(hex(2*i*p))
    # print(hex((2*i+1)*p))
    A = function_h(2*i*p, M_e)
    # print(hex(A))
    B = function_h((2*i+1)*p, M_o)
    # print(hex(B))
    B = ROL(B, 8, 32)
    # print(hex(B))
    K_0 = (A+B) % (2**32)  # K_2i
    K_1 = (A+(B << 1)) % (2**32)
    K_1 = ROL(K_1, 9, 32)  # K_2i+1
    return (K_0, K_1)


def matrix_multiplication_GF256(M1, M2, p):

    rows_a = len(M1)
    rows_b = len(M2)  # == colums_a
    colums_a = rows_b
    colums_b = 1
    if (type(M2[0]) is list):
        colums_b = len(M2[0])

    result = []

    for i in range(0, rows_a):
        result.append([])
        for j in range(0, colums_b):
            result[i].append(0)
            for k in range(0, rows_b):
                a_1 = result[i][j]

                if (colums_b > 1):
                    a_3 = M2[k][j]
                else:
                    a_3 = M2[k]

                if (colums_a > 1):
                    a_2 = M1[i][k]
                else:
                    a_2 = M1[k]

                # result[i][j] = (a_1 + (a_2 * a_3))
                gf_1 = galois_multiplication(a_2, a_3, p)
                '''
                print("==========================")
                print(i)
                print(j)
                print(hex(a_2))
                print(hex(a_3))
                print(hex(gf_1))
                print(hex(a_1))
                print("==========================")
                '''
                result[i][j] = galois_add(a_1, gf_1)

    return result


def galois_add(a, b):
    return a ^ b


def galois_multiplication(a, b, p):
    # GF(256)
    t = 0
    for i in range(0, 8):
        mask = 0x1 << i
        bit_b = b & mask
        b_i = 0 if bit_b == 0 else 1
        r = b_i*(a << i)
        t = galois_add(t, r)

    t = reduced_polinomial_GF256(t, p)

    return t


def reduced_polinomial_GF256(a, p):
    # grado del polinomio p
    n = math.ceil(math.log(p, 2))
    n = n - 1
    t = a
    for i in range(15, 7, -1):
        mask = 0x1 << i
        bit_t = t & mask
        t_i = 0 if bit_t == 0 else 1
        if (t_i):
            m = int(i - n)
            t = galois_add(p << m, t)

    return t


def ROL(x, i, len_bits):
    j = len_bits - i
    return ((x << i) | (x >> j)) & (2**len_bits - 1)


def ROR(x, i, len_bits):
    j = len_bits - i
    return ((x >> i) | (x << j)) & (2**len_bits - 1)


def changeEndiannes_128(a):
    a_3 = swap32(a & (2**32 - 1))
    a_2 = swap32((a >> 32) & (2**32 - 1))
    a_1 = swap32((a >> 64) & (2**32 - 1))
    a_0 = swap32((a >> 96) & (2**32 - 1))

    a_swap = (a_3 << 96) + (a_2 << 64) + (a_1 << 32) + a_0

    return a_swap


if __name__ == "__main__":

    key = 0x9F589F5CF6122C32B6BFEC2F2AE8C35A
    iv = 0xa9876e45234aaabbbcc9645668636489
    text = 0x0
    ciphertext = 0xf3e9b4ffc2b3edc6aa5b4c64b9b24c0d

    plaintext = changeEndiannes_128(text)
    ciphertext = changeEndiannes_128(ciphertext)
    key = changeEndiannes_128(key)
    iv = changeEndiannes_128(iv)

    cipher = Twofish_CTR(key, iv)

    for i in range(0, 2):
        ciphertext = cipher.encryption_decryption(text, i)
        print("************************************")
        plaintext = cipher.encryption_decryption(ciphertext, i)

        # result = galois_multiplication(0x5b,0xfc,0x169)
        # result = matrix_multiplication_GF256(MDS,[0x98,0xCA,0xe0,0xFC],0x169)
        if (text != plaintext):
            print("ERROR")
        else:
            print(hex(plaintext))
            print(hex(ciphertext))

        z = 0
        for i in range(0, 16):
            x = ((ciphertext >> 8*i & 0xFF) << 8*(15-i))
            z = z | x

        print(hex(z))
        # print(result)
