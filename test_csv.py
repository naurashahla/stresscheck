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
    csv_filename = "Kuesioner Tingkat Stres Akademik Mahasiswa (Jawaban).csv"
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

    # Generate Diagram Distribusi
    try:
        import matplotlib.pyplot as plt
        
        categories = ['Stres Ringan', 'Stres Sedang', 'Stres Berat']
        counts = [stats[cat] for cat in categories]
        percentages = [(count / total_responden * 100) if total_responden > 0 else 0 for count in counts]
        
        # Color palette for research presentation
        colors = ['#2ec4b6', '#ffb703', '#e63946'] # Teal, Warm Yellow, Crimson
        
        # Create a figure with 2 subplots (1 row, 2 columns)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle(f'Distribusi Hasil Diagnosa Stres Akademik\n(Total Responden Terproses: {total_responden})', 
                     fontsize=16, fontweight='bold', y=0.98)
        
        # 1. Bar Chart
        bars = ax1.bar(categories, counts, color=colors, edgecolor='black', alpha=0.85, width=0.6)
        ax1.set_title('Jumlah Responden per Tingkat Stres', fontsize=12, pad=10)
        ax1.set_ylabel('Jumlah Responden', fontsize=11)
        ax1.set_ylim(0, max(counts) + 10)
        ax1.grid(axis='y', linestyle='--', alpha=0.5)
        
        # Add values on top of the bars
        for bar, count, pct in zip(bars, counts, percentages):
            height = bar.get_height()
            ax1.annotate(f'{count}\n({pct:.2f}%)',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=10, fontweight='bold')
            
        # 2. Pie Chart (Donut style)
        pie_labels = [f'{cat}\n({pct:.2f}%)' for cat, pct in zip(categories, percentages)]
        wedges, texts, autotexts = ax2.pie(counts, labels=pie_labels, colors=colors, 
                                          autopct='%1.1f%%', startangle=140, 
                                          wedgeprops=dict(width=0.4, edgecolor='black', alpha=0.85))
        
        # Hide the default percentage labels since we custom-formatted labels
        for autotext in autotexts:
            autotext.set_visible(False)
            
        ax2.set_title('Persentase Distribusi Tingkat Stres', fontsize=12, pad=10)
        
        plt.tight_layout()
        
        chart_filename = "diagram_distribusi_stres.png"
        chart_path = os.path.join(os.path.dirname(__file__), chart_filename)
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Diagram distribusi telah disimpan ke file:\n  {chart_path}\n")
    except Exception as e:
        print(f"Gagal membuat diagram: {e}")


if __name__ == '__main__':
    process_csv()
