#   read in a text file of assembling language and then parse it to machine code
import re
import sys

#   Table of opcode names, the values and their arguments
#   A hash table implemented with dictionary
Opcode = {
        'add':  [ 0, 'dst'  ],
        'sub':  [ 1, 'dst'  ],
        'mul':  [ 2, 'dst'  ],
        'div':  [ 3, 'dst'  ],
        'rem':  [ 4, 'dst'  ],
        'and':  [ 5, 'dst'  ],
        'or':   [ 6, 'dst'  ],
        'xor':  [ 7, 'dst'  ],
        'nand': [ 8, 'dst'  ],
        'nor':  [ 9, 'dst'  ],
        'not':  [ 10, 'ds'  ],
        'lsl':  [ 11, 'dst' ],
        'lsr':  [ 12, 'dst' ],
        'asr':  [ 13, 'dst' ],
        'rol':  [ 14, 'dst' ],
        'ror':  [ 15, 'dst' ],
        'addi': [ 16, 'dsi' ],
        'subi': [ 17, 'dsi' ],
        'muli': [ 18, 'dsi' ],
        'divi': [ 19, 'dsi' ],
        'remi': [ 20, 'dsi' ],
        'andi': [ 21, 'dsi' ],
        'ori':  [ 22, 'dsi' ],
        'xori': [ 23, 'dsi' ],
        'nandi':[ 24, 'dsi' ],
        'nori': [ 25, 'dsi' ],
        'lsli': [ 26, 'dsi' ],
        'lsri': [ 27, 'dsi' ],
        'asri': [ 28, 'dsi' ],
        'roli': [ 29, 'dsi' ],
        'rori': [ 30, 'dsi' ],
        'addc': [ 31, 'dstI'],
        'subc': [ 32, 'dstI'],
        'jeq':  [ 33, 'sti' ],
        'jne':  [ 34, 'sti' ],
        'jgt':  [ 35, 'sti' ],
        'jle':  [ 36, 'sti' ],
        'jlt':  [ 37, 'sti' ],
        'jge':  [ 38, 'sti' ],
        'jeqz': [ 39, 'si'  ],
        'jnez': [ 40, 'si'  ],
        'jgtz': [ 41, 'si'  ],
        'jlez': [ 42, 'si'  ],
        'jltz': [ 43, 'si'  ],
        'jgez': [ 44, 'si'  ],
        'jmp':  [ 45, 'i'   ],
        'beq':  [ 46, 'stI' ],
        'bne':  [ 47, 'stI' ],
        'bgt':  [ 48, 'stI' ],
        'ble':  [ 49, 'stI' ],
        'blt':  [ 50, 'stI' ],
        'bge':  [ 51, 'stI' ],
        'beqz': [ 52, 'sI'  ],
        'bnez': [ 53, 'sI'  ],
        'bgtz': [ 54, 'sI'  ],
        'blez': [ 55, 'sI'  ],
        'bltz': [ 56, 'sI'  ],
        'bgez': [ 57, 'sI'  ],
        'br':   [ 58, 'I'   ],
        'jsr':  [ 59, 'i',        '$Mcode[$PC]+= 7<<3; # sp' ], 
        'rts':  [ 60, '',         '$Mcode[$PC]+= 7<<3; # sp' ],
        'inc':  [ 61, 's'   ],
        'dec':  [ 62, 's'   ],
        'li':   [ 63, 'di'  ],
        'lw':   [ 64, 'di'  ],
        'sw':   [ 65, 'di'  ],
        'lwi':  [ 66, 'dX'  ],
        'swi':  [ 67, 'dX'  ],
        'push': [ 68, 'd',        '$Mcode[$PC]+= 7<<3; # sp' ],
        'pop':  [ 69, 'd',        '$Mcode[$PC]+= 7<<3; # sp' ],
        'move': [ 70, 'ds'  ],
        'clr':  [ 71, 's'   ],
        'neg':  [ 72, 's'   ],
        'lwri': [ 73, 'dS' ],
        'swri': [ 74, 'dS' ],
}

Label = {}  # declare Hash of label -> PC values as a dictionary
Mcode = {}  # declare Machine code for each PC value as the Key of this dictionary
Origline = {}   # declare Original line as an dictionary
Ltype = {}  # Type of label? undef is not, 1 is abs, 2 is rel
PC=0        # Current program counter


