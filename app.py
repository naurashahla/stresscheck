from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from functools import wraps
import json
import datetime
import os

app = Flask(__name__)
app.secret_key = 'stress_akademik_secret_key_2024'

# ─── MOCK DATABASE (JSON Persisted) ──────────────────────────────────────────
DEFAULT_USERS = {
    'admin@kampus.ac.id':   {'password': 'admin123',  'role': 'admin',  'name': 'Administrator'},
    'pakar@kampus.ac.id':   {'password': 'pakar123',  'role': 'pakar',  'name': 'Dr. Pakar Psikologi'},
    'mahasiswa@kampus.ac.id':{'password': 'user123',  'role': 'user',   'name': 'Budi Santoso'},
}

USERS = {}

def load_users():
    global USERS
    users_path = os.path.join(os.path.dirname(__file__), 'users.json')
    if os.path.exists(users_path):
        try:
            with open(users_path, 'r', encoding='utf-8') as f:
                USERS = json.load(f)
        except Exception as e:
            print("Error loading users.json:", e)
            USERS = DEFAULT_USERS.copy()
    else:
        USERS = DEFAULT_USERS.copy()
        save_users()

def save_users():
    users_path = os.path.join(os.path.dirname(__file__), 'users.json')
    try:
        with open(users_path, 'w', encoding='utf-8') as f:
            json.dump(USERS, f, indent=4)
    except Exception as e:
        print("Error saving users.json:", e)

# Load users on startup
load_users()

GEJALA = [
    {'id': 'G01', 'teks': 'Sering merasakan nyeri kepala atau pusing saat memikirkan tugas akademik'},
    {'id': 'G02', 'teks': 'Tubuh terasa lemas saat menghadapi tekanan perkuliahan'},
    {'id': 'G03', 'teks': 'Jantung berdebar cepat saat mengingat tugas'},
    {'id': 'G04', 'teks': 'Cepat lelah secara fisik ketika menyelesaikan tugas kampus'},
    {'id': 'G05', 'teks': 'Tubuh terasa segar saat bangun tidur'},
    {'id': 'G06', 'teks': 'Kesulitan tidur saat menghadapi tekanan akademik'},
    {'id': 'G07', 'teks': 'Cenderung begadang untuk menyelesaikan tugas perkuliahan'},
    {'id': 'G08', 'teks': 'Hanya bisa produktif belajar pada malam hari'},
    {'id': 'G09', 'teks': 'Kesulitan berkonsentrasi saat mengerjakan tugas kuliah'},
    {'id': 'G10', 'teks': 'Mudah terdistraksi saat mengikuti perkuliahan'},
    {'id': 'G11', 'teks': 'Mampu mengarahkan pikiran untuk menyelesaikan tugas'},
    {'id': 'G12', 'teks': 'Mudah lupa terhadap jadwal atau tanggung jawab akademik'},
    {'id': 'G13', 'teks': 'Sulit mengingat kembali materi yang sudah dipelajari'},
    {'id': 'G14', 'teks': 'Pikiran tidak tenang karena tekanan tugas akademik'},
    {'id': 'G15', 'teks': 'Beban akademik terasa sulit dituntaskan'},
    {'id': 'G16', 'teks': 'Yakin mampu menyelesaikan kewajiban akademik tepat waktu'},
    {'id': 'G17', 'teks': 'Menyalahkan pihak lain saat gagal akademik'},
    {'id': 'G18', 'teks': 'Sensitif atau kesal melihat progres orang lain'},
    {'id': 'G19', 'teks': 'Dapat menerima perbedaan pendapat orang lain'},
    {'id': 'G20', 'teks': 'Kesal saat ditanya progres studi'},
    {'id': 'G21', 'teks': 'Terganggu dengan unggahan keberhasilan teman'},
    {'id': 'G22', 'teks': 'Gelisah saat menunggu hasil evaluasi akademik'},
    {'id': 'G23', 'teks': 'Cemas ketika ada proses akademik belum disetujui'},
    {'id': 'G24', 'teks': 'Bersemangat menjelang konsultasi akademik'},
    {'id': 'G25', 'teks': 'Sedih karena perkembangan studi lambat'},
    {'id': 'G26', 'teks': 'Tertekan karena tuntutan akademik keluarga/institusi'},
    {'id': 'G27', 'teks': 'Terbebani jadwal akademik yang padat'},
    {'id': 'G28', 'teks': 'Mudah marah setelah interaksi negatif terkait kuliah'},
    {'id': 'G29', 'teks': 'Memendam kesal terhadap komentar seputar studi'},
    {'id': 'G30', 'teks': 'Mudah tersinggung saat dibandingkan dengan progres orang lain'},
    {'id': 'G31', 'teks': 'Tidak nyaman dalam situasi sosial terkait studi'},
    {'id': 'G32', 'teks': 'Rendah diri karena tertinggal capaian akademik'},
    {'id': 'G33', 'teks': 'Menghindari pertemuan sosial agar tidak membahas studi'},
    {'id': 'G34', 'teks': 'Membatasi interaksi dengan teman selama tugas'},
    {'id': 'G35', 'teks': 'Malu bertemu orang lain karena belum menyelesaikan tanggung jawab akademik'},
]

