# model.py — Sistem Pakar Deteksi Stres Akademik
# Metode  : Forward Chaining + Certainty Factor
# Penulis : Naura Shahla Meisamarva (434221050)

# ─── NILAI CF PAKAR (Tabel 4.4 — satu nilai per gejala) ─────────────────────
CF_PAKAR = {
    'G01': 0.75,   # Nyeri kepala saat memikirkan tugas
    'G02': 0.80,   # Tubuh terasa lemas
    'G03': 0.80,   # Jantung berdebar
    'G04': 0.70,   # Cepat lelah fisik
    'G05': 0.50,   # Tubuh segar saat bangun  [POSITIF -> masuk rule T01]
    'G06': 0.90,   # Kesulitan tidur
    'G07': 0.90,   # Cenderung begadang
    'G08': 0.60,   # Produktif hanya malam hari
    'G09': 0.95,   # Kesulitan konsentrasi
    'G10': 0.80,   # Mudah terdistraksi
    'G11': 0.60,   # Mampu mengarahkan pikiran  [POSITIF -> masuk rule T01]
    'G12': 0.95,   # Mudah lupa jadwal
    'G13': 0.90,   # Sulit mengingat materi
    'G14': 0.90,   # Pikiran tidak tenang
    'G15': 0.80,   # Beban akademik sulit dituntaskan
    'G16': 0.75,   # Yakin mampu selesai tepat waktu  [POSITIF -> masuk rule T01]
    'G17': 0.80,   # Menyalahkan pihak lain
    'G18': 0.90,   # Sensitif terhadap progres orang lain
    'G19': 0.70,   # Dapat menerima perbedaan pendapat  [POSITIF -> masuk rule T01]
    'G20': 0.95,   # Kesal saat ditanya progres
    'G21': 0.85,   # Terganggu unggahan keberhasilan teman
    'G22': 0.85,   # Gelisah menunggu evaluasi
    'G23': 0.90,   # Cemas proses akademik belum disetujui
    'G24': 0.50,   # Bersemangat menjelang konsultasi  [POSITIF -> masuk rule T01]
    'G25': 0.70,   # Sedih karena perkembangan studi lambat
    'G26': 0.80,   # Tertekan tuntutan keluarga/institusi
    'G27': 0.80,   # Terbebani jadwal padat
    'G28': 0.90,   # Mudah marah setelah interaksi negatif
    'G29': 0.80,   # Memendam kesal
    'G30': 0.80,   # Mudah tersinggung dibandingkan orang lain
    'G31': 0.90,   # Tidak nyaman dalam situasi sosial
    'G32': 0.90,   # Rendah diri karena tertinggal
    'G33': 0.90,   # Menghindari pertemuan sosial
    'G34': 0.90,   # Membatasi interaksi dengan teman
    'G35': 0.80,   # Malu bertemu orang lain
}

# ─── SKALA LIKERT -> CF USER (Tabel 3.6) ─────────────────────────────────────
SKALA_CF = {
    1: 0.00,   # Sangat Tidak Setuju
    2: 0.25,   # Tidak Setuju
    3: 0.50,   # Netral
    4: 0.75,   # Setuju
    5: 1.00,   # Sangat Setuju
}

LIKERT_LABELS = {
    1: 'Sangat Tidak Setuju',
    2: 'Tidak Setuju',
    3: 'Netral',
    4: 'Setuju',
    5: 'Sangat Setuju',
}

