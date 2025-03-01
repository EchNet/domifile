def test_webhook_endpoint_missing_headers(client):
  response = client.post('/webhook')
  assert response.status_code == 400


def test_health_check(client):
  response = client.post('/')
  assert response.status_code == 200
  assert response.json == {"status": "OK"}
