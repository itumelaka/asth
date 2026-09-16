# ASTH — Adaptive Smart Training Hub

> **One Hub. Smarter Learning. Better Skills.**

## Ringkasan

**Adaptive Smart Training Hub (ASTH)** ialah hab latihan digital mudah alih berasaskan Raspberry Pi 5. ASTH mengutamakan operasi **offline-first** untuk penyampaian kandungan latihan, akses setempat, Learning Hub, media, pembelajaran interaktif dan penjejakan kemajuan pelajar pada fasa akan datang.

ASTH direka supaya boleh beroperasi sebagai stesen latihan kendiri: skrin sentuh memaparkan konsol kesihatan, peserta menyambung ke hotspot tempatan, dan perkhidmatan latihan boleh dicapai tanpa bergantung pada internet.

## Sempadan Skop ASTH dan SPDK

Pembahagian tanggungjawab projek dikunci seperti berikut:

| Sistem | Tanggungjawab utama |
|---|---|
| **SPDK** | Pendaftaran kursus, pentadbiran peserta, jadual dan pentadbiran kursus, kehadiran, CPD, sijil, serta fungsi penyumbang/pentadbir |
| **ASTH** | Penyampaian latihan, akses kandungan setempat/offline, pembelajaran interaktif dan kemajuan pelajar |

ASTH **tidak sepatutnya menduplikasi sistem pengurusan kursus penuh SPDK**. Integrasi masa depan hendaklah ringan dan hanya menggunakan pengenal atau data yang diperlukan untuk enrolmen dan kemajuan pembelajaran.

Prinsip seni bina:

> **SPDK = pentadbiran kursus dan peserta**
> **ASTH = penyampaian latihan dan kemajuan pelajar**

## Modul Rintis

Modul pertama ASTH ialah:

**Sijil Kemahiran Malaysia — Operasi Ladang Poltri**

## LIVE — Platform dan Perkakasan Semasa

- Raspberry Pi 5 dengan 2 GB RAM.
- Debian 13 Trixie `arm64`.
- Sistem operasi masih dihoskan pada kad microSD.
- Storan luaran ROG dipasang pada `/mnt/rog` untuk media setempat.
- Samsung 980 PRO telah diuji sihat melalui enclosure USB.
- N04 PCIe/NVMe HAT diparkir buat masa ini kerana pautan PCIe luaran gagal.
- Skrin sentuh HDMI 1024x600 digunakan sebagai paparan fizikal.
- Wi-Fi terbina dalam digunakan untuk hotspot `ASTH-PORTABLE`.
- Tetikus Bluetooth AULA SC580, papan kekunci Bluetooth dan pembesar suara Bluetooth disambungkan dan berfungsi.
- Casing keras mudah alih masih dirancang.

Papan kekunci Bluetooth menyediakan akses pentadbiran tempatan. `Alt+F4` keluar daripada Chromium kiosk ke desktop Raspberry Pi. Pembesar suara Bluetooth tersedia untuk video latihan, audio dan main balik media. Periferal ini membolehkan ASTH beroperasi sebagai stesen latihan mudah alih yang berdikari.

## LIVE — Aliran Kiosk

```text
Boot → Raspberry Pi GUI → Chromium kiosk → ASTH Health Console
```

Dashboard kiosk dibuka pada:

`http://127.0.0.1/`

## LIVE — ASTH Health Console

Dashboard 1024x600 ditala untuk skrin LCD fizikal dengan kontras tinggi, warna status yang jelas, teks lebih gelap dan sempadan kad yang mudah dilihat. Maklumat kritikal dipaparkan tanpa perlu menatal.

Konsol memaparkan:

- status keseluruhan `SIHAT`, `AMARAN` atau `GANGGUAN`;
- penggunaan dan suhu CPU;
- penggunaan RAM;
- storan sistem dan storan media tempatan;
- alamat IP LAN dan hotspot;
- status `ASTH-PORTABLE` dan bilangan peranti tersambung;
- RX/TX serta graf rangkaian;
- status ASTH, Nginx, Jellyfin, Samba, Cockpit dan Uptime Kuma;
- status WireGuard dan ITUNAS Media secara berasingan.

Endpoint sedia ada termasuk `/health`, `/api/hub-status` dan `/learn/`.

## LIVE — Akses Peserta melalui QR

Butang besar **AKSES PELAJAR / QR** membuka paparan QR offline pada skrin sentuh.

- **SSID:** `ASTH-PORTABLE`
- **Portal:** `http://10.42.0.1/`

Aliran peserta:

1. Sambung ke Wi-Fi `ASTH-PORTABLE`.
2. Imbas QR Portal.
3. Akses perkhidmatan ASTH.

QR portal dijana dan dipaparkan secara setempat; ia tidak bergantung pada perkhidmatan internet luaran.

## LIVE — Seni Bina Media

### Local Media Storage

- Mount: `/mnt/rog`
- Digunakan untuk media setempat dan operasi offline.
- Jellyfin boleh menyampaikan kandungan daripada storan ini.

### ITUNAS Media

- Mount: `/mnt/office-movies`
- Sumber NAS: `//192.168.1.254/Movies`
- Dicapai melalui Office WireGuard.
- CIFS dipasang secara baca sahaja.
- Jellyfin boleh menggunakan sumber ini; main balik jarak jauh menggunakan lebar jalur internet di lokasi ASTH.

WireGuard kekal **informasi/baca sahaja** pada dashboard. Kawalan `CONNECT ITUNAS` dan `DISCONNECT ITUNAS` hanya mengawal mount/automount media ITUNAS dan tidak memulakan, menghentikan atau memulakan semula WireGuard.

