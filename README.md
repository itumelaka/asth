# ASTH — Adaptive Smart Training Hub

> **One Hub. Smarter Learning. Better Skills.**

## Ringkasan

**Adaptive Smart Training Hub (ASTH)** ialah platform latihan digital TVET yang dibangunkan untuk Institut Teknologi Unggas, Jabatan Perkhidmatan Veterinar. Sistem ini direka sebagai **web app / Progressive Web App (PWA)** yang boleh dihoskan pada Raspberry Pi 5 dan digunakan melalui telefon, tablet atau komputer dalam rangkaian Wi-Fi tempatan.

Perkakasan semasa yang disahkan ialah Raspberry Pi 5 dengan **2 GB RAM**. Raspberry Pi OS masih boot dan berjalan daripada **kad microSD 32 GB**. Pemasangan akhir casing/LCD dan NVMe masih belum lengkap. Arah pilihan selepas perkakasan dipasang dan lulus ujian ialah memindahkan keseluruhan sistem operasi ke NVMe serta mengekalkan microSD sebagai media pemulihan.

ASTH menggabungkan:

- modul pembelajaran interaktif;
- SOP digital;
- kuiz dan penilaian;
- rekod kemajuan peserta;
- dashboard trainer;
- Smart Tutor berasaskan knowledge base tempatan;
- operasi offline-first;
- pengembangan masa depan kepada IoT, sensor dan hybrid AI.

## Modul Rintis

Modul pertama ASTH ialah:

**Sijil Kemahiran Malaysia — Operasi Ladang Poltri**

## Masalah Yang Diselesaikan

Latihan TVET semasa masih banyak bergantung kepada PDF, slaid, nota bercetak dan sambungan internet. ASTH menyediakan satu platform latihan yang:

- mudah dibawa;
- kos rendah;
- boleh digunakan tanpa internet;
- sesuai untuk ladang, makmal, bengkel dan bilik latihan;
- membolehkan bahan latihan digunakan semula;
- membantu trainer memantau kemajuan peserta.

## Konsep Operasi

1. Raspberry Pi 5 dihidupkan.
2. Peserta menyambung kepada Wi-Fi ASTH.
3. Peserta mengimbas QR atau membuka alamat tempatan.
4. Web app ASTH dibuka.
5. Peserta memilih modul, belajar, menjawab kuiz dan menerima maklum balas.
6. Trainer melihat kemajuan melalui dashboard.

## Teknologi Dicadangkan

| Komponen | Teknologi |
|---|---|
| Antara muka | HTML, CSS, JavaScript |
| Jenis aplikasi | Progressive Web App |
| Backend | Python FastAPI |
| Database | SQLite |
| Hosting tempatan | Raspberry Pi 5 |
| Web server | Nginx sebagai reverse proxy kepada FastAPI/Uvicorn |
| Smart Tutor | Local knowledge base |
| Internet | Tidak wajib |
| Cloud AI/API | Pilihan dan terkawal |

Seni bina MVP menggunakan satu aplikasi modular, SQLite dan bilangan proses minimum. Pengembangan masa depan boleh dibuat melalui storan NVMe, servis luaran terkawal atau pengasingan workload tanpa mengubah arah asas projek.

## Infrastruktur disahkan pada 6 September 2026

SSD ROG kini dipasang secara kekal di `/mnt/rog` menggunakan `ntfs3` dengan uid/gid 1000 dan kembali selepas reboot. Share Samba `ROG-Drive` menyokong tulis serta penamaan semula fail dari Windows. Jellyfin tersedia melalui LAN di `http://192.168.100.187:8096` dan ASTH-PORTABLE di `http://10.42.0.1:8096`, dengan akses UFW terhad kepada rangkaian tempatan tersebut. Jellyfin ialah servis media tambahan, bukan keperluan teras MVP ASTH; elakkan transcoding berat atau banyak strim serentak pada Pi 2 GB RAM. Lihat [Deployment Status](docs/DEPLOYMENT_STATUS.md) dan [Operations Runbook](docs/OPERATIONS_RUNBOOK.md).

## Rekod aplikasi dan perkakasan pada 13 Ogos 2026

