BUCKET_NAME=test-bucket
REGION=eu-west-3

awslocal s3api delete-bucket --bucket $BUCKET_NAME 
BUCKET_EXISTS=$(awslocal s3api list-buckets | jq -r '.Buckets[].Name' | grep "$BUCKET_NAME")
if [ -n "$BUCKET_EXISTS" ]; then
  echo "Bucket exists: $BUCKET_EXISTS"
else
    echo "Bucket '$BUCKET_NAME' Does Not Exists"
    echo "Creating Bucket '$BUCKET_NAME' ..."
    awslocal s3 mb s3://$BUCKET_NAME
fi