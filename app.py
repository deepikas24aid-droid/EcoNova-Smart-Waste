import math
from datetime import datetime

import requests
import streamlit as st
import folium
from streamlit_folium import st_folium

try:
    from streamlit_geolocation import streamlit_geolocation
    GPS_AVAILABLE = True
except ImportError:
    GPS_AVAILABLE = False


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="EcoNova",
    page_icon="♻️",
    layout="wide"
)

FIREBASE_URL = (
    "https://econova-8e761-default-rtdb."
    "asia-southeast1.firebasedatabase.app"
)

TIMEOUT = 5


# ============================================================
# TRANSLATION
# ============================================================

TEXT = {
    "English": {
        "home": "Home",
        "seg": "Waste Segregation",
        "bins": "Smart Bins",
        "report": "Report Issue",
        "my": "My Reports",
        "dashboard": "Admin Dashboard",
        "issues": "Issue Reports",
        "route": "Smart Route Planning",
        "manage": "Manage Bins",
        "language": "Language",
        "portal": "Portal",
        "user": "User",
        "admin": "Admin",
        "welcome": "Welcome to EcoNova",
        "tagline": "Smart Waste Segregation, Disposal & Sanitation Platform",
        "description": "A digital platform for smart waste collection and improved sanitation.",
        "organic": "Organic / Wet Waste",
        "dry": "Dry Waste",
        "recycle": "Recyclable Waste",
        "other": "Other / Reject",
        "select": "Select waste type",
        "recommended": "Recommended category",
        "issue_type": "Issue type",
        "overflow": "Overflowing bin",
        "unclean": "Unclean area",
        "uncollected": "Uncollected waste",
        "sanitation": "Other sanitation issue",
        "issue_location": "Issue location",
        "gps": "Current location - GPS",
        "different": "Different location",
        "area": "Area",
        "street": "Street",
        "landmark": "Landmark",
        "details": "Description",
        "photo": "Photo (optional)",
        "submit": "Submit report",
        "success": "Report submitted successfully.",
        "need_description": "Please enter a description.",
        "need_location": "Please provide Area, Street, or Landmark.",
        "gps_permission": "Allow browser location permission.",
        "gps_unavailable": "GPS is unavailable. Please enter the issue location manually.",
        "fill": "Fill Level",
        "sensor": "Sensor",
        "hardware": "Hardware",
        "collection": "Collection",
        "status": "Status",
        "normal": "Normal",
        "ready": "Ready for collection",
        "full": "FULL - URGENT",
        "online": "Online",
        "healthy": "Healthy",
        "pending": "Pending",
        "collected": "Collected",
        "alert": "Automatic Alerts",
        "no_alert": "No active automatic alerts.",
        "demo": "Prototype demo data",
        "demo_note": "These bin readings are demo values, not live sensor readings.",
        "hardware_note": "A real smart bin can send sensor readings through sensor → ESP32 → Wi-Fi → Firebase. The admin portal monitors those readings.",
        "total": "Total Bins",
        "urgent": "Urgent Bins",
        "open": "Open Issues",
        "resolved": "Resolved Issues",
        "route_note": "High-fill bins receive higher priority. The system then requests an actual road route between the collection depot and the selected bins.",
        "route_map": "Actual Road Route",
        "distance": "Road distance",
        "time": "Estimated travel time",
        "priority": "Priority",
        "stop": "Stop",
        "team": "Collection team",
        "assign": "Assign route",
        "assigned": "Route assigned successfully.",
        "no_route": "No bins currently need collection.",
        "status_update": "Update",
        "progress": "Progress",
        "no_reports": "No reports yet.",
        "register": "Register New Bin",
        "bin_id": "Bin ID",
        "bin_location": "Bin location",
        "initial_fill": "Initial fill level %",
        "save": "Save",
        "exists": "That Bin ID already exists.",
        "required_bin": "Bin ID and location are required.",
        "refresh": "Refresh"
    },

    "Tamil": {
        "home": "முகப்பு",
        "seg": "கழிவு வகைப்படுத்தல்",
        "bins": "Smart Bins",
        "report": "பிரச்சினையை தெரிவிக்க",
        "my": "எனது புகார்கள்",
        "dashboard": "Admin Dashboard",
        "issues": "புகார்கள்",
        "route": "Smart Route Planning",
        "manage": "Manage Bins",
        "language": "மொழி",
        "portal": "Portal",
        "user": "User",
        "admin": "Admin",
        "welcome": "EcoNova-க்கு வரவேற்கிறோம்",
        "tagline": "Smart Waste Segregation, Disposal & Sanitation Platform",
        "description": "Smart waste collection மற்றும் சிறந்த sanitation management-க்கான digital platform.",
        "organic": "மக்கும் / ஈரக் கழிவு",
        "dry": "உலர் கழிவு",
        "recycle": "மறுசுழற்சி கழிவு",
        "other": "மற்றவை / Reject",
        "select": "கழிவு வகையை தேர்வு செய்யவும்",
        "recommended": "பரிந்துரைக்கப்படும் வகை",
        "issue_type": "பிரச்சினை வகை",
        "overflow": "நிரம்பிய குப்பைத்தொட்டி",
        "unclean": "சுத்தமில்லாத பகுதி",
        "uncollected": "சேகரிக்கப்படாத கழிவு",
        "sanitation": "மற்ற சுகாதாரப் பிரச்சினை",
        "issue_location": "பிரச்சினை இருக்கும் இடம்",
        "gps": "தற்போதைய இடம் - GPS",
        "different": "வேறு இடம்",
        "area": "பகுதி",
        "street": "தெரு",
        "landmark": "Landmark",
        "details": "விவரம்",
        "photo": "புகைப்படம் (விருப்பம்)",
        "submit": "புகாரை சமர்ப்பிக்க",
        "success": "புகார் வெற்றிகரமாக சமர்ப்பிக்கப்பட்டது.",
        "need_description": "விவரத்தை உள்ளிடவும்.",
        "need_location": "Area, Street அல்லது Landmark வழங்கவும்.",
        "gps_permission": "Browser location permission கொடுக்கவும்.",
        "gps_unavailable": "GPS கிடைக்கவில்லை. Location-ஐ manually உள்ளிடவும்.",
        "fill": "நிரம்பிய அளவு",
        "sensor": "Sensor",
        "hardware": "Hardware",
        "collection": "சேகரிப்பு",
        "status": "நிலை",
        "normal": "சாதாரணம்",
        "ready": "சேகரிப்புக்கு தயாராக உள்ளது",
        "full": "FULL - அவசரம்",
        "online": "Online",
        "healthy": "Healthy",
        "pending": "Pending",
        "collected": "Collected",
        "alert": "Automatic Alerts",
        "no_alert": "Active automatic alerts இல்லை.",
        "demo": "Prototype demo data",
        "demo_note": "இந்த bin readings demo values; live sensor readings அல்ல.",
        "hardware_note": "Real smart bin-ல் sensor → ESP32 → Wi-Fi → Firebase மூலம் readings அனுப்பலாம். Admin portal அதை monitor செய்யும்.",
        "total": "மொத்த Bins",
        "urgent": "Urgent Bins",
        "open": "Open Issues",
        "resolved": "Resolved Issues",
        "route_note": "அதிகமாக நிரம்பிய bins-க்கு அதிக priority கொடுக்கப்படும். பிறகு collection depot-ல் இருந்து selected bins வரை actual road route பெறப்படும்.",
        "route_map": "Actual Road Route",
        "distance": "Road distance",
        "time": "மதிப்பிடப்பட்ட பயண நேரம்",
        "priority": "Priority",
        "stop": "Stop",
        "team": "Collection team",
        "assign": "Route-ஐ ஒதுக்கவும்",
        "assigned": "Route வெற்றிகரமாக ஒதுக்கப்பட்டது.",
        "no_route": "இப்போது collection தேவைப்படும் bins இல்லை.",
        "status_update": "Update",
        "progress": "முன்னேற்றம்",
        "no_reports": "புகார்கள் இல்லை.",
        "register": "புதிய Bin பதிவு",
        "bin_id": "Bin ID",
        "bin_location": "Bin இருக்கும் இடம்",
        "initial_fill": "Initial fill level %",
        "save": "Save",
        "exists": "இந்த Bin ID ஏற்கனவே உள்ளது.",
        "required_bin": "Bin ID மற்றும் location கட்டாயம்.",
        "refresh": "Refresh"
    }
}


