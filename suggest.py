import re
import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from scipy.sparse import csr_matrix
import sparse_dot_topn.sparse_dot_topn as ct

def ngrams(string, n=3):
    string = re.sub(r'[,-./]|\sExt',r'', string)
    ngrams = zip(*[string[i:] for i in range(n)])
    return [''.join(ngram) for ngram in ngrams]

names = pd.read_table('wordlist.txt', header=None)
names.columns = ['Company Name']


company_names = names['Company Name'].unique()
vectorizer = TfidfVectorizer(min_df=1, analyzer=ngrams)
tf_idf_matrix = vectorizer.fit_transform(company_names)


def awesome_cossim_top(A, B, ntop, lower_bound=0):
    # force A and B as a CSR matrix.
    # If they have already been CSR, there is no overhead
    A = A.tocsr()
    B = B.tocsr()
    M, _ = A.shape
    _, N = B.shape
 
    idx_dtype = np.int32
 
    nnz_max = M*ntop
 
    indptr = np.zeros(M+1, dtype=idx_dtype)
    indices = np.zeros(nnz_max, dtype=idx_dtype)
    data = np.zeros(nnz_max, dtype=A.dtype)

    ct.sparse_dot_topn(
        M, N, np.asarray(A.indptr, dtype=idx_dtype),
        np.asarray(A.indices, dtype=idx_dtype),
        A.data,
        np.asarray(B.indptr, dtype=idx_dtype),
        np.asarray(B.indices, dtype=idx_dtype),
        B.data,
        ntop,
        lower_bound,
        indptr, indices, data)

    return csr_matrix((data,indices,indptr),shape=(M,N))


matches = awesome_cossim_top(tf_idf_matrix, tf_idf_matrix.transpose(), 10, 0.8)


def get_matches_df(sparse_matrix, name_vector, top=100):
    non_zeros = sparse_matrix.nonzero()
    
    sparserows = non_zeros[0]
    sparsecols = non_zeros[1]
    
    if top:
        nr_matches = top
    else:
        nr_matches = sparsecols.size
    
    left_side = np.empty([nr_matches], dtype=object)
    right_side = np.empty([nr_matches], dtype=object)
    similairity = np.zeros(nr_matches)
    
    for index in range(0, nr_matches):
        left_side[index] = name_vector[sparserows[index]]
        right_side[index] = name_vector[sparsecols[index]]
        similairity[index] = sparse_matrix.data[index]
    
    return pd.DataFrame({'left_side': left_side,
                          'right_side': right_side,
                           'similarity': similairity})
 
matches_df = get_matches_df(matches, company_names, top=None)
matches_df = matches_df[matches_df['similarity'] < 0.99999] # Remove all exact matches

samps_sorted = matches_df.sort_values(['similarity'], ascending=False)

print(samps_sorted.shape)
print(samps_sorted)

lgrouped = samps_sorted[['left_side', 'right_side']].groupby('left_side', sort=True)

if not os.path.exists('matches'):
    os.mkdir('matches')
else:
    os.system('rm matches/*')

for k, gr in lgrouped:
    print("Processing {}".format(k))
    gr['right_side'].to_csv('matches/{}.csv'.format(k.replace(' ', '_')), index=False, header=False )

group_counts = lgrouped.count()
group_counts.to_csv('matches-groups.csv')

print(group_counts.sort_values('right_side'))
