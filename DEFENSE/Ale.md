https://pvs-studio.ru/ru/blog/posts/cpp/1028/?ysclid=m90dbtrps411266111

https://habr.com/ru/companies/dsec/articles/702652/#semgrep

https://research.aimultiple.com/open-source-sast-tools/

https://tproger.ru/articles/best-kali-linux-tools

### 1. Компилятор C в Kali Linux

В Kali Linux уже предустановлен GCC (GNU Compiler Collection) — стандартный компилятор для C.  

Проверь его наличие и версию:

```bash
gcc --version
```

Если его нет (маловероятно), установи:

```bash
sudo apt update && sudo apt install gcc
```


#### Дополнительные полезные флаги компиляции для безопасности:

```bash
gcc -fstack-protector -D_FORTIFY_SOURCE=2 -O2 -Wformat -Werror=format-security -pie -fPIE program.c -o program

- -fstack-protector — защита от переполнения буфера.
- -D_FORTIFY_SOURCE=2 — проверки на переполнение буферов.
- -pie -fPIE — рандомизация адресного пространства (ASLR).
- -Wformat -Werror=format-security — защита от format string уязвимостей.
```


### 2. Статический анализ кода (поиск уязвимостей без запуска программы)
#### Инструменты:

- `gcc -Wall -Wextra -Wpedantic` — базовые предупреждения компилятора.

- `cppcheck` — статический анализатор кода.
  
```bash
  sudo apt install cppcheck
  cppcheck --enable=all program.c
```
  
- `flawfinder` — поиск уязвимостей (например, strcpy, gets).
  
```bash
  sudo apt install flawfinder
  flawfinder program.c
```
  
- `splint` — строгий анализатор кода (устарел, но иногда полезен).
  
```bash
  sudo apt install splint
  splint program.c
```
  
- `clang-tidy` (из LLVM) — мощный статический анализатор.
  
```bash
  sudo apt install clang-tidy
  clang-tidy program.c --checks='*'
```

---

### 3. Динамический анализ (анализ во время выполнения)
#### Инструменты:
- `Valgrind` — поиск утечек памяти и ошибок.
  
```bash
  sudo apt install valgrind
  valgrind --leak-check=full ./program
 ```

- `AddressSanitizer (ASan)` — детектор переполнений буфера, use-after-free.
  
```bash
  gcc -fsanitize=address -g program.c -o program
  ./program
```
  
- `GDB (GNU Debugger)` — отладчик для анализа крашей.
  
```bash
  sudo apt install gdb
  gdb ./program
```
  
- `strace` / `ltrace` — мониторинг системных вызовов и библиотечных функций.
  
```bash
  strace ./program
  ltrace ./program
```

### 4. Поиск уязвимостей в бинарных файлах (если нужно анализировать скомпилированную программу)

- `checksec` — проверка защит бинарного файла (ASLR, NX, Canary и др.).
  
```bash
  sudo apt install checksec
  checksec --file=./program
  ```

- `radare2` / `Cutter` — дизассемблер и отладчик.
  
```bash
  sudo apt install radare2 cutter
  r2 ./program
  ```

- `Ghidra` (от NSA) — декомпилятор и анализ бинарников.
  
```bash
  sudo apt install ghidra
 ``` 

---

### 5. Типичные уязвимости в C и как их искать
#### Основные категории:

1. Переполнение буфера (`buffer overflow`)

```bash
   - Поиск: strcpy, gets, scanf, memcpy без проверки длины.  
   - Защита: strncpy, snprintf, fgets.
```

3. Уязвимости форматной строки (`format string`)

```bash
   - Поиск: printf(user_input) вместо printf("%s", user_input).
```

5. Use-after-free / Double-free

```bash
   - Поиск: free() без обнуления указателя, повторный free().
```

7. Целочисленные переполнения (`integer overflow`)

```bash
   - Поиск: арифметика без проверки границ (например, size = width * height перед `malloc`).  
```

9. Race conditions (`TOCTOU`)
   
   - Поиск: проверка файла перед открытием (`access()` + `open()`).  

---

### 6. Дополнительные инструменты

