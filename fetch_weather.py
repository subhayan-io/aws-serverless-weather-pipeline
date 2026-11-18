import json
from datetime import datetime, timezone
import requests
import boto3
BUCKET_NAME = "subhayan-kolkata-weather-2026"
REGION_NAME = "ap-southeast-2"
S3_KEY = "latest_weather.json"

def get_kolkata_weather():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 22.5726,
        "longitude": 88.3639,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "wind_speed_10m",
        ],
        "hourly": ["temperature_2m", "precipitation_probability"],
        "timezone": "Asia/Kolkata",
        "forecast_days": 1,
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    raw_data = response.json()

    return {
        "city": "Kolkata",
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
        "current": raw_data["current"],
        "units": raw_data["current_units"],
        "hourly_forecast": {
            "time": raw_data["hourly"]["time"],
            "temperature_2m": raw_data["hourly"]["temperature_2m"],
            "precipitation_probability": raw_data["hourly"][
                "precipitation_probability"
            ],
        },
    }


def upload_to_s3(data):
    s3_client = boto3.client("s3", region_name=REGION_NAME)
    payload = json.dumps(data, indent=2).encode("utf-8")

    # Generate date-partitioned archive key in UTC (e.g., history/2026/11/17/09-30.json)
    now_utc = datetime.now(timezone.utc)
    archive_key = now_utc.strftime("history/%Y/%m/%d/%H-%M.json")

    # 1. Overwrite latest snapshot for real-time dashboard consumption
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=S3_KEY,
        Body=payload,
        ContentType="application/json",
    )

    # 2. Write immutable timestamped archive for historical tracking
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=archive_key,
        Body=payload,
        ContentType="application/json",
    )

    print(f"Uploaded latest snapshot: s3://{BUCKET_NAME}/{S3_KEY}")
    print(f"Uploaded archive record:  s3://{BUCKET_NAME}/{archive_key}")
    return {"latest_key": S3_KEY, "archive_key": archive_key}


def lambda_handler(event, context):
    weather_data = get_kolkata_weather()
    result = upload_to_s3(weather_data)
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Kolkata weather pipeline executed successfully",
            "keys": result,
        }),
    }


if __name__ == "__main__":
    weather_data = get_kolkata_weather()
    upload_to_s3(weather_data)