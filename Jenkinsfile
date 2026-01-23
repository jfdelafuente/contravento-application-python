// ============================================================================
// ContraVento - Jenkins Pipeline (Simplified)
// ============================================================================
// Pipeline simplificado para build y push de imágenes Docker
//
// Stages:
//   1. Build Docker Images (parallel) - Construye backend + frontend
//   2. Push to Docker Hub - Sube imágenes a Docker Hub
//
// Note: Git checkout is automatic (done by Jenkins SCM)
//
// Prerequisites (Jenkins Credentials):
//   - dockerhub_id: Docker Hub credentials (username + password)
//   - vite_api_url: Frontend API URL (secret text)
//   - vite_turnstile_site_key: Cloudflare Turnstile site key (secret text)
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
    }

    options {
        // Keep only last 10 builds
        buildDiscarder(logRotator(numToKeepStr: '10'))

        // Timeout after 20 minutes
        timeout(time: 20, unit: 'MINUTES')

        // Don't run concurrent builds
        disableConcurrentBuilds()
    }

    stages {
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
    }

    post {
        success {
            echo '========================================='
            echo '✅ Pipeline Completed Successfully!'
            echo '========================================='
            echo "Backend Image: ${BACKEND_IMAGE}"
            echo "Frontend Image: ${FRONTEND_IMAGE}"
            echo '========================================='
        }

        failure {
            echo '========================================='
            echo '❌ Pipeline Failed!'
            echo '========================================='
        }

        always {
            echo 'Cleaning up...'
            // Logout from Docker Hub
            sh 'docker logout || true'
            echo 'Cleanup completed'
        }
    }
}