# Riwayat diagnosa (JSON Persisted)
DEFAULT_DIAGNOSA_HISTORY = [
    {
        'id': 1, 'user': 'mahasiswa@kampus.ac.id', 'nama': 'Budi Santoso',
        'tanggal': '2024-01-15', 'hasil': 'Stres Sedang', 'cf': 72.45,
        'validasi': 'Sesuai', 'catatan_pakar': 'Hasil sesuai dengan kondisi mahasiswa',
        'gejala_dipilih': ['G01','G03','G06','G09','G14','G15','G22','G23','G25','G26'],
        'jawaban_gejala': {
            'G01': 4, 'G02': 2, 'G03': 5, 'G04': 3, 'G05': 1, 'G06': 4, 'G07': 2, 'G08': 3, 'G09': 5, 'G10': 3,
            'G11': 2, 'G12': 1, 'G13': 2, 'G14': 4, 'G15': 5, 'G16': 3, 'G17': 1, 'G18': 2, 'G19': 3, 'G20': 3,
            'G21': 2, 'G22': 4, 'G23': 5, 'G24': 2, 'G25': 4, 'G26': 5, 'G27': 2, 'G28': 2, 'G29': 2, 'G30': 2,
            'G31': 2, 'G32': 1, 'G33': 1, 'G34': 1, 'G35': 2
        },
        'pembayaran': 'Sudah Dibayar'
    },
    {
        'id': 2, 'user': 'mahasiswa@kampus.ac.id', 'nama': 'Budi Santoso',
        'tanggal': '2024-02-20', 'hasil': 'Stres Ringan', 'cf': 41.20,
        'validasi': None, 'catatan_pakar': '',
        'gejala_dipilih': ['G06','G07','G09','G10'],
        'jawaban_gejala': {
            'G01': 2, 'G02': 1, 'G03': 3, 'G04': 2, 'G05': 4, 'G06': 4, 'G07': 5, 'G08': 1, 'G09': 4, 'G10': 5,
            'G11': 4, 'G12': 1, 'G13': 2, 'G14': 3, 'G15': 1, 'G16': 4, 'G17': 1, 'G18': 3, 'G19': 4, 'G20': 1,
            'G21': 2, 'G22': 3, 'G23': 3, 'G24': 4, 'G25': 3, 'G26': 2, 'G27': 3, 'G28': 1, 'G29': 1, 'G30': 3,
            'G31': 1, 'G32': 1, 'G33': 1, 'G34': 2, 'G35': 2
        },
        'pembayaran': 'Belum Dibayar'
    },
]

DIAGNOSA_HISTORY = []

