# ASTH Project Status

**Tarikh status:** 16 September 2026
**Versi aplikasi live yang direkodkan:** v0.4.0
**Fasa semasa:** Learning Hub Core v1 dengan tiga Learning Pack live; penyediaan bukti pertandingan dan pemantapan perkakasan mudah alih
**Status keseluruhan:** Aktif — operasi offline-first, penyampaian setempat dan tiga Learning Pack telah disahkan
**Tindakan utama seterusnya:** Lengkapkan bukti pertandingan, ujian pengguna/pilot, BOM/kos dan penyelesaian kuasa 12V monitor tanpa mengganggu Core v1.

## Sempadan Skop

- **SPDK:** pendaftaran kursus, pentadbiran peserta, jadual/pentadbiran kursus, kehadiran, CPD, sijil dan fungsi penyumbang/pentadbir.
- **ASTH:** penyampaian latihan, akses setempat/offline, pembelajaran interaktif dan kemajuan pelajar.
- ASTH tidak akan menduplikasi sistem pengurusan kursus penuh SPDK.
- Integrasi masa depan hanya menggunakan pengenal atau data minimum yang diperlukan untuk enrolmen dan kemajuan.

## LIVE — Sistem Semasa

### Platform dan Perkakasan

- Raspberry Pi 5, 2 GB RAM, Debian 13 Trixie `arm64`.
- Sistem operasi masih berjalan daripada microSD.
- Samsung 980 PRO telah diuji sihat melalui enclosure USB dan storan ROG dipasang pada `/mnt/rog`.
- N04 PCIe/NVMe HAT diparkir kerana pautan PCIe luaran gagal.
- Skrin sentuh HDMI 1024x600 digunakan untuk kiosk.
- Wi-Fi terbina dalam `wlan0` menyediakan hotspot `ASTH-PORTABLE` pada `10.42.0.1/24`.
- Casing keras mudah alih belum dimuktamadkan.

### Periferal Bluetooth

- Tetikus Bluetooth AULA SC580 disambungkan dan berfungsi.
- Papan kekunci Bluetooth menyediakan akses pentadbiran tempatan; `Alt+F4` keluar daripada Chromium kiosk ke desktop Raspberry Pi.
- Pembesar suara Bluetooth tersedia untuk video latihan, audio dan media.
- Periferal ini membolehkan ASTH beroperasi sebagai stesen latihan mudah alih kendiri.

### Aliran Kiosk

```text
Boot → Raspberry Pi GUI → Chromium kiosk → ASTH Health Console
```

URL dashboard kiosk: `http://127.0.0.1/`

### ASTH Health Console

Dashboard fizikal 1024x600 menggunakan gaya kontras tinggi untuk LCD dan memaparkan tanpa skrol:

- keseluruhan `SIHAT`, `AMARAN` atau `GANGGUAN`;
- CPU dan suhu, RAM serta storan sistem;
- Local Media Storage;
- LAN IP, hotspot IP, status `ASTH-PORTABLE` dan peranti tersambung;
- RX/TX dan graf rangkaian;
- ASTH, Nginx, Jellyfin, Samba, Cockpit dan Uptime Kuma;
- WireGuard dan ITUNAS Media sebagai status berasingan.

Route utama yang dikekalkan: `/`, `/health`, `/api/hub-status` dan `/learn/`.

### Akses Peserta

- Dashboard menyediakan butang **AKSES PELAJAR / QR**.
- SSID: `ASTH-PORTABLE`.
- Portal: `http://10.42.0.1/`.
- Aliran offline: sambung ke hotspot, imbas QR Portal, kemudian akses perkhidmatan ASTH.
- QR portal berfungsi tanpa perkhidmatan internet luar.

### Learning Hub Core v1

Tiga Learning Pack kini live:

1. **Persediaan Reban & Brooder** — `/learn/packs/reban-brooder/`
2. **Biosekuriti Asas Ladang** — `/learn/packs/biosekuriti/`
   - Sumber: WIM `A014-006-3:2022-C08` — Laksana Sistem Biosekuriti Ladang Poltri.
