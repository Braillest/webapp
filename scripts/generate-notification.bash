#!/bin/bash

URL="http://localhost:3000/send-notification"

# Send the POST request
curl -X POST "$URL" -H "Content-Type: application/json"
