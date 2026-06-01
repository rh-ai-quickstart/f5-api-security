# Deploy F5 Distributed Cloud on OpenShift

## Objective

Integrate **F5 Distributed Cloud (XC) Mesh** with a **Red Hat OpenShift Container Platform (OCP)** cluster by deploying the **F5 XC site as pods** directly within the cluster.
This deployment method automatically discovers services running in the OCP cluster by querying the **kube-API** for services.

---

## Prerequisites

This deployment supports Mesh functionalities and was validated on the following environment:

| Requirement | Example configuration | Notes |
|---|---|---|
| **OCP Node** | `<your-ocp-node>` (control-plane, master, worker, worker-hp roles) | Single-node or multi-node |
| **Kubernetes Version** | `v1.31.6` (OCP 4.18+) | |
| **Minimum Resources** | 4 vCPUs and 8 GB memory per node | |
| **StorageClass (Dynamic PVC)** | `lvms-vg1 (default)` | Dynamic PVC must be enabled |

---

## Step 1: OCP environment configuration

This step ensures the OCP environment meets the **kernel and storage requirements** for the F5 XC pod deployment.

### 1.1 Verify OpenShift cluster readiness

Check the cluster state:

```bash
oc get nodes
```

Example output:

```
NAME              STATUS   ROLES                                    AGE   VERSION
<your-ocp-node>   Ready    control-plane,master,worker,worker-hp   221d  v1.31.6
```

Check for any failed pods:

```bash
oc get pod -A | egrep -vi 'Running|Completed'
```

> No pending or failed pods should be present before proceeding.

---

### 1.2 Enable kernel HugePages

HugePages must be configured when deploying Mesh as OCP pods.

**Steps:**

1. **Label the node:**
   Assign a custom role `worker-hp` to the target node.

   ```bash
   oc label node <your-ocp-node> node-role.kubernetes.io/worker-hp=
   ```

2. **Apply Tuned and MachineConfigPool (MCP):**

   `hugepages-tuned-boottime.yaml`:

   ```yaml
   apiVersion: tuned.openshift.io/v1
   kind: Tuned
   metadata:
     name: hugepages
     namespace: openshift-cluster-node-tuning-operator
   spec:
     profile:
     - data: |
         [main]
         summary=Boot time configuration for hugepages
         include=openshift-node
         [bootloader]
         cmdline_openshift_node_hugepages=hugepagesz=2M hugepages=1792
       name: openshift-node-hugepages

     recommend:
     - machineConfigLabels:
         machineconfiguration.openshift.io/role: "worker-hp"
       priority: 30
       profile: openshift-node-hugepages
   ```

   `hugepages-mcp.yaml`:

   ```yaml
   apiVersion: machineconfiguration.openshift.io/v1
   kind: MachineConfigPool
   metadata:
     name: worker-hp
     labels:
       worker-hp: ""
   spec:
     machineConfigSelector:
       matchExpressions:
         - {key: machineconfiguration.openshift.io/role, operator: In, values: [worker,worker-hp]}
     nodeSelector:
       matchLabels:
         node-role.kubernetes.io/worker-hp: ""
   ```

3. **Verify:** Confirm HugePages allocation on the labeled node.

---

### 1.3 Validate StorageClass and PVC functionality

Ensure a StorageClass with **dynamic persistent volume provisioner** is available:

```bash
oc get sc
```

Example output:

```
NAME              PROVISIONER                  RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
localblock-sc     kubernetes.io/no-provisioner Delete          WaitForFirstConsumer   false                  221d
lvms-vg1 (default) topolvm.io                  Delete          WaitForFirstConsumer   true                   221d
```

> The presence of `(default)` on a StorageClass confirms dynamic PVC provisioning is enabled.

---

## Step 2: Deploy Cloud Mesh pod

This step deploys the F5 XC site using the **CE on K8s** manifest file.

### 2.1 Download manifest

