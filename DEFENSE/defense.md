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
