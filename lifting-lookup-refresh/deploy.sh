#!/bin/bash
mkdir -p package
pip install -r requirements.txt --target package/
cp lambda_function.py package/
cd package
zip -r ../deployment.zip .
cd ..
rm -rf package

echo "Deployment package created: deployment.zip" 