## VERIFIED — Keselamatan Kawalan ITUNAS

Servis ASTH berjalan sebagai pengguna dan kumpulan `asthadmin`. Mutasi media menggunakan laluan tetap:

`/usr/bin/sudo -n /usr/bin/systemctl`

Hanya unit tetap berikut dibenarkan:

- `mnt-office\x2dmovies.automount`
- `mnt-office\x2dmovies.mount`

Hanya kombinasi `start` dan `stop` yang diperlukan dibenarkan melalui peraturan sudoers berskop sempit; `NOPASSWD: ALL` tidak digunakan. Endpoint kawalan skrin sentuh dihadkan kepada permintaan kawalan loopback/tempatan. Nama unit, arahan, laluan dan mount tidak diterima daripada klien.

## VERIFIED — Pengesanan dan Kawalan ITUNAS di Produksi

Pembetulan pengesanan telah dideploy dan disahkan pada Raspberry Pi. Parser kini memilih padanan tepat berikut walaupun target yang sama turut mempunyai entri `autofs`:

- mount point `/mnt/office-movies`;
- filesystem `cifs`;
- source `//192.168.1.254/Movies`;
- pilihan baca sahaja.

Pengesahan produksi menunjukkan `asth.service` aktif, dashboard berjaya dimuatkan dan `/api/hub-status` mengembalikan HTTP 200. ITUNAS Media pada mulanya dipaparkan sebagai `CONNECTED`. Tindakan **DISCONNECT ITUNAS** daripada skrin sentuh tempatan berjaya menukar status media kepada `DISCONNECTED` dan butang kepada **CONNECT ITUNAS**. Tindakan connect seterusnya berjaya mengembalikan ITUNAS Media kepada `CONNECTED`.

WireGuard kekal `CONNECTED` sepanjang kedua-dua tindakan. Ini mengesahkan kawalan dashboard hanya memutasi mount/automount ITUNAS dan tidak memutasi WireGuard.

## PARTIAL — Learning Hub

`/learn/` tersedia sebagai pintu masuk Learning Hub. Kandungan sebenar dan fungsi pembelajaran akan dibangunkan secara berperingkat.

## FUTURE — Hala Tuju Pembelajaran

- video dan kandungan latihan;
- nota, PDF dan bahan rujukan;
- latihan interaktif dan kuiz;
- kemajuan pelajar dan penyelesaian modul;
- integrasi ringan dengan SPDK untuk enrolmen atau kemajuan;
- pilihan adapter Wi-Fi USB sebagai uplink/klien berasingan daripada hotspot terbina dalam;
- casing keras mudah alih.

## Status Prototaip

ASTH kini ialah prototaip mudah alih yang berfungsi dengan kiosk automatik, konsol kesihatan skrin sentuh, hotspot peserta, akses QR offline, media tempatan, Jellyfin, seni bina media ITUNAS jarak jauh, WireGuard, periferal input/audio Bluetooth dan asas Learning Hub.

## Teknologi Utama

| Komponen | Teknologi |
|---|---|
| Antara muka | HTML, CSS, JavaScript |
| Backend | Python FastAPI |
| Web server | Nginx sebagai reverse proxy kepada FastAPI/Uvicorn |
| Hosting tempatan | Raspberry Pi 5, Debian 13 Trixie arm64 |
| Media | Jellyfin, storan `/mnt/rog`, CIFS ITUNAS baca sahaja |
| Rangkaian peserta | `ASTH-PORTABLE` pada Wi-Fi terbina dalam |
| Internet | Tidak wajib untuk perkhidmatan setempat |

## Rekod Pengesahan Terdahulu

- `ASTH-PORTABLE` telah disahkan pada `wlan0`, `10.42.0.1/24`, 5 GHz channel 36 dengan dua klien tersambung semula selepas migrasi.
- Ethernet `eth0` pernah disahkan sebagai uplink Gigabit; adapter USB Wi-Fi tidak digunakan dalam ujian tersebut.
- SSD ROG, Samba `ROG-Drive`, Jellyfin, Uptime Kuma dan Cockpit telah disahkan beroperasi dalam pengesahan terdahulu.
- Rollback manual aplikasi v0.4.0 ke v0.3.0 dan pemulihan semula telah berjaya diuji.
- Stack paparan `vc4-kms-v3d` telah dipulihkan dan disahkan.

Butiran sejarah dan operasi lanjut dikekalkan dalam [Project Status](PROJECT_STATUS.md), [Changelog](CHANGELOG.md), [Deployment Status](docs/DEPLOYMENT_STATUS.md) dan [Operations Runbook](docs/OPERATIONS_RUNBOOK.md).

## Dokumen Utama

- [Project Principles](docs/ASTH_PROJECT_PRINCIPLES.md)
- [Project Charter](docs/ASTH_PROJECT_CHARTER.md)
- [Executive Summary](docs/EXECUTIVE_SUMMARY.md)
- [MVP Scope](docs/MVP_SCOPE.md)
- [Development Roadmap](docs/DEVELOPMENT_ROADMAP.md)
- [Hardware Baseline](docs/HARDWARE_BASELINE.md)
- [Deployment Status](docs/DEPLOYMENT_STATUS.md)
- [Operations Runbook](docs/OPERATIONS_RUNBOOK.md)

## Pemilikan Projek

Projek ini dibangunkan untuk:

**Institut Teknologi Unggas**  
**Jabatan Perkhidmatan Veterinar Malaysia**

ASTH tidak menggantikan trainer atau SPDK. ASTH memperkukuh penyampaian latihan, pembelajaran kendiri dan pemantauan kemajuan/kompetensi peserta.
