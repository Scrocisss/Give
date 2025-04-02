# PYTHON SAST:

```bash
python3 -m venv myenv
source myenv/bin/activate
git clone https://github.com/Scrocisss/SAST-dockerbandit
cd SAST-dockerbandit
docker build -t davarski/bandit -f Dockerfile .
```

How to use?:

    docker run -u root --rm -v YOUR_PYTHON_PROJECT_PATH:/app davarski/bandit bandit -r ./

    //help

    docker run -u root --rm -v YOUR_PYTHON_PROJECT_PATH:/app davarski/bandit bandit -h



# C SAST:

```bash
python3 -m venv myenv
source myenv/bin/activate
apt update && apt install -y clang-tidy
pip install clang-html
```

How to use?:

```bash
cd "project directory"
find -name '*.c' | xargs clang-tidy -checks=*,-clang-analyzer=* > clang-tidy.log
python3 -m clang_html clang-tidy.log -o clang-tidy.html
```





# Zhest'

```bash
    1  sudo apt update
    2  sudo apt install opam
    3  opam init --compiler 4.14.1
    4  eval $(opam env)
    5  opam install frama-c
    6  npm use 22
    7  nvm install 22\nnvm use 22\nnpm install --global yarn
    8  apt install nvm
    9  nvm install 22
   10  nvm use 22
   11  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash\n
   12  export NVM_DIR="$HOME/.nvm"\nsource "$NVM_DIR/nvm.sh"\n
   13  export NVM_DIR="$HOME/.config/nvm"\n[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"\n[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"\n
   14  nvm --version\n
   15  nvm install 22\nnvm use 22
   16  npm install --global yarn
   17  ivette
   18  yarn run
   19  ivette
   20  df -h
   21  ivette
   22  chmod +x ./node_modules/app-builder-bin/linux/x64/app-builder\n
   23  find ~/.cache -type f -name app-builder 2>/dev/null\n
   24  chmod +x /home/kali/.cache/yarn/v6/npm-app-builder-bin-4.0.0-integrity/node_modules/app-builder-bin/linux/x64/app-builder\n
   25  ivette
   26  chmod +x /tmp/tmp.2sKDDnL16A/ivette/node_modules/app-builder-bin/linux/x64/app-builder\n
   27  mount | grep /tmp\n
   28  mkdir -p ~/tmp_exec\nTMPDIR=~/tmp_exec ivette\n

```



```bash
frama-c -wp -wp-rte -wp-prover cvc4 -wp-timeout 30 \
  -cpp-extra-args="-I/usr/include -I/usr/include/x86_64-linux-gnu" \
  /home/kali/Desktop/*.c -then -report
```
