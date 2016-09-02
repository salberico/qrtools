# -​- coding: utf-8 -​-
from data import error_chart

class QR(object):
	def __init__(self, data):
		self.version = 1
		self.correction = 'L'
		self.mode = '0001'
		
		# QR Specification
		               # 236      ,  17
		self.padders = ['11101100', '00010001']

	def get_bits(self, version, correction):
		#http://www.thonky.com/qr-code-tutorial/error-correction-table
		return error_chart[version][correction][0]
		
	def get_block_data(self, version, correction):
		#http://www.thonky.com/qr-code-tutorial/error-correction-table
		return error_chart[version][correction][1:]
		
	def get_bytestring(self, mode, charcount, edata):
		prestring = mode + charcount + edata
		
		# Get maximum size based on QR version and error correction
		size = self.get_bits(self.version, self.correction)
		
		# Add terminator zeros up to a max of 4
		prestring += '0' * min(4, size - len(prestring))
		
		# Make bit count multiple of 8 by padding zeros 
		prestring += '0' * (-len(prestring) % 8)
		
		# Finally add QR specification padders to make the string the desired size 
		for pad in range((size - len(prestring))//8):
			prestring += padders[pad%2]
		
		return prestring
		
	def encode(self, data, version, correction, mode):
		data = str(data)
		
		# 0001 Numeric
		if mode == '0001':
			bin_length = bin(len(data))[2:]
			if version <= 9:
				ccount = '0'*(10 - len(bin_length)) + bin_length
			# TEMP
			else:
				ccount = '0'*(10 - len(bin_length)) + bin_length
			sliced = [data[i:i+3] for i in range(0, len(data), 3)]
			edata = ''.join([bin(int(slice))[2:] for slice in sliced])
		
		# General
		return self.get_bytestring(mode, ccount, edata)
		
	def encode_error(self):
		# Next step
		pass
		

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