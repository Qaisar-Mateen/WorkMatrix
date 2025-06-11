# WorkMatrix Background Service

This is the background monitoring service for WorkMatrix.

## Setup Instructions:

1. Configure the .env file with your Supabase credentials and desired settings
2. Ensure the following directory structure exists:
   - data/screenshots/ (for storing screenshots)
   - logs/ (for application logs)
   - config/ (for configuration files)

3. Start the application by running:
   workmatrix-background.exe

## Configuration:

Edit the .env file to customize:
- Screenshot interval
- Keystroke monitoring
- Sync frequency
- Storage limits
- WebSocket connection

## Troubleshooting:

Check the logs directory for:
- workmatrix.log (main application log)
- error.log (error messages)
- performance.log (performance metrics)