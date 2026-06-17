#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : twofish_test.py
# Author            : German C.Quiveu <germancq@dte.us.es>
# Date              : 17.06.2026
# Last Modified Date: 17.06.2026
# Last Modified By  : German C.Quiveu <germancq@dte.us.es>

import cocotb
import numpy as np
import time
import random
import math
from cocotb.triggers import Timer, RisingEdge, FallingEdge
from cocotb.regression import TestFactory
from cocotb.result import TestFailure, ReturnValue
from cocotb.clock import Clock


import os

home = os.getenv("HOME")
abs_path_file_storage = (
    home
    + "/gitProjects/IPCores/block_ciphers/twofish_cipher/python_code/test_cases.HEX"
)

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
    cocotb.fork(Clock(dut.clk, CLK_PERIOD).start())
    dut.key = key
    dut.enc_dec = enc_dec
    dut.text_input = text_input
    dut.rst = 1


@cocotb.coroutine
def rst_function_test(dut, enc_dec):

    dut.rst = 1

    yield n_cycles_clock(dut, 10)

    if dut.R0 != 0:
        raise TestFailure(
            """Error R0 in rst, wrong_value = {0}""".format(
                hex(int(dut.R0.value)))
        )
    if dut.R1 != 0:
        raise TestFailure(
            """Error R1 in rst, wrong_value = {0}""".format(
                hex(int(dut.R1.value)))
        )
    if dut.R2 != 0:
        raise TestFailure(
            """Error R2 in rst, wrong_value = {0}""".format(
                hex(int(dut.R2.value)))
        )
    if dut.R3 != 0:
        raise TestFailure(
            """Error R3 in rst, wrong_value = {0}""".format(
                hex(int(dut.R3.value)))
        )

    if enc_dec == 1:
        if dut.counter_out != 15:
            raise TestFailure(
                """Error counter in rst decrypt, wrong_value = {0}""".format(
                    hex(int(dut.counter_out.value))
                )
            )
    else:
        if dut.counter_out != 0:
            raise TestFailure(
                """Error counter in rst encrypt, wrong_value = {0}""".format(
                    hex(int(dut.counter_out.value))
                )
            )

    dut.rst = 0


@cocotb.coroutine
def enc_dec_test(dut, expected_value):
    print("VERILOG_VALUES")
    while dut.end_signal == 0:
        if dut.current_state == 3:
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
    if dut.text_output != expected_value:
        raise TestFailure(
            """Error enc_test,wrong value = {0}, expected value is {1}""".format(
                hex(int(dut.text_output.value)), hex(expected_value)
            )
        )


@cocotb.coroutine
def n_cycles_clock(dut, n):
    for i in range(0, n):
        yield RisingEdge(dut.clk)
        yield FallingEdge(dut.clk)


@cocotb.coroutine
def run_test(dut, index=0):

    with open(abs_path_file_storage, "rb+") as storage_file:

        storage_file.seek((index * 64))
        key = int.from_bytes(storage_file.read(16), byteorder="little")
        text = int.from_bytes(storage_file.read(16), byteorder="little")
        expected_enc_value = int.from_bytes(
            storage_file.read(16), byteorder="little")
        expected_dec_value = int.from_bytes(
            storage_file.read(16), byteorder="little")

        setup_function(dut, key, 0, text)
        yield rst_function_test(dut, 0)
        yield enc_dec_test(dut, expected_enc_value)
        # decrypt
        # print("DECRYPT")
        setup_function(dut, key, 1, text)
        yield rst_function_test(dut, 1)
        yield enc_dec_test(dut, expected_dec_value)


n = 500
factory = TestFactory(run_test)

# array de 10 int aleatorios entre 0 y 31
factory.add_option("index", range(0, n))
factory.generate_tests()
