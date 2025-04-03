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




Чтобы использовать PHPStan в вашем проекте на PHP, следуйте следующим шагам:

### 1. Установка PHPStan

Если у вас ещё нет Composer, сначала установите его. Затем перейдите в корневую директорию вашего проекта и выполните следующую команду для установки PHPStan:

composer require --dev phpstan/phpstan


### 2. Конфигурация PHPStan

PHPStan может работать без конфигурации, но для более точного анализа рекомендуется создать конфигурационный файл. Создайте файл phpstan.neon в корневой директории вашего проекта со следующим содержимым:

parameters:
    level: 5 # уровень проверки, можно указать от 0 до 8
    paths:
        - %currentWorkingDirectory%/src # путь к вашим исходным файлам


Вы можете изменить уровень проверки и пути в соответствии с вашей структурой проекта. Уровни проверки варьируются от 0 (минимальный уровень) до 8 (максимальный, очень строгий).

### 3. Анализ вашего проекта

После установки и конфигурации PHPStan, вы можете запустить его с помощью команды:

vendor/bin/phpstan analyse


Это выполнит анализ вашего проекта на основе настроенного уровня и файлов.

### 4. Адаптация в зависимости от применения

Если вы хотите специфично указать файлы и директории для анализа, вы можете просто добавить их в команду, например:

vendor/bin/phpstan analyse src tests


Здесь src и tests - это папки, которые вы хотите анализировать.

### 5. Интерпретация результатов

PHPStan выдаст список найденных проблем в вашем коде, включая ошибки типов, нарушения стандартов и другие потенциальные проблемы. Следуйте рекомендациям PHPStan для исправления найденных ошибок.

### 6. Интеграция с CI/CD

Можно интегрировать PHPStan в вашу CI/CD систему для автоматического анализа кода при каждом коммите или перед сборкой. Например, добавив следующую команду в конфигурацию вашего CI/CD:

- name: Run PHPStan
  run: vendor/bin/phpstan analyse


### 7. Документация и уровни анализа

Посмотрите документацию PHPStan для подробной информации о настройке, уровня
