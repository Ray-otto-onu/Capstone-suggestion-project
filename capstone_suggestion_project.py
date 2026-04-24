#!/usr/bin/env python3
"""
Engineering Capstone Advisor
Flask web application for capstone project matching and team formation.

Install: pip install flask
Run:     python app.py
Open:    http://localhost:5000
"""

from flask import Flask, render_template_string, request, session, redirect, url_for, jsonify
import json, os, uuid, math, re
from collections import defaultdict

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "capstone-advisor-2025-dev")

DATA_FILE    = "capstone_students.json"
FACULTY_PASS = "faculty2025"

# ─────────────────────────────────────────────────────────────────────────────
# Static Data
# ─────────────────────────────────────────────────────────────────────────────

YEARS    = ["Freshman", "Sophomore", "Junior", "Senior", "Graduate"]
MAJORS   = ["Computer Engineering", "Electrical Engineering",
            "Computer Science", "Mechanical Engineering", "Other"]

STRENGTHS = [
    {"id": "programming",       "label": "Programming / Software",   "icon": "💻"},
    {"id": "electrical",        "label": "Electrical / Circuits",    "icon": "⚡"},
    {"id": "hardware",          "label": "Hardware / PCB Design",    "icon": "🔌"},
    {"id": "embedded",          "label": "Embedded Systems",         "icon": "🖥️"},
    {"id": "networking",        "label": "Networking / Comm",        "icon": "🌐"},
    {"id": "security",          "label": "Cybersecurity",            "icon": "🔐"},
    {"id": "robotics",          "label": "Robotics / Automation",    "icon": "🤖"},
    {"id": "signal_processing", "label": "Signal Processing",        "icon": "📡"},
    {"id": "design",            "label": "Engineering Design",       "icon": "📐"},
    {"id": "data",              "label": "Data / Machine Learning",  "icon": "📊"},
]

ENGINEERING_COURSES = [
    {"code": "ENGR 1001", "name": "Engineering Orientation",        "credits": 0, "tags": ["engineering", "design"]},
    {"code": "ENGR 1041", "name": "Foundations of Design 1",        "credits": 3, "tags": ["engineering", "design"]},
    {"code": "ENGR 1051", "name": "Foundations of Design 2",        "credits": 3, "tags": ["engineering", "design"]},
    {"code": "ECCS 1611", "name": "Programming 1",                  "credits": 4, "tags": ["programming", "software"]},
    {"code": "ECCS 1621", "name": "Programming 2",                  "credits": 4, "tags": ["programming", "software"]},
    {"code": "ECCS 1721", "name": "Digital Logic",                  "credits": 4, "tags": ["electrical", "hardware"]},
    {"code": "ECCS 2311", "name": "Electric Circuits",              "credits": 4, "tags": ["electrical"]},
    {"code": "ECCS 2331", "name": "Digital Signal Processing",      "credits": 3, "tags": ["electrical", "signal_processing"]},
    {"code": "ECCS 2341", "name": "Electronics",                    "credits": 4, "tags": ["electrical", "hardware"]},
    {"code": "ECCS 2381", "name": "Maker Engineering",              "credits": 1, "tags": ["robotics", "design", "embedded"]},
    {"code": "ECCS 2671", "name": "Data Structures & Algorithms 1", "credits": 3, "tags": ["programming", "software"]},
    {"code": "ECCS 3241", "name": "Embedded Hardware-Software",     "credits": 4, "tags": ["embedded", "hardware", "programming"]},
    {"code": "ECCS 3351", "name": "Embedded Real-Time App",         "credits": 4, "tags": ["embedded", "programming", "robotics"]},
    {"code": "ECCS 3411", "name": "Computer Security",              "credits": 3, "tags": ["security", "programming", "networking"]},
    {"code": "ECCS 3611", "name": "Computer Architecture",          "credits": 4, "tags": ["hardware", "electrical"]},
    {"code": "ECCS 3631", "name": "Networks & Data Communications", "credits": 4, "tags": ["networking", "software"]},
    {"code": "ECCS 3661", "name": "Operating Systems",              "credits": 3, "tags": ["software", "programming"]},
]

DEFAULT_CAPSTONES = [
    {
        "id": "cap_01", "name": "Smart Home Automation System",
        "description": "Design and build an IoT-based home automation system using embedded microcontrollers, wireless networking protocols, and a real-time web dashboard for monitoring and control.",
        "tags": ["embedded", "electrical", "programming", "networking"],
        "required_skills": ["embedded", "programming"],
        "team_size": 4, "difficulty": "Intermediate",
    },
    {
        "id": "cap_02", "name": "Cybersecurity Intrusion Detection Platform",
        "description": "Build a network intrusion detection system using traffic analysis, ML-based anomaly detection, real-time alerting, and a security event dashboard.",
        "tags": ["security", "networking", "programming", "software"],
        "required_skills": ["security", "networking"],
        "team_size": 4, "difficulty": "Advanced",
    },
    {
        "id": "cap_03", "name": "Autonomous Robotics Platform",
        "description": "Develop a mobile autonomous robot with real-time sensor fusion, PID motor control, obstacle avoidance, and path planning running on a real-time OS.",
        "tags": ["robotics", "embedded", "programming", "hardware"],
        "required_skills": ["robotics", "embedded"],
        "team_size": 5, "difficulty": "Advanced",
    },
    {
        "id": "cap_04", "name": "FPGA-Based Signal Processing System",
        "description": "Implement DSP algorithms (FFT, filtering, modulation) on FPGA hardware using HDL for real-time audio processing or RF communications.",
        "tags": ["electrical", "signal_processing", "hardware"],
        "required_skills": ["electrical", "hardware"],
        "team_size": 3, "difficulty": "Expert",
    },
    {
        "id": "cap_05", "name": "Enterprise Network Infrastructure",
        "description": "Design, simulate, and deploy a scalable enterprise network with VLANs, routing protocols, QoS policies, and integrated security monitoring across multiple sites.",
        "tags": ["networking", "software", "security"],
        "required_skills": ["networking"],
        "team_size": 4, "difficulty": "Intermediate",
    },
    {
        "id": "cap_06", "name": "Embedded Medical Monitoring Device",
        "description": "Prototype a wearable biosignal acquisition system with low-power hardware, real-time data processing, Bluetooth telemetry, and a companion mobile dashboard.",
        "tags": ["embedded", "electrical", "hardware", "programming"],
        "required_skills": ["embedded", "electrical"],
        "team_size": 4, "difficulty": "Advanced",
    },
    {
        "id": "cap_07", "name": "Custom RISC Processor Design",
        "description": "Design and simulate a pipelined RISC processor from scratch in HDL, covering ALU design, instruction set architecture, cache hierarchy, and performance benchmarking.",
        "tags": ["hardware", "electrical", "engineering"],
        "required_skills": ["hardware", "electrical"],
        "team_size": 3, "difficulty": "Expert",
    },
    {
        "id": "cap_08", "name": "Full-Stack IoT Engineering Platform",
        "description": "Build a platform that ingests real-time sensor data from embedded edge devices, stores it in a cloud database, and visualizes it on an interactive analytics dashboard.",
        "tags": ["programming", "software", "networking", "embedded"],
        "required_skills": ["programming", "software"],
        "team_size": 4, "difficulty": "Intermediate",
    },
    {
        "id": "cap_09", "name": "Software-Defined Radio Communications",
        "description": "Develop an SDR system for real-time modulation/demodulation with a GUI for spectrum visualization and configurable radio parameter tuning.",
        "tags": ["electrical", "signal_processing", "programming"],
        "required_skills": ["signal_processing", "electrical"],
        "team_size": 3, "difficulty": "Expert",
    },
    {
        "id": "cap_10", "name": "Secure Embedded Firmware Framework",
        "description": "Create a security-hardened firmware framework featuring secure boot, encrypted OTA updates, and runtime anomaly detection with minimal performance overhead.",
        "tags": ["embedded", "security", "programming", "hardware"],
        "required_skills": ["embedded", "security"],
        "team_size": 4, "difficulty": "Advanced",
    },
]

