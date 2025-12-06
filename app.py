import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import json
from io import StringIO

# Page configuration
st.set_page_config(
    page_title="MedTimer - Medication Tracker",
    page_icon="💊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for mobile-like design
st.markdown("""
<style>
    /* Main container styling */
    .stApp {
        background-color: #EFF6FF;
        max-width: 450px;
        margin: 0 auto;
    }
    
    /* Remove padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }
    
    /* Card styling */
    .medicine-card {
        background: white;
        border-radius: 24px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .medicine-card.taken {
        opacity: 0.6;
        border: 2px solid #86EFAC;
    }
    
    /* Header styling */
    h1 {
        color: #1E3A8A;
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        color: #1E3A8A;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        color: #1F2937;
        font-size: 1.25rem;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        border-radius: 16px;
        height: 3.5rem;
        font-weight: 500;
        border: none;
        transition: all 0.3s;
    }
    
    /* Input styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select,
    .stTimeInput > div > div > input {
        border-radius: 16px;
        border: 2px solid #E5E7EB;
        padding: 1rem 1.5rem;
        background-color: #F9FAFB;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    .status-taken {
        background-color: #D1FAE5;
        color: #065F46;
    }
    
    .status-pending {
        background-color: #FED7AA;
        color: #9A3412;
    }
    
    /* Stats box */
    .stats-box {
        background: white;
        border-radius: 24px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Progress circle */
    .progress-circle {
        width: 200px;
        height: 200px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
        font-size: 3rem;
        font-weight: bold;
    }
    
    /* Bottom navigation */
    .bottom-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: white;
        border-top: 2px solid #E5E7EB;
        padding: 0.75rem 1rem;
        z-index: 999;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
    }
    
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'medicines' not in st.session_state:
    st.session_state.medicines = []

if 'logs' not in st.session_state:
    st.session_state.logs = []

if 'current_screen' not in st.session_state:
    st.session_state.current_screen = 'home'

if 'editing_medicine' not in st.session_state:
    st.session_state.editing_medicine = None

# Helper functions
def get_today():
    return datetime.now().strftime('%Y-%m-%d')

def get_today_formatted():
    return datetime.now().strftime('%A, %B %d')

def is_medicine_taken(medicine_id, scheduled_time):
    today = get_today()
    return any(
        log['medicine_id'] == medicine_id and 
        log['date'] == today and 
        log['time'] == scheduled_time and 
        log['taken']
        for log in st.session_state.logs
    )

def mark_medicine_taken(medicine_id, medicine_name, scheduled_time):
    today = get_today()
    now = datetime.now().strftime('%H:%M')
    
    # Find existing log
    for i, log in enumerate(st.session_state.logs):
        if (log['medicine_id'] == medicine_id and 
            log['date'] == today and 
            log['time'] == scheduled_time):
            # Toggle taken status
            st.session_state.logs[i]['taken'] = not log['taken']
            st.session_state.logs[i]['taken_at'] = now if not log['taken'] else None
            return
    
    # Create new log
    st.session_state.logs.append({
        'medicine_id': medicine_id,
        'medicine_name': medicine_name,
        'date': today,
        'time': scheduled_time,
        'taken': True,
        'taken_at': now
    })

def calculate_adherence():
    if not st.session_state.medicines:
        return 0
    
    last_7_days = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') 
                   for i in range(7)]
    
    total_expected = len(st.session_state.medicines) * 7
    total_taken = sum(
        1 for log in st.session_state.logs
        if log['date'] in last_7_days and log['taken']
    )
    
    return round((total_taken / total_expected) * 100) if total_expected > 0 else 0

# Navigation function
def navigate_to(screen):
    st.session_state.current_screen = screen
    st.rerun()

# Home Screen
def home_screen():
    st.markdown("# MedTimer")
    st.markdown(f"<p style='color: #1E40AF; font-size: 1.1rem;'>{get_today_formatted()}</p>", 
                unsafe_allow_html=True)
    
    st.markdown("## Today's Medicines")
    
    if not st.session_state.medicines:
        st.markdown("""
        <div class="medicine-card" style="text-align: center; padding: 3rem 1.5rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">💊</div>
            <p style="color: #6B7280; font-size: 1.1rem; margin-bottom: 0.5rem;">No medicines scheduled</p>
            <p style="color: #9CA3AF; font-size: 0.9rem;">Tap the + button below to add your first medicine</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Sort medicines by time
        sorted_medicines = sorted(st.session_state.medicines, key=lambda x: x['time'])
        
        for medicine in sorted_medicines:
            taken = is_medicine_taken(medicine['id'], medicine['time'])
            
            card_class = "medicine-card taken" if taken else "medicine-card"
            
            with st.container():
                st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
                
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    icon = "💊" if not taken else "✅"
                    name_style = "text-decoration: line-through; color: #9CA3AF;" if taken else "color: #1F2937;"
                    st.markdown(f"""
                        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
                            <span style="font-size: 2rem;">{icon}</span>
                            <h3 style="{name_style} margin: 0;">{medicine['name']}</h3>
                        </div>
                        <p style="color: #6B7280; margin-left: 2.75rem; margin-bottom: 0.75rem;">{medicine['dosage']}</p>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-left: 2.75rem; color: #6B7280; margin-bottom: 0.75rem;">
                            <span>🕐</span>
                            <span>{medicine['time']}</span>
                            <span>•</span>
                            <span>{medicine['frequency']}</span>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    status_class = "status-taken" if taken else "status-pending"
                    status_text = "✓ Taken" if taken else "Pending"
                    st.markdown(f'<span class="status-badge {status_class}">{status_text}</span>', 
                              unsafe_allow_html=True)
                    
                    if medicine.get('notes'):
                        st.markdown(f"<p style='color: #6B7280; font-size: 0.875rem; font-style: italic; margin-top: 0.75rem; margin-left: 2.75rem;'>Note: {medicine['notes']}</p>", 
                                  unsafe_allow_html=True)
                
                with col2:
                    if st.button("✏️", key=f"edit_{medicine['id']}", help="Edit medicine"):
                        st.session_state.editing_medicine = medicine
                        navigate_to('edit')
                
                # Mark taken button
                button_type = "secondary" if taken else "primary"
                button_text = "Mark as Not Taken" if taken else "✓ Mark as Taken"
                
                if st.button(button_text, key=f"mark_{medicine['id']}", 
                           type=button_type, use_container_width=True):
                    mark_medicine_taken(medicine['id'], medicine['name'], medicine['time'])
                    st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick stats
        total_today = len(sorted_medicines)
        completed_today = sum(1 for m in sorted_medicines 
                            if is_medicine_taken(m['id'], m['time']))
        
        st.markdown("""
        <div class="medicine-card" style="margin-top: 2rem;">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div style="text-align: center;">
                    <p style="color: #6B7280; margin-bottom: 0.25rem;">Total Today</p>
                    <p style="color: #1E3A8A; font-size: 1.5rem; font-weight: bold; margin: 0;">{}</p>
                </div>
                <div style="text-align: center;">
                    <p style="color: #6B7280; margin-bottom: 0.25rem;">Completed</p>
                    <p style="color: #16A34A; font-size: 1.5rem; font-weight: bold; margin: 0;">{}</p>
                </div>
            </div>
        </div>
        """.format(total_today, completed_today), unsafe_allow_html=True)

# Add Medicine Screen
def add_medicine_screen():
    st.markdown("← Back", help="Go back")
    if st.button("⬅️ Back to Home", use_container_width=True):
        navigate_to('home')
    
    st.markdown("# 💊 Add Medicine")
    
    with st.form("add_medicine_form"):
        name = st.text_input("Medicine Name *", placeholder="e.g., Aspirin")
        dosage = st.text_input("Dosage *", placeholder="e.g., 100mg, 1 tablet")
        time = st.time_input("Time", value=datetime.strptime("09:00", "%H:%M").time())
        frequency = st.selectbox("Frequency", [
            "Daily", "Twice daily", "Three times daily", 
            "Every other day", "Weekly", "As needed"
        ])
        notes = st.text_area("Notes (Optional)", placeholder="e.g., Take with food")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Add Medicine", type="primary", 
                                            use_container_width=True)
        with col2:
            cancelled = st.form_submit_button("Cancel", use_container_width=True)
        
        if submitted:
            if name.strip() and dosage.strip():
                medicine = {
                    'id': str(datetime.now().timestamp()),
                    'name': name.strip(),
                    'dosage': dosage.strip(),
                    'time': time.strftime("%H:%M"),
                    'frequency': frequency,
                    'notes': notes.strip()
                }
                st.session_state.medicines.append(medicine)
                st.success("✅ Medicine added successfully!")
                st.balloons()
                navigate_to('home')
            else:
                st.error("Please fill in medicine name and dosage")
        
        if cancelled:
            navigate_to('home')

# Edit Medicine Screen
def edit_medicine_screen():
    if not st.session_state.editing_medicine:
        navigate_to('home')
        return
    
    medicine = st.session_state.editing_medicine
    
    if st.button("⬅️ Back to Home", use_container_width=True):
        st.session_state.editing_medicine = None
        navigate_to('home')
    
    st.markdown("# ✏️ Edit Medicine")
    
    with st.form("edit_medicine_form"):
        name = st.text_input("Medicine Name *", value=medicine['name'])
        dosage = st.text_input("Dosage *", value=medicine['dosage'])
        time_obj = datetime.strptime(medicine['time'], "%H:%M").time()
        time = st.time_input("Time", value=time_obj)
        frequency = st.selectbox("Frequency", [
            "Daily", "Twice daily", "Three times daily", 
            "Every other day", "Weekly", "As needed"
        ], index=["Daily", "Twice daily", "Three times daily", 
                 "Every other day", "Weekly", "As needed"].index(medicine['frequency']))
        notes = st.text_area("Notes (Optional)", value=medicine.get('notes', ''))
        
        col1, col2, col3 = st.columns(3)
        with col1:
            updated = st.form_submit_button("Update", type="primary", 
                                          use_container_width=True)
        with col2:
            deleted = st.form_submit_button("Delete", use_container_width=True)
        with col3:
            cancelled = st.form_submit_button("Cancel", use_container_width=True)
        
        if updated:
            if name.strip() and dosage.strip():
                for i, med in enumerate(st.session_state.medicines):
                    if med['id'] == medicine['id']:
                        st.session_state.medicines[i] = {
                            'id': medicine['id'],
                            'name': name.strip(),
                            'dosage': dosage.strip(),
                            'time': time.strftime("%H:%M"),
                            'frequency': frequency,
                            'notes': notes.strip()
                        }
                        break
                st.success("✅ Medicine updated successfully!")
                st.session_state.editing_medicine = None
                navigate_to('home')
            else:
                st.error("Please fill in medicine name and dosage")
        
        if deleted:
            st.session_state.medicines = [m for m in st.session_state.medicines 
                                         if m['id'] != medicine['id']]
            st.success("🗑️ Medicine deleted")
            st.session_state.editing_medicine = None
            navigate_to('home')
        
        if cancelled:
            st.session_state.editing_medicine = None
            navigate_to('home')

# Adherence Screen
def adherence_screen():
    st.markdown("# 📈 Adherence Score")
    st.markdown("<p style='color: #6B7280;'>Your medication adherence over the last 7 days</p>", 
                unsafe_allow_html=True)
    
    adherence_score = calculate_adherence()
    
    # Determine color and message based on score
    if adherence_score >= 90:
        color = "#22C55E"
        bg_color = "#F0FDF4"
        border_color = "#86EFAC"
        emoji = "🌟"
        title = "Excellent!"
        message = "You're doing a great job staying on track with your medications."
    elif adherence_score >= 70:
        color = "#EAB308"
        bg_color = "#FEFCE8"
        border_color = "#FDE047"
        emoji = "👍"
        title = "Good Progress"
        message = "You're making good progress. Try to maintain consistency."
    else:
        color = "#F97316"
        bg_color = "#FFF7ED"
        border_color = "#FDBA74"
        emoji = "💪"
        title = "Keep Trying"
        message = "Don't worry! Every day is a new chance to improve your routine."
    
    # Progress circle
    st.markdown(f"""
    <div class="medicine-card" style="text-align: center; padding: 2rem;">
        <div class="progress-circle" style="background: conic-gradient({color} {adherence_score}%, #E5E7EB 0); position: relative;">
            <div style="position: absolute; background: white; width: 160px; height: 160px; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                <span style="font-size: 3rem; color: {color}; font-weight: bold;">{adherence_score}%</span>
                <span style="color: #6B7280; font-size: 0.875rem;">Adherence</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Feedback message
    st.markdown(f"""
    <div style="background: {bg_color}; border: 2px solid {border_color}; border-radius: 24px; padding: 1.5rem; margin: 1.5rem 0;">
        <div style="display: flex; gap: 1rem; align-items: start;">
            <span style="font-size: 2.5rem;">{emoji}</span>
            <div>
                <h3 style="color: {color}; margin-bottom: 0.5rem;">{title}</h3>
                <p style="color: #374151; margin: 0;">{message}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Statistics
    total_taken = sum(1 for log in st.session_state.logs if log['taken'])
    expected_doses = len(st.session_state.medicines) * 7
    
    st.markdown(f"""
    <div class="medicine-card">
        <h3 style="margin-bottom: 1rem;">7-Day Statistics</h3>
        <div style="display: flex; flex-direction: column; gap: 1rem;">
            <div style="background: #EFF6FF; padding: 1rem; border-radius: 16px; display: flex; justify-content: space-between;">
                <span style="color: #374151;">Total Medicines</span>
                <span style="color: #1E3A8A; font-weight: bold;">{len(st.session_state.medicines)}</span>
            </div>
            <div style="background: #F0FDF4; padding: 1rem; border-radius: 16px; display: flex; justify-content: space-between;">
                <span style="color: #374151;">Doses Taken</span>
                <span style="color: #16A34A; font-weight: bold;">{total_taken}</span>
            </div>
            <div style="background: #F9FAFB; padding: 1rem; border-radius: 16px; display: flex; justify-content: space-between;">
                <span style="color: #374151;">Expected Doses</span>
                <span style="color: #1F2937; font-weight: bold;">{expected_doses}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Perfect week badge
    if adherence_score == 100:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #FCD34D 0%, #F59E0B 100%); border-radius: 24px; padding: 1.5rem; text-align: center; margin-top: 1.5rem;">
            <div style="font-size: 4rem; margin-bottom: 0.5rem;">🏆</div>
            <h3 style="color: white; margin-bottom: 0.5rem;">Perfect Week!</h3>
            <p style="color: white; font-size: 0.875rem; margin: 0;">You took all your medicines on time this week!</p>
        </div>
        """, unsafe_allow_html=True)

# Report Screen
def report_screen():
    st.markdown("# 📊 7-Day Report")
    st.markdown("<p style='color: #6B7280;'>Your medication history at a glance</p>", 
                unsafe_allow_html=True)
    
    # Export button
    if st.button("📥 Export to CSV", type="primary", use_container_width=True, 
                disabled=len(st.session_state.medicines) == 0):
        if st.session_state.medicines:
            # Generate last 7 days
            last_7_days = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') 
                          for i in range(7)]
            last_7_days.reverse()
            
            # Create CSV
            csv_data = []
            for medicine in st.session_state.medicines:
                row = {
                    'Medicine Name': medicine['name'],
                    'Dosage': medicine['dosage'],
                    'Time': medicine['time']
                }
                for day in last_7_days:
                    day_name = datetime.strptime(day, '%Y-%m-%d').strftime('%a %d')
                    taken = any(
                        log['medicine_id'] == medicine['id'] and 
                        log['date'] == day and 
                        log['taken']
                        for log in st.session_state.logs
                    )
                    row[day_name] = 'Taken' if taken else 'Missed'
                csv_data.append(row)
            
            df = pd.DataFrame(csv_data)
            csv = df.to_csv(index=False)
            
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"medtimer-report-{get_today()}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    if not st.session_state.medicines:
        st.markdown("""
        <div class="medicine-card" style="text-align: center; padding: 3rem 1.5rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📅</div>
            <p style="color: #6B7280; font-size: 1.1rem; margin-bottom: 0.5rem;">No medicines to show</p>
            <p style="color: #9CA3AF; font-size: 0.9rem;">Add medicines to see your history</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Generate report table
        last_7_days = [(datetime.now() - timedelta(days=i)) for i in range(7)]
        last_7_days.reverse()
        
        # Create table HTML
        table_html = '<div class="medicine-card" style="overflow-x: auto; padding: 0;">'
        table_html += '<table style="width: 100%; border-collapse: collapse;">'
        
        # Header
        table_html += '<tr style="background: #DBEAFE; border-bottom: 2px solid #93C5FD;">'
        table_html += '<th style="padding: 1rem; text-align: left; color: #1E3A8A;">Medicine</th>'
        for day in last_7_days:
            day_name = day.strftime('%a')
            day_num = day.strftime('%d')
            table_html += f'<th style="padding: 1rem; text-align: center; color: #1E3A8A;"><div>{day_name}</div><div style="font-size: 0.75rem; color: #1E40AF;">{day_num}</div></th>'
        table_html += '</tr>'
        
        # Rows
        for idx, medicine in enumerate(st.session_state.medicines):
            bg = '#F9FAFB' if idx % 2 == 0 else 'white'
            table_html += f'<tr style="background: {bg}; border-bottom: 1px solid #E5E7EB;">'
            table_html += f'<td style="padding: 1rem;"><div style="color: #1F2937; font-weight: 500;">{medicine["name"]}</div><div style="color: #6B7280; font-size: 0.75rem;">{medicine["dosage"]}</div></td>'
            
            for day in last_7_days:
                day_str = day.strftime('%Y-%m-%d')
                taken = any(
                    log['medicine_id'] == medicine['id'] and 
                    log['date'] == day_str and 
                    log['taken']
                    for log in st.session_state.logs
                )
                icon = '✅' if taken else '❌'
                color = '#22C55E' if taken else '#D1D5DB'
                table_html += f'<td style="padding: 1rem; text-align: center;"><span style="font-size: 1.5rem;">{icon}</span></td>'
            
            table_html += '</tr>'
        
        # Footer
        total_taken = sum(1 for log in st.session_state.logs if log['taken'])
        table_html += f'''
        <tr style="background: #EFF6FF; border-top: 2px solid #93C5FD;">
            <td colspan="8" style="padding: 1rem;">
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; text-align: center;">
                    <div>
                        <p style="color: #6B7280; font-size: 0.875rem; margin-bottom: 0.25rem;">Total Medicines</p>
                        <p style="color: #1E3A8A; font-weight: bold; margin: 0;">{len(st.session_state.medicines)}</p>
                    </div>
                    <div>
                        <p style="color: #6B7280; font-size: 0.875rem; margin-bottom: 0.25rem;">Days Tracked</p>
                        <p style="color: #1E3A8A; font-weight: bold; margin: 0;">7</p>
                    </div>
                    <div>
                        <p style="color: #6B7280; font-size: 0.875rem; margin-bottom: 0.25rem;">Total Taken</p>
                        <p style="color: #16A34A; font-weight: bold; margin: 0;">{total_taken}</p>
                    </div>
                </div>
            </td>
        </tr>
        '''
        
        table_html += '</table></div>'
        
        st.markdown(table_html, unsafe_allow_html=True)
        
        # Legend
        st.markdown("""
        <div class="medicine-card" style="margin-top: 1.5rem;">
            <h3 style="margin-bottom: 1rem;">Legend</h3>
            <div style="display: flex; flex-direction: column; gap: 0.75rem;">
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <span style="font-size: 1.5rem;">✅</span>
                    <span style="color: #374151;">Medicine taken</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <span style="font-size: 1.5rem;">❌</span>
                    <span style="color: #374151;">Medicine not taken</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Bottom Navigation
def bottom_nav():
    nav_items = [
        {'id': 'home', 'label': 'Home', 'icon': '🏠'},
        {'id': 'add', 'label': 'Add', 'icon': '➕'},
        {'id': 'report', 'label': 'Report', 'icon': '📊'},
        {'id': 'adherence', 'label': 'Score', 'icon': '📈'},
    ]
    
    st.markdown('<div style="height: 5rem;"></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="bottom-nav"><div style="max-width: 450px; margin: 0 auto;"><div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.5rem;">', unsafe_allow_html=True)
    
    cols = st.columns(4)
    for i, item in enumerate(nav_items):
        with cols[i]:
            is_active = st.session_state.current_screen == item['id']
            button_style = """
                background: #3B82F6; 
                color: white; 
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            """ if is_active else """
                background: transparent; 
                color: #6B7280;
            """
            
            if st.button(
                f"{item['icon']}\n{item['label']}", 
                key=f"nav_{item['id']}", 
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                navigate_to(item['id'])
    
    st.markdown('</div></div></div>', unsafe_allow_html=True)

# Main app logic
def main():
    # Display current screen
    if st.session_state.current_screen == 'home':
        home_screen()
    elif st.session_state.current_screen == 'add':
        add_medicine_screen()
    elif st.session_state.current_screen == 'edit':
        edit_medicine_screen()
    elif st.session_state.current_screen == 'adherence':
        adherence_screen()
    elif st.session_state.current_screen == 'report':
        report_screen()
    
    # Bottom navigation
    bottom_nav()

if __name__ == "__main__":
    main()
