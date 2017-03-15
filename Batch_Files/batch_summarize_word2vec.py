""" word2vec based text summarization """

import glob
from nltk.stem.snowball import SnowballStemmer
import re
import numpy as np
from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity


def build_vocab(text):
    vocab = defaultdict(float)
    for sent in text:
        words = sent.split()
        for word in words:
            vocab[word] += 1
    
    wordtoix = defaultdict(float) 
    ixtoword = defaultdict(float)
    
    count = 0
    for w in vocab.keys():
        wordtoix[w] = count
        ixtoword[count] = w
        count += 1
    
    return wordtoix, ixtoword


def load_bin_vec(fname, vocab):
    """
    Loads 300x1 word vecs from Google (Mikolov) word2vec
    """
    word_vecs = {}
    with open(fname, "rb") as f:
        header = f.readline()
        vocab_size, layer1_size = map(int, header.split())
        binary_len = np.dtype('float32').itemsize * layer1_size
        for line in xrange(vocab_size):
            word = []
            while True:
                ch = f.read(1)
                if ch == ' ':
                    word = ''.join(word)
                    break
                if ch != '\n':
                    word.append(ch)   
            if word in vocab:
               word_vecs[word] = np.fromstring(f.read(binary_len), dtype='float32')  
            else:
                f.read(binary_len)
    return word_vecs

def get_W(w2v, content, k=300):
    """
    Return:
    ID: Get index of words in the given document;
    W:  Get word matrix. W[i] is the vector for word indexed by i
    """
    cnt_size = len(content)
    W = []          
    ID = []
    for idx in range(cnt_size):
        w = content[idx]
        if w in w2v:
            ID.append(idx)
            W.append(w2v[w])
            
    return np.array(ID), np.array(W)




"""
Step 1. pre-process the plain text files to construct a vocab. 
"""

file_list = glob.glob("./txt_summ/txt_all/*.txt")
stemmer = SnowballStemmer("english",ignore_stopwords=True) 


# build the vocab. based on all documents
word_counts = {}
j = 0
for source_file_path in file_list:
    j = j + 1
    print j 
    with open(source_file_path) as f:
        for line in f:
            line = re.sub("[^a-zA-Z]", " ", line) 
            tokens = line.lower().split()
            for w in tokens:
                #w = stemmer.stem(w)
                word_counts[w] = word_counts.get(w, 0) + 1

words = word_counts.keys()
freqs = [word_counts[word] for word in words]

# remove stop word
stopWords = []
with open("./txt_summ/englishStopWords.txt") as f:
    for line in f:
        stopWords.append(line.strip())

word_nonstop = []
freq_nonstop = []
for i in range(len(words)):
    if words[i] not in stopWords:
        word_nonstop.append(words[i])
        freq_nonstop.append(freqs[i])

# save the vocab.     
fw = open("./txt_summ/vocab_nonstop_total.txt", "w")
for w in word_nonstop: 
    fw.write(w + "\n")
fw.close()
    

   
"""
Step 2. Obtain word2vec for the words appearing in the given document 
"""

print "loading word2vec vectors...",
w2v_file = 'GoogleNews-vectors-negative300.bin'

wordtoix, ixtoword = build_vocab(word_nonstop) 
w2v = load_bin_vec(w2v_file, wordtoix)
f = open('./txt_summ/summarization_word2vec.txt', 'w')

for c in range(len(file_list)):
    print c
    # c=1
    source_file_path=file_list[c]
    
    dir_str = str.split(source_file_path,'\\' )
    file_name = dir_str[1]
    content = []
    with open(source_file_path) as rf:
        for line in rf:
            line = re.sub("[^a-zA-Z]", " ", line) 
            tokens = line.lower().split()
            for w in tokens:
                # w = stemmer.stem(w)         
                content.append(w)
                
    wordtoix, ixtoword = build_vocab(content) 
    
    # vector for this doc
    ID, W = get_W(w2v,content) 
    
    # mean vec for entire doc
    doc_vec = np.mean(W,0)
    
    # mean vec for windows   
    stride = 10
    hw_size = 40
    start = 0
    end = len(content)
    
    try:  
        # compute the mean of word2vec for each window
        sents_W_mean = []
        while start <= end-hw_size:
            idx_sent = range(start, start+ hw_size)
            idx = np.intersect1d(np.where(ID>=start), np.where(ID<start+ hw_size))
            sent_W = W[idx]
            sent_W_mean = np.mean(sent_W, 0)
            sents_W_mean.append(sent_W_mean)
            start += stride
            
        # the nearest neighbor of windows to the mean of the document
        sents_W_mean = np.array(sents_W_mean)
        cos_sim = cosine_similarity(doc_vec.reshape([1,len(doc_vec)]), sents_W_mean)
        max_sim_id = int( np.argmax(cos_sim))
        summarize_sent = content[stride*max_sim_id:stride*max_sim_id+ hw_size]
        
        key_sent_str = ''
        for w in summarize_sent:
            key_sent_str = key_sent_str + ' ' + w        
        
        print key_sent_str 
        
        # save the summarization
        f.write("Document"+str(c)+"("+file_name+")")
        f.write("\n\n")
        
        f.write(key_sent_str)
        
        f.write("\n\n")
    except:
        pass

f.close()                
         
                

