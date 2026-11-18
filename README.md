# Serverless Kolkata Weather Data Pipeline (AWS)

An automated, event-driven serverless data ingestion pipeline built on AWS that fetches real-time and hourly forecast metrics for Kolkata from the Open-Meteo API and persists structured JSON datasets into Amazon S3 using Hive-style date partitioning.

## Architecture

```text
+--------------------+     rate(1 hour)     +------------------------------+
| Amazon EventBridge | -------------------> |         AWS Lambda           |
| (Scheduled Rule)   |                      |  (kolkata-weather-ingestion) |
+--------------------+                      +--------------+---------------+
                                                           |
                                              IAM Least-Privilege Role
                                              (s3:PutObject only)
                                                           |
                                                           v
                                            +------------------------------+
                                            |          Amazon S3           |
                                            | subhayan-kolkata-weather-2026|
                                            |  ├── latest_weather.json     |
                                            |  └── history/YYYY/MM/DD/...  |
                                            +------------------------------+
```

## Key Engineering & Security Highlights
- **Dual-Write S3 Ingestion:** Updates `latest_weather.json` for real-time consumption while writing immutable, timestamped records (`history/YYYY/MM/DD/HH-MM.json`) for historical time-series analysis.
- **Least-Privilege IAM Security:** The Lambda execution role (`KolkataWeatherLambdaRole`) is scoped strictly to `s3:PutObject` on `arn:aws:s3:::subhayan-kolkata-weather-2026/*` alongside basic CloudWatch logging (`trust-policy.json` & `s3-write-policy.json`).
- **Serverless Scheduling & Observability:** Automated via Amazon EventBridge (`rate(1 hour)`) in `ap-southeast-2` and monitored through Amazon CloudWatch Logs.

## Repository Structure
- `fetch_weather.py` — Core ingestion script supporting both local CLI execution and AWS Lambda (`lambda_handler`).
- `requirements.txt` — Python dependencies (`requests`, `boto3`).
- `trust-policy.json` — IAM assume-role policy for AWS Lambda.
- `s3-write-policy.json` — Least-privilege inline S3 write policy.
-