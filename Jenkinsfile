pipeline {
    agent any

    environment {
        IMAGE_NAME = "language-membership-system"
        CONTAINER_NAME = "language-membership-system-container"
        DOCKER_REGISTRY = "moanas" // Change this to your actual DockerHub username
        DOCKER_PORT = "5000"
    }

    stages {
        stage('Verify Environment') {
            steps {
                echo '🔍 Checking Docker installation...'
                script {
                    // Check if Docker is installed and accessible
                    def dockerVersion = sh(script: 'docker --version', returnStatus: true)
                    if (dockerVersion != 0) {
                        error('Docker is not installed or not in PATH. Please configure Docker on the Jenkins agent.')
                    }
                    
                    // Verify docker-compose if needed
                    // def composeVersion = sh(script: 'docker-compose --version', returnStatus: true)
                    // if (composeVersion != 0) {
                    //     error('docker-compose is not installed or not in PATH.')
                    // }
                }
            }
        }

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
                    try {
                        sh "docker build -t ${IMAGE_NAME} ."
                    } catch (Exception e) {
                        error("Failed to build Docker image: ${e.message}")
                    }
                }
            }
        }

        stage('Run Tests') {
            steps {
                echo '🧪 Running tests on container...'
                script {
                    try {
                        // Run container with port mapping
                        sh "docker run -d -p ${DOCKER_PORT}:${DOCKER_PORT} --name ${CONTAINER_NAME} ${IMAGE_NAME}"
                        
                        // Wait for app to start with proper health check
                        def healthCheck = sh(script: """
                            for i in {1..10}; do
                                if curl -s -f http://localhost:${DOCKER_PORT}/health; then
                                    exit 0
                                fi
                                sleep 5
                            done
                            exit 1
                        """, returnStatus: true)
                        
                        if (healthCheck != 0) {
                            error("Application failed to start or health check failed")
                        }
                        
                        // Run actual tests (replace with your test commands)
                        sh "curl -f http://localhost:${DOCKER_PORT}/test-endpoint || exit 1"
                        
                    } finally {
                        // Clean up even if tests fail
                        sh "docker stop ${CONTAINER_NAME} || true"
                        sh "docker rm ${CONTAINER_NAME} || true"
                    }
                }
            }
        }

        stage('Push to Docker Registry') {
            when {
                // Only push to registry for main branch or tags
                anyOf {
                    branch 'main'
                    tag '*'
                }
            }
            steps {
                echo '🚀 Pushing Docker image to registry...'
                script {
                    withCredentials([usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )]) {
                        sh """
                            echo \$DOCKER_PASS | docker login -u \$DOCKER_USER --password-stdin
                            docker tag ${IMAGE_NAME} ${DOCKER_REGISTRY}/${IMAGE_NAME}:${env.BRANCH_NAME}
                            docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:${env.BRANCH_NAME}
                        """
                    }
                }
            }
        }

        stage('Deploy to Staging') {
            when {
                branch 'main'
            }
            steps {
                echo '🚀 Deploying to staging environment...'
                script {
                    try {
                        // Stop old container if exists
                        sh "docker stop ${CONTAINER_NAME}-staging || true"
                        sh "docker rm ${CONTAINER_NAME}-staging || true"

                        // Run updated container
                        sh """
                            docker run -d \
                                -p 5001:${DOCKER_PORT} \
                                --name ${CONTAINER_NAME}-staging \
                                ${DOCKER_REGISTRY}/${IMAGE_NAME}:${env.BRANCH_NAME}
                        """
                    } catch (Exception e) {
                        error("Deployment failed: ${e.message}")
                    }
                }
            }
        }
    }

    post {
        always {
            echo '🧹 Cleaning up...'
            script {
                // Clean up any running containers
                sh "docker stop ${CONTAINER_NAME} || true"
                sh "docker rm ${CONTAINER_NAME} || true"
                sh "docker stop ${CONTAINER_NAME}-staging || true"
                sh "docker rm ${CONTAINER_NAME}-staging || true"
            }
            cleanWs()
        }
        success {
            echo '✅ Pipeline completed successfully!'
        }
        failure {
            echo '❌ Pipeline failed!'
            // Optional: Send notification
            // emailext body: "Pipeline failed: ${env.BUILD_URL}",
            //            subject: "Pipeline Failed: ${env.JOB_NAME}",
            //            to: 'team@example.com'
        }
    }
}
