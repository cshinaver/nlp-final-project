import numpy
import autograd
from collections import defaultdict

speaker_freq = defaultdict(int)
speaker_prob = defaultdict(int)
speaker_word_counts = defaultdict(lambda: defaultdict(int))
speaker_word_counts = defaultdict(lambda: defaultdict(int))
speaker_word_prob = defaultdict(lambda: defaultdict(int))
correct_speaker_list = []
guess_speaker_list = []

def read_data(doc):
	f = open(doc,'r')
	for line in f:
		speaker = line.split(' ')[0]
		speaker_freq[speaker] = speaker_freq[speaker] + 1
		for word in line.split(' ')[1:]:
			speaker_word_counts[speaker][word] = speaker_word_counts[speaker][word] + 1

#prob fcns
#p(k)
def prob_speaker(k):
	total_documents = 0
	for speaker in speaker_freq:
		total_documents += speaker_freq[speaker]
	return speaker_freq[k]/total_documents

def create_speaker_prob():
	for speaker in speaker_freq:
		speaker_prob[speaker] = speaker_freq[speaker]/sum(speaker_freq.values())

#p(k,w)
def prob_speaker_word(k,w,d=0,smoothing=False):
	total_words = 0
	v = len(speaker_word_counts[k]) + 1
	for word in speaker_word_counts[k]:
		total_words += speaker_word_counts[k][word]
	if smoothing:
		total_words += (v*d)
	return (speaker_word_counts[k][w] + d) / total_words

def create_prob_dictionary(d=1):
	all_word_types = 0
	for speaker in speaker_word_counts:
		all_word_types += len(speaker_word_counts[speaker].values())
	for speaker in speaker_word_counts:
		v = all_word_types + 1
		total_words = sum(speaker_word_counts[speaker].values()) + (v*d)
		for word in speaker_word_counts[speaker]:
			speaker_word_prob[speaker][word] = (speaker_word_counts[speaker][word] + d)/ total_words
		speaker_word_prob[speaker]['<unk>'] = 1 / total_words
#training P(k|d)
def read_speakers(doc):
	f = open(doc,'r')
	for line in f:
		speaker = line.split(' ')[0]
		correct_speaker_list.append(speaker)
def compare(a,b):
	total = len(a)
	count = 0
	if len(a) == len(b):
		for i in range(len(a)):
			if a[i] == b[i]:
			 	count += 1
	return count/total

def testing_results_first_line():
	speaker_line_prob = defaultdict(int)
	speaker_exp_prob = defaultdict(int)
	speaker_doc_prob = defaultdict(int)
	f = open('hw1-data/dev','r')
	for line in f.readlines()[:1]:
		for speaker in speaker_freq:
			speaker_line_prob[speaker] = numpy.log(speaker_prob[speaker])
			for word in line.split(' ')[1:]:
				if word not in speaker_word_counts[speaker]:
					speaker_line_prob[speaker] += numpy.log(speaker_word_prob[speaker]['<unk>'])
				else:
					speaker_line_prob[speaker] += numpy.log(speaker_word_prob[speaker][word])
		maxvalue = max(speaker_line_prob.values())
		for speaker in speaker_line_prob:
			speaker_line_prob[speaker] = speaker_line_prob[speaker] - maxvalue #normalize
			speaker_exp_prob[speaker] = numpy.exp(speaker_line_prob[speaker])
		total_exp = sum(speaker_exp_prob.values())
		for speaker in speaker_line_prob:
			speaker_doc_prob[speaker] = speaker_exp_prob[speaker] / total_exp
		print(speaker_doc_prob)

def testing(file):
	speaker_line_prob = defaultdict(int)
	speaker_exp_prob = defaultdict(int)
	speaker_doc_prob = defaultdict(int)
	f = open(file,'r')
	for line in f.readlines():
		for speaker in speaker_freq:
			speaker_line_prob[speaker] = numpy.log(speaker_prob[speaker])
			for word in line.split(' ')[1:]:
				if word not in speaker_word_counts[speaker]:
					speaker_line_prob[speaker] += numpy.log(speaker_word_prob[speaker]['<unk>'])
				else:
					speaker_line_prob[speaker] += numpy.log(speaker_word_prob[speaker][word])
		maxvalue = max(speaker_line_prob.values())
		for speaker in speaker_line_prob:
			speaker_line_prob[speaker] = speaker_line_prob[speaker] - maxvalue #normalize
			speaker_exp_prob[speaker] = numpy.exp(speaker_line_prob[speaker])
		total_exp = sum(speaker_exp_prob.values())
		for speaker in speaker_line_prob:
			speaker_doc_prob[speaker] = speaker_exp_prob[speaker] / total_exp
		#print(speaker_doc_prob)
		guess_speaker_list.append(max( 
			speaker_line_prob.keys(),
			key=(lambda key: speaker_line_prob[key])
		))
	return compare(correct_speaker_list,guess_speaker_list)
		
#results 

read_data('newtrainfile')
read_speakers('newtestfile') #read correct
create_prob_dictionary(0.5) #0.5 smoothing
create_speaker_prob()
accuracy = testing('newtestfile')

print(accuracy)