class TestMain:
    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

class TestLibraryRoutes:
    def test_create(self, client):
        library_data = {
            "name": "Test library",
            "des, documents_router, search_routercription": "A test library",
        }
        response = client.post("/libraries", json=library_data)
        assert response.status_code == 201

        data = response.json()
        assert data["name"] == library_data["name"]
        assert data["description"] == library_data["description"]
        assert "id" in data
