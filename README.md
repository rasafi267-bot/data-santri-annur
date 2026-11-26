# Website Pondok Pesantren Annur Kalibaru — Starter Lokal

## Cara menjalankan (Windows)
1. Instal Python 3.10+ dan pastikan opsi Add Python to PATH aktif.
2. Ekstrak ZIP ini.
3. Klik `START.bat`. Script membuat virtual environment dan memasang dependensi.
4. Buka browser di `http://127.0.0.1:5000`.

## Login awal administrator
- Username: `admin`
- Password awal: `AnnurGanti123!`
- Segera ubah password di Dashboard > Ganti Password.

## Fitur starter
- Beranda dan halaman profil yang kontennya dapat diedit.
- Login admin.
- CRUD data santri, kode unik, status, pendidikan, kelas, asrama, kamar, tanggungan (nilai saldo), catatan privat, ringkasan pelanggaran privat.
- Pencarian daftar admin, export CSV.
- Lookup kode santri yang hanya menampilkan data dasar yang ditentukan.
- Upload foto (format jpg/png/webp).
- Database SQLite lokal.

## Catatan privasi dan batasan
Starter ini **belum siap dipublikasikan di internet**. Data santri merupakan data pribadi; kode lookup bukan autentikasi wali. Jangan mengunggah data nyata atau mengaktifkan akses publik sebelum menerapkan HTTPS, autentikasi wali, izin akses berbasis backend, rate limit, audit, kebijakan retensi, serta pengamanan backup. Pada starter ini, data privat hanya tampil di area admin, bukan lookup publik.

## Backup
Untuk backup lokal, hentikan aplikasi lalu salin `instance/annur.db` (database) dan folder `static/uploads`. Simpan backup di lokasi aman. Restore dengan mengganti database dan folder upload saat aplikasi berhenti.

## Mengubah website
Admin login > Konten & Profil. Untuk data santri, gunakan Tambah Santri / Edit. CSV tersedia dari tombol Export CSV.

## Template Excel
Gunakan file `template_santri.csv` yang dapat dibuka melalui Excel. Ini CSV, bukan import otomatis pada starter ini.

## Scope
Ini merupakan starter aplikasi lokal yang berfungsi untuk bagian dasar (website publik, admin, CRUD santri, konten, export). Modul pendaftaran online, import Excel interaktif, keuangan terperinci, laporan pelanggaran, galeri/CMS penuh, backup/restore dari dashboard, peta, dan verifikasi wali belum diselesaikan dalam versi ini dan perlu dikembangkan sebelum digunakan operasional.
