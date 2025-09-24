import pytest


class TestEndToEnd:
    def test_library_crud_operations(self, client):
        library_data = {
            "name": "E2E Test Library",
            "description": "End-to-end testing library",
            "metadata": {"test": True},
        }

        response = client.post("/libraries", json=library_data)
        assert response.status_code == 201
        library = response.json()
        library_id = library["id"]
        assert library["name"] == library_data["name"]
        assert library["description"] == library_data["description"]

        response = client.get(f"/libraries/{library_id}")
        assert response.status_code == 200
        fetched_library = response.json()
        assert fetched_library["id"] == library_id
        assert fetched_library["name"] == library_data["name"]

        response = client.get("/libraries")
        assert response.status_code == 200
        libraries = response.json()
        assert any(lib["id"] == library_id for lib in libraries)

        update_data = {
            "id": library_id,
            "name": "Updated E2E Library",
            "description": "Updated description",
            "metadata": {"test": True, "updated": True},
        }
        response = client.put("/libraries", json=update_data)
        assert response.status_code == 201
        updated_library = response.json()
        assert updated_library["name"] == "Updated E2E Library"
        assert updated_library["description"] == "Updated description"

        response = client.delete("/libraries", params={"id": library_id})
        assert response.status_code == 202
        assert response.json()["deleted"] == 1

    @pytest.mark.parametrize("index_type", ["flat", "ivf"])
    def test_document_indexing_and_search(self, client, index_type):
        library_data = {
            "name": f"Vector Search Library - {index_type}",
            "description": f"Library for testing {index_type} vector search",
        }
        response = client.post("/libraries", json=library_data)
        library = response.json()
        library_id = library["id"]

        documents = [
            {
                "title": "Machine Learning Basics",
                "content": "Machine learning is a subset of artificial intelligence that focuses on algorithms and statistical models. It enables computers to perform tasks without explicit programming by learning from data patterns.",
                "library_id": library_id,
            },
            {
                "title": "Deep Learning Networks",
                "content": "Deep learning uses neural networks with multiple layers to model and understand complex patterns in data. It has applications in computer vision, natural language processing, and speech recognition.",
                "library_id": library_id,
            },
            {
                "title": "Data Science Methods",
                "content": "Data science combines domain expertise, programming skills, and knowledge of mathematics and statistics to extract meaningful insights from data. It involves data collection, cleaning, analysis, and visualization.",
                "library_id": library_id,
            },
        ]

        for doc_data in documents:
            response = client.post("/documents", json=doc_data)
            assert response.status_code == 201

        search_queries = [
            "artificial intelligence and machine learning algorithms",
            "neural networks and deep learning applications",
            "statistical analysis and data visualization techniques",
        ]

        for query in search_queries:
            search_data = {
                "content": query,
                "library_id": library_id,
                "index_type": index_type,
            }
            response = client.post("/search", json=search_data)
            assert response.status_code == 200

            result = response.json()
            assert len(result) > 0
            first_result = result[0]
            assert "document" in first_result
            assert "content" in first_result["document"]
            assert "title" in first_result["document"]

        response = client.delete("/libraries", params={"id": library_id})
        assert response.status_code == 202

    def test_full_workflow_integration(self, client):
        library_data = {
            "name": "Integration Test Library",
            "description": "Full workflow integration testing",
        }
        response = client.post("/libraries", json=library_data)
        library = response.json()
        library_id = library["id"]

        documents = [
            {
                "title": "Healthcare AI",
                "content": "Healthcare AI applications include medical image analysis for disease diagnosis, drug discovery and development, personalized treatment recommendations, and epidemic prediction and tracking systems.",
                "library_id": library_id,
            },
            {
                "title": "Financial Technology",
                "content": "Financial technology leverages artificial intelligence for fraud detection, algorithmic trading, credit scoring, and risk assessment. Machine learning models analyze transaction patterns and market data.",
                "library_id": library_id,
            },
        ]

        created_docs = []
        for doc_data in documents:
            response = client.post("/documents", json=doc_data)
            assert response.status_code == 201
            created_docs.append(response.json())

        for index_type in ["flat", "ivf"]:
            search_data = {
                "content": "medical diagnosis and healthcare applications",
                "library_id": library_id,
                "index_type": index_type,
            }
            response = client.post("/search", json=search_data)
            assert response.status_code == 200
            result = response.json()
            assert len(result) > 0
            first_result = result[0]
            assert "document" in first_result
            assert "content" in first_result["document"]

            healthcare_found = "healthcare" in first_result["document"].get("content", "").lower()
            assert (
                healthcare_found
            ), f"Healthcare content not found in {index_type} search results"

        response = client.get(f"/libraries/{library_id}/documents")
        if response.status_code == 200:
            docs = response.json()
            assert len(docs) == len(documents)

        response = client.delete("/libraries", params={"id": library_id})
        assert response.status_code == 202