def load_diagnosa_history():
    global DIAGNOSA_HISTORY
    history_path = os.path.join(os.path.dirname(__file__), 'diagnosa_history.json')
    if os.path.exists(history_path):
        try:
            with open(history_path, 'r', encoding='utf-8') as f:
                DIAGNOSA_HISTORY = json.load(f)
            # Pastikan semua item riwayat memiliki field 'pembayaran'
            updated = False
            for d in DIAGNOSA_HISTORY:
                if 'pembayaran' not in d:
                    if d.get('validasi') is not None:
                        d['pembayaran'] = 'Sudah Dibayar'
                    else:
                        d['pembayaran'] = 'Belum Dibayar'
                    updated = True
            if updated:
                save_diagnosa_history()
        except Exception as e:
            print("Error loading diagnosa_history.json:", e)
            DIAGNOSA_HISTORY = DEFAULT_DIAGNOSA_HISTORY.copy()
    else:
        DIAGNOSA_HISTORY = DEFAULT_DIAGNOSA_HISTORY.copy()
        save_diagnosa_history()

def save_diagnosa_history():
    history_path = os.path.join(os.path.dirname(__file__), 'diagnosa_history.json')
    try:
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump(DIAGNOSA_HISTORY, f, indent=4)
    except Exception as e:
        print("Error saving diagnosa_history.json:", e)

