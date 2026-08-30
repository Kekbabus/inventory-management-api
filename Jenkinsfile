pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = "inventory-api"
        CONTAINER_NAME = "inventory-api-container"
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Pulling code from GitHub...'
                checkout scm
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                script {
                    bat "docker build -t ${DOCKER_IMAGE} ."
                }
            }
        }
        
        stage('Run Container') {
            steps {
                echo 'Starting Docker container...'
                script {
                    // Stop and remove existing container if it exists
                    bat "docker stop ${CONTAINER_NAME} || exit 0"
                    bat "docker rm ${CONTAINER_NAME} || exit 0"
                    
                    // Run new container in detached mode
                    bat "docker run -d -p 8000:8000 --name ${CONTAINER_NAME} ${DOCKER_IMAGE}"
                    
                    // Wait for container to be ready
                    sleep(time: 10, unit: 'SECONDS')
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                echo 'Running unit tests...'
                script {
                    bat "docker exec ${CONTAINER_NAME} python3 -m pytest test_api.py -v"
                }
            }
        }
        
        stage('Run Newman Tests') {
            steps {
                echo 'Running Postman/Newman tests...'
                script {
                    // If you have Postman collection, run it here
                    echo 'Newman tests would run here if collection exists'
                }
            }
        }
        
        stage('Generate README') {
            steps {
                echo 'Generating README documentation...'
                script {
                    def readmeContent = """
INVENTORY MANAGEMENT API - DOCUMENTATION
=========================================

Base URL: http://localhost:8000

API ENDPOINTS:
--------------

1. GET /
   Description: Welcome endpoint
   Parameters: None
   
2. GET /getSingleProduct
   Description: Get a single product by ID
   Parameters: product_id (integer, required) - The product ID
   Example: /getSingleProduct?product_id=1
   
3. GET /getAll
   Description: Get all products from inventory
   Parameters: None
   
4. POST /addNew
   Description: Add a new product to inventory
   Body (JSON):
   {
     "Name": "string",
     "UnitPrice": float,
     "StockQuantity": integer,
     "Description": "string"
   }
   
5. DELETE /deleteOne
   Description: Delete a product by ID
   Parameters: product_id (integer, required) - The product ID to delete
   Example: /deleteOne?product_id=5
   
6. GET /startsWith
   Description: Get all products starting with a specific letter
   Parameters: letter (string, required) - Single letter
   Example: /startsWith?letter=M
   
7. GET /paginate
   Description: Get products in batches of 10 between start and end IDs
   Parameters: 
     - start_id (integer, required) - Starting product ID
     - end_id (integer, required) - Ending product ID
   Example: /paginate?start_id=1&end_id=10
   
8. GET /convert
   Description: Convert product price from USD to EUR
   Parameters: product_id (integer, required) - The product ID
   Example: /convert?product_id=1

FASTAPI DOCUMENTATION:
----------------------
Interactive API Docs: http://localhost:8000/docs
Alternative Docs: http://localhost:8000/redoc

Generated: ${new Date().format('yyyy-MM-dd HH:mm:ss')}
"""
                    writeFile file: 'README.txt', text: readmeContent
                }
            }
        }
        
        stage('Create Release Package') {
            steps {
                echo 'Creating release zip file...'
                script {
                    def timestamp = new Date().format('yyyyMMdd-HHmmss')
                    def zipFilename = "complete-${timestamp}.zip"
                    
                    bat """
                        powershell -Command "Compress-Archive -Path main.py,requirements.txt,Dockerfile,test_api.py,csv_to_mongo.py,products.csv,README.txt -DestinationPath ${zipFilename} -Force"
                    """
                    
                    echo "Created ${zipFilename}"
                }
            }
        }
        
        stage('Cleanup') {
            steps {
                echo 'Stopping Docker container...'
                script {
                    bat "docker stop ${CONTAINER_NAME} || exit 0"
                    bat "docker rm ${CONTAINER_NAME} || exit 0"
                }
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline completed!'
        }
        success {
            echo 'Build succeeded!'
        }
        failure {
            echo 'Build failed!'
        }
    }
}
