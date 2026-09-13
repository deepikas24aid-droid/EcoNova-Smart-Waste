import streamlit as st
import requests, math
from datetime import datetime
import pandas as pd
import folium
from streamlit_folium import st_folium

try:
    from PIL import Image
except Exception:
    Image = None

try:
    from transformers import pipeline
except Exception:
    pipeline = None

st.set_page_config(page_title="EcoNova | Smart Waste", page_icon="♻️", layout="wide")

# -------------------- ATTRACTIVE UI --------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:Inter,sans-serif}
.stApp{background:radial-gradient(circle at 10% 0%,rgba(34,197,94,.12),transparent 28%),radial-gradient(circle at 95% 5%,rgba(14,165,233,.10),transparent 25%),#07110d;color:#edf8f0}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#07130e,#0d2117);border-right:1px solid rgba(255,255,255,.08)}
[data-testid="stSidebar"] *{color:#eaf6ee!important}
.block-container{max-width:1450px;padding-top:2.5rem;padding-bottom:2rem}
.hero{padding:32px;border-radius:26px;background:linear-gradient(135deg,#123522,#091c14);border:1px solid rgba(94,229,140,.20);box-shadow:0 18px 60px #0005;margin-bottom:24px}
.hero .eyebrow{color:#60e58e;font-size:11px;font-weight:800;letter-spacing:2px}
.hero h1{font-size:43px;font-weight:800;letter-spacing:-1.8px;margin:7px 0}
.hero p{color:#a9c5b3;font-size:15px;margin:0;max-width:900px}
.card{padding:20px;border-radius:20px;background:linear-gradient(145deg,#142b20,#0b1d15);border:1px solid #ffffff10;min-height:135px;box-shadow:0 10px 35px #0003}
.card small{color:#8da99a}.card b{display:block;font-size:30px;margin-top:7px}.card span{color:#759284;font-size:11px}
.feature{padding:22px;border-radius:20px;background:#0d2419;border:1px solid #ffffff0d;min-height:175px}
.feature .icon{font-size:28px}.feature h3{font-size:17px}.feature p{color:#8da698;font-size:13px;line-height:1.55}
.section{margin:27px 0 13px}.section h2{font-size:22px;margin:0}.section p{color:#829d8d;margin:4px 0}
.progress{height:8px;background:#162a21;border-radius:99px;overflow:hidden}.progress div{height:100%;background:linear-gradient(90deg,#35d878,#73e7a0);border-radius:99px}
.pill{display:inline-block;padding:6px 11px;border-radius:99px;font-size:11px;font-weight:700}
.green{background:#22c55e18;color:#6ee79a}.yellow{background:#f59e0b18;color:#f8c66a}.red{background:#ef444418;color:#ff8d8d}
.notice{padding:14px 16px;border-radius:14px;background:#38bdf80d;border:1px solid #38bdf822;color:#b7dff0;font-size:13px}
div[data-testid="stButton"]>button{border-radius:12px;background:#10271a;border:1px solid #ffffff12;color:#edf8f0;font-weight:650}
.footer{text-align:center;color:#5f7d6d;border-top:1px solid #ffffff0d;padding-top:18px;margin-top:45px;font-size:11px}
</style>
""", unsafe_allow_html=True)

# -------------------- FIREBASE --------------------
FIREBASE_URL = "https://econova-8e761-default-rtdb.asia-southeast1.firebasedatabase.app"

DEMO_BINS = [
    {"id":"BIN001","area":"Gandhi Road","fill":25,"lat":11.0168,"lon":76.9558,"sensor":"Online","collection":"Scheduled","assigned_vehicle":"Not assigned","assigned_person":"Not assigned"},
    {"id":"BIN002","area":"Bus Stand","fill":55,"lat":11.0183,"lon":76.9725,"sensor":"Online","collection":"Scheduled","assigned_vehicle":"Not assigned","assigned_person":"Not assigned"},
    {"id":"BIN003","area":"Market Area","fill":82,"lat":11.0046,"lon":76.9616,"sensor":"Online","collection":"Ready","assigned_vehicle":"EV-02","assigned_person":"Ravi Kumar"},
    {"id":"BIN004","area":"Railway Station Road","fill":95,"lat":11.0270,"lon":76.9563,"sensor":"Online","collection":"Urgent","assigned_vehicle":"EV-01","assigned_person":"Arun Team"},
]

DEMO_REPORTS = [
    {"id":"REP001","type":"Overflowing bin","location":"Market Area","description":"Bin is nearly full.","status":"Resolved","progress":100,"reported":"Today, 10:20","assigned_team":"Sanitation Team A","assigned_person":"Ravi Kumar"},
    {"id":"REP002","type":"Uncollected waste","location":"Railway Station Road","description":"Collection is pending.","status":"Work in Progress","progress":65,"reported":"Today, 11:05","assigned_team":"Sanitation Team B","assigned_person":"Arun Team"},
]

DEFAULT_DATA = {
    "bins": DEMO_BINS,
    "reports": DEMO_REPORTS,
    "analytics": [
        {"date":datetime.now().strftime("%Y-%m-%d"),"category":"Wet Waste","confidence":92,"area":"Gandhi Road"},
        {"date":datetime.now().strftime("%Y-%m-%d"),"category":"Dry Waste","confidence":89,"area":"Bus Stand"},
        {"date":datetime.now().strftime("%Y-%m-%d"),"category":"E-Waste","confidence":94,"area":"Market Area"},
        {"date":datetime.now().strftime("%Y-%m-%d"),"category":"Sanitary Waste","confidence":87,"area":"Railway Station Road"}
    ],
    "assignments": []
}

def firebase_get():
    try:
        r = requests.get(FIREBASE_URL + "/econova.json", timeout=8)
        if r.ok and isinstance(r.json(), dict):
            return r.json()
    except Exception:
        pass
    return None

def firebase_save(data):
    try:
        r = requests.put(FIREBASE_URL + "/econova.json", json=data, timeout=8)
        return r.ok
    except Exception:
        return False

if "firebase_loaded" not in st.session_state:
    remote = firebase_get()
    if remote:
        st.session_state.data = remote
        st.session_state.firebase_ok = True
    else:
        st.session_state.data = {k:list(v) for k,v in DEFAULT_DATA.items()}
        st.session_state.firebase_ok = False
    st.session_state.firebase_loaded = True

data = st.session_state.data
data.setdefault("bins", [])
data.setdefault("reports", [])
data.setdefault("analytics", [])
data.setdefault("assignments", [])
if not data["bins"]:
    data["bins"] = [dict(x) for x in DEMO_BINS]
if not data["reports"]:
    data["reports"] = [dict(x) for x in DEMO_REPORTS]
if not data["analytics"]:
    data["analytics"] = [
        {"date":datetime.now().strftime("%Y-%m-%d"),"category":"Wet Waste","confidence":92,"area":"Gandhi Road"},
        {"date":datetime.now().strftime("%Y-%m-%d"),"category":"Dry Waste","confidence":89,"area":"Bus Stand"},
        {"date":datetime.now().strftime("%Y-%m-%d"),"category":"E-Waste","confidence":94,"area":"Market Area"},
        {"date":datetime.now().strftime("%Y-%m-%d"),"category":"Sanitary Waste","confidence":87,"area":"Railway Station Road"}
    ]

def save():
    st.session_state.firebase_ok = firebase_save(data)

# -------------------- AI WASTE IDENTIFICATION --------------------
@st.cache_resource(show_spinner=False)
def ai_model():
    if pipeline is None:
        return None
    try:
        return pipeline(
            "zero-shot-image-classification",
            model="openai/clip-vit-base-patch32"
        )
    except Exception:
        return None

AI_LABELS = [
    "wet organic waste: food scraps, fruit peel, vegetable waste",
    "dry waste: paper, cardboard, plastic packaging and other dry household waste",
    "electronic waste: mobile phone, charger, cable, battery or circuit board",
    "sanitary waste: sanitary pad, diaper, tissue, mask or other sanitary product"
]

def classify_waste(img):
    model = ai_model()
    if model is None:
        return None
    try:
        result = model(img, candidate_labels=AI_LABELS)
        top = result[0]
        label = top["label"].lower()
        score = float(top["score"]) * 100

        if "wet" in label or "food" in label or "organic" in label or "fruit" in label or "vegetable" in label:
            category = "Wet Waste"
        elif "electronic" in label or "phone" in label or "charger" in label or "circuit" in label or "battery" in label:
            category = "E-Waste"
        elif "sanitary" in label or "diaper" in label or "pad" in label or "mask" in label or "tissue" in label:
            category = "Sanitary Waste"
        else:
            category = "Dry Waste"

        return top["label"], category, score
    except Exception:
        return None

# -------------------- HELPERS --------------------
def bin_status(fill):
    if fill >= 90: return "Critical", "red"
    if fill >= 75: return "Ready", "yellow"
    return "Normal", "green"

def route_api(points):
    if len(points) < 2:
        return None
    coords = ";".join(f"{lon},{lat}" for lat,lon in points)
    try:
        r = requests.get(
            f"https://router.project-osrm.org/route/v1/driving/{coords}",
            params={"overview":"full","geometries":"geojson"},
            timeout=10
        )
        if r.ok and r.json().get("routes"):
            q = r.json()["routes"][0]
            return q["geometry"], q["distance"]/1000, q["duration"]/60
    except Exception:
        pass
    return None

# -------------------- SIDEBAR / ACCESS --------------------
with st.sidebar:
    st.markdown('<div style="font-size:28px;font-weight:800">♻️ EcoNova</div><div style="color:#78a18b;font-size:11px;letter-spacing:1px">SMART WASTE • CLEANER CITIES</div>', unsafe_allow_html=True)
    role = st.radio("Portal", ["Citizen", "Admin"], index=0)
    if role == "Admin":
        pages = ["Command Center","Waste Segregation","Location Intelligence","Smart Bins","Alerts","Issue Management","Smart Route Planning","Collection Assignments","Analytics"]
    else:
        pages = ["Overview","Waste Segregation","Smart Bins","Location Intelligence","Report Issue","My Reports","Analytics"]
    st.divider()
    if "page" not in st.session_state or st.session_state.page not in pages:
        st.session_state.page = pages[0]
    for pg in pages:
        if st.button(pg, use_container_width=True, key="nav_"+pg):
            st.session_state.page = pg
    st.divider()
    if st.session_state.firebase_ok:
        st.success("Firebase connected")
    else:
        st.warning("Firebase unavailable — demo session data")
    st.caption("EcoNova Prototype • Software-first • Hardware-ready")

page = st.session_state.page

# One global demo notice only
st.markdown('<div class="notice">⚠️ DEMO / PROTOTYPE DATA — Hardware sensors are not connected. Bin readings shown are sample values; the same dashboard can receive live sensor data when ESP32/sensors are connected.</div>', unsafe_allow_html=True)

if role == "Admin":
    h="EcoNova Command Center"
    sub="Monitor bins, sanitation reports, collection assignments, analytics and smart routes from one control layer."
else:
    h="A cleaner city starts with one smart action."
    sub="Identify waste, find smart bins, report sanitation issues and track your reports from one simple platform."

st.markdown(f'<div class="hero"><div class="eyebrow">SMART WASTE & SANITATION PLATFORM</div><h1>{h}</h1><p>{sub}</p></div>', unsafe_allow_html=True)

# -------------------- OVERVIEW --------------------
if page in ["Overview","Command Center"]:
    bins = data["bins"]; reports = data["reports"]
    total=len(bins)
    ready=sum(int(b.get("fill",0))>=75 for b in bins)
    critical=sum(int(b.get("fill",0))>=90 for b in bins)
    openr=sum(int(r.get("progress",0))<100 for r in reports)
    avg=sum(int(b.get("fill",0)) for b in bins)/total if total else 0
    vals=[("Smart Bins",total,"Registered monitoring points"),("Average Fill",f"{avg:.0f}%","Network snapshot"),("Ready",ready,"Collection attention"),("Critical",critical,"Urgent collection"),("Open Issues",openr,"Being handled")]
    for col,(a,b,c) in zip(st.columns(5),vals):
        with col: st.markdown(f'<div class="card"><small>{a}</small><b>{b}</b><span>{c}</span></div>',unsafe_allow_html=True)

    st.markdown('<div class="section"><h2>Everything connected, nothing complicated.</h2><p>Core operations working together.</p></div>',unsafe_allow_html=True)
    fs=[("📡","Smart Bin Monitoring","Fill-level and sensor status visibility."),("🔔","Automatic Alerts","Critical and ready bins are surfaced for collection."),("🚨","Sanitation Reports","Citizens report overflowing or unclean areas."),("🧭","Smart Collection Routes","Priority stops are sequenced on road routes and assigned."),("♻️","Four-Way Waste Identification","AI-assisted identification for wet, dry, e-waste and sanitary waste.")]
    for col,(i,a,b) in zip(st.columns(5),fs):
        with col: st.markdown(f'<div class="feature"><div class="icon">{i}</div><h3>{a}</h3><p>{b}</p></div>',unsafe_allow_html=True)

    st.markdown('<div class="section"><h2>Operations snapshot</h2></div>',unsafe_allow_html=True)
    for b in bins:
        s,css=bin_status(int(b.get("fill",0)))
        c1,c2,c3=st.columns([2,5,2])
        with c1: st.markdown(f"**{b['id']}**"); st.caption(b.get("area",""))
        with c2:
            fill=int(b.get("fill",0))
            st.markdown(f'<div style="display:flex;justify-content:space-between"><span>Fill level</span><b>{fill}%</b></div><div class="progress"><div style="width:{fill}%"></div></div>',unsafe_allow_html=True)
        with c3: st.markdown(f'<span class="pill {css}">{s}</span>',unsafe_allow_html=True)

# -------------------- WASTE SEGREGATION --------------------
elif page=="Waste Segregation":
    st.markdown('<div class="section"><h2>♻️ AI Waste Identification — Four-Way Segregation</h2><p>Use the browser camera directly or upload one clear waste-item photo. Camera permission is the only browser permission needed.</p></div>',unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        cam = st.camera_input("📷 Turn on camera")
    with c2:
        up = st.file_uploader("Upload photo", type=["jpg","jpeg","png"])

    f = cam or up
    if f and Image:
        img = Image.open(f).convert("RGB")
        st.image(img, width=430)
        if st.button("🔎 Analyze Waste", type="primary", use_container_width=True):
            with st.spinner("AI is analyzing the waste..."):
                result = classify_waste(img)
            if result:
                item,cat,conf=result
                a,b,c=st.columns(3)
                a.metric("Detected", item.title())
                b.metric("Segregation", cat)
                c.metric("Confidence", f"{conf:.1f}%")
                if conf < 55:
                    st.warning("Low confidence. Please show one waste item clearly and scan again.")
                elif conf < 75:
                    st.info("Moderate confidence. Confirm the item before disposal.")
                else:
                    st.success("AI identification completed. Follow local municipal disposal rules.")
                data["analytics"].append({"date":datetime.now().strftime("%Y-%m-%d"),"category":cat,"confidence":conf,"area":"Unspecified"})
                save()
            else:
                st.error("AI model is not available on the server. Please make sure the deployment installs transformers, torch and safetensors and can download the CLIP model. The camera does not require a file download; it opens directly in the browser after Camera permission is allowed.")
    st.markdown('<div class="section"><h2>Four-way disposal guide</h2></div>',unsafe_allow_html=True)
    st.dataframe(pd.DataFrame([
        ["Wet Waste","Food scraps, vegetable/fruit waste","Organic / composting"],
        ["Dry Waste","Paper, cardboard, clean dry packaging","Dry/recyclable stream"],
        ["E-Waste","Phones, chargers, electronics, circuit boards","Authorized e-waste collection"],
        ["Sanitary Waste","Diapers, sanitary pads, masks and similar waste","Separate sanitary disposal"],
    ],columns=["Category","Examples","Recommended handling"]),use_container_width=True,hide_index=True)
    st.caption("For mixed waste, separate items first. A single photo cannot reliably identify every item in a mixed bag.")

# -------------------- SMART BINS --------------------
elif page=="Smart Bins":
    st.markdown('<div class="section"><h2>🗑️ Smart Bin Monitoring</h2><p>Admin can manage registered bins; citizens can view public bin status.</p></div>',unsafe_allow_html=True)
    q=st.text_input("Search Bin ID or Area",placeholder="BIN003 / Market Area").lower()
    found=[b for b in data["bins"] if not q or q in b["id"].lower() or q in b.get("area","").lower()]
    for b in found:
        fill=int(b.get("fill",0));s,css=bin_status(fill)
        c1,c2,c3=st.columns([2,5,2])
        with c1: st.markdown(f"### {b['id']}"); st.caption("📍 "+b.get("area","")); st.markdown(f'<span class="pill {css}">{s}</span>',unsafe_allow_html=True)
        with c2: st.markdown(f'<div style="display:flex;justify-content:space-between"><span>Fill level</span><b>{fill}%</b></div><div class="progress"><div style="width:{fill}%"></div></div>',unsafe_allow_html=True); st.caption(f"Sensor: {b.get('sensor','Unknown')}")
        with c3: st.metric("Collection",b.get("collection","Pending"))
        st.divider()

    if role=="Admin":
        st.markdown('<div class="section"><h2>Admin Bin Management</h2></div>',unsafe_allow_html=True)
        with st.expander("➕ Register New Bin"):
            bid=st.text_input("Bin ID")
            area=st.text_input("Area / Street")
            fill=st.number_input("Initial fill %",0,100,0)
            lat=st.number_input("Latitude",format="%.6f")
            lon=st.number_input("Longitude",format="%.6f")
            if st.button("Register Bin",type="primary"):
                if bid and area:
                    data["bins"].append({"id":bid.upper(),"area":area,"fill":fill,"lat":lat,"lon":lon,"sensor":"Online","collection":"Scheduled","assigned_vehicle":"Not assigned","assigned_person":"Not assigned"})
                    save(); st.success("Bin registered and saved to Firebase."); st.rerun()

# -------------------- LOCATION --------------------
elif page=="Location Intelligence":
    st.markdown('<div class="section"><h2>📍 Location Intelligence</h2><p>Search a registered bin or area and inspect its operational location on the map.</p></div>',unsafe_allow_html=True)
    q=st.text_input("Search location or Bin ID",placeholder="Gandhi Road / BIN001").lower()
    found=[b for b in data["bins"] if not q or q in b["id"].lower() or q in b.get("area","").lower()]
    if found:
        b=found[0]
        a,c,d,e=st.columns(4);a.metric("Bin ID",b["id"]);c.metric("Area",b.get("area",""));d.metric("Fill",f"{b.get('fill',0)}%");e.metric("Sensor",b.get("sensor",""))
        m=folium.Map([b["lat"],b["lon"]],zoom_start=15)
        for x in data["bins"]:
            folium.Marker([x["lat"],x["lon"]],tooltip=f"{x['id']} • {x.get('area','')}",popup=f"Fill: {x.get('fill',0)}%").add_to(m)
        st_folium(m,width=None,height=450,returned_objects=[])
    else:
        st.info("No registered smart bin found.")

# -------------------- CITIZEN REPORT --------------------
elif page=="Report Issue":
    st.markdown('<div class="section"><h2>🚨 Report a Sanitation Issue</h2><p>Report overflowing bins, uncollected waste and sanitation problems.</p></div>',unsafe_allow_html=True)
    typ=st.selectbox("Issue type",["Overflowing bin","Uncollected waste","Unclean area","Sanitation issue","Damaged bin","Other"])
    loc_mode=st.radio("Issue location",["Current location","Different location"],horizontal=True)
    if loc_mode=="Current location":
       loc=""
    st.caption("📍 Allow location access to detect your current area automatically.")

    try:
        from streamlit_geolocation import streamlit_geolocation
        g=streamlit_geolocation()

        if g and g.get("latitude") is not None and g.get("longitude") is not None:

            lat = g["latitude"]
            lon = g["longitude"]

            try:
                response = requests.get(
                    "https://nominatim.openstreetmap.org/reverse",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "format": "json"
                    },
                    headers={"User-Agent": "EcoNova"}
                )

                address = response.json().get("address", {})

                area = (
                    address.get("suburb")
                    or address.get("neighbourhood")
                    or address.get("road")
                    or "Not available"
                )

                city = (
                    address.get("city")
                    or address.get("town")
                    or address.get("village")
                    or "Not available"
                )

                state = address.get("state", "Not available")
                country = address.get("country", "Not available")

                loc = f"{area}, {city}, {state}, {country}"

                st.success("📍 Current location detected")
                st.write(f"**Area:** {area}")
                st.write(f"**City:** {city}")
                st.write(f"**State:** {state}")
                st.write(f"**Country:** {country}")

            except Exception:
                loc = f"{lat:.5f}, {lon:.5f}"
                st.warning("Location detected, but place name could not be retrieved.")

        else:
            st.info("Waiting for location permission…")

    except Exception as e:
        st.error(f"Location component error: {e}")
    else:
        loc=st.text_input("Area / Street / Landmark",placeholder="Example: Gandhi Road near bus stop")
    desc=st.text_area("What happened?",placeholder="Briefly describe the issue...")
    if st.button("Submit Report",type="primary",use_container_width=True):
        rid=f"REP{len(data['reports'])+1:03d}"
        data["reports"].insert(0,{"id":rid,"type":typ,"location":loc or "Not provided","description":desc or "No description","status":"Reported","progress":0,"reported":datetime.now().strftime("%d %b, %H:%M"),"assigned_team":"Not assigned","assigned_person":"Not assigned"})
        ok=save()
        st.success(f"{rid} submitted successfully." + (" Saved to Firebase." if ok else ""))

# -------------------- MY REPORTS --------------------
elif page=="My Reports":
    st.markdown('<div class="section"><h2>📋 My Reports</h2><p>Track sanitation reports from reporting to closure.</p></div>',unsafe_allow_html=True)
    for r in data["reports"]:
        p=min(100,int(r.get("progress",0)))
        s="Resolved" if p>=100 else r.get("status","Reported")
        st.markdown(f"**{r['id']} — {r.get('type','')}** · {r.get('location','')}")
        st.caption(f"Assigned: {r.get('assigned_team','Not assigned')} / {r.get('assigned_person','Not assigned')}")
        st.progress(p/100,text=f"{s} • {p}%")
        st.divider()

# -------------------- ALERTS --------------------
elif page=="Alerts":
    st.markdown('<div class="section"><h2>🔔 Automatic Alerts</h2><p>Alerts are generated from bin fill thresholds.</p></div>',unsafe_allow_html=True)
    critical=[b for b in data["bins"] if int(b.get("fill",0))>=90]
    ready=[b for b in data["bins"] if 75<=int(b.get("fill",0))<90]
    if critical:
        st.error(f"{len(critical)} critical bin(s) need urgent collection.")
        for b in critical: st.write(f"**{b['id']} — {b.get('area','')}** • {b.get('fill',0)}%")
    else: st.success("No critical bins right now.")
    if ready: st.warning("Approaching capacity: "+", ".join(b["id"] for b in ready))

# -------------------- ISSUE MANAGEMENT --------------------
elif page=="Issue Management":
    st.markdown('<div class="section"><h2>🛠️ Issue Management</h2><p>Assign sanitation reports to responsible teams and track a clear operational workflow.</p></div>',unsafe_allow_html=True)
    teams=["Sanitation Team A","Sanitation Team B","Municipal Response Team","Emergency Clean-up Team"]
    people=["Ravi Kumar","Arun Team","Priya Team","Karthik Officer"]
    statuses=["Reported","Verified","Assigned","Accepted","Work Started","Work in Progress","Inspection","Resolved","Closed"]

    for r in data["reports"]:
        with st.expander(f"{r['id']} • {r.get('type','')} • {r.get('location','')}"):
            st.write(r.get("description",""))
            a,b,c=st.columns(3)
            with a: team=st.selectbox("Responsible team",teams,index=teams.index(r.get("assigned_team")) if r.get("assigned_team") in teams else 0,key="team_"+r["id"])
            with b: person=st.selectbox("Responsible person",people,index=people.index(r.get("assigned_person")) if r.get("assigned_person") in people else 0,key="person_"+r["id"])
            with c: status_val=st.selectbox("Status",statuses,index=statuses.index(r.get("status")) if r.get("status") in statuses else 0,key="status_"+r["id"])
            progress=st.slider("Work progress",0,100,int(r.get("progress",0)),key="prog_"+r["id"])
            if st.button("Save Assignment & Progress",key="saveissue_"+r["id"],type="primary"):
                r["assigned_team"]=team;r["assigned_person"]=person;r["progress"]=progress;r["status"]="Resolved" if progress>=100 else status_val
                save();st.success("Issue assignment and progress saved to Firebase.");st.rerun()

# -------------------- SMART ROUTE --------------------
elif page=="Smart Route Planning":
    st.markdown('<div class="section"><h2>🧭 Smart Collection Route</h2><p>Prioritize bins by urgency, create a practical road route, then assign the collection run to a vehicle and personnel.</p></div>',unsafe_allow_html=True)
    priority=sorted([b for b in data["bins"] if int(b.get("fill",0))>=75],key=lambda x:int(x.get("fill",0)),reverse=True)
    vehicles=["EV-01","EV-02","Truck-03","Mini-Tipper-01"]
    people=["Ravi Kumar","Arun Team","Karthik Officer","Collection Team C"]
    if not priority:
        st.success("No priority bins.")
    else:
        depot=(11.0169,76.9558)
        pts=[depot]+[(b["lat"],b["lon"]) for b in priority]
        road=route_api(pts)
        a,b,c=st.columns(3);a.metric("Priority bins",len(priority));b.metric("Road distance",f"{road[1]:.1f} km" if road else "Unavailable");c.metric("Drive time",f"{road[2]:.0f} min" if road else "Unavailable")
        for i,x in enumerate(priority,1):
            st.write(f"**{i}. {x['id']} — {x.get('area','')}** • {x.get('fill',0)}% • Current assignment: {x.get('assigned_vehicle','Not assigned')} / {x.get('assigned_person','Not assigned')}")
        m=folium.Map(depot,zoom_start=14);folium.Marker(depot,tooltip="Collection Depot").add_to(m)
        for i,x in enumerate(priority,1):folium.Marker([x["lat"],x["lon"]],tooltip=f"Stop {i}: {x['id']}").add_to(m)
        if road:
            coords=road[0]["coordinates"];folium.PolyLine([(lat,lon) for lon,lat in coords],weight=6).add_to(m)
        else:
            folium.PolyLine(pts,weight=4,dash_array="8").add_to(m)
            st.warning("Road routing service unavailable; priority sequence is still shown.")
        st_folium(m,width=None,height=500,returned_objects=[])

        st.markdown('<div class="section"><h2>Assign collection run</h2></div>',unsafe_allow_html=True)
        v=st.selectbox("Collection vehicle",vehicles)
        p=st.selectbox("Collection personnel",people)
        reason="Priority based on fill level and urgency; critical bins are handled first."
        st.info(reason)
        if st.button("Assign Route & Save",type="primary",use_container_width=True):
            stamp=datetime.now().strftime("%Y-%m-%d %H:%M")
            for x in priority:
                x["assigned_vehicle"]=v;x["assigned_person"]=p;x["collection"]="Assigned"
            data["assignments"].append({"type":"Collection Route","vehicle":v,"person":p,"bins":[x["id"] for x in priority],"reason":reason,"created":stamp})
            save();st.success(f"Route assigned to {v} and {p}. Saved to Firebase.");st.rerun()

# -------------------- COLLECTION ASSIGNMENTS --------------------
elif page=="Collection Assignments":
    st.markdown('<div class="section"><h2>🚛 Collection Assignments</h2><p>See which vehicle and collection personnel are responsible for each bin/run.</p></div>',unsafe_allow_html=True)
    rows=[{"Bin":b["id"],"Area":b.get("area",""),"Fill %":b.get("fill",0),"Collection":b.get("collection",""),"Vehicle":b.get("assigned_vehicle","Not assigned"),"Personnel":b.get("assigned_person","Not assigned")} for b in data["bins"]]
    st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
    for a in reversed(data["assignments"]):
        st.info(f"{a.get('created','')} • {a.get('type','')} • Vehicle: {a.get('vehicle','')} • Personnel: {a.get('person','')} • Reason: {a.get('reason','')}")

# -------------------- ANALYTICS --------------------
elif page=="Analytics":
    st.markdown('<div class="section"><h2>📊 Waste Analytics</h2><p>Area-wise and time-based segregation analytics from recorded AI identifications.</p></div>',unsafe_allow_html=True)
    records=data["analytics"]
    if records:
        df=pd.DataFrame(records)
        df["date"]=pd.to_datetime(df["date"])
        period=st.selectbox("Period",["Daily","Weekly","Monthly"])
        if period=="Daily": df["period"]=df["date"].dt.strftime("%Y-%m-%d")
        elif period=="Weekly": df["period"]=df["date"].dt.to_period("W").astype(str)
        else: df["period"]=df["date"].dt.to_period("M").astype(str)
        pivot=df.groupby(["period","category"]).size().unstack(fill_value=0)
        st.bar_chart(pivot)
        st.dataframe(pivot,use_container_width=True)
    else:
        st.info("Analytics will appear after AI waste identifications are recorded.")
    st.caption("The prototype records AI identification events. Municipality-wide analytics become richer as more verified disposal records are collected.")

st.markdown('<div class="footer">EcoNova • Smart Waste & Sanitation • Software-first, hardware-ready • Firebase-backed prototype</div>',unsafe_allow_html=True)