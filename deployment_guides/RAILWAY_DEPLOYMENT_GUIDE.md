# Railway Deployment Guide for Parate Welding Workshop Bill Generator

This guide provides step-by-step instructions for deploying the Parate Welding Workshop bill generation system to Railway.

## Prerequisites

1. A Railway account (you can sign up at [Railway.app](https://railway.app/))
2. GitHub account with the project repository

## Step 1: Prepare your GitHub repository

Ensure your project repository includes these files:

- `Dockerfile` - Already configured for Railway deployment
- `Procfile` - Contains the command to run the application
- `railway_requirements.txt` - Lists all the Python dependencies
- `docker-compose.yml` - (Optional) For local testing with Docker

## Step 2: Deploy on Railway

### Using the Railway Dashboard

1. Log in to your Railway dashboard at [https://railway.app/dashboard](https://railway.app/dashboard)
2. Click on "New Project"
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account if not already connected
5. Select the repository containing the bill generator project
6. Railway will automatically detect the Dockerfile and use it for deployment

### Using the Railway CLI (Alternative Method)

If you prefer using the CLI:

1. Install the Railway CLI:
   ```
   npm i -g @railway/cli
   ```

2. Log in to Railway:
   ```
   railway login
   ```

3. Link to your project (or create a new one):
   ```
   railway link
   ```

4. Deploy your application:
   ```
   railway up
   ```

## Step 3: Add a PostgreSQL Database

1. In your Railway project dashboard, click on "New"
2. Select "Database" → "PostgreSQL"
3. Wait for the database to provision (typically takes a few minutes)

## Step 4: Configure Environment Variables

Add the following environment variables in your Railway project settings:

| Variable | Value | Description |
|----------|-------|-------------|
| `SESSION_SECRET` | *random string* | Secret key for session management (generate a random string) |
| `FLASK_ENV` | `production` | Set the environment to production mode |
| `PDF_STORAGE_PATH` | `/app/generated_pdfs` | Path where PDF files will be stored |
| `RAILWAY_ENVIRONMENT` | `1` | Flag to indicate Railway deployment |

Note: Railway automatically adds the `DATABASE_URL` environment variable when you add a PostgreSQL database.

## Step 5: Deploy and Monitor

1. After configuring environment variables, Railway will automatically redeploy your application
2. Monitor the deployment logs in the Railway dashboard
3. Once deployment is complete, click on the generated domain URL to access your application

## Step 6: Verify Functionality

1. Open the application URL provided by Railway
2. Create a test bill to verify that bill generation works
3. Verify that the PDF generation works
4. Check that payment tracking and history are working correctly

## Important Notes

1. **Data Migration**: If you're migrating from a local SQLite database, you may need to manually export and import your data.

2. **Persistent Storage**: Railway manages file storage through the container filesystem. For long-term storage, consider using cloud storage solutions.

3. **Database Backups**: Set up regular database backups through the Railway dashboard.

4. **Monitoring**: Railway provides basic monitoring. For more advanced monitoring, consider adding tools like Sentry.

5. **Custom Domain**: To use a custom domain:
   - Go to your project settings in the Railway dashboard
   - Click on "Domains"
   - Add your custom domain and follow the DNS configuration instructions

## Troubleshooting

1. **Database Connection Issues**:
   - Verify that the `DATABASE_URL` environment variable is set correctly
   - Check if PostgreSQL service is running

2. **PDF Generation Errors**:
   - Verify that the `PDF_STORAGE_PATH` is correctly set and writable
   - Check application logs for any file permission issues

3. **Application Crashes**:
   - Review logs in the Railway dashboard
   - Ensure all required environment variables are set

For further assistance, refer to Railway documentation at [docs.railway.app](https://docs.railway.app/).