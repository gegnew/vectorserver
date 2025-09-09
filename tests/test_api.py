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

    # TODO: implement other CRUD routes

    def test_semantic_search(self, client, service_with_documents):
        search_data = {
            "content": """
            Healthcare
            - Medical image analysis for disease diagnosis
            - Drug discovery and development
            - Personalized treatment recommendations
            - Epidemic prediction and tracking
            """
        }
        response = client.post("/search", json=search_data)
        assert response.status_code == 200
