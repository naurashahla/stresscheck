# test_csv.py
import csv
import os
from model import diagnosa_stres

def map_likert_text_to_val(text):
    text_clean = text.strip().lower()
    if 'sangat tidak setuju' in text_clean:
        return 1
    elif 'tidak setuju' in text_clean:
        return 2
    elif 'sangat setuju' in text_clean:
        return 5
    elif 'setuju' in text_clean:
        return 4
    elif 'netral' in text_clean:
        return 3
    else:
        # Fallback to Netral if empty or unrecognized
        return 3

def process_csv():
    csv_filename = "Kuesioner Tingkat Stres Akademik Mahasiswa (Jawaban) - Form Responses 1 (1).csv"
    csv_path = os.path.join(os.path.dirname(__file__), csv_filename)
    
    if not os.path.exists(csv_path):
        print(f"Error: File CSV tidak ditemukan di: {csv_path}")
        return

    # Counter hasil
    stats = {
        'Stres Ringan': 0,
        'Stres Sedang': 0,
        'Stres Berat': 0
    }
    
    detail_records = []
    
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader) # skip header row
        
        # Gejala G01 - G35 ada di kolom indeks ke-6 sampai ke-40 (total 35 kolom)
        # Indeks 0: Timestamp
        # Indeks 1: Nama Lengkap
        # Indeks 2: Usia
        # Indeks 3: Shopeepay
        # Indeks 4: Fakultas
        # Indeks 5: Semester
        for row_idx, row in enumerate(reader, start=1):
            if not row or len(row) < 41:
                continue
                
            nama = row[1]
            fakultas = row[4]
            semester = row[5]
            
            # Map columns 6 through 40 to G01-G35
            jawaban_user = {}
            for i in range(35):
                gejala_id = f"G{i+1:02d}"
                val_text = row[6 + i]
                jawaban_user[gejala_id] = map_likert_text_to_val(val_text)
                
            # Jalankan diagnosa sistem pakar
            hasil = diagnosa_stres(jawaban_user)
            hasil_tingkat = hasil['tingkat']
            cf_final = hasil['cf_final']
            
            stats[hasil_tingkat] += 1
            
            detail_records.append({
                'no': row_idx,
                'nama': nama,
                'fakultas': fakultas,
                'semester': semester,
                'hasil': hasil_tingkat,
                'cf': cf_final
            })
            
    # Hitung total dan persentase
    total_responden = len(detail_records)
    print("\n" + "="*60)
    print("HASIL DIAGNOSA KUESIONER 109 RESPONDEN")
    print("="*60)
    
    # Cetak Tabel 5.2
    print("\nTabel 5.2 Distribusi Hasil Diagnosa Sistem terhadap 109 Responden\n")
    print("| No. | Tingkat Stres | Jumlah Responden | Persentase |")
    print("|---|---|---|---|")
    
    idx = 1
    # Urutan output: Stres Ringan, Stres Sedang, Stres Berat
    for tingkat in ['Stres Ringan', 'Stres Sedang', 'Stres Berat']:
        count = stats[tingkat]
        pct = (count / total_responden * 100) if total_responden > 0 else 0
        print(f"| {idx} | T0{idx} — {tingkat} | {count} | {pct:.2f}% |")
        idx += 1
        
    print(f"| Total | | {total_responden} | 100% |")
    print("\n" + "="*60)
    
    # Simpan hasil rinci ke file baru
    output_filename = "hasil_diagnosa_responden.csv"
    output_path = os.path.join(os.path.dirname(__file__), output_filename)
    with open(output_path, mode='w', newline='', encoding='utf-8') as f_out:
        writer = csv.writer(f_out)
        writer.writerow(['No', 'Nama Lengkap', 'Fakultas', 'Semester', 'Hasil Diagnosa', 'Certainty Factor (%)'])
        for r in detail_records:
            writer.writerow([r['no'], r['nama'], r['fakultas'], r['semester'], r['hasil'], f"{r['cf']:.2f}%"])
            
    print(f"Hasil lengkap masing-masing responden telah disimpan ke file:\n  {output_path}\n")

if __name__ == '__main__':
    process_csv()
