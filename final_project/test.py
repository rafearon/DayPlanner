# self.unaryFactors[var] = {val:self.unaryFactors[var][val] * \
#                 factor[val] for val in factor}

values = {}
values[0] = 0
values[1] = 1
values[2] = 2
values[3] = 3
values[4] = 4

print values
print "HEHE"
new_vals = {val:values[val] * \
	 1 for val in values}
print new_vals