TAG_COLORS = {
    "programming":       ("bg-blue-100 text-blue-800",   "#dbeafe", "#1d4ed8"),
    "software":          ("bg-sky-100 text-sky-800",      "#e0f2fe", "#0369a1"),
    "electrical":        ("bg-yellow-100 text-yellow-800","#fef9c3", "#854d0e"),
    "hardware":          ("bg-orange-100 text-orange-800","#ffedd5", "#9a3412"),
    "embedded":          ("bg-purple-100 text-purple-800","#f3e8ff", "#6b21a8"),
    "robotics":          ("bg-green-100 text-green-800",  "#dcfce7", "#166534"),
    "networking":        ("bg-cyan-100 text-cyan-800",    "#cffafe", "#155e75"),
    "security":          ("bg-red-100 text-red-800",      "#fee2e2", "#991b1b"),
    "signal_processing": ("bg-amber-100 text-amber-800",  "#fef3c7", "#92400e"),
    "design":            ("bg-pink-100 text-pink-800",    "#fce7f3", "#9d174d"),
    "engineering":       ("bg-slate-100 text-slate-700",  "#f1f5f9", "#334155"),
    "data":              ("bg-indigo-100 text-indigo-800","#e0e7ff", "#3730a3"),
}
DIFF_COLORS = {
    "Intermediate": ("#d1fae5", "#065f46"),
    "Advanced":     ("#dbeafe", "#1e40af"),
    "Expert":       ("#f3e8ff", "#5b21b6"),
}

