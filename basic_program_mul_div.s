# This program uses the instructions defined in the
# basic_microcode file. It multiply the numbers n and the half of it
# down to 1 and stores the result in memory location 256.
#
main:	li	r0, 1		# r0 is the running sum
	li	r1, 100		# r1 is the counter
	li	r2, 2		# Used to divide r1 by 2
loop:	mul	r0, r0, r1	# r0= r0 + r1
	div	r1, r1, r2	# r1/2
	jnez	r1, loop	# loop if r1 != 0
	sw	r0, 256		# Save the result	
