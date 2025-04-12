pipeline {
    agent any

    environment {
        VENV_DIR = "venv"
    }

    stages {
        stage('Clone Repository') {
            steps {
                git 'https://github.com/Mo-anas/LLMS.git'
            }
        }

        stage('Set Up Python Environment') {
            steps {
                sh 'python3 -m venv $VENV_DIR'
                sh '. $VENV_DIR/bin/activate && pip install --upgrade pip'
                sh '. $VENV_DIR/bin/activate && pip install -r requirements.txt'
            }
        }

        stage('Run Flask App (Optional)') {
            steps {
                echo 'Running Flask app for testing...'
                sh '''
                . $VENV_DIR/bin/activate
                export FLASK_APP=app.py
                flask run --host=0.0.0.0 --port=5000 &
                sleep 5
                '''
            }
        }

        stage('Clean Up') {
            steps {
                echo 'Cleaning up...'
                sh 'pkill flask || true'
            }
        }
    }

    post {
        success {
            echo '✅ CI pipeline completed successfully!'
        }
        failure {
            echo '❌ Pipeline failed. Please check the logs.'
        }
    }
}