def t(key):
    return TEXT[st.session_state.language].get(key, key)


# ============================================================
# DEMO DATABASE
# ============================================================

def demo_data():
    return {
        "bins": [
            {
                "id": "BIN001",
                "area": "Gandhi Road",
                "fill": 25,
                "lat": 11.0168,
                "lon": 76.9558,
                "sensor": "Online",
                "hardware": "Healthy",
                "collection": "Pending"
            },
            {
                "id": "BIN002",
                "area": "Bus Stand",
                "fill": 55,
                "lat": 11.0183,
                "lon": 76.9725,
                "sensor": "Online",
                "hardware": "Healthy",
                "collection": "Pending"
            },
            {
                "id": "BIN003",
                "area": "Market Area",
                "fill": 82,
                "lat": 11.0046,
                "lon": 76.9616,
                "sensor": "Online",
                "hardware": "Healthy",
                "collection": "Ready"
            },
            {
                "id": "BIN004",
                "area": "Railway Station Road",
                "fill": 95,
                "lat": 11.0270,
                "lon": 76.9563,
                "sensor": "Online",
                "hardware": "Healthy",
                "collection": "Ready"
            }
        ],
        "reports": [],
        "segregation": {
            "Organic / Wet Waste": 24,
            "Dry Waste": 18,
            "Recyclable Waste": 12,
            "Other / Reject Waste": 4
        },
        "assignment": None
    }


