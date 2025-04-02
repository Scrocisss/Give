https://pvs-studio.ru/ru/blog/posts/cpp/1028/?ysclid=m90dbtrps411266111

https://habr.com/ru/companies/dsec/articles/702652/#semgrep

https://research.aimultiple.com/open-source-sast-tools/

https://tproger.ru/articles/best-kali-linux-tools

Привет! Участие в defence-only CTF — это отличный опыт. Для анализа кода на C и устранения уязвимостей в Kali Linux тебе пригодятся следующие инструменты и методики.

---

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
