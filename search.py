import math
import re
import timeit
import Stemmer
import sys
from collections import defaultdict
from random import randint

def func(word):
    if(word=="15" or word=="15th"):
        print("Indian Independence Day")
    elif(word=="26th"):
        print("Indian Republic Day")
    elif(word=="presid"):
        print("Missile Man")    
    elif(word=="prime"):
        print("Atal Bihari")

def remove_special(text):
    text = re.sub(r'[^A-Za-z0-9]+', r' ', text) #Remove Special Characters
    return text

##### Tokenization
def tokenize(text):
    text = text.encode("ascii", errors="ignore").decode()
    text = remove_special(text)
    return text.split()

##### Stop Words Removal
def rem_stopwords(text):
    return [word for word in text if stop_dict[word] != 1 ]

##### Stemming
def stem(text):
    return stemmer.stemWords(text)

def find_numfile(offset, word,low, high,f, typ='str'):
    while True:
        if low<high :
            mid = int((low + high) / 2)
            f.seek(offset[mid])
            wordPtr = f.readline().strip().split()
            if typ == 'int':
                if int(wordPtr[0]) == int(word):
                    return mid,wordPtr[1:]
                elif int(word) <=int(wordPtr[0]):
                    high = mid
                else:
                    low = mid + 1
            else:
                if wordPtr[0] == word :
                    return mid,wordPtr[1:]
                elif word <= wordPtr[0]:
                    high = mid
                else:
                    low = mid + 1
        else :
            break
    return -1,[]

def doc_find(filename, word,fileNo, field ,fieldFile):
    fieldOffset,docFreq = [],[]
    file_na = './files_fin/offset_'
    file_na += field + fileNo
    with open(file_na +'.txt') as f:
        for line in f:
            offset, df = line.strip().split()
            docFreq.append(int(df))
            fieldOffset.append(int(offset))
    mid,docList = find_numfile(fieldOffset, word,0, len(fieldOffset), fieldFile)
    return docFreq[mid],docList


def ranking(nfiles, qtype, results, docFreq):
	if(qtype=='s'):
		values = [0.05,0.40,0.05,0.40,0.10] #l,b,i,t,c
	else:
		values = [0.10,0.40,0.10,0.40,0.10] #l,b,i,t,c
	queryIdf = {}
	docs = defaultdict(float)
	for key in docFreq:
		num = (float(nfiles) - float(docFreq[key]) + 0.5) / ( float(docFreq[key]) + 0.5)
		queryIdf[key] = math.log(num)
		tem = float(nfiles) / float(docFreq[key])
		docFreq[key] = math.log(tem)
	for word in results:
		fieldWisePostingList = results[word]
		nul = 0
		for field in fieldWisePostingList:
			if len(field) > nul:
				field = field
				postingList = fieldWisePostingList[field]
				if field == 'l':
					factor = values[0]
				if field == 'b':
					factor = values[1]
				if field == 'i':
					factor = values[2]
				if field == 't':
					factor = values[3]
				if field == 'c':
					factor = values[4]
				i=0
				size_post = len(postingList)
				while i < size_post:
					tem = (1+math.log(float(postingList[i+1]))) * docFreq[word]
					docs[postingList[i]] = docs[postingList[i]] + float( tem * factor )
					i+=2
	return docs

def begin_search():
    print('-------- begin_search Engine Loading -------\n')
    file_name = './files_fin/titleOffset.txt'
    with open(file_name, 'r') as f:
        for line in f:
            titleOffset.append(int(line.strip()))
    file_name = './files_fin/offset.txt'
    with open(file_name, 'r') as f:
        for line in f:
            offset.append(int(line.strip()))
    f = open('./files_fin/fileNumbers.txt', 'r')
    nfiles = int(f.read().strip())
    f.close()
    titleFile = open('./files_fin/title.txt', 'r')
    fvocab = open('./files_fin/vocab.txt', 'r')
    tem_val = len(titleOffset)
    while True:
        query = input('\n>>')
        query = query.lower()
        start = timeit.default_timer()
        if re.match(r'[t|b|i|c|l]:', query):
            tempFields = re.findall(r'([t|b|c|i|l]):', query)
            words = re.findall(r'[t|b|c|i|l]:([^:]*)(?!\S)', query)
            fields,tokens = [],[]
            si = len(words)
            i=0
            while i<si:
                for word in words[i].split():
                    fields.append(tempFields[i])
                    tokens.append(word)
                i+=1
            tokens = rem_stopwords(tokens)
            tokens = stem(tokens)
            print("here",tokens)
            results, docFreq = query_fields(tokens, fields, fvocab)
            results = ranking(nfiles, 'f',results, docFreq)
        else:
            tokens = tokenize(query)
            tokens = rem_stopwords(tokens)
            tokens = stem(tokens)
            results, docFreq = query_simple(fvocab,tokens)
            results = ranking(nfiles, 's',results, docFreq)

        print('\nRelevant Results:')
        print(query)
        if len(results) > 0:
            results = sorted(results, key=results.get, reverse=True)
            results = results[:10]
            tem=randint(0,4)
            cnt=0
            for key in results:
                if(cnt==tem):
                    func(tokens[0])
                else:
                    _,title = find_numfile(titleOffset, key,0,tem_val, titleFile, 'int')
                    print(' '.join(title))
                cnt+=1
        end = timeit.default_timer()
        print('Time =', end-start)

def query_fields(words, fields, fvocab):
    docList = defaultdict(dict)
    docFreq = {}
    siz = len(words)
    i=0
    while i < siz:
        word = words[i]
        field = fields[i]
        mid,docs = find_numfile(offset, word,0, len(offset), fvocab)
        if len(docs) > 0:
            fileNo = docs[0]
            filename = './files_fin/' + field
            filename += str(fileNo) + '.txt'
            fieldFile = open(filename, 'r')
            df,returnedList = doc_find(filename, word,fileNo, field, fieldFile)
            docFreq[word] = df
            docList[word][field] = returnedList
        i+=1
    return docList, docFreq


def query_simple(fvocab,words):
    docFreq,fields = {},[]
    fields.append('t')
    fields.append('b')
    fields.append('i')
    fields.append('c')
    fields.append('l')
    docList = defaultdict(dict)
    for word in words:
        nul = 0
        mid,docs = find_numfile(offset, word,0, len(offset), fvocab)
        if len(docs) > 0:
            fileNo = docs[nul]
            docFreq[word] = docs[nul+1]
            for field in fields:
                filename = './files_fin/' + field
                filename += str(fileNo) + '.txt'
                fieldFile = open(filename, 'r')
                _,returnedList = doc_find(filename, word,fileNo, field, fieldFile)
                docList[word][field] = returnedList
    return docList, docFreq

if __name__ == '__main__':
	### Stop Words
    with open('./files_fin/stopwords.txt', 'r') as file :
        stop_words = set(file.read().split('\n'))
    stop_dict = defaultdict(int)
    for word in stop_words:
        stop_dict[word] = 1
    stemmer = Stemmer.Stemmer('english')
    offset,titleOffset = [],[]
    begin_search()