# ============================================================
# FIREBASE
# ============================================================

def firebase_get():
    try:
        response = requests.get(
            FIREBASE_URL + "/econova.json",
            timeout=TIMEOUT
        )

        if response.ok:
            value = response.json()

            if isinstance(value, dict):
                return value

    except Exception:
        pass

    return None


def firebase_put(data):
    try:
        response = requests.put(
            FIREBASE_URL + "/econova.json",
            json=data,
            timeout=TIMEOUT
        )

        return response.ok

    except Exception:
        return False


def normalise_data(value):
    base = demo_data()

    if not isinstance(value, dict):
        return base

    if isinstance(value.get("bins"), list):
        base["bins"] = value["bins"]

    if isinstance(value.get("reports"), list):
        base["reports"] = value["reports"]

    if isinstance(value.get("segregation"), dict):
        base["segregation"] = value["segregation"]

    base["assignment"] = value.get("assignment")

    return base


def save_data():
    st.session_state.firebase_ok = firebase_put(
        st.session_state.data
    )


# ============================================================
# ROUTE CALCULATION
# ============================================================

def haversine(lat1, lon1, lat2, lon2):
    radius = 6371.0

    p1 = math.radians(lat1)
    p2 = math.radians(lat2)

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(p1)
        * math.cos(p2)
        * math.sin(dlon / 2) ** 2
    )

    return radius * 2 * math.asin(
        math.sqrt(a)
    )


def build_priority_route(bins):
    depot = (11.0169, 76.9558)

    candidates = []

    for item in bins:

        try:
            fill = float(item["fill"])
            lat = float(item["lat"])
            lon = float(item["lon"])
        except Exception:
            continue

        if item.get("collection") == "Collected":
            continue

        if fill < 50:
            continue

        candidates.append(
            {
                **item,
                "fill": fill,
                "lat": lat,
                "lon": lon
            }
        )

    route = []
    current = depot

    while candidates:

        scored = []

        for item in candidates:

            distance = haversine(
                current[0],
                current[1],
                item["lat"],
                item["lon"]
            )

            fill = item["fill"]

            if fill >= 95:
                urgency = 40
            elif fill >= 80:
                urgency = 25
            elif fill >= 60:
                urgency = 10
            else:
                urgency = 0

            score = (
                fill * 2
                + urgency
                - distance * 8
            )

            scored.append(
                (score, distance, item)
            )

        _, distance, selected = max(
            scored,
            key=lambda x: x[0]
        )

        selected["from_distance"] = round(
            distance,
            2
        )

        route.append(selected)

        current = (
            selected["lat"],
            selected["lon"]
        )

        candidates.remove(selected)

    return route


# ============================================================
# ACTUAL ROAD ROUTING
# ============================================================

