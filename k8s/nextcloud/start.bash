minikube delete
minikube start

kubectl create -f pg_secret.yaml
kubectl create -f pg_configmap.yaml
kubectl create -f pg_deployment.yaml
kubectl create -f pg_service.yaml
kubectl create -f nc_secret.yaml
kubectl create -f nc_configmap.yaml
kubectl create -f nc_deployment.yaml

kubectl get pods -w

kubectl expose deployment nextcloud --type=NodePort --port=80

minikube service nextcloud