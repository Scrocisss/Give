# LINUX

https://archive.org/details/access-data-ftk-imager-4.7.1

https://blog.desdelinux.net/ru/сбросить-пароль-root-grub/

mount -t ext4 /dev/sdb1 /root/deb

lsblk -f


unshadow:

https://askubuntu.com/questions/383057/how-to-decode-the-hash-password-in-etc-shadow

autopsy

https://habr.com/ru/companies/alexhost/articles/533260/


Linux table:

https://github.com/volatilityfoundation/volatility3?tab=readme-ov-file


unzip /root/mnt/linux.zip -d /root/mnt/linux_symbols






strings "/root/mnt/Forensics-Debian10(1)-Snapshot3.vmem" | grep -i "Debian"

```bash
grub_target_cc_version='gcc-8 (Debian 8.3.0-6) 8.3.0'
4.19.0-22-amd64 (debian-kernel@lists.debian.org) (gcc version 8.3.0 (Debian 8.3.0-6)) #1 SMP Debian 4.19.260-1 (2022-09-29)
Debian Secure Boot CA0
&Debian Secure Boot Signer 2022 - linux0
Debian Secure Boot CA
4.19.0-22-amd64 (debian-kernel@lists.debian.org) (gcc version 8.3.0 (Debian 8.3.0-6)) #1 SMP Debian 4.19.260-1 (2022-09-29)
Debian Secure Boot CA0
&Debian Secure Boot Signer 2022 - linux0
Debian Secure Boot CA
4.19.0-22-amd64 (debian-kernel@lists.debian.org) (gcc version 8.3.0 (Debian 8.3.0-6)) #1 SMP Debian 4.19.260-1 (2022-09-29)
Debian Secure Boot CA0
&Debian Secure Boot Signer 2022 - linux0
Debian Secure Boot CA
4.19.0-22-amd64 (debian-kernel@lists.debian.org) (gcc version 8.3.0 (Debian 8.3.0-6)) #1 SMP Debian 4.19.260-1 (2022-09-29)
```

apt install dwarf2json golang -y

git clone https://github.com/AsafEitani/Volatility3LinuxSymbols

Меняем Dockerfile

```bash
FROM debian:buster
COPY --from=golang:1.20-buster /usr/local/go/ /usr/local/go/
```

nameserver 8.8.8.8

```bash
apt update && apt install docker.io -y
systemctl start docker
systemctl enable --now docker
```

./build_profile.sh -f "/root/mnt/Forensics-Debian10(1)-Snapshot3.vmem" -v /root/volatility3 -k 4.19.0-22-amd64 -d debian:buster















iso    /root/mnt    vboxsf    defaults,uid=0,gid=0    0    0
mount -a












https://ptresearch.media/articles/top-10-artefaktov-linux-dlya-rassledovaniya-inczidentov?ysclid=m8q8qtyaua274473452


# С живой системой

cat ~/.bash_history

tail -n 15 /var/log/<file> по умолчанию выводит 10 строк, но при помощи параметра n их количество можно изменять.

tail -f -s 5 /var/log/<file> используется для отслеживания появления новых строк. Это аналог команды watch для тех же журналов. Может быть полезна для отслеживания определенных событий в реальном времени.

Например, историю входов пользователей можно посмотреть разными способами. Если мы имеем дело с SSH-протоколом (один из наиболее популярных способов удаленного управления хостом), можно использовать:

cat /var/log/auth.log | grep "sshd". Фильтрует логи аутентификации исключительно по демону sshd.


