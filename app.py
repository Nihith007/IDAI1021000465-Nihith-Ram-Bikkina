import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import tempfile
import os

# Page configuration
st.set_page_config(
    page_title="MedTimer - Daily Medicine Companion",
    page_icon="💊",
    layout="wide"
)

# Initialize session state
if 'medicines' not in st.session_state:
    st.session_state.medicines = []
if 'adherence_data' not in st.session_state:
    st.session_state.adherence_data = {}

# Custom CSS for exact styling
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 10px 24px;
        border: none;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #45a049;
        color: white;
    }
    .medicine-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 10px;
        border-left: 5px solid #4CAF50;
    }
    .taken-card {
        border-left-color: #4CAF50 !important;
        background-color: #e8f5e9 !important;
    }
    .upcoming-card {
        border-left-color: #ff9800 !important;
        background-color: #fff3e0 !important;
    }
    .missed-card {
        border-left-color: #f44336 !important;
        background-color: #ffebee !important;
    }
    .adherence-score {
        font-size: 72px;
        font-weight: bold;
        color: #4CAF50;
        text-align: center;
        margin: 20px 0;
    }
    .score-label {
        text-align: center;
        color: #666;
        font-size: 16px;
        margin-bottom: 30px;
    }
    .main-header {
        color: #2c3e50;
        font-weight: 600;
        margin-bottom: 20px;
    }
    .status-badge {
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 14px;
    }
    .taken-badge {
        background-color: #4CAF50;
        color: white;
    }
    .upcoming-badge {
        background-color: #ff9800;
        color: white;
    }
    .missed-badge {
        background-color: #f44336;
        color: white;
    }
    .download-button {
        display: inline-block;
        background-color: #4CAF50;
        color: white;
        padding: 10px 20px;
        text-decoration: none;
        border-radius: 5px;
        font-weight: bold;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Generate smiley face image (using matplotlib instead of turtle for Streamlit compatibility)
def generate_smiley():
    fig, ax = plt.subplots(figsize=(3, 3))
    ax.set_aspect('equal')
    
    # Draw face
    face_circle = plt.Circle((0.5, 0.5), 0.4, color='#FFD700', ec='black', lw=2)
    ax.add_patch(face_circle)
    
    # Draw eyes
    left_eye = plt.Circle((0.35, 0.6), 0.08, color='white', ec='black', lw=1)
    right_eye = plt.Circle((0.65, 0.6), 0.08, color='white', ec='black', lw=1)
    ax.add_patch(left_eye)
    ax.add_patch(right_eye)
    
    # Draw pupils
    left_pupil = plt.Circle((0.35, 0.6), 0.04, color='black')
    right_pupil = plt.Circle((0.65, 0.6), 0.04, color='black')
    ax.add_patch(left_pupil)
    ax.add_patch(right_pupil)
    
    # Draw smile
    smile = plt.Arc((0.5, 0.4), 0.3, 0.2, angle=0, theta1=180, theta2=0, color='black', lw=3)
    ax.add_patch(smile)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    # Save to buffer
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    
    return buf

# Generate trophy image
def generate_trophy():
    fig, ax = plt.subplots(figsize=(3, 3))
    ax.set_aspect('equal')
    
    # Draw trophy base
    base = plt.Rectangle((0.2, 0.1), 0.6, 0.1, color='#FFD700', ec='black', lw=2)
    ax.add_patch(base)
    
    # Draw trophy cup
    cup_bottom = plt.Rectangle((0.25, 0.2), 0.5, 0.2, color='#FFD700', ec='black', lw=2)
    ax.add_patch(cup_bottom)
    
    cup_top = plt.Rectangle((0.3, 0.4), 0.4, 0.3, color='#FFD700', ec='black', lw=2)
    ax.add_patch(cup_top)
    
    # Draw handles
    left_handle = plt.Arc((0.2, 0.45), 0.2, 0.2, angle=0, theta1=90, theta2=270, color='#FFD700', lw=4)
    right_handle = plt.Arc((0.8, 0.45), 0.2, 0.2, angle=0, theta1=270, theta2=90, color='#FFD700', lw=4)
    ax.add_patch(left_handle)
    ax.add_patch(right_handle)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    # Save to buffer
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    
    return buf

# Medicine management functions
def add_medicine(name, dosage, time_str, frequency, notes=""):
    medicine = {
        'id': len(st.session_state.medicines) + 1,
        'name': name,
        'dosage': dosage,
        'time': time_str,
        'frequency': frequency,
        'notes': notes,
        'taken': False,
        'date_added': date.today().isoformat()
    }
    st.session_state.medicines.append(medicine)
    
    # Update adherence data
    today = date.today().isoformat()
    if today not in st.session_state.adherence_data:
        st.session_state.adherence_data[today] = {'expected': 0, 'taken': 0}
    st.session_state.adherence_data[today]['expected'] += 1

def mark_as_taken(medicine_id):
    for med in st.session_state.medicines:
        if med['id'] == medicine_id:
            med['taken'] = True
            
            # Update adherence data
            today = date.today().isoformat()
            if today in st.session_state.adherence_data:
                st.session_state.adherence_data[today]['taken'] += 1
            break

def mark_as_not_taken(medicine_id):
    for med in st.session_state.medicines:
        if med['id'] == medicine_id:
            med['taken'] = False
            
            # Update adherence data
            today = date.today().isoformat()
            if today in st.session_state.adherence_data:
                st.session_state.adherence_data[today]['taken'] = max(0, st.session_state.adherence_data[today]['taken'] - 1)
            break

def delete_medicine(medicine_id):
    st.session_state.medicines = [med for med in st.session_state.medicines if med['id'] != medicine_id]
    # Note: We're not removing from adherence_data as it's historical

def calculate_adherence_score():
    """Calculate adherence score for last 7 days"""
    if not st.session_state.adherence_data:
        return 0
    
    today = date.today()
    seven_days_ago = today - timedelta(days=6)
    
    total_expected = 0
    total_taken = 0
    
    for day_offset in range(7):
        current_day = today - timedelta(days=day_offset)
        day_str = current_day.isoformat()
        
        if day_str in st.session_state.adherence_data:
            data = st.session_state.adherence_data[day_str]
            total_expected += data['expected']
            total_taken += data['taken']
    
    if total_expected == 0:
        return 0
    
    return round((total_taken / total_expected) * 100)

# Streamlit UI
def main():
    # Sidebar Navigation
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="color: #4CAF50; margin-bottom: 10px;">💊</h1>
            <h2 style="color: #2c3e50; margin: 0;">MedTimer</h2>
            <p style="color: #666; margin-top: 5px;">Daily Medicine Companion</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Current date
        st.markdown(f"### {datetime.now().strftime('%A, %B %d')}")
        
        # Quick stats
        score = calculate_adherence_score()
        st.metric("Adherence Score", f"{score}%")
        
        st.markdown("---")
        
        # Navigation
        nav_options = ["🏠 Home", "➕ Add Medicine", "📊 Report", "⭐ Score"]
        selected_nav = st.radio("Navigate", nav_options, label_visibility="collapsed")
    
    # Home Page
    if selected_nav == "🏠 Home":
        st.title("Today's Medicines")
        
        if not st.session_state.medicines:
            st.info("No medicines added yet. Go to 'Add Medicine' to get started!")
        else:
            current_time = datetime.now().time()
            today_str = date.today().isoformat()
            
            for med in st.session_state.medicines:
                # Only show medicines added today or earlier
                if med['date_added'] > today_str:
                    continue
                    
                med_time = datetime.strptime(med['time'], "%H:%M").time()
                
                # Determine status
                if med['taken']:
                    status_class = "taken-card"
                    status_badge_class = "taken-badge"
                    status_text = "✓ Taken"
                elif current_time >= med_time:
                    status_class = "missed-card"
                    status_badge_class = "missed-badge"
                    status_text = "✗ Missed"
                else:
                    status_class = "upcoming-card"
                    status_badge_class = "upcoming-badge"
                    status_text = "⏰ Upcoming"
                
                # Display medicine card
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.markdown(f"""
                        <div class="medicine-card {status_class}">
                            <div style="display: flex; justify-content: space-between; align-items: start;">
                                <div style="flex: 1;">
                                    <h3 style="margin: 0 0 5px 0; color: #2c3e50;">{med['name']}</h3>
                                    <p style="margin: 0 0 5px 0; color: #666; font-size: 16px;">{med['dosage']}</p>
                                    <p style="margin: 0 0 5px 0; color: #666; font-size: 14px;">{med['time']} - {med['frequency']}</p>
                                    {f'<p style="margin: 0; color: #888; font-size: 13px;"><em>Note: {med["notes"]}</em></p>' if med['notes'] else ''}
                                </div>
                                <div>
                                    <span class="status-badge {status_badge_class}">{status_text}</span>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        if not med['taken'] and current_time >= med_time:
                            if st.button("Mark Taken", key=f"mark_{med['id']}", use_container_width=True):
                                mark_as_taken(med['id'])
                                st.rerun()
                        elif med['taken']:
                            if st.button("Undo", key=f"undo_{med['id']}", use_container_width=True):
                                mark_as_not_taken(med['id'])
                                st.rerun()
                        else:
                            st.button("Upcoming", key=f"up_{med['id']}", disabled=True, use_container_width=True)
            
            st.markdown("---")
            col_total, col_taken, col_missed = st.columns(3)
            with col_total:
                total_today = len([m for m in st.session_state.medicines if m['date_added'] <= today_str])
                st.metric("Total Today", total_today)
            with col_taken:
                taken_today = len([m for m in st.session_state.medicines if m['taken'] and m['date_added'] <= today_str])
                st.metric("Taken", taken_today, delta=None)
            with col_missed:
                missed_today = len([m for m in st.session_state.medicines if not m['taken'] and 
                                  datetime.strptime(m['time'], "%H:%M").time() <= current_time and 
                                  m['date_added'] <= today_str])
                st.metric("Missed", missed_today, delta=None)
    
    # Add Medicine Page
    elif selected_nav == "➕ Add Medicine":
        st.title("Add Medicine")
        
        with st.form("add_medicine_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Medicine Name *", placeholder="e.g., Aspirin", help="Enter the name of your medicine")
                dosage = st.text_input("Dosage *", placeholder="e.g., 100mg, 1 tablet", help="Enter the dosage amount")
                med_time = st.time_input("Time", value=datetime.strptime("09:00", "%H:%M").time())
            
            with col2:
                frequency = st.selectbox("Frequency", ["Daily", "Twice Daily", "Weekly", "Monthly", "As Needed"])
                notes = st.text_area("Notes (Optional)", placeholder="e.g., Take with food, After meals", 
                                   help="Any additional instructions")
            
            st.markdown("---")
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
            
            with col_btn1:
                submit = st.form_submit_button("✅ Add Medicine", type="primary", use_container_width=True)
            with col_btn2:
                cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
            
            if submit:
                if name and dosage:
                    add_medicine(name, dosage, med_time.strftime("%H:%M"), frequency, notes)
                    st.success(f"✅ **{name}** has been added successfully!")
                    st.balloons()
                else:
                    st.error("Please fill in all required fields (*)")
    
    # Report Page
    elif selected_nav == "📊 Report":
        st.title("7-Day Report")
        st.markdown("Your medication history at a glance")
        
        # Generate report data
        today = date.today()
        
        if st.session_state.medicines:
            # Create date headers for last 7 days
            date_headers = []
            for i in range(6, -1, -1):
                report_date = today - timedelta(days=i)
                date_headers.append(report_date.strftime("%a %d"))
            
            # Create report table data
            report_data = []
            medicines_today = [m for m in st.session_state.medicines if m['date_added'] <= today.isoformat()]
            
            for med in medicines_today:
                row = {"Medicine": f"{med['name']}\n{med['dosage']}"}
                med_date_added = datetime.strptime(med['date_added'], "%Y-%m-%d").date()
                
                for i in range(6, -1, -1):
                    report_date = today - timedelta(days=i)
                    date_key = report_date.strftime("%a %d")
                    
                    if report_date >= med_date_added:
                        # For today, check if taken
                        if report_date == today:
                            row[date_key] = "☑" if med['taken'] else "☒"
                        else:
                            # For past days, show taken status (simplified logic)
                            row[date_key] = "☑" if med['taken'] and report_date == today else "☒"
                    else:
                        row[date_key] = ""
                
                report_data.append(row)
            
            if report_data:
                df = pd.DataFrame(report_data)
                
                # Display as table
                st.dataframe(
                    df,
                    use_container_width=True,
                    column_config={
                        "Medicine": st.column_config.TextColumn(
                            "Medicine",
                            width="medium"
                        )
                    }
                )
                
                # Download CSV
                csv = df.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="medtimer_report.csv" class="download-button">📥 Export to CSV</a>'
                st.markdown(href, unsafe_allow_html=True)
                
                # Summary statistics
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    total_meds = len(medicines_today)
                    st.metric("Total Medicines", total_meds)
                
                with col2:
                    days_tracked = min(len(st.session_state.adherence_data), 7)
                    st.metric("Days Tracked", days_tracked)
                
                with col3:
                    total_taken = sum(data['taken'] for data in st.session_state.adherence_data.values())
                    st.metric("Total Taken", total_taken)
                
                # Legend
                st.markdown("---")
                st.markdown("**Legend**")
                legend_col1, legend_col2 = st.columns(2)
                with legend_col1:
                    st.markdown("☑ Medicine taken")
                with legend_col2:
                    st.markdown("☒ Medicine not taken")
            else:
                st.info("No medicine history available for the last 7 days.")
        else:
            st.info("No medicines added yet. Add medicines to see your report.")
    
    # Score Page
    else:
        st.title("Adherence Score")
        st.markdown("Your medication adherence over the last 7 days")
        
        score = calculate_adherence_score()
        
        # Display score in large format
        st.markdown(f'<div class="adherence-score">{score}%</div>', unsafe_allow_html=True)
        st.markdown('<div class="score-label">Adherence</div>', unsafe_allow_html=True)
        
        # Display message based on score
        col_msg, col_img = st.columns([2, 1])
        
        with col_msg:
            if score >= 80:
                st.success("### 🎉 Excellent! Keep up the great work!")
                st.markdown("You're doing an amazing job staying on track with your medications!")
                img_buffer = generate_trophy()
            elif score >= 50:
                st.info("### 👍 Good Job!")
                st.markdown("You're making good progress with your medication routine!")
                img_buffer = generate_smiley()
            else:
                st.warning("### 💪 Keep Trying!")
                st.markdown("Don't worry! Every day is a new chance to improve your routine.")
                img_buffer = generate_smiley()  # Still show smiley for encouragement
        
        with col_img:
            if score >= 50:
                st.image(img_buffer, caption="Great job!" if score >= 80 else "You're doing well!")
        
        # Statistics
        st.markdown("---")
        st.markdown("### 7-Day Statistics")
        
        today = date.today()
        total_expected = 0
        total_taken = 0
        
        for day_offset in range(7):
            current_day = today - timedelta(days=day_offset)
            day_str = current_day.isoformat()
            
            if day_str in st.session_state.adherence_data:
                data = st.session_state.adherence_data[day_str]
                total_expected += data['expected']
                total_taken += data['taken']
        
        # Display metrics in cards
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        
        with col_stat1:
            st.metric(
                "Total Medicines",
                len(st.session_state.medicines),
                help="Number of medicines in your schedule"
            )
        
        with col_stat2:
            st.metric(
                "Doses Taken",
                total_taken,
                help="Total doses taken in the last 7 days"
            )
        
        with col_stat3:
            st.metric(
                "Expected Doses",
                total_expected,
                help="Total doses expected in the last 7 days"
            )
        
        # Progress visualization
        if total_expected > 0:
            progress = total_taken / total_expected
            st.markdown("---")
            st.markdown("### Progress Overview")
            
            # Progress bar
            st.progress(progress)
            st.caption(f"{total_taken} out of {total_expected} doses taken ({score}%)")
            
            # Create a simple chart
            if len(st.session_state.adherence_data) > 0:
                dates = []
                adherence_rates = []
                
                for day_offset in range(6, -1, -1):
                    current_day = today - timedelta(days=day_offset)
                    day_str = current_day.isoformat()
                    date_label = current_day.strftime("%a")
                    
                    if day_str in st.session_state.adherence_data:
                        data = st.session_state.adherence_data[day_str]
                        if data['expected'] > 0:
                            rate = (data['taken'] / data['expected']) * 100
                        else:
                            rate = 0
                    else:
                        rate = 0
                    
                    dates.append(date_label)
                    adherence_rates.append(rate)
                
                # Create bar chart
                fig, ax = plt.subplots(figsize=(10, 4))
                bars = ax.bar(dates, adherence_rates, color='#4CAF50', alpha=0.7)
                ax.set_ylim(0, 100)
                ax.set_ylabel('Adherence %')
                ax.set_title('Daily Adherence (Last 7 Days)')
                ax.grid(True, alpha=0.3)
                
                # Add value labels on bars
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                           f'{int(height)}%', ha='center', va='bottom', fontsize=9)
                
                st.pyplot(fig)

if __name__ == "__main__":
    main()
