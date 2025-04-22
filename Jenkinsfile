pipeline {
    agent any

    environment {
        IMAGE_NAME = "language-membership-system"
        CONTAINER_NAME = "language-membership-system-container"
        DOCKER_REGISTRY = "moanas" // Your actual Docker Hub username
    }

    stages {
        stage('Checkout Code') {
            steps {
                echo '📦 Checking out code from repository...'
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                echo '🐳 Building Docker image...'
                script {
                    sh "docker build -t ${IMAGE_NAME} ."
                }
            }
        }

        stage('Run Tests') {
            steps {
                echo '🧪 Running tests on container...'
                script {
                    // Run container with port mapping
                    sh "docker run -d -p 5000:5000 --name ${CONTAINER_NAME} ${IMAGE_NAME}"

                    // Wait for app to start
                    sh "sleep 5"

                    // Test endpoint
                    sh "curl -f http://localhost:5000 || exit 1"

                    // Clean up
                    sh "docker stop ${CONTAINER_NAME}"
                    sh "docker rm ${CONTAINER_NAME}"
                }
            }
        }

        stage('Push to Docker Registry') {
            steps {
                echo '🚀 Pushing Docker image to registry...'
                script {
                    // Use Jenkins credentials for DockerHub login
                    withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                        sh "echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin"
                    }

                    // Tag and push image
                    sh "docker tag ${IMAGE_NAME} ${DOCKER_REGISTRY}/${IMAGE_NAME}"
                    sh "docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}"
                }
            }
        }

        stage('Deploy') {
            steps {
                echo '📤 Deploying application...'
                script {
                    // Stop old container if exists
                    sh "docker stop ${CONTAINER_NAME} || true"
                    sh "docker rm ${CONTAINER_NAME} || true"

                    // Run updated container
                    sh "docker run -d -p 5000:5000 --name ${CONTAINER_NAME} ${DOCKER_REGISTRY}/${IMAGE_NAME}"
                }
            }
        }
    }

    post {
        always {
            echo '🧹 Cleaning up workspace...'
            cleanWs()
        }
    }
}