# Load diagnosa history on startup
load_diagnosa_history()

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user' not in session:
                return redirect(url_for('login'))
            if session.get('role') not in roles:
                flash('Akses ditolak.', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated
    return decorator

# ─── ROUTES ──────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        user = USERS.get(email)
        if user and user['password'] == password:
            session['user'] = email
            session['role'] = user['role']
            session['name'] = user['name']
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user['role'] == 'pakar':
                return redirect(url_for('pakar_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        flash('Email atau password salah.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        name = request.form.get('name', '').strip()
        password = request.form.get('password', '').strip()
        
        if not email or not name or not password:
            flash('Semua field wajib diisi.', 'error')
        elif email in USERS:
            flash('Email sudah terdaftar.', 'error')
        else:
            USERS[email] = {
                'password': password,
                'role': 'user',
                'name': name
            }
            save_users()
            flash('Registrasi berhasil! Silakan masuk.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    role = session.get('role')
    if role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif role == 'pakar':
        return redirect(url_for('pakar_dashboard'))
    return redirect(url_for('user_dashboard'))

# ─── USER ROUTES ─────────────────────────────────────────────────────────────
@app.route('/user/dashboard')
@role_required('user')
def user_dashboard():
    user_email = session['user']
    riwayat = [d for d in DIAGNOSA_HISTORY if d['user'] == user_email]
    return render_template('user_dashboard.html', riwayat=riwayat)

@app.route('/diagnosa', methods=['GET', 'POST'])
@role_required('user')
def diagnosa():
    if request.method == 'POST':
        jawaban = {}
        for g in GEJALA:
            val = request.form.get(g['id'], '0')
            jawaban[g['id']] = int(val)
        
        # Import model dan jalankan
        try:
            from model import diagnosa_stres
            hasil = diagnosa_stres(jawaban)
        except Exception as e:
            hasil = {
                'tingkat': 'Stres Sedang',
                'cf_final': 68.75,
                'label': 'Sedang',
                'saran': 'Pertimbangkan untuk berbicara dengan konselor akademik.'
            }
        
        # Simpan ke history (mock)
        new_entry = {
            'id': len(DIAGNOSA_HISTORY) + 1,
            'user': session['user'],
            'nama': session['name'],
            'tanggal': datetime.date.today().strftime('%Y-%m-%d'),
            'hasil': hasil.get('tingkat', 'Stres Sedang'),
            'cf': hasil.get('cf_final', 0),
            'validasi': None,
            'catatan_pakar': '',
            'gejala_dipilih': [g['id'] for g in GEJALA if jawaban.get(g['id'], 0) >= 4],
            'jawaban_gejala': jawaban,
            'pembayaran': 'Belum Dibayar'
        }
        DIAGNOSA_HISTORY.append(new_entry)
        save_diagnosa_history()
        
        session['hasil_diagnosa'] = hasil
        session['last_diagnosa_id'] = new_entry['id']
        
        return redirect(url_for('pembayaran', diagnosa_id=new_entry['id']))
    
    import model
    return render_template('diagnosa.html', gejala=GEJALA, likert_labels=model.LIKERT_LABELS, skala_cf=model.SKALA_CF)

@app.route('/pembayaran/<int:diagnosa_id>', methods=['GET', 'POST'])
@role_required('user')
def pembayaran(diagnosa_id):
    entry = next((d for d in DIAGNOSA_HISTORY if d['id'] == diagnosa_id), None)
    if not entry:
        flash('Data diagnosa tidak ditemukan.', 'error')
        return redirect(url_for('user_dashboard'))
    
    if entry['user'] != session['user']:
        flash('Akses ditolak.', 'error')
        return redirect(url_for('user_dashboard'))
        
    if entry.get('pembayaran') == 'Sudah Dibayar':
        flash('Diagnosa ini sudah dibayar.', 'success')
        return redirect(url_for('hasil', id=diagnosa_id))
        
    if request.method == 'POST':
        method = request.form.get('payment_method', 'QRIS')
        entry['pembayaran'] = 'Sudah Dibayar'
        save_diagnosa_history()
        
        # Set ke session agar halaman hasil ter-update jika di-refresh langsung
        from model import diagnosa_stres
        hasil = diagnosa_stres(entry['jawaban_gejala'])
        session['hasil_diagnosa'] = hasil
        session['last_diagnosa_id'] = entry['id']
        
        flash(f'Pembayaran sebesar Rp 15.000 via {method} berhasil dilakukan! Silakan tunggu hasil validasi pakar.', 'success')
        return redirect(url_for('hasil', id=diagnosa_id))
        
    return render_template('pembayaran.html', entry=entry)

@app.route('/hasil')
@role_required('user')
def hasil():
    diagnosa_id = request.args.get('id')
    if diagnosa_id:
        try:
            d_id = int(diagnosa_id)
            entry = next((x for x in DIAGNOSA_HISTORY if x['id'] == d_id and x['user'] == session['user']), None)
            if entry:
                # Keamanan: Jika belum dibayar, paksa ke halaman pembayaran
                if entry.get('pembayaran') != 'Sudah Dibayar':
                    flash('Silakan selesaikan pembayaran terlebih dahulu untuk melihat hasil diagnosa.', 'warning')
                    return redirect(url_for('pembayaran', diagnosa_id=entry['id']))
                
                from model import diagnosa_stres
                hasil = diagnosa_stres(entry['jawaban_gejala'])
                hasil['validasi'] = entry.get('validasi')
                hasil['catatan_pakar'] = entry.get('catatan_pakar')
                hasil['pembayaran'] = entry.get('pembayaran', 'Belum Dibayar')
                hasil['diagnosa_id'] = entry['id']
                return render_template('hasil.html', hasil=hasil)
        except Exception as e:
            pass
            
    hasil = session.get('hasil_diagnosa')
    if not hasil:
        return redirect(url_for('diagnosa'))
        
    if 'last_diagnosa_id' in session:
        last_id = session['last_diagnosa_id']
        hasil['diagnosa_id'] = last_id
        entry = next((x for x in DIAGNOSA_HISTORY if x['id'] == last_id), None)
        if entry:
            # Keamanan: Jika belum dibayar, paksa ke halaman pembayaran
            if entry.get('pembayaran') != 'Sudah Dibayar':
                flash('Silakan selesaikan pembayaran terlebih dahulu untuk melihat hasil diagnosa.', 'warning')
                return redirect(url_for('pembayaran', diagnosa_id=entry['id']))
                
            hasil['pembayaran'] = entry.get('pembayaran', 'Belum Dibayar')
            hasil['validasi'] = entry.get('validasi')
            hasil['catatan_pakar'] = entry.get('catatan_pakar')
            
    return render_template('hasil.html', hasil=hasil)

# ─── ADMIN ROUTES ────────────────────────────────────────────────────────────
@app.route('/admin/dashboard')
@role_required('admin')
def admin_dashboard():
    stats = {
        'total_user': sum(1 for u in USERS.values() if u['role'] == 'user'),
        'total_diagnosa': len(DIAGNOSA_HISTORY),
        'stres_ringan': sum(1 for d in DIAGNOSA_HISTORY if 'Ringan' in d['hasil']),
        'stres_sedang': sum(1 for d in DIAGNOSA_HISTORY if 'Sedang' in d['hasil']),
        'stres_berat': sum(1 for d in DIAGNOSA_HISTORY if 'Berat' in d['hasil']),
    }
    return render_template('admin_dashboard.html', stats=stats, diagnosa=DIAGNOSA_HISTORY)

@app.route('/admin/gejala')
@role_required('admin')
def admin_gejala():
    from model import CF_PAKAR
    return render_template('admin_gejala.html', gejala=GEJALA, cf_pakar=CF_PAKAR)

@app.route('/admin/diagnosa')
@role_required('admin')
def admin_diagnosa():
    return render_template('admin_diagnosa.html', diagnosa=DIAGNOSA_HISTORY)

@app.route('/admin/tingkat', methods=['GET', 'POST'])
@role_required('admin')
def admin_tingkat():
    import model
    if request.method == 'POST':
        action = request.form.get('action', 'edit')
        kode = request.form.get('kode', '').strip().upper()
        label = request.form.get('label', '').strip()
        saran = request.form.get('saran', '').strip()
        
        if action == 'add':
            if not kode or not label or not saran:
                flash('Semua field harus diisi.', 'error')
            elif kode in model.LABEL_TINGKAT:
                flash('Kode tingkat stres sudah ada.', 'error')
            else:
                model.LABEL_TINGKAT[kode] = label
                model.SARAN[kode] = saran
                model.save_kb()
                flash('Tingkat stres berhasil ditambahkan.', 'success')
        else: # edit
            if kode in model.LABEL_TINGKAT:
                model.LABEL_TINGKAT[kode] = label
                model.SARAN[kode] = saran
                model.save_kb()
                flash('Tingkat stres berhasil diperbarui.', 'success')
            else:
                flash('Kode tingkat stres tidak valid.', 'error')
        return redirect(url_for('admin_tingkat'))
    
    data = []
    for k in sorted(model.LABEL_TINGKAT.keys()):
        data.append({
            'kode': k,
            'label': model.LABEL_TINGKAT[k],
            'saran': model.SARAN.get(k, '')
        })
    return render_template('admin_tingkat.html', tingkat=data)

@app.route('/admin/likert', methods=['GET', 'POST'])
@role_required('admin')
def admin_likert():
    import model
    if request.method == 'POST':
        action = request.form.get('action', 'edit')
        try:
            skala = int(request.form.get('skala'))
            label = request.form.get('label', '').strip()
            cf_val = float(request.form.get('cf'))
            
            if action == 'add':
                if skala in model.SKALA_CF:
                    flash('Skala sudah ada dalam sistem.', 'error')
                else:
                    model.SKALA_CF[skala] = cf_val
                    model.LIKERT_LABELS[skala] = label
                    model.save_kb()
                    flash('Skala baru berhasil ditambahkan.', 'success')
            else: # edit
                if skala in model.SKALA_CF:
                    model.SKALA_CF[skala] = cf_val
                    if label:
                        model.LIKERT_LABELS[skala] = label
                    model.save_kb()
                    flash('Skala berhasil diperbarui.', 'success')
                else:
                    flash('Skala tidak valid.', 'error')
        except Exception as e:
            flash(f'Gagal memproses data: {e}', 'error')
        return redirect(url_for('admin_likert'))
    
    data = []
    for k in sorted(model.SKALA_CF.keys()):
        data.append({
            'skala': k,
            'label': model.LIKERT_LABELS.get(k, f'Skala {k}'),
            'cf': model.SKALA_CF[k]
        })
    return render_template('admin_likert.html', likert=data)

@app.route('/admin/rules', methods=['GET', 'POST'])
@role_required('admin')
def admin_rules():
    import model
    import re
    if request.method == 'POST':
        action = request.form.get('action')
        rule_id = request.form.get('rule_id', '').strip()
        tingkat = request.form.get('tingkat', '').strip()
        operator = request.form.get('operator', '').strip()
        gejala_raw = request.form.get('gejala', '').strip()
        
        gejala_list = [g.strip().upper() for g in re.split(r'[,;\s]+', gejala_raw) if g.strip()]
        
        if action == 'add':
            if not rule_id or rule_id in model.RULES:
                flash('Rule ID tidak boleh kosong dan harus unik.', 'error')
            elif not tingkat or not operator or not gejala_list:
                flash('Semua field harus diisi.', 'error')
            else:
                model.RULES[rule_id] = [tingkat, operator, gejala_list]
                model.save_kb()
                flash(f'Rule {rule_id} berhasil ditambahkan.', 'success')
                
        elif action == 'edit':
            if rule_id in model.RULES:
                model.RULES[rule_id] = [tingkat, operator, gejala_list]
                model.save_kb()
                flash(f'Rule {rule_id} berhasil diperbarui.', 'success')
            else:
                flash('Rule ID tidak ditemukan.', 'error')
                
        elif action == 'delete':
            del_rule_id = request.form.get('del_rule_id')
            if del_rule_id in model.RULES:
                del model.RULES[del_rule_id]
                model.save_kb()
                flash(f'Rule {del_rule_id} berhasil dihapus.', 'success')
            else:
                flash('Rule ID tidak ditemukan.', 'error')
                
        return redirect(url_for('admin_rules'))
    
    data = []
    sorted_keys = sorted(model.RULES.keys(), key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 0)
    for r in sorted_keys:
        val = model.RULES[r]
        tingkat = val[0]
        operator = val[1]
        gejala_list = val[2]
        
        if operator == 'AND_NOT':
            g_and_list = gejala_list[:-1]
            g_not = gejala_list[-1]
            condition = " AND ".join(g_and_list) + f" AND NOT {g_not}"
        else:
            condition = f" {operator} ".join(gejala_list)
            
        kaidah = f"IF {condition} THEN {tingkat}"
        
        data.append({
            'id': r,
            'tingkat': tingkat,
            'tingkat_label': model.LABEL_TINGKAT.get(tingkat, tingkat),
            'operator': operator,
            'gejala': ", ".join(gejala_list),
            'kaidah': kaidah
        })
        
    return render_template('admin_rules.html', rules=data, tingkat_list=model.LABEL_TINGKAT)


# ─── PAKAR ROUTES ────────────────────────────────────────────────────────────
@app.route('/pakar/dashboard')
@role_required('pakar')
def pakar_dashboard():
    import model
    # Hanya tampilkan yang sudah dibayar dan belum divalidasi pakar
    pending_validasi = [d for d in DIAGNOSA_HISTORY if d.get('pembayaran') == 'Sudah Dibayar' and d.get('validasi') is None]
    return render_template('pakar_dashboard.html', diagnosa=pending_validasi, gejala=GEJALA, likert_labels=model.LIKERT_LABELS)

@app.route('/pakar/validasi/<int:diagnosa_id>', methods=['POST'])
@role_required('pakar')
def pakar_validasi(diagnosa_id):
    status = request.form.get('validasi')
    catatan = request.form.get('catatan', '')
    for d in DIAGNOSA_HISTORY:
        if d['id'] == diagnosa_id:
            # Pastikan sudah dibayar
            if d.get('pembayaran') != 'Sudah Dibayar':
                flash('Gagal validasi: Diagnosa belum dibayar.', 'error')
                return redirect(url_for('pakar_dashboard'))
            d['validasi'] = status
            d['catatan_pakar'] = catatan
            break
    save_diagnosa_history()
    flash('Validasi berhasil disimpan.', 'success')
    next_page = request.args.get('next') or request.referrer or url_for('pakar_dashboard')
    return redirect(next_page)

@app.route('/pakar/history')
@role_required('pakar')
def pakar_history():
    import model
    # Hanya tampilkan riwayat yang sudah dibayar
    paid_history = [d for d in DIAGNOSA_HISTORY if d.get('pembayaran') == 'Sudah Dibayar']
    return render_template('pakar_history.html', diagnosa=paid_history, gejala=GEJALA, likert_labels=model.LIKERT_LABELS)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
