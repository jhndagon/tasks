pipeline {
    agent { label 'jenkins-jenkins-agent' }

    environment {
        DOCKER_REGISTRY = 'docker.io'
        DOCKER_IMAGE = 'jhndagon11/tasks'
        DOCKER_CREDENTIALS_ID = 'dockerhub-credentials'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Clonar repositorio') {
            steps {
                checkout scm
            }
        }

        stage('Construir imagen Docker') {
            steps {
                container('docker') {
                    sh 'docker build -t ${DOCKER_IMAGE}:${IMAGE_TAG} -t ${DOCKER_IMAGE}:latest .'
                }
            }
        }

        stage('Publicar imagen en registro') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: "${DOCKER_CREDENTIALS_ID}",
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {
                    container('docker') {
                        sh '''
                            echo "$DOCKER_PASSWORD" | docker login "$DOCKER_REGISTRY" \
                                --username "$DOCKER_USERNAME" \
                                --password-stdin

                            docker push "${DOCKER_IMAGE}:${IMAGE_TAG}"
                            docker push "${DOCKER_IMAGE}:latest"
                        '''
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                container('docker') {
                    sh 'docker logout ${DOCKER_REGISTRY} || true'
                }
            }
        }
        success {
            echo "Imagen publicada: ${DOCKER_IMAGE}:${IMAGE_TAG}"
        }
    }
}
