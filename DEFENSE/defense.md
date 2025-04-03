docker-compose up --build -d

docker-compose up -d

docker-compose down


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










# ПУПУПУПУП

Если вы ищете SAST (статический анализ безопасности) инструмент для анализа уязвимостей в ваших PHP файлах, вот несколько популярных вариантов, которые вы можете быстро развернуть:

### 1. RIPS код анализа

Описание: RIPS — это инструмент статического анализа безопасности, специально разработанный для обнаружения уязвимостей в PHP коде. Он позволяет находить такие проблемы, как SQL-инъекции, XSS уязвимости и т. д.

Установка: RIPS можно развернуть в Docker. Для этого потребуется его образ. Вам нужно будет создать учетную запись на их сайте, чтобы получить доступ к инструменту и его образу Docker.

Документация: RIPS Documentation

### 2. SonarQube с плагином для PHP

Описание: SonarQube — это платформа для анализа кода, которая поддерживает множество языков, включая PHP. С помощью плагина для PHP вы сможете выполнять статический анализ, включая обнаружение уязвимостей.

Установка: Можно установить SonarQube через Docker:

docker run -d -p 9000:9000 sonarqube


После запуска откройте браузер и перейдите на http://localhost:9000, чтобы завершить настройку.

Плагин для PHP: Убедитесь, что у вас установлен плагин SonarPHP. Вы можете найти его в разделе обновлений плагинов в интерфейсе SonarQube.

Анализ проекта: После настройки SonarQube вы можете анализировать ваши PHP проекты с помощью команды:

sonar-scanner


### 3. PHP Security Checker

Описание: Этот инструмент позволяет быстро проверять ваши зависимости на наличие уязвимостей, используя базы данных, такие как Packagist и GitHub.

Установка:

composer global require secbzi/php-security-checker


Использование: Чтобы проверить пакет на наличие уязвимостей, выполните:

php-security-checker security:check






Конечно! Вот как вы можете использовать SonarQube и RIPS для анализа уязвимостей в вашем PHP проекте, включая команды и шаги для их настройки и работы.

### 1. Использование SonarQube

Шаг 1: Установка SonarQube через Docker

docker run -d --name sonarqube -p 9000:9000 sonarqube


После запуска SonarQube (это может занять некоторое время), откройте в браузере http://localhost:9000. 

Шаг 2: Завершение настройки SonarQube

- Первоначальный логин: admin / admin.
- После первого входа рекомендуется изменить пароль.

Шаг 3: Установка плагина SonarPHP

1. Перейдите в раздел "Administration".
2. Выберите "Marketplace".
3. Найдите SonarPHP и установите его, если он не установлен по умолчанию.
4. После установки перезапустите SonarQube.

Шаг 4: Установка SonarScanner

Для анализа проекта вам понадобится SonarScanner. Установите его глобально:

# Для загрузки и установки SonarScanner, используйте подходящий для вашей системы метод
# Например, для Linux можно загрузить и извлечь архив
wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/4.6.2.2472/sonar-scanner-cli-4.6.2.2472-linux.zip
unzip sonar-scanner-cli-4.6.2.2472-linux.zip
sudo mv sonar-scanner-4.6.2.2472-linux/bin/* /usr/local/bin/


Шаг 5: Настройка проекта для анализа

Перейдите в корневую директорию вашего PHP проекта и создайте файл sonar-project.properties со следующим содержимым:

sonar.projectKey=your_project_key
sonar.projectName=Your Project Name
sonar.projectVersion=1.0
sonar.sources=src  # Замените на путь к вашим PHP исходным файлам
sonar.language=php
sonar.sourceEncoding=UTF-8


Шаг 6: Запуск анализа

Запустите SonarScanner в корневой директории вашего

