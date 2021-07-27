import numpy as np
import math as m

import typer
np.seterr(divide='ignore', invalid='ignore')


class IREProcessor:
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
    def applyWeighting(self, freqList, globalForm):
        tncList = []
        for i in range(len(freqList)):
            type(freqList[i])
            tncList.append(self.computeLocalWeight(
                freqList[i], freqList))

        globalWeights = self.computeGlobalNormalWeights(
            freqList) if globalForm == 'normal' else self.computeGlobalWeights(freqList)
        globalWeights = list(globalWeights.items())

        tncList, _ = self.convertDictToMatrix(tncList)
        for i in range(len(globalWeights)):
            tncList[:, i] = tncList[:, i] * globalWeights[i][1]

        return tncList

    # Compute the local weights for a a term in a document
    def computeLocalWeight(self, freq, freqList):
        weightedDict = {}
        lenDoc = sum(freq.values())

        for token, count in freq.items():
            try:
                weightedDict[token] = (count / lenDoc)
            except:
                weightedDict[token] = 0

        return weightedDict

    # Compute global idf weights for the terms
    def computeGlobalWeights(self, freqList):
        globalWeights = dict.fromkeys(freqList[0].keys(), 0)
        matrix, features = self.convertDictToMatrix(freqList)
        N = len(freqList)

        for key, _ in globalWeights.items():
            featIndex = features.index(key)
            col = matrix[:, featIndex]
            col = list(filter(lambda x: x != 0, col))
            globalWeights[key] = m.log2((N + 1) / (float(len(col)) + 1) + 1)

        return globalWeights

    # Compute global normal weights for the terms
    def computeGlobalNormalWeights(self, freqList):
        globalWeights = dict.fromkeys(freqList[0].keys(), 0)
        matrix, features = self.convertDictToMatrix(freqList)

        for key, _ in globalWeights.items():
            featIndex = features.index(key)
            col = matrix[:, featIndex]
            col = list(map(lambda x: x*x, col))
            globalWeights[key] = 1 / m.sqrt(sum(col))

        return globalWeights

    # Decompose the td-matrix using SVD
    def calculateSVD(self, matrix):
        U, sigma, Vt = np.linalg.svd(matrix, full_matrices=False)
        sigma = np.diag(sigma)
        optimalU = U
        optimalSigma = sigma
        optimalVt = Vt
        for k in range(1, sigma.shape[0]):
            U_new, sigma_new, Vt_new = self.reduceDimensions(k, U, sigma, Vt)
            error = 1 - (np.trace(sigma_new) / np.trace(sigma))
            if error <= 0.01:
                optimalU, optimalSigma, optimalVt = U_new, sigma_new, Vt_new
                break
        return optimalU, optimalSigma, optimalVt

    # Reduce dimension of the matrix
    def reduceDimensions(self, k, U, sigma, Vt):
        U = U[:, :k]
        sigma = sigma[:k, :k]
        Vt = Vt[:k, :]
        return U, sigma, Vt

    # Create a matrix from list of dictionary
    def convertDictToMatrix(self, freqList):
        features = []

        # Extract features
        for key, _ in freqList[0].items():
            features.append(key)

        matrix = np.empty((0, len(features)))
        for freq in freqList:
            dictList = [value for _, value in freq.items()]
            matrix = np.vstack([matrix, dictList])

        return matrix, features

    # Calculate the magnitude of a vector(list)
    def calculateMagnitude(self, vector):
        return m.sqrt(sum(list(map(lambda x: x*x, vector))))

    # Calculate similarity using euclidean distance
    def calculateSimilarityByEuclideanMethod(self, matrix, sigma):
        result = np.zeros((matrix.shape[0], matrix.shape[0]))
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[0]):
                vector = matrix[i] - matrix[j]
                magnitude = self.calculateMagnitude(vector)
                result[i, j] = m.exp(-(magnitude ** 2) / (2 * (sigma ** 2)))

        return result

    # Calculate the similarity
    def calculateSimilarity(self, matrix):
        matrix = matrix.transpose()

        # Normalize document vectors from 0 to 1
        for i in range(matrix.shape[1]):
            magnitude = self.calculateMagnitude(matrix[:, i])
            matrix[:, i] = matrix[:, i] / magnitude

        matrix = np.nan_to_num(matrix)

        try:
            U, sigma, Vt = self.calculateSVD(matrix)
            V = Vt.transpose()
            val = V.dot(sigma)
            result = val.dot(val.transpose())
            return result
        except Exception as ex:
            typer.echo(str(ex))
            typer.secho('Error computing Single Value Decomposition!',
                        fg=typer.colors.RED)
            typer.secho(
                'Recalculating similarity using Cosine Factor...', fg=typer.colors.CYAN)
            result = matrix.transpose() @ matrix
            return result
