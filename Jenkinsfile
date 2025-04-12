pipeline {
    agent any

    environment {
        IMAGE_NAME = "language-membership-system"
        CONTAINER_NAME = "language-membership-system-container"
        DOCKER_REGISTRY = "your-dockerhub-username"
    }

    stages {
        stage('Checkout Code') {
            steps {
                echo 'Checking out code from repository...'
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                script {
                    sh "docker build -t ${IMAGE_NAME} ."
                }
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running tests...'
                script {
                    // Run the container in detached mode for testing
                    sh "docker run -d --name ${CONTAINER_NAME} ${IMAGE_NAME}"
                    
                    // Add your test commands here (e.g., curl or pytest)
                    sh "curl -f http://localhost:5000 || exit 1"
                    
                    // Stop the container after tests
                    sh "docker stop ${CONTAINER_NAME}"
                    sh "docker rm ${CONTAINER_NAME}"
                }
            }
        }

        stage('Push to Docker Registry') {
            steps {
                echo 'Pushing Docker image to registry...'
                script {
                    sh "docker tag ${IMAGE_NAME} ${DOCKER_REGISTRY}/${IMAGE_NAME}"
                    sh "docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}"
                }
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying application...'
                script {
                    // Stop and remove any existing container
                    sh "docker stop ${CONTAINER_NAME} || true"
                    sh "docker rm ${CONTAINER_NAME} || true"
                    
                    // Run the new container
                    sh "docker run -d -p 5000:5000 --name ${CONTAINER_NAME} ${DOCKER_REGISTRY}/${IMAGE_NAME}"
                }
            }
        }
    }

    post {
        always {
            echo 'Cleaning up workspace...'
            cleanWs()
        }
    }
}