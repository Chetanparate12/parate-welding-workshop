# Railway Deployment Guide for Parate Welding Workshop Bill Generation System

This guide will walk you through the steps to deploy the Parate Welding Workshop bill generation system on Railway, a modern platform for deploying web applications.

## Prerequisites

1. A [Railway](https://railway.app/) account
2. Your bill generation system code in a GitHub repository (or you can deploy directly from this Replit)

## Step 1: Prepare Your Project

Your project is already set up with the necessary files for Railway deployment:

- `Procfile` - Tells Railway how to run your application
- `runtime.txt` - Specifies the Python version
- `docker-compose.yml` (optional) - For Docker-based deployment
- `Dockerfile` (optional) - For Docker-based deployment

## Step 2: Set Up Your Railway Project

### Option 1: Deploy from GitHub

1. Go to [Railway Dashboard](https://railway.app/) and log in
2. Click on "New Project"
3. Select "Deploy from GitHub repo"
4. Select the repository containing your code
5. Railway will automatically detect your `Procfile` and deploy your app

### Option 2: Deploy from Replit

1. Go to [Railway Dashboard](https://railway.app/) and log in
2. Click on "New Project"
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account and select the repository you've pushed this code to
5. Railway will automatically deploy your app

### Option 3: Deploy with Railway CLI

1. Install the Railway CLI:
   ```
   npm install -g @railway/cli
   ```
2. Login to Railway:
   ```
   railway login
   ```
3. Link your project:
   ```
   railway link
   ```
4. Deploy your app:
   ```
   railway up
   ```

## Step 3: Configure Environment Variables

Set the following environment variables in your Railway project settings:

1. `DATABASE_URL`: Railway will automatically set this if you add a PostgreSQL plugin
2. `SESSION_SECRET`: Generate a strong random string for session security
3. `PDF_STORAGE_PATH`: Path for storing generated PDFs (usually `/app/generated_pdfs`)
4. `FLASK_ENV`: Set to `production`

## Step 4: Add a PostgreSQL Database (Recommended)

1. In your Railway project dashboard, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically connect your app to this database

## Step 5: Add a Persistent Volume for PDF Storage

1. Add the Railway Volume plugin to your project for persistent storage
2. Configure the volume mount path to match your `PDF_STORAGE_PATH` environment variable

## Step 6: Verify Deployment

1. After deployment completes, Railway will provide a URL for your application
2. Visit the URL to ensure your application is working correctly
3. Test creating and viewing bills to verify everything is working

## Step 7: Configure Custom Domain (Optional)

1. Go to your Railway project settings
2. Click on "Domains"
3. Add your custom domain and follow the instructions to set up DNS records

## Troubleshooting

### PDF Generation Issues

- Check that the volume for PDF storage is properly configured
- Verify that the `PDF_STORAGE_PATH` environment variable is set correctly
- Check application logs for any path-related errors

### Database Connection Issues

- Verify your `DATABASE_URL` environment variable
- Check if your PostgreSQL instance is running
- Ensure your application has access to the database

### Application Errors

- View logs in the Railway dashboard for error messages
- Check if all required environment variables are set
- Verify that the application works locally before deployment

## Maintenance

- Railway automatically rebuilds your application when you push changes to your connected GitHub repository
- To update your application, simply push changes to your repository
- Monitor resource usage in the Railway dashboard to ensure your application has adequate resources

## Backup Strategy

- Regularly backup your PostgreSQL database using Railway's backup features
- Consider implementing additional backup methods for critical PDF files

---

For any further assistance, refer to the [Railway documentation](https://docs.railway.app/) or contact the Railway support team.