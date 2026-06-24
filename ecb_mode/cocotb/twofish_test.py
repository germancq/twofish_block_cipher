#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : twofish_test.py
# Author            : German C.Quiveu <germancq@dte.us.es>
# Date              : 17.06.2026
# Last Modified Date: 17.06.2026
# Last Modified By  : German C.Quiveu <germancq@dte.us.es>

import math
import os
import random
import time

import cocotb
import numpy as np
import twofish
from cocotb.clock import Clock
from cocotb.regression import TestFactory
from cocotb.triggers import FallingEdge, RisingEdge, Timer

home = os.getenv("HOME")

CLK_PERIOD = 20  # 50 MHz

# the keyword yield
#   Testbenches built using Cocotb use coroutines.
#   While the coroutine is executing the simulation is paused.
#   The coroutine uses the yield keyword
#   to pass control of execution back to
#   the simulator and simulation time can advance again.
#
#   yield return when the 'Trigger' is resolve
#
#   Coroutines may also yield a list of triggers
#   to indicate that execution should resume if any of them fires


def setup_function(dut, key, enc_dec, text_input):
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD, unit="ns").start())
    dut.key.value = key
    dut.enc_dec.value = enc_dec
    dut.text_input.value = text_input
    dut.rst.value = 1


async def rst_function_test(dut, enc_dec):

    dut.rst = 1

    yield n_cycles_clock(dut, 10)

    if dut.R0 != 0:
        assert """Error R0 in rst, wrong_value = {0}""".format(
            hex(int(dut.R0.value)))
    if dut.R1 != 0:
        assert """Error R1 in rst, wrong_value = {0}""".format(
            hex(int(dut.R1.value)))
    if dut.R2 != 0:
        assert """Error R2 in rst, wrong_value = {0}""".format(
            hex(int(dut.R2.value)))
    if dut.R3 != 0:
        assert """Error R3 in rst, wrong_value = {0}""".format(
            hex(int(dut.R3.value)))

    if enc_dec == 1:
        if dut.counter_out.value != 15:
            assert """Error counter in rst decrypt, wrong_value = {0}""".format(
                hex(int(dut.counter_out.value))
            )
    else:
        if dut.counter_out.value != 0:
            assert """Error counter in rst encrypt, wrong_value = {0}""".format(
                hex(int(dut.counter_out.value))
            )

    dut.rst = 0


async def enc_dec_test(dut, expected_value):
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
        yield n_cycles_clock(dut, 1)

    print(hex(int(dut.text_output.value)))
    if dut.text_output.value != expected_value:
        assert """Error enc_test,wrong value = {0}, expected value is {1}""".format(
            hex(int(dut.text_output.value)), hex(expected_value)
        )


async def n_cycles_clock(dut, n):
    for i in range(0, n):
        yield RisingEdge(dut.clk)
        yield FallingEdge(dut.clk)


async def run_test(dut, index=0):

    random.seed(index)

    key = random.getrandbits(128)
    text = random.getrandbits(128)
    sw_model = twofish.Twofish(key)
    expected_enc_value = sw_model.encrypt(text)
    expected_dec_value = sw_model.decrypt(text)

    setup_function(dut, key, 0, text)
    yield rst_function_test(dut, 0)
    yield enc_dec_test(dut, expected_enc_value)
    # decrypt
    # print("DECRYPT")
    setup_function(dut, key, 1, text)
    yield rst_function_test(dut, 1)
    yield enc_dec_test(dut, expected_dec_value)


n = 20
factory = TestFactory(run_test)

# array de 10 int aleatorios entre 0 y 31
factory.add_option("index", range(0, n))
factory.generate_tests()