- `binwalk` — анализ бинарных файлов (если нужно искать скрытые данные).
  
- `strings` — поиск строк в бинарнике.
  
- `hexeditor` (например, `xxd`) — ручной анализ hex-дампов.  

---

### 7. Методика работы на соревнованиях

1. Статический анализ → cppcheck, flawfinder.
   
3. Компиляция с флагами защиты → -fstack-protector, -D_FORTIFY_SOURCE=2.
   
5. Динамический анализ → valgrind, ASan.
    
7. Проверка бинарника → checksec, Ghidra.
   
9. Ручной аудит кода — ищи типовые уязвимости (см. выше).  

---
---

## **1. Переполнение буфера (Buffer Overflow)**
### **Что это?**  
Запись данных за пределы выделенного буфера, что может привести к перезаписи соседних переменных, адреса возврата или ROP-цепочкам.  

### **Где искать?**  
Опасные функции:  
```c
strcpy(buf, input);          // Копирует без проверки длины
gets(buf);                   // Читает строку без ограничения
scanf("%s", buf);            // Аналогично gets
sprintf(buf, "%s", input);   // Может переполнить buf
memcpy(dest, src, n);        // Если n вычисляется небезопасно
```

### **Пример уязвимого кода**  
```c
#include <string.h>

void vulnerable() {
    char buf[16];
    gets(buf);  // Переполнение, если ввод > 15 символов
}
```

### **Как эксплуатировать?**  
Если переполнение происходит в стеке, можно:  
1. Перезаписать адрес возврата (`return address`).  
2. Внедрить шелл-код (если нет NX).  

### **Защита**  
- Использовать безопасные аналоги:  
  ```c
  strncpy(buf, input, sizeof(buf) - 1);  // Ограничение длины
  fgets(buf, sizeof(buf), stdin);        // Безопасный ввод
  snprintf(buf, sizeof(buf), "%s", input); // Контроль длины
  ```
- Включить защиту компилятора:  
  ```bash
  gcc -fstack-protector-all -D_FORTIFY_SOURCE=2 ...
  ```

---

## **2. Уязвимости форматной строки (Format String)**
### **Что это?**  
Если пользовательский ввод передаётся прямо в `printf`, `sprintf` и т. д., злоумышленник может читать/писать память.  

### **Где искать?**  
```c
printf(input);          // Опасный вызов (вместо printf("%s", input))
sprintf(buf, input);    // Аналогично
syslog(LOG_ERR, input); // Да, даже так!
```

### **Пример уязвимого кода**  
```c
void vulnerable() {
    char buf[100];
    scanf("%99s", buf);
    printf(buf);  // Уязвимость!
}
```

### **Как эксплуатировать?**  
- **Чтение памяти**: `%x`, `%p` — дамп стека.  
- **Запись в память**: `%n` — записывает кол-во байт в указанный адрес.  

### **Защита**  
Всегда указывать формат строки:  
```c
printf("%s", input);  // Так безопасно
```

---

## **3. Use-After-Free / Double-Free**
### **Что это?**  
- **Use-After-Free (UAF)**: Использование памяти после её освобождения.  
- **Double-Free**: Двойное освобождение той же памяти.  

### **Где искать?**  
```c
free(ptr);
// ...
free(ptr);  // Double-Free

// Или
free(ptr);
printf("%s", ptr->data);  // Use-After-Free
```

### **Пример уязвимого кода**  
```c
struct User {
    char name[32];
};

void vulnerable() {
    struct User *user = malloc(sizeof(struct User));
    free(user);
    strcpy(user->name, "hacker");  // UAF!
}
```

### **Как эксплуатировать?**  
- Перезаписать структуры кучи для выполнения произвольного кода.  
- Использовать `tcache poisoning` (в современных glibc).  

### **Защита**  
- Обнулять указатели после `free`:  
  ```c
  free(ptr);
  ptr = NULL;  // Теперь UAF невозможен
  ```
- Использовать `AddressSanitizer (ASan)`:  
  ```bash
  gcc -fsanitize=address -g ...
  ```

---

## **4. Целочисленные переполнения (Integer Overflow)**
### **Что это?**  
Арифметические операции приводят к неожиданным результатам из-за ограничений типа.  

