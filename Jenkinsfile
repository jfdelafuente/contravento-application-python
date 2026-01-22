pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub_id')
    }

    stages {
        stage('Git Checkout') {
            steps {
                git branch: 'develop', url: 'https://github.com/jfdelafuente/contravento-application-python.git'
                echo 'Git Checkout Completed'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t jfdelafuente/contravento:latest -f backend/Dockerfile backend/'
                echo 'Build Image Completed'
            }
        }

        stage('Login to Docker Hub') {
            steps {
                sh 'echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin'
                echo 'Login Completed'
            }
        }

        stage('Push Image to Docker Hub') {
            steps {
                sh 'docker push jfdelafuente/contravento:latest'
                echo 'Push Image Completed'
            }
        }
    }

    post {
        always {
            sh 'docker logout'
        }
    }
}