- **CONFIRMED:** Akses pemulihan fizikal melalui HDMI dan papan kekunci USB lengkap; login tempatan `asthadmin`, pemulihan kata laluan melalui boot recovery, `sudo` (`SUDO_OK`) dan reboot normal telah disahkan.
- **CONFIRMED:** Rangkaian portable ASTH dan aplikasi web FastAPI v0.4.0 beroperasi pada Raspberry Pi.
- **VERIFIED:** `ASTH-PORTABLE` kekal pada built-in Wi-Fi `wlan0` dengan `10.42.0.1/24` dan kini menggunakan 5 GHz, channel 36 (5180 MHz), lebar 20 MHz. Dua peranti berjaya menyambung semula dan konfigurasi ini kekal selepas reboot.
- **CONFIRMED:** Uplink internet semasa ialah Gigabit Ethernet `eth0` (`1.1.1.1 via 192.168.100.1 dev eth0 src 192.168.100.187`); Alfa USB `wlan1` disconnected dan tidak terlibat dalam ujian 13 Ogos.
- **OBSERVED:** Satu speedtest melalui hotspot selepas migrasi merekodkan ping 25 ms, download 48.9 Mbps dan upload 35.8 Mbps. Ini bukan prestasi terjamin atau gigabit Wi-Fi; hotspot 20 MHz pada Raspberry Pi kekal sebagai kemungkinan kekangan tempatan berbanding uplink Ethernet 1000 Mbps full-duplex.
- **CONFIRMED:** Halaman utama `/` memaparkan status hub, statistik rangkaian masa nyata dan pautan ke Learning Hub, Uptime Kuma serta Cockpit.
- **VERIFIED:** Rollback manual aplikasi daripada ASTH v0.4.0 kepada salinan v0.3.0 dan pemulihan semula kepada v0.4.0 berjaya; kedua-dua health check akhir mengembalikan HTTP 200 dan keadaan `healthy`.
- **VERIFIED:** `vc4-kms-v3d` diaktifkan semula; selepas reboot, peranti DRI dan modul kernel `vc4`/`v3d` tersedia, `rp1-test.service` aktif, `asth.service` aktif dan tiada unit systemd gagal.
- **PARTIAL:** `/learn/` tersedia sebagai Learning Hub berasingan, tetapi kandungan sebenar belum dimasukkan.
- **DEFERRED:** Ujian backup/restore database ditangguhkan kerana `/var/lib/asth/db` kosong dan aplikasi semasa belum mempunyai fail atau rujukan database.
- **PENDING:** MHS35 LCD belum dipasang dan `MHS35-show` tidak dijalankan semasa pemulihan; NVMe controller/HAT belum tiba; konfigurasi kiosk LCD, migrasi storan dan sinkronisasi source v0.4.0 dari Pi ke repository ini masih belum lengkap.

Butiran semasa direkodkan dalam [Deployment Status](docs/DEPLOYMENT_STATUS.md).


## Office Connectivity / Always-On Office Tunnel

Seni bina yang disahkan melalui validasi rangkaian yang dibekalkan:

```text
ASTH-PORTABLE (10.42.0.0/24)
    -> Pi ASTH
    -> WireGuard asth-office
    -> UDM Pro
    -> Office LAN (192.168.1.0/24)
```

- Interface `asth-office` menggunakan subnet WireGuard `192.168.3.0/24`; servis `wg-quick@asth-office.service` bermula secara automatik melalui systemd.
- Split tunnel menghantar trafik `192.168.1.0/24` melalui `asth-office`. Trafik Internet biasa kekal melalui Internet rumah.
- Polisi routed UFW diperlukan untuk membenarkan `10.42.0.0/24` dari `wlan0` ke `192.168.1.0/24` melalui `asth-office`.
- Router upstream mempunyai port forward UDP 51820 ke WAN UDM Pro.
- Semasa validasi yang dibekalkan, servis dan interface aktif selepas reboot serta laluan pejabat tersedia. Pi mencapai `192.168.1.254`, dan klien ASTH-PORTABLE mencapai TCP 80 serta 445 pada pelayan tersebut. Alamat ini ialah sasaran ujian, bukan kebergantungan tetap tunnel.