@st.cache_data(ttl=300, show_spinner=False)
def get_road_route(points):

    if len(points) < 2:
        return None

    coordinates = ";".join(
        f"{lon},{lat}"
        for lat, lon in points
    )

    url = (
        "https://router.project-osrm.org/"
        "route/v1/driving/"
        f"{coordinates}"
        "?overview=full"
        "&geometries=geojson"
    )

    try:

        response = requests.get(
            url,
            timeout=15
        )

        if not response.ok:
            return None

        data = response.json()

        if data.get("code") != "Ok":
            return None

        routes = data.get("routes", [])

        if not routes:
            return None

        return routes[0]

    except Exception:
        return None


# ============================================================
# STATUS
# ============================================================

WORKFLOW = [
    "Reported",
    "Verified",
    "Assigned",
    "Accepted by Team",
    "Work Started",
    "Work in Progress",
    "Inspection",
    "Resolved",
    "Closed"
]


def display_status(report):

    progress = int(
        report.get("progress", 0)
    )

    if progress >= 100:
        return "Resolved"

    return report.get(
        "status",
        "Reported"
    )


# ============================================================
# SESSION STATE
# ============================================================

if "language" not in st.session_state:
    st.session_state.language = "English"

if "role" not in st.session_state:
    st.session_state.role = "User"

