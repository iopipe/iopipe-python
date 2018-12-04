#!/bin/bash -e

REGIONS=(
  ap-northeast-1
  ap-northeast-2
  ap-south-1
  ap-southeast-1
  ap-southeast-2
  ca-central-1
  eu-central-1
  eu-west-1
  eu-west-2
  eu-west-3
  #sa-east-1
  us-east-1
  us-east-2
  us-west-1
  us-west-2
)

echo "python3.6, python3.7:"
echo ""

for region in "${REGIONS[@]}"; do
    latest_arn=$(aws --region $region lambda list-layer-versions --layer-name IOpipePython --output text --query "LayerVersions[0].LayerVersionArn")
    echo "* ${region}: \`${latest_arn}\`"
done

echo ""
echo "python2.7:"
echo ""

for region in "${REGIONS[@]}"; do
    latest_arn=$(aws --region $region lambda list-layer-versions --layer-name IOpipePython27 --output text --query "LayerVersions[0].LayerVersionArn")
    echo "* ${region}: \`${latest_arn}\`"
done
