pipeline {
    agent any
    environment {
        DOCKER_PATH = '/usr/bin/docker'  // Add the correct path to your Docker installation
    }
    stages {
        stage('Build Docker Image') {
            steps {
                script {
                    sh '''#!/bin/bash
                    $DOCKER_PATH build -t llms_app .
                    '''
                }
            }
        }
    }
}