### **Где искать?**  
```c
size_t size = width * height;  // Если width=65536, height=65536 → 0 (32-бит)
malloc(size);  // Выделит 0 байт!

int index = offset + len;  // Может стать отрицательным
array[index] = 0;          // Переполнение буфера
```

### **Пример уязвимого кода**  
```c
void vulnerable(int a, int b) {
    int size = a * b;  // Переполнение, если a и b большие
    char *buf = malloc(size);
    // ...
}
```

### **Как эксплуатировать?**  
- Вызвать `malloc(0)` → последующий переполнение кучи.  
- Отрицательный индекс → запись за пределы массива.  

### **Защита**  
- Проверять границы:  
  ```c
  if (a > SIZE_MAX / b) {
      // Ошибка!
  }
  ```
- Использовать `safe` функции (`__builtin_add_overflow` в GCC).  

---

## **5. Race Conditions (TOCTOU)**
### **Что это?**  
**Time of Check to Time of Use (TOCTOU)** — состояние гонки между проверкой и использованием.  

### **Где искать?**  
```c
if (access("file", W_OK) == 0) {  // Проверка прав
    // Злоумышленник заменяет file на symlink
    fd = open("file", O_WRONLY);  // Открытие
}
```

### **Пример уязвимого кода**  
```c
void vulnerable() {
    if (access("/tmp/file", R_OK) == 0) {
        // Между access и open файл может быть заменён!
        FILE *f = fopen("/tmp/file", "r");
    }
}
```

### **Как эксплуатировать?**  
- Подменить файл на симлинк (`/etc/passwd`).  
- Обойти проверки прав доступа.  

### **Защита**  
- Использовать атомарные операции:  
  ```c
  fd = open("file", O_WRONLY | O_NOFOLLOW);  // Без симлинков
  fstat(fd, &st);  // Проверка прав уже после открытия
  ```
- Работать в защищённых каталогах (`/proc/self/fd/`).  

---

## **Вывод: Как искать и исправлять?**  
| Уязвимость         | Где искать?                          | Защита                          | Инструменты для анализа       |  
|--------------------|--------------------------------------|---------------------------------|-------------------------------|  
| Buffer Overflow    | `strcpy`, `gets`, `scanf`           | `strncpy`, `fgets`, `snprintf`  | `valgrind`, `ASan`, `cppcheck` |  
| Format String      | `printf(input)`                     | `printf("%s", input)`           | `gcc -Wformat-security`       |  
| Use-After-Free     | `free()` + использование указателя  | Обнулять указатели              | `ASan`, `valgrind`            |  
| Integer Overflow   | `a * b`, `a + b` перед `malloc`     | Проверка границ                 | `clang-tidy`, `cppcheck`      |  
| TOCTOU            | `access()` + `open()`               | Атомарные операции              | `strace`, `ltrace`            |  