3. **Pengendalian Telur Sajian & Telur Tetasan** — `/learn/packs/pengendalian-telur/`
   - Sumber: WIM `A014-006-3:2022-C05` — Laksana Pengendalian Telur Poltri.

Pack 2 dan Pack 3 telah dideploy ke produksi. Learning Hub Core v1 kini menyediakan tiga pack yang boleh dicapai secara setempat.

### Media

- **Local Media Storage:** `/mnt/rog`, untuk penggunaan setempat/offline.
- **ITUNAS Media:** `/mnt/office-movies`, sumber CIFS baca sahaja `//192.168.1.254/Movies` melalui Office WireGuard.
- Jellyfin boleh menggunakan media tempatan dan ITUNAS; main balik daripada ITUNAS menggunakan lebar jalur internet lokasi ASTH.
- WireGuard hanya dipantau secara informasi dan tidak dimutasi oleh dashboard.
- Kawalan ITUNAS hanya mengawal mount/automount media, bukan tunnel WireGuard.

## VERIFIED — Pengesahan Operasi dan Keselamatan

### Pengesahan Offline ASTH-PORTABLE — 16 September 2026

- Peranti peserta berjaya menyambung ke `ASTH-PORTABLE` walaupun telefon memaparkan `No Internet access`.
- Portal tempatan kekal boleh dicapai pada `http://10.42.0.1/`.
- Learning Hub boleh digunakan tanpa sambungan Internet luaran.
- Keputusan ini menyokong kenyataan bahawa ASTH tidak memerlukan Internet untuk penyampaian latihan setempat; Internet hanya tambahan.
- Tiada tuntutan dibuat bahawa captive portal akan dilancarkan secara automatik.

### Pengesahan UGREEN Powerbank — 16 September 2026

Spare Raspberry Pi 5:

- boot selesai;
- LAN dan SSH aktif;
- `vcgencmd get_throttled` menunjukkan `throttled=0x0`;
- `dmesg` tidak menunjukkan amaran voltan atau throttle;
- ujian `stress-ng` CPU empat teras berjalan selama 120 saat;
- selepas ujian, `throttled=0x0` dan suhu direkodkan pada 55.4 C.

Raspberry Pi utama ASTH:

- berjaya boot ke desktop menggunakan UGREEN powerbank;
- `vcgencmd get_throttled` menunjukkan `throttled=0x0`;
- `asth.service` aktif dan `/learn/` mengembalikan HTTP 200;
- telefon berjaya menyambung ke `ASTH-PORTABLE` dan membuka Learning Hub.

Had bukti: ujian ini tidak mengesahkan runtime jangka panjang, pensijilan beban penuh ASTH atau kuasa monitor. Monitor `DC 12V 2A` masih memerlukan penyelesaian kuasa 12V yang sesuai secara berasingan.

### Kawalan ITUNAS

- Servis ASTH berjalan sebagai `User=asthadmin` dan `Group=asthadmin`.
- Mutasi terhad menggunakan `/usr/bin/sudo -n /usr/bin/systemctl`.
- Hanya unit `mnt-office\x2dmovies.automount` dan `mnt-office\x2dmovies.mount` boleh dimutasi.
- Hanya operasi `start` dan `stop` yang ditetapkan dibenarkan; tiada `NOPASSWD: ALL`.
- Disconnect menghentikan automount sebelum mount supaya akses latar tidak mengaktifkannya semula.
- Connect memeriksa WireGuard tetapi tidak memulakan atau memulakan semula tunnel.
- Endpoint mutasi dihadkan kepada permintaan loopback/kawalan tempatan dan tidak menerima unit atau arahan daripada klien.
- Timeout, kegagalan tersanitasi dan pengesahan status selepas tindakan diliputi ujian setempat.

### Pengesanan dan Kawalan ITUNAS di Produksi

- Pembetulan parser exact-match telah dideploy pada Raspberry Pi dan mengesan entri CIFS baca sahaja `//192.168.1.254/Movies` pada `/mnt/office-movies` walaupun entri `autofs systemd-1` turut wujud pada target yang sama.
- `asth.service` berjaya dimulakan semula dan kekal `active/running`.
- Dashboard berjaya dimuatkan dan `/api/hub-status` mengembalikan HTTP 200.
- WireGuard dan ITUNAS Media pada mulanya menunjukkan `CONNECTED`.
- **DISCONNECT ITUNAS** berjaya dari dashboard skrin sentuh tempatan; ITUNAS Media bertukar kepada `DISCONNECTED` dan butang bertukar kepada **CONNECT ITUNAS**.
- **CONNECT ITUNAS** kemudian berjaya dan ITUNAS Media kembali kepada `CONNECTED`.
- WireGuard kekal `CONNECTED` sepanjang ujian disconnect dan connect.
- Keputusan ini mengesahkan dashboard hanya mengawal unit mount/automount ITUNAS dan tidak memutasi WireGuard.

### Office WireGuard Media dan Jellyfin

- Split tunnel `asth-office` antara `ASTH-PORTABLE` (`10.42.0.0/24`) dan LAN pejabat (`192.168.1.0/24`) telah disahkan kekal selepas reboot.
- Kandungan SMB3 berautentikasi daripada pelayan Windows `ITUNAS` dipasang baca sahaja pada `/mnt/office-movies` menggunakan kelayakan root-only yang dilindungi serta ownership/mode yang serasi dengan Jellyfin.
- Systemd automount disusun dan diperlukan selepas `wg-quick@asth-office.service`; mount kembali tersedia selepas reboot.
- Jellyfin mengekalkan `Movies ITUNAS` sebagai library berasingan daripada `/mnt/rog/Movies`.
- Jellyfin Media Player 1.12.0 pada `BurnRogZ13` telah memainkan *Thor: Love and Thunder* melalui Direct Play tanpa proses transcoding `ffmpeg` aktif.
- Jellyfin service disahkan aktif semasa ujian 16 September 2026.
- Dua peranti menjalankan main balik aktif daripada ITUNAS melalui tunnel WireGuard `asth-office`; kedua-dua stream diperhatikan bermain dengan lancar.
- Purata receive throughput semasa ujian dua peranti ialah kira-kira 64.51 Mbps.
- Satu snapshot throughput sementara 215.73 Mbps kekal **tidak divalidasi** dan tidak digunakan sebagai bukti tiga peranti kerana iPad belum memulakan main balik pada ketika itu.
- Ujian ini tidak menentukan throughput maksimum WireGuard atau menjamin main balik 4K. Sasaran praktikal kandungan media ASTH kekal 1080p.
- Rujuk [Office Media and Jellyfin Integration](docs/OFFICE_MEDIA_JELLYFIN.md).

### Dokumentasi Pertandingan — 16 September 2026

- **Manual Penggunaan ASTH v1.2** telah dikemas kini untuk tiga Learning Pack live, bukti ujian powerbank, bukti WireGuard/ITUNAS/Jellyfin dan status Core v1.
- **Poster Konsep Operasi v1.2** telah dikemas kini.
- **Infografik Learning Hub v1.2** telah dikemas kini.
- Infografik lain tidak diubah apabila kandungannya masih semasa.
- Bahan akhir pertandingan NTRIC belum dinyatakan lengkap.

### Tailscale Remote Access

- Tailscale 1.102.3 dipasang daripada repositori rasmi Debian Trixie dan `tailscaled.service` aktif pada peranti Pi `asth-pi`.
- Telefon Android melalui data selular berjaya membuka ASTH Service Hub melalui alamat overlay peribadi; HUD kekal berfungsi dan memaparkan Office Tunnel sebagai connected.
- Selepas Jellyfin Remote Access diaktifkan, `asth-media` 10.11.11, web interface dan library `Movies ITUNAS` boleh dicapai melalui Tailscale.
- Akses ini menggunakan overlay peribadi dan bukan pendedahan terus ASTH kepada Internet awam.
- Rujuk [Tailscale Remote Access](docs/REMOTE_ACCESS_TAILSCALE.md).

### Pengesahan Terdahulu yang Masih Relevan

