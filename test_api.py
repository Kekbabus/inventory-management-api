import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_home():
    """Test the home endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_get_all():
    """Test getting all products"""
    response = client.get("/getAll")
    assert response.status_code == 200
    assert "products" in response.json()
    assert "count" in response.json()

def test_get_single_product():
    """Test getting a single product"""
    response = client.get("/getSingleProduct?product_id=1001")
    assert response.status_code == 200
    assert response.json()["ProductID"] == 1001

def test_get_single_product_not_found():
    """Test getting a non-existent product"""
    response = client.get("/getSingleProduct?product_id=9999")
    assert response.status_code == 404

def test_add_new_product():
    """Test adding a new product"""
    new_product = {
        "Name": "Test Product",
        "UnitPrice": 99.99,
        "StockQuantity": 10,
        "Description": "This is a test product"
    }
    response = client.post("/addNew", json=new_product)
    assert response.status_code == 200
    assert "ProductID" in response.json()

def test_starts_with():
    """Test products starting with a letter"""
    response = client.get("/startsWith?letter=N")
    assert response.status_code == 200
    assert "products" in response.json()

def test_paginate():
    """Test pagination"""
    response = client.get("/paginate?start_id=1001&end_id=1010")
    assert response.status_code == 200
    assert "products" in response.json()
    assert len(response.json()["products"]) <= 10

def test_convert():
    """Test currency conversion"""
    response = client.get("/convert?product_id=1001")
    assert response.status_code == 200
    assert "PriceUSD" in response.json()
    assert "PriceEUR" in response.json()

def test_delete_one():
    """Test deleting a product"""
    # First add a product to delete
    new_product = {
        "Name": "Delete Me",
        "UnitPrice": 10.00,
        "StockQuantity": 1,
        "Description": "Product to be deleted"
    }
    add_response = client.post("/addNew", json=new_product)
    product_id = add_response.json()["ProductID"]
    
    # Now delete it
    response = client.delete(f"/deleteOne?product_id={product_id}")
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]
