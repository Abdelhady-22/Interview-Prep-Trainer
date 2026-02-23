# Kubernetes (K8S) Plan for Interview Prep Trainer

## What is Kubernetes?

Kubernetes is a container orchestration platform that automates deploying, scaling, and managing containerized applications. Since your app is already containerized with Docker Compose (4 services), K8S is the natural next step for production-grade deployment.

---

## Architecture Overview

### Current: Docker Compose

```
docker-compose.yml
├── Frontend     :3000
├── Backend      :8000
├── PostgreSQL   :5432
└── Ollama       :11434
```

### Next: Kubernetes Cluster

```
K8S Cluster
└── K8S Control Plane
    ├── Frontend Deployment  →  Frontend Service
    ├── Backend Deployment   →  Backend Service
    ├── PostgreSQL StatefulSet → DB Service
    ├── Ollama Deployment    →  Ollama Service
    └── Ingress Controller
```

---

## Why K8S Over Docker Compose?

| Feature | Docker Compose | Kubernetes |
|---|---|---|
| Auto-restart on crash | ✅ Basic | ✅ Advanced (health probes, rolling restarts) |
| Horizontal scaling | ❌ Manual | ✅ Auto-scale pods based on CPU/memory |
| Load balancing | ❌ None | ✅ Built-in service load balancing |
| Rolling updates | ❌ Downtime | ✅ Zero-downtime deployments |
| Secret management | ❌ .env files | ✅ Encrypted Secrets objects |
| Multi-node | ❌ Single host | ✅ Distributed across nodes |
| Self-healing | ❌ Limited | ✅ Automatic pod rescheduling |
| Resource limits | ⚠️ Basic | ✅ Fine-grained CPU/memory limits per pod |

---

## Cluster Layout

```
K8S Cluster on VM
└── Namespace: interview-prep
    ├── AI / LLM
    │   ├── Deployment: ollama (1 replica)
    │   ├── Service: ClusterIP :11434
    │   └── PersistentVolumeClaim: ollama-models (20Gi)
    ├── Database
    │   ├── StatefulSet: postgres (1 replica)
    │   ├── Service: ClusterIP :5432
    │   └── PersistentVolumeClaim: postgres-data (10Gi)
    ├── Backend
    │   ├── Deployment: backend (2 replicas)
    │   └── Service: ClusterIP :8000
    ├── Frontend
    │   ├── Deployment: frontend (2 replicas)
    │   └── Service: ClusterIP :3000
    ├── Ingress: prep.example.com
    ├── ConfigMap: app-config
    └── Secret: db-credentials
```

---

## K8S Resource Mapping (Docker Compose → K8S)

Each Docker Compose service maps to K8S resources:

| Docker Compose Service | K8S Resource | Why |
|---|---|---|
| `frontend` | Deployment + Service | Stateless, can scale horizontally |
| `backend` | Deployment + Service | Stateless, can scale horizontally |
| `db` (PostgreSQL) | StatefulSet + PVC + Service | Stateful, needs persistent storage |
| `ollama` | Deployment + PVC + Service | Needs GPU/large storage for models |
| `.env` variables | ConfigMap + Secret | Centralized, encrypted config |
| `app-network` | Namespace + K8S DNS | Built-in service discovery (`backend.interview-prep.svc.cluster.local`) |
| Port mappings | Ingress | External routing with TLS |

---

## Step-by-Step Deployment Plan

### Phase 1: Set Up the K8S Cluster on a VM

> **IMPORTANT:** You need a Linux VM with at least **4 vCPUs, 8GB RAM, 50GB disk** (more for Ollama with larger models).

**Option A — Single-node with K3s (recommended for simplicity):**

```bash
# SSH into your VM
curl -sfL https://get.k3s.io | sh -

# Verify
kubectl get nodes
```

**Option B — Multi-node with kubeadm:**

```bash
# On master node
sudo kubeadm init --pod-network-cidr=10.244.0.0/16
kubectl apply -f https://raw.githubusercontent.com/flannel-io/flannel/master/Documentation/kube-flannel.yml

# On worker nodes
sudo kubeadm join <master-ip>:6443 --token <token> --discovery-token-ca-cert-hash <hash>
```

**Option C — Managed cloud (easiest):**

GKE (Google), EKS (AWS), AKS (Azure) — managed control plane, no infrastructure burden.

---

### Phase 2: Create K8S Manifest Files

You'll need these files in a new `k8s/` directory:

```
k8s/
├── namespace.yaml
├── configmap.yaml
├── secret.yaml
├── frontend/
│   ├── deployment.yaml
│   └── service.yaml
├── backend/
│   ├── deployment.yaml
│   └── service.yaml
├── postgres/
│   ├── statefulset.yaml
│   ├── service.yaml
│   └── pvc.yaml
├── ollama/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── pvc.yaml
└── ingress.yaml
```

#### Namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: interview-prep
```

#### Secret (DB credentials)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
  namespace: interview-prep
type: Opaque
stringData:
  POSTGRES_USER: grader
  POSTGRES_PASSWORD: graderpass
  POSTGRES_DB: examgrader
  DATABASE_URL: postgresql://grader:graderpass@postgres:5432/examgrader
```

