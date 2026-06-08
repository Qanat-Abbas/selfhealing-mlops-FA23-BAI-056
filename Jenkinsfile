pipeline {
    agent any

    environment {
        DOCKERHUB_USER     = "qanatabbas"
        IMAGE_NAME         = "qanatabbas/sentiment-api"
        IMAGE_TAG_UNSTABLE = "unstable"
        KUBECONFIG         = "/var/lib/jenkins/.kube/config"
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Stage 1: Cloning repository from GitHub...'
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Stage 2: Installing Python dependencies...'
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --quiet -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Stage 3: Running PyTest API tests...'
                sh '''
                    . venv/bin/activate
                    pytest tests/test_api.py -v --tb=short
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Stage 4: Building Docker image...'
                sh '''
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG_UNSTABLE} .
                    docker tag ${IMAGE_NAME}:${IMAGE_TAG_UNSTABLE} ${IMAGE_NAME}:latest
                '''
            }
        }

        stage('Push to DockerHub') {
            steps {
                echo 'Stage 5: Pushing image to DockerHub...'
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker push ${IMAGE_NAME}:${IMAGE_TAG_UNSTABLE}
                        docker push ${IMAGE_NAME}:latest
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes - Blue Slot') {
            steps {
                echo 'Stage 6: Deploying to Minikube blue slot...'
                sh '''
                    # Copy minikube kubeconfig for Jenkins
                    mkdir -p /var/lib/jenkins/.kube
                    sudo cp /home/ubuntu/.kube/config /var/lib/jenkins/.kube/config
                    sudo chown jenkins:jenkins /var/lib/jenkins/.kube/config

                    # Apply all K8s manifests
                    kubectl apply -f k8s/pvc.yaml
                    kubectl apply -f k8s/blue-deployment.yaml
                    kubectl apply -f k8s/green-deployment.yaml
                    kubectl apply -f k8s/service.yaml

                    # Wait for blue deployment to be ready
                    kubectl rollout status deployment/sentiment-blue-deployment --timeout=120s

                    echo "Blue slot is live. Service pointing to: blue"
                    kubectl get service sentiment-service
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully. Blue slot is serving traffic.'
        }
        failure {
            echo 'Pipeline failed. Check logs above for details.'
        }
    }
}
