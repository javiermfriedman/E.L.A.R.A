#!/bin/bash
set -e

if [ -z "$LOCAL_SERVER_URL" ]; then
  echo "LOCAL_SERVER_URL not set — attempting to discover from ngrok..."

  NGROK_API="http://ngrok:4040/api/tunnels"
  MAX_RETRIES=30
  RETRY_INTERVAL=2

  for i in $(seq 1 $MAX_RETRIES); do
    NGROK_URL=$(curl -s "$NGROK_API" 2>/dev/null | python3 -c "
import sys, json
try:
    tunnels = json.load(sys.stdin).get('tunnels', [])
    url = next((t['public_url'] for t in tunnels if t['public_url'].startswith('https')), '')
    print(url)
except Exception:
    pass
" 2>/dev/null)

    if [ -n "$NGROK_URL" ]; then
      export LOCAL_SERVER_URL="$NGROK_URL"
      echo "Discovered ngrok URL: $LOCAL_SERVER_URL"
      break
    fi

    echo "Waiting for ngrok... ($i/$MAX_RETRIES)"
    sleep $RETRY_INTERVAL
  done

  if [ -z "$LOCAL_SERVER_URL" ]; then
    echo "WARNING: Could not discover ngrok URL after ${MAX_RETRIES} attempts."
    echo "Twilio calls will fail until LOCAL_SERVER_URL is configured."
  fi
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 "$@"
