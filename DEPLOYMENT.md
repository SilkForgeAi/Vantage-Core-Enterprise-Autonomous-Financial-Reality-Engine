# Production Deployment Guide

Complete guide for deploying Vantage Core to production environments.

## Table of Contents

1. [Kubernetes Deployment](#kubernetes-deployment)
2. [AWS EKS Deployment](#aws-eks-deployment)
3. [Google Cloud GKE Deployment](#google-cloud-gke-deployment)
4. [Azure AKS Deployment](#azure-aks-deployment)
5. [Docker Compose Production](#docker-compose-production)
6. [Health Checks & Monitoring](#health-checks--monitoring)
7. [Backup & Recovery](#backup--recovery)
8. [Security Considerations](#security-considerations)

---

## Kubernetes Deployment

See [k8s/README.md](k8s/README.md) for complete Kubernetes deployment instructions.

**Quick Deploy:**
```bash
kubectl apply -f k8s/
```

---

## AWS EKS Deployment

### Prerequisites

- AWS CLI configured
- `eksctl` or `kubectl` with EKS access
- EKS cluster (1.24+)

### Step 1: Create EKS Cluster

```bash
eksctl create cluster \
  --name vantage-core-cluster \
  --version 1.28 \
  --region us-east-1 \
  --nodegroup-name workers \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 3 \
  --nodes-max 10 \
  --managed
```

### Step 2: Configure Storage

```bash
# Create EBS storage class (default)
kubectl apply -f - <<EOF
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ebs-sc
provisioner: ebs.csi.aws.com
volumeBindingMode: WaitForFirstConsumer
EOF
```

Update `k8s/pvc.yaml` to use `storageClassName: ebs-sc`.

### Step 3: Store Secrets in AWS Secrets Manager

```bash
# Store secrets
aws secretsmanager create-secret \
  --name vantage-core/production \
  --secret-string file://.env.production

# Create External Secrets Operator (recommended) or use IAM roles
```

### Step 4: Deploy Application

```bash
kubectl apply -f k8s/
```

### Step 5: Set Up Load Balancer

```bash
# Update service.yaml to use LoadBalancer type
kubectl patch service vantage-core-agent -n vantage-core -p '{"spec":{"type":"LoadBalancer"}}'
```

### Step 6: Configure Auto-Scaling

Auto-scaling is configured via HPA. For cluster autoscaling:
```bash
eksctl create cluster \
  --with-oidc \
  --install-cluster-autoscaler
```

### Monitoring

- **CloudWatch**: Metrics available at `/metrics` endpoint
- **X-Ray**: Add AWS X-Ray SDK for distributed tracing
- **CloudWatch Logs**: Configure Fluent Bit for log aggregation

---

## Google Cloud GKE Deployment

### Prerequisites

- `gcloud` CLI configured
- GKE cluster (1.24+)

### Step 1: Create GKE Cluster

```bash
gcloud container clusters create vantage-core-cluster \
  --zone us-central1-a \
  --machine-type e2-medium \
  --num-nodes 3 \
  --enable-autoscaling \
  --min-nodes 3 \
  --max-nodes 10 \
  --enable-autorepair \
  --enable-autoupgrade
```

### Step 2: Configure Storage

GKE uses `standard` storage class by default. Update `k8s/pvc.yaml`:
```yaml
storageClassName: standard  # GKE default
```

For high-performance, use `premium-rwo`:
```yaml
storageClassName: premium-rwo
```

### Step 3: Store Secrets in Secret Manager

```bash
# Store secrets
gcloud secrets create vantage-core-secrets --data-file=.env.production

# Grant access to GKE service account
gcloud secrets add-iam-policy-binding vantage-core-secrets \
  --member="serviceAccount:PROJECT_ID.svc.id.goog[vantage-core/default]" \
  --role="roles/secretmanager.secretAccessor"
```

### Step 4: Deploy Application

```bash
gcloud container clusters get-credentials vantage-core-cluster --zone us-central1-a
kubectl apply -f k8s/
```

### Step 5: Set Up Ingress

```bash
# Enable GKE Ingress
kubectl apply -f k8s/service.yaml

# Get Ingress IP
kubectl get ingress -n vantage-core
```

### Monitoring

- **Cloud Monitoring**: Use `/metrics` endpoint with Prometheus
- **Cloud Logging**: Automatic log aggregation
- **Cloud Trace**: Add OpenTelemetry for distributed tracing

---

## Azure AKS Deployment

### Prerequisites

- `az` CLI configured
- AKS cluster (1.24+)

### Step 1: Create AKS Cluster

```bash
az aks create \
  --resource-group vantage-core-rg \
  --name vantage-core-cluster \
  --node-count 3 \
  --enable-cluster-autoscaler \
  --min-count 3 \
  --max-count 10 \
  --node-vm-size Standard_B2s \
  --enable-addons monitoring
```

### Step 2: Configure Storage

AKS uses `default` storage class (Azure Disk). Update `k8s/pvc.yaml`:
```yaml
storageClassName: default  # Azure Disk
```

For premium storage:
```yaml
storageClassName: managed-premium
```

### Step 3: Store Secrets in Key Vault

```bash
# Create Key Vault
az keyvault create --name vantage-core-kv --resource-group vantage-core-rg

# Store secrets
az keyvault secret set --vault-name vantage-core-kv --name "vantage-core-secrets" --file .env.production

# Use Azure Key Vault Provider for Secrets Store CSI Driver
```

### Step 4: Deploy Application

```bash
az aks get-credentials --resource-group vantage-core-rg --name vantage-core-cluster
kubectl apply -f k8s/
```

### Step 5: Set Up Application Gateway Ingress

```bash
# Enable AGIC (Application Gateway Ingress Controller)
az aks enable-addons --resource-group vantage-core-rg --name vantage-core-cluster --addons ingress-appgw --appgw-name vantage-core-appgw
```

### Monitoring

- **Azure Monitor**: Metrics from `/metrics` endpoint
- **Application Insights**: Add OpenTelemetry SDK
- **Log Analytics**: Automatic log aggregation

---

## Docker Compose Production

For single-host or Docker Swarm deployments:

```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Scale agents (Docker Swarm)
docker service scale vantage-core-agent=3
```

**Requirements:**
- Docker 20.10+
- Docker Compose 2.0+
- 4GB+ RAM
- 100GB+ disk space

---

## Health Checks & Monitoring

### Health Endpoints

- **Liveness**: `GET /health/live` - Kubernetes liveness probe
- **Readiness**: `GET /health/ready` - Kubernetes readiness probe
- **Full Health**: `GET /health` - Comprehensive health check
- **Metrics**: `GET /metrics` - Prometheus metrics
- **Stats**: `GET /api/stats` - Application statistics

### Prometheus Configuration

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'vantage-core'
    kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
            - vantage-core
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
```

### Grafana Dashboard

Key metrics to monitor:
- Request rate and latency
- Error rates
- Redis connection status
- ChromaDB status
- Active users
- Trade execution metrics
- System resources (CPU, memory)

---

## Backup & Recovery

### Redis Backup

```bash
# Manual backup
kubectl exec -it vantage-redis-0 -n vantage-core -- redis-cli BGSAVE

# Automated backup (CronJob)
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: CronJob
metadata:
  name: redis-backup
  namespace: vantage-core
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: redis:7-alpine
            command:
            - sh
            - -c
            - redis-cli -h vantage-redis BGSAVE && sleep 5 && cp /data/dump.rdb /backup/dump-\$(date +%Y%m%d).rdb
            volumeMounts:
            - name: redis-data
              mountPath: /data
            - name: backup-storage
              mountPath: /backup
          volumes:
          - name: redis-data
            persistentVolumeClaim:
              claimName: redis-data
          - name: backup-storage
            persistentVolumeClaim:
              claimName: redis-backup
          restartPolicy: OnFailure
EOF
```

### ChromaDB Backup

ChromaDB data is stored in persistent volume. Backup the PVC:

```bash
# AWS EBS snapshot
aws ec2 create-snapshot --volume-id <volume-id>

# GCP snapshot
gcloud compute disks snapshot <disk-name> --zone=<zone> --snapshot-names=vantage-chroma-$(date +%Y%m%d)

# Azure snapshot
az snapshot create --resource-group vantage-core-rg --source <disk-name> --name vantage-chroma-$(date +%Y%m%d)
```

### Audit Logs Backup

Audit logs are stored in persistent volume. Same backup strategy as ChromaDB.

### Recovery Procedures

1. **Redis Recovery**: Restore from backup snapshot
2. **ChromaDB Recovery**: Restore PVC from snapshot
3. **Full System Recovery**: Restore all PVCs and redeploy

---

## Security Considerations

### Secrets Management

**DO NOT** commit secrets to Git. Use:
- Kubernetes Secrets (basic)
- AWS Secrets Manager / Parameter Store (AWS)
- Google Secret Manager (GCP)
- Azure Key Vault (Azure)
- HashiCorp Vault (self-hosted)

### Network Security

- Use NetworkPolicies to restrict pod-to-pod communication
- Enable TLS for all external connections
- Use Ingress with TLS termination
- Restrict Redis to internal network only

### Container Security

- Run containers as non-root user (configured in deployment.yaml)
- Use minimal base images
- Regularly update base images
- Scan images for vulnerabilities (Trivy, Clair)

### API Security

- Rate limiting enabled (Redis-based)
- Input validation on all endpoints
- Structured error responses (no information leakage)
- API key encryption at rest

### Compliance

- All actions are logged (audit logs)
- Complete execution trails
- Encryption for sensitive data
- Per-user data isolation

---

## Performance Tuning

### Resource Limits

Adjust based on load:
- **Light load**: 512Mi memory, 0.25 CPU
- **Medium load**: 1Gi memory, 0.5 CPU (default)
- **Heavy load**: 4Gi memory, 2 CPU

### Redis Optimization

- Enable persistence (appendonly)
- Configure maxmemory and eviction policy
- Use Redis Cluster for high availability

### Scaling

- Horizontal Pod Autoscaler (HPA) for auto-scaling
- Cluster autoscaler for node scaling
- Load balancing across pods

---

## Troubleshooting

### Pods Not Starting

```bash
kubectl describe pod <pod-name> -n vantage-core
kubectl logs <pod-name> -n vantage-core
```

### Redis Connection Issues

```bash
kubectl exec -it vantage-redis-0 -n vantage-core -- redis-cli ping
```

### Health Check Failures

```bash
kubectl exec -it <pod-name> -n vantage-core -- curl http://localhost:8000/health
```

### Performance Issues

Check metrics:
```bash
kubectl top pods -n vantage-core
kubectl get hpa -n vantage-core
```

