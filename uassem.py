'''
Created on Dec 5, 2013

@author: zhangtong
'''
## Microassembler for 32-bit microcontrolled CPU.

import sys
import re

# Table of control ROM values for the
# known control=value pairs
Cvalue= {
    'aluop=add' :      0,
    'aluop=sub' :      1,
    'aluop=mul' :      2,
    'aluop=div' :      3,
    'aluop=rem' :      4,
    'aluop=and' :      5,
    'aluop=or'  :      6,
    'aluop=xor' :      7,
    'aluop=nand':      8,
    'aluop=nor' :      9,
    'aluop=not' :      10,
    'aluop=lsl' :      11,
    'aluop=lsr' :      12,
    'aluop=asr' :      13,
    'aluop=rol' :      14,
    'aluop=ror' :      15,
    'op2sel=treg' :    0 << 4,
    'op2sel=immed':    1 << 4,
    'op2sel=0' :       2 << 4,
    'op2sel=1' :       3 << 4,
    'datawrite=0' :    0 << 6,
    'datawrite=1' :    1 << 6,
    'addrsel=pc'  :    0 << 7,
    'addrsel=immed' :  1 << 7,
    'addrsel=aluout':  2 << 7,
    'addrsel=sreg'  :   3 << 7,
    'pcsel=pc' :        0 << 9,
    'pcsel=immed' :     1 << 9,
    'pcsel=pcimmed' :   2 << 9,
    'pcsel=sreg' :      3 << 9,
    'pcload=0' :        0 << 11,
    'pcload=1' :        1 << 11,
    'dwrite=0' :        0 << 12,
    'dwrite=1' :        1 << 12,
    'irload=0' :        0 << 13,
    'irload=1' :        1 << 13,
    'imload=0' :        0 << 14,
    'imload=1' :        1 << 14,
    'regsrc=databus' :  0 << 15,
    'regsrc=immed' :    1 << 15,
    'regsrc=aluout' :   2 << 15,
    'regsrc=sreg' :     3 << 15,
    'cond=z' :          0 << 17,
    'cond=norz' :       1 << 17,
    'cond=n' :          2 << 17,
    'cond=c' :          3 << 17,
    'indexsel=0' :      0 << 19,
    'indexsel=opcode' : 1 << 19,
    'datasel=pc' :      0 << 20,
    'datasel=dreg' :    1 << 20,
    'datasel=treg' :    2 << 20,
    'datasel=aluout' :  3 << 20,
    'swrite=0' :        0 << 22,
    'swrite=1' :        1 << 22,
}

#write the jump address to CROM and JROM
def jumpend():
    CROM[this]= cvalue
    JROM[this]= [tjump,fjump]
    Origline[this]= origline

# Condition values
Cond={
      'z':0,
      'norz':1,
      'n':2,
      'c':3
      }

# Label to address lookup table
Label={}

# The control and jump ROMs
CROM={}
JROM={}
Origline={}

# Next address to use
nextaddr=0
# Offset to opcode 0
offset=0


# Open up the input
f=open(sys.argv[1],'r')
#print sys.argv[0]
#f=open('basic_microcode','r')

for line in f:
    #print line
    #ignore comment and blank lines
    if line[0]=='#' or line.strip()=='':
        continue
    this=nextaddr
    label=''
    origline=line
    tmp=''
    
    mat=re.match(r'(.*):\s+(.*)',line)
    
    # Deal with labels
    if mat:
        label=mat.group(1)
        tmp=mat.group(2)
        # Set this address up if its an opcode number
        if re.match(r'^\d+$',label):
            this=int(label)+offset
        if label in Label:
            print 'Error: label $label already defined\n'
            break
        # Save the label
        Label[label]=this
        
    #if not re.match(r'^\d+$',line):
    if not re.match(r'^\d+.*',line):
        nextaddr=nextaddr+1
    if tmp=='':
        tmp=line
    
    # Split the line up into control/val pairs and any jump
    lis=tmp.split(',',1)
    cpairs=lis[0]
    if len(lis)==1:
        jump=''
    else:
        jump=lis[1]
        jump=jump.strip()
    
    # Deal with the control lines, build up the 32-bit control value
    cvalue=0
    cpairs=cpairs.strip()
    for cpair in re.split('\s+',cpairs):
        if cpair not in Cvalue:
            print 'Error: unrecognised  control/val $cpair\n'
            continue
        cvalue=cvalue+Cvalue[cpair]
    
    # Deal with jump    
    tjump=nextaddr
    fjump=nextaddr
    
    if jump:
        # End of the fetch logic, so we now know the opcode offset
        if jump=='opcode_jump':
            offset=nextaddr
            nextaddr=offset+128
            cvalue=cvalue+Cvalue["indexsel=opcode"]
            jumpend()
        # Explicit goto
        elif re.match(r'goto\s+(\S+)',jump):
            tmp=re.match(r'goto\s+(\S+)',jump)
            tjump=tmp.group(1)
            fjump=tmp.group(1)
            jumpend()
        # Full if decision
        elif re.match(r'if\s+(\S+)\s+then\s(\S+)\s+else\s+(\S+)',jump):
            tmp=re.match(r'if\s+(\S+)\s+then\s(\S+)\s+else\s+(\S+)',jump)
            cond=tmp.group(1)
            tjump=tmp.group(2)
            fjump=tmp.group(3)
            if cond not in Cond:
                print 'Error: unknown condition cond\n'
                exit
            condtmp="cond=%s" % cond
            cvalue=cvalue+Cvalue[condtmp]
            jumpend()
        # Partial if decision
        elif re.match(r'if\s+(\S+)\s+then\s(\S+)',jump):
            tmp=re.match(r'if\s+(\S+)\s+then\s(\S+)',jump)
            cond=tmp.group(1)
            jump=tmp.group(2)
            if cond not in Cond:
                print 'Error: unknown condition cond\n'
                exit
            condtmp="cond=%s" % cond
            cvalue=cvalue+Cvalue[condtmp]
            jumpend()
        # Unrecognised jump command
        else:
            print 'Error: unrecognised jump command %s\n' % jump
    else:
        jumpend()

f.close()

# Patch in the labels in the @JROM
for i in range(255):
    if i in JROM:
        tjump=JROM[i][0]
        fjump=JROM[i][1]
    else: 
        tjump=0
        fjump=0
    
    if not re.match(r'^\d+$',str(tjump)):
        if tjump not in Label:
            print 'unkown label %s\n' % tjump
            exit
        tjump=Label[tjump]
    if not re.match(r'^\d+$',str(fjump)):
        if fjump not in Label:
            print 'unkown label %s\n' % fjump
            exit
        fjump=Label[fjump]
    
    JROM[i]=(tjump<<8)+fjump

# Print out the ROMs    
for i in range(255):
    if i in JROM and i in CROM and i in Origline:
        print "%02x: %08x %04x\t# %s\n" % (i, CROM[i], JROM[i], Origline[i])

# Write out the ROMs
rw=open('ucontrol.rom','w')
rw.write("v2.0 raw\n")

for i in range(256):
    if i in CROM:
        rw.write("%x " % CROM[i])
    else:
        rw.write("%x " % 0)
    if i%8==7:
        rw.write("\n")
rw.close()
    
rw=open('udecision.rom','w')
rw.write("v2.0 raw\n")
for i in range(256):
    if i in JROM:
        rw.write("%x " % JROM[i])
    else:
        rw.write("%x " % 0)
    if i%8==7:
        rw.write("\n")
rw.close()

exit(0)
        
        