# ─── 14 RULE IF-THEN (Tabel 3.7) ─────────────────────────────────────────────
# Format: rule_id -> (tingkat, operator, [gejala])
# Untuk AND_NOT: elemen terakhir adalah gejala yang di-NOT-kan
RULES = {
    'R01': ('T01', 'OR',      ['G05', 'G11', 'G16', 'G19', 'G24']),
    'R02': ('T01', 'AND',     ['G01', 'G04', 'G16']),
    'R03': ('T01', 'AND_NOT', ['G05', 'G11', 'G06']),   # NOT G06
    'R04': ('T02', 'AND',     ['G02', 'G10', 'G25']),
    'R05': ('T02', 'AND',     ['G08', 'G15', 'G27']),
    'R06': ('T02', 'AND',     ['G17', 'G21', 'G22']),
    'R07': ('T02', 'AND',     ['G26', 'G29', 'G30']),
    'R08': ('T02', 'AND',     ['G01', 'G10', 'G15', 'G25']),
    'R09': ('T03', 'AND',     ['G06', 'G09', 'G12', 'G14']),
    'R10': ('T03', 'AND',     ['G18', 'G20', 'G23']),
    'R11': ('T03', 'AND',     ['G28', 'G31', 'G33']),
    'R12': ('T03', 'AND',     ['G09', 'G13', 'G32', 'G35']),
    'R13': ('T03', 'AND',     ['G14', 'G27', 'G34']),
    'R14': ('T03', 'AND',     ['G06', 'G07', 'G09', 'G33']),
}

# ─── LABEL DAN SARAN ─────────────────────────────────────────────────────────
LABEL_TINGKAT = {
    'T01': 'Stres Ringan',
    'T02': 'Stres Sedang',
    'T03': 'Stres Berat',
}

SARAN = {
    'T01': (
        'Kondisi Anda masih dalam batas wajar. Pertahankan pola hidup sehat, '
        'olahraga teratur, dan istirahat cukup untuk menjaga keseimbangan akademik.'
    ),
    'T02': (
        'Anda mengalami stres sedang. Disarankan untuk mencoba teknik relaksasi, '
        'manajemen waktu yang lebih baik, dan berbicara dengan konselor akademik '
        'jika diperlukan.'
    ),
    'T03': (
        'Tingkat stres Anda cukup tinggi. Sangat disarankan untuk segera '
        'berkonsultasi dengan konselor akademik atau psikolog kampus untuk '
        'mendapatkan dukungan profesional.'
    ),
}

import json
import os