# ─────────────────────────────────────────────────────────────────────────────
# Persistence
# ─────────────────────────────────────────────────────────────────────────────

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {"students": {}, "capstones": DEFAULT_CAPSTONES, "teams": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ─────────────────────────────────────────────────────────────────────────────
# Recommendation Algorithm
# ─────────────────────────────────────────────────────────────────────────────

def score_capstone(capstone, student):
    """
    Three-factor scoring (each 0.0–1.0):
      course_score  (40%) – coverage of matching courses weighted by enjoyment
      pref_score    (40%) – explicit student interest rating for this project
      strength_score(20%) – overlap of self-reported strengths vs required skills

    Returns dict with per-factor breakdown and total.
    """
    courses_taken = {c["code"]: c["rating"] for c in student.get("courses", [])}

    # ── Course score ───────────────────────────────────────────────────────
    tag_scores = []
    tag_breakdown = {}
    for tag in capstone["tags"]:
        courses_with_tag = [c for c in ENGINEERING_COURSES if tag in c["tags"]]
        if not courses_with_tag:
            continue
        taken_with_tag = [c for c in courses_with_tag if c["code"] in courses_taken]
        if not taken_with_tag:
            tag_scores.append(0.0)
            tag_breakdown[tag] = 0.0
            continue
        coverage   = len(taken_with_tag) / len(courses_with_tag)
        avg_enjoy  = sum(courses_taken[c["code"]] for c in taken_with_tag) / len(taken_with_tag)
        interest   = 0.4 + (avg_enjoy / 5.0) * 0.6   # 0.4–1.0
        ts = coverage * interest
        tag_scores.append(ts)
        tag_breakdown[tag] = round(ts, 3)

    course_score = sum(tag_scores) / len(tag_scores) if tag_scores else 0.0

    # ── Preference score ───────────────────────────────────────────────────
    prefs = {p["project_id"]: p["interest"] for p in student.get("project_preferences", [])}
    pref_score = prefs.get(capstone["id"], 0) / 5.0

    # ── Strength score ─────────────────────────────────────────────────────
    student_strengths = set(student.get("strengths", []))
    required = set(capstone.get("required_skills", []))
    strength_score = (len(student_strengths & required) / len(required)) if required else 0.5

    total = round(0.40 * course_score + 0.40 * pref_score + 0.20 * strength_score, 4)

    return {
        "total":    total,
        "course":   round(course_score, 3),
        "pref":     round(pref_score, 3),
        "strength": round(strength_score, 3),
        "tags":     tag_breakdown,
    }


def top_recommendations(student, capstones, n=3):
    scored = sorted(
        [(score_capstone(c, student), c) for c in capstones],
        key=lambda x: x[0]["total"],
        reverse=True,
    )
    return scored[:n]


# ─────────────────────────────────────────────────────────────────────────────
# Team Formation Algorithm
# ─────────────────────────────────────────────────────────────────────────────

def run_team_formation(data):
    """
    1. Score every student–capstone pair.
    2. Greedy assignment: most-opinionated students pick first; respect capacity.
    3. Within each project, form balanced sub-teams by rotating through strength profiles.
    Returns: {capstone_id: {capstone, teams: [{number, members}]}}
    """
    submitted = {sid: s for sid, s in data["students"].items() if s.get("submitted")}
    if not submitted:
        return {}

    capstones_list = data.get("capstones", DEFAULT_CAPSTONES)
    cap_by_id      = {c["id"]: c for c in capstones_list}

    # Step 1 – score matrix
    scores = {}
    for sid, student in submitted.items():
        scores[sid] = {c["id"]: score_capstone(c, student)["total"] for c in capstones_list}

    # Step 2 – greedy assignment with capacity guard
    n           = len(submitted)
    cap_ids     = list(cap_by_id)
    capacity    = {cid: max(cap_by_id[cid]["team_size"] * 3, math.ceil(n / len(cap_ids)) + 2)
                   for cid in cap_ids}
    assignment  = defaultdict(list)

    # Students with biggest score gap between top-2 choices go first
    def certainty(sid):
        vals = sorted(scores[sid].values(), reverse=True)
        return vals[0] - (vals[1] if len(vals) > 1 else 0)

    for sid in sorted(submitted, key=certainty, reverse=True):
        ranked = sorted(scores[sid].items(), key=lambda x: x[1], reverse=True)
        for cid, _ in ranked:
            if capacity[cid] > 0:
                assignment[cid].append(sid)
                capacity[cid] -= 1
                break

    # Step 3 – balance sub-teams by round-robin on primary strength
    result = {}
    for cid, sids in assignment.items():
        cap       = cap_by_id[cid]
        team_size = cap["team_size"]

        def primary_strength(sid):
            strengths = submitted[sid].get("strengths", [""])
            return strengths[0] if strengths else ""

        ordered   = sorted(sids, key=primary_strength)
        n_teams   = max(1, math.ceil(len(ordered) / team_size))
        buckets   = [[] for _ in range(n_teams)]
        for i, sid in enumerate(ordered):
            buckets[i % n_teams].append(sid)

        result[cid] = {
            "capstone": cap,
            "teams": [
                {
                    "number":  ti + 1,
                    "members": [submitted[sid] | {"id": sid} for sid in bucket],
                }
                for ti, bucket in enumerate(buckets) if bucket
            ],
        }

    return result


# ─────────────────────────────────────────────────────────────────────────────
# Shared HTML fragments
# ─────────────────────────────────────────────────────────────────────────────

def tag_pill_html(tag):
    _, bg, fg = TAG_COLORS.get(tag, ("", "#e5e7eb", "#374151"))
    return (f'<span style="background:{bg};color:{fg};padding:2px 8px;border-radius:99px;'
            f'font-size:0.72rem;font-weight:600;font-family:monospace;">&lt;{tag}&gt;</span>')


def base_page(content, step=0, faculty=False):
    steps = ["Profile", "Courses", "Projects", "Results"]
    step_html = ""
    if not faculty and step > 0:
        parts = []
        for i, label in enumerate(steps, 1):
            active  = i == step
            done    = i < step
            circle_style = (
                "background:#2563eb;color:#fff;" if active else
                "background:#10b981;color:#fff;" if done else
                "background:#cbd5e1;color:#64748b;"
            )
            line = '<div style="flex:1;height:2px;background:#2563eb;margin:0 4px;"></div>' if i < 4 else ''
            parts.append(
                f'<div style="display:flex;align-items:center;gap:6px;">'
                f'  <div style="width:28px;height:28px;border-radius:50%;{circle_style}'
                f'       display:flex;align-items:center;justify-content:center;font-size:.8rem;font-weight:700;">'
                f'    {"✓" if done else i}</div>'
                f'  <span style="font-size:.8rem;font-weight:{"700" if active else "500"};'
                f'         color:{"#e2e8f0" if active else "#94a3b8"};">{label}</span>'
                f'  {line}'
                f'</div>'
            )
        step_html = (
            '<div style="display:flex;align-items:center;gap:4px;margin-top:8px;">'
            + "".join(parts) + '</div>'
        )

    nav_right = (
        '<a href="/faculty/dashboard" style="color:#94a3b8;text-decoration:none;font-size:.85rem;">'
        '🏫 Faculty Dashboard</a>'
        if not faculty else
        '<a href="/" style="color:#94a3b8;text-decoration:none;font-size:.85rem;">← Student View</a>'
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Engineering Capstone Advisor</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{
    --navy:   #1a2e4a;
    --blue:   #2563eb;
    --green:  #10b981;
    --amber:  #f59e0b;
    --red:    #ef4444;
    --purple: #7c3aed;
    --bg:     #f0f4f8;
    --card:   #ffffff;
    --border: #e2e8f0;
    --muted:  #64748b;
    --text:   #0f172a;
  }}
  body {{ font-family: 'Inter', system-ui, sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; }}
  .navbar {{ background: var(--navy); padding: 0 2rem; }}
  .navbar-inner {{ max-width: 1100px; margin: 0 auto; display: flex; align-items: flex-start; justify-content: space-between; padding: 14px 0; }}
  .brand {{ color: #fff; font-size: 1.15rem; font-weight: 800; letter-spacing: -.3px; }}
  .brand small {{ display: block; font-size: .72rem; font-weight: 400; color: #94a3b8; margin-top: 1px; }}
  .container {{ max-width: 1000px; margin: 0 auto; padding: 2rem 1.5rem 4rem; }}
  .card {{ background: var(--card); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; margin-bottom: 1.5rem; box-shadow: 0 1px 4px rgba(0,0,0,.06); }}
  .card-header {{ background: #f8fafc; border-bottom: 1px solid var(--border); padding: 14px 20px; display: flex; align-items: center; gap: 10px; }}
  .card-header h2 {{ font-size: 1rem; font-weight: 700; color: var(--navy); }}
  .card-header .badge {{ font-size: .7rem; font-weight: 600; padding: 3px 8px; border-radius: 99px; }}
  .card-body {{ padding: 20px; }}
  .form-group {{ margin-bottom: 1.2rem; }}
  label {{ display: block; font-size: .875rem; font-weight: 600; color: #374151; margin-bottom: 6px; }}
  label .hint {{ font-weight: 400; color: var(--muted); }}
  input[type=text], input[type=email], select, textarea {{
    width: 100%; padding: 9px 12px; border: 1px solid #d1d5db; border-radius: 8px;
    font-size: .9rem; font-family: inherit; background: #fff; outline: none;
    transition: border-color .2s;
  }}
  input:focus, select:focus, textarea:focus {{ border-color: var(--blue); box-shadow: 0 0 0 3px rgba(37,99,235,.1); }}
  textarea {{ resize: vertical; min-height: 80px; }}
  .btn {{ display: inline-flex; align-items: center; gap: 6px; padding: 10px 22px;
          border: none; border-radius: 8px; font-size: .9rem; font-weight: 600;
          cursor: pointer; font-family: inherit; transition: all .15s; text-decoration: none; }}
  .btn-primary  {{ background: var(--blue);   color: #fff; }}
  .btn-success  {{ background: var(--green);  color: #fff; }}
  .btn-purple   {{ background: var(--purple); color: #fff; }}
  .btn-amber    {{ background: var(--amber);  color: #fff; }}
  .btn-ghost    {{ background: transparent; color: var(--muted); border: 1px solid var(--border); }}
  .btn:hover {{ filter: brightness(1.08); transform: translateY(-1px); }}
  .btn:active {{ transform: translateY(0); }}
  .chip-grid {{ display: flex; flex-wrap: wrap; gap: 8px; }}
  .chip {{ display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px;
           border: 2px solid var(--border); border-radius: 99px; font-size: .82rem;
           font-weight: 500; cursor: pointer; transition: all .15s; background: #fff;
           user-select: none; }}
  .chip.selected {{ border-color: var(--blue); background: #eff6ff; color: var(--blue); }}
  .chip:hover:not(.selected) {{ border-color: #94a3b8; background: #f8fafc; }}
  .chip input {{ display: none; }}
  table {{ width: 100%; border-collapse: collapse; }}
  thead th {{ background: #f8fafc; padding: 10px 14px; font-size: .8rem; font-weight: 700;
              text-transform: uppercase; letter-spacing: .05em; color: var(--muted);
              text-align: left; border-bottom: 2px solid var(--border); }}
  tbody tr {{ border-bottom: 1px solid #f1f5f9; transition: background .1s; }}
  tbody tr:hover {{ background: #f8fafc; }}
  tbody td {{ padding: 10px 14px; font-size: .875rem; vertical-align: middle; }}
  .course-code {{ font-family: 'JetBrains Mono', monospace; font-size: .8rem;
                  color: #4b5563; background: #f1f5f9; padding: 2px 6px; border-radius: 4px; }}
  .slider-wrap {{ display: flex; align-items: center; gap: 8px; }}
  input[type=range] {{ -webkit-appearance: none; height: 4px; border-radius: 99px;
                       background: #e2e8f0; outline: none; cursor: pointer;
                       accent-color: var(--blue); }}
  input[type=range]:disabled {{ opacity: .35; cursor: not-allowed; }}
  .stars {{ font-size: .95rem; letter-spacing: 1px; }}
  .project-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }}
  .project-card {{ border: 2px solid var(--border); border-radius: 12px; padding: 16px;
                   background: #fff; transition: border-color .2s; position: relative; }}
  .project-card.selected {{ border-color: var(--blue); background: #eff6ff; }}
  .proj-title {{ font-size: .9rem; font-weight: 700; color: var(--navy); margin-bottom: 6px; }}
  .proj-desc {{ font-size: .8rem; color: var(--muted); margin-bottom: 10px; line-height: 1.5; }}
  .tags {{ display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 10px; }}
  .star-rating {{ display: flex; gap: 4px; }}
  .star-btn {{ font-size: 1.3rem; cursor: pointer; color: #d1d5db; transition: color .1s; }}
  .star-btn.active {{ color: var(--amber); }}
  .result-card {{ border: 2px solid var(--border); border-radius: 14px; overflow: hidden; margin-bottom: 18px; }}
  .result-header {{ padding: 16px 20px; display: flex; justify-content: space-between; align-items: center; }}
  .result-body {{ padding: 16px 20px; }}
  .score-bar-wrap {{ background: #e5e7eb; border-radius: 99px; height: 8px; overflow: hidden; }}
  .score-bar {{ height: 8px; border-radius: 99px; transition: width 1s ease; }}
  .factor-row {{ display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }}
  .factor-label {{ width: 130px; font-size: .8rem; font-weight: 600; color: var(--muted); flex-shrink: 0; }}
  .factor-bar-wrap {{ flex: 1; background: #e5e7eb; border-radius: 99px; height: 6px; }}
  .factor-bar {{ height: 6px; border-radius: 99px; }}
  .factor-pct {{ width: 36px; text-align: right; font-size: .8rem; font-weight: 700; }}
  .team-card {{ border: 1px solid var(--border); border-radius: 10px; padding: 14px; background: #fafafa; margin-bottom: 12px; }}
  .team-header {{ font-size: .85rem; font-weight: 700; color: var(--navy); margin-bottom: 10px; }}
  .member-chip {{ display: inline-flex; align-items: center; gap: 6px; padding: 5px 12px;
                  background: #fff; border: 1px solid var(--border); border-radius: 99px;
                  font-size: .8rem; margin: 3px; }}
  .alert {{ padding: 12px 16px; border-radius: 8px; margin-bottom: 16px; font-size: .875rem; }}
  .alert-success {{ background: #d1fae5; color: #065f46; border: 1px solid #a7f3d0; }}
  .alert-warning {{ background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }}
  .stat-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 14px; }}
  .stat-card {{ background: #fff; border: 1px solid var(--border); border-radius: 10px; padding: 16px; text-align: center; }}
  .stat-card .num {{ font-size: 2rem; font-weight: 800; color: var(--navy); }}
  .stat-card .lbl {{ font-size: .78rem; color: var(--muted); font-weight: 500; margin-top: 2px; }}
  .tab-bar {{ display: flex; gap: 4px; margin-bottom: 1.5rem; border-bottom: 2px solid var(--border); }}
  .tab {{ padding: 10px 18px; font-size: .875rem; font-weight: 600; color: var(--muted);
          cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -2px; transition: all .15s; }}
  .tab.active {{ color: var(--blue); border-bottom-color: var(--blue); }}
  .tab-content {{ display: none; }}
  .tab-content.active {{ display: block; }}
  .nav-footer {{ display: flex; gap: 10px; justify-content: space-between; align-items: center;
                 padding-top: 1rem; border-top: 1px solid var(--border); margin-top: 1.5rem; }}
  @media (max-width: 640px) {{
    .project-grid {{ grid-template-columns: 1fr; }}
    .factor-label {{ width: 90px; }}
  }}
</style>
</head>
<body>
<nav class="navbar">
  <div class="navbar-inner">
    <div class="brand">
      🎓 Engineering Capstone Advisor
      <small>Ohio Northern University · Department of Engineering</small>
    </div>
    <div style="text-align:right;">
      {nav_right}
      {step_html}
    </div>
  </div>
</nav>
<div class="container">
{content}
</div>
<script>
  // Generic tab switcher
  document.querySelectorAll('.tab').forEach(t => {{
    t.addEventListener('click', () => {{
      const group = t.dataset.tab;
      document.querySelectorAll(`.tab[data-tab="${{group}}"]`).forEach(x => x.classList.remove('active'));
      document.querySelectorAll(`.tab-content[data-tab="${{group}}"]`).forEach(x => x.classList.remove('active'));
      t.classList.add('active');
      document.getElementById(t.dataset.target).classList.add('active');
    }});
  }});
</script>
</body>
</html>"""


# ─────────────────────────────────────────────────────────────────────────────
# Route helpers
# ─────────────────────────────────────────────────────────────────────────────

def get_or_create_student_id():
    if "student_id" not in session:
        session["student_id"] = str(uuid.uuid4())[:8]
    return session["student_id"]


# ─────────────────────────────────────────────────────────────────────────────
# Routes — Landing
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    content = """
    <div style="text-align:center;padding:3rem 1rem;">
      <div style="font-size:3.5rem;margin-bottom:16px;">🎓</div>
      <h1 style="font-size:2rem;font-weight:800;color:#1a2e4a;margin-bottom:10px;">
        Engineering Capstone Advisor
      </h1>
      <p style="color:#64748b;font-size:1.05rem;max-width:560px;margin:0 auto 32px;line-height:1.7;">
        Tell us about your background, courses, and project interests — and we'll
        recommend the capstone projects that fit you best and form balanced teams.
      </p>
      <div style="display:flex;gap:14px;justify-content:center;flex-wrap:wrap;">
        <a href="/step/1" class="btn btn-primary" style="font-size:1rem;padding:13px 28px;">
          ▶ Start My Profile
        </a>
        <a href="/faculty/login" class="btn btn-ghost">
          🏫 Faculty Login
        </a>
      </div>
    </div>

    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:14px;margin-top:2rem;">
      <div class="card" style="text-align:center;">
        <div class="card-body">
          <div style="font-size:2rem;margin-bottom:8px;">📋</div>
          <div style="font-weight:700;margin-bottom:4px;">Build Your Profile</div>
          <div style="font-size:.82rem;color:#64748b;">Share your strengths, experience, and courses completed.</div>
        </div>
      </div>
      <div class="card" style="text-align:center;">
        <div class="card-body">
          <div style="font-size:2rem;margin-bottom:8px;">⭐</div>
          <div style="font-weight:700;margin-bottom:4px;">Rate Your Interests</div>
          <div style="font-size:.82rem;color:#64748b;">Rank projects and rate how much you enjoyed each course.</div>
        </div>
      </div>
      <div class="card" style="text-align:center;">
        <div class="card-body">
          <div style="font-size:2rem;margin-bottom:8px;">🏆</div>
          <div style="font-weight:700;margin-bottom:4px;">Get Matched</div>
          <div style="font-size:.82rem;color:#64748b;">Receive your top 3 personalized capstone recommendations.</div>
        </div>
      </div>
      <div class="card" style="text-align:center;">
        <div class="card-body">
          <div style="font-size:2rem;margin-bottom:8px;">👥</div>
          <div style="font-weight:700;margin-bottom:4px;">Form Your Team</div>
          <div style="font-size:.82rem;color:#64748b;">Faculty use smart algorithms to build balanced project teams.</div>
        </div>
      </div>
    </div>
    """
    return base_page(content, step=0)


# ─────────────────────────────────────────────────────────────────────────────
# Step 1 — Student Profile
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/step/1", methods=["GET", "POST"])
def step1():
    sid = get_or_create_student_id()
    data = load_data()

    if request.method == "POST":
        strengths = request.form.getlist("strengths")
        data["students"].setdefault(sid, {})
        data["students"][sid].update({
            "id":         sid,
            "name":       request.form.get("name", "").strip(),
            "student_id": request.form.get("student_id", "").strip(),
            "year":       request.form.get("year", ""),
            "major":      request.form.get("major", ""),
            "strengths":  strengths,
            "experience": request.form.get("experience", "").strip(),
            "submitted":  False,
        })
        save_data(data)
        return redirect(url_for("step2"))

    existing = data["students"].get(sid, {})

    year_opts  = "".join(f'<option {"selected" if existing.get("year") == y else ""}>{y}</option>' for y in YEARS)
    major_opts = "".join(f'<option {"selected" if existing.get("major") == m else ""}>{m}</option>' for m in MAJORS)

    chips = ""
    for s in STRENGTHS:
        checked = "selected" if s["id"] in existing.get("strengths", []) else ""
        chips += (f'<label class="chip {checked}" onclick="toggleChip(this, \'{s["id"]}\')"> '
                  f'<input type="checkbox" name="strengths" value="{s["id"]}" '
                  f'       {"checked" if checked else ""}>'
                  f'{s["icon"]} {s["label"]}</label>')

    content = f"""
    <div class="card">
      <div class="card-header">
        <h2>👤 Student Profile</h2>
        <span class="badge" style="background:#eff6ff;color:#1d4ed8;">Step 1 of 4</span>
      </div>
      <div class="card-body">
        <form method="POST">
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
            <div class="form-group">
              <label>Full Name</label>
              <input type="text" name="name" value="{existing.get('name','')}" required placeholder="Jane Smith">
            </div>
            <div class="form-group">
              <label>Student ID</label>
              <input type="text" name="student_id" value="{existing.get('student_id','')}" placeholder="e.g. 123456">
            </div>
            <div class="form-group">
              <label>Academic Year</label>
              <select name="year"><option value="">-- Select --</option>{year_opts}</select>
            </div>
            <div class="form-group">
              <label>Major</label>
              <select name="major"><option value="">-- Select --</option>{major_opts}</select>
            </div>
          </div>

          <div class="form-group" style="margin-top:8px;">
            <label>Your Strengths <span class="hint">(select all that apply)</span></label>
            <div class="chip-grid">{chips}</div>
          </div>

          <div class="form-group">
            <label>Relevant Experience <span class="hint">(internships, personal projects, labs — optional)</span></label>
            <textarea name="experience" placeholder="e.g. Interned at XYZ, built an Arduino weather station, completed online ML course...">{existing.get('experience','')}</textarea>
          </div>

          <div class="nav-footer">
            <a href="/" class="btn btn-ghost">← Back</a>
            <button type="submit" class="btn btn-primary">Next: Courses →</button>
          </div>
        </form>
      </div>
    </div>
    <script>
      function toggleChip(el, id) {{
        el.classList.toggle('selected');
        el.querySelector('input').checked = el.classList.contains('selected');
      }}
    </script>
    """
    return base_page(content, step=1)


# ─────────────────────────────────────────────────────────────────────────────
# Step 2 — Courses + Enjoyment
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/step/2", methods=["GET", "POST"])
def step2():
    sid = get_or_create_student_id()
    data = load_data()

    if request.method == "POST":
        taken_codes = set(request.form.getlist("taken"))
        courses = []
        for c in ENGINEERING_COURSES:
            if c["code"] in taken_codes:
                rating_key = f"rating_{c['code'].replace(' ', '_')}"
                courses.append({"code": c["code"], "rating": int(request.form.get(rating_key, 3))})
        data["students"].setdefault(sid, {})["courses"] = courses
        save_data(data)
        return redirect(url_for("step3"))

    existing     = data["students"].get(sid, {})
    taken_map    = {c["code"]: c["rating"] for c in existing.get("courses", [])}

    rows = ""
    for c in ENGINEERING_COURSES:
        code_key = c["code"].replace(" ", "_")
        taken    = c["code"] in taken_map
        rating   = taken_map.get(c["code"], 3)
        tags_html = " ".join(tag_pill_html(t) for t in c["tags"])
        rows += f"""
        <tr>
          <td style="text-align:center;">
            <input type="checkbox" name="taken" value="{c['code']}"
                   class="course-check" data-id="{code_key}"
                   {"checked" if taken else ""}
                   style="width:16px;height:16px;cursor:pointer;accent-color:#2563eb;">
          </td>
          <td><span class="course-code">{c['code']}</span></td>
          <td style="font-weight:500;">{c['name']}</td>
          <td><div style="display:flex;flex-wrap:wrap;gap:4px;">{tags_html}</div></td>
          <td>
            <div class="slider-wrap rating-cell" id="rcell_{code_key}"
                 style="opacity:{'1' if taken else '0.3'};pointer-events:{'auto' if taken else 'none'};">
              <input type="range" name="rating_{code_key}" min="0" max="5" step="1"
                     value="{rating}" class="enj-slider" style="width:100px;"
                     oninput="updateStars(this)">
              <span class="stars" id="stars_{code_key}">{stars_html(rating)}</span>
            </div>
          </td>
        </tr>"""

    content = f"""
    <div class="card">
      <div class="card-header">
        <h2>📚 Engineering Courses</h2>
        <span class="badge" style="background:#eff6ff;color:#1d4ed8;">Step 2 of 4</span>
      </div>
      <div class="card-body" style="padding:0;">
        <div style="padding:16px 20px;border-bottom:1px solid #e2e8f0;background:#fffbeb;font-size:.85rem;color:#92400e;">
          ✅ Check every course you have <strong>completed</strong>, then drag the slider to rate how much you <strong>enjoyed</strong> it (0 = disliked, 5 = loved).
        </div>
        <form method="POST" id="coursesForm">
          <div style="overflow-x:auto;">
            <table>
              <thead>
                <tr>
                  <th style="width:50px;">Done</th>
                  <th style="width:120px;">Code</th>
                  <th>Course Name</th>
                  <th>Topics</th>
                  <th style="width:200px;">Enjoyment</th>
                </tr>
              </thead>
              <tbody>{rows}</tbody>
            </table>
          </div>
          <div class="nav-footer" style="margin:0;padding:16px 20px;">
            <a href="/step/1" class="btn btn-ghost">← Back</a>
            <button type="submit" class="btn btn-primary">Next: Project Preferences →</button>
          </div>
        </form>
      </div>
    </div>
    <script>
      function stars_from_val(v) {{
        return '★'.repeat(v) + '☆'.repeat(5 - v);
      }}
      function updateStars(slider) {{
        const id = slider.name.replace('rating_', 'stars_');
        const el = document.getElementById(id);
        if (el) el.textContent = stars_from_val(parseInt(slider.value));
      }}
      document.querySelectorAll('.course-check').forEach(cb => {{
        cb.addEventListener('change', function() {{
          const id   = this.dataset.id;
          const cell = document.getElementById('rcell_' + id);
          if (cell) {{
            cell.style.opacity = this.checked ? '1' : '0.3';
            cell.style.pointerEvents = this.checked ? 'auto' : 'none';
          }}
        }});
      }});
    </script>
    """
    return base_page(content, step=2)


def stars_html(rating):
    return "★" * int(rating) + "☆" * (5 - int(rating))


# ─────────────────────────────────────────────────────────────────────────────
# Step 3 — Project Preferences
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/step/3", methods=["GET", "POST"])
def step3():
    sid = get_or_create_student_id()
    data = load_data()

    if request.method == "POST":
        prefs = []
        for c in data.get("capstones", DEFAULT_CAPSTONES):
            key     = f"interest_{c['id']}"
            interest = int(request.form.get(key, 0))
            rank_key = f"rank_{c['id']}"
            rank     = int(request.form.get(rank_key, 0))
            prefs.append({"project_id": c["id"], "interest": interest, "rank": rank})
        data["students"].setdefault(sid, {})["project_preferences"] = prefs
        save_data(data)
        return redirect(url_for("step4"))

    existing    = data["students"].get(sid, {})
    capstones   = data.get("capstones", DEFAULT_CAPSTONES)
    pref_map    = {p["project_id"]: p for p in existing.get("project_preferences", [])}

    cards = ""
    for cap in capstones:
        pid       = cap["id"]
        interest  = pref_map.get(pid, {}).get("interest", 0)
        rank      = pref_map.get(pid, {}).get("rank", 0)
        diff_bg, diff_fg = DIFF_COLORS.get(cap.get("difficulty", ""), ("#f1f5f9", "#334155"))
        tags_html = " ".join(tag_pill_html(t) for t in cap["tags"])
        req_html  = " ".join(tag_pill_html(t) for t in cap.get("required_skills", []))

        stars = "".join(
            f'<span class="star-btn {"active" if i <= interest else ""}" '
            f'      data-pid="{pid}" data-val="{i}">★</span>'
            for i in range(1, 6)
        )

        cards += f"""
        <div class="project-card {'selected' if interest >= 3 else ''}" id="pcard_{pid}">
          <input type="hidden" name="interest_{pid}" id="interest_{pid}" value="{interest}">
          <input type="hidden" name="rank_{pid}" id="rank_{pid}" value="{rank}">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;margin-bottom:6px;">
            <div class="proj-title">{cap['name']}</div>
            <span style="font-size:.7rem;font-weight:700;padding:2px 8px;border-radius:99px;
                         background:{diff_bg};color:{diff_fg};flex-shrink:0;">{cap.get('difficulty','')}</span>
          </div>
          <p class="proj-desc">{cap['description']}</p>
          <div class="tags" style="margin-bottom:6px;">{tags_html}</div>
          <div style="font-size:.75rem;color:#64748b;margin-bottom:8px;">
            <strong>Requires:</strong> {req_html}
          </div>
          <div style="display:flex;align-items:center;gap:8px;margin-top:6px;">
            <span style="font-size:.78rem;font-weight:600;color:#64748b;">Interest:</span>
            <div class="star-rating" id="stars_{pid}">{stars}</div>
            <span style="font-size:.78rem;color:#94a3b8;" id="val_{pid}">
              {'⬤' * interest + '○' * (5 - interest) if interest else 'tap to rate'}
            </span>
          </div>
        </div>"""

    content = f"""
    <div class="card">
      <div class="card-header">
        <h2>🗂️ Project Preferences</h2>
        <span class="badge" style="background:#eff6ff;color:#1d4ed8;">Step 3 of 4</span>
      </div>
      <div class="card-body">
        <div class="alert alert-warning" style="margin-bottom:16px;">
          ⭐ Rate each project from 1–5 stars based on your interest. A rating of 3+ indicates you'd be happy to work on it.
        </div>
        <form method="POST" id="prefForm">
          <div class="project-grid">{cards}</div>
          <div class="nav-footer">
            <a href="/step/2" class="btn btn-ghost">← Back</a>
            <button type="submit" class="btn btn-purple">Get My Recommendations →</button>
          </div>
        </form>
      </div>
    </div>
    <script>
      document.querySelectorAll('.star-btn').forEach(btn => {{
        btn.addEventListener('click', function() {{
          const pid = this.dataset.pid;
          const val = parseInt(this.dataset.val);
          document.getElementById('interest_' + pid).value = val;
          document.querySelectorAll(`.star-btn[data-pid="${{pid}}"]`).forEach(s => {{
            s.classList.toggle('active', parseInt(s.dataset.val) <= val);
          }});
          const valEl = document.getElementById('val_' + pid);
          if (valEl) valEl.textContent = '⬤'.repeat(val) + '○'.repeat(5 - val);
          const card = document.getElementById('pcard_' + pid);
          if (card) card.classList.toggle('selected', val >= 3);
        }});
      }});
    </script>
    """
    return base_page(content, step=3)


# ─────────────────────────────────────────────────────────────────────────────
# Step 4 — Recommendations
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/step/4")
def step4():
    sid  = get_or_create_student_id()
    data = load_data()
    student = data["students"].get(sid)

    if not student:
        return redirect(url_for("step1"))

    # Mark as submitted
    data["students"][sid]["submitted"] = True
    save_data(data)

    capstones = data.get("capstones", DEFAULT_CAPSTONES)
    recs      = top_recommendations(student, capstones, n=3)

    medals  = ["🥇", "🥈", "🥉"]
    colors  = ["#10b981", "#2563eb", "#f59e0b"]
    borders = ["#d1fae5", "#dbeafe", "#fef3c7"]

    cards = ""
    for rank, (sc, cap) in enumerate(recs):
        total_pct  = int(sc["total"] * 100)
        course_pct = int(sc["course"] * 100)
        pref_pct   = int(sc["pref"] * 100)
        str_pct    = int(sc["strength"] * 100)
        color      = colors[rank]
        bg         = borders[rank]
        medal      = medals[rank]
        tags_html  = " ".join(tag_pill_html(t) for t in cap["tags"])
        diff_bg, diff_fg = DIFF_COLORS.get(cap.get("difficulty", ""), ("#f1f5f9", "#334155"))

        # Tag contribution breakdown
        tag_rows = ""
        for tag, ts in sorted(sc.get("tags", {}).items(), key=lambda x: -x[1]):
            _, tbg, tfg = TAG_COLORS.get(tag, ("", "#e5e7eb", "#374151"))
            tag_rows += (f'<div style="display:inline-flex;align-items:center;gap:6px;margin:2px;">'
                         f'{tag_pill_html(tag)}'
                         f'<div style="width:60px;height:4px;background:#e5e7eb;border-radius:99px;overflow:hidden;">'
                         f'  <div style="height:4px;width:{int(ts*100)}%;background:{tfg};border-radius:99px;"></div>'
                         f'</div><span style="font-size:.72rem;color:{tfg};font-weight:700;">{int(ts*100)}%</span>'
                         f'</div>')

        cards += f"""
        <div class="result-card" style="border-color:{color};">
          <div class="result-header" style="background:{bg};">
            <div>
              <div style="font-size:1.1rem;font-weight:800;color:#0f172a;">{medal} {cap['name']}</div>
              <div style="font-size:.8rem;color:#64748b;margin-top:2px;">
                {cap.get('team_size',4)}-person team &nbsp;·&nbsp;
                <span style="font-weight:700;padding:1px 7px;border-radius:99px;background:{diff_bg};color:{diff_fg};">{cap.get('difficulty','')}</span>
              </div>
            </div>
            <div style="text-align:center;">
              <div style="font-size:2rem;font-weight:800;color:{color};">{total_pct}%</div>
              <div style="font-size:.72rem;color:#64748b;font-weight:600;">Match Score</div>
            </div>
          </div>
          <div class="result-body">
            <div class="score-bar-wrap" style="margin-bottom:14px;">
              <div class="score-bar" style="width:{total_pct}%;background:{color};"></div>
            </div>
            <p style="font-size:.875rem;color:#374151;line-height:1.6;margin-bottom:14px;">{cap['description']}</p>

            <div style="margin-bottom:14px;">
              <div class="factor-row">
                <span class="factor-label">📚 Course Match</span>
                <div class="factor-bar-wrap">
                  <div class="factor-bar" style="width:{course_pct}%;background:#7c3aed;"></div>
                </div>
                <span class="factor-pct" style="color:#7c3aed;">{course_pct}%</span>
              </div>
              <div class="factor-row">
                <span class="factor-label">⭐ Your Interest</span>
                <div class="factor-bar-wrap">
                  <div class="factor-bar" style="width:{pref_pct}%;background:#2563eb;"></div>
                </div>
                <span class="factor-pct" style="color:#2563eb;">{pref_pct}%</span>
              </div>
              <div class="factor-row">
                <span class="factor-label">💪 Skill Fit</span>
                <div class="factor-bar-wrap">
                  <div class="factor-bar" style="width:{str_pct}%;background:#10b981;"></div>
                </div>
                <span class="factor-pct" style="color:#10b981;">{str_pct}%</span>
              </div>
            </div>

            <div style="margin-bottom:10px;">
              <div style="font-size:.78rem;font-weight:700;color:#64748b;margin-bottom:6px;">TOPIC ALIGNMENT:</div>
              <div>{tag_rows}</div>
            </div>

            <div class="tags">{tags_html}</div>
          </div>
        </div>"""

    name     = student.get("name", "Student")
    n_taken  = len(student.get("courses", []))
    n_prefs  = sum(1 for p in student.get("project_preferences", []) if p.get("interest", 0) >= 3)
    strengths_str = ", ".join(student.get("strengths", [])) or "Not specified"

    content = f"""
    <div class="alert alert-success">
      ✅ <strong>{name}</strong>, your profile has been submitted! Faculty will use this data to finalize project assignments.
    </div>

    <div class="card">
      <div class="card-header">
        <h2>📊 Your Summary</h2>
      </div>
      <div class="card-body">
        <div class="stat-grid">
          <div class="stat-card">
            <div class="num">{n_taken}</div>
            <div class="lbl">Courses Completed</div>
          </div>
          <div class="stat-card">
            <div class="num">{n_prefs}</div>
            <div class="lbl">Projects You'd Enjoy</div>
          </div>
          <div class="stat-card">
            <div class="num">{len(student.get('strengths', []))}</div>
            <div class="lbl">Strengths Listed</div>
          </div>
        </div>
        <div style="margin-top:14px;font-size:.875rem;color:#374151;">
          <strong>Your strengths:</strong> {strengths_str}
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-header">
        <h2>🏆 Your Top 3 Capstone Recommendations</h2>
        <span class="badge" style="background:#eff6ff;color:#1d4ed8;">Personalized for {name}</span>
      </div>
      <div class="card-body">
        <p style="font-size:.85rem;color:#64748b;margin-bottom:18px;">
          Scored using 40% course coverage + enjoyment, 40% your stated interest, and 20% skill alignment.
        </p>
        {cards}
      </div>
    </div>

    <div style="text-align:center;padding:1rem 0;">
      <a href="/step/1" class="btn btn-ghost" style="margin-right:10px;">✏️ Edit My Profile</a>
      <a href="/step/3" class="btn btn-ghost">← Back to Preferences</a>
    </div>
    """
    return base_page(content, step=4)


# ─────────────────────────────────────────────────────────────────────────────
# Faculty — Login
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/faculty/login", methods=["GET", "POST"])
def faculty_login():
    error = ""
    if request.method == "POST":
        if request.form.get("password") == FACULTY_PASS:
            session["faculty"] = True
            return redirect(url_for("faculty_dashboard"))
        error = "Incorrect password."

    content = f"""
    <div style="max-width:380px;margin:4rem auto;">
      <div class="card">
        <div class="card-header"><h2>🏫 Faculty Login</h2></div>
        <div class="card-body">
          {'<div class="alert" style="background:#fee2e2;color:#991b1b;border:1px solid #fca5a5;">' + error + '</div>' if error else ''}
          <form method="POST">
            <div class="form-group">
              <label>Faculty Password</label>
              <input type="password" name="password" autofocus placeholder="Enter password">
            </div>
            <button type="submit" class="btn btn-primary" style="width:100%;">Login →</button>
          </form>
          <p style="text-align:center;margin-top:12px;font-size:.8rem;color:#94a3b8;">
            Default: <code>faculty2025</code>
          </p>
        </div>
      </div>
    </div>"""
    return base_page(content, faculty=True)


# ─────────────────────────────────────────────────────────────────────────────
# Faculty — Dashboard
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/faculty/dashboard")
def faculty_dashboard():
    if not session.get("faculty"):
        return redirect(url_for("faculty_login"))

    data       = load_data()
    students   = data.get("students", {})
    capstones  = data.get("capstones", DEFAULT_CAPSTONES)
    submitted  = [s for s in students.values() if s.get("submitted")]
    pending    = [s for s in students.values() if not s.get("submitted")]

    # ── Overview stats ─────────────────────────────────────────────────────
    total_courses = sum(len(s.get("courses", [])) for s in submitted)
    avg_courses   = round(total_courses / len(submitted), 1) if submitted else 0

    stat_html = f"""
    <div class="stat-grid" style="margin-bottom:1.5rem;">
      <div class="stat-card"><div class="num">{len(students)}</div><div class="lbl">Total Students</div></div>
      <div class="stat-card"><div class="num">{len(submitted)}</div><div class="lbl">Submitted</div></div>
      <div class="stat-card"><div class="num">{len(pending)}</div><div class="lbl">In Progress</div></div>
      <div class="stat-card"><div class="num">{avg_courses}</div><div class="lbl">Avg Courses / Student</div></div>
      <div class="stat-card"><div class="num">{len(capstones)}</div><div class="lbl">Capstone Projects</div></div>
    </div>"""

    # ── Student table ──────────────────────────────────────────────────────
    student_rows = ""
    for s in sorted(students.values(), key=lambda x: x.get("name", "")):
        status_badge = (
            '<span style="background:#d1fae5;color:#065f46;padding:2px 8px;border-radius:99px;font-size:.75rem;font-weight:600;">✓ Submitted</span>'
            if s.get("submitted") else
            '<span style="background:#fef3c7;color:#92400e;padding:2px 8px;border-radius:99px;font-size:.75rem;font-weight:600;">⏳ Pending</span>'
        )
        strengths_str = ", ".join(s.get("strengths", [])[:3])
        if len(s.get("strengths", [])) > 3:
            strengths_str += f" +{len(s['strengths'])-3}"
        n_interested = sum(1 for p in s.get("project_preferences", []) if p.get("interest", 0) >= 3)
        student_rows += f"""
        <tr>
          <td><strong>{s.get('name','—')}</strong><br><span style="font-size:.78rem;color:#94a3b8;">{s.get('student_id','')}</span></td>
          <td>{s.get('year','—')} · {s.get('major','—')}</td>
          <td>{len(s.get('courses', []))}</td>
          <td style="font-size:.8rem;">{strengths_str or '—'}</td>
          <td>{n_interested}</td>
          <td>{status_badge}</td>
        </tr>"""

    if not student_rows:
        student_rows = '<tr><td colspan="6" style="text-align:center;color:#94a3b8;padding:24px;">No students yet.</td></tr>'

    # ── Capstone manager ───────────────────────────────────────────────────
    cap_rows = ""
    for cap in capstones:
        tags_html = " ".join(tag_pill_html(t) for t in cap["tags"])
        diff_bg, diff_fg = DIFF_COLORS.get(cap.get("difficulty", ""), ("#f1f5f9", "#334155"))
        # Count interest
        interested = sum(1 for s in submitted
                         for p in s.get("project_preferences", [])
                         if p["project_id"] == cap["id"] and p.get("interest", 0) >= 3)
        cap_rows += f"""
        <tr>
          <td><strong>{cap['name']}</strong></td>
          <td>{tags_html}</td>
          <td><span style="background:{diff_bg};color:{diff_fg};padding:2px 8px;border-radius:99px;font-size:.75rem;font-weight:600;">{cap.get('difficulty','')}</span></td>
          <td style="text-align:center;">{cap.get('team_size',4)}</td>
          <td style="text-align:center;font-weight:700;color:#2563eb;">{interested}</td>
          <td><a href="/faculty/delete-capstone/{cap['id']}" class="btn btn-ghost" style="padding:4px 10px;font-size:.78rem;" onclick="return confirm('Delete this capstone?')">✕</a></td>
        </tr>"""

    # ── Add capstone form ──────────────────────────────────────────────────
    diff_opts = "".join(f"<option>{d}</option>" for d in ["Intermediate", "Advanced", "Expert"])
    tag_ref   = " ".join(tag_pill_html(t) for t in TAG_COLORS)

    content = f"""
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1.5rem;">
      <h1 style="font-size:1.4rem;font-weight:800;color:#1a2e4a;">🏫 Faculty Dashboard</h1>
      <div style="display:flex;gap:10px;">
        <a href="/faculty/teams" class="btn btn-purple">👥 Generate Teams</a>
        <a href="/faculty/logout" class="btn btn-ghost">Logout</a>
      </div>
    </div>

    {stat_html}

    <div class="tab-bar">
      <div class="tab active" data-tab="main" data-target="tab-students">📋 Students</div>
      <div class="tab" data-tab="main" data-target="tab-capstones">🗂️ Capstone Projects</div>
    </div>

    <div id="tab-students" class="tab-content active">
      <div class="card">
        <div class="card-header"><h2>Student Submissions</h2></div>
        <div class="card-body" style="padding:0;">
          <div style="overflow-x:auto;">
            <table>
              <thead><tr>
                <th>Student</th><th>Year · Major</th><th>Courses</th>
                <th>Strengths</th><th>Interested In</th><th>Status</th>
              </tr></thead>
              <tbody>{student_rows}</tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <div id="tab-capstones" class="tab-content">
      <div class="card">
        <div class="card-header"><h2>Current Capstone Projects</h2></div>
        <div class="card-body" style="padding:0;">
          <div style="overflow-x:auto;">
            <table>
              <thead><tr>
                <th>Project Name</th><th>Tags</th><th>Difficulty</th>
                <th style="text-align:center;">Team Size</th>
                <th style="text-align:center;">Interested</th><th></th>
              </tr></thead>
              <tbody>{cap_rows}</tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header"><h2>➕ Add New Capstone Project</h2></div>
        <div class="card-body">
          <div style="font-size:.8rem;color:#64748b;margin-bottom:10px;">
            Available tags: {tag_ref}
          </div>
          <form method="POST" action="/faculty/add-capstone">
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;">
              <div class="form-group" style="grid-column:1/-1;">
                <label>Project Name</label>
                <input type="text" name="name" required placeholder="e.g. Smart Grid Energy Monitor">
              </div>
              <div class="form-group" style="grid-column:1/-1;">
                <label>Description</label>
                <textarea name="description" placeholder="Brief description of the project scope and deliverables..."></textarea>
              </div>
              <div class="form-group">
                <label>Tags <span class="hint">(comma separated, e.g. programming, electrical)</span></label>
                <input type="text" name="tags" placeholder="programming, electrical, embedded">
              </div>
              <div class="form-group">
                <label>Required Skills <span class="hint">(comma separated)</span></label>
                <input type="text" name="required_skills" placeholder="programming, embedded">
              </div>
              <div class="form-group">
                <label>Team Size</label>
                <input type="number" name="team_size" value="4" min="2" max="8">
              </div>
              <div class="form-group">
                <label>Difficulty</label>
                <select name="difficulty">{diff_opts}</select>
              </div>
            </div>
            <button type="submit" class="btn btn-success">➕ Add Capstone</button>
          </form>
        </div>
      </div>
    </div>
    """
    return base_page(content, faculty=True)


@app.route("/faculty/add-capstone", methods=["POST"])
def faculty_add_capstone():
    if not session.get("faculty"):
        return redirect(url_for("faculty_login"))
    data = load_data()
    tags = [t.strip() for t in request.form.get("tags", "").split(",") if t.strip()]
    req  = [t.strip() for t in request.form.get("required_skills", "").split(",") if t.strip()]
    data.setdefault("capstones", list(DEFAULT_CAPSTONES)).append({
        "id":             f"cap_{uuid.uuid4().hex[:6]}",
        "name":           request.form.get("name", "").strip(),
        "description":    request.form.get("description", "").strip(),
        "tags":           tags,
        "required_skills": req,
        "team_size":      int(request.form.get("team_size", 4)),
        "difficulty":     request.form.get("difficulty", "Intermediate"),
    })
    save_data(data)
    return redirect(url_for("faculty_dashboard") + "#tab-capstones")


@app.route("/faculty/delete-capstone/<cap_id>")
def faculty_delete_capstone(cap_id):
    if not session.get("faculty"):
        return redirect(url_for("faculty_login"))
    data = load_data()
    data["capstones"] = [c for c in data.get("capstones", DEFAULT_CAPSTONES) if c["id"] != cap_id]
    save_data(data)
    return redirect(url_for("faculty_dashboard"))


@app.route("/faculty/logout")
def faculty_logout():
    session.pop("faculty", None)
    return redirect(url_for("faculty_login"))


# ─────────────────────────────────────────────────────────────────────────────
# Faculty — Team Formation
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/faculty/teams")
def faculty_teams():
    if not session.get("faculty"):
        return redirect(url_for("faculty_login"))

    data    = load_data()
    results = run_team_formation(data)

    if not results:
        content = """
        <div class="alert alert-warning">
          ⚠️ No submitted student profiles yet. Students must complete and submit their profiles before teams can be formed.
        </div>
        <a href="/faculty/dashboard" class="btn btn-ghost">← Back to Dashboard</a>
        """
        return base_page(content, faculty=True)

    # Store results
    data["teams"] = {cid: {"capstone": r["capstone"],
                            "teams": [{"number": t["number"],
                                       "member_ids": [m["id"] for m in t["members"]]}
                                      for t in r["teams"]]}
                     for cid, r in results.items()}
    save_data(data)

    total_assigned = sum(
        sum(len(t["members"]) for t in r["teams"])
        for r in results.values()
    )
    total_students = sum(1 for s in data["students"].values() if s.get("submitted"))

    project_cards = ""
    for cid, proj in results.items():
        cap       = proj["capstone"]
        tags_html = " ".join(tag_pill_html(t) for t in cap["tags"])
        diff_bg, diff_fg = DIFF_COLORS.get(cap.get("difficulty", ""), ("#f1f5f9", "#334155"))

        team_html = ""
        for team in proj["teams"]:
            members_html = ""
            for m in team["members"]:
                # Strength chips
                str_chips = "".join(
                    f'<span style="font-size:.68rem;background:#f1f5f9;color:#475569;padding:1px 6px;border-radius:99px;">{s}</span> '
                    for s in m.get("strengths", [])[:3]
                )
                members_html += f"""
                <div class="member-chip">
                  <span style="font-weight:600;">{m.get('name','?')}</span>
                  <span style="font-size:.72rem;color:#94a3b8;">{m.get('year','')}</span>
                  <div>{str_chips}</div>
                </div>"""

            team_html += f"""
            <div class="team-card">
              <div class="team-header">Team {team['number']} · {len(team['members'])} member{'s' if len(team['members'])!=1 else ''}</div>
              <div>{members_html}</div>
            </div>"""

        n_teams = len(proj["teams"])
        project_cards += f"""
        <div class="card">
          <div class="card-header" style="background:#f8fafc;">
            <div>
              <h2>📁 {cap['name']}</h2>
              <div style="margin-top:4px;display:flex;gap:6px;flex-wrap:wrap;">
                {tags_html}
                <span style="background:{diff_bg};color:{diff_fg};padding:2px 8px;border-radius:99px;font-size:.72rem;font-weight:700;">{cap.get('difficulty','')}</span>
              </div>
            </div>
            <span class="badge" style="background:#eff6ff;color:#1d4ed8;font-size:.85rem;">
              {n_teams} Team{'s' if n_teams != 1 else ''}
            </span>
          </div>
          <div class="card-body">{team_html}</div>
        </div>"""

    content = f"""
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1.5rem;">
      <h1 style="font-size:1.4rem;font-weight:800;color:#1a2e4a;">👥 Team Assignments</h1>
      <div style="display:flex;gap:10px;">
        <a href="/api/export" class="btn btn-ghost" target="_blank">📥 Export JSON</a>
        <a href="/faculty/dashboard" class="btn btn-ghost">← Dashboard</a>
      </div>
    </div>

    <div class="alert alert-success" style="margin-bottom:1.5rem;">
      ✅ Teams generated for <strong>{len(results)}</strong> project(s) covering
      <strong>{total_assigned}</strong> of <strong>{total_students}</strong> submitted students.
      Teams are balanced for skill diversity. Faculty should review and adjust as needed.
    </div>

    <div class="card" style="padding:0;overflow:hidden;margin-bottom:1.5rem;">
      <div class="card-body" style="background:#f8fafc;padding:14px 20px;">
        <strong style="font-size:.875rem;">Algorithm:</strong>
        <span style="font-size:.85rem;color:#64748b;">
          Students are ranked by preference certainty and greedily assigned to their highest-scored available project.
          Within each project, sub-teams are formed by rotating across strength profiles to maximize skill diversity.
          Scoring: 40% course coverage × enjoyment · 40% stated interest · 20% skill alignment.
        </span>
      </div>
    </div>

    {project_cards}
    """
    return base_page(content, faculty=True)


# ─────────────────────────────────────────────────────────────────────────────
# API — Export
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/export")
def api_export():
    if not session.get("faculty"):
        return jsonify({"error": "Unauthorized"}), 401
    data = load_data()
    # Sanitize: remove session IDs from export
    export = {
        "students": [
            {k: v for k, v in s.items() if k != "id"}
            for s in data["students"].values()
            if s.get("submitted")
        ],
        "capstones": data.get("capstones", DEFAULT_CAPSTONES),
        "teams": data.get("teams", {}),
    }
    from flask import Response
    return Response(
        json.dumps(export, indent=2),
        mimetype="application/json",
        headers={"Content-Disposition": "attachment;filename=capstone_export.json"},
    )


# ─────────────────────────────────────────────────────────────────────────────
# Init & run
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Initialize data file with default capstones if it doesn't exist
    if not os.path.exists(DATA_FILE):
        save_data({"students": {}, "capstones": DEFAULT_CAPSTONES, "teams": {}})
    print("\n🎓 Engineering Capstone Advisor")
    print("   Open: http://localhost:5000")
    print("   Faculty password: faculty2025\n")
    app.run(debug=True, port=5000)
    