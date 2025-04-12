pipeline {
    agent any

    environment {
        IMAGE_NAME = "llms_app"
        CONTAINER_NAME = "llms_container"
    }

    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'main', url: 'https://github.com/Mo-anas/LLMS.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "🔧 Building Docker image..."
                    sh 'docker build -t $IMAGE_NAME .'
                }
            }
        }

        stage('Stop Existing Container (If Running)') {
            steps {
                script {
                    sh """
                        docker ps -q --filter name=$CONTAINER_NAME | grep -q . && docker stop $CONTAINER_NAME && docker rm $CONTAINER_NAME || echo "No existing container to stop."
                    """
                }
            }
        }

        stage('Run Docker Container') {
            steps {
                script {
                    echo "🚀 Running the app in Docker..."
                    sh 'docker run -d --name $CONTAINER_NAME -p 5000:5000 $IMAGE_NAME'
                }
            }
        }
    }

    post {
        success {
            echo "✅ Deployment successful. Your Flask app should be running on port 5000."
        }
        failure {
            echo "❌ Pipeline failed. Please check the logs."
        }
    }
}
