# ASTH Development Roadmap

## Sasaran Utama

Menghasilkan MVP yang boleh didemokan, diuji dan dibentangkan kepada pengurusan serta pertandingan inovasi.

## Sprint 0 — Project Foundation

**Output**

- Project Principles.
- Project Charter.
- Executive Summary.
- MVP Scope.
- Development Roadmap.
- Struktur repository.
- Senarai kandungan yang diperlukan.

**Exit criteria**

- nama, skop, teknologi dan objektif dipersetujui;
- fungsi luar MVP dikenal pasti;
- pemilik kandungan ditentukan.

## Sprint 1 — UI/UX Prototype

**Output**

- landing page;
- login;
- portal peserta;
- portal trainer;
- mobile navigation;
- reka bentuk modul;
- mock data.

**Exit criteria**

- semua skrin utama boleh dilayari;
- paparan telefon dan desktop lulus semakan awal;
- tiada backend sebenar diperlukan pada tahap ini.

## Sprint 2 — Backend and Database

**Output**

- FastAPI;
- SQLite;
- model pengguna, kursus, modul, kuiz dan progress;
- authentication asas;
- API dalaman;
- data seed.

**Exit criteria**

- login berfungsi;
- data modul boleh dibaca;
- markah boleh disimpan;
- dashboard membaca data sebenar.

## Sprint 3 — Learning Experience

**Output**

- modul Operasi Ladang Poltri;
- SOP interaktif;
- media;
- kuiz;
- progress;
- feedback.

**Exit criteria**

- satu aliran pembelajaran lengkap boleh diselesaikan oleh peserta.

## Sprint 4 — ASTH Smart Tutor

**Output**

- knowledge base;
- carian kata kunci dan topik;
- ranking jawapan;
- rujukan sumber;
- fallback;
- log pertanyaan.

**Exit criteria**

- Smart Tutor menjawab set soalan ujian yang telah ditentukan;
- tiada jawapan direka apabila sumber tiada.

## Sprint 5 — Raspberry Pi Deployment

**Output**

- deployment script;
- Nginx;
- Uvicorn service;
- local network access;
- QR access;
- auto-start;
- backup;
- recovery notes.

**Exit criteria**

- Pi boleh reboot dan ASTH hidup sendiri;
- minimum lima peranti berjaya masuk;
- sistem asas berfungsi tanpa internet.

## Sprint 6 — Testing and Hardening

**Output**

- functional test;
- mobile test;
- performance test;
- security review;
- content review;
- user acceptance test;
- bug fixing.

**Exit criteria**

- tiada bug kritikal;
- demo flow stabil;
- backup dan restore diuji.

## Sprint 7 — Presentation Readiness

**Output**

- video demo;
- proposal;
- pitch deck;
- poster;
- manual;
- booth flow;
- FAQ juri;
- live demo checklist.

**Exit criteria**

- demonstrasi lima minit boleh dilaksanakan tanpa bantuan developer;
- bahan boleh digunakan oleh team lain.

## Milestone Versi

| Versi | Fokus |
|---|---|
| 0.1 | Foundation documentation |
| 0.2 | UI prototype |
| 0.3 | Backend and database |
| 0.4 | Learning modules |
| 0.5 | Smart Tutor |
| 0.6 | Raspberry Pi deployment |
| 0.8 | User testing |
| 0.9 | Competition candidate |
| 1.0 | MVP release |

## Feature Freeze

Selepas versi 0.9:

- tiada feature besar baru;
- hanya bug fixing;
- penambahbaikan kandungan;
- kestabilan;
- dokumentasi;
- rehearsal demo.

## Selepas MVP

### Phase 2

- sensor IoT;
- dashboard persekitaran;
- content management;
- badge dan sijil;
- laporan lebih lengkap.

### Phase 3

- hybrid AI;
- voice assistant;
- AR;
- digital twin;
- peluasan kepada kursus lain;
- integrasi sistem organisasi.
