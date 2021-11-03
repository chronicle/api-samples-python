# Service Management APIs in Python

Python samples and guidelines for using Chronicle Service Management APIs.

## Authentication Setup

To access the Chronicle Service Management API programmatically, use Cloud Shell
to authenticate a service account under your GCP organization.

### Environment Variables Setup

1. Go to the Google Cloud Console.
2. Activate Cloud Chell.
3. Set environment variables by running:
   a. Set your organization name:
   ```
   export ORG_ID=[YOUR_ORGANIZATION_ID]
   ```
   b. Set the project ID:
   ```
   export PROJECT_ID=[SERVICE_MANAGEMENT_ENABLED_PROJECT_ID]
   ```
   c. Set the service account name:
   ```
   export SERVICE_ACCOUNT=[SERVICE_ACCOUNT_NAME]
   ```
   d. Set the path in which the service account key should be stored:
   ```
   export KEY_LOCATION=[FULL_PATH]
   # This is used by client libraries to find the key.
   export GOOGLE_APPLICATION_CREDENTIALS=$KEY_LOCATION
   ```

### Service Account Setup

1. Create a service account that's associated with your project ID.
```
gcloud iam service-accounts create $SERVICE_ACCOUNT --display-name \
  "Service Account for Chronicle Service Management APIs" --project $PROJECT_ID
```
2. Create a key to associate with the service account.
```
gcloud iam service-accounts keys create $KEY_LOCATION --iam-account \
 $SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com
```
3. Grant the service account the `chroniclesm.admin` role for the organization.
```
gcloud organizations add-iam-policy-binding $ORG_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com" \
  --role='roles/chroniclesm.admin'
```

