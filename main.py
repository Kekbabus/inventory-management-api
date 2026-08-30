from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, validator
from pymongo import MongoClient
from typing import Optional
import requests

app = FastAPI(title="Inventory Management API", version="1.0.0")

# MongoDB connection
client = MongoClient('mongodb+srv://shadowblader333_db_user:qwerty123@cluster0.f1z6erc.mongodb.net/?appName=Cluster0')
db = client['inventory_db']
collection = db['products']

# Pydantic models for data validation
class Product(BaseModel):
    ProductID: int = Field(..., gt=0, description="Product ID must be positive")
    Name: str = Field(..., min_length=1, description="Product name cannot be empty")
    UnitPrice: float = Field(..., gt=0, description="Price must be positive")
    StockQuantity: int = Field(..., ge=0, description="Stock quantity cannot be negative")
    Description: str = Field(..., min_length=1, description="Description cannot be empty")

class ProductCreate(BaseModel):
    Name: str = Field(..., min_length=1)
    UnitPrice: float = Field(..., gt=0)
    StockQuantity: int = Field(..., ge=0)
    Description: str = Field(..., min_length=1)

@app.get("/")
def home():
    """Welcome endpoint"""
    return {"message": "Welcome to Inventory Management API"}

@app.get("/getSingleProduct")
def get_single_product(product_id: int = Query(..., gt=0, description="Product ID")):
    """
    Get a single product by ID
    """
    product = collection.find_one({"ProductID": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.get("/getAll")
def get_all():
    """
    Get all products from inventory
    """
    products = list(collection.find({}, {"_id": 0}))
    return {"products": products, "count": len(products)}

@app.post("/addNew")
def add_new(product: ProductCreate):
    """
    Add a new product to inventory
    """
    # Find the highest ProductID and increment it
    last_product = collection.find_one(sort=[("ProductID", -1)])
    new_id = 1 if not last_product else last_product["ProductID"] + 1
    
    new_product = {
        "ProductID": new_id,
        "Name": product.Name,
        "UnitPrice": product.UnitPrice,
        "StockQuantity": product.StockQuantity,
        "Description": product.Description
    }
    
    collection.insert_one(new_product)
    return {"message": "Product added successfully", "ProductID": new_id}

@app.delete("/deleteOne")
def delete_one(product_id: int = Query(..., gt=0, description="Product ID to delete")):
    """
    Delete a product by ID
    """
    result = collection.delete_one({"ProductID": product_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": f"Product {product_id} deleted successfully"}

@app.get("/startsWith")
def starts_with(letter: str = Query(..., min_length=1, max_length=1, description="Starting letter")):
    """
    Get all products that start with a specific letter
    """
    # Case-insensitive search
    products = list(collection.find(
        {"Name": {"$regex": f"^{letter}", "$options": "i"}},
        {"_id": 0}
    ))
    return {"products": products, "count": len(products)}

@app.get("/paginate")
def paginate(start_id: int = Query(..., gt=0, description="Starting Product ID"),
             end_id: int = Query(..., gt=0, description="Ending Product ID")):
    """
    Get products in batches of 10 between start and end IDs
    """
    if start_id > end_id:
        raise HTTPException(status_code=400, detail="start_id must be less than or equal to end_id")
    
    products = list(collection.find(
        {"ProductID": {"$gte": start_id, "$lte": end_id}},
        {"_id": 0}
    ).limit(10))
    
    return {"products": products, "count": len(products)}

@app.get("/convert")
def convert(product_id: int = Query(..., gt=0, description="Product ID")):
    """
    Convert product price from USD to EUR using live exchange rate
    """
    product = collection.find_one({"ProductID": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    try:
        # Use exchangerate-api for currency conversion
        response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
        rates = response.json()
        eur_rate = rates['rates']['EUR']
        
        price_in_eur = round(product['UnitPrice'] * eur_rate, 2)
        
        return {
            "ProductID": product_id,
            "Name": product['Name'],
            "PriceUSD": product['UnitPrice'],
            "PriceEUR": price_in_eur,
            "ExchangeRate": eur_rate
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching exchange rate: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
