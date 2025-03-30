# Windows

===== Форенсика и incident response, винда =====

Цель — установить ход инцидента

Подход: смотрим на всё, записываем интересное, собираем в голове картинку

=== Монтирование и автосбор ===

Под виндой
```bash
    FTK??
    FTK Imager
        Block Device
        File System
```

    Запуск
    
        Создать виртуалку, жёсткие диски всех типов

Под Kali

```bash
    qemu-nbd
        modprobe nbd
        qemu-nbd -c /dev/nbd0 -r \[clean\]\ Windows\ 10\ x64\ LTSC\ 2019-cl1.vmdk
        file -Ls /dev/nbd0
        ...
        qemu-nbd -d /dev/nbd0
    kpartx
        kpartx -a /dev/nbd0
        ...
        kpartx -d /dev/nbd0
    mount
        mount -o ro /dev/mapper/nbd0p3 /opt/
        ...
        umount /opt/
```

```bash 
    fls -r -m C: /dev/mapper/nbd0p3 > fls.txt
    mactime -b fls.txt > mactime.txt
        pv -d 116813 → смотреть прогресс доступа к файлам
    icat
        icat /dev/mapper/nbd0p3 107922-128-3 > recovered.file
```

```bash
    regripper → запустить плагины для конкретного куста
        SYSTEM: services сервисы, devclass mountdev usbdevices usbstor подключённые usb-девайсы, (network nic nic2 адаптеры и айпи, compname имя компа)
        SOFTWARE: soft_run автозапуск, regback кеш тасков шедулера, removdev юзб-девайсы, (apppaths imagefile перехваты ехешников, installer msis product uninstall установленные проги, networklist vista_wireless вайфайки, winver версия винды)
        NTUSER.DAT: user_run автозапуск, UserAssist запущенные ехешники, recentdocs открытые файлы
```

   ```bash
        php > $f = file("f:/tasks.txt");
        php > foreach ($f as $ln) { preg_match('#Path\s+:\s+(.+?)\|LastWrite\s+:\s+(.+?) \(UTC#s', $ln, $mt); $date = strtotime($mt[2]); echo date("r", $date) . " " . $mt[1] . "\n"; }
```

    photorec → карвинг из свободного пространства
    
    log2timeline??
    
        https://code.google.com/archive/p/log2timeline/
        
        log2timeline -r -p -o mactime -w l2t.txt /opt/



=== Где файлы ===

Юзера

```bash
    C:\Users\
    C:\Users\...\NTUSER.DAT — реестр
    C:\Users\...\AppData\ — от софта
    C:\Users\...\AppData\Local\Temp — временные
```

Системы

```bash
    C:\$Recycle.Bin\ — корзина
        08.07.2019  13:29               118 $IUKYRXB.conf ← метаданные
        07.07.2019  15:56               251 $RUKYRXB.conf ← выкинутый файл
    C:\ProgramData\ — от софта
    C:\Windows\System32\config — реестр
    C:\Windows\Temp — временные
    C:\Windows\System32\winevt\Logs — логи
  ```  


=== Ручной анализ ===

Как происходит инцидент:

    Попадание малвари — действие извне (прозохали), либо действие изнутри (сам запустил)
    
    Закрепление — прописывается в автозагрузку
    
    Деятельность — следы на файловой системе
    
    Последствия — что малварь сделала, что утекло
    
    IOC — хеши (md5), пути к файлам, сетевая активность, ключи реестра


Файлы

    автозагрузка и сервисы в реестре
    
    автозагрузка в таймлайне (Startup, Tasks)
    
  ```bash
        Users\user\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\*.lnk
        Windows\System32\Tasks\*\*
        Windows\SysWOW64\Tasks\*\*
    .exe в таймлайне
    Temp
  ```

Логи
    запущенные ехешники
    
    логи аутхов Security.evtx
    
        4625 = неудачный вход
        
        4624 = успешный вход
        
        4634 = выход
        
    логи psexec System.evtx
    
        7045 = создан сервис

Артефакты

```bash
    Internet Explorer
        Кеш — AppData\Local\Microsoft\Windows\Temporary Internet Files, AppData\Local\Microsoft\Windows\INetCache\IE\
        История — AppData\Local\Microsoft\Windows\History, AppData\Local\Microsoft\Windows\WebCache
        Куки — Users\...\Cookies, AppData\Local\Microsoft\Windows\INetCookies
```

```bash
    Firefox
        Кеш — AppData\Local\Mozilla\Firefox\Profiles\*\cache2\entries
        История — AppData\Roaming\Mozilla\Firefox\Profiles\*\places.sqlite (select * from moz_places;)
        Куки — AppData\Roaming\Mozilla\Firefox\Profiles\*\cookies.sqlite (select * from moz_cookies;)
```

```bash
    Chrome
        Кеш — AppData\Local\Google\Chrome\User Data\Default\Cache
        История — AppData\Local\Google\Chrome\User Data\Default\History (select * from urls;)
        Куки — AppData\Local\Google\Chrome\User Data\Default\Cookies (select * from cookies;)
```

```bash
    Thunderbird
        AppData\Roaming\Thunderbird\Profiles\*\Mail ImapMail
    Outlook
        AppData\Local\Microsoft\Outlook (readpst)
```


=== Дополнительно ===

```bash
reglookup-timeline → таймлайн ключей реестра
reglookup-recover → удалённые записи в реестре
dir /s /r c:\ | find ":$DATA"
    [ZoneTransfer]
    ZoneId=3
    HostUrl=https://www.aethereternity.com/coolprogram.exe
```



События с файлами

fls -r -m C: имя раздела > vivod.txt

Сделать таймлайн 

mactime -b vivod.txt > mactime.txt

М - модификация, а - доступ, c - поменяли атрибуты, b - создание файла (возможно)

Можно видеть удаленные файлы (deleted)

icat - чтобы прочитать файл 

icat имя раздела номер айнода (перед директорией C:)

regripper - выбираем хост реестра (куда примонтирована файловая система, windows, system32, confit, SOFTWARE/SYSTEM)

Задания планировщика в C:/windows/system.32

Image file execution options - запускаете exe, а винда к нему «дебагер»

photorec - файлы по сигнатурам

photorec раздел

Выбираем там диск и тд

samdump2 SYSTEM SAM

/winevent/LOG - system - логи пользователей

Открываем файл security в винде, выгружаем события в csv
