/**
 * File              : twofish.sv
 * Author            : German C.Quiveu <germancq@dte.us.es>
 * Date              : 17.06.2026
 * Last Modified Date: 17.06.2026
 * Last Modified By  : German C.Quiveu <germancq@dte.us.es>
 */

module twofish (
    input clk,
    input rst,
    input enc_dec,
    input [127:0] key,
    input [127:0] text_input,
    output [127:0] text_output,
    output logic end_signal
);

  wire [31:0] Me[1:0];
  wire [31:0] Mo[1:0];
  wire [31:0] Si[1:0];

  key_schedule key_schedule_impl (
      .key(key),
      .Me (Me),
      .Mo (Mo),
      .Si (Si)
  );

  //k0,k1,k2,k3,k4,k5,k6,k7
  logic [31:0] K0;
  logic [31:0] K1;
  logic [31:0] K2;
  logic [31:0] K3;
  logic [31:0] K4;
  logic [31:0] K5;
  logic [31:0] K6;
  logic [31:0] K7;

  expanded_key_words key_words_0_1 (
      .i  (8'h0),
      .Me (Me),
      .Mo (Mo),
      .K_0(K0),
      .K_1(K1)
  );

  expanded_key_words key_words_2_3 (
      .i  (8'h1),
      .Me (Me),
      .Mo (Mo),
      .K_0(K2),
      .K_1(K3)
  );

  expanded_key_words key_words_4_5 (
      .i  (8'h2),
      .Me (Me),
      .Mo (Mo),
      .K_0(K4),
      .K_1(K5)
  );

  expanded_key_words key_words_6_7 (
      .i  (8'h3),
      .Me (Me),
      .Mo (Mo),
      .K_0(K6),
      .K_1(K7)
  );


  //Reg for R0,R1,R2,R3
  logic [31:0] R0;
  logic [31:0] R1;
  logic [31:0] R2;
  logic [31:0] R3;

  logic [31:0] R0_input;
  logic R0_w;
  logic R0_cl;

  register #(
      .DATA_WIDTH(32)
  ) R0_reg (
      .clk(clk),
      .cl(R0_cl),
      .w(R0_w),
      .din(R0_input),
      .dout(R0)
  );

  logic [31:0] R1_input;
  logic R1_w;
  logic R1_cl;

  register #(
      .DATA_WIDTH(32)
  ) R1_reg (
      .clk(clk),
      .cl(R1_cl),
      .w(R1_w),
      .din(R1_input),
      .dout(R1)
  );

  logic [31:0] R2_input;
  logic R2_w;
  logic R2_cl;

  register #(
      .DATA_WIDTH(32)
  ) R2_reg (
      .clk(clk),
      .cl(R2_cl),
      .w(R2_w),
      .din(R2_input),
      .dout(R2)
  );

  logic [31:0] R3_input;
  logic R3_w;
  logic R3_cl;

  register #(
      .DATA_WIDTH(32)
  ) R3_reg (
      .clk(clk),
      .cl(R3_cl),
      .w(R3_w),
      .din(R3_input),
      .dout(R3)
  );


  //Reg for Z0,Z1,Z2,Z3
  logic [31:0] Z0;
  logic [31:0] Z1;
  logic [31:0] Z2;
  logic [31:0] Z3;

  logic [31:0] Z0_output;
  logic Z0_w;
  logic Z0_cl;

  register #(
      .DATA_WIDTH(32)
  ) Z0_reg (
      .clk(clk),
      .cl(Z0_cl),
      .w(Z0_w),
      .din(Z0),
      .dout(Z0_output)
  );

  logic [31:0] Z1_output;
  logic Z1_w;
  logic Z1_cl;

  register #(
      .DATA_WIDTH(32)
  ) Z1_reg (
      .clk(clk),
      .cl(Z1_cl),
      .w(Z1_w),
      .din(Z1),
      .dout(Z1_output)
  );

  logic [31:0] Z2_output;
  logic Z2_w;
  logic Z2_cl;

  register #(
      .DATA_WIDTH(32)
  ) Z2_reg (
      .clk(clk),
      .cl(Z2_cl),
      .w(Z2_w),
      .din(Z2),
      .dout(Z2_output)
  );

  logic [31:0] Z3_output;
  logic Z3_w;
  logic Z3_cl;

  register #(
      .DATA_WIDTH(32)
  ) Z3_reg (
      .clk(clk),
      .cl(Z3_cl),
      .w(Z3_w),
      .din(Z3),
      .dout(Z3_output)
  );



  //contador
  logic [7:0] counter_in;
  mux2 #(
      .N(8)
  ) mux_0 (
      .a  (8'h0),
      .b  (8'hF),
      .sel(enc_dec),
      .c  (counter_in)
  );
  logic [7:0] counter_out;
  logic up_counter;
  logic down_counter;
  counter #(
      .DATA_WIDTH(8)
  ) counter_impl (
      .clk (clk),
      .rst (rst),
      .up  (up_counter),
      .down(down_counter),
      .din (counter_in),
      .dout(counter_out)
  );


  //stage

  twofish_stage stage_impl (
      .enc_dec(enc_dec),  //enc = 0, dec = 1
      .i(counter_out),
      .Me(Me),
      .Mo(Mo),
      .Si(Si),
      .R0(R0),
      .R1(R1),
      .R2(R2),
      .R3(R3),
      .Z0(Z0),
      .Z1(Z1),
      .Z2(Z2),
      .Z3(Z3)
  );

  //

  assign text_output = {R3, R2, R1, R0};

  //FSM
  typedef enum logic [3:0] {
    IDLE,
    INPUT_ENC,
    INPUT_DEC,
    STORE_OUTPUTS,
    UPDATE_INPUTS,
    WAIT_CHECK_FINAL,
    OUTPUT_ENC,
    OUTPUT_DEC,
    END
  } state_t;
  state_t current_state, next_state;


  always_comb begin

    next_state = current_state;

    down_counter = 0;
    up_counter = 0;
    R0_w = 0;
    R0_cl = 0;
    R1_w = 0;
    R1_cl = 0;
    R2_w = 0;
    R2_cl = 0;
    R3_w = 0;
    R3_cl = 0;
    Z0_w = 0;
    Z0_cl = 0;
    Z1_w = 0;
    Z1_cl = 0;
    Z2_w = 0;
    Z2_cl = 0;
    Z3_w = 0;
    Z3_cl = 0;
    R0_input = 0;
    R1_input = 0;
    R2_input = 0;
    R3_input = 0;
    end_signal = 0;

    case (current_state)
      IDLE: begin

        R0_cl = 1'b1;
        R1_cl = 1'b1;
        R2_cl = 1'b1;
        R3_cl = 1'b1;
        Z0_cl = 1'b1;
        Z1_cl = 1'b1;
        Z2_cl = 1'b1;
        Z3_cl = 1'b1;

        if (enc_dec == 1'b1) begin
          next_state = INPUT_DEC;
        end else begin
          next_state = INPUT_ENC;
        end


      end
      INPUT_ENC: begin
        R0_input = text_input[31:0] ^ K0;
        R1_input = text_input[63:32] ^ K1;
        R2_input = text_input[95:64] ^ K2;
        R3_input = text_input[127:96] ^ K3;
        R0_w = 1'b1;
        R1_w = 1'b1;
        R2_w = 1'b1;
        R3_w = 1'b1;
        next_state = WAIT_CHECK_FINAL;
      end
      INPUT_DEC: begin
        R0_input = text_input[31:0] ^ K4;
        R1_input = text_input[63:32] ^ K5;
        R2_input = text_input[95:64] ^ K6;
        R3_input = text_input[127:96] ^ K7;
        R0_w = 1'b1;
        R1_w = 1'b1;
        R2_w = 1'b1;
        R3_w = 1'b1;
        next_state = WAIT_CHECK_FINAL;
      end
      STORE_OUTPUTS: begin
        Z0_w = 1'b1;
        Z1_w = 1'b1;
        Z2_w = 1'b1;
        Z3_w = 1'b1;
        next_state = UPDATE_INPUTS;

      end
      UPDATE_INPUTS: begin
        R0_input = Z0_output;
        R1_input = Z1_output;
        R2_input = Z2_output;
        R3_input = Z3_output;
        R0_w = 1'b1;
        R1_w = 1'b1;
        R2_w = 1'b1;
        R3_w = 1'b1;
        next_state = WAIT_CHECK_FINAL;
        if (enc_dec == 1'b1) begin
          down_counter = 1'b1;
          if (counter_out == 8'h0) begin
            next_state = OUTPUT_DEC;
          end

        end else begin
          up_counter = 1'b1;
          if (counter_out == 8'hF) begin
            next_state = OUTPUT_ENC;
          end
        end
      end
      WAIT_CHECK_FINAL: begin
        next_state = STORE_OUTPUTS;


      end

      OUTPUT_ENC: begin
        R0_input = R2 ^ K4;
        R1_input = R3 ^ K5;
        R2_input = R0 ^ K6;
        R3_input = R1 ^ K7;
        R0_w = 1'b1;
        R1_w = 1'b1;
        R2_w = 1'b1;
        R3_w = 1'b1;
        next_state = END;
      end

      OUTPUT_DEC: begin
        R0_input = R2 ^ K0;
        R1_input = R3 ^ K1;
        R2_input = R0 ^ K2;
        R3_input = R1 ^ K3;
        R0_w = 1'b1;
        R1_w = 1'b1;
        R2_w = 1'b1;
        R3_w = 1'b1;
        next_state = END;
      end

      END: begin
        end_signal = 1'b1;
      end

    endcase
  end


  always_ff @(posedge clk) begin
    if (rst) begin
      current_state <= IDLE;
    end else begin
      current_state <= next_state;
    end
  end


endmodule : twofish


module twofish_stage (
    input enc_dec,  //enc = 0, dec = 1
    input [7:0] i,
    input [31:0] Me[1:0],
    input [31:0] Mo[1:0],
    input [31:0] Si[1:0],
    input [31:0] R0,
    input [31:0] R1,
    input [31:0] R2,
    input [31:0] R3,
    output [31:0] Z0,
    output [31:0] Z1,
    output [31:0] Z2,
    output [31:0] Z3
);

  logic [31:0] F0;
  logic [31:0] F1;

  f_function f_i (
      .R0(R0),
      .R1(R1),
      .Me(Me),
      .Mo(Mo),
      .Si(Si),
      .i (i),
      .F0(F0),
      .F1(F1)
  );

  wire  [31:0] Z0_input_0;
  logic [31:0] Z0_output_0;

  mux2 #(
      .N(32)
  ) m0 (
      .a  (R2),
      .b  ({R2[30:0], R2[31]}),
      .sel(enc_dec),
      .c  (Z0_input_0)
  );

  //assign Z0_input_0 = enc_dec == 1'b1 ? {R2[30:0],R2[31]} : R2;
  galois_adder #(
      .N(32)
  ) a1 (
      .a(F0),
      .b(Z0_input_0),
      .s(Z0_output_0)
  );



  logic [31:0] Z1_input_0;
  logic [31:0] Z1_output_0;
  //assign Z1_input_0 = enc_dec == 1'b1 ? R3 : {R3[30:0],R3[31]};

  mux2 #(
      .N(32)
  ) m1 (
      .a  ({R3[30:0], R3[31]}),
      .b  (R3),
      .sel(enc_dec),
      .c  (Z1_input_0)
  );
  galois_adder #(
      .N(32)
  ) a2 (
      .a(F1),
      .b(Z1_input_0),
      .s(Z1_output_0)
  );






  mux2 #(
      .N(32)
  ) m3 (
      .a  ({Z0_output_0[0], Z0_output_0[31:1]}),
      .b  (Z0_output_0),
      .sel(enc_dec),
      .c  (Z0)
  );


  mux2 #(
      .N(32)
  ) m4 (
      .a  (Z1_output_0),
      .b  ({Z1_output_0[0], Z1_output_0[31:1]}),
      .sel(enc_dec),
      .c  (Z1)
  );


  //assign Z0 = enc_dec == 1'b1 ? Z0_output_0 : {Z0_output_0[0],Z0_output_0[31:1]} ;
  //assign Z1 = enc_dec == 1'b1 ? {Z1_output_0[0],Z1_output_0[31:1]} : Z1_output_0;
  assign Z2 = R0;
  assign Z3 = R1;



