# ASTH Raspberry Pi 5 Hardware Baseline

Dokumen ini merekodkan baseline perkakasan yang telah disahkan untuk deployment ASTH. Raspberry Pi 5 ini mempunyai **2GB RAM**. Angka **32GB merujuk kepada kapasiti kad microSD sistem**, bukan kapasiti RAM. SSD luaran bukan sebahagian daripada baseline minimum, tetapi kini telah dipasang secara kekal untuk storan ASTH, NAS dan backup.

## 1. Spesifikasi Perkakasan Disahkan

| Komponen | Spesifikasi |
|---|---|
| Platform | Raspberry Pi 5 Model B Rev 1.1 |
| Pemproses | Pemproses 64-bit quad-core Cortex-A76 |
| Memori | 2GB LPDDR4X RAM |
| Storan sistem wajib | Kad microSD 32GB |
| Storan luaran | ASUS ROG STRIX Arion SSD, `/dev/sda2`, label `ROG`, kira-kira 512GB, NTFS |
| Status SSD | Mount kekal `/mnt/rog` melalui driver `ntfs3`; UUID `8E5AAE985AAE7C99`; `mnt-rog.mount` aktif |
| Sistem operasi disahkan | Debian GNU/Linux 13 (Trixie), arm64/aarch64 |
| Rangkaian berwayar | Gigabit Ethernet; aktif untuk deployment semasa |
| Wi-Fi terbina dalam | `wlan0`; access point `ASTH-PORTABLE`, 2.4 GHz (`bg`), channel 6 |
| Adapter Wi-Fi luaran | ALFA AWUS036NHV sebagai `wlan1`, driver `rtl8xxxu`; uplink `PHONE-UPLINK` telah disahkan |
| Sambungan periferal | Bluetooth 5.0 |
| USB | Dua port USB 3.0 dan dua port USB 2.0 |
| Paparan | Dua port micro HDMI dengan sokongan sehingga 4K60 |
| Pengembangan | Penyambung PCIe |
| Bekalan kuasa disyorkan | USB-C 5V/5A |
| Bekalan kuasa minimum | 5V/3A |
| Penyejukan | Penyejukan aktif dipasang dan disahkan |

### Baseline wajib dan storan luaran

Baseline minimum ASTH kekal Raspberry Pi 5, RAM 2GB, kad microSD 32GB, bekalan kuasa sesuai, sambungan LAN dan penyejukan aktif. SSD ASUS ROG STRIX Arion bukan storan sistem utama dan backup automatik masih belum production-ready, tetapi mount kekalnya serta servis NAS telah berjaya disahkan selepas reboot penuh.

Partition `/dev/sda2` menggunakan filesystem NTFS sedia ada melalui driver Linux `ntfs3` dan dipasang pada `/mnt/rog`. Entri `/etc/fstab` menggunakan UUID `8E5AAE985AAE7C99` dengan pilihan `uid=1000,gid=1000,umask=0022,nofail,x-systemd.device-timeout=10`. Mount dan unit `mnt-rog.mount` kembali aktif selepas reboot penuh; data sedia ada, termasuk `ASTH_BACKUP`, kekal tersedia dan ujian baca/tulis berjaya. SSD tidak diformat atau dipartition semula.

Semasa verifikasi, kapasiti dilaporkan kira-kira 477 GB keseluruhan, 305 GB digunakan dan 173 GB tersedia. `findmnt --verify` melaporkan 0 parse error dan 0 error; satu warning tentang jenis `ntfs` pada disk berbanding nama driver `ntfs3` adalah dijangka.

Seni bina storan ASTH akhir:

```text
/mnt/rog/ASTH/
├── nas/
│   ├── public
│   ├── staff
│   └── uploads
├── app-data
├── database
├── backups
├── logs
└── staging
```

Semua direktori dalam namespace `/mnt/rog/ASTH` dimiliki oleh `asthadmin`. Kandungan SSD lain yang tidak berkaitan kekal di luar namespace ini dan tidak boleh diubah. Samba menyediakan `ASTH-Public`, `ASTH-Staff` dan `ASTH-Uploads` sebagai share authenticated read/write, serta `ROG-Drive` sebagai share authenticated read-only.

### Baseline hotspot mudah alih

