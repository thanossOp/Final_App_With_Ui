#!/bin/bash
# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt
# Install dependencies for frontend
echo "Installing frontend dependencies..."
npm install
# Start frontend
echo "Starting frontend..."
npm run start &
# Change directory to server
echo "Changing directory to server..."
cd server
# Install dependencies for server
echo "Installing server dependencies..."
npm install
# Start server
echo "Starting server..."
node server.js