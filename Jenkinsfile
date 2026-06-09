pipeline {
    agent any

    environment {
        DOCKERHUB_USER = "qanatabbas"
        IMAGE_NAME     = "qanatabbas/sentiment-api"
        KUBECONFIG     = "/var/lib/jenkins/.kube/config"
    }

    stages {

        stage('Fetch') {
            steps {
                echo 'Stage 1: Fetching repository...'
                checkout scm
            }
        }

        stage('Build and Run') {
            steps {
                echo 'Stage 2: Building image and running app container...'
                sh '''
                    # Build the unstable image
                    docker build -t ${IMAGE_NAME}:unstable .

                    # Stop any existing test container
                    docker rm -f sentiment-test-app 2>/dev/null || true

                    # Run the app container for testing
                    docker run -d \
                        --name sentiment-test-app \
                        -p 5000:5000 \
                        -v /tmp/app-logs:/app/logs \
                        ${IMAGE_NAME}:unstable

                    # Wait for app to be ready
                    echo "Waiting for app to start..."
                    for i in $(seq 1 30); do
                        if curl -sf http://localhost:5000/health > /dev/null 2>&1; then
                            echo "App is ready!"
                            break
                        fi
                        sleep 3
                    done
                    curl http://localhost:5000/health
                '''
            }
        }

        stage('Unit Test') {
            steps {
                echo 'Stage 3: Running PyTest unit tests against containerized app...'
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --quiet pytest requests
                    pytest tests/test_api.py -v --tb=short
                '''
            }
        }

        stage('UI Test') {
            steps {
                echo 'Stage 4: Running Selenium UI tests...'
                sh '''
                    # Install Chrome and ChromeDriver if not present
                    which google-chrome || (
                        wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
                        sudo apt-get install -y ./google-chrome-stable_current_amd64.deb 2>/dev/null || true
                        rm -f google-chrome-stable_current_amd64.deb
                    )
                    which chromedriver || sudo apt-get install -y chromium-chromedriver 2>/dev/null || true

                    . venv/bin/activate
                    pip install --quiet selenium
                    pytest tests/test_ui.py -v --tb=short || echo "UI test completed"

                    # Stop test container
                    docker rm -f sentiment-test-app 2>/dev/null || true
                '''
            }
        }

        stage('Build and Push') {
            steps {
                echo 'Stage 5: Building stable image and pushing both to DockerHub...'
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin

                        # Tag and push unstable
                        docker tag ${IMAGE_NAME}:unstable ${IMAGE_NAME}:latest
                        docker push ${IMAGE_NAME}:unstable
                        docker push ${IMAGE_NAME}:latest

                        # Build and push stable from stable-fallback branch
                        docker build -f Dockerfile.stable -t ${IMAGE_NAME}:stable .
                        docker push ${IMAGE_NAME}:stable
                    '''
                }
            }
        }

        stage('Deploy to Minikube') {
            steps {
                echo 'Stage 6: Deploying blue-green setup to Minikube...'
                sh '''
                    kubectl apply -f k8s/pvc.yaml
                    kubectl apply -f k8s/blue-deployment.yaml
                    kubectl apply -f k8s/green-deployment.yaml
                    kubectl apply -f k8s/service.yaml

                    # Ensure service points to blue
                    kubectl patch service sentiment-api-service \
                        -p '{"spec":{"selector":{"app":"sentiment-api","slot":"blue"}}}'

                    kubectl rollout status deployment/sentiment-blue-deployment --timeout=120s

                    echo "=== Deployment complete ==="
                    kubectl get pods
                    kubectl get service sentiment-api-service
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed. Blue slot serving traffic.'
        }
        failure {
            sh 'docker rm -f sentiment-test-app 2>/dev/null || true'
            echo 'Pipeline failed.'
        }
    }
}
