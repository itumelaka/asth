# ASTH MVP Scope

## Matlamat

Membina satu prototaip ASTH yang stabil, boleh didemokan dan boleh diuji bersama peserta sebenar tanpa internet.

## Must Have

### Platform

- PWA responsif.
- Berjalan pada Raspberry Pi 5.
- Akses melalui IP tempatan dan QR.
- Startup automatik selepas Pi dihidupkan.

### Peranan

- Peserta.
- Trainer.
- Admin ringkas.

### Kandungan

- Satu kursus: Operasi Ladang Poltri.
- Minimum tiga modul.
- Minimum satu SOP interaktif.
- Minimum satu video atau media demonstrasi.
- Minimum 20 soalan kuiz.

### Smart Tutor

- Tiada API wajib.
- Carian knowledge base tempatan.
- Paparan jawapan berserta sumber.
- Jawapan fallback apabila maklumat tidak ditemui.
- Log soalan untuk penambahbaikan kandungan.

### Penilaian

- Kuiz objektif.
- Markah automatik.
- Rekod cubaan.
- Progress peserta.
- Ringkasan trainer.

### Dashboard

- Bilangan peserta.
- Status modul.
- Markah kuiz.
- Aktiviti terkini.
- Export ringkas jika sempat.

### Dokumentasi

- README.
- Project Charter.
- Executive Summary.
- Manual peserta.
- Manual trainer.
- Installation Guide.
- Demo script.
- Testing checklist.

## Should Have

- badge;
- sijil demo;
- QR mengikut modul;
- video offline;
- carian bahan;
- export CSV;
- tema gelap;
- backup automatik;
- audit log asas.

## Could Have

- sensor suhu dan kelembapan;
- dashboard IoT;
- trainer content editor;
- voice input;
- cloud AI terkawal;
- multilingual content;
- notification;
- gamification lebih lengkap.

## Won't Have in MVP

- face recognition;
- payment;
- AR/VR penuh;
- digital twin kompleks;
- LLM besar pada Raspberry Pi;
- free-form ChatGPT API untuk peserta;
- integrasi rasmi sistem HR atau SPDK;
- multi-institute tenancy;
- analytics lanjutan.

## Definition of Done

Sesuatu fungsi hanya dianggap siap apabila:

1. boleh digunakan pada telefon;
2. berjaya diuji tanpa internet;
3. mempunyai empty-state dan error handling;
4. data disimpan dengan betul;
5. dokumentasi dikemas kini;
6. perubahan direkod dalam Git;
7. tidak mengganggu fungsi sedia ada.
