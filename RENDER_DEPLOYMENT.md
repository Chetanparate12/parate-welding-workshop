# Deploying to Render.com

This guide provides step-by-step instructions for deploying the Bill Generator application to Render.com.

## Prerequisites

1. Create a [Render.com](https://render.com) account
2. Have your code in a GitHub repository (recommended for easy deployment)

## Deployment Steps

### Method 1: Using the Render Dashboard (Recommended)

1. **Fork or clone this repository to your GitHub account**
   - This allows Render to access and deploy your code

2. **Create a PostgreSQL Database**
   - Go to the Render Dashboard
   - Click "New +" at the top, then select "PostgreSQL"
   - Configure your database:
     - Name: `parate-db` (or any name you prefer)
     - Database: `parate_db`
     - User: `parate_user`
     - Region: Choose one close to your users
     - Plan: Select a plan (Free tier is available)
   - Click "Create Database"
   - **Important**: Copy the "Internal Database URL" - you'll need this in the next step

3. **Create a Web Service**
   - In the Render Dashboard, click "New +" again, then select "Web Service"
   - Link to your GitHub repository
   - Configure your web service:
     - Name: `parate-welding-workshop`
     - Region: Same as your database
     - Branch: `main` (or your preferred branch)
     - Root Directory: Leave empty
     - Runtime: `Python`
     - Build Command: `pip install -r railway_requirements.txt`
     - Start Command: `gunicorn main:app`
     - Plan: Select a plan (Free tier is available)

4. **Configure Environment Variables**
   - In your web service, scroll down to the "Environment" section
   - Add the following variables:
     - `DATABASE_URL`: Paste the Internal Database URL from step 2
     - `FLASK_ENV`: `production`
     - `RAILWAY_ENVIRONMENT`: `1` (this enables production mode)
     - `SESSION_SECRET`: Generate a random string or use the "Generate" button
     - `PDF_STORAGE_PATH`: `/var/data/generated_pdfs`

5. **Set Up a Persistent Disk**
   - Scroll down to "Disks" in your web service settings
   - Click "Add Disk"
   - Configure the disk:
     - Name: `pdf-storage`
     - Mount Path: `/var/data`
     - Size: 1 GB (minimum, adjust as needed)

6. **Deploy**
   - Click "Create Web Service"
   - Render will start the build and deployment process
   - Monitor the logs for any issues

### Method 2: Using render.yaml (Blueprint)

1. **Create a render.yaml file in your repository**
   ```yaml
   services:
     # A web service
     - type: web
       name: parate-welding-workshop
       env: python
       plan: free
       buildCommand: pip install -r railway_requirements.txt
       startCommand: gunicorn main:app
       disk:
         name: pdf-storage
         mountPath: /var/data
         sizeGB: 1
       envVars:
         - key: FLASK_ENV
           value: production
         - key: RAILWAY_ENVIRONMENT
           value: "1"
         - key: PDF_STORAGE_PATH
           value: /var/data/generated_pdfs
         - key: SESSION_SECRET
           generateValue: true
         - key: DATABASE_URL
           fromDatabase:
             name: parate-db
             property: connectionString
       
     # A PostgreSQL database
   databases:
     - name: parate-db
       plan: free
       databaseName: parate_db
       user: parate_user
   ```

2. **Deploy using Blueprint**
   - Commit and push the render.yaml file to your repository
   - In the Render Dashboard, click "New +" and select "Blueprint"
   - Connect to your GitHub repository
   - Render will automatically create all the services defined in your render.yaml file

## Verifying Deployment

1. Once deployed, Render will provide a domain for your application (e.g., `https://parate-welding-workshop.onrender.com`)
2. Visit this domain to access your deployed Bill Generator application
3. The application will automatically:
   - Connect to the PostgreSQL database
   - Run any pending database migrations
   - Create necessary tables if they don't exist
   - Set up the storage directory for PDFs

## Troubleshooting

- If you encounter database connection issues, verify the `DATABASE_URL` is correct and that Render's internal network can access the database
- For PDF storage issues, check that the persistent disk is properly mounted and the app has write permissions
- View deployment logs in the Render dashboard to diagnose any startup problems
- If the application starts but pages don't load, check the server logs for errors

## Important Notes

- Render's free tier has some limitations:
  - Free web services spin down after 15 minutes of inactivity
  - Free databases are limited to 1GB storage
  - Consider upgrading to a paid plan for production use
- PDF files are stored on the persistent disk, not in the database
- The application automatically performs database migrations on startup
- You can set up a custom domain in the Render dashboard settings