Title: Finding the SqueezeBox Radio Default SSH Passwort
Date: 2016-09-02
Author: Frederik
Slug: squeezebox-radio-ssh-default-password

***Note:*** *This post was originally hosted somewhere else. Republishing here for better visibility.
Also, the slimdevices wiki has a section on SSH authentication that [mentions the default password](http://wiki.slimdevices.com/index.php/Squeezebox_SSH_public_key_authentication). I must have missed it.*


## Prelude
I have a SqueezeBox Radio at home. It does a nice job of playing music from the internet and my local network.
The radio is clearly a linux device and it even listens on por 22. But I don't have the password and this always bummed me.
I can stream music to the radio from my local network using the logitech media server software.
When migrating server hardware, I looked around what to keep and noticed an `updates` folder in `/var/lib/squeezeboxserver`.
It turns out, that when the radio asks for updates, the local server is in charge of getting the update file and providing it
to the radio.

```
$ ls updates/
baby_7.7.3_r16676.bin  baby.version
$ ls -l updates/
-rw-r--r-- 1 freddy freddy 14771422 Sep  2 07:54 baby_7.7.3_r16676.bin
-rw-r--r-- 1 freddy freddy      139 Sep  2 07:53 baby.version
$ cat updates/baby.version
7.7.3 r16676
root@ec2mbubld01.idc.logitech.com Fri Feb 14 09:25:26 PST 2014
Base build revision:  bad080aecfec8226a4c1699b29d32cbba4ba396b
$ file updates/*
updates/baby_7.7.3_r16676.bin: Zip archive data, at least v2.0 to extract
updates/baby.version:          ASCII text
```
So, not knowing this, I had the firmware information on my disk all along? It is on.

## Understanding the Firmware Update

This turned out very simple and accessible. Thanks Logitech!
Unzipping yields multiple files, among them text files with metadata a `zImage` (~2.8M) and `root.cramfs` (13M).
Alright, let's mount the root filesystem and take a look around

```
$ mount -o loop root.cramfs /mnt/
$ cat /etc/shadow
root:$1$Ubbe0.Et$fxA9h74pN/qDu12VAGZca1:13826:0:99999:7:::
nobody:*:14062:0:99999:7:::
```

Asking a search engine yields nothing, so we have to crack it ourselves. Running `john` on this takes less than a second.

The password is **1234**

## Logging in
Logging in is a bit harder than it seems. The radio uses ancient SSH, which offers outdated legacy ciphers:

```
ssh  192.168.x.y -l root
Unable to negotiate with 192.168.x.y port 22: no matching key exchange method found. Their offer: diffie-hellman-group1-sha1
```
A quick search shows that we can re-enable the legacy crypto:
```
$ ssh -oKexAlgorithms=+diffie-hellman-group1-sha1 192.168.x.y -l root
root@192.168.x.y's password:

This network device is for authorized use only. Unauthorized or improper use
of this system may result in you hearing very bad music. If you do not consent
to these terms, LOG OFF IMMEDIATELY.

Ha, only joking. Now you have logged in feel free to change your root password
using the 'passwd' command. You can safely modify any of the files on this
system. A factory reset (press and hold add on power on) will remove all your
modifications and revert to the installed firmware.

Enjoy!
```
