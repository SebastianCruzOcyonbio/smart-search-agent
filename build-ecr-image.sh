# Authenticate AWS credentials
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 797049021047.dkr.ecr.us-east-1.amazonaws.com

# # Build Image
# docker build -t smart-search .

# # Tag w/ "latest"
# docker tag smart-search:latest 797049021047.dkr.ecr.us-east-1.amazonaws.com/smart-search

# # Push image to ECR
# docker push 797049021047.dkr.ecr.us-east-1.amazonaws.com/smart-search

docker buildx build --platform linux/amd64 -t 797049021047.dkr.ecr.us-east-1.amazonaws.com/smart-search:latest --push .