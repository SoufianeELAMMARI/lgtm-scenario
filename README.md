# Local LGTM Observability Scenario

A complete observability stack that runs locally with **one `docker compose` command**.
It includes a small demo service that produces real telemetry so you have data to
explore the moment it starts.

## What's inside

| Component | Role |
|---|---|
| **lgtm** (`grafana/otel-lgtm`) | The whole backend in one container: Grafana + Loki (logs) + Tempo (traces) + Prometheus (metrics) + OpenTelemetry Collector. Persists to **one volume** (`/data`). |
| **app** (`demo-app`) | A small Flask service, auto-instrumented with OpenTelemetry. Emits traces, logs, and metrics. **~10% of `/rolldice` requests fail on purpose** so the SLO / error budget is meaningful. |
| **loadgen** | Sends continuous traffic to the app so dashboards fill up immediately. |

## Prerequisites

- Docker Desktop (Apple Silicon or Intel - images are multi-arch).
- Give Docker at least **4 GB RAM** (Docker Desktop → Settings → Resources).

## Run it

```bash
docker compose up -d --build
```

Then open Grafana: **http://localhost:3000** (no login required in this image).

It takes ~15–30s for the first telemetry to appear.

## What to look at (Grafana → Explore)

In Grafana, click **Explore** (compass icon) and switch the data source at the top.

**Logs - choose the `Loki` data source:**
```
{service_name="demo-app"}
```
You'll see the info / warning / error log lines coming from the app.

**Traces - choose the `Tempo` data source:**
- Use the **Search** tab, service name `demo-app`. Click any trace to see the spans.
- Slow ones (the `/slow` route) and failing ones (5xx) stand out.

**Metrics - choose the `Prometheus` data source:**
- Type `http_server` in the query box and let autocomplete show the exact metric
  names produced on your version (e.g. `http_server_request_duration_seconds_count`).

## Hit the app yourself

```bash
curl http://localhost:5001/rolldice
curl http://localhost:5001/slow
```

## The SLO angle (error budget)

The app fails ~10% of requests, so its real availability is ~90% - far below a 99.9%
target. That's intentional: it makes the error budget visibly burn.

First confirm the exact metric name in **Explore → Prometheus** (search `http_server`),
then an **availability SLI** (success ratio) looks like this - adjust the metric name
and the status-code label to match what you see:

```promql
# success ratio over the last 5 minutes
1 - (
  sum(rate(http_server_request_duration_seconds_count{http_response_status_code=~"5.."}[5m]))
  /
  sum(rate(http_server_request_duration_seconds_count[5m]))
)
```

Add it as a Grafana panel (Time series or Stat) to watch the SLI move.

> Want true SLO-as-code with multi-burn-rate alerts? Add **Sloth** to generate the
> Prometheus recording + alerting rules from a `PrometheusServiceLevel` spec. It's a
> separate step because this all-in-one image bundles its own Prometheus config.

## Stop / reset

```bash
docker compose down        # stop everything, KEEP the data volume
docker compose down -v      # stop AND wipe the volume (clean slate)
```

## Zero-build alternative (no demo app)

If you just want the backend with some synthetic data and no image build, drop the
`app` and `loadgen` services and generate telemetry with `telemetrygen`:

```bash
docker run --rm \
  ghcr.io/open-telemetry/opentelemetry-collector-contrib/telemetrygen:latest \
  traces --otlp-insecure --otlp-endpoint host.docker.internal:4317 --traces 50
```

## Notes

- This image is for **development, demo, and testing** - not production. For production,
  deploy the components separately (Helm charts: `loki-distributed`, `tempo-distributed`,
  `mimir-distributed`, plus Grafana).
- macOS uses port 5000 for AirPlay, so the app is published on **5001** to avoid a clash.
