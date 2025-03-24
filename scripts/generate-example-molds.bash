#!/bin/bash

URL="https://localhost:8000/generate"

# Send the POST request
curl -X POST "$URL" -H "Content-Type: application/json" --insecure
