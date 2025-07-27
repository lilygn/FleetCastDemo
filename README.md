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

## Accessing FleetCast via `orbital.local:8080`

To access the app at `http://orbital.local:8080`, you need to map the domain to your cluster's ingress IP.

#### Port forward to expose ingress controller on a local port

```bash
kubectl port-forward -n ingress-nginx service/ingress-nginx-controller 8080:80
```


---

Now open your browser and visit:

```
http://orbital.local:8080
```

FleetCast should be running!

##  Using the App with TiDB Credentials

This app is configured to use a shared TiDB Cloud database managed by the project author.

Please request a secure copy of the `values.secret.yaml` file containing the required credentials.

Then run:

```bash
helm install satellite-app fleetcast/satellite-app -f values.secret.yaml
