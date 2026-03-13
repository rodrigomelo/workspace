#!/bin/bash
cd /Users/rodrigomelo/.openclaw/workspace/projects/cli-task-manager/web

# Start the web server
npm start &
SERVER_PID=$!

# Wait for server to be ready
sleep 2

# Start ngrok
ngrok http 3000 &
NGROK_PID=$!

# Keep running
wait
