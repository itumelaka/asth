# Executive Summary

## Adaptive Smart Training Hub (ASTH)

Adaptive Smart Training Hub ialah cadangan platform latihan digital TVET untuk Institut Teknologi Unggas, Jabatan Perkhidmatan Veterinar Malaysia. Projek ini bertujuan menyatukan modul pembelajaran, SOP, kuiz, rekod kemajuan, dashboard trainer dan Smart Tutor dalam satu web app yang boleh digunakan melalui telefon, tablet dan komputer.

Keunikan utama ASTH ialah konsep **offline-first**. Sistem dihoskan pada Raspberry Pi 5 dan boleh dicapai melalui rangkaian Wi-Fi tempatan tanpa bergantung kepada internet atau cloud. Pendekatan ini sesuai untuk latihan di ladang, makmal, bengkel dan lokasi yang mempunyai sambungan internet terhad.

Modul rintis yang dicadangkan ialah Sijil Kemahiran Malaysia — Operasi Ladang Poltri. Peserta boleh membuka bahan pembelajaran, mengikuti SOP interaktif, menjawab kuiz dan melihat kemajuan. Trainer pula boleh melihat penyertaan, markah dan kemajuan peserta melalui dashboard.

ASTH Smart Tutor untuk MVP tidak menggunakan API berbayar. Ia menggunakan knowledge base tempatan yang dibina daripada modul, SOP dan FAQ rasmi. Jawapan dipadankan kepada kandungan yang telah disahkan serta disertakan rujukan sumber. Integrasi cloud AI hanya dicadangkan sebagai pilihan masa depan dan boleh dikawal mengikut bajet.

Projek ini menggunakan Raspberry Pi 5 dan SD card yang telah tersedia. Perisian utama seperti FastAPI, SQLite, Nginx dan teknologi PWA ialah sumber terbuka. Oleh itu, proof of concept boleh dimulakan dengan kos tambahan yang sangat rendah.

ASTH dicadangkan bukan sekadar sebagai projek pertandingan, tetapi sebagai asas kepada platform latihan digital institut yang boleh dikembangkan secara berperingkat kepada modul penetasan, biosekuriti, makmal, kesihatan haiwan, IoT dan kursus lain.

## Nilai Strategik

- mengurangkan kebergantungan kepada internet;
- menyusun bahan latihan dalam satu platform;
- membantu trainer memantau prestasi;
- meningkatkan pengalaman pembelajaran;
- mengoptimumkan aset ICT sedia ada;
- menyokong transformasi digital TVET;
- boleh dikembangkan tanpa membina sistem baru untuk setiap kursus.

## Status Pelaksanaan pada 30 Julai 2026

Raspberry Pi 5 dengan 2 GB RAM kini beroperasi menggunakan Raspberry Pi OS pada kad microSD 32 GB. Akses pemulihan fizikal melalui HDMI dan papan kekunci USB telah disahkan lengkap: login tempatan `asthadmin` berjaya, kata laluan dipulihkan melalui boot recovery, `sudo` mengembalikan `SUDO_OK` dan Raspberry Pi reboot secara normal. Selepas reboot, tiada unit systemd yang gagal, health endpoint ASTH melaporkan `healthy`/`running`, SSD luaran kekal mounted pada `/mnt/rog` dan `smbd` aktif.

Rangkaian `ASTH-PORTABLE` aktif pada `wlan0` dengan alamat `10.42.0.1/24`. Telefon yang disambungkan berjaya mencapai health endpoint ASTH dan forwarding internet melalui `eth0` telah disahkan. Uptime Kuma memberikan HTTP 200 selepas redirect, manakala Cockpit mendengar pada port 9090 dan memberikan HTTP 200. Halaman utama `/` memaparkan identiti DVS/ASTH, status hub, bilangan peranti, kadar muat turun/muat naik, jumlah RX/TX, uptime, maklumat Wi-Fi, graf aktiviti rangkaian dan pautan ke Learning Hub, Uptime Kuma serta Cockpit. Data status dibekalkan secara langsung oleh `/api/hub-status`.

Learning Hub di `/learn/` telah dipisahkan daripada dashboard rangkaian dan sengaja tidak mempunyai graf rangkaian. Ia masih **PARTIAL** kerana bahagian Modul Pembelajaran, Video Latihan dan Latihan Interaktif belum diisi dengan kandungan sebenar. NVMe, casing dan LCD juga masih **PENDING** dan tidak boleh dianggap telah dipasang. Source aplikasi v0.4.0 yang berjalan pada Pi belum diselaraskan ke repository ini.

## Cadangan Pelaksanaan Seterusnya

Kekalkan deployment microSD yang sedang berfungsi sementara perkakasan tiba. Selepas casing, NVMe dan LCD diterima, uji bekalan kuasa, penyejukan, suhu dan pengesanan NVMe sebelum memilih kaedah migrasi. Arah pilihan ialah boot keseluruhan OS daripada NVMe dan mengekalkan microSD sebagai media pemulihan, tertakluk kepada ujian. Kandungan pembelajaran sebenar, kiosk LCD, ujian backup/restore database, rollback aplikasi dan ujian pengguna perlu disiapkan sebelum MVP diterima sepenuhnya. Pemilik sistem/custodian dan maintenance window juga perlu dimuktamadkan.

## Keputusan Yang Dimohon

Pihak pengurusan dipohon mempertimbangkan persetujuan awal untuk pembangunan prototaip, penggunaan aset Raspberry Pi sedia ada, akses kepada kandungan modul yang diluluskan serta ujian rintis bersama kumpulan peserta terpilih.
