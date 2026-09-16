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

## LIVE — Learning Hub Core v1

`/learn/` ialah pintu masuk Learning Hub offline-first. Core v1 kini mempunyai tiga Learning Pack live:

| Learning Pack | Sumber | Route |
|---|---|---|
| **Persediaan Reban & Brooder** | Kandungan latihan asas ASTH | `/learn/packs/reban-brooder/` |
| **Biosekuriti Asas Ladang** | WIM `A014-006-3:2022-C08` — Laksana Sistem Biosekuriti Ladang Poltri | `/learn/packs/biosekuriti/` |
| **Pengendalian Telur Sajian & Telur Tetasan** | WIM `A014-006-3:2022-C05` — Laksana Pengendalian Telur Poltri | `/learn/packs/pengendalian-telur/` |

Peserta telah disahkan boleh menyambung ke `ASTH-PORTABLE` dan membuka `http://10.42.0.1/` walaupun telefon melaporkan tiada akses Internet. Learning Hub kekal boleh dicapai secara setempat tanpa Internet luaran. Internet boleh digunakan sebagai tambahan, tetapi tidak diperlukan untuk penyampaian latihan setempat. Tiada tuntutan dibuat bahawa captive portal akan dibuka secara automatik pada semua peranti.

## VERIFIED — Kuasa Mudah Alih dan Media

- UGREEN powerbank berjaya menghidupkan spare Raspberry Pi 5, termasuk ujian `stress-ng` CPU empat teras selama 120 saat tanpa petunjuk throttling (`throttled=0x0` sebelum dan selepas; suhu selepas ujian 55.4 C).
- Raspberry Pi utama ASTH berjaya boot ke desktop menggunakan powerbank yang sama; `asth.service` aktif, `/learn/` mengembalikan HTTP 200 dan telefon berjaya mengakses Learning Hub melalui `ASTH-PORTABLE`.
- Jellyfin aktif dan dua peranti memainkan media ITUNAS melalui tunnel WireGuard `asth-office` dengan lancar semasa ujian; purata receive throughput yang diukur ialah kira-kira 64.51 Mbps.
- Sasaran media praktikal semasa ialah 1080p. Ujian ini bukan pengesahan throughput maksimum, sokongan 4K atau runtime powerbank jangka panjang.
- Monitor kekal menggunakan `DC 12V 2A` dan memerlukan penyelesaian kuasa 12V yang sesuai secara berasingan.

Dokumentasi pertandingan semasa merangkumi **Manual Penggunaan ASTH v1.2**, **Poster Konsep Operasi v1.2** dan **Infografik Learning Hub v1.2**. Bahan pertandingan akhir masih belum lengkap.

## FUTURE — Hala Tuju Pembelajaran

- perluasan video dan kandungan latihan;
- penambahan nota, PDF dan bahan rujukan;
- penambahan Learning Pack dan aktiviti interaktif;
- kemajuan pelajar dan penyelesaian modul;
- integrasi ringan dengan SPDK untuk enrolmen atau kemajuan;
- pilihan adapter Wi-Fi USB sebagai uplink/klien berasingan daripada hotspot terbina dalam;
- casing keras mudah alih.

## Status Prototaip

ASTH kini ialah prototaip mudah alih yang berfungsi dengan kiosk automatik, konsol kesihatan skrin sentuh, hotspot peserta, akses QR offline, tiga Learning Pack live, media tempatan, Jellyfin, seni bina media ITUNAS jarak jauh, WireGuard dan periferal input/audio Bluetooth.

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

Projek ini dibangunkan untuk:

**Institut Teknologi Unggas**  
**Jabatan Perkhidmatan Veterinar Malaysia**

ASTH tidak menggantikan trainer atau SPDK. ASTH memperkukuh penyampaian latihan, pembelajaran kendiri dan pemantauan kemajuan/kompetensi peserta.
