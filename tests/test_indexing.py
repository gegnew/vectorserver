import numpy as np

from app.embeddings import Embedder
from app.utils.ivf import IVF


class TestIndexing:
    def test_search_basic_functionality(self):
        """Test search() with simple synthetic data"""
        np.random.seed(42)
        cluster1 = np.random.normal([0, 0], 0.5, (20, 2))
        cluster2 = np.random.normal([5, 5], 0.5, (20, 2))
        cluster3 = np.random.normal([10, 0], 0.5, (20, 2))
        dataset = np.vstack([cluster1, cluster2, cluster3])

        query = np.array([0.1, 0.1])  # close to cluster1

        ivf = IVF(n_partitions=3)
        result = ivf.search(dataset, query)

        # Should return indices from cluster1 (0-19)
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(idx, int | np.integer) for idx in result)

    def test_ivf_embeddings(self):
        eb = Embedder()
        phrases = [
            "i love soup",
            "soup is my favorite",
            "london is far away",
            "soup",
            "very much soup soup",
        ]
        embeddings = eb.embed(phrases)
        query_term = "london"
        query = eb.embed([query_term])

        ivf = IVF(n_partitions=3)
        res = ivf.search(embeddings, query[0])

        assert isinstance(res, list)
        assert all(isinstance(idx, int) for idx in res)
        assert all(query_term in phrases[i] for i in res)
