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
