import csv
import json
from pymongo import MongoClient

def load_csv_to_mongo():
    """
    Load product data from CSV file into MongoDB database
    """
    # Connect to MongoDB (local instance)
    client = MongoClient('mongodb+srv://shadowblader333_db_user:qwerty123@cluster0.f1z6erc.mongodb.net/?appName=Cluster0')
    db = client['inventory_db']
    collection = db['products']
    
    # Clear existing data
    collection.delete_many({})
    
    # Read CSV and insert into MongoDB
    products = []
    with open('products.csv', 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            product = {
                'ProductID': int(row['ProductID']),
                'Name': row['Name'],
                'UnitPrice': float(row['UnitPrice']),
                'StockQuantity': int(row['StockQuantity']),
                'Description': row['Description']
            }
            products.append(product)
    
    # Insert all products
    if products:
        collection.insert_many(products)
        print(f"Successfully loaded {len(products)} products into MongoDB")
    else:
        print("No products found in CSV file")
    
    client.close()

if __name__ == "__main__":
    load_csv_to_mongo()