endmodule : twofish_stage






module key_schedule (
    input  [127:0] key,
    output [ 31:0] Me [1:0],
    output [ 31:0] Mo [1:0],
    output [ 31:0] Si [1:0]
);

  assign Me[0] = key[31:0];
  assign Me[1] = key[95:64];
  assign Mo[0] = key[63:32];
  assign Mo[1] = key[127:96];

  logic [7:0] m_0[7:0];
  assign m_0[0] = key[7:0];
  assign m_0[1] = key[15:8];
  assign m_0[2] = key[23:16];
  assign m_0[3] = key[31:24];
  assign m_0[4] = key[39:32];
  assign m_0[5] = key[47:40];
  assign m_0[6] = key[55:48];
  assign m_0[7] = key[63:56];
  logic [7:0] m_1[7:0];
  assign m_1[0] = key[71:64];
  assign m_1[1] = key[79:72];
  assign m_1[2] = key[87:80];
  assign m_1[3] = key[95:88];
  assign m_1[4] = key[103:96];
  assign m_1[5] = key[111:104];
  assign m_1[6] = key[119:112];
  assign m_1[7] = key[127:120];
  logic [7:0] RS[31:0];
  assign RS[0]  = 8'h01;
  assign RS[1]  = 8'hA4;
  assign RS[2]  = 8'h55;
  assign RS[3]  = 8'h87;
  assign RS[4]  = 8'h5A;
  assign RS[5]  = 8'h58;
  assign RS[6]  = 8'hDB;
  assign RS[7]  = 8'h9E;
  assign RS[8]  = 8'hA4;
  assign RS[9]  = 8'h56;
  assign RS[10] = 8'h82;
  assign RS[11] = 8'hF3;
  assign RS[12] = 8'h1E;
  assign RS[13] = 8'hC6;
  assign RS[14] = 8'h68;
  assign RS[15] = 8'hE5;
  assign RS[16] = 8'h02;
  assign RS[17] = 8'hA1;
  assign RS[18] = 8'hFC;
  assign RS[19] = 8'hC1;
  assign RS[20] = 8'h47;
  assign RS[21] = 8'hAE;
  assign RS[22] = 8'h3D;
  assign RS[23] = 8'h19;
  assign RS[24] = 8'hA4;
  assign RS[25] = 8'h55;
  assign RS[26] = 8'h87;
  assign RS[27] = 8'h5A;
  assign RS[28] = 8'h58;
  assign RS[29] = 8'hDB;
  assign RS[30] = 8'h9E;
  assign RS[31] = 8'h03;

  wire [7:0] s0[3:0];
  wire [7:0] s1[3:0];


  matrix_multiplication #(
      .N(8),
      .COL_A(8),
      .ROW_A(4),
      .COL_B(1)
  ) m0 (
      .a(RS),
      .b(m_0),
      .p(9'h14D),
      .s(s0)
  );
  matrix_multiplication #(
      .N(8),
      .COL_A(8),
      .ROW_A(4),
      .COL_B(1)
  ) m1 (
      .a(RS),
      .b(m_1),
      .p(9'h14D),
      .s(s1)
  );

  assign Si[1] = {s0[3], s0[2], s0[1], s0[0]};
  assign Si[0] = {s1[3], s1[2], s1[1], s1[0]};


endmodule : key_schedule


module f_function (
    input  [31:0] R0,
    input  [31:0] R1,
    input  [31:0] Me[1:0],
    input  [31:0] Mo[1:0],
    input  [31:0] Si[1:0],
    input  [ 7:0] i,
    output [31:0] F0,
    output [31:0] F1
);

  logic [31:0] T0;
  logic [31:0] T1;

  logic [31:0] K0;
  logic [31:0] K1;

  logic [31:0] sum_output_0;
  logic [31:0] sum_output_1;

  h_function g0 (
      .X(R0),
      .L(Si),
      .Z(T0)
  );

  h_function g1 (
      .X({R1[23:0], R1[31:24]}),
      .L(Si),
      .Z(T1)
  );

  expanded_key_words k_0 (
      .i  (i + 4),
      .Me (Me),
      .Mo (Mo),
      .K_0(K0),
      .K_1(K1)
  );

  adder #(
      .N(32)
  ) at00 (
      .a(T0),
      .b(T1),
      .s(sum_output_0),
      .c()
  );

  adder #(
      .N(32)
  ) at01 (
      .a(sum_output_0),
      .b(K0),
      .s(F0),
      .c()
  );

  adder #(
      .N(32)
  ) at10 (
      .a(T0),
      .b(T1 << 1),
      .s(sum_output_1),
      .c()
  );

  adder #(
      .N(32)
  ) at11 (
      .a(sum_output_1),
      .b(K1),
      .s(F1),
      .c()
  );