#### ConfigMap (app config)

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: interview-prep
data:
  OLLAMA_BASE_URL: "http://ollama:11434"
  OLLAMA_MODEL: "qwen2.5:0.5b"
  MAX_RETRIES: "3"
  GRADING_MODE: "single"
  DEFAULT_EXAM_QUESTIONS: "5"
  VITE_API_URL: "http://backend:8000"
```

#### Backend Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: interview-prep
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
        - name: backend
          image: interview-prep-backend:latest
          ports:
            - containerPort: 8000
          envFrom:
            - configMapRef:
                name: app-config
            - secretRef:
                name: db-credentials
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 15
          resources:
            requests:
              cpu: "250m"
              memory: "256Mi"
            limits:
              cpu: "500m"
              memory: "512Mi"
```

#### Backend Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: interview-prep
spec:
  selector:
    app: backend
  ports:
    - port: 8000
      targetPort: 8000
  type: ClusterIP
```

#### PostgreSQL StatefulSet

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: interview-prep
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:16-alpine
          ports:
            - containerPort: 5432
          envFrom:
            - secretRef:
                name: db-credentials
          volumeMounts:
            - name: postgres-data
              mountPath: /var/lib/postgresql/data
          readinessProbe:
            exec:
              command: ["pg_isready", "-U", "grader", "-d", "examgrader"]
            initialDelaySeconds: 5
            periodSeconds: 5
          resources:
            requests:
              cpu: "250m"
              memory: "256Mi"
            limits:
              cpu: "500m"
              memory: "512Mi"
  volumeClaimTemplates:
    - metadata:
        name: postgres-data
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 10Gi
```

#### Ingress (external access)

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: interview-prep-ingress
  namespace: interview-prep
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
    - host: prep.yourdomain.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend
                port:
                  number: 3000
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: backend
                port:
                  number: 8000
```

---

### Phase 3: Build & Push Images

```bash
# Build images
docker build -t interview-prep-frontend:latest ./frontend
docker build -t interview-prep-backend:latest ./backend

# If using a private registry
docker tag interview-prep-frontend:latest your-registry.com/interview-prep-frontend:latest
docker push your-registry.com/interview-prep-frontend:latest

docker tag interview-prep-backend:latest your-registry.com/interview-prep-backend:latest
docker push your-registry.com/interview-prep-backend:latest
```

---

### Phase 4: Deploy to the Cluster

```bash
# Apply all manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/postgres/
kubectl apply -f k8s/ollama/
kubectl apply -f k8s/backend/
kubectl apply -f k8s/frontend/
kubectl apply -f k8s/ingress.yaml

# Verify everything is running
kubectl get all -n interview-prep
```

---

### Phase 5: Scaling & Auto-Scaling

```bash
# Manual scale
kubectl scale deployment backend --replicas=3 -n interview-prep

# Auto-scale based on CPU (requires metrics-server)
kubectl autoscale deployment backend \
  --cpu-percent=70 \
  --min=2 --max=5 \
  -n interview-prep
```

**HorizontalPodAutoscaler manifest:**

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: interview-prep
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 5
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

---

## VM Cluster Setup Options

| Approach | Nodes | Complexity | Best For |
|---|---|---|---|
| K3s (single VM) | 1 | ⭐ Low | Development, small-scale |
| K3s (multi-VM) | 2–3 VMs | ⭐⭐ Medium | Small production |
| kubeadm | 3+ VMs | ⭐⭐⭐ High | Full control, learning |
| Managed (GKE/EKS/AKS) | Auto | ⭐ Low | Production, no infra burden |

### Recommended VM Specs

| Node Role | vCPUs | RAM | Disk | Purpose |
|---|---|---|---|---|
| Master | 2 | 4 GB | 30 GB | Control plane |
| Worker 1 | 2 | 4 GB | 30 GB | Frontend + Backend pods |
| Worker 2 | 4 | 8 GB | 50 GB | Ollama + PostgreSQL pods |

> **TIP:** For Ollama with larger models (e.g., `qwen2.5:7b`), allocate a dedicated worker node with 16GB+ RAM and optionally a GPU.

---

## Day-to-Day Operations

```bash
# View pods
kubectl get pods -n interview-prep

# View logs
kubectl logs -f deployment/backend -n interview-prep

# Enter a pod shell
kubectl exec -it <pod-name> -n interview-prep -- /bin/bash

# Rolling update (after new image push)
kubectl rollout restart deployment/backend -n interview-prep

# Check rollout status
kubectl rollout status deployment/backend -n interview-prep

# Rollback to previous version
kubectl rollout undo deployment/backend -n interview-prep
```

---

## Summary — What Changes From Today

| Area | Current (Docker Compose) | After (Kubernetes) |
|---|---|---|
| Start command | `docker compose up` | `kubectl apply -f k8s/` |
| Config | `.env` file | ConfigMap + Secret |
| Networking | `app-network` bridge | K8S DNS + Ingress |
| Storage | Docker volumes | PersistentVolumeClaims |
| Scaling | Manual container restart | HPA auto-scaling |
| Monitoring | Docker logs | Prometheus + Grafana (optional) |
| Deployment | Rebuild & restart | Rolling updates, zero downtime |

> **NOTE:** Your existing Docker Compose setup remains valid for local development. K8S is for staging/production environments.