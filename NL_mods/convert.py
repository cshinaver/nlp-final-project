#convert json to the text we need
import json
import string
from collections import defaultdict

def create_punctuation_table():
	table = defaultdict(str)
	for pun in string.punctuation:
		table[ord(pun)] = ' ' #replace with a space
	return table

def convert(infile, outfile):
	f = open(outfile, 'w')
	space_conv = ''
	for p in string.punctuation: #create for table
		space_conv += ' '
	json_data = open(infile).read()
	data = json.loads(json_data)
	table = create_punctuation_table()
	for item in data:
		string_to_write = item['category'] + ' ' + str(item['description']).lower().translate(str.maketrans(string.punctuation,space_conv)) + '\n'
		f.write(string_to_write)
	#create new doc of filtered text to run the train on


if __name__ == '__main__':
	convert('newtrain','newtrainfile')