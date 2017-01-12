#!/bin/sh

echo "Installing Apex"
mkdir bin
wget https://github.com/apex/apex/releases/download/v0.11.0/apex_linux_amd64 -P bin/apex
chmod +x bin/apex
echo "installed apex"
ls -la
echo $PATH
export PATH="${PATH}:${HOME}/bin/"
echo $PATH


for func in $(ls functions); do
  if [ -f functions/${func}/package.json ]; then
    cd functions/${func}/
    echo $PWD
    echo "Installing node packages for ${func}"
    yarn
    cd ../..
  fi

  if [ -f functions/${func}/requirements.txt ]; then
    cd functions/${func}/
    echo "Installing Python packages for ${func}"
    pip install -r requirements.txt -t .
    cd ../..
  fi
done
