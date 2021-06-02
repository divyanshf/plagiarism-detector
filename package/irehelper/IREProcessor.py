from operator import index
import numpy as np
import pandas as pd
import math as m
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer


class IREProcessor:
    def __init__(self, pcomment):
        self.pcomment = pcomment

    def createVectorizerImplementation(self, corpus):
        vectorizer = TfidfVectorizer()
        return vectorizer.fit_transform(corpus)

    # Create a term by document matrix
    def createTermDocumentMatrix(self, corpus):
        # Create a set of terms
        features = set()
        tokenList = []
        for doc in corpus:
            tokens = doc.split()
            tokenList.append(tokens)
            features = features.union(set(tokens))

        # Create a term frequency dictionary for each token list
        freqList = []
        for tokens in tokenList:
            freq = dict.fromkeys(features, 0)
            for token in tokens:
                freq[token] += 1
            freqList.append(freq)

        return freqList

    # Apply TNC weigthing on the t-d matrix
    def applyTNCWeighting(self, freqList):
        tncList = []
        for i in range(len(freqList)):
            type(freqList[i])
            tncList.append(self.computeTNCWeight(
                freqList[i], freqList))

        return tncList

    # Compute the tnc weights for a document
    def computeTNCWeight(self, freq, freqList):
        weightedDict = {}
        lenDoc = sum(freq.values())

        # Local Term frequency weighting and Global Normal weighting
        # (fij / total terms) * (1 / sqrt(sumj((fij)^2)))
        for token, count in freq.items():
            sumFreqSquared = 0
            for doc in freqList:
                sumFreqSquared += pow(doc[token], 2)
            normal = 1 / m.sqrt(sumFreqSquared)
            weightedDict[token] = (count / lenDoc) * normal

        return weightedDict

    # Decompose the td-matrix using SVD
    def calculateSVD(self, matrix):
        U, sigma, Vt = np.linalg.svd(matrix)
        sigma = np.diag(sigma)
        return U, sigma, Vt

    # Reduce dimension of the matrix
    def reduceDimensions(self, k, matrix):
        reducedMatrix = matrix[:, :k]
        return reducedMatrix

    # Calculate the similarity
    def calculateSimilarity(self, freqList):
        features = []

        # Extract features
        for key, _ in freqList[0].items():
            features.append(key)

        # Numpy matrix out of the freqlist
        matrix = np.empty((0, len(features)))
        for freq in freqList:
            dictList = [value for _, value in freq.items()]
            matrix = np.vstack([matrix, dictList])

        matrix = matrix.transpose()
        U, sigma, Vt = self.calculateSVD(matrix)

        # Reducing dimensions to the shape of sigma
        U = self.reduceDimensions(sigma.shape[0], U)
        V = self.reduceDimensions(sigma.shape[0], Vt.transpose())
        # reducedMatrix = U @ sigma @ (V.transpose())
        # result = (reducedMatrix.transpose())[0] @ reducedMatrix
        val = V.dot(sigma)
        result = val.dot(val.transpose())
        # print(result[0, 1:])
        print(result)