def pre_process(contents):
    # declare global varibles
    global PC
    global Label
    global Mcode
    global Origline
    global Ltype
    global Opcode
    
    lines = contents.split("\n") # return a list of strings, splited by "\n" in previous file
    p = re.compile('(\s*#.*)')  # regular expression object for finding comments
    labelRegEx = re.compile('(.*):\s+(.*)') # regular expression object for finding labels
    ldt = re.compile('^\D*') # regular expression for finding 'leading text'
    hexa = re.compile('^0x') # regular expression for judjing 'hexadecimal'
    
    for line in lines:
        #print line
        line = line.strip() # take off spaces around a line
        matches = p.search(line)
        
        if matches:
            newline = line[0:matches.start()] # the new line is original line without comments
        else:
            newline = line
            
        if len(newline)>0:
            hadImmed=False
            Origline[PC] = newline
            
            matches = labelRegEx.search(newline)
            print 'PC:', PC, ' ', newline
            
            if matches:
                # print 'has a label', matches.group(1), matches.group(2)
                # the "matches" get whatever strings matches regular expressions, so "group(1) is the first 'label block'"
                # group(1) is the first '(.*)' of '(.*):\s+(.*)'
                Label[matches.group(1)] = PC
                # if it is the label line, the newline should be trimed off the label -> then it can be splitted to op and arg
                newline = matches.group(2)
                
            # currently the 'newline' is in the form of 'li        r1, 100'
            # split the line into opcode and arguments, putting into a list of two elements (opcode and arguments)
            opcode_arg_list = re.split('\s+', newline, 1)
            print 'the opcode and arg list is: ', opcode_arg_list
            # check if the opcode is in the Opcode dictionary
            check_opcode = opcode_arg_list[0]
            try:
                check_opcode in Opcode
            except ValueError:
                print "The opcode is invalid"
            
            opcode = opcode_arg_list[0]
            print 'the opcode is:', opcode
    
            # now the 'opcode_arg_list' is in the form of '['li', 'r1, 100']'
            # Fill in the opcode of the machine instruction
            print "---------the type of opcode is-------------:", type(opcode)
            Mcode[PC] = Opcode[opcode][0] <<16  # shift 3 regs
                
            # Run any code associated with this instruction [i think it makes no sense to run 'eval' here]
            # eval($Opcode{$opcode}->[2]) if (defined($Opcode{$opcode}->[2]));
            
            # Get the arguments as a list
            arg_string = opcode_arg_list[1]
            arg_list = re.split(',\s*', arg_string)
            print 'the argument list is:', arg_list
            
            # Check if the number of arguments is correct
            num_args = len(arg_list)
            try:
                num_args == len(Opcode[opcode][1])
            except ValueError:
                print "The number of arguments is invalid"
            
            # Process the arguments
            args = list(Opcode[opcode][1])
            for arg_type in args:
                arg = arg_list.pop(0)
                
                # D-reg:
                if arg_type is 'd':
                    # Lose leading text
                    matches = ldt.search(arg)
                    if matches:
                        arg = arg[matches.end():] # from the end of leading text to the end of original string
                        arg = int(arg)            # convert the string to int for later calculating
                    Mcode[PC] += (arg & 31)
                # D-reg, S-reg is D-reg
                elif arg_type is 'D':
                    # Lose leading text
                    matches = ldt.search(arg)
                    if matches:
                        arg = arg[matches.end():] # from the end of leading text to the end of original string
                        arg = int(arg)            # convert the string to int for later calculating
                    Mcode[PC] += (arg & 31)
                    Mcode[PC] += (arg & 31) << 5
                # S-reg
                elif arg_type is 's':
                    # Lose leading text
                    matches = ldt.search(arg)
                    if matches:
                        arg = arg[matches.end():] # from the end of leading text to the end of original string
                        arg = int(arg)            # convert the string to int for later calculating
                    Mcode[PC] += (arg & 31)<<5
                # T-reg
                elif arg_type is 't':
                    # Lose leading text
                    matches = ldt.search(arg)
                    if matches:
                        arg = arg[matches.end():] # from the end of leading text to the end of original string
                        arg = int(arg)            # convert the string to int for later calculating
                    Mcode[PC] += (arg & 31) << 10
                # Absolute immediate
                elif arg_type is 'i':
                    # Deal with hex values - judge if the value arg is a hex by looking if it is start with '0x'
                    matches = hexa.search(arg)
                    if matches:
                        arg = int(arg, 16) # convert the hex to int
                    # Simply bump up the PC and save the value for now
                    PC += 1
                    Mcode[PC] = arg
                    Ltype[PC] = 1
                # Relative immediate
                elif arg_type is 'I':
                    # Deal with hex values - judge if the value arg is a hex by looking if it is start with '0x'
                    matches = hexa.search(arg)
                    if matches:
                        arg = int(arg, 16) # convert the hex to int
                    # Simply bump up the PC and save the value for now
                    PC += 1
                    Mcode[PC] = arg
                    Ltype[PC] = 2
                    
                # Indexed addressing. We want to allow these types of argument:
                # (Rn) where immed=0, immed(Rn), Rn(immed) and immed can be
                # numeric or a label and Rn is the s-reg
                elif arg_type is 'X':
                    # regex for finding arguments as below:
                    regnum = None
                    immed = None
                    match_arg_1 = re.compile('(\S*)\([Rr](\d+)\)')
                    match_arg_2 = re.compile('[Rr](\d+)\((\S+)\)')
                    matches_1 = match_arg_1.search(arg)
                    matches_2 = match_arg_2.search(arg)
                    if matches_1:
                        immed = matches_1.group(1)
                        regnum = matches_1.group(2)
                    elif matches_2:
                        immed = matches_2.group(2)
                        regnum = matches_2.group(1)
                        
                    # check if regnum has been changed
                    try:
                        regnum is not None
                    except ValueError:
                        print "Bad indexed addressing"
                    # question here, how could immed be ""?
                    if immed == "":
                        immed = 0
                    
                    match_immed = hexa.search(immed)
                    if match_immed:
                        immed = int(immed, 16)
                        
                    Mcode[PC] += (regnum & 7) << 3
                    PC += 1
                    Mcode[PC] = immed
                    Ltype[PC] = 1
                    
                # Register indexed addressing. We want to see Rs(Rt) only.
                elif arg_type is 'S':
                    sreg = None
                    treg = None
                    match_arg = re.compile('[Rr](\d+)\([Rr](\d+)\)')
                    matches = match_arg.search(arg)
                    if matches:
                        sreg = matches.group(1)
                        treg = matches.group(2)
                    else:
                        sys.exit('Bad indexed arg')
                    Mcode[PC] += (sreg & 7) << 3
                    Mcode[PC] += (treg & 7) << 6
            # at the end of each loop for parsing the lines, add 1 to PC value
            PC += 1        
            
    
