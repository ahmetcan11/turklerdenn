#! /bin/bash

export PROJECT_ID=fluent-horizon-388119
export REGION=us-west2
export CONNECTION_NAME=fluent-horizon-388119:us-west2:turklerdendb

gcloud builds submit \
  --tag gcr.io/$PROJECT_ID/poll \
  --project $PROJECT_ID

gcloud run deploy poll \
  --image gcr.io/$PROJECT_ID/poll \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --add-cloudsql-instances $CONNECTION_NAME \
  --project $PROJECT_ID