endmodule : f_function



module expanded_key_words (
    input  [ 7:0] i,
    input  [31:0] Me [1:0],
    input  [31:0] Mo [1:0],
    output [31:0] K_0,
    output [31:0] K_1
);

  logic [31:0] p;
  assign p = 32'h01010101;

  logic [31:0] A;
  logic [31:0] B;

  logic [31:0] h1_input;
  logic [31:0] h1_output;

  assign B = {h1_output[23:0], h1_output[31:24]};

  logic [31:0] adder_out;
  logic [31:0] m;  //2*i*p
  assign m = {i, i, i, i};


  h_function h0 (
      .X(m << 1),
      .L(Me),
      .Z(A)
  );

  adder #(
      .N(32)
  ) ai (
      .a(m << 1),
      .b(p),
      .s(h1_input),
      .c()
  );

  h_function h1 (
      .X(h1_input),
      .L(Mo),
      .Z(h1_output)
  );

  adder #(
      .N(32)
  ) a0 (
      .a(A),
      .b(B),
      .s(K_0),
      .c()
  );

  adder #(
      .N(32)
  ) a1 (
      .a(A),
      .b(B << 1),
      .s(adder_out),
      .c()
  );

  assign K_1 = {adder_out[22:0], adder_out[31:23]};

endmodule : expanded_key_words



