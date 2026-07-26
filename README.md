# ASTH — Adaptive Smart Training Hub

> **One Hub. Smarter Learning. Better Skills.**

## Ringkasan

**Adaptive Smart Training Hub (ASTH)** ialah platform latihan digital TVET yang dibangunkan untuk Institut Teknologi Unggas, Jabatan Perkhidmatan Veterinar. Sistem ini direka sebagai **web app / Progressive Web App (PWA)** yang boleh dihoskan pada Raspberry Pi 5 dan digunakan melalui telefon, tablet atau komputer dalam rangkaian Wi-Fi tempatan.

Perkakasan semasa yang disahkan ialah Raspberry Pi 5 dengan **32 GB RAM**. Raspberry Pi OS masih boot dan berjalan daripada **kad microSD 32 GB**. Casing, NVMe base/HAT dan SSD, LCD serta kabel paparan yang sesuai masih belum diterima atau dipasang. Arah pilihan selepas perkakasan tiba dan lulus ujian ialah memindahkan keseluruhan sistem operasi ke NVMe serta mengekalkan microSD sebagai media pemulihan.

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

## Status pada 26 Julai 2026

- **CONFIRMED:** Rangkaian portable ASTH dan aplikasi web FastAPI v0.4.0 beroperasi pada Raspberry Pi.
- **CONFIRMED:** Halaman utama `/` memaparkan status hub, statistik rangkaian masa nyata dan pautan ke Learning Hub, Uptime Kuma serta Cockpit.
- **PARTIAL:** `/learn/` tersedia sebagai Learning Hub berasingan, tetapi kandungan sebenar belum dimasukkan.
- **PENDING:** Pemasangan casing, NVMe dan LCD; konfigurasi kiosk LCD; migrasi storan; ujian backup/pemulihan; serta sinkronisasi source v0.4.0 dari Pi ke repository ini.

Butiran semasa direkodkan dalam [Deployment Status](docs/DEPLOYMENT_STATUS.md).

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

Projek ini dicadangkan untuk dibangunkan di bawah:

**Institut Teknologi Unggas**  
**Jabatan Perkhidmatan Veterinar Malaysia**

ASTH bukan dibangunkan untuk menggantikan trainer. ASTH dibangunkan untuk memperkukuh penyampaian latihan, pembelajaran kendiri dan pemantauan kompetensi peserta.
