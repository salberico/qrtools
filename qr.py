# -​- coding: utf-8 -​-
from data import *

def cap_exp(e):
	return e%256 + e//256

class Matrix(object):
	""" QR Matrix """
	
	def __init__(self, version):
		self.size = version * 4 + 17
		
		# Char map for OFF(0) and ON(1)
		self.char = ['  ', '██']
	
		# Finder pattern for QR code
		self.finder = [[1,1,1,1,1,1,1], \
		               [1,0,0,0,0,0,1], \
		               [1,0,1,1,1,0,1], \
		               [1,0,1,1,1,0,1], \
		               [1,0,1,1,1,0,1], \
		               [1,0,0,0,0,0,1], \
		               [1,1,1,1,1,1,1]]
		
		self.matrix = self.gen_matrix(self.size)
		self.add_finders()
		
	def __getitem__(self, index):
		return self.matrix[index[0]][index[1]]
		
	def __setitem__(self, index, val):
		self.matrix[index[0]][index[1]] = val
	
	def blit(self, pattern, loc):
		''' 
		Made for overlaying QR Patterns matrices on the base matrix
		but can also be used for putting general matrices starting at the supplied location.
		'''
		for y in range(len(pattern)):
			for x in range(len(pattern[y])):
				# Override the matrix at needed locations offset by supplied
				self.matrix[loc[0]+x][loc[1]+y] = pattern[y][x]
			
			
	def add_finders(self):
		# Add finder pattern to top-left, bottom-left and top-right
		self.blit(self.finder, (0,0))
		self.blit(self.finder, (0,self.size-7))
		self.blit(self.finder, (self.size-7,0))
	
	def flatten(self):
		flat = []
		# Return flat representation of matrix
		
		for x in range(self.size):
			for y in range(self.size):
				flat.append(self)
				
		return flat
	
	def reverse(self):
		''' Swap zeros and ones in matrix '''
		
		for x in range(self.size):
			for y in range(self.size):
				# Flip 0 and 1 
				self.matrix[x][y] ^= 1
	
	def gen_matrix(self, size):
		# Get side length of final QR code
		# BASIC INDEX FORMAT
		# [(0,0)][][][(3,0)][]
		# [     ][][][     ][]
		# [(0,2)][][][     ][]
		
		matrix = []
		
		# Initialize matrix with zeros for (size, size)
		for c in range(size):
			column = []
			for y in range(size):
				column.append(0)
				
			# Add the current column to the final matrix
			matrix.append(column)
			
		return matrix
		
	def to_string(self):
		outstring = ''
		
		# Representation is [column][row] so need to index by index then array
		for y in range(self.size):
			for x in range(self.size):
				# Add corrosponding character for matrix value
				outstring += self.char[self.matrix[x][y]]
				
			# Start new line as y increments
			outstring += '\n'
			
		return outstring
	
	def __str__(self):
		return self.to_string()
		
	