## **1. Статический анализ кода (SAST)**
### **Автоматизированные анализаторы**
| Инструмент | Описание | Установка |
|------------|----------|-----------|
| **`GCC с флагами`** | Базовые предупреждения (`-Wall`, `-Wextra`, `-Werror`) | Уже в Kali |
| **`clang-tidy`** | Мощный статический анализатор от LLVM (ищет UB, уязвимости) | `sudo apt install clang-tidy` |
| **`flawfinder`** | Ищет опасные функции (`strcpy`, `gets`, `printf`) | `sudo apt install flawfinder` |
| **`cppcheck`** | Анализирует поток данных, находит утечки | `sudo apt install cppcheck` |
| **`splint`** | Устарел, но иногда полезен для строгого анализа | `sudo apt install splint` |
| **`Infer`** (от Meta) | Ищет null dereference, memory leaks | `sudo apt install infer` |
| **`Semgrep`** | Поиск шаблонов уязвимостей (есть готовые правила) | `pip install semgrep` |
| **`CodeQL`** (от GitHub) | Продвинутый анализ (нужно писать запросы) | [Установка](https://codeql.github.com/) |

### **Ручной аудит**
- **`grep`** — поиск опасных функций:  
  ```bash
  grep -nE '(strcpy|gets|scanf|printf\([^"]*\)|memcpy)' *.c
  ```
- **`radare2` / `Cutter`** — анализ бинарников (если код уже скомпилирован).  

---

## **2. Динамический анализ (DAST)**
### **Фаззинг (Fuzzing)**
| Инструмент | Описание | Установка |
|------------|----------|-----------|
| **`AFL++`** | Фаззер для поиска крашей (ASan + покрытие) | `sudo apt install afl++` |
| **`libFuzzer`** (LLVM) | Встроенный фаззер для unit-тестов | `sudo apt install clang` |
| **`honggfuzz`** | Альтернатива AFL | `sudo apt install honggfuzz` |

### **Отладка и мониторинг**
| Инструмент | Описание | Установка |
|------------|----------|-----------|
| **`Valgrind`** | Поиск утечек памяти (memcheck) | `sudo apt install valgrind` |
| **`AddressSanitizer` (ASan)** | Находит переполнения буфера, UAF | `gcc -fsanitize=address` |
| **`GDB` + `pwndbg`** | Отладка (с удобными плагинами) | `sudo apt install gdb pwndbg` |
| **`strace` / `ltrace`** | Логирование системных вызовов | Уже в Kali |
| **`rr`** (Record & Replay) | Детерминированная отладка | `sudo apt install rr` |

---

## **3. Анализ бинарников (если код уже скомпилирован)**
| Инструмент | Описание | Установка |
|------------|----------|-----------|
| **`checksec`** | Проверка защит (ASLR, NX, Canary) | `sudo apt install checksec` |
| **`Ghidra`** | Декомпилятор (от NSA) | `sudo apt install ghidra` |
| **`Binary Ninja`** | Платформа для реверса (платная) | [Сайт](https://binary.ninja/) |
| **`radare2`** | Консольный дизассемблер | `sudo apt install radare2` |
| **`Cutter`** | GUI для radare2 | `sudo apt install cutter` |
| **`angr`** | Символьное исполнение (для сложных тасков) | `pip install angr` |

---

## **4. Инструменты для эксплуатации**
Если defence-only, то не пригодятся, но для полноты:  
- **`pwntools`** — Python-библиотека для эксплойтов.  
  ```bash
  pip install pwntools
  ```
- **`ROPgadget`** — поиск гаджетов для ROP-цепочки.  
  ```bash
  sudo apt install ropgadget
  ```
- **`one_gadget`** — поиск готовых вызовов `/bin/sh` в libc.  
  ```bash
  sudo apt install ruby-dev && gem install one_gadget
  ```

---

## **5. Дополнительные утилиты**
| Инструмент | Описание | Установка |
|------------|----------|-----------|
| **`binwalk`** | Анализ бинарников (например, встроенных файлов) | `sudo apt install binwalk` |
| **`xxd` / `hexedit`** | Ручной анализ hex | Уже в Kali |
| **`ltrace`** | Логирование вызовов библиотек | Уже в Kali |
| **`strings`** | Поиск строк в бинарнике | Уже в Kali |

---

## **Какой инструмент выбрать?**
1. **Статический анализ**:  
   - Быстрый поиск: `grep`, `flawfinder`.  
   - Глубокий анализ: `clang-tidy`, `CodeQL`.  
2. **Динамический анализ**:  
   - Фаззинг: `AFL++`.  
   - Отладка: `GDB + ASan`.  
3. **Анализ бинарников**:  
   - Простота: `Ghidra`.  
   - Продвинутый уровень: `radare2`/`angr`.  

---

## **Пример рабочего процесса**
1. **Проверить код статически**:  
   ```bash
   cppcheck --enable=all ./src/
   flawfinder ./src/
   ```
2. **Скомпилировать с защитами**:  
   ```bash
   gcc -fstack-protector-all -D_FORTIFY_SOURCE=2 -O2 -Werror=format-security program.c -o program
   ```
3. **Протестировать динамически**:  
   ```bash
   valgrind --leak-check=full ./program
   AFL_Fuzzing ./program
   ```
4. **Проверить бинарник**:  
   ```bash
   checksec --file=./program
   r2 ./program
   ```

---

## **1. Установка компилятора (если ещё не установлен)**
GCC (GNU Compiler Collection) — стандартный компилятор для C в Linux.  
Проверь его наличие:
```bash
gcc --version
```
Если команда не найдена, установи:
```bash
sudo apt update && sudo apt install gcc
```

---

## **2. Компиляция программы**
### **Базовый способ**
Допустим, у тебя есть файл `program.c`.  
Скомпилируй его в исполняемый файл (`program`):
```bash
gcc program.c -o program
```
- `program.c` — исходный файл.  
- `-o program` — название выходного файла (можно любое).  

### **Пример**
```c
// program.c
#include <stdio.h>

int main() {
    printf("Hello, Kali Linux!\n");
    return 0;
}
```
Компиляция:
```bash
gcc program.c -o program
```

---

## **3. Запуск программы**
После компиляции выполни:
```bash
./program
```
Вывод:
```
Hello, Kali Linux!
```

---

## **4. Дополнительные флаги компиляции**
### **1. Включение всех предупреждений**
Помогает найти потенциальные ошибки:
```bash
gcc -Wall -Wextra -Werror program.c -o program
```
- `-Wall` — включает основные предупреждения.  
- `-Wextra` — дополнительные предупреждения.  
- `-Werror` — трактует предупреждения как ошибки.  

### **2. Защита от уязвимостей**
Полезно для CTF и безопасного кода:
```bash
gcc -fstack-protector-all -D_FORTIFY_SOURCE=2 -O2 -Wformat -Werror=format-security program.c -o program
```
- `-fstack-protector-all` — защита от переполнения буфера.  
- `-D_FORTIFY_SOURCE=2` — проверки на переполнение.  
- `-Wformat-security` — защита от format string атак.  

### **3. Отладочная информация**
Для отладки в `gdb`:
```bash
gcc -g program.c -o program
```
- `-g` — добавляет отладочные символы.  

### **4. Оптимизация**
```bash
gcc -O2 program.c -o program  # Оптимизация скорости
gcc -Os program.c -o program  # Оптимизация размера
```

---

## **5. Полезные команды для работы**
### **1. Просмотр содержимого файла**
```bash
cat program.c
```

### **2. Изменение прав (если программа не запускается)**
```bash
chmod +x program  # Даёт права на выполнение
```

### **3. Запуск с аргументами**
Если программа принимает аргументы:
```bash
./program arg1 arg2
```

### **4. Перенаправление вывода**
```bash
./program > output.txt  # Вывод в файл
./program | grep "Hello"  # Фильтрация вывода
```

---

## **6. Где выводится результат?**
- **По умолчанию** — в терминал (stdout).  
- Если нужно записать в файл:  
  ```bash
  ./program > output.txt
  ```
- Если программа читает ввод (stdin), можно передать файл:  
  ```bash
  ./program < input.txt
  ```

---

## **7. Пример с вводом/выводом**
```c
// example.c
#include <stdio.h>

int main() {
    int num;
    printf("Enter a number: ");
    scanf("%d", &num);
    printf("You entered: %d\n", num);
    return 0;
}
```
**Компиляция и запуск:**
```bash
gcc example.c -o example
./example
```
Вывод:
```
Enter a number: 42
You entered: 42
```

---

## **8. Как исправить частые ошибки?**
### **1. «Нет такого файла» (`No such file or directory`)**
- Проверь путь:  
  ```bash
  ls  # Убедись, что файл существует
  gcc ./correct_folder/program.c -o program
  ```

### **2. «Permission denied»**
Дай права на выполнение:  
```bash
chmod +x program
```

### **3. Неизвестная функция (`implicit declaration`)**
Добавь заголовочные файлы (например, `#include <string.h>`).  

---

## **Вывод**
1. **Компиляция**:  
   ```bash
   gcc file.c -o output
   ```
2. **Запуск**:  
   ```bash
   ./output
   ```
3. **Доп. флаги**:  
   - `-Wall -Wextra` для предупреждений.  
   - `-fstack-protector` для защиты.  
   - `-g` для отладки.  