def load_kb():
    global CF_PAKAR, SKALA_CF, LIKERT_LABELS, RULES, LABEL_TINGKAT, SARAN
    kb_path = os.path.join(os.path.dirname(__file__), 'knowledge_base.json')
    if os.path.exists(kb_path):
        try:
            with open(kb_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'CF_PAKAR' in data:
                    CF_PAKAR.clear()
                    CF_PAKAR.update(data['CF_PAKAR'])
                if 'SKALA_CF' in data:
                    SKALA_CF.clear()
                    for k, v in data['SKALA_CF'].items():
                        SKALA_CF[int(k)] = v
                if 'LIKERT_LABELS' in data:
                    LIKERT_LABELS.clear()
                    for k, v in data['LIKERT_LABELS'].items():
                        LIKERT_LABELS[int(k)] = v
                if 'RULES' in data:
                    RULES.clear()
                    RULES.update(data['RULES'])
                if 'LABEL_TINGKAT' in data:
                    LABEL_TINGKAT.clear()
                    LABEL_TINGKAT.update(data['LABEL_TINGKAT'])
                if 'SARAN' in data:
                    SARAN.clear()
                    SARAN.update(data['SARAN'])
        except Exception as e:
            print("Error loading knowledge_base.json:", e)

def save_kb():
    kb_path = os.path.join(os.path.dirname(__file__), 'knowledge_base.json')
    try:
        skala_str_keys = {str(k): v for k, v in SKALA_CF.items()}
        labels_str_keys = {str(k): v for k, v in LIKERT_LABELS.items()}
        data = {
            'CF_PAKAR': CF_PAKAR,
            'SKALA_CF': skala_str_keys,
            'LIKERT_LABELS': labels_str_keys,
            'RULES': RULES,
            'LABEL_TINGKAT': LABEL_TINGKAT,
            'SARAN': SARAN
        }
        with open(kb_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print("Error saving knowledge_base.json:", e)

# Auto load on import
load_kb()


# ─── FUNGSI UTAMA ─────────────────────────────────────────────────────────────

def combine_cf(cf1: float, cf2: float) -> float:
    """
    Kombinasi dua nilai CF secara paralel.
    Persamaan (2): CF_kombinasi = CF1 + CF2 x (1 - CF1)
    """
    return cf1 + cf2 * (1 - cf1)


def diagnosa_stres(jawaban: dict) -> dict:
    """
    Menjalankan inferensi Forward Chaining + Certainty Factor.

    Alur sesuai Tabel 3.10:
      Tahap 1 - Input gejala      : parameter 'jawaban' {G01: 1-5, ...}
      Tahap 2 - Preprocessing     : konversi skala -> CF User (Tabel 3.6)
      Tahap 3 - CF Gejala         : CF_gejala = CF_user x CF_pakar  [Persamaan 1]
      Tahap 4 - Evaluasi 14 Rule  : AND / OR / AND_NOT  (Tabel 3.7)
      Tahap 5 - Kombinasi Paralel : CF_komb = CF1 + CF2x(1-CF1)  [Persamaan 2]
      Tahap 6 - Hasil Diagnosa    : tingkat dengan CF tertinggi

    Catatan gejala positif (G05, G11, G16, G19, G24):
      Rumus CF_gejala SAMA: CF_user x CF_pakar -- tidak ada inversi.
      Perbedaannya hanya pada rule: gejala positif masuk rule T01 (R01/R02/R03),
      sehingga jawaban tinggi (SS) justru MENGUATKAN diagnosa Stres Ringan.
    """

    # Tahap 2: Konversi skala -> CF User
    cf_user = {}
    for gejala_id, nilai_skala in jawaban.items():
        cf_user[gejala_id] = SKALA_CF.get(int(nilai_skala), 0.0)

    # Tahap 3: Hitung CF Gejala
    # Rumus: CF_gejala = CF_user x CF_pakar  (berlaku untuk semua gejala)
    cf_gejala = {}
    for gejala_id in jawaban:
        if gejala_id in CF_PAKAR:
            cf_gejala[gejala_id] = round(cf_user[gejala_id] * CF_PAKAR[gejala_id], 4)

    # Tahap 4: Evaluasi Rule (Forward Chaining)
    cf_per_rule = {}
    for rule_id, (tingkat, operator, gejala_list) in RULES.items():
        if not all(g in cf_gejala for g in gejala_list):
            cf_per_rule[rule_id] = (tingkat, 0.0)
            continue

        if operator == 'OR':
            cf_rule = max(cf_gejala[g] for g in gejala_list)

        elif operator == 'AND':
            cf_rule = min(cf_gejala[g] for g in gejala_list)

        elif operator == 'AND_NOT':
            g_and_list = gejala_list[:-1]
            g_not      = gejala_list[-1]
            if cf_user.get(g_not, 1.0) == 0.00:
                cf_rule = min(
                    [cf_gejala[g] for g in g_and_list] + [CF_PAKAR[g_not]]
                )
            else:
                cf_rule = min(cf_gejala[g] for g in g_and_list)

        else:
            cf_rule = 0.0

        cf_per_rule[rule_id] = (tingkat, round(cf_rule, 4))

    # Tahap 5: Kombinasi Paralel per Tingkat
    cf_akumulasi = {'T01': 0.0, 'T02': 0.0, 'T03': 0.0}
    rules_aktif  = {'T01': [], 'T02': [], 'T03': []}

    for rule_id, (tingkat, cf_rule) in cf_per_rule.items():
        if cf_rule > 0:
            rules_aktif[tingkat].append({'rule': rule_id, 'cf': cf_rule})
            cf_akumulasi[tingkat] = combine_cf(cf_akumulasi[tingkat], cf_rule)

    # Tahap 6: Pilih Hasil Diagnosa
    if all(v == 0.0 for v in cf_akumulasi.values()):
        tingkat_terpilih = 'T01'
    else:
        tingkat_terpilih = max(cf_akumulasi, key=lambda k: cf_akumulasi[k])

    cf_final     = round(cf_akumulasi[tingkat_terpilih] * 100, 2)
    gejala_aktif = [g for g, cf in cf_gejala.items() if cf > 0]

    matched_rules = []
    for rule_id, (tingkat, cf_rule) in cf_per_rule.items():
        if tingkat == tingkat_terpilih and cf_rule > 0:
            for g in RULES[rule_id][2]:
                matched_rules.append({
                    'gejala_id'  : g,
                    'gejala_teks': '',
                    'cf_pakar'   : CF_PAKAR.get(g, 0),
                    'cf_user'    : cf_user.get(g, 0),
                    'cf_gabungan': cf_gejala.get(g, 0),
                })

    return {
        'tingkat'      : LABEL_TINGKAT[tingkat_terpilih],
        'kode'         : tingkat_terpilih,
        'cf_final'     : cf_final,
        'cf_detail'    : {LABEL_TINGKAT[k]: round(v * 100, 2)
                          for k, v in cf_akumulasi.items()},
        'gejala_aktif' : gejala_aktif,
        'rules_aktif'  : rules_aktif,
        'cf_per_rule'  : {r: (t, cf) for r, (t, cf) in cf_per_rule.items()},
        'matched_rules': matched_rules,
        'saran'        : SARAN[tingkat_terpilih],
        'label'        : LABEL_TINGKAT[tingkat_terpilih].replace('Stres ', ''),
    }


# ─── TEST (python model.py) ───────────────────────────────────────────────────
if __name__ == '__main__':

    # Responden 1: Amelia Nur Indah Puspita — jawaban Google Form (Tabel 4.6)
    amelia = {
        'G01':3,'G02':4,'G03':4,'G04':3,'G05':3,'G06':4,'G07':3,'G08':3,
        'G09':2,'G10':3,'G11':5,'G12':1,'G13':2,'G14':2,'G15':2,'G16':3,
        'G17':1,'G18':2,'G19':3,'G20':3,'G21':2,'G22':3,'G23':3,'G24':2,
        'G25':2,'G26':3,'G27':2,'G28':2,'G29':2,'G30':2,'G31':2,'G32':1,
        'G33':1,'G34':1,'G35':2,
    }
    h = diagnosa_stres(amelia)
    print(f"AMELIA -> {h['tingkat']} | CF = {h['cf_final']}%")
    print(f"         Detail : {h['cf_detail']}")
    print(f"         Gejala aktif ({len(h['gejala_aktif'])}): {h['gejala_aktif']}")
    print()

    # Responden 2: Fiqhi Nadya Roja Effendi — jawaban laporan konseling (Tabel 4.7)
    fiqhi = {
        'G01':2,'G02':1,'G03':4,'G04':2,'G05':4,'G06':2,'G07':2,'G08':1,
        'G09':2,'G10':1,'G11':4,'G12':1,'G13':2,'G14':4,'G15':1,'G16':4,
        'G17':1,'G18':3,'G19':4,'G20':1,'G21':2,'G22':4,'G23':3,'G24':4,
        'G25':3,'G26':2,'G27':3,'G28':1,'G29':1,'G30':4,'G31':1,'G32':1,
        'G33':1,'G34':2,'G35':2,
    }
    h2 = diagnosa_stres(fiqhi)
    print(f"FIQHI  -> {h2['tingkat']} | CF = {h2['cf_final']}%")
    print(f"         Detail : {h2['cf_detail']}")
    print(f"         Gejala aktif ({len(h2['gejala_aktif'])}): {h2['gejala_aktif']}")
    print()

    for nama, hasil in [('Amelia', h), ('Fiqhi', h2)]:
        for label, val in hasil['cf_detail'].items():
            assert 0 <= val <= 100, f"{nama} {label} CF={val} di luar range!"
    print("Semua nilai CF dalam range 0-100%")