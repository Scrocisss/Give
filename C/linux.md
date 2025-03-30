# LINUX



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

git clone https://github.com/AsafEitani/Volatility3LinuxSymbols

```bash
apt update && apt install docker.io -y
systemctl start docker
systemctl enable --now docker
```

./build_profile.sh -f "/root/mnt/Forensics-Debian10(1)-Snapshot3.vmem" -v /root/volatility3 -k 4.19.0-22-amd64 -d debian:buster




