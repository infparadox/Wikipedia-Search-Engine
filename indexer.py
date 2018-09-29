from collections import defaultdict
import timeit
import xml.sax
from unidecode import unidecode
import sys
import re
import Stemmer
import heapq
import operator
import os
import pdb
import threading
from tqdm import tqdm

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
    #return [stemmer.stem(word) for word in text]
##### Process Text using regex
def processText(text, title):
    #### References , Links, Categories below references & info,body, tilte above references.
    st1 = "== references == "
    st2 = "==references=="
    text = text.lower() #Case Folding
    temp = text.split(st1)
    x=1
    if len(temp) == x:
        temp = text.split('st2')
    if len(temp) == x: # If empty then initialize with empty lists
        links = []
        categories = []
    else: 
        categories = process_categories(temp[1])
        links = process_links(temp[1])
    body = process_body(temp[0])
    title= title.lower()
    title = process_title(title)
    info = process_info(temp[0])
    return title, body, info, categories, links

def process_title(text):
    data = tokenize(text)
    data = rem_stopwords(data)
    data = stem(data)
    return data

def process_body(text):
    data = re.sub(r'\{\{.*\}\}', r' ', text)
    data = tokenize(data)
    data = rem_stopwords(data)
    data = stem(data)
    return data

def process_info(text):
    data = text.split('\n')
    fl = -1
    info = []
    st="}}"
    for line in data:
        if re.match(r'\{\{infobox', line):
            info.append(re.sub(r'\{\{infobox(.*)', r'\1', line))
            fl = 0
        elif fl == 0:
            if line == st:
                fl = -1
                continue
            info.append(line)
    data = tokenize(' '.join(info))
    data = rem_stopwords(data)
    data = stem(data)
    return data

def process_categories(text):
    data = text.split('\n')
    categories = []
    for line in data:
        if re.match(r'\[\[category', line):
            categories.append(re.sub(r'\[\[category:(.*)\]\]', r'\1', line))
    data = tokenize(' '.join(categories))
    data = rem_stopwords(data)
    data = stem(data)
    return data

def process_links(text):
    data = text.split('\n')
    links = []
    for line in data:
        if re.match(r'\*[\ ]*\[', line):
            links.append(line)
    data = tokenize(' '.join(links))
    data = rem_stopwords(data)
    data = stem(data)
    return data

def Indexer(title, body, info, categories, links):
    global p_cnt
    global PostList
    global docID
    global f_cnt
    global offset
    ID = p_cnt
    words={}
    d={}
    for word in links:
        if(d.get(word)==None):
            d[word]=1
        else:
            d[word]+=1
        if(words.get(word)==None):
            words[word]=1
        else:
            words[word]+=1
    links = d
    d = {} # Local Vocabulary
    for word in title:
        if(d.get(word)==None):
            d[word]=1
        else:
            d[word]+=1
        if(words.get(word)==None):
            words[word]=1
        else:
            words[word]+=1
    title = d
    d = {}
    for word in info:
        if(d.get(word)==None):
            d[word]=1
        else:
            d[word]+=1
        if(words.get(word)==None):
            words[word]=1
        else:
            words[word]+=1
    info = d
    d = {}
    for word in body:
        if(d.get(word)==None):
            d[word]=1
        else:
            d[word]+=1
        if(words.get(word)==None):
            words[word]=1
        else:
            words[word]+=1
    body = d
    d = {}
    for word in categories:
        if(d.get(word)==None):
            d[word]=1
        else:
            d[word]+=1
        if(words.get(word)==None):
            words[word]=1
        else:
            words[word]+=1
    categories = d 
    for word,key in words.items():
    	string ='d'+(str(ID))
    	if(title.get(word)):
    		string += 't' + str(title[word])
    	if(body.get(word)):
    		string += 'b' + str(body[word])
    	if(info.get(word)):
    		string += 'i' + str(info[word])
    	if(categories.get(word)):
    		string += 'c' + str(categories[word])
    	if(links.get(word)):
    		string += 'l' + str(links[word])
    	PostList[word].append(string)
    p_cnt += 1
    tem_var = p_cnt%20000
    if tem_var == 0 :
    	offset = writeinfile(PostList, docID, f_cnt , offset)
    	PostList = defaultdict(list)
    	docID = {}
    	f_cnt = f_cnt + 1

