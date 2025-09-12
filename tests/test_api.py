import pytest


class TestMain:
    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestRoutes:
    def test_create_library(self, client):
        library_data = {
            "name": "Test library",
            "description": "A test library",
        }
        response = client.post("/libraries", json=library_data)
        assert response.status_code == 201

        data = response.json()
        assert data["name"] == library_data["name"]
        assert data["description"] == library_data["description"]
        assert "id" in data

    def test_update_library(self, client):
        library_data = {
            "name": "Test library",
            "description": "A test library",
        }
        lib = client.post("/libraries", json=library_data).json()

        response = client.put(
            "/libraries", json={
                "id": lib["id"],
                "name": "Updated Test Library",
                "description": "Updated test library description",
                "metadata": {"updated": True}
            }
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Updated Test Library"

    def test_delete_library(self, client):
        library_data = {
            "name": "Test library",
            "description": "A test library",
        }
        lib = client.post("/libraries", json=library_data).json()

        response = client.delete("/libraries", params={"id": lib["id"]})
        assert response.status_code == 202
        assert response.json()["deleted"] == 1

    @pytest.mark.parametrize("index_type", ["flat", "ivf"])
    def test_semantic_search(self, client, index_type, service_with_documents):
        """Test IVF and flat index

        # TODO: for some reason this test fails when the whole test suite runs
        """
        lib = client.get("/libraries").json()[0]["id"]

        search_data = {
            "content": """
            Healthcare
            - Medical image analysis for disease diagnosis
            - Drug discovery and development
            - Personalized treatment recommendations
            - Epidemic prediction and tracking
            """,
            "index_type": index_type,
            "library_id": lib,
        }
        response = client.post("/search", json=search_data)
        assert response.status_code == 200
