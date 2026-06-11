# StresCheck — Sistem Pakar Deteksi Stres Akademik
## Metode: Forward Chaining + Certainty Factor

---

## Cara Menjalankan

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Jalankan server
python app.py

# 3. Buka browser
http://localhost:5000
```

---

## Akun Demo

| Role  | Email                     | Password  |
|-------|---------------------------|-----------|
| Admin | admin@kampus.ac.id        | admin123  |
| Pakar | pakar@kampus.ac.id        | pakar123  |
| User  | mahasiswa@kampus.ac.id    | user123   |

---

## Struktur File

```
stress_app/
├── app.py           ← Flask routes & logic
├── model.py         ← Forward Chaining + CF algorithm
├── requirements.txt
└── templates/
    ├── base.html           ← Base layout
    ├── index.html          ← Landing page
    ├── login.html          ← Login page
    ├── diagnosa.html       ← Kuesioner step-by-step
    ├── hasil.html          ← Hasil diagnosa
    ├── user_dashboard.html ← Dashboard mahasiswa
    ├── admin_dashboard.html
    ├── admin_gejala.html
    ├── admin_diagnosa.html
    └── pakar_dashboard.html
```

---

## Fitur

- **Landing Page** dengan hero section, penjelasan metode, kategori tingkat stres
- **Login** multi-role (Admin, Pakar, User) dengan tampilan split-screen modern
- **Kuesioner** 35 pertanyaan step-by-step dengan progress bar & validasi
- **Hasil Diagnosa** dengan animasi CF counter, breakdown per tingkat, dan saran
- **Dashboard User** + riwayat diagnosa lengkap
- **Admin Dashboard** dengan statistik & monitoring seluruh diagnosa
- **Validasi Pakar** dengan form sesuai/tidak sesuai + catatan

## Desain

Terinspirasi dari satupersen.net — warm, clean, modern dengan:
- Font: **Plus Jakarta Sans** (body) + **Fraunces** (serif display)
- Warna utama: **#FF6B35** (orange brand) + cream background
- Animasi halus: float card, progress bar, CF counter
