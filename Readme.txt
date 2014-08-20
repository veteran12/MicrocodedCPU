1:We write the assembler and micro assembler for the 32-bit microcoded CPU in python.
2:The massem.py is the assembler.
3:The uassem.py is the micro assembler.
4:We implement the add/sub/mul/div instruction.
5:In order to test the add/sub/mul/div instruction,we write two high level assembly language programs
basic_program_add_sub.s and basic_program_mul_div.s and a microcode assembly language program basic_microcode.
6:The function of basic_program_add_sub.s is add from 100 down to 1,the result is 5050 and stored at address 256 in the ram.
7:The function of basic_program_mul_div.s is just like the function written in C.The result is 27000000 and stored at address
256 in the ram.

int res=1;
int i=100;
while(i!=0){
    res=res*i;
    i=i/2;
}

8:32bit-MicrocodedCPU.circ is the 32bit CPU designed using logisim.
9:How to use the two assembler
type the command below:
1)python massem.py basic_program_add_sub.s
    output basic_program.ram
2)python uassem.py basic_microcode
    output ucontrol.rom and udecision.rom