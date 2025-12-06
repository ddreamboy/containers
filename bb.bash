minikube start
minikube docker-env | Invoke-Expression
docker build -t habr-adapter-image:latest -f habr_adapter/Dockerfile.good habr_adapter/
kubectl apply -f k8s/habr_project/