def writeinfile(PostList, docID, f_cnt , offset):	
    d_offset = []    
    data = []
    p_offset = offset
    for key in sorted(docID):
        temp = str(key) + ' ' + docID[key].strip()
        size_1=len(temp)
        if(size_1>0):
            p_offset = 1 + p_offset + size_1
        else:
            p_offset = 1 + p_offset
        data.append(temp)
        d_offset.append(str(p_offset))
    f_name = './files/titleOffset.txt'
    with open(f_name, 'a') as f:
        f.write('\n'.join(d_offset))
        f.write('\n')
    f_name = './files/title.txt'
    with open(f_name, 'a') as f:
        f.write('\n'.join(data))
        f.write('\n')
    data = []
    for key in sorted(PostList.keys()):
        postings = PostList[key]
        string = key + ' '
        string = string + ' '.join(postings)
        data.append(string)
    file_name = './files/index' 
    f_name = file_name + str(f_cnt) + '.txt'
    with open(f_name, 'w') as f:
        f.write('\n'.join(data))
    return p_offset

class writeThread(threading.Thread):
    def __init__(self, field, data, offset, count):
        threading.Thread.__init__(self)
        self.field = field
        self.offset = offset
        self.data = data
        self.count = count
    def run(self):
        st_fl=str(self.count)
        file_name = './files/' 
        f_name = file_name + self.field + st_fl + '.txt'
        with open(f_name, 'w') as f:
            f.write('\n'.join(self.data))
        file_name = './files/offset_'     
        f_name = file_name + self.field + st_fl + '.txt'
        with open(f_name, 'w') as f:
            f.write('\n'.join(self.offset))

def final_write(data, finalCount, offsetSize):
    offset = []
    distinctWords = []
    title = defaultdict(dict)
    link = defaultdict(dict)
    info = defaultdict(dict)
    category = defaultdict(dict)
    body = defaultdict(dict)
    for key in tqdm(sorted(data.keys())):
        temp = []
        docs = data[key]
        i=0
        si=len(docs)
        while(i<si):
            posting = docs[i]
            temp = re.sub(r'.*c([0-9]*).*', r'\1', posting)
            docID = re.sub(r'.*d([0-9]*).*', r'\1', posting)
            siz=len(temp)
            if siz>0 and posting != temp:
                category[key][docID] = float(temp)
            temp = re.sub(r'.*i([0-9]*).*', r'\1', posting)
            siz=len(temp)
            if siz>0 and posting != temp:
                info[key][docID] = float(temp)
            temp = re.sub(r'.*l([0-9]*).*', r'\1', posting)
            siz=len(temp)
            if siz > 0 and posting != temp:
                link[key][docID] = float(temp)
            temp = re.sub(r'.*b([0-9]*).*', r'\1', posting)
            siz=len(temp)
            if siz>0 and posting != temp:
                body[key][docID] = float(temp)
            temp = re.sub(r'.*t([0-9]*).*', r'\1', posting)
            siz=len(temp)
            if siz >0 and posting != temp:
                title[key][docID] = float(temp)
            i+=1
        string = key + ' ' + str(finalCount) + ' ' + str(len(docs))
        offset.append(str(offsetSize))
        offsetSize += len(string) + 1
        distinctWords.append(string)
    categoryData = []
    categoryOffset = []
    prevCategory = 0
    bodyData = []
    bodyOffset = []
    prevBody = 0
    linkData = []
    linkOffset = []
    prevLink = 0
    infoData = []
    infoOffset = []
    prevInfo = 0
    titleData = []
    titleOffset = []
    prevTitle = 0
    for key in tqdm(sorted(data.keys())):
        if key in link:
            docs = link[key]
            docs = sorted(docs, key = docs.get, reverse=True)
            string = key + ' '
            for doc in docs:
                string += doc + ' ' + str(link[key][doc]) + ' '
            linkData.append(string)
            linkOffset.append(str(prevLink) + ' ' + str(len(docs)))
            prevLink = prevLink + len(string) + 1
        if key in info:
            docs = info[key]
            docs = sorted(docs, key = docs.get, reverse=True)
            string = key + ' '
            for doc in docs:
                string += doc + ' ' + str(info[key][doc]) + ' '
            infoData.append(string)
            infoOffset.append(str(prevInfo) + ' ' + str(len(docs)))
            prevInfo += len(string) + 1
        if key in body:
            docs = body[key]
            docs = sorted(docs, key = docs.get, reverse=True)
            string = key + ' '
            for doc in docs:
                string += doc + ' ' + str(body[key][doc]) + ' '
            bodyData.append(string)
            bodyOffset.append(str(prevBody) + ' ' + str(len(docs)))
            prevBody += len(string) + 1
        if key in category:
            docs = category[key]
            docs = sorted(docs, key = docs.get, reverse=True)
            string = key + ' '
            for doc in docs:
                string += doc + ' ' + str(category[key][doc]) + ' '
            categoryData.append(string)
            categoryOffset.append(str(prevCategory) + ' ' + str(len(docs)))
            prevCategory += len(string) + 1
        if key in title:
            docs = title[key]
            docs = sorted(docs, key = docs.get, reverse=True)
            string = key + ' '
            for doc in docs:
                string += doc + ' ' + str(title[key][doc]) + ' '
            titleData.append(string)
            titleOffset.append(str(prevTitle) + ' ' + str(len(docs)))
            prevTitle += len(string) + 1
    thread = []
    thread.append(writeThread('t', titleData, titleOffset, finalCount))
    thread.append(writeThread('b', bodyData, bodyOffset, finalCount))
    thread.append(writeThread('i', infoData, infoOffset, finalCount))
    thread.append(writeThread('c', categoryData, categoryOffset, finalCount))
    thread.append(writeThread('l', linkData, linkOffset, finalCount))
    i=0
    total=5
    while(i<total):
        thread[i].start()
        i+=1
    i=0
    while(i<total):
        thread[i].join()
        i+=1
    file_name = './files/offset.txt' 
    with open(file_name, 'a') as f:
        f.write('\n'.join(offset))
        f.write('\n')
    file_name = './files/vocab.txt' 
    with open(file_name, 'a') as f:
        f.write('\n'.join(distinctWords))
        f.write('\n')
    return offsetSize , finalCount+1
  
