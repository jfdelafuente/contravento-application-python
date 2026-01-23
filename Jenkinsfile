// ============================================================================
// ContraVento - Jenkins Pipeline
// ============================================================================
// Pipeline for building, testing, and deploying ContraVento application
//
// Prerequisites (Jenkins Credentials):
//   - dockerhub_id: Docker Hub credentials (username + password)
//   - vite_api_url: Frontend API URL (e.g., http://localhost:8000)
//   - vite_turnstile_site_key: Cloudflare Turnstile site key
//
// Stages:
//   1. Git Checkout - Clone repository
//   2. Run Backend Tests - Execute pytest suite
//   3. Build Images - Build backend and frontend Docker images
//   4. Push to Docker Hub - Push images to registry
//   5. Deploy to Preproduction - Deploy using docker-compose.preproduction.yml
//   6. Validate Deployment - Run smoke tests
//   7. Cleanup - Remove containers and logout
// ============================================================================

pipeline {
    agent any

    environment {
        // Docker Hub credentials
        DOCKERHUB_CREDENTIALS = credentials('dockerhub_id')

        // Frontend build arguments
        VITE_API_URL = credentials('vite_api_url')
        VITE_TURNSTILE_SITE_KEY = credentials('vite_turnstile_site_key')

        // Docker image names
        BACKEND_IMAGE = 'jfdelafuente/contravento-backend:latest'
        FRONTEND_IMAGE = 'jfdelafuente/contravento-frontend:latest'

        // Compose file
        COMPOSE_FILE = 'docker-compose.preproduction.yml'
    }

    options {
        // Keep only last 10 builds
        buildDiscarder(logRotator(numToKeepStr: '10'))

        // Timeout after 30 minutes
        timeout(time: 30, unit: 'MINUTES')

        // Don't run concurrent builds
        disableConcurrentBuilds()
    }

    stages {
        stage('Git Checkout') {
            steps {
                echo '========================================='
                echo 'Stage: Git Checkout'
                echo '========================================='

                git branch: 'develop',
                    url: 'https://github.com/jfdelafuente/contravento-application-python.git'

                // Display current commit
                sh 'git log -1 --oneline'

                echo '✅ Git Checkout Completed'
            }
        }

        stage('Run Backend Tests') {
            steps {
                echo '========================================='
                echo 'Stage: Run Backend Tests'
                echo '========================================='

                dir('backend') {
                    // Install dependencies and run tests
                    sh '''
                        # Install Poetry if not available
                        if ! command -v poetry &> /dev/null; then
                            pip install poetry
                        fi

                        # Install dependencies
                        poetry install

                        # Run tests with coverage
                        poetry run pytest --cov=src --cov-report=term --cov-report=html -v
                    '''
                }

                echo '✅ Backend Tests Passed'
            }
        }

        stage('Build Docker Images') {
            parallel {
                stage('Build Backend Image') {
                    steps {
                        echo '========================================='
                        echo 'Stage: Build Backend Image'
                        echo '========================================='

                        sh """
                            docker build -t ${BACKEND_IMAGE} \
                              -f backend/Dockerfile \
                              backend/
                        """

                        echo '✅ Backend Image Build Completed'
                    }
                }

                stage('Build Frontend Image') {
                    steps {
                        echo '========================================='
                        echo 'Stage: Build Frontend Image'
                        echo '========================================='

                        sh """
                            docker build -t ${FRONTEND_IMAGE} \
                              --build-arg VITE_API_URL=${VITE_API_URL} \
                              --build-arg VITE_TURNSTILE_SITE_KEY=${VITE_TURNSTILE_SITE_KEY} \
                              --build-arg VITE_ENV=production \
                              --build-arg VITE_DEBUG=false \
                              -f frontend/Dockerfile.prod \
                              frontend/
                        """

                        echo '✅ Frontend Image Build Completed'
                    }
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                echo '========================================='
                echo 'Stage: Push to Docker Hub'
                echo '========================================='

                script {
                    // Login to Docker Hub
                    sh 'echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin'

                    // Push backend image
                    sh """
                        docker push ${BACKEND_IMAGE}
                        echo '✅ Backend Image Pushed'
                    """

                    // Push frontend image
                    sh """
                        docker push ${FRONTEND_IMAGE}
                        echo '✅ Frontend Image Pushed'
                    """
                }

                echo '✅ All Images Pushed to Docker Hub'
            }
        }

        stage('Deploy to Preproduction') {
            steps {
                echo '========================================='
                echo 'Stage: Deploy to Preproduction'
                echo '========================================='

                script {
                    // Stop any existing containers
                    sh """
                        docker-compose -f ${COMPOSE_FILE} down -v || true
                        echo 'Stopped existing containers'
                    """

                    // Pull latest images
                    sh """
                        docker-compose -f ${COMPOSE_FILE} pull
                        echo 'Pulled latest images'
                    """

                    // Start services
                    sh """
                        docker-compose -f ${COMPOSE_FILE} up -d
                        echo 'Started preproduction environment'
                    """

                    // Wait for services to be healthy
                    sh """
                        echo 'Waiting for services to be healthy...'
                        sleep 30
                        docker-compose -f ${COMPOSE_FILE} ps
                    """
                }

                echo '✅ Preproduction Deployment Completed'
            }
        }

        stage('Validate Deployment') {
            steps {
                echo '========================================='
                echo 'Stage: Validate Deployment'
                echo '========================================='

                script {
                    // Check backend health
                    sh '''
                        echo 'Checking backend health endpoint...'
                        for i in {1..10}; do
                            if curl -f http://localhost:8000/health; then
                                echo '✅ Backend is healthy'
                                break
                            else
                                echo "Attempt $i/10 failed, retrying in 5s..."
                                sleep 5
                            fi
                        done
                    '''

                    // Check frontend
                    sh '''
                        echo 'Checking frontend...'
                        if curl -f http://localhost:5173; then
                            echo '✅ Frontend is accessible'
                        else
                            echo '❌ Frontend is not accessible'
                            exit 1
                        fi
                    '''

                    // Display logs
                    sh """
                        echo 'Recent backend logs:'
                        docker-compose -f ${COMPOSE_FILE} logs --tail=50 backend
                    """
                }

                echo '✅ Deployment Validation Passed'
            }
        }
    }

    post {
        success {
            echo '========================================='
            echo '✅ Pipeline Completed Successfully!'
            echo '========================================='
            echo 'Access preproduction environment:'
            echo '  - Frontend: http://localhost:5173'
            echo '  - Backend API: http://localhost:8000'
            echo '  - API Docs: http://localhost:8000/docs'
            echo '  - pgAdmin: http://localhost:5050'
            echo '========================================='
        }

        failure {
            echo '========================================='
            echo '❌ Pipeline Failed!'
            echo '========================================='

            // Display logs for debugging
            sh """
                echo 'Backend logs:'
                docker-compose -f ${COMPOSE_FILE} logs --tail=100 backend || true

                echo 'Frontend logs:'
                docker-compose -f ${COMPOSE_FILE} logs --tail=100 frontend || true
            """
        }

        always {
            echo 'Cleaning up...'

            // Logout from Docker Hub
            sh 'docker logout || true'

            // Optional: Stop containers after build (comment out if you want to keep them running)
            // sh "docker-compose -f ${COMPOSE_FILE} down || true"

            echo 'Cleanup completed'
        }
    }
}