class QR(object):
	def __init__(self, data):
		self.version = 5
		self.correction = 'Q'
		# 0001:Numeric, 0010:Alphanumeric
		mode = '0010' 
		
		# Gen blank matrix with patterns in place
		self.matrix = Matrix(self.version)
		
		# QR Specification
		               # 236      ,  17
		self.padders = ['11101100', '00010001']
		self.encoded = self.encode(data, mode)
		self.groups = self.add_encoded_error(self.segment_codewords(self.encoded))
		self.interweave(self.groups)
	
	def segment_codewords(self, data):
		group_data = error_chart[self.version][self.correction][2:]
		# Get group data from dic, which is :
		#[#blocks in g1, #codewords in each block in g1, #blocks in g2, #codewords in each block in g2]
		
		# Initialize empty groups and start index at 0
		# blocks are filled in sequential order
		groups = []
		index = 0
		
		# Iterate through groups if there is 2 otherwise just do the one
		for group in [0,2] if group_data[2] != 0 else [0]:
			blocks = []
			
			# Add for each block
			for b in range(group_data[group]):
				block = []
				
				# Iterate index through codeword in each group
				for code in range(group_data[group+1]):
					# Add bytes(codeword) to current block
					block.append(data[index:index+8])
					index += 8
					
				# Add block to blocks in group
				blocks.append([block])
				
			# Add blocks to group
			groups.append(blocks)
					
		return groups
	
	def get_bytestring(self, mode, charcount, edata):
		prestring = mode + charcount + edata
		
		# Get maximum size bit size based on QR version and error correction bytes
		size = error_chart[self.version][self.correction][0] * 8
		
		# Add terminator zeros up to a max of 4
		prestring += '0' * min(4, size - len(prestring))
		
		# Make bit count multiple of 8 by padding zeros 
		prestring += '0' * (-len(prestring) % 8)
		
		# Finally add QR specification padders to make the string the desired size 
		for pad in range((size - len(prestring))//8):
			prestring += self.padders[pad%2]
		
		return prestring
		
	def encode(self, data, mode):
		data = str(data)
		
		# 0001 Numeric
		if mode == '0001':
			# Get standardized count string length
			if self.version <= 9:
				count = 10
			elif self.version <= 26:
				count = 12
			else:
				count = 14
				
			# Slice digits into groups of 3 then convert resulting number to binary
			sliced = [data[i:i+3] for i in range(0, len(data), 3)]
			edata = ''.join([bin(int(slice))[2:] for slice in sliced])
			
		# 0010 Alphanumeric
		if mode == '0010':
			# Get standardized count string length
			if self.version <= 9:
				count = 9
			elif self.version <= 26:
				count = 11
			else:
				count = 13
				
			# Split into groups of 2
			sliced = [data[i:i+2] for i in range(0, len(data), 2)]
			
			# For each slice find alphanumeric code multiply first char by 45 then add index of second code
			# if there is only one character just use that code
			# then convert to binary with either 11 or 6 bits for 2 or 1 character then join
			edata = ''.join([format(alphanumeric[slice[0]] * 45 + alphanumeric[slice[1]], '011b') if len(slice) == 2 
				else format(alphanumeric[slice], '06b') for slice in sliced])
			
		# General
		bin_length = bin(len(data))[2:]
		count_string = '0'*(count - len(bin_length)) + bin_length
		
		return self.get_bytestring(mode, count_string, edata)
		
	def divide_polynomial(self, m, g):
		mult = exponent[m[0]]
		#(m)essage, (g)enerator
	
		# Temp generator to be used 
		temp_g = [val for val in g]
	
		xor_last = m
		for _ in range(len(m)):
			xor = []
		
			for i in range(len(temp_g)):
				# Multiply term from original generator and convert to integer notation
				temp_g[i] = integer[cap_exp(g[i] + mult)]

			for i in range(1, max(len(xor_last), len(g))):
				# Bitwise XOR on each coeffitient
				xor.append((xor_last[i] if i < len(xor_last) else 0) ^ (temp_g[i] if i < len(temp_g) else 0))
		
			# Update multiplier alpha
			mult = exponent[xor[0]]
			xor_last = xor
		
		return xor
		
	def add_encoded_error(self, groups):
		# g is the group index
		for g in range(len(groups)):
			# b is the block index in the current group
			for b in range(len(groups[g])):
				# Convert codewords intro integers for coeffitients of message polynomial
				message_coeffitients = [int(code, 2) for code in groups[g][b][0]]
				# Retrieve the appropriate generator polynomial to be used for error correction 
				generator = alpha_coefficients[error_chart[self.version][self.correction][1]]
				
				# Divide the two as shown in divide_polynomial() to retrieve the error polynomial coeffitients
				error_coeffitients = self.divide_polynomial(message_coeffitients, generator)
				
				# Append the error_coeffitients converted into bytes onto the current block
				groups[g][b].append([format(c, '08b') for c in error_coeffitients])
				
				# Add empty string at the end to prevent index error without if statment
				groups[g][b][0].append('')
				
		return groups

	def interweave(self, groups):
		outweave = ''
		
		########### MESSAGE WEAVING ##############
		#
		# Total count of data increments to weave for
		data_count = max(error_chart[self.version][self.correction][3], error_chart[self.version][self.correction][5])
		
		# Total count of blocks in both groups
		block_count = [error_chart[self.version][self.correction][2], error_chart[self.version][self.correction][4]]
		
		# Add byte to outweave by index of codeword first for each block
		for d_index in range(data_count):
		
			# Unified loop so iterate through the sum of the length of both blocks
			for b_index in range(sum(block_count)):
			
				# Should move to 1 when first group is done, 0 otherwise
				outweave += groups[b_index // block_count[0]][b_index % block_count[0]][0][d_index]
		#
		##########################################
		
		####### ERROR CORRECTION WEAVING #########
		#
		# Error corretion is appended to existing message weave
		
		# Length of data index is consitent to the generator steps for all blocks
		for d_index in range(error_chart[self.version][self.correction][1]):
			
			# Unified loop so iterate through the sum of the length of both blocks
			for b_index in range(sum(block_count)):
			
				# Should move to 1 when first group is done, 0 otherwise
				print(int(groups[b_index // block_count[0]][b_index % block_count[0]][1][d_index], 2))
				outweave += groups[b_index // block_count[0]][b_index % block_count[0]][1][d_index]
		#
		##########################################
		
		# Add required remainder bits prior to returning
		outweave += '0' * remainder[self.version]
		return outweave

class QRtext(object):
	def __init__(self, length=21, lines=[]):
		self.lines = lines
		self.length = length
		for i in range(len(self.lines)):
			self.lines[i] = self.lines[i][:self.length*2]
		
	def __str__(self):
		return '\n'.join(self.lines)
		
	def invert(self):
		for i in range(len(self.lines)):
			new = ''
			for char in self.lines[i]:
				new += '█' if char == ' ' else ' '
			self.lines[i] = new
			
	def pad(self, padding):
		for i in range(len(self.lines)):
			self.lines[i] = '  ' * padding + self.lines[i] + '  ' * padding
		linepad = [' ' * (self.length*2 + padding*4) for _ in range(padding)]
		self.lines = linepad + self.lines + linepad
		self.length += padding * 2
		
if __name__ == "__main__":
	t = QR('TEST123')
	print(t.groups)