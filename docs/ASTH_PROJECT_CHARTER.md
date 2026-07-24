# ASTH Project Charter

## 1. Maklumat Projek

**Nama projek:** Adaptive Smart Training Hub  
**Singkatan:** ASTH  
**Tagline:** One Hub. Smarter Learning. Better Skills.  
**Organisasi:** Institut Teknologi Unggas, Jabatan Perkhidmatan Veterinar Malaysia  
**Modul rintis:** Sijil Kemahiran Malaysia — Operasi Ladang Poltri  
**Jenis projek:** Platform latihan digital TVET, offline-first, Raspberry Pi powered  
**Versi charter:** 0.1

## 2. Latar Belakang

Penyampaian latihan TVET memerlukan gabungan teori, demonstrasi, amali, penilaian dan pemantauan kompetensi. Walau bagaimanapun, bahan pembelajaran sering berada dalam format berasingan seperti PDF, PowerPoint, video, borang, kuiz dan rekod manual.

Latihan di ladang, bengkel atau lokasi luar juga boleh terjejas oleh sambungan internet yang tidak stabil. Keadaan ini mewujudkan keperluan kepada sebuah platform latihan setempat yang mudah dibawa, kos rendah dan boleh diakses melalui peranti peserta sendiri.

ASTH dicadangkan sebagai sebuah platform latihan digital yang menggabungkan kandungan pembelajaran, SOP, kuiz, Smart Tutor dan dashboard trainer dalam satu sistem yang dihoskan pada Raspberry Pi 5.

## 3. Pernyataan Masalah

1. Bahan latihan tersimpan dalam pelbagai format dan lokasi.
2. Kebergantungan kepada internet menghadkan latihan di sesetengah lokasi.
3. Trainer perlu mengulang penerangan asas yang sama kepada peserta.
4. Tiada satu platform tempatan untuk melihat kemajuan peserta secara masa nyata.
5. SOP dan modul panjang sukar diteroka melalui telefon.
6. Sistem latihan digital komersial mungkin memerlukan langganan, cloud dan kos operasi.
7. Bahan latihan sedia ada belum distrukturkan sebagai pengalaman pembelajaran interaktif.

## 4. Cadangan Penyelesaian

ASTH akan menyediakan:

- portal peserta;
- portal trainer;
- modul pembelajaran digital;
- SOP interaktif;
- video dan media pembelajaran;
- kuiz dan maklum balas;
- rekod kemajuan;
- dashboard trainer;
- Smart Tutor berasaskan knowledge base tempatan;
- operasi melalui Wi-Fi setempat tanpa internet;
- pilihan integrasi cloud AI yang dikawal pada masa depan.

## 5. Visi

Menjadi platform latihan digital pintar yang memperkukuh pendidikan TVET veterinar dan pertanian melalui pembelajaran mudah capai, interaktif, berasaskan bukti dan boleh digunakan di mana-mana.

## 6. Misi

1. Mendigitalkan bahan latihan secara tersusun dan mesra pengguna.
2. Menyediakan platform pembelajaran yang boleh beroperasi tanpa internet.
3. Membantu trainer memantau kemajuan dan prestasi peserta.
4. Menggalakkan pembelajaran kendiri serta pengukuhan kompetensi.
5. Membina platform modular yang boleh diperluas kepada kursus lain.
6. Menggunakan teknologi kos rendah dan sumber terbuka.

## 7. Objektif Projek

### Objektif Umum

Membangunkan prototaip ASTH sebagai platform latihan digital TVET berasaskan Raspberry Pi untuk menyokong program Operasi Ladang Poltri.

### Objektif Khusus

- membangunkan satu web app responsif dan installable;
- menyediakan sekurang-kurangnya satu kursus rintis;
- membina minimum tiga modul pembelajaran;
- menyediakan Smart Tutor tanpa kebergantungan API;
- menyediakan kuiz dan rekod markah;
- menyediakan dashboard trainer;
- membolehkan sistem digunakan dalam rangkaian tempatan;
- menghasilkan dokumentasi, manual dan video demonstrasi.

## 8. Sasaran Pengguna

### Pengguna Utama

- pelajar SKM Operasi Ladang Poltri;
- trainer dan pengajar;
- penyelaras latihan;
- pentadbir ASTH.

### Pemegang Taruh

- Pengarah Institut Teknologi Unggas;
- pengurusan Jabatan Perkhidmatan Veterinar;
- tenaga pengajar;
- unit ICT;
- urus setia pertandingan inovasi;
- organisasi TVET berkaitan.

## 9. Skop Dalam MVP

- landing page ASTH;
- login ringkas mengikut peranan;
- portal pelajar;
- portal trainer;
- satu kursus Operasi Ladang Poltri;
- minimum tiga modul;
- SOP interaktif;
- Smart Tutor knowledge-based;
- kuiz;
- markah dan kemajuan;
- dashboard trainer;
- PWA;
- deployment Raspberry Pi 5;
- akses melalui Wi-Fi setempat;
- dokumentasi dan demo.

## 10. Di Luar Skop MVP

- model LLM besar pada Raspberry Pi;
- ChatGPT API terbuka kepada semua peserta;
- face recognition;
- digital twin penuh;
- AR/VR kompleks;
- integrasi sistem HR rasmi;
- pembayaran;
- sijil rasmi automatik;
- sensor IoT berskala besar;
- penggunaan merentas banyak institut semasa fasa prototaip.

