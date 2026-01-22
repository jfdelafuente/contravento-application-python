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

        stage('Build Backend Docker Image') {
            steps {
                sh 'docker build -t jfdelafuente/contravento-backend:latest -f backend/Dockerfile backend/'
                echo 'Backend Image Build Completed'
            }
        }

        stage('Build Frontend Docker Image') {
            steps {
                sh '''
                    docker build -t jfdelafuente/contravento-frontend:latest \
                      --build-arg VITE_API_URL=https://api.contravento.com \
                      --build-arg VITE_TURNSTILE_SITE_KEY=1x00000000000000000000AA \
                      --build-arg VITE_ENV=production \
                      --build-arg VITE_DEBUG=false \
                      -f frontend/Dockerfile.prod frontend/
                '''
                echo 'Frontend Image Build Completed'
            }
        }

        stage('Login to Docker Hub') {
            steps {
                sh 'echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin'
                echo 'Login Completed'
            }
        }

        stage('Push Backend Image to Docker Hub') {
            steps {
                sh 'docker push jfdelafuente/contravento-backend:latest'
                echo 'Backend Image Push Completed'
            }
        }

        stage('Push Frontend Image to Docker Hub') {
            steps {
                sh 'docker push jfdelafuente/contravento-frontend:latest'
                echo 'Frontend Image Push Completed'
            }
        }
    }

    post {
        always {
            sh 'docker logout'
        }
    }
}