# Time to backpatch the label values in the machine code
# Currently, this piece of code is included in process() function
    for i in range(0, len(Mcode)):
        if i not in Ltype:
            continue
        # Get the label's value, lookup if not numeric:
        # optional leading - sign, followed by 1 or more digits
        label = Mcode[i]
        label_match = re.compile('^-?\d+$')
        matches = label_match.search(label)
        if not matches:
            try:
                label in Label
            except ValueError:
                print "Undefined label:", label
            label = Label[label]
        # Calculate absolute value if it is relative
        if Ltype[i] == 2:
            label = label - i
        # Save the final value:
        label = int(label)
        Mcode[i] = label & 0xffffffff
        
# print machine code in hex for now
    for i in range(0, len(Mcode)):
        print "%04x: %08x \t%s" %(i, Mcode[i], Origline[i] if i in Origline else "")
    
# create and write to a file
    print "Writing to '.ram' file..."
    file = open('basic_program.ram', 'w+') # 'w+', cover the original file
    
    file.write('v2.0 raw\n')
    for i in range(0, len(Mcode)):
            # assign the value of Mcode to 'M_code' which is to be output
        M_code = Mcode[i]
        # the number of bits in the format may be needed to be modified:
        print 'the type of this Mcode is:', type(M_code)
        print 'the Mcode is:', Mcode
        print 'i == ', i
        # use buffer here to convert M_code into hexadecimal number
        #if (str)(M_Code) == 'ffff':
        #    'fffffffff'
        if M_code < 0:
            buf = "ffff%x" %(M_code)
        else:    
            buf = "%x" %(M_code)
        
        # Mcode = format(Mcode, '04x')
        file.write(buf+' ')
        if i%8 == 7:
            file.write('\n')
        
    file.write('\n')
    file.close()
    print "Writing to file complished."
    
#   input file from command line
#   open and read the input file which is the assembling language
IN = sys.argv[1]
f = open(IN, "rb")
#f=open('basic_program.s','rb')
contents = f.read()
        
        
def main():
    print '\nrun pre_processing\n'
    print 'pre_processed result is as below:\n'
    pre_process(contents)
    print 'pre_processing finished'

if __name__ == '__main__':
    main()