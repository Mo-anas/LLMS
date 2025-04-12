pipeline {
    agent any

    stages {
        stage('Clone Repository') {
            steps {
                git 'https://github.com/Mo-anas/LLMS.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo '🔧 Building Docker image...'
                sh 'docker build -t llms_app .'
            }
        }

        stage('Stop Existing Container (If Running)') {
            steps {
                script {
                    sh 'docker stop llms_container || true'
                    sh 'docker rm llms_container || true'
                }
            }
        }

        stage('Run Docker Container') {
            steps {
                echo '🚀 Running Docker container...'
                sh 'docker run -d -p 5000:5000 --name llms_container llms_app'
            }
        }
    }

    post {
        failure {
            echo '❌ Pipeline failed. Please check the logs.'
        }
        success {
            echo '✅ Pipeline completed successfully!'
        }
    }
}