module h_function (
    input  [31:0] X,
    input  [31:0] L[1:0],
    output [31:0] Z
);

  logic [7:0] MDS[15:0];
  assign MDS[0]  = 8'h01;
  assign MDS[1]  = 8'hEF;
  assign MDS[2]  = 8'h5B;
  assign MDS[3]  = 8'h5B;
  assign MDS[4]  = 8'h5B;
  assign MDS[5]  = 8'hEF;
  assign MDS[6]  = 8'hEF;
  assign MDS[7]  = 8'h01;
  assign MDS[8]  = 8'hEF;
  assign MDS[9]  = 8'h5B;
  assign MDS[10] = 8'h01;
  assign MDS[11] = 8'hEF;
  assign MDS[12] = 8'hEF;
  assign MDS[13] = 8'h01;
  assign MDS[14] = 8'hEF;
  assign MDS[15] = 8'h5B;


  logic [31:0] X1;
  logic [31:0] X2;
  logic [31:0] Q0;
  logic [31:0] Q1;
  wire  [ 7:0] Q2 [3:0];
  wire  [ 7:0] y  [3:0];



  /*step1*/
  q0_transform i00 (
      .x (X[7:0]),
      .q0(Q0[7:0])
  );
  q1_transform i01 (
      .x (X[15:8]),
      .q1(Q0[15:8])
  );
  q0_transform i02 (
      .x (X[23:16]),
      .q0(Q0[23:16])
  );
  q1_transform i03 (
      .x (X[31:24]),
      .q1(Q0[31:24])
  );
  galois_adder #(
      .N(32)
  ) a0 (
      .a(L[1]),
      .b(Q0),
      .s(X1)
  );
  /*step2*/
  q0_transform i10 (
      .x (X1[7:0]),
      .q0(Q1[7:0])
  );
  q0_transform i11 (
      .x (X1[15:8]),
      .q0(Q1[15:8])
  );
  q1_transform i12 (
      .x (X1[23:16]),
      .q1(Q1[23:16])
  );
  q1_transform i13 (
      .x (X1[31:24]),
      .q1(Q1[31:24])
  );
  galois_adder #(
      .N(32)
  ) a1 (
      .a(L[0]),
      .b(Q1),
      .s(X2)
  );
  /*step3*/
  q1_transform i20 (
      .x (X2[7:0]),
      .q1(Q2[0])
  );
  q0_transform i21 (
      .x (X2[15:8]),
      .q0(Q2[1])
  );
  q1_transform i22 (
      .x (X2[23:16]),
      .q1(Q2[2])
  );
  q0_transform i23 (
      .x (X2[31:24]),
      .q0(Q2[3])
  );
  /*Matrix*/

  matrix_multiplication #(
      .N(8),
      .COL_A(4),
      .ROW_A(4),
      .COL_B(1)
  ) m0 (
      .a(MDS),
      .b(Q2),
      .p(9'h169),
      .s(y)
  );

  assign Z = {y[3], y[2], y[1], y[0]};


endmodule : h_function


module q0_transform (
    input  [7:0] x,
    output [7:0] q0
);

  logic [3:0] t0[15:0];
  logic [3:0] t1[15:0];
  logic [3:0] t2[15:0];
  logic [3:0] t3[15:0];

  assign t0[0] = 4'h8;
  assign t0[1] = 4'h1;
  assign t0[2] = 4'h7;
  assign t0[3] = 4'hD;
  assign t0[4] = 4'h6;
  assign t0[5] = 4'hF;
  assign t0[6] = 4'h3;
  assign t0[7] = 4'h2;
  assign t0[8] = 4'h0;
  assign t0[9] = 4'hB;
  assign t0[10] = 4'h5;
  assign t0[11] = 4'h9;
  assign t0[12] = 4'hE;
  assign t0[13] = 4'hC;
  assign t0[14] = 4'hA;
  assign t0[15] = 4'h4;

  assign t1[0] = 4'hE;
  assign t1[1] = 4'hC;
  assign t1[2] = 4'hB;
  assign t1[3] = 4'h8;
  assign t1[4] = 4'h1;
  assign t1[5] = 4'h2;
  assign t1[6] = 4'h3;
  assign t1[7] = 4'h5;
  assign t1[8] = 4'hF;
  assign t1[9] = 4'h4;
  assign t1[10] = 4'hA;
  assign t1[11] = 4'h6;
  assign t1[12] = 4'h7;
  assign t1[13] = 4'h0;
  assign t1[14] = 4'h9;
  assign t1[15] = 4'hD;

  assign t2[0] = 4'hB;
  assign t2[1] = 4'hA;
  assign t2[2] = 4'h5;
  assign t2[3] = 4'hE;
  assign t2[4] = 4'h6;
  assign t2[5] = 4'hD;
  assign t2[6] = 4'h9;
  assign t2[7] = 4'h0;
  assign t2[8] = 4'hC;
  assign t2[9] = 4'h8;
  assign t2[10] = 4'hF;
  assign t2[11] = 4'h3;
  assign t2[12] = 4'h2;
  assign t2[13] = 4'h4;
  assign t2[14] = 4'h7;
  assign t2[15] = 4'h1;

  assign t3[0] = 4'hD;
  assign t3[1] = 4'h7;
  assign t3[2] = 4'hF;
  assign t3[3] = 4'h4;
  assign t3[4] = 4'h1;
  assign t3[5] = 4'h2;
  assign t3[6] = 4'h6;
  assign t3[7] = 4'hE;
  assign t3[8] = 4'h9;
  assign t3[9] = 4'hB;
  assign t3[10] = 4'h3;
  assign t3[11] = 4'h0;
  assign t3[12] = 4'h8;
  assign t3[13] = 4'h5;
  assign t3[14] = 4'hC;
  assign t3[15] = 4'hA;

  /*
    logic [3:0] a0,b0,a1,b1,a2,b2,a3,b3,a4,b4;
    logic [7:0] y;


    always_comb begin
        a0 = x[7:4];
        b0 = x[3:0];
        a1 = a0 ^ b0;
        b1 = a0 ^ {b0[0],b0[3:1]} ^ {a0[0],3'b000};
        a2 = t0[a1];
        b2 = t1[b1];
        a3 = a2 ^ b2;
        b3 = a2 ^ {b2[0],b2[3:1]} ^ {a2[0],3'b000};
        a4 = t2[a3];
        b4 = t3[b3];
        y = {b4,a4};
    end
    assign q0 = y;
    */

  assign q0 = {
    t3[(t0[(x[7:4] ^ x[3:0])] ^ {t1[(x[7:4] ^ {x[0],x[3:1]} ^ {x[4],3'b000})][0],t1[(x[7:4] ^ {x[0],x[3:1]} ^ {x[4],3'b000})][3:1]} ^ {t0[(x[7:4] ^ x[3:0])][0],3'b000})],
    t2[(t0[(x[7:4]^x[3:0])]^t1[(x[7:4]^{x[0], x[3:1]}^{x[4], 3'b000})])]
  };



endmodule : q0_transform


module q1_transform (
    input  [7:0] x,
    output [7:0] q1
);
  logic [3:0] t0[15:0];
  logic [3:0] t1[15:0];
  logic [3:0] t2[15:0];
  logic [3:0] t3[15:0];

  assign t0[0] = 4'h2;
  assign t0[1] = 4'h8;
  assign t0[2] = 4'hB;
  assign t0[3] = 4'hD;
  assign t0[4] = 4'hF;
  assign t0[5] = 4'h7;
  assign t0[6] = 4'h6;
  assign t0[7] = 4'hE;
  assign t0[8] = 4'h3;
  assign t0[9] = 4'h1;
  assign t0[10] = 4'h9;
  assign t0[11] = 4'h4;
  assign t0[12] = 4'h0;
  assign t0[13] = 4'hA;
  assign t0[14] = 4'hC;
  assign t0[15] = 4'h5;

  assign t1[0] = 4'h1;
  assign t1[1] = 4'hE;
  assign t1[2] = 4'h2;
  assign t1[3] = 4'hB;
  assign t1[4] = 4'h4;
  assign t1[5] = 4'hC;
  assign t1[6] = 4'h3;
  assign t1[7] = 4'h7;
  assign t1[8] = 4'h6;
  assign t1[9] = 4'hD;
  assign t1[10] = 4'hA;
  assign t1[11] = 4'h5;
  assign t1[12] = 4'hF;
  assign t1[13] = 4'h9;
  assign t1[14] = 4'h0;
  assign t1[15] = 4'h8;

  assign t2[0] = 4'h4;
  assign t2[1] = 4'hC;
  assign t2[2] = 4'h7;
  assign t2[3] = 4'h5;
  assign t2[4] = 4'h1;
  assign t2[5] = 4'h6;
  assign t2[6] = 4'h9;
  assign t2[7] = 4'hA;
  assign t2[8] = 4'h0;
  assign t2[9] = 4'hE;
  assign t2[10] = 4'hD;
  assign t2[11] = 4'h8;
  assign t2[12] = 4'h2;
  assign t2[13] = 4'hB;
  assign t2[14] = 4'h3;
  assign t2[15] = 4'hF;

  assign t3[0] = 4'hB;
  assign t3[1] = 4'h9;
  assign t3[2] = 4'h5;
  assign t3[3] = 4'h1;
  assign t3[4] = 4'hC;
  assign t3[5] = 4'h3;
  assign t3[6] = 4'hD;
  assign t3[7] = 4'hE;
  assign t3[8] = 4'h6;
  assign t3[9] = 4'h4;
  assign t3[10] = 4'h7;
  assign t3[11] = 4'hF;
  assign t3[12] = 4'h2;
  assign t3[13] = 4'h0;
  assign t3[14] = 4'h8;
  assign t3[15] = 4'hA;

  /*
    logic [3:0] a0,b0,a1,b1,a2,b2,a3,b3,a4,b4;
    logic [7:0] y;


    always_comb begin
        a0 = x[7:4];
        b0 = x[3:0];
        a1 = a0 ^ b0;
        b1 = a0 ^ {b0[0],b0[3:1]} ^ {a0[0],3'b000};
        a2 = t0[a1];
        b2 = t1[b1];
        a3 = a2 ^ b2;
        b3 = a2 ^ {b2[0],b2[3:1]} ^ {a2[0],3'b000};
        a4 = t2[a3];
        b4 = t3[b3];
        y = {b4,a4};
    end
    assign q1 = y;
    */

  assign q1 = {
    t3[(t0[(x[7:4] ^ x[3:0])] ^ {t1[(x[7:4] ^ {x[0],x[3:1]} ^ {x[4],3'b000})][0],t1[(x[7:4] ^ {x[0],x[3:1]} ^ {x[4],3'b000})][3:1]} ^ {t0[(x[7:4] ^ x[3:0])][0],3'b000})],
    t2[(t0[(x[7:4]^x[3:0])]^t1[(x[7:4]^{x[0], x[3:1]}^{x[4], 3'b000})])]
  };




endmodule : q1_transform
