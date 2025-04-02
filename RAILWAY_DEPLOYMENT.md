# Deploying to Railway

This guide will walk you through the steps to deploy the Parate Welding Workshop bill generation system to Railway.

## Step 1: Set up your Railway account

1. Go to [Railway.app](https://railway.app/) and sign up for an account if you don't have one
2. Install the Railway CLI (optional, but helpful):
   ```
   npm i -g @railway/cli
   ```
3. Login to Railway:
   ```
   railway login
   ```

## Step 2: Prepare your application for deployment

### Create these files in your project:

**Procfile** (create this file at the root of your project)
```
web: gunicorn main:app
```

**runtime.txt** (create this file at the root of your project)
```
python-3.11.1
```

**requirements.txt** (This file should include all Python dependencies)
```
email-validator
flask
flask-sqlalchemy
frozen-flask
gunicorn
psycopg2-binary
reportlab
sqlalchemy
trafilatura
```

## Step 3: Set up your project on Railway

1. Create a new project in Railway dashboard
2. Choose "Deploy from GitHub repo"
3. Select your repository
4. (Optional) If you're using the CLI:
   ```
   railway init
   ```

## Step 4: Configure environment variables

Add these environment variables in the Railway dashboard:

| Variable | Value |
|----------|-------|
| SESSION_SECRET | (Generate a random string) |
| FLASK_ENV | production |
| DATABASE_URL | (Railway will provide this automatically if you add a PostgreSQL plugin) |

## Step 5: Add the PostgreSQL plugin (optional, but recommended)

1. In your Railway project dashboard, click on "New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically add the DATABASE_URL to your environment variables

## Step 6: Database considerations

If you're migrating from SQLite to PostgreSQL, you'll need to handle any database migration issues. The application already includes migration support, but you may need to run manual migrations.

To stick with SQLite on Railway (possible, but not ideal for production):
1. Create a volume for persistent storage
2. Update the DATABASE_URL to point to the SQLite file on the volume

## Step 7: Deploy your application

1. Push your code to your GitHub repository
2. Railway will automatically deploy your application
3. (Or with CLI): `railway up`

## Step 8: Access your deployed application

1. In your Railway dashboard, find the URL for your deployed application
2. Click on the URL to open your application in a browser

## Important Notes for Railway Deployment:

1. **Persistent Storage**: Railway provides volumes for persistent storage, which you should use for storing PDFs and the SQLite database if you continue using it.

2. **PostgreSQL Recommendation**: For production, it's recommended to switch to PostgreSQL (which Railway provides) rather than SQLite.

3. **Environment Variables**: Make sure all necessary environment variables are set in the Railway dashboard.

4. **Custom Domain**: You can configure a custom domain in the Railway project settings.

5. **Scaling**: Railway allows easy scaling of your application as needed.

6. **Logging**: Railway provides logs for debugging and monitoring your application.