Download from GitLab:
[volterra-ce GitLab Repository](https://gitlab.com/volterra.io/volterra-ce/-/raw/master/k8s/ce_k8s.yml)

---

### 2.2 Update manifest for your environment

For a single-site deployment, customize the manifest for your cluster.
The standard manifest includes optional **NodePort definitions** for multi-cluster configurations, which can be safely **commented out or removed**.

Key fields to update:

```diff
-    ClusterName: <cluster name>
+    ClusterName: <your-site-name>

-    Latitude: <latitude>
+    Latitude: <your-latitude>

-    Longitude: <longitude>
+    Longitude: <your-longitude>

-    Token: <token>
+    Token: <your-site-token>
```

> Generate a site token from the F5 XC Console under **Multi-Cloud Network Connect → Manage → Site Management → Site Tokens**.

---

### 2.3 Apply deployment

```bash
oc create -f <your-manifest>.yml
```

Example output:

```
namespace/ves-system created
serviceaccount/volterra-sa created
role.rbac.authorization.k8s.io/volterra-admin-role created
rolebinding.rbac.authorization.k8s.io/volterra-admin-role-binding created
daemonset.apps/volterra-ce-init created
serviceaccount/vpm-sa created
role.rbac.authorization.k8s.io/vpm-role created
clusterrole.rbac.authorization.k8s.io/vpm-cluster-role created
rolebinding.rbac.authorization.k8s.io/vpm-role-binding created
clusterrolebinding.rbac.authorization.k8s.io/vpm-sa created
clusterrolebinding.rbac.authorization.k8s.io/ver created
configmap/vpm-cfg created
statefulset.apps/vp-manager created
service/vpm created
```

### Verify PVC binding

```bash
oc -n ves-system get pvc
```
```
NAME                     STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
data-vp-manager-0        Bound    pvc-48a97ea0-deaa-425d-9349-a92525865c1b   1Gi        RWO            lvms-vg1       40s
etcvpm-vp-manager-0      Bound    pvc-8f5d12cd-d648-4c50-ac3f-a356f69a3694   1Gi        RWO            lvms-vg1       40s
varvpm-vp-manager-0      Bound    pvc-7f89642f-c304-4ee3-b797-042304c58eef   1Gi        RWO            lvms-vg1       40s
```

---

### 2.4 Approve site registration

**Automatic (default):** When `make f5-deploy` runs with `f5xc_auto_approve: true` (default), the Ansible role calls the F5 XC Console API to approve the pending registration and waits until the site state is **ONLINE**. Configure these in `deploy/ansible/group_vars/all/secrets.yml`:

| Variable | Source |
|----------|--------|
| `f5xc_api_token` | Console → **Administration → Credentials → API Token** (required) |
| `f5xc_cluster_name` | Must match the CE site name (same as manual flow) |
| `f5xc_tenant` | Optional override for tenant subdomain (auto-discovered if omitted) |

Tenant discovery (when `f5xc_tenant` is not set): probes `https://console.ves.volterra.io` with your API token (follows redirects), then JWT claims, then optional `F5XC_TENANT` env var.

Verify the API token (after tenant is known or set):

```bash
TENANT="<your-tenant>"   # optional if using global console probe
curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: APIToken <your-api-token>" \
  "https://${TENANT}.console.ves.volterra.io/api/register/namespaces/system/registrations"
# Expected: 200
```

**Manual:** Set `f5xc_auto_approve: false` in `deploy/ansible/group_vars/all/vars.yml`, then log into the F5 XC Console to accept the site registration.

After deployment, monitor F5 XC pods:

```bash
oc -n ves-system get pod -o wide
```

Example output (initial state — some pods may show `CrashLoopBackOff` or `PodInitializing`):

```
NAME                          READY   STATUS             RESTARTS   AGE   IP             NODE
etcd-0                        2/2     Running            0          3m    10.128.1.254   <your-ocp-node>
prometheus-5c79db4978-tx7st   4/5     CrashLoopBackOff   4          3m    10.128.0.5     <your-ocp-node>
ver-0                         0/17    PodInitializing    0          3m    10.128.0.10    <your-ocp-node>
volterra-ce-init-rsj65        1/1     Running            0          6m    192.170.3.130  <your-ocp-node>
vp-manager-0                  1/1     Running            2          5m    10.128.1.252   <your-ocp-node>
```

### Troubleshooting: Prometheus HostPort issue

If Prometheus enters `CrashLoopBackOff`, it may be caused by **hostPort bindings** conflicting with OpenShift network policy.

Inspect the deployment:

```bash
oc get deployment prometheus -n ves-system -o yaml | egrep -n 'hostNetwork|hostPort|containerPort'
```

Offending configuration:

```yaml
- containerPort: 65210
  hostPort: 65210
- containerPort: 65211
  hostPort: 65211
- containerPort: 65220
  hostPort: 65220
- containerPort: 65221
  hostPort: 65221
```

**Remediation:** Remove the `hostPort` lines:

```bash
oc -n ves-system edit deploy/prometheus
```

Resulting configuration:

```yaml
- containerPort: 65210
  protocol: TCP
- containerPort: 65211
  protocol: TCP
- containerPort: 65220
  protocol: TCP
- containerPort: 65221
  protocol: TCP
```

---

### Final running status

Once registration is approved and Prometheus is fixed, all pods should be `Running`:

```bash
oc get pod -n ves-system -o wide
```

```
NAME                          READY   STATUS    RESTARTS   AGE   IP             NODE
etcd-0                        2/2     Running   0          45m   10.128.1.214   <your-ocp-node>
prometheus-57df68c9dd-qnbtn   5/5     Running   0          72s   10.128.1.237   <your-ocp-node>
ver-0                         17/17   Running   0          45m   10.128.1.216   <your-ocp-node>
volterra-ce-init-jm8tb        1/1     Running   0          48m   192.170.3.130  <your-ocp-node>
vp-manager-0                  1/1     Running   3          47m   10.128.1.212   <your-ocp-node>
```

---

## Step 3: Deploy application on OpenShift

With the F5 XC site operational, deploy your application. The example below uses the **Hipster Shop** demo app, but you can substitute your own workload (e.g., the RAG/LLM stack from this quickstart).

### 3.1 Install the application

1. **Create namespace:**

   ```bash
   oc new-project <your-namespace>
   ```

2. **Deploy the application:**

   ```bash
   oc create -f <your-app-manifest>.yaml -n <your-namespace>
   ```

3. Since Mesh runs inside OCP, services can use type `ClusterIP`.

4. **Verify pod status:** Ensure all pods reach `Running` state.

   ```bash
   oc get pod -n <your-namespace>
   ```

---

## Step 4: Advertise services

Since the F5 XC site runs as pods, **service discovery is automatic** via the kube-API.
Services are advertised using **Origin Pools** and **HTTP Load Balancers** in the F5 XC Console.

### 4.1 Create Origin Pool

1. In F5 XC Console → **Multi-Cloud App Connect**
2. Select your namespace (e.g., `<your-namespace>`)
3. Navigate to **Manage → Load Balancers → Origin Pools**
4. Click **Add Origin Pool**
5. Select **K8s Service Name of Origin Server on given Sites**
6. Enter `<service-name>.<your-namespace>` (e.g., `frontend.<your-namespace>`)
7. Choose the deployed Mesh site
8. Select **Outside Network**
9. Click **Save and Exit**

![F5 XC Origin Pool configuration showing K8s service as origin server](images/hipster-origin-pool.png)

---

### 4.2 Create HTTP Load Balancer

1. Go to **Manage → Load Balancers → HTTP Load Balancers**
2. Provide a descriptive name in **Metadata**
3. Under **Basic Configuration**, enter the domain name
4. Under **Default Origin Servers**, reference the Origin Pool from Step 4.1
5. Click **Save and Exit**

![F5 XC HTTP Load Balancer configuration with origin pool attached](images/hipster-lb.png)

---

### 4.3 Verify application accessibility

After the load balancer deployment:

- Application pods appear as origin servers under the **Origin Servers** tab
- Application is accessible via the configured domain name

![Application accessible through F5 XC load balancer showing healthy origin servers](images/hipster-app.png)
