class TestMain:
    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