def mergefiles(fileCount):
    flag = [0] * fileCount
    words = {}
    heap = []
    finalCount,offsetSize = 0,0
    files = {}
    top = {}
    data = defaultdict(list)
    i=0
    while i < fileCount:
        file_na = './files/index'
        f_name = file_na + str(i) + '.txt'
        files[i] = open(f_name, 'r')
        top[i] = files[i].readline().strip()
        words[i] = top[i].split()
        x = words[i][0]
        if x not in heap:
            heapq.heappush(heap,x)
        flag[i] = 1
        i=i+1
    count = 0
    while any(flag) == 1:
        temp = heapq.heappop(heap)
        count = count + 1
        tem_val = count%100000
        if tem_val == 0:
            oldFileCount = finalCount
            offsetSize,finalCount = final_write(data, finalCount, offsetSize)
            if finalCount != oldFileCount :
                data = defaultdict(list)
        i=0
        while i < fileCount:
            if flag[i]:
                if temp == words[i][0] :
                    top[i] = files[i].readline().strip()
                    data[temp].extend(words[i][1:])
                    if top[i]!='':
                        words[i] = top[i].split()
                        if words[i][0] not in heap:
                            heapq.heappush(heap, words[i][0])
                    else:
                        flag[i] = 0
                        files[i].close()       
            i+=1            
    offsetSize,finalCount = final_write(data, finalCount, offsetSize)

def file_handler(index, docID, out_path):
    data = []
    for key in sorted(index.keys()):
        string = key + ' '
        postings = index[key]
        string += ' '.join(postings)
        data.append(string)
    file_input = out_path 
    with open(file_input, 'w') as f:
        f.write('\n'.join(data))
    
class Handle(xml.sax.ContentHandler):
    def __init__(self):
        self.title = ''
        self.text = ''
        self.data = ''
        self.ID = ''
        self.fl = 0
    def startElement(self, tag, attributes):
        self.data = tag   
    def endElement(self, tag):
        if tag == 'page':
            docID[p_cnt] = self.title.strip().encode("ascii", errors="ignore").decode()
            title, body, info, categories, links = processText(self.text, self.title)
            Indexer( title, body, info, categories, links)
            self.data = ''
            self.title = ''
            self.text = ''
            self.ID = ''
            self.fl = 0
            #print('Finished:',p_cnt)
    def characters(self, content):
        if self.data == 'title':
            self.title = self.title + content
        elif self.data == 'id' and self.fl == 0:
            self.ID = content
            self.fl = 1
        elif self.data == 'text':
            self.text += content

class Parser():
    def __init__(self, file_input):
        self.parser = xml.sax.make_parser()
        self.parser.setFeature(xml.sax.handler.feature_namespaces, 0)
        self.handler = Handle()
        self.parser.setContentHandler(self.handler)
        self.parser.parse(file_input)

if __name__ == '__main__':
    ##### Store stop words in a dictionary
    with open('./files/stopwords.txt', 'r') as file :
    	stop_words = set(file.read().split('\n'))
    stop_dict = defaultdict(int)
    for word in stop_words:
    	stop_dict[word] = 1
    docID = {} ## {Doc id : Title}
    p_cnt = 0 ### Page Count
    f_cnt = 0 ### File Count
    offset = 0 ## Offset
    PostList = defaultdict(list)
    ##### Initialise Porter Stemmer
    #stemmer = PorterStemmer() 
    stemmer = Stemmer.Stemmer('english')
    ##### Begin Parsing
    parser = Parser(sys.argv[1])
    file_handler(PostList, docID,sys.argv[2])
    with open('./files/fileNumbers.txt', 'w') as f:
        f.write(str(p_cnt))
    offset = writeinfile(PostList, docID, f_cnt , offset)
    PostList = defaultdict(list)
    docID = {}
    f_cnt = f_cnt + 1
    mergefiles(f_cnt)
