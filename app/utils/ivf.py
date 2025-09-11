import numpy as np


class IVF:
    def __init__(self, n_partitions: int = 16, max_iters: int = 32):
        self.n_partitions = n_partitions
        self.ix = [[] for _ in range(self.n_partitions + 1)]
        self.max_iters = max_iters
        self.centroids = None
        self.is_fit = False
        self.labels = None

    def fit(self, X):
        ix = np.random.choice(len(X), self.n_partitions, replace=False)
        self.centroids = X[ix]

        for _ in range(self.max_iters):
            distances = self._calculate_distances(X)
            labels = np.argmin(distances, axis=0)

            new_centroids = np.array(
                [X[labels == k].mean(axis=0) for k in range(self.n_partitions)]
            )

            if np.all(self.centroids == new_centroids):
                break
            self.centroids = new_centroids
        self.is_fit = True
        self.labels = labels

    def predict(self, y):
        distances = self._calculate_distances(y)
        return np.argmin(distances, axis=0)

    def _calculate_distances(self, y):
        n_samples = y.shape[0]
        distances = np.zeros((self.n_partitions, n_samples))
        for i in range(n_samples):
            diff = self.centroids - y[i]
            distances[:, i] = np.linalg.norm(diff, axis=1)
        return distances

    def create_index(self, dataset):
        # Fit the dataset and get cluster assignments
        if not self.is_fit:
            self.fit(dataset)

        # Build index - group vector indices by their cluster assignment
        index = {i: [] for i in range(self.n_partitions)}
        for i, label in enumerate(self.labels):
            index[label].append(i)
        self.index = index
        return self.index

    def search(self, query):
        # Ensure query is 1D vector for distance calculation
        if query.ndim > 1:
            query = query.flatten()
        
        # Coarse search - find nearest centroid to query
        distances_to_centroids = [np.linalg.norm(query - centroid) for centroid in self.centroids]
        nearest_centroid = np.argmin(distances_to_centroids)

        # Fine search - return indices of vectors in the nearest centroid's index
        nearest_vectors = self.index.get(nearest_centroid, [])
        return nearest_vectors
