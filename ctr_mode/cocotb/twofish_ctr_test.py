#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : twofish_ctr_test.py
# Author            : German C.Quiveu <germancq@dte.us.es>
# Date              : 17.06.2026
# Last Modified Date: 17.06.2026
# Last Modified By  : German C.Quiveu <germancq@dte.us.es>

import math
import os
import random
import time

import numpy as np
import twofish_ctr

import cocotb
from cocotb.clock import Clock
from cocotb.regression import TestFactory
from cocotb.result import ReturnValue, TestFailure
from cocotb.triggers import FallingEdge, RisingEdge, Timer

home = os.getenv("HOME")

CLK_PERIOD = 20  # 50 MHz
BLOCK_LEN = 128
KEY_LEN = 128
IV_LEN = 128

# the keyword await
#   Testbenches built using Cocotb use coroutines.
#   While the coroutine is executing the simulation is paused.
#   The coroutine uses the await keyword
#   to pass control of execution back to
#   the simulator and simulation time can advance again.
#
#   await return when the 'Trigger' is resolve
#
#   Coroutines may also await a list of triggers
#   to indicate that execution should resume if any of them fires


def setup_function(dut, key, IV, text_input, num_block):
    cocotb.fork(Clock(dut.clk, CLK_PERIOD).start())
    dut.key.value = key
    dut.IV.value = IV
    dut.text_input.value = text_input
    dut.block_number.value = num_block
    dut.rst.value = 1


async def rst_function_test(dut):

    dut.rst.value = 1

    await n_cycles_clock(dut, 10)

    if dut.R_i[0] != 0:
        raise TestFailure(
            """Error R0 in rst, wrong_value = {0}""".format(
                hex(int(dut.R_i[0].value)))
        )
    if dut.R_i[1] != 0:
        raise TestFailure(
            """Error R1 in rst, wrong_value = {0}""".format(
                hex(int(dut.R_i[1].value)))
        )
    if dut.R_i[2] != 0:
        raise TestFailure(
            """Error R2 in rst, wrong_value = {0}""".format(
                hex(int(dut.R_i[2].value)))
        )
    if dut.R_i[3] != 0:
        raise TestFailure(
            """Error R3 in rst, wrong_value = {0}""".format(
                hex(int(dut.R_i[3].value)))
        )

    if dut.counter_out != 0:
        raise TestFailure(
            """Error counter in rst encrypt, wrong_value = {0}""".format(
                hex(int(dut.counter_out.value))
            )
        )

    dut.rst.value = 0


async def enc_dec_test(dut, block_number, text_input, expected_value):

    dut.text_input.value = text_input
    dut.block_number.value = block_number

    print("VERILOG_VALUES")
    while dut.end_signal.value == 0:
        if dut.current_state.value == 3:
            """
            print('//////////////////////////')
            print(int(dut.counter_out.value))
            print(int(dut.stage_impl.i.value))
            print(hex(int(dut.stage_impl.R0.value)))
            print(hex(int(dut.stage_impl.R1.value)))
            print(hex(int(dut.stage_impl.R2.value)))
            print(hex(int(dut.stage_impl.R3.value)))
            print(hex(int(dut.R0.value)))
            print(hex(int(dut.R1.value)))
            print(hex(int(dut.R2.value)))
            print(hex(int(dut.R3.value)))
            print('//////////////////////////')
            """
        await n_cycles_clock(dut, 1)

    print(hex(int(dut.text_output.value)))
    if dut.text_output != expected_value:
        raise TestFailure(
            """Error enc_test,wrong value = {0}, expected value is {1}""".format(
                hex(int(dut.text_output.value)), hex(expected_value)
            )
        )


async def n_cycles_clock(dut, n):
    for i in range(0, n):
        await RisingEdge(dut.clk)
        await FallingEdge(dut.clk)


async def run_test(dut, index=0):

    n_blocks = 5

    key = random.getrandbits(KEY_LEN)
    iv = random.getrandbits(IV_LEN)

    print(hex(key))
    print(hex(iv))

    twofish_SW = twofish_ctr.Twofish_CTR(key, iv)

    setup_function(dut, key, iv, 0, 0)
    await rst_function_test(dut)

    for j in range(0, n_blocks):
        print(j)
        plaintext = random.getrandbits(BLOCK_LEN)

        ciphertext = twofish_SW.encryption_decryption(plaintext, j)

        if index == 0:
            await enc_dec_test(dut, j, plaintext, ciphertext)
        else:
            await enc_dec_test(dut, j, ciphertext, plaintext)

        await rst_function_test(dut)


n = 10
factory = TestFactory(run_test)

# array de 10 int aleatorios entre 0 y 31
factory.add_option("index", range(0, n))
factory.generate_tests()
