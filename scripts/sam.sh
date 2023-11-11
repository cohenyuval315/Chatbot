samlocal build --base-dir . --cache-dir .aws-sam/cache --build-dir ./build --debug
samlocal local start-api -p 3002