Wi-Fi terbina dalam Raspberry Pi ialah sebahagian daripada baseline dan kini disahkan sebagai interface hotspot:

| Item | Konfigurasi disahkan |
|---|---|
| Connection / SSID | `ASTH-PORTABLE` |
| Interface | `wlan0`, Wi-Fi terbina dalam Raspberry Pi |
| Mode | Access point |
| Radio | 2.4 GHz (`bg`), channel 6 |
| Security | WPA-PSK; kata laluan tidak direkodkan dalam repository |
| IPv4 | Shared, gateway `10.42.0.1/24` |
| Portable URL | `http://10.42.0.1` |
| Autoconnect | Ya, priority 100 |

Ethernet dan hotspot boleh beroperasi serentak. DHCP hotspot telah memberikan alamat kepada telefon dan laptop, Nginx port 80 boleh dicapai melalui `wlan0`, dan hotspot kembali secara automatik selepas reboot penuh.

Tiga mode rangkaian disokong: offline portable tanpa uplink, online portable melalui `PHONE-UPLINK` pada `wlan1`, dan office LAN melalui `eth0`. Dalam offline portable, paparan “connected without internet” adalah normal selagi `http://10.42.0.1` boleh dicapai. Dalam online portable, client `ASTH-PORTABLE` mendapat internet melalui forwarding `wlan0` ke `wlan1`.

ALFA AWUS036NHV pada `wlan1` ialah aksesori uplink, bukan interface hotspot. Dengan driver `rtl8xxxu`, ia bersambung sebagai client melalui profil NetworkManager `PHONE-UPLINK`. Semasa validasi tanpa Ethernet, `wlan1` menerima `10.13.68.119/24` dan default route menjadi `default via 10.13.68.67 dev wlan1`. Laptop pada `ASTH-PORTABLE` berjaya mencapai internet dan ASTH; 0% packet loss direkodkan. Credential `PHONE-UPLINK` kekal dalam NetworkManager tempatan dan tidak boleh dimasukkan ke repository.
### Seni bina router portable disahkan

```text
Phone hotspot
  → wlan1 / PHONE-UPLINK
  → Raspberry Pi 5 / UFW forwarding
  → wlan0 / ASTH-PORTABLE / 10.42.0.1
  → peranti client
```

UFW membenarkan forwarding `wlan0` ke `wlan1` untuk online portable dan mengekalkan forwarding `wlan0` ke `eth0` untuk office-LAN mode. SSH pada hotspot dibenarkan hanya dari `10.42.0.0/24` ke TCP port 22 pada `wlan0`. Akses `ssh asthadmin@10.42.0.1` telah disahkan.
## 2. Batasan Perkakasan Semasa

- RAM 2GB mengehadkan bilangan servis, worker aplikasi, proses latar dan pengguna serentak yang boleh ditampung dengan selesa.
- Kad microSD 32GB menyediakan ruang yang terhad selepas sistem operasi, aplikasi, media, pangkalan data, log dan backup diambil kira.
- Kad microSD mempunyai ketahanan tulis dan prestasi rawak yang lebih rendah berbanding SSD; penulisan log atau pangkalan data yang berlebihan boleh memendekkan jangka hayatnya.
- SSD menggunakan NTFS melalui `ntfs3`; pilihan mount, unit `mnt-rog.mount`, ruang tersedia dan pemilikan namespace ASTH perlu dipantau sebelum automasi backup production.
- Pemproses ini sesuai untuk aplikasi web ringan tetapi bukan untuk latihan model AI, inferens LLM besar, pemprosesan video berat atau analitik intensif.
- Prestasi berterusan boleh menurun akibat thermal throttling jika peranti tidak mempunyai penyejukan aktif dan aliran udara yang baik.
- Bekalan 5V/3A ialah minimum dan mungkin mengehadkan kuasa yang tersedia kepada periferal USB. Bekalan USB-C 5V/5A lebih sesuai untuk operasi stabil.
- Kapasiti dan prestasi rangkaian sebenar bergantung pada liputan Wi-Fi, kesesakan rangkaian dan bilangan klien serentak.

## 3. Workload ASTH yang Sesuai

