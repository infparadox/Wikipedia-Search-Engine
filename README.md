# Wikipedia-Search-Engine

This repository consists of a search engine over the 63GB Wikipedia dump. The code consists of indexer.py and search.py. Both simple and multi field queries have been implemented. The search returns a ranked list of articles in real time.

Indexing:
1)Parsing: SAX Parser is used to parse the XML corpus.
2)Casefolding: Converting Upper Case to Lower Case.
3)Tokenisation: It is done using regex.
4)Stop Word Removal: Stop words are removed by referring to the stop word list returned by nltk.
5)Stemming: A python library PyStemmer is used for this purpose.
6)Creating various index files with word to field postings.
7)Multi-way External sorting on the index files to create field based files along with their respective offsets.

Searching:
1)The query given is parsed, processed and given to the respective query handler(simple or field).
2)One by one word is searched in vocabulary and the file number is noted.
3)The respective field files are opened and the document ids along with the frequencies are noted.
4)The documents are ranked on the basis of TF-IDF scores.
5)The title of the documents are extracted using title.txt

Files Produced
1)index*.txt (intermediate files) : It consists of words with their posting list. Eg. d1b2t4c5 d5b3t6l1
2)title.txt : It consist of id-title mapping.
3)titleOffset.txt : Offset for title.txt
4)vocab.txt : It has all the words and the file number in which those words can be found along with the document frequency.
offset.txt : Offset for vocab.txt
5)[b|t|i|r|l|c]*.txt : It consists of words found in various sections of the article along with document id and frequency.
offset_[b|t|i|r|l|c]*.txt : Offset for various field files.

How to run:
1) Run python3 indexer.py ./path of xml dump ./path of output(Inverted Index)
2) Now, run python3 search.py , wait for files to be loaded 
3) Now, input queries .
4) For field queries give space separated in form of t:(title) b:(body)  i:(infobox)  c:category l:(links)
5) Output shows top10 relevant documents.
