@echo off
rem Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt
rem Install dependencies for frontend
echo Installing frontend dependencies...
npm install
rem Start frontend
echo Starting frontend...
start npm run start
rem Change directory to server
echo Changing directory to server...
cd server
rem Install dependencies for server
echo Installing server dependencies...
npm install
rem Start server
echo Starting server...
node server.js
