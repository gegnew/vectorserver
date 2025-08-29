class TestMain:
    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