if "data" not in st.session_state:

    firebase_data = firebase_get()

    st.session_state.data = normalise_data(
        firebase_data
    )

    st.session_state.firebase_ok = (
        firebase_data is not None
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("♻️ EcoNova")

    st.session_state.language = st.selectbox(
        t("language"),
        ["English", "Tamil"],
        index=(
            0
            if st.session_state.language == "English"
            else 1
        )
    )

    st.session_state.role = st.selectbox(
        t("portal"),
        ["User", "Admin"],
        index=(
            0
            if st.session_state.role == "User"
            else 1
        )
    )

    if st.button(
        "🔄 " + t("refresh"),
        use_container_width=True
    ):

        firebase_data = firebase_get()

        st.session_state.data = normalise_data(
            firebase_data
        )

        st.session_state.firebase_ok = (
            firebase_data is not None
        )

        st.rerun()


# ============================================================
# HEADER
# ============================================================

st.title("♻️ EcoNova")

st.caption(
    t("tagline")
)

if not st.session_state.firebase_ok:

    st.warning(
        "Firebase connection unavailable. "
        "Prototype data is being used."
    )


data = st.session_state.data
bins = data["bins"]
reports = data["reports"]


# ============================================================
# NAVIGATION
# ============================================================

if st.session_state.role == "User":

    pages = [
        t("home"),
        t("seg"),
        t("bins"),
        t("report"),
        t("my")
    ]

else:

    pages = [
        t("dashboard"),
        t("seg"),
        t("bins"),
        t("issues"),
        t("route"),
        t("manage")
    ]


page = st.sidebar.radio(
    "Menu",
    pages
)


# ============================================================
# USER HOME
# ============================================================

if page == t("home"):

    st.header(
        t("welcome")
    )

    st.write(
        t("description")
    )

    urgent = sum(
        float(b.get("fill", 0)) >= 95
        for b in bins
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        t("total"),
        len(bins)
    )

    c2.metric(
        t("urgent"),
        urgent
    )

    c3.metric(
        t("open"),
        sum(
            int(r.get("progress", 0)) < 100
            for r in reports
        )
    )

    st.info(
        t("demo_note")
    )


# ============================================================
# WASTE SEGREGATION
# ============================================================

elif page == t("seg"):

    st.header(
        "♻️ " + t("seg")
    )

    waste_types = [
        t("organic"),
        t("dry"),
        t("recycle"),
        t("other")
    ]

    selected = st.selectbox(
        t("select"),
        waste_types
    )

    st.success(
        f"**{t('recommended')}:** "
        f"{selected}"
    )

    st.subheader(
        "Segregation Monitoring"
    )

    stats = data.get(
        "segregation",
        {}
    )

    columns = st.columns(4)

    labels = [
        t("organic"),
        t("dry"),
        t("recycle"),
        t("other")
    ]

    keys = [
        "Organic / Wet Waste",
        "Dry Waste",
        "Recyclable Waste",
        "Other / Reject Waste"
    ]

    for i in range(4):

        columns[i].metric(
            labels[i],
            stats.get(
                keys[i],
                0
            )
        )


# ============================================================
# SMART BINS
# ============================================================

elif page == t("bins"):

    st.header(
        "🗑️ " + t("bins")
    )

    st.info(
        t("demo_note")
    )

    for item in bins:

        fill = float(
            item.get("fill", 0)
        )

        if fill >= 95:
            status = t("full")
        elif fill >= 75:
            status = t("ready")
        else:
            status = t("normal")

        with st.container(border=True):

            c1, c2, c3, c4 = st.columns(4)

            c1.subheader(
                item.get("id", "")
            )

            c1.write(
                item.get("area", "")
            )

            c2.metric(
                t("fill"),
                f"{fill:.0f}%"
            )

            c3.write(
                f"**{t('status')}:** "
                f"{status}"
            )

            c3.write(
                f"**{t('collection')}:** "
                f"{item.get('collection', 'Pending')}"
            )

            c4.write(
                f"**{t('sensor')}:** "
                f"{item.get('sensor', 'Online')}"
            )

            c4.write(
                f"**{t('hardware')}:** "
                f"{item.get('hardware', 'Healthy')}"
            )


# ============================================================
# USER REPORT
# ============================================================

elif page == t("report"):

    st.header(
        "📢 " + t("report")
    )

    issue = st.selectbox(
        t("issue_type"),
        [
            t("overflow"),
            t("unclean"),
            t("uncollected"),
            t("sanitation")
        ]
    )

    location_mode = st.radio(
        t("issue_location"),
        [
            t("gps"),
            t("different")
        ],
        horizontal=True
    )

    latitude = None
    longitude = None

    area = ""
    street = ""
    landmark = ""

    if location_mode == t("gps"):

        if GPS_AVAILABLE:

            location = streamlit_geolocation()

            if (
                isinstance(location, dict)
                and location.get("latitude") is not None
                and location.get("longitude") is not None
            ):

                latitude = float(
                    location["latitude"]
                )

                longitude = float(
                    location["longitude"]
                )

                st.success(
                    f"📍 {latitude:.5f}, "
                    f"{longitude:.5f}"
                )

            else:

                st.info(
                    t("gps_permission")
                )

        else:

            st.info(
                t("gps_unavailable")
            )

    if (
        location_mode == t("different")
        or latitude is None
    ):

        c1, c2 = st.columns(2)

        area = c1.text_input(
            t("area")
        )

        street = c2.text_input(
            t("street")
        )

        landmark = st.text_input(
            t("landmark")
        )

    description = st.text_area(
        t("details")
    )

    photo = st.file_uploader(
        t("photo"),
        type=[
            "jpg",
            "jpeg",
            "png"
        ]
    )

    if st.button(
        "📤 " + t("submit"),
        type="primary"
    ):

        has_location = any(
            [
                area.strip(),
                street.strip(),
                landmark.strip()
            ]
        )

        if not description.strip():

            st.error(
                t("need_description")
            )

        elif (
            latitude is None
            and not has_location
        ):

            st.error(
                t("need_location")
            )

        else:

            report_id = (
                f"REP"
                f"{len(reports) + 1:03d}"
            )

            reports.append(
                {
                    "id": report_id,
                    "issue": issue,
                    "area": area.strip(),
                    "street": street.strip(),
                    "landmark": landmark.strip(),
                    "latitude": latitude,
                    "longitude": longitude,
                    "description": description.strip(),
                    "photo_name": (
                        photo.name
                        if photo
                        else ""
                    ),
                    "status": "Reported",
                    "progress": 0,
                    "created_at": datetime.now().strftime(
                        "%Y-%m-%d %H:%M"
                    )
                }
            )

            save_data()

            st.success(
                t("success")
            )


# ============================================================
# USER MY REPORTS
# ============================================================

elif page == t("my"):

    st.header(
        "📋 " + t("my")
    )

    if not reports:

        st.info(
            t("no_reports")
        )

    for report in reports:

        progress = max(
            0,
            min(
                100,
                int(
                    report.get(
                        "progress",
                        0
                    )
                )
            )
        )

        status = display_status(
            report
        )

        with st.container(border=True):

            st.subheader(
                report.get(
                    "id",
                    ""
                )
            )

            st.write(
                f"**{t('issue_type')}:** "
                f"{report.get('issue', '')}"
            )

            location = ", ".join(
                x
                for x in [
                    report.get("area", ""),
                    report.get("street", ""),
                    report.get("landmark", "")
                ]
                if x
            )

            if not location:

                if report.get("latitude") is not None:

                    location = (
                        f"{float(report['latitude']):.5f}, "
                        f"{float(report['longitude']):.5f}"
                    )

            st.write(
                f"**Location:** "
                f"{location or 'Not provided'}"
            )

            st.write(
                f"**{t('status')}:** "
                f"{status}"
            )

            st.progress(
                progress / 100
            )

            st.caption(
                f"{t('progress')}: "
                f"{progress}%"
            )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

elif page == t("dashboard"):

    st.header(
        "📊 " + t("dashboard")
    )

    urgent_bins = [
        b
        for b in bins
        if float(b.get("fill", 0)) >= 95
    ]

    open_issues = [
        r
        for r in reports
        if int(r.get("progress", 0)) < 100
    ]

    resolved_issues = [
        r
        for r in reports
        if int(r.get("progress", 0)) >= 100
    ]

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        t("total"),
        len(bins)
    )

    c2.metric(
        t("urgent"),
        len(urgent_bins)
    )

    c3.metric(
        t("open"),
        len(open_issues)
    )

    c4.metric(
        t("resolved"),
        len(resolved_issues)
    )

    st.subheader(
        "🚨 " + t("alert")
    )

    if urgent_bins:

        for b in urgent_bins:

            st.error(
                f"{b['id']} | "
                f"{b['area']} | "
                f"{b['fill']}% | "
                f"{t('full')}"
            )

    else:

        st.success(
            t("no_alert")
        )

    st.subheader(
        "🔧 Hardware & Sensor Monitoring"
    )

    st.info(
        t("hardware_note")
    )

    for b in bins:

        with st.container(border=True):

            a, c, d, e = st.columns(4)

            a.write(
                f"**{b['id']}**"
            )

            c.write(
                f"{t('fill')}: "
                f"{b.get('fill', 0)}%"
            )

            d.write(
                f"{t('sensor')}: "
                f"{b.get('sensor', 'Online')}"
            )

            e.write(
                f"{t('hardware')}: "
                f"{b.get('hardware', 'Healthy')}"
            )


