from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os, secrets, csv, io

app = Flask(__name__)
app.secret_key = os.environ.get("ANNUR_SECRET_KEY", secrets.token_hex(32))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///annur.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "static/uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
db = SQLAlchemy(app)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(40), unique=True, nullable=False)
    name = db.Column(db.String(160), nullable=False)
    nis = db.Column(db.String(60), default="")
    education = db.Column(db.String(100), default="")
    class_name = db.Column(db.String(100), default="")
    dorm = db.Column(db.String(100), default="")
    room = db.Column(db.String(100), default="")
    status = db.Column(db.String(40), default="Aktif")
    guardian = db.Column(db.String(160), default="")
    notes = db.Column(db.Text, default="")
    balance = db.Column(db.Integer, default=0)
    violations = db.Column(db.Text, default="")
    photo = db.Column(db.String(255), default="")

class SiteContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(80), unique=True, nullable=False)
    value = db.Column(db.Text, default="")

def logged_in():
    return bool(session.get("admin_id"))

@app.context_processor
def inject():
    return {"admin_logged": logged_in()}

with app.app_context():
    db.create_all()
    if not Admin.query.first():
        db.session.add(Admin(username="admin", password_hash=generate_password_hash("AnnurGanti123!")))
        db.session.commit()
    for k,v in [("title","Pondok Pesantren Annur Kalibaru"),("hero","Menanamkan Nilai, Membentuk Karakter"),("about","Pondok Pesantren Annur Kalibaru — ruang tumbuh bagi ilmu, iman, dan akhlak."),("contact","Kalibaruwetan, Kalibaru, Banyuwangi, Jawa Timur")]:
        if not SiteContent.query.filter_by(key=k).first():
            db.session.add(SiteContent(key=k,value=v))
    db.session.commit()

def content(key, default=""):
    c=SiteContent.query.filter_by(key=key).first()
    return c.value if c else default

@app.route("/")
def home():
    students=Student.query.filter_by(status="Aktif").count()
    return render_template("home.html", students=students, title=content("title"), hero=content("hero"), about=content("about"), contact=content("contact"))

@app.route("/profil")
def profil():
    return render_template("page.html", title="Profil Pesantren", content=content("about"), contact=content("contact"))

@app.route("/data-santri", methods=["GET","POST"])
def lookup():
    # Local starter: lookup exposes only minimal public fields. Sensitive information is admin-only.
    student=None
    if request.method=="POST":
        code=request.form.get("code","").strip().upper()
        student=Student.query.filter_by(code=code, status="Aktif").first()
        if not student: flash("Kode tidak ditemukan atau data tidak tersedia.")
    return render_template("lookup.html", student=student)

@app.route("/admin", methods=["GET","POST"])
def admin_login():
    if logged_in(): return redirect(url_for("dashboard"))
    if request.method=="POST":
        a=Admin.query.filter_by(username=request.form.get("username","")).first()
        if a and check_password_hash(a.password_hash, request.form.get("password","")):
            session["admin_id"]=a.id
            return redirect(url_for("dashboard"))
        flash("Username atau password salah.")
    return render_template("login.html")

@app.route("/admin/dashboard")
def dashboard():
    if not logged_in(): return redirect(url_for("admin_login"))
    return render_template("dashboard.html", students=Student.query.order_by(Student.name).all(), active=Student.query.filter_by(status="Aktif").count())

@app.route("/admin/student/new", methods=["GET","POST"])
@app.route("/admin/student/<int:sid>", methods=["GET","POST"])
def student_edit(sid=None):
    if not logged_in(): return redirect(url_for("admin_login"))
    s=Student.query.get(sid) if sid else Student()
    if request.method=="POST":
        s.code=request.form.get("code","").strip().upper()
        s.name=request.form.get("name","").strip()
        s.nis=request.form.get("nis","")
        s.education=request.form.get("education","")
        s.class_name=request.form.get("class_name","")
        s.dorm=request.form.get("dorm","")
        s.room=request.form.get("room","")
        s.status=request.form.get("status","Aktif")
        s.guardian=request.form.get("guardian","")
        s.balance=int(request.form.get("balance",0) or 0)
        s.violations=request.form.get("violations","")
        s.notes=request.form.get("notes","")
        upload=request.files.get("photo")
        if upload and upload.filename:
            fname=secure_filename(upload.filename)
            ext=os.path.splitext(fname)[1].lower()
            if ext in [".jpg",".jpeg",".png",".webp"]:
                unique=secrets.token_hex(8)+ext
                upload.save(os.path.join(app.config["UPLOAD_FOLDER"],unique))
                s.photo=unique
        if not s.name or not s.code:
            flash("Kode dan nama wajib diisi.")
            return render_template("student_form.html", s=s)
        duplicate=Student.query.filter_by(code=s.code).first()
        if duplicate and duplicate.id != s.id:
            flash("Kode santri sudah digunakan.")
            return render_template("student_form.html", s=s)
        db.session.add(s); db.session.commit()
        flash("Data tersimpan.")
        return redirect(url_for("dashboard"))
    return render_template("student_form.html", s=s)

@app.route("/admin/student/<int:sid>/delete", methods=["POST"])
def student_delete(sid):
    if not logged_in(): return redirect(url_for("admin_login"))
    s=Student.query.get_or_404(sid)
    db.session.delete(s); db.session.commit()
    flash("Data santri dihapus.")
    return redirect(url_for("dashboard"))

@app.route("/admin/content", methods=["GET","POST"])
def content_edit():
    if not logged_in(): return redirect(url_for("admin_login"))
    keys=["title","hero","about","contact"]
    if request.method=="POST":
        for k in keys:
            c=SiteContent.query.filter_by(key=k).first()
            if c: c.value=request.form.get(k,"")
        db.session.commit(); flash("Konten website disimpan.")
    return render_template("content.html", vals={k:content(k) for k in keys})

@app.route("/admin/password", methods=["GET","POST"])
def password_change():
    if not logged_in(): return redirect(url_for("admin_login"))
    if request.method=="POST":
        a=Admin.query.get(session["admin_id"])
        if not check_password_hash(a.password_hash,request.form.get("old","")):
            flash("Password lama salah.")
        elif len(request.form.get("new",""))<12:
            flash("Password baru minimal 12 karakter.")
        else:
            a.password_hash=generate_password_hash(request.form.get("new"))
            db.session.commit(); flash("Password berhasil diganti.")
    return render_template("password.html")

@app.route("/admin/export")
def export_csv():
    if not logged_in(): return redirect(url_for("admin_login"))
    out=io.StringIO(); w=csv.writer(out)
    w.writerow(["Kode","Nama","NIS","Pendidikan","Kelas","Asrama","Kamar","Status","Wali","Tanggungan","Pelanggaran","Catatan"])
    for s in Student.query.all():
        w.writerow([s.code,s.name,s.nis,s.education,s.class_name,s.dorm,s.room,s.status,s.guardian,s.balance,s.violations,s.notes])
    return app.response_class(out.getvalue(), mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=data-santri.csv"})

@app.route("/logout")
def logout():
    session.clear(); return redirect(url_for("home"))

if __name__=="__main__":
    app.run(host="127.0.0.1",port=5000,debug=False)
