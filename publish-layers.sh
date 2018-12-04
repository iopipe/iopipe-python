#!/bin/bash -e

PY27_DIST=dist/python27.zip
PY3X_DIST=dist/python3x.zip

REGIONS=(
  #ap-northeast-1
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

rm -rf dist python
mkdir -p dist

echo "Building iopipe layer for python2.7"
docker run --rm -v "$PWD":/var/task lambci/lambda:build-python2.7 pip install -qU iopipe -t python/lib/python2.7/site-packages \
    && find python -name '*.pyc' -exec rm -f {} + \
    && zip -rq $PY27_DIST python \
    && rm -rf python \
    && echo "Build complete: ${PY27_DIST}" \
    || echo "Build failure: ${PY27_DIST}"

echo "Building iopipe Layer for python3.x"
docker run --rm -v "$PWD":/var/task lambci/lambda:build-python3.6 pip install -qU iopipe -t python \
    && find python -name '__pycache__' -exec rm -fr {} + \
    && zip -rq $PY3X_DIST python \
    && rm -rf python \
    && echo "Build complete: ${PY3X_DIST}" \
    || echo "Build failure: ${PY3X_DIST}"

PY27_MD5SUM=$(md5 -q $PY27_DIST)
PY27_S3KEY="iopipe-python2.7/${PY27_MD5SUM}"

PY3X_MD5SUM=$(md5 -q $PY3X_DIST)
PY3X_S3KEY="iopipe-python3.x/${PY3X_MD5SUM}"

for region in "${REGIONS[@]}"; do
	bucket_name="iopipe-layers-${region}"

	echo "Uploading ${PY27_DIST} to s3://${bucket_name}/${PY27_S3KEY}.zip"
	aws --region $region s3 cp $PY27_DIST "s3://${bucket_name}/${PY27_S3KEY}.zip"

	echo "Uploading ${PY3X_DIST} to s3://${bucket_name}/${PY3X_S3KEY}.zip"
	aws --region $region s3 cp $PY3X_DIST "s3://${bucket_name}/${PY3X_S3KEY}.zip"

	echo "Publishing python2.7 layer to ${region}"
	py27_version=$(aws lambda publish-layer-version \
		--layer-name IOpipePython27 \
		--content "S3Bucket=${bucket_name},S3Key=${PY27_S3KEY}.zip" \
		--description "IOpipe Layer for Python 2.7" \
		--compatible-runtimes python2.7 \
		--license-info "Apache 2.0" \
		--region $region \
		--output text \
		--query Version)
	echo "Published python2.7 layer version ${py27_version} to ${region}"

	echo "Setting public permissions for python2.7 layer version ${py27_version} in ${region}"
	aws lambda add-layer-version-permission \
      --layer-name IOpipePython27 \
      --version-number $py27_version \
      --statement-id public \
      --action lambda:GetLayerVersion \
      --principal "*" \
      --region $region \
      > /dev/null
	echo "Public permissions set for python2.7 layer version ${py27_version} in region ${region}"

	echo "Publishing python3.x layer to ${region}"
	py3x_version=$(aws lambda publish-layer-version \
		--layer-name IOpipePython \
		--content "S3Bucket=${bucket_name},S3Key=${PY3X_S3KEY}.zip" \
		--description "IOpipe Layer for Python 3.6+" \
		--compatible-runtimes python3.6 python3.7 \
		--license-info "Apache 2.0" \
		--region $region \
		--output text \
		--query Version)
	echo "published python3.x layer version ${py3x_version} to ${region}"

	echo "Setting public permissions for python3.x layer version ${py3x_version} in ${region}"
	aws lambda add-layer-version-permission \
      --layer-name IOpipePython \
      --version-number $py3x_version \
      --statement-id public \
      --action lambda:GetLayerVersion \
      --principal "*" \
      --region $region \
      > /dev/null
	echo "Public permissions set for python3.x Layer version ${py3x_version} in region ${region}"
done
