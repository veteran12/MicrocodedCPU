# This program uses the instructions defined in the
# basic_microcode file. It adds the numbers from 100
# down to 1 and stores the result in memory location 256.
# (c) GPL3 Warren Toomey, 2012
#
main:	li	r0, 0		# r0 is the running sum
	li	r1, 100		# r1 is the counter
	li	r2, 1		# Used to decrement r1
loop:	add	r0, r0, r1	# r0= r0 + r1
	sub	r1, r1, r2	# r1--
	jnez	r1, loop	# loop if r1 != 0
	sw	r0, 256		# Save the result	
