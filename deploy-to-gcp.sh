#!/bin/bash

# Deploy Synapse-Lang Platform to Google Cloud Platform
# Project: industrial-joy-456916-a2

PROJECT_ID="industrial-joy-456916-a2"
REGION="us-central1"

echo "Deploying Synapse-Lang Platform to GCP Project: $PROJECT_ID"

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "Enabling required Google Cloud APIs..."
gcloud services enable appengine.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable compute.googleapis.com

# Create App Engine app if it doesn't exist
echo "Initializing App Engine..."
gcloud app create --region=$REGION 2>/dev/null || echo "App Engine already initialized"

# Create Firestore database if it doesn't exist
echo "Setting up Firestore..."
gcloud firestore databases create --region=$REGION 2>/dev/null || echo "Firestore already initialized"

# Create storage buckets
echo "Creating storage buckets..."
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://${PROJECT_ID}-code 2>/dev/null || echo "Code bucket exists"
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://${PROJECT_ID}-data 2>/dev/null || echo "Data bucket exists"
gsutil mb -p $PROJECT_ID -c NEARLINE -l $REGION gs://${PROJECT_ID}-backups 2>/dev/null || echo "Backup bucket exists"

# Set up secrets in Secret Manager
echo "Setting up secrets..."
echo "Please add your API keys to Secret Manager:"
echo "  - stripe-secret-key"
echo "  - stripe-webhook-secret"
echo "  - openai-api-key (optional)"
echo "  - anthropic-api-key (optional)"

# Deploy the application
echo "Deploying application to App Engine..."
gcloud app deploy app.yaml --quiet

# Deploy dispatch rules
echo "Deploying dispatch configuration..."
gcloud app deploy dispatch.yaml --quiet

# Set up Cloud Build trigger
echo "Setting up Cloud Build trigger..."
gcloud builds triggers create github \
  --repo-name=synapse-lang \
  --repo-owner=MichaelCrowe11 \
  --branch-pattern="^master$" \
  --build-config=cloudbuild.yaml \
  --name="synapse-lang-deploy"

echo "Deployment complete!"
echo "Your app is available at: https://$PROJECT_ID.appspot.com"
echo "Custom domain setup: Map synapse-lang.com to $PROJECT_ID.appspot.com"