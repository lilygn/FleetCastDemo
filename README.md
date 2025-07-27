# FleetCast

A Satellite Operations Simulator deployed via Helm.

---

## Installation

### 1. Add the Helm Chart Repository

```bash
helm repo add fleetcast https://lilygn.github.io/FleetCast
helm repo update
```

### 2. Install the Chart

```bash
helm install satellite-app fleetcast/satellite-app -f values.secret.yaml
```

> ⚠️ Make sure your `values.secret.yaml` includes valid TiDB credentials (host, user, password, database).

---

## Accessing FleetCast via `orbital.local`

To access the app at `http://orbital.local`, you need to map the domain to your cluster's ingress IP.

### Option 1: Modify your local hosts file

#### Step 1: Get the External IP of the ingress controller

```bash
kubectl get svc -n ingress-nginx
```

Find the `EXTERNAL-IP` of the `ingress-nginx-controller` service.

#### Step 2: Edit your hosts file

**On macOS/Linux:**

```bash
sudo nano /etc/hosts
```

**On Windows:**
Edit this file in Notepad as administrator:

```
C:\Windows\System32\drivers\etc\hosts
```

#### Step 3: Add this line (replace `<EXTERNAL-IP>`):

```
<EXTERNAL-IP>    orbital.local
```

---

Now open your browser and visit:

```
http://orbital.local
```

FleetCast should be running!

##  Using the App with TiDB Credentials

This app is configured to use a shared TiDB Cloud database managed by the project author.

Please request a secure copy of the `values.secret.yaml` file containing the required credentials.

Then run:

```bash
helm install satellite-app fleetcast/satellite-app -f values.secret.yaml
