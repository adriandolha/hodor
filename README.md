# hodor
Authentication and authorization service based on AuthLib to generate JWTs.
It can be deployed and exposed as a service in Kubernetes. Currently, it supports postgres 
database. It's designed to share the database with the application that is using it.

## Exposed APIs:
* register & signin user
* social signin with google
* create, get, update, delete user
* get all users
* create, get, update, delete roles
* get all roles
* create, get, update, delete permissions
* get all permissions

## Hodor secrets example
<details>
  <summary>Secrets example for hodor </summary>

````
apiVersion: v1
kind: Secret
metadata:
  name: hodor
  namespace: dev
type: Opaque
stringData:
  aurora-host: "postgres-postgresql.dev.svc.cluster.local"
  aurora-database: "hodor"
  root-url: "http://hodor.dev.svc.cluster.local"
  aurora-user: "postgres"
  aurora-port: "5432"
  admin-user: admin
  admin-password: <admin_password>
  guest-user: guest
  guest-password: <guest_password>
  jwk-public-key-path: "/jwk/certs/public.key"
  jwk_private_key_path: "/jwk/certs/private.key"
  google-client-id: "<google_client_id>"
  google-client-secret: "<google_client_secret>"

````
</details>

## Usage
````
kubectl apply -f hodor-secrets.yaml 
kubectl -n hodor create secret generic jwk-certs --from-file=$HOME/.cloud-projects/oauth
./deploy_db.sh
./deploy.sh
````