# ============================================================
# ADMIN ISSUE REPORTS
# ============================================================

elif page == t("issues"):

    st.header(
        "📋 " + t("issues")
    )

    if not reports:

        st.info(
            t("no_reports")
        )

    for i, report in enumerate(
        reports
    ):

        current = display_status(
            report
        )

        with st.container(border=True):

            st.subheader(
                report.get(
                    "id",
                    ""
                )
            )

            st.write(
                f"**{t('issue_type')}:** "
                f"{report.get('issue', '')}"
            )

            st.write(
                f"**{t('details')}:** "
                f"{report.get('description', '')}"
            )

            c1, c2 = st.columns(2)

            status = c1.selectbox(
                t("status"),
                WORKFLOW,
                index=(
                    WORKFLOW.index(current)
                    if current in WORKFLOW
                    else 0
                ),
                key=f"status_{i}"
            )

            progress = c2.slider(
                t("progress"),
                0,
                100,
                int(
                    report.get(
                        "progress",
                        0
                    )
                ),
                key=f"progress_{i}"
            )

            if st.button(
                t("status_update"),
                key=f"update_{i}"
            ):

                report["progress"] = progress

                if progress >= 100:
                    report["status"] = "Resolved"
                else:
                    report["status"] = status

                save_data()

                st.success(
                    "Updated"
                )

                st.rerun()


# ============================================================
# SMART ROUTE PLANNING
# ============================================================

