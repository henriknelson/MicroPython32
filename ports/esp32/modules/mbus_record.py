class MBusValueRecord:

	STORAGE_MASK = 0x40		# 0100 0000
	FUNCTION_MASK = 0x30   		# 0011 0000
	EXTENSION_MASK = 0x80		# 1000 0000
	DIFE_STORAGE_MASK = 0x0F	# 0000 1111
	DIFE_TARIFF_MASK = 0x30		# 0011 0000
	DIFE_SUBUNIT_MASK = 0x40	# 0100 0000
	DATA_TYPE_MASK = 0x0F		# 0000 1111

	def __init__(self,dib,vib,data):
		self.dib = dib
		self.vib = vib
		self.data = data
		ret_bytes = []
		ret_bytes.extend(self.dib)
		ret_bytes.extend(self.vib)
		ret_bytes.extend(self.data)
		self._bytes = bytearray(ret_bytes)

	def get_bytes(self):
                return self._bytes

	def set_storage(self,storage):
		if (storage < 0) or (storage > 2**41):
			raise Exception("Erroneous storage number")
		#storage_array = ''.join(reversed('{0:b}'.format(storage)))
		index = 0
		self.dib[0] = self.dib[-0] | (self.STORAGE_MASK) & ((storage & 0x1) << 6)
		storage = storage >> 1
		while storage > 0:
			self.dib[index-1] = self.dib[-index-1] | self.EXTENSION_MASK
			if(index == len(self.dib)):
				self.dib.append(0)
			self.dib[index] = self.dib[index] | (storage & self.DIFE_STORAGE_MASK)
			storage = storage >> 4
			index = index + 1
		self.dib[-1] = self.dib[-1] ^ (not self.EXTENSION_MASK)

	def get_storage(self):
		result = 0
		bit_index = 1
		for index,dife in enumerate(self.dib):
			if index == 0:
				result |= (dife & self.STORAGE_MASK) >> 6
			else:
				result |= (dife & self.DIFE_STORAGE_MASK) << bit_index
				bit_index = bit_index + 4
		return result

	def set_tariff(self,tariff):
		if (tariff < 0) or (tariff > 2**20):
			raise Exception("Erroneous tariff number")
		index = 1
		while tariff > 0:
			self.dib[index-1] = self.dib[index-1] | self.EXTENSION_MASK
			if(index == len(self.dib)):
				self.dib.append(0)
			self.dib[index] = self.dib[index] | (self.DIFE_TARIFF_MASK & ((tariff & 0x03) << 4))
			tariff = tariff >> 2
			index = index + 1
		self.dib[-1] = self.dib[-1] ^ (not self.EXTENSION_MASK)

	def get_tariff(self):
		result = 0
		bit_index = 0
		for index,dife in enumerate(self.dib[1:]):
			result |= ((dife & self.DIFE_TARIFF_MASK) >> 4) << bit_index
			bit_index = bit_index + 2
		return result

	def set_function(self,function):
		if function < 0 or function > 3:
			raise Exception("Erroneous function")
		self.dib[0] |= (self.FUNCTION_MASK & function << 4)

	def get_function(self):
		return (self.dib[0] & self.FUNCTION_MASK) >> 4

	def set_subunit(self,subunit):
		if subunit < 0 or subunit > 2**10:
			raise Exception("Erroneous subunit")
		index = 1

		while subunit > 0:
			self.dib[index-1] = self.dib[index-1] | self.EXTENSION_MASK
			if(index == len(self.dib)):
				self.dib.append(0)
			self.dib[index] = self.dib[index] | (self.DIFE_SUBUNIT_MASK & ((subunit & 0x01) << 6))
			subunit = subunit >> 1
			index = index + 1
		self.dib[-1] = self.dib[-1] ^ (not self.EXTENSION_MASK)

	def get_subunit(self):
		result = 0
		bit_index = 0
		for index,dife in enumerate(self.dib[1:]):
			result |= ((dife & self.DIFE_SUBUNIT_MASK) >> 6) << bit_index
			bit_index = bit_index + 1
		return result

	def set_data_field(self,data_field):
		if data_field < 0 or data_field > 15:
			raise Exception("Erroneous data type")
		self.dib[0] |= (self.DATA_TYPE_MASK & data_field)

	def get_data_field(self):
		return (self.dib[0] & self.DATA_TYPE_MASK)

#rec = MBusValueRecord()
#rec.set_subunit(0x3FF)

#rec.set_storage(2045)
#print(rec.get_storage())
#rec.set_function(3)
#print(rec.get_function())
#rec.set_tariff(1000)
#print(rec.get_tariff())
#for elem in rec.dib:
#	print('{0:08b}'.format(elem))
#print(rec.get_subunit())
#print(rec.get_bytes())