- PWA atau aplikasi web responsif yang dilayan melalui rangkaian tempatan.
- Portal peserta, trainer dan admin ringkas.
- Modul pembelajaran berasaskan teks, imej yang dioptimumkan dan media bersaiz terkawal.
- Kuiz objektif, pemarkahan automatik, rekod cubaan dan progress peserta.
- Dashboard asas dan eksport CSV berskala kecil.
- FastAPI dengan satu atau sejumlah kecil worker Uvicorn.
- SQLite untuk dataset MVP dan kadar transaksi rendah.
- Smart Tutor ringan menggunakan carian kata kunci, topik atau indeks knowledge base tempatan yang kecil.
- Akses offline melalui Ethernet atau hotspot `ASTH-PORTABLE` pada `wlan0` untuk kumpulan pengguna terkawal.

## 4. Workload yang Perlu Dielakkan

- Menjalankan atau melatih LLM besar secara tempatan.
- Inferens AI berat, computer vision berterusan atau pemprosesan audio/video masa nyata.
- Transcoding video, penyuntingan media atau penyampaian banyak stream video serentak.
- Pangkalan data besar dengan penulisan serentak yang tinggi.
- Analitik data besar, digital twin kompleks atau beban IoT berskala tinggi.
- Terlalu banyak container, worker, servis latar atau alat pemantauan yang menggunakan RAM dengan banyak.
- Menjadikan Pi sebagai pelayan awam bertrafik tinggi tanpa hardening, pemantauan dan infrastruktur tambahan.
- Menyimpan satu-satunya salinan data penting atau backup pada kad microSD yang sama.

## 5. Seni Bina Deployment ASTH MVP yang Disyorkan

Gunakan seni bina satu nod yang ringan dan mengutamakan operasi offline:

1. Gunakan Raspberry Pi OS Lite 64-bit jika pemasangan semula praktikal. Jika mengekalkan Raspberry Pi OS sedia ada, nyahaktifkan desktop dan servis yang tidak diperlukan.
2. Jalankan Nginx sebagai reverse proxy serta pelayan aset statik yang telah dimampatkan dan di-cache.
3. Jalankan satu servis aplikasi FastAPI/Uvicorn melalui `systemd`, bermula dengan satu worker dan tambah hanya selepas ujian beban menunjukkan keperluan.
4. Gunakan SQLite untuk data MVP, dengan transaksi ringkas, indeks yang sesuai dan hanya satu servis aplikasi yang menulis kepadanya.
5. Simpan kandungan kursus dan knowledge base secara tempatan. Gunakan carian ringan dan jawapan bersumber, tanpa model generatif besar pada Pi.
6. Sediakan PWA kepada telefon atau komputer peserta melalui IP tempatan atau QR pada LAN.
7. Gunakan Gigabit Ethernet untuk sambungan utama apabila tersedia; gunakan Wi-Fi untuk akses peranti peserta.
8. Hadkan log, aktifkan log rotation dan jalankan backup berjadual ke storan berasingan.

Aliran deployment yang disyorkan:

`Peranti peserta → Ethernet LAN atau ASTH-PORTABLE (wlan0, 10.42.0.1) → Nginx → FastAPI/Uvicorn → SQLite dan kandungan tempatan`

Elakkan orkestrasi dan pecahan microservice untuk MVP. Satu aplikasi modular dengan bilangan proses minimum lebih sesuai dengan RAM 2GB.

## 6. Aksesori dan Naik Taraf Masa Hadapan

### Aksesori disyorkan

- Bekalan kuasa USB-C 5V/5A berkualiti.
- Casing berventilasi dengan kipas atau Active Cooler yang serasi.
- Kabel micro HDMI jika paparan tempatan diperlukan untuk pemasangan atau troubleshooting.
- Kabel Ethernet berkualiti untuk deployment tetap.
- Pembaca kad microSD atau kad microSD gantian untuk pemulihan.
- SSD kedua atau storan off-device yang sesuai untuk salinan backup tambahan.
- UPS atau power bank UPS yang sesuai bagi mengurangkan risiko kerosakan data akibat gangguan kuasa.

### Keutamaan naik taraf

