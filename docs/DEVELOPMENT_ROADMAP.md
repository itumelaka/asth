# ASTH Development Roadmap

**Status date:** 30 July 2026

Status labels used below: **CONFIRMED** for directly verified work, **PARTIAL** for an operational shell or incomplete milestone, **PLANNED** for an approved future direction and **PENDING** for work not yet completed.

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

**Current state: PARTIAL**

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

The deployed v0.4.0 landing page at `/` is visually confirmed and includes live network status. The separate `/learn/` page exists, but participant/trainer portals and the complete learning experience are not confirmed.

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

**Current state: PARTIAL**

**Output**

- modul Operasi Ladang Poltri;
- SOP interaktif;
- media;
- kuiz;
- progress;
- feedback.

**Exit criteria**

- satu aliran pembelajaran lengkap boleh diselesaikan oleh peserta.

The Learning Hub currently contains placeholders for Modul Pembelajaran, Video Latihan and Latihan Interaktif. Actual modules, PDFs, videos and interactive content remain pending.

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

**Current state: PARTIAL**

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

Confirmed: the Raspberry Pi with 2 GB RAM, physical HDMI/USB-keyboard recovery access, local `asthadmin` login, recovered password, `sudo`, normal reboot, portable network, v0.4.0 application service, `/`, `/learn/`, `/health` and `/api/hub-status` are operational. Post-reboot checks also confirmed zero failed units, `/mnt/rog`, `smbd`, Uptime Kuma, Cockpit, phone access through `ASTH-PORTABLE` and internet forwarding through `eth0`. Pending: final casing, NVMe and LCD installation, kiosk mode, post-installation validation, database backup/restore testing, application rollback testing and repository synchronisation of the deployed source.

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

## Immediate Hardware and Content Sequence

1. **PENDING:** Receive and install the casing.
2. **PENDING:** Receive and install the NVMe base/HAT and SSD, then detect and test the device.
3. **PLANNED:** Choose and execute the final NVMe migration method; prefer full-OS boot from NVMe and retain the microSD as recovery media if testing succeeds.
4. **PENDING:** Receive and install the LCD and suitable display cable; configure kiosk mode to open `/`.
5. **PENDING:** Populate Learning Hub content and move large content to NVMe when available.
6. **PENDING:** Complete final power, cooling and temperature validation after assembly.
7. **PENDING:** Complete database backup/restore and application rollback testing.
8. **PENDING:** Finalise the system custodian and maintenance window.