HUD **Office Tunnel** menggunakan cache metrik 30 saat dan hanya memaparkan Connected, Disconnected atau Unavailable. Connected memerlukan servis aktif, interface `asth-office` wujud dan laluan tepat `192.168.1.0/24` menggunakan interface tersebut. Ini ialah petunjuk keadaan servis, interface dan laluan setempat, bukan jaminan capaian aplikasi pejabat; tiada ping atau probe pelayan dilakukan.

Validasi langsung menunjukkan pengguna aplikasi `asthadmin` tidak boleh menjalankan `wg show` tanpa keistimewaan tambahan. ASTH sengaja tidak menaikkan keistimewaan hanya untuk pemantauan HUD. Pemeriksaan menggunakan keadaan systemd, kewujudan interface dan output laluan setempat yang tidak memerlukan sudo; kegagalan pemeriksaan menghasilkan Unavailable.

Private key, pre-shared key, kelayakan, QR code dan konfigurasi penuh WireGuard tidak boleh dikomit. API hanya menambah `office_tunnel`; ia tidak mendedahkan identiti peer, endpoint atau output mentah sistem.

Integrasi media pejabat turut disahkan pada 6 September 2026. Share SMB3 `Movies` pada pelayan Windows `ITUNAS` dipasang secara read-only di `/mnt/office-movies` melalui tunnel `asth-office`, kekal tersedia selepas reboot, dan digunakan oleh library Jellyfin `Movies ITUNAS`. Jellyfin Media Player 1.12.0 pada `BurnRogZ13` memainkan *Thor: Love and Thunder* melalui Direct Play tanpa proses transcoding `ffmpeg` aktif. Library tempatan `/mnt/rog/Movies` kekal berasingan. Lihat [Office Media and Jellyfin Integration](docs/OFFICE_MEDIA_JELLYFIN.md) untuk seni bina, kawalan akses dan batas operasi yang disahkan.

## Remote Access / Tailscale

Pada 6 September 2026, akses peribadi jarak jauh ke ASTH dan Jellyfin disahkan dari telefon Android menggunakan data selular melalui Tailscale. Pi `asth-pi` menjalankan Tailscale 1.102.3 pada alamat overlay `100.87.140.5`; Service Hub, HUD dan Jellyfin `asth-media` 10.11.11 boleh dicapai tanpa pendedahan langsung servis ASTH ke Internet awam. Tailscale menyediakan akses klien dipercayai ke Pi, manakala tunnel WireGuard `asth-office` yang berasingan menghubungkan Pi ke media pejabat.

Keadaan keselamatan Tailscale masih **PARTIAL / PENDING HARDENING**. Peraturan khusus pemilik kepada port 22, 80, 3001, 8096 dan 9090 pada Pi telah dibuat, tetapi peraturan broad allow-all sedia ada masih aktif dan belum diuji selepas dinyahaktifkan. Lihat [Tailscale Remote Access](docs/REMOTE_ACCESS_TAILSCALE.md) untuk bukti, sempadan keselamatan dan kerja pengukuhan yang masih diperlukan.

## Dokumen Utama

- [Project Principles](docs/ASTH_PROJECT_PRINCIPLES.md)
- [Project Charter](docs/ASTH_PROJECT_CHARTER.md)
- [Executive Summary](docs/EXECUTIVE_SUMMARY.md)
- [MVP Scope](docs/MVP_SCOPE.md)
- [Development Roadmap](docs/DEVELOPMENT_ROADMAP.md)
- [Hardware Baseline](docs/HARDWARE_BASELINE.md)
- [Deployment Status](docs/DEPLOYMENT_STATUS.md)
- [Operations Runbook](docs/OPERATIONS_RUNBOOK.md)
- [Office Media and Jellyfin Integration](docs/OFFICE_MEDIA_JELLYFIN.md)
- [Tailscale Remote Access](docs/REMOTE_ACCESS_TAILSCALE.md)

## Pemilikan Projek

Projek ini dicadangkan untuk dibangunkan di bawah:

**Institut Teknologi Unggas**  
**Jabatan Perkhidmatan Veterinar Malaysia**

ASTH bukan dibangunkan untuk menggantikan trainer. ASTH dibangunkan untuk memperkukuh penyampaian latihan, pembelajaran kendiri dan pemantauan kompetensi peserta.
