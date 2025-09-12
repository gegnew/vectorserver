import numpy as np


class KMeans:
    def __init__(self, n_clusters: int = 3, max_iters: int = 32):
        self.n_clusters = n_clusters
        self.max_iters = max_iters
        self.centroids = None
        self.labels = None
        self.is_fitted = False

    def fit(self, X):
        # Initialize centroids randomly.
        # If fewer data points than clusters, use all data points and reduce clusters
        n_samples = len(X)
        actual_clusters = min(self.n_clusters, n_samples)

        if actual_clusters < self.n_clusters:
            self.n_clusters = actual_clusters

        ix = np.random.choice(n_samples, actual_clusters, replace=False)
        self.centroids = X[ix]

        # Initialize labels
        distances = self._calculate_distances(X)
        labels = np.argmin(distances, axis=0)

        # Iterative k-means algorithm
        for _ in range(self.max_iters):
            distances = self._calculate_distances(X)
            labels = np.argmin(distances, axis=0)

            # Update centroids
            new_centroids = np.array(
                [X[labels == k].mean(axis=0) for k in range(self.n_clusters)]
            )

            # Check for convergence
            if np.all(self.centroids == new_centroids):
                break
            self.centroids = new_centroids

        self.labels = labels
        self.is_fitted = True
        return self

    def predict(self, X):
        if not self.is_fitted:
            raise ValueError("KMeans must be fitted before prediction")

        distances = self._calculate_distances(X)
        return np.argmin(distances, axis=0)

    def _calculate_distances(self, X):
        n_samples = X.shape[0]
        distances = np.zeros((self.n_clusters, n_samples))
        for i in range(n_samples):
            diff = self.centroids - X[i]
            distances[:, i] = np.linalg.norm(diff, axis=1)
        return distances


class IVF:
    def __init__(self, n_clusters: int = 16, max_iters: int = 32):
        self.n_clusters = n_clusters
        self.ix = [[] for _ in range(self.n_clusters + 1)]
        self.max_iters = max_iters
        self.kmeans = KMeans(n_clusters=n_clusters, max_iters=max_iters)
        self.index = None

    def fit(self, X):
        self.kmeans.fit(X)
        return self

    def predict(self, X):
        return self.kmeans.predict(X)

    @property
    def centroids(self):
        return self.kmeans.centroids

    @property
    def labels(self):
        return self.kmeans.labels

    @property
    def is_fit(self):
        return self.kmeans.is_fitted

    def create_index(self, dataset):
        # Fit the dataset and get cluster assignments
        if not self.is_fit:
            self.fit(dataset)

        # Build index - group vector indices by their cluster assignment
        index = {i: [] for i in range(self.n_clusters)}
        for i, label in enumerate(self.labels):
            index[label].append(i)
        self.index = index
        return self.index

    def search(self, query):
        # Ensure query is 1D vector for distance calculation
        if query.ndim > 1:
            query = query.flatten()

        # Coarse search - find nearest centroid to query
        distances_to_centroids = [
            np.linalg.norm(query - centroid) for centroid in self.centroids
        ]
        nearest_centroid = np.argmin(distances_to_centroids)

        # Fine search - return indices of vectors in the nearest centroid's index
        nearest_vectors = self.index.get(nearest_centroid, [])
        return nearest_vectors
