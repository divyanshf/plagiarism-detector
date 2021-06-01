import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer


class IREProcessor:
    def __init__(self, pcomment):
        self.pcomment = pcomment

    def createTermDocMatrix(self, corpus):
        corpusCode = [doc.file for doc in corpus]
        # corpusComments = [doc.comments for doc in corpus]
        vectorizer = CountVectorizer()
        tdMatrixCode = vectorizer.fit_transform(corpusCode)
        # tdMatrixComments = vectorizer.fit_transform(corpusComments)
        dfCode = pd.DataFrame(tdMatrixCode.toarray(),
                              columns=vectorizer.get_feature_names(), index=[doc.filename for doc in corpus])
        # dfComments = pd.DataFrame(tdMatrixComments.toarray(),
        #                           columns=vectorizer.get_feature_names(), index=[doc.filename for doc in corpus])
        print(dfCode)
        # print(dfComments)
        return tdMatrixCode

    def createTermDocumentMatrixCode(self, corpus):
        corpusCode = [doc.file for doc in corpus]

        # Create a set of terms
        features = set()
        tokenList = []
        for code in corpusCode:
            tokens = code.split()
            tokenList.append(tokens)
            features = features.union(set(tokens))

        # Create a term frequency dictionary for each token list
        freqList = []
        for tokens in tokenList:
            freq = dict.fromkeys(features, 0)
            for token in tokens:
                freq[token] += 1
            freqList.append(freq)

        df = pd.DataFrame(freqList)
        print(df)

    def applyTNCTermWeighting(self, tdMatrix):
        print(tdMatrix.toarray())