1. Tentukan data aplikasi dan pangkalan data yang akan dipindahkan ke namespace SSD yang telah disediakan.
2. Tambah salinan backup off-device dan polisi retensi yang diuji.
3. Gunakan microSD berkapasiti lebih besar atau berkelas high-endurance apabila penggantian diperlukan.
4. Naik taraf kepada varian Raspberry Pi dengan RAM lebih besar jika bilangan pengguna, servis atau dataset meningkat.
5. Pisahkan pangkalan data atau workload AI ke server lain apabila keperluan melebihi skop MVP ringan.

## 7. Pertimbangan Storan dan Backup

- Kekalkan ruang kosong yang munasabah pada microSD 32GB; jangan biarkan log, cache, upload atau media memenuhi partition.
- Optimumkan imej dan video serta elakkan menyimpan media asal beresolusi tinggi pada Pi.
- Tetapkan log rotation, had saiz upload dan polisi pembersihan fail sementara.
- Simpan pangkalan data, fail konfigurasi bukan rahsia dan kandungan yang diperlukan dalam backup berjadual.
- Salin backup ke SSD/USB berasingan, NAS atau lokasi rangkaian lain. Backup pada microSD yang sama tidak melindungi daripada kegagalan kad.
- Backup manual sedia ada kekal di `/mnt/rog/ASTH_BACKUP`; recovery telah diuji menggunakan `rsync` dan perbandingan checksum SHA-256.
- Snapshot konfigurasi semasa disimpan di `/mnt/rog/ASTH_BACKUP/config-snapshot`.
- Gunakan `/mnt/rog/ASTH/backups` untuk seni bina backup ASTH yang baharu selepas schedule, retention, ownership dan failure handling diluluskan.
- Kekalkan sekurang-kurangnya satu salinan backup di luar Pi dan gunakan polisi retensi supaya beberapa titik pemulihan tersedia.
- Uji proses restore secara berkala; backup hanya berguna apabila pemulihan telah dibuktikan.
- Lakukan shutdown yang betul dan pertimbangkan UPS untuk mengurangkan risiko filesystem atau SQLite rosak akibat kehilangan kuasa.

## 8. Pertimbangan Prestasi dan Thermal

- Gunakan penyejukan aktif untuk operasi server berpanjangan dan pastikan lubang udara tidak terhalang.
- Pantau suhu, penggunaan RAM, swap, CPU, ruang storan dan kadar pertumbuhan log semasa ujian serta demo.
- Mulakan dengan satu worker aplikasi dan minimumkan servis latar. Tambah concurrency hanya berdasarkan hasil ujian pada perkakasan sebenar.
- Elakkan swap berlebihan kerana ia memperlahankan sistem dan menambah penulisan pada microSD.
- Uji dengan bilangan peranti serentak yang dijangka, termasuk login, pembukaan modul, kuiz, dashboard dan Smart Tutor.
- Gunakan aset termampat, pagination, caching dan query pangkalan data yang cekap.
- Gunakan Ethernet untuk sambungan rangkaian utama apabila tersedia dan `ASTH-PORTABLE` pada `wlan0` untuk akses portable offline.
- Kekalkan hotspot pada Wi-Fi terbina dalam `wlan0`; gunakan ALFA `wlan1` sebagai client melalui `PHONE-UPLINK` untuk online portable mode.
- Sahkan default route memilih `wlan1` apabila Ethernet ditanggalkan, atau `eth0` apabila office-LAN mode digunakan.
- Gunakan bekalan 5V/5A untuk kestabilan terbaik, terutama apabila SSD, kipas atau periferal USB turut disambungkan.

## 9. Kesimpulan

Raspberry Pi 5 Model B Rev 1.1 dengan **2GB LPDDR4X RAM** dan **kad microSD 32GB** sesuai untuk **lightweight ASTH infrastructure MVP**. SSD luaran kini mempunyai mount UUID yang reboot-verified serta namespace ASTH dan Samba NAS yang tersusun; backup/recovery manual telah dibuktikan, tetapi schedule dan retensi production masih perlu ditetapkan. Kesesuaian platform bergantung pada seni bina ringkas, servis minimum, satu worker aplikasi, kandungan dioptimumkan dan penyejukan aktif. Hotspot `ASTH-PORTABLE` menyokong operasi offline, online portable melalui `PHONE-UPLINK` pada `wlan1`, dan office LAN melalui `eth0`. Platform ini tidak patut dianggap sesuai untuk LLM besar, pemprosesan media berat atau skala pengguna tinggi.
