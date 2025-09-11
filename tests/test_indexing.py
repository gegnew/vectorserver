from uuid import uuid4

import numpy as np

from app.embeddings import Embedder
from app.models.chunk import Chunk
from app.utils.flat_index import FlatIndex
from app.utils.ivf import IVF


class TestFlatIndex:
    def test_basic_search(self):
        vectors = np.random.random((5, 10)).astype(np.float32)

        flat_index = FlatIndex()
        flat_index.fit(vectors)

        query = np.random.random(10).astype(np.float32)
        results = flat_index.search(query, k=3)

        assert len(results) == 3
        assert all(isinstance(idx, int) for idx in results)
        assert all(0 <= idx < 5 for idx in results)



class TestIVFIndex:
    def test_search_basic_functionality(self):
        np.random.seed(42)
        # 20 rows of 2 features
        cluster1 = np.random.normal([0, 0], 0.5, (20, 2))
        cluster2 = np.random.normal([5, 5], 0.5, (20, 2))
        cluster3 = np.random.normal([10, 0], 0.5, (20, 2))
        dataset = np.vstack([cluster1, cluster2, cluster3])

        query = np.array([0.1, 0.1])  # close to cluster1

        ivf = IVF(n_clusters=6)
        ivf.fit(dataset)
        ivf.create_index(dataset)
        result = ivf.search(query)

        # Should return indices from cluster1 (0-19)
        assert isinstance(result, list)
        assert all(isinstance(idx, int | np.integer) for idx in result)
        assert result == list(range(20))

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

        ivf = IVF(n_clusters=3)
        ivf.fit(embeddings)
        ivf.create_index(embeddings)
        res = ivf.search(query[0])

        assert isinstance(res, list)
        assert all(isinstance(idx, int) for idx in res)
        assert all(query_term in phrases[i] for i in res)
