# filepath: e:\HackVortex\SewageMapAI\backend\tests\test_app.py
import os
import sys
import pytest
import json
from io import BytesIO

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    """Test the index route returns expected welcome message"""
    response = client.get('/')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert "Welcome to SewageMapAI API" in data['message']

def test_sewage_demand_route(client):
    """Test the sewage demand route returns data"""
    response = client.get('/sewage-demand')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert 'data' in data
    assert 'count' in data
    assert isinstance(data['data'], list)

def test_complaints_route(client):
    """Test the complaints route returns data"""
    response = client.get('/complaints')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert 'data' in data
    assert 'count' in data
    assert isinstance(data['data'], list)

def test_illegal_connections_route(client):
    """Test the illegal connections route returns data"""
    response = client.get('/illegal-connections')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert 'data' in data
    assert 'count' in data
    assert isinstance(data['data'], list)

def test_upload_image_without_file(client):
    """Test image upload route returns error when no file is provided"""
    response = client.post('/upload-image')
    data = json.loads(response.data)
    
    assert response.status_code == 400
    assert 'error' in data
    assert "No file part" in data['error']

def test_upload_image_empty_file(client):
    """Test image upload route returns error when empty file is provided"""
    response = client.post('/upload-image', data={
        'file': (BytesIO(), '')
    })
    data = json.loads(response.data)
    
    assert response.status_code == 400
    assert 'error' in data
    assert "No selected file" in data['error']

def test_invalid_route(client):
    """Test an invalid route returns 404"""
    response = client.get('/invalid-route')
    data = json.loads(response.data)
    
    assert response.status_code == 404
    assert 'error' in data
