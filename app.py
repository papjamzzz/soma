from flask import Flask, render_template, jsonify
from dotenv import load_dotenv
import random, math, time

load_dotenv()
app = Flask(__name__)
# Re-read templates from disk on every request (dev convenience)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True

# ── Biomarker definitions ─────────────────────────────────────────────
# The ~12 signals an Apple Watch pulls easily. Each maps to one or more
# body regions. `dir` is just for the readout arrow ('high'/'low'/'band').
# Severity is computed from how far a value sits outside its optimal band:
#   sev = clamp( max(optLo - v, v - optHi, 0) / scale, 0, 1 )
# For "higher is better" markers, optHi is set huge (no upper penalty);
# for "lower is better", optLo is set tiny.
MARKERS = [
    # key             label                unit   regions                 base   optLo  optHi  scale  sd     lo    hi
    ("heart_rate",     "Heart Rate",        "bpm", ["cardio"],             74,    55,    90,    40,    4.0,   48,   165),
    ("resting_hr",     "Resting HR",        "bpm", ["cardio"],             88,    45,    65,    28,    2.0,   40,   110),
    ("hrv",            "HRV (SDNN)",        "ms",  ["cardio", "brain"],    58,    50,    400,   45,    5.0,   15,   120),
    ("spo2",           "Blood Oxygen",      "%",   ["extremities"],        94,    96,    100,   6,     0.6,   88,   100),
    ("resp_rate",      "Respiratory Rate",  "br/min", ["cardio"],          15,    11,    19,    8,     0.8,   9,    28),
    ("vo2max",         "VO₂ Max",      "ml/kg", ["legs", "cardio"],   39,    42,    400,   18,    0.6,   25,   60),
    ("wrist_temp",     "Wrist Temp Δ", "°C", ["gut"],            0.15,  -0.3,  0.3,   1.0,   0.07,  -0.6, 1.6),
    ("sleep",          "Sleep",             "h",   ["brain"],              7.4,   7.0,   24,    3.0,   0.35,  3.0,  9.5),
    ("cardio_rec",     "Cardio Recovery",   "bpm", ["cardio"],             28,    22,    200,   14,    2.0,   10,   60),
    ("walking_hr",     "Walking HR",        "bpm", ["legs"],               112,   70,    100,   30,    3.0,   80,   150),
    ("active_energy",  "Active Energy",     "%goal", ["legs"],             78,    90,    300,   60,    5.0,   25,   180),
    ("ecg",            "ECG Rhythm",        "",    ["cardio"],             0,     0,     0,     1,     0,     0,    1),  # categorical, handled specially
]

# ── Lab layer (Path B) ────────────────────────────────────────────────
# SIMULATED blood-panel markers. A watch can NEVER read these — they need
# a real blood/saliva test (Function Health, etc.). They fill the body
# zones the watch can't reach (gut, pelvis, arms) and are always tagged
# `source: lab` so the UI never passes them off as live Watch data.
LAB = [
    # key            label                 unit     regions                   base   optLo  optHi  scale  sd     lo    hi
    ("cortisol",     "Cortisol",           "µg/dL", ["gut", "brain"],         23,    6,     18,    12,    1.2,   3,    38),
    ("testosterone", "Testosterone",       "ng/dL", ["arms", "legs", "pelvis"], 330, 400,   1000,  350,   12,    180,  1100),
    ("crp",          "CRP (Inflammation)", "mg/L",  ["gut", "arms"],          2.2,   0,     1.0,   4,     0.25,  0,    12),
    ("glucose",      "Fasting Glucose",    "mg/dL", ["gut"],                  92,    70,    99,    40,    2.0,   60,   200),
    ("vitamin_d",    "Vitamin D",          "ng/mL", ["pelvis"],               34,    30,    100,   25,    1.0,   8,    90),
    ("tsh",          "Thyroid (TSH)",      "mIU/L", ["brain"],                2.1,   0.4,   4.0,   3,     0.15,  0.1,  9),
    ("estradiol",    "Estradiol",          "pg/mL", ["pelvis"],               30,    15,    50,    35,    2.0,   5,    130),
    ("ldl",          "LDL Cholesterol",    "mg/dL", ["cardio"],               118,   0,     100,   60,    3.0,   50,   230),
]

SOURCES = [("watch", MARKERS), ("lab", LAB)]
ALL_REGIONS = ["brain", "cardio", "gut", "pelvis", "arms", "legs", "extremities"]

# Live drifting state (replace this with real HealthKit / lab values later)
# tuple layout: (key, label, unit, regions, base, optLo, optHi, scale, sd, lo, hi)
STATE = {}
for _src, _lst in SOURCES:
    for _m in _lst:
        STATE[_m[0]] = _m[4]
STATE["ecg"] = 0.0          # 0 = Sinus, 1 = AFib flag

def _step():
    """Mean-reverting random walk so values feel organically alive."""
    for _src, _lst in SOURCES:
        for key, label, unit, regions, base, optLo, optHi, scale, sd, lo, hi in _lst:
            if key == "ecg":
                # mostly Sinus; rare, sticky AFib flag
                if STATE["ecg"] >= 1:
                    if random.random() < 0.35: STATE["ecg"] = 0.0
                elif random.random() < 0.02:
                    STATE["ecg"] = 1.0
                continue
            v = STATE[key]
            v += random.gauss(0, sd * 0.5)      # jitter
            v += (base - v) * 0.05              # pull toward baseline
            STATE[key] = max(lo, min(hi, v))

def _severity(key, v, optLo, optHi, scale):
    if key == "ecg":
        return 1.0 if v >= 1 else 0.0
    return max(0.0, min(1.0, max(optLo - v, v - optHi, 0) / scale))

def _status(sev):
    return "good" if sev < 0.34 else ("warn" if sev < 0.67 else "critical")

def snapshot():
    _step()
    markers = []
    reg = {"watch": {}, "lab": {}}
    for src, lst in SOURCES:
        for key, label, unit, regions, base, optLo, optHi, scale, sd, lo, hi in lst:
            v = STATE[key]
            sev = _severity(key, v, optLo, optHi, scale)
            if key == "ecg":
                disp, unit_out = ("AFib" if v >= 1 else "Sinus"), ""
            else:
                disp, unit_out = round(v, 1), unit
            markers.append({
                "key": key, "label": label, "value": disp, "unit": unit_out,
                "regions": regions, "severity": round(sev, 3),
                "status": _status(sev), "source": src,
            })
            for r in regions:
                reg[src][r] = max(reg[src].get(r, 0.0), sev)
    for src in ("watch", "lab"):
        for r in ALL_REGIONS:
            reg[src].setdefault(r, 0.0)

    def overall(src):
        ms = [m for m in markers if m["source"] == src]
        return round(100 - (sum(m["severity"] for m in ms) / len(ms)) * 100)

    return {
        "markers": markers,
        "regions_watch": reg["watch"], "regions_lab": reg["lab"],
        "overall_watch": overall("watch"), "overall_lab": overall("lab"),
        "ts": time.time(),
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/biomarkers')
def biomarkers():
    return jsonify(snapshot())

@app.route('/api/status')
def status():
    return jsonify({'status': 'ok', 'project': 'soma'})

if __name__ == '__main__':
    PORT = int(os.getenv("PORT", "5573"))
    app.run(host='0.0.0.0', port=PORT, debug=False)