elif page == t("route"):

    st.header(
        "🚛 " + t("route")
    )

    st.write(
        t("route_note")
    )

    route = build_priority_route(
        bins
    )

    if not route:

        st.success(
            t("no_route")
        )

    else:

        st.subheader(
            "📋 Collection Sequence"
        )

        st.write(
            "Collection Depot → "
            + " → ".join(
                b["id"]
                for b in route
            )
        )

        for i, b in enumerate(
            route,
            start=1
        ):

            if b["fill"] >= 95:
                priority = "URGENT"
            elif b["fill"] >= 75:
                priority = "HIGH"
            else:
                priority = "MEDIUM"

            with st.container(
                border=True
            ):

                a, c, d, e = st.columns(4)

                a.subheader(
                    f"{t('stop')} {i}"
                )

                c.write(
                    f"**{b['id']}**"
                )

                c.write(
                    b["area"]
                )

                d.write(
                    f"{t('fill')}: "
                    f"{b['fill']:.0f}%"
                )

                e.write(
                    f"{t('priority')}: "
                    f"{priority}"
                )

        # ----------------------------------------------------
        # ACTUAL ROAD MAP
        # ----------------------------------------------------

        points = [
            (11.0169, 76.9558)
        ]

        points.extend(
            [
                (
                    b["lat"],
                    b["lon"]
                )
                for b in route
            ]
        )

        road = get_road_route(
            points
        )

        if road:

            st.subheader(
                "🗺️ " + t("route_map")
            )

            center_lat = sum(
                p[0]
                for p in points
            ) / len(points)

            center_lon = sum(
                p[1]
                for p in points
            ) / len(points)

            map_object = folium.Map(
                location=[
                    center_lat,
                    center_lon
                ],
                zoom_start=14
            )

            folium.Marker(
                points[0],
                tooltip="Collection Depot"
            ).add_to(
                map_object
            )

            for i, b in enumerate(
                route,
                start=1
            ):

                folium.Marker(
                    [
                        b["lat"],
                        b["lon"]
                    ],
                    tooltip=(
                        f"Stop {i} - "
                        f"{b['id']} - "
                        f"{b['fill']}%"
                    )
                ).add_to(
                    map_object
                )

            geometry = road[
                "geometry"
            ][
                "coordinates"
            ]

            road_line = [
                (
                    lat,
                    lon
                )
                for lon, lat
                in geometry
            ]

            folium.PolyLine(
                road_line,
                weight=5
            ).add_to(
                map_object
            )

            st_folium(
                map_object,
                use_container_width=True,
                height=500
            )

            c1, c2 = st.columns(2)

            c1.metric(
                t("distance"),
                f"{road['distance'] / 1000:.2f} km"
            )

            c2.metric(
                t("time"),
                f"{road['duration'] / 60:.0f} min"
            )

        else:

            st.warning(
                "Road routing service is unavailable right now. "
                "The priority sequence is still available."
            )

        # ----------------------------------------------------
        # ASSIGN TEAM
        # ----------------------------------------------------

        st.subheader(
            "👷 " + t("team")
        )

        team = st.selectbox(
            t("team"),
            [
                "Municipality Team A",
                "Municipality Team B",
                "Collection Vehicle 01"
            ]
        )

        if st.button(
            "🚛 " + t("assign"),
            type="primary"
        ):

            data["assignment"] = {
                "team": team,
                "bins": [
                    b["id"]
                    for b in route
                ],
                "time": datetime.now().strftime(
                    "%Y-%m-%d %H:%M"
                )
            }

            save_data()

            st.success(
                t("assigned")
            )


# ============================================================
# MANAGE BINS
# ============================================================

elif page == t("manage"):

    st.header(
        "🗑️ " + t("manage")
    )

    c1, c2 = st.columns(2)

    new_id = c1.text_input(
        t("bin_id")
    )

    new_area = c2.text_input(
        t("bin_location")
    )

    new_fill = st.number_input(
        t("initial_fill"),
        min_value=0,
        max_value=100,
        value=0,
        step=1
    )

    if st.button(
        "💾 " + t("save"),
        type="primary"
    ):

        new_id = new_id.strip()
        new_area = new_area.strip()

        if not new_id or not new_area:

            st.error(
                t("required_bin")
            )

        elif any(
            str(b.get("id", "")).lower()
            == new_id.lower()
            for b in bins
        ):

            st.error(
                t("exists")
            )

        else:

            bins.append(
                {
                    "id": new_id,
                    "area": new_area,
                    "fill": int(new_fill),

                    # Demo coordinates.
                    # Real hardware can provide actual coordinates.
                    "lat": 11.0168,
                    "lon": 76.9558,

                    "sensor": "Online",
                    "hardware": "Healthy",
                    "collection": "Pending"
                }
            )

            save_data()

            st.success(
                "Saved"
            )

            st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "EcoNova • Smart Waste Segregation, Disposal & Improved Sanitation"
)