## 11. Deliverable Utama

1. Project documentation pack.
2. Source code web app dan backend.
3. Database SQLite.
4. Knowledge base modul rintis.
5. Raspberry Pi deployment package.
6. Manual pengguna, trainer dan pemasangan.
7. Video demo.
8. Bahan pembentangan.
9. Laporan ujian.
10. Prototype competition-ready.

## 12. Seni Bina Ringkas

```text
Telefon / Tablet / Laptop
          |
     Wi-Fi Tempatan
          |
    Raspberry Pi 5
          |
  -------------------
  |        |        |
 PWA    FastAPI   SQLite
  |        |
 Modul   Smart Tutor
          |
   Knowledge Base
```

## 13. Teknologi Teras

- HTML5
- CSS3
- JavaScript
- Progressive Web App
- Python
- FastAPI
- SQLite
- Nginx
- Uvicorn
- Raspberry Pi OS
- Git dan GitHub

## 14. Anggaran Kos MVP

MVP menggunakan Raspberry Pi 5 dan SD card sedia ada.

| Item | Status | Kos awal |
|---|---|---:|
| Raspberry Pi 5 | Sedia ada | RM0 |
| SD card 32GB | Sedia ada | RM0 |
| Raspberry Pi OS | Percuma | RM0 |
| FastAPI / SQLite / Nginx | Sumber terbuka | RM0 |
| Web app | Dibangunkan dalaman | RM0 |
| Casing / cooling | Jika diperlukan | Opsyenal |
| QR sticker / bahan booth | Jika diperlukan | Rendah |

**Pendekatan rasmi:** proof of concept menggunakan aset sedia ada sebelum memohon peruntukan penambahbaikan.

## 15. Kriteria Kejayaan MVP

MVP dianggap berjaya apabila:

1. Raspberry Pi boleh menghoskan ASTH secara stabil.
2. Minimum lima peranti boleh mengakses sistem serentak dalam ujian awal.
3. Peserta boleh membuka modul, SOP dan kuiz melalui telefon.
4. Markah kuiz disimpan dengan betul.
5. Dashboard trainer memaparkan rekod peserta.
6. Smart Tutor menjawab soalan berdasarkan knowledge base.
7. Sistem asas boleh digunakan tanpa internet.
8. Demo lengkap dapat dijalankan dalam masa lima minit.
9. Dokumentasi dan manual tersedia.
10. Sekurang-kurangnya satu sesi ujian pengguna dilaksanakan.

## 16. Risiko Utama

| Risiko | Impak | Mitigasi |
|---|---|---|
| Skop terlalu besar | Lewat siap | Kunci skop MVP |
| Kandungan modul lambat diterima | Smart Tutor tidak lengkap | Mulakan FAQ dan modul teras |
| Pi terlalu panas | Sistem tidak stabil | Casing dan cooling aktif |
| Wi-Fi tidak stabil | Peserta sukar akses | Ujian hotspot dan router pilihan |
| Data rosak | Kehilangan rekod | Backup automatik SQLite |
| AI disalahfaham | Ekspektasi terlalu tinggi | Jelaskan Smart Tutor knowledge-based |
| Team terlalu bergantung seorang | Risiko kesinambungan | Dokumentasi dan Git |

## 17. Tadbir Urus Projek

### Peranan Dicadangkan

- **Project Sponsor:** Pengarah / wakil pengurusan.
- **Project Lead:** Ketua team inovasi.
- **Technical Lead:** Pembangunan web, backend dan Raspberry Pi.
- **Content Lead:** Modul Operasi Ladang Poltri.
- **Training Lead:** Penyelarasan penggunaan dengan pelajar.
- **Documentation Lead:** Proposal, manual dan laporan.
- **Quality Reviewer:** Ujian, semakan kandungan dan demonstrasi.

## 18. Prinsip Pelaksanaan

- satu langkah pada satu masa;
- dokumentasi sebelum pembangunan besar;
- feature freeze sebelum tarikh penghantaran;
- hanya kandungan disahkan digunakan;
- setiap perubahan melalui Git;
- demo mestilah boleh dijalankan tanpa internet.

## 19. Pelan Fasa

### Fasa 0 — Foundation

Charter, prinsip, skop, roadmap dan seni bina.

### Fasa 1 — UI Prototype

Landing page, portal peserta dan portal trainer.

### Fasa 2 — Core MVP

Modul, SOP, kuiz, progress dan database.

### Fasa 3 — Smart Tutor

Knowledge base, carian dan source citation.

### Fasa 4 — Raspberry Pi Deployment

Wi-Fi, web server, startup service dan backup.

### Fasa 5 — Competition Readiness

Testing, video, manual, poster, pitch dan demo.

### Fasa 6 — Pilot

Ujian bersama kumpulan pelajar sebenar.

## 20. Kelulusan Awal Yang Dimohon

1. Persetujuan prinsip untuk membangunkan proof of concept ASTH.
2. Kebenaran menggunakan Raspberry Pi 5 sedia ada.
3. Kebenaran menggunakan kandungan modul latihan yang telah disahkan.
4. Pelantikan team kecil pembangunan.
5. Kebenaran menjalankan ujian rintis bersama peserta terpilih.
6. Pertimbangan penambahbaikan selepas MVP terbukti berfungsi.