- Hotspot `ASTH-PORTABLE` telah disahkan pada 5 GHz channel 36, lebar 20 MHz; dua klien menyambung semula dan tetapan kekal selepas reboot.
- Profil 2.4 GHz `ASTH-PORTABLE-2G-BACKUP` dikekalkan dengan autoconnect dimatikan untuk rollback.
- Ethernet `eth0` pernah menyediakan laluan internet dan berunding pada 1000 Mbps full-duplex; Alfa USB `wlan1` tidak terlibat dalam ujian tersebut.
- Satu ujian hotspot merekodkan ping 25 ms, muat turun 48.9 Mbps dan muat naik 35.8 Mbps. Ini ialah satu pemerhatian, bukan prestasi terjamin.
- SSD ROG kekal pada `/mnt/rog`; Samba `ROG-Drive` telah disahkan menyokong tulis dan penamaan semula daripada Windows.
- Jellyfin, Uptime Kuma dan Cockpit telah disahkan tersedia dalam pemeriksaan terdahulu.
- Rollback manual aplikasi v0.4.0 ke v0.3.0 dan pemulihan semula ke v0.4.0 menghasilkan HTTP 200 dan keadaan sihat.
- Stack paparan `vc4-kms-v3d`, peranti DRI serta modul `vc4`/`v3d` telah dipulihkan dan disahkan.
- Akses pemulihan fizikal, login tempatan `asthadmin`, pemulihan kata laluan, sudo dan reboot normal telah disahkan.

## PENDING — Belum Selesai atau Belum Disahkan di Produksi

### Tailscale Hardening

- Least-privilege hardening masih **PARTIAL / PENDING**.
- Peraturan khusus pemilik telah mengehadkan akses kepada Pi pada port 22, 80, 3001, 8096 dan 9090, tetapi peraturan broad allow-all sedia ada untuk semua pengguna/peranti masih aktif.
- Peraturan broad tersebut belum dibuang dan peraturan terhad belum disahkan sebagai satu-satunya laluan akses.

### Operasi dan Kandungan

- Jalankan ujian pilot/pengguna dan rekodkan bukti penggunaan.
- Lengkapkan BOM dan anggaran kos.
- Siapkan poster pertandingan A1 akhir.
- Siapkan slide deck akhir.
- Siapkan video pertandingan 3–5 minit.
- Siapkan laporan inovasi akhir.
- Tentukan penyelesaian kuasa sesuai untuk monitor `DC 12V 2A`; powerbank Pi tidak disahkan membekalkan monitor.
- Tentukan pasukan projek, peranan, penjaga sistem dan maintenance window.
- Sahkan modul sumber, SOP dan keperluan pertandingan.
- Jalankan ujian backup/restore apabila modul berpangkalan data benar-benar wujud; `/var/lib/asth/db` direkodkan kosong dalam pengesahan terdahulu.
- Sahkan semula Alfa `wlan1` sebagai uplink tanpa wayar jika adapter itu digunakan pada masa depan.
- Selesaikan pemasangan dalam casing keras mudah alih dan jalankan validasi pasca-pemasangan.

## FUTURE — Hala Tuju

- Kandungan video latihan, nota, PDF dan rujukan.
- Latihan interaktif dan kuiz.
- Penjejakan kemajuan pelajar dan penyelesaian modul.
- Integrasi ringan SPDK menggunakan data minimum untuk enrolmen atau kemajuan.
- Adapter Wi-Fi USB pilihan untuk memisahkan uplink/klien daripada hotspot `wlan0`.
- Penilaian semula storan NVMe hanya jika laluan PCIe luaran yang serasi dan stabil tersedia.
- Smart Tutor atau fungsi AI tempatan hanya selepas asas kandungan, prestasi dan tadbir urus disahkan.

## Ringkasan Status Prototaip

ASTH ialah prototaip mudah alih yang berfungsi dengan:

- kiosk automatik dan konsol kesihatan skrin sentuh;
- hotspot peserta dan akses QR offline;
- storan media tempatan dan Jellyfin;
- seni bina media ITUNAS melalui WireGuard;
- periferal input dan audio Bluetooth;
- Learning Hub Core v1 dengan tiga Learning Pack live.

Fungsi pengurusan kursus penuh kekal dalam SPDK. ASTH menumpukan penyampaian latihan dan kemajuan pelajar.
