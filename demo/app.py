from flask import Flask, request, render_template, send_file, flash, redirect, url_for
import tempfile
import os
from werkzeug.utils import secure_filename
from xulyamthanh import mix_audio
import librosa
import soundfile as sf

app = Flask(__name__)
app.secret_key = "dev-yoursecretkey"


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/mix", methods=["POST"])
def mix():
    # Validate files
    f1 = request.files.get("file1")
    f2 = request.files.get("file2")
    if not f1 or not f2:
        flash("Vui lòng chọn cả hai file âm thanh.")
        return redirect(url_for("index"))

    try:
        vol1 = float(request.form.get("vol1", "1.0"))
        vol2 = float(request.form.get("vol2", "1.0"))
        start1 = float(request.form.get("start1", "0"))
        start2 = float(request.form.get("start2", "0"))
    except ValueError:
        flash("Giá trị âm lượng hoặc thời gian không hợp lệ.")
        return redirect(url_for("index"))
    # Server-side validation and clamping to avoid negative or extreme values
    MIN_VOL, MAX_VOL = 0.0, 3.0
    orig_vol1, orig_vol2 = vol1, vol2
    vol1 = max(MIN_VOL, min(MAX_VOL, vol1))
    vol2 = max(MIN_VOL, min(MAX_VOL, vol2))

    print(f"[mix request] vol1={orig_vol1} -> {vol1}, vol2={orig_vol2} -> {vol2}")
    # Create temporary files
    tmpdir = tempfile.mkdtemp(prefix="mixaudio_")
    in1_path = os.path.join(tmpdir, secure_filename(f1.filename) or "in1.wav")
    in2_path = os.path.join(tmpdir, secure_filename(f2.filename) or "in2.wav")
    out_path = os.path.join(tmpdir, "mixed.wav")

    f1.save(in1_path)
    f2.save(in2_path)

    # Call backend mix function
    try:
        # Cắt file theo thời gian bắt đầu
        data1, sr1 = librosa.load(in1_path, sr=None)
        data2, sr2 = librosa.load(in2_path, sr=None)
        if start1 > 0:
            data1 = data1[int(start1 * sr1):]
        if start2 > 0:
            data2 = data2[int(start2 * sr2):]
        # Save tạm để truyền cho mix_audio
        sf.write(in1_path, data1, sr1)
        sf.write(in2_path, data2, sr2)
        mix_audio(in1_path, in2_path, out_path, vol1, vol2)
    except Exception as e:
        flash(f"Lỗi khi trộn âm thanh: {e}")
        return redirect(url_for("index"))

    # Send resulting file
    return send_file(out_path, as_attachment=True, download_name="mixed.wav")


if __name__ == "__main__":
    # Run local dev server
    app.run(host="127.0.0.1", port=5000, debug=True)
