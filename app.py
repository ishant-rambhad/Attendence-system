# # app.py
# from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from datetime import datetime, timedelta
# import os
# import cv2
# import numpy as np
# import face_recognition
# import bcrypt
# import base64
# from flask import jsonify
# from werkzeug.utils import secure_filename

# app = Flask(__name__)
# app.secret_key = 'sambhavai_attendance_system'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['UPLOAD_FOLDER'] = 'static/faces'
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# # Ensure the upload folder exists
# os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# db = SQLAlchemy(app)


# from flask_wtf import FlaskForm
# from wtforms import StringField, PasswordField, SubmitField
# from wtforms.validators import DataRequired

# # Create Login Form
# class LoginForm(FlaskForm):
#     username = StringField('Username', validators=[DataRequired()])
#     password = PasswordField('Password', validators=[DataRequired()])
#     submit = SubmitField('Login')
# # Database Models
# class Admin(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(100), unique=True, nullable=False)
#     password = db.Column(db.String(100), nullable=False)

# class EmployeeForm(FlaskForm):
#     name = StringField('Name', validators=[DataRequired()])
#     employee_id = StringField('Employee ID', validators=[DataRequired()])
#     face_image = FileField('Face Image', validators=[DataRequired()])
#     submit = SubmitField('Add Employee')

# class Employee(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     emp_id = db.Column(db.String(20), unique=True, nullable=False)
#     name = db.Column(db.String(100), nullable=False)
#     face_encoding = db.Column(db.Text, nullable=True)
#     face_image_path = db.Column(db.String(200), nullable=True)
#     created_at = db.Column(db.DateTime, default=datetime.now)

# class Attendance(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     emp_id = db.Column(db.String(20), nullable=False)
#     date = db.Column(db.Date, nullable=False)
#     check_in = db.Column(db.DateTime, nullable=True)
#     check_out = db.Column(db.DateTime, nullable=True)
#     status = db.Column(db.String(20), default='Pending')  # 'Full Day', 'Half Day', 'Pending'
#     working_hours = db.Column(db.Float, default=0.0)

# # Create tables
# with app.app_context():
#     db.create_all()
    
#     # Check if admin exists, if not create default admin
#     admin = Admin.query.filter_by(username='HR@sambhavai.com').first()
#     if not admin:
#         hashed_password = bcrypt.hashpw('Shraddhaji@9087654'.encode('utf-8'), bcrypt.gensalt())
#         new_admin = Admin(username='HR@sambhavai.com', password=hashed_password.decode('utf-8'))
#         db.session.add(new_admin)
#         db.session.commit()
#         print("Default admin created")

# # Helper functions
# def encode_face(image_path):
#     image = face_recognition.load_image_file(image_path)
#     face_locations = face_recognition.face_locations(image)
    
#     if not face_locations:
#         return None
    
#     face_encoding = face_recognition.face_encodings(image, face_locations)[0]
#     return base64.b64encode(face_encoding.tobytes()).decode('utf-8')

# def decode_face_encoding(encoding_str):
#     encoding_bytes = base64.b64decode(encoding_str)
#     return np.frombuffer(encoding_bytes, dtype=np.float64)

# def recognize_face(face_encoding):
#     known_face_encodings = []
#     known_face_ids = []
    
#     employees = Employee.query.all()
#     for employee in employees:
#         if employee.face_encoding:
#             known_face_encodings.append(decode_face_encoding(employee.face_encoding))
#             known_face_ids.append(employee.emp_id)
    
#     if not known_face_encodings:
#         return None
    
#     # Compare with tolerance of 0.6
#     matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
#     face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
    
#     if not any(matches):
#         return None
    
#     best_match_index = np.argmin(face_distances)
#     if matches[best_match_index]:
#         return known_face_ids[best_match_index]
    
#     return None

# def calculate_working_hours(check_in, check_out):
#     if not check_in or not check_out:
#         return 0
    
#     delta = check_out - check_in
#     hours = delta.total_seconds() / 3600
#     return round(hours, 2)

# def update_attendance_status(attendance_id):
#     attendance = Attendance.query.get(attendance_id)
#     if attendance and attendance.check_in and attendance.check_out:
#         attendance.working_hours = calculate_working_hours(attendance.check_in, attendance.check_out)
#         if attendance.working_hours >= 8.0:
#             attendance.status = 'Full Day'
#         elif attendance.working_hours >= 7.0:
#             attendance.status = 'Half Day'
#         else:
#             attendance.status = 'Absent'
        
#         db.session.commit()

# # Routes
# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/process_face', methods=['POST'])
# def process_face():
#     if request.method == 'POST':
#         face_data = request.form.get('face_data')
#         if not face_data:
#             return jsonify({'success': False, 'message': 'No face data provided'})
        
#         # Convert base64 image to cv2 image
#         encoded_data = face_data.split(',')[1]
#         nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
#         img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
#         # Detect face
#         rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#         face_locations = face_recognition.face_locations(rgb_img)
        
#         if not face_locations:
#             return jsonify({'success': False, 'message': 'No face detected'})
        
#         face_encoding = face_recognition.face_encodings(rgb_img, face_locations)[0]
        
#         # Recognize face
#         emp_id = recognize_face(face_encoding)
        
#         if not emp_id:
#             return jsonify({'success': False, 'message': 'Face not recognized'})
        
#         # Get employee details
#         employee = Employee.query.filter_by(emp_id=emp_id).first()
        
#         if not employee:
#             return jsonify({'success': False, 'message': 'Employee not found'})
        
#         # Check for existing attendance today
#         today = datetime.now().date()
#         attendance = Attendance.query.filter_by(emp_id=emp_id, date=today).first()
        
#         # Prepare response
#         response = {
#             'success': True,
#             'employee': {
#                 'id': employee.emp_id,
#                 'name': employee.name
#             },
#             'attendance_status': 'new'
#         }
        
#         if attendance:
#             if attendance.check_in and not attendance.check_out:
#                 response['attendance_status'] = 'checked_in'
#             elif attendance.check_in and attendance.check_out:
#                 response['attendance_status'] = 'completed'
        
#         return jsonify(response)

# @app.route('/mark_attendance', methods=['POST'])
# def mark_attendance():
#     emp_id = request.form.get('emp_id')
#     action = request.form.get('action')  # 'check_in' or 'check_out'
    
#     if not emp_id or not action:
#         return jsonify({'success': False, 'message': 'Invalid request'})
    
#     # Check if employee exists
#     employee = Employee.query.filter_by(emp_id=emp_id).first()
#     if not employee:
#         return jsonify({'success': False, 'message': 'Employee not found'})
    
#     now = datetime.now()
#     today = now.date()
    
#     # Get or create attendance record for today
#     attendance = Attendance.query.filter_by(emp_id=emp_id, date=today).first()
    
#     if action == 'check_in':
#         if attendance and attendance.check_in:
#             return jsonify({'success': False, 'message': 'Already checked in today'})
        
#         if not attendance:
#             attendance = Attendance(emp_id=emp_id, date=today, check_in=now)
#             db.session.add(attendance)
#         else:
#             attendance.check_in = now
        
#         db.session.commit()
#         return jsonify({'success': True, 'message': 'Check-in successful'})
    
#     elif action == 'check_out':
#         if not attendance or not attendance.check_in:
#             return jsonify({'success': False, 'message': 'Need to check-in first'})
        
#         attendance.check_out = now
#         db.session.commit()
        
#         # Update status after check-out
#         update_attendance_status(attendance.id)
        
#         return jsonify({'success': True, 'message': 'Check-out successful'})
    
#     return jsonify({'success': False, 'message': 'Invalid action'})

# # @app.route('/admin_login', methods=['GET', 'POST'])
# # def admin_login():
# #     if request.method == 'POST':
# #         username = request.form.get('username')
# #         password = request.form.get('password')
        
# #         admin = Admin.query.filter_by(username=username).first()
        
# #         if admin and bcrypt.checkpw(password.encode('utf-8'), admin.password.encode('utf-8')):
# #             session['admin_logged_in'] = True
# #             return redirect(url_for('admin_dashboard'))
# #         else:
# #             flash('Invalid login credentials', 'danger')
    
# #     return render_template('admin_login.html')


# @app.route('/api/admin_registration', methods=['POST'])
# def admin_registration():
#     # Get JSON data from request
#     data = request.get_json()
    
#     if not data:
#         return jsonify({'success': False, 'message': 'No data provided'}), 400
    
#     # Extract username and password
#     username = data.get('username')
#     password = data.get('password')
    
#     # Validate input
#     if not username or not password:
#         return jsonify({'success': False, 'message': 'Username and password are required'}), 400
    
#     # Check if username already exists
#     existing_admin = Admin.query.filter_by(username=username).first()
#     if existing_admin:
#         return jsonify({'success': False, 'message': 'Username already exists'}), 409
    
#     # Hash the password and create new admin
#     hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
#     new_admin = Admin(username=username, password=hashed_password.decode('utf-8'))
    
#     try:
#         db.session.add(new_admin)
#         db.session.commit()
#         return jsonify({'success': True, 'message': 'Admin registered successfully'}), 201
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'success': False, 'message': f'Registration failed: {str(e)}'}), 500


# @app.route('/admin_login', methods=['GET', 'POST'])
# def admin_login():
#     form = LoginForm()
    
#     if form.validate_on_submit():
#         username = form.username.data
#         password = form.password.data
        
#         admin = Admin.query.filter_by(username=username).first()
        
#         if admin and bcrypt.checkpw(password.encode('utf-8'), admin.password.encode('utf-8')):
#             session['admin_logged_in'] = True
#             return redirect(url_for('admin_dashboard'))
#         else:
#             flash('Invalid login credentials', 'danger')
    
#     return render_template('admin_login.html', form=form)

# @app.route('/admin_dashboard')
# def admin_dashboard():
#     if not session.get('admin_logged_in'):
#         return redirect(url_for('admin_login'))
    
#     return render_template('admin_dashboard.html')

# @app.route('/admin_logout')
# def admin_logout():
#     session.pop('admin_logged_in', None)
#     return redirect(url_for('admin_login'))

# @app.route('/manage_employees')
# def manage_employees():
#     if not session.get('admin_logged_in'):
#         return redirect(url_for('admin_login'))
    
#     employees = Employee.query.all()
#     return render_template('manage_employees.html', employees=employees)

# # @app.route('/add_employee', methods=['GET', 'POST'])
# # def add_employee():
# #     if not session.get('admin_logged_in'):
# #         return redirect(url_for('admin_login'))
    
# #     if request.method == 'POST':
# #         emp_id = request.form.get('emp_id')
# #         name = request.form.get('name')
        
# #         # Check if employee ID already exists
# #         existing_employee = Employee.query.filter_by(emp_id=emp_id).first()
# #         if existing_employee:
# #             flash('Employee ID already exists', 'danger')
# #             return redirect(url_for('add_employee'))
        
# #         # Create new employee
# #         new_employee = Employee(emp_id=emp_id, name=name)
# #         db.session.add(new_employee)
# #         db.session.commit()
        
# #         flash('Employee added successfully', 'success')
# #         return redirect(url_for('capture_face', emp_id=emp_id))
    
# #     return render_template('add_employee.html')

# # Updated Add Employee Route
# @app.route('/add_employee', methods=['GET', 'POST'])
# def add_employee():
#     if not session.get('admin_logged_in'):
#         return redirect(url_for('admin_login'))
    
#     form = EmployeeForm()
#     if form.validate_on_submit():
#         emp_id = form.employee_id.data
#         name = form.name.data
#         face_image = form.face_image.data
        
#         # Check if employee ID already exists
#         existing_employee = Employee.query.filter_by(emp_id=emp_id).first()
#         if existing_employee:
#             flash('Employee ID already exists', 'danger')
#             return render_template('add_employee.html', form=form)
        
#         # Save the uploaded face image
#         filename = secure_filename(f"{emp_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg")
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         face_image.save(file_path)
        
#         # Generate face encoding
#         face_encoding = encode_face(file_path)
#         if not face_encoding:
#             flash('No face detected in the uploaded image', 'danger')
#             os.remove(file_path)  # Clean up if no face is detected
#             return render_template('add_employee.html', form=form)
        
#         # Create and save new employee
#         new_employee = Employee(
#             emp_id=emp_id,
#             name=name,
#             face_encoding=face_encoding,
#             face_image_path=os.path.join('faces', filename)
#         )
#         db.session.add(new_employee)
#         db.session.commit()
        
#         flash('Employee added successfully', 'success')
#         return redirect(url_for('manage_employees'))
    
#     return render_template('add_employee.html', form=form)

# @app.route('/capture_face/<emp_id>')
# def capture_face(emp_id):
#     if not session.get('admin_logged_in'):
#         return redirect(url_for('admin_login'))
    
#     employee = Employee.query.filter_by(emp_id=emp_id).first()
#     if not employee:
#         flash('Employee not found', 'danger')
#         return redirect(url_for('manage_employees'))
    
#     return render_template('capture_face.html', employee=employee)

# @app.route('/save_face', methods=['POST'])
# def save_face():
#     if not session.get('admin_logged_in'):
#         return jsonify({'success': False, 'message': 'Not authorized'})
    
#     emp_id = request.form.get('emp_id')
#     face_data = request.form.get('face_data')
    
#     if not emp_id or not face_data:
#         return jsonify({'success': False, 'message': 'Missing data'})
    
#     employee = Employee.query.filter_by(emp_id=emp_id).first()
#     if not employee:
#         return jsonify({'success': False, 'message': 'Employee not found'})
    
#     # Process and save face image
#     encoded_data = face_data.split(',')[1]
#     nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
#     img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
#     # Detect face
#     rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#     face_locations = face_recognition.face_locations(rgb_img)
    
#     if not face_locations:
#         return jsonify({'success': False, 'message': 'No face detected'})
    
#     # Save face image
#     filename = f"{emp_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
#     file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#     cv2.imwrite(file_path, img)
    
#     # Generate and store face encoding
#     face_encoding = face_recognition.face_encodings(rgb_img, face_locations)[0]
#     encoded_face = base64.b64encode(face_encoding.tobytes()).decode('utf-8')
    
#     # Update employee record
#     employee.face_encoding = encoded_face
#     employee.face_image_path = os.path.join('faces', filename)
#     db.session.commit()
    
#     return jsonify({'success': True, 'message': 'Face captured successfully'})

# @app.route('/view_attendance')
# def view_attendance():
#     if not session.get('admin_logged_in'):
#         return redirect(url_for('admin_login'))
    
#     month = request.args.get('month', datetime.now().month)
#     year = request.args.get('year', datetime.now().year)
    
#     try:
#         month = int(month)
#         year = int(year)
#     except ValueError:
#         month = datetime.now().month
#         year = datetime.now().year
    
#     # Get all employees
#     employees = Employee.query.all()
    
#     # Prepare attendance data for calendar view
#     attendance_data = {}
    
#     for employee in employees:
#         emp_id = employee.emp_id
#         attendance_data[emp_id] = {
#             'name': employee.name,
#             'days': {}
#         }
        
#         # Get attendance records for the month
#         start_date = datetime(year, month, 1).date()
#         if month == 12:
#             end_date = datetime(year + 1, 1, 1).date()
#         else:
#             end_date = datetime(year, month + 1, 1).date()
        
#         records = Attendance.query.filter(
#             Attendance.emp_id == emp_id,
#             Attendance.date >= start_date,
#             Attendance.date < end_date
#         ).all()
        
#         for record in records:
#             day = record.date.day
#             attendance_data[emp_id]['days'][day] = {
#                 'check_in': record.check_in.strftime('%H:%M') if record.check_in else None,
#                 'check_out': record.check_out.strftime('%H:%M') if record.check_out else None,
#                 'status': record.status,
#                 'working_hours': record.working_hours
#             }
    
#     # Calculate calendar data
#     first_day = datetime(year, month, 1)
#     last_day = (datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)) - timedelta(days=1)
#     days_in_month = last_day.day
#     first_weekday = first_day.weekday()  # Monday is 0
    
#     # Adjust for Sunday as the first day of the week
#     first_weekday = (first_weekday + 1) % 7  # Sunday is now 0
    
#     calendar_weeks = []
#     day = 1
#     for week in range(6):  # Maximum 6 weeks in a month
#         week_days = [None] * 7
#         for weekday in range(7):
#             if (week == 0 and weekday < first_weekday) or day > days_in_month:
#                 week_days[weekday] = None
#             else:
#                 week_days[weekday] = day
#                 day += 1
        
#         calendar_weeks.append(week_days)
#         if day > days_in_month:
#             break
    
#     # Get previous and next month/year
#     if month == 1:
#         prev_month, prev_year = 12, year - 1
#     else:
#         prev_month, prev_year = month - 1, year
    
#     if month == 12:
#         next_month, next_year = 1, year + 1
#     else:
#         next_month, next_year = month + 1, year
    
#     month_name = datetime(year, month, 1).strftime('%B')
    
#     return render_template(
#         'view_attendance.html',
#         employees=employees,
#         attendance_data=attendance_data,
#         calendar_weeks=calendar_weeks,
#         month=month,
#         year=year,
#         month_name=month_name,
#         prev_month=prev_month,
#         prev_year=prev_year,
#         next_month=next_month,
#         next_year=next_year
#     )

# @app.route('/employee_attendance/<emp_id>')
# def employee_attendance(emp_id):
#     if not session.get('admin_logged_in'):
#         return redirect(url_for('admin_login'))
    
#     employee = Employee.query.filter_by(emp_id=emp_id).first()
#     if not employee:
#         flash('Employee not found', 'danger')
#         return redirect(url_for('view_attendance'))
    
#     month = request.args.get('month', datetime.now().month)
#     year = request.args.get('year', datetime.now().year)
    
#     try:
#         month = int(month)
#         year = int(year)
#     except ValueError:
#         month = datetime.now().month
#         year = datetime.now().year
    
#     # Get attendance records for the month
#     start_date = datetime(year, month, 1).date()
#     if month == 12:
#         end_date = datetime(year + 1, 1, 1).date()
#     else:
#         end_date = datetime(year, month + 1, 1).date()
    
#     attendance_records = Attendance.query.filter(
#         Attendance.emp_id == emp_id,
#         Attendance.date >= start_date,
#         Attendance.date < end_date
#     ).order_by(Attendance.date).all()
    
#     month_name = datetime(year, month, 1).strftime('%B')
    
#     # Calculate stats
#     total_days = len(attendance_records)
#     full_days = sum(1 for record in attendance_records if record.status == 'Full Day')
#     half_days = sum(1 for record in attendance_records if record.status == 'Half Day')
#     absent_days = sum(1 for record in attendance_records if record.status == 'Absent')
    
#     # Get previous and next month/year
#     if month == 1:
#         prev_month, prev_year = 12, year - 1
#     else:
#         prev_month, prev_year = month - 1, year
    
#     if month == 12:
#         next_month, next_year = 1, year + 1
#     else:
#         next_month, next_year = month + 1, year
    
#     return render_template(
#         'employee_attendance.html',
#         employee=employee,
#         attendance_records=attendance_records,
#         month=month,
#         year=year,
#         month_name=month_name,
#         prev_month=prev_month,
#         prev_year=prev_year,
#         next_month=next_month,
#         next_year=next_year,
#         stats={
#             'total_days': total_days,
#             'full_days': full_days,
#             'half_days': half_days,
#             'absent_days': absent_days
#         }
#     )

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import cv2
import numpy as np
import face_recognition
import bcrypt
import base64
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.secret_key = 'sambhavai_attendance_system'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/faces'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# Forms
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class EmployeeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    employee_id = StringField('Employee ID', validators=[DataRequired()])
    face_image = FileField('Face Image', validators=[DataRequired()])
    submit = SubmitField('Add Employee')

# Database Models
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    face_encoding = db.Column(db.Text, nullable=True)
    face_image_path = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(20), nullable=False)
    date = db.Column(db.Date, nullable=False)
    check_in = db.Column(db.DateTime, nullable=True)
    check_out = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='Pending')  # 'Full Day', 'Half Day', 'Pending'
    working_hours = db.Column(db.Float, default=0.0)

# Create tables
with app.app_context():
    db.create_all()
    # Check if admin exists, if not create default admin
    admin = Admin.query.filter_by(username='HR@sambhavai.com').first()
    if not admin:
        hashed_password = bcrypt.hashpw('Shraddhaji@9087654'.encode('utf-8'), bcrypt.gensalt())
        new_admin = Admin(username='HR@sambhavai.com', password=hashed_password.decode('utf-8'))
        db.session.add(new_admin)
        db.session.commit()
        print("Default admin created")

# Helper functions
def encode_face(image_path):
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)
    if not face_locations:
        return None
    face_encoding = face_recognition.face_encodings(image, face_locations)[0]
    return base64.b64encode(face_encoding.tobytes()).decode('utf-8')

def decode_face_encoding(encoding_str):
    encoding_bytes = base64.b64decode(encoding_str)
    return np.frombuffer(encoding_bytes, dtype=np.float64)

def recognize_face(face_encoding):
    known_face_encodings = []
    known_face_ids = []
    employees = Employee.query.all()
    for employee in employees:
        if employee.face_encoding:
            known_face_encodings.append(decode_face_encoding(employee.face_encoding))
            known_face_ids.append(employee.emp_id)
    if not known_face_encodings:
        return None
    matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
    if not any(matches):
        return None
    best_match_index = np.argmin(face_distances)
    if matches[best_match_index]:
        return known_face_ids[best_match_index]
    return None

def calculate_working_hours(check_in, check_out):
    if not check_in or not check_out:
        return 0
    delta = check_out - check_in
    hours = delta.total_seconds() / 3600
    return round(hours, 2)

def update_attendance_status(attendance_id):
    attendance = Attendance.query.get(attendance_id)
    if attendance and attendance.check_in and attendance.check_out:
        attendance.working_hours = calculate_working_hours(attendance.check_in, attendance.check_out)
        if attendance.working_hours >= 8.0:
            attendance.status = 'Full Day'
        elif attendance.working_hours >= 7.0:
            attendance.status = 'Half Day'
        else:
            attendance.status = 'Absent'
        db.session.commit()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_face', methods=['POST'])
def process_face():
    if request.method == 'POST':
        face_data = request.form.get('face_data')
        if not face_data:
            return jsonify({'success': False, 'message': 'No face data provided'})
        
        encoded_data = face_data.split(',')[1]
        nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_img)
        
        if not face_locations:
            return jsonify({'success': False, 'message': 'No face detected'})
        
        face_encoding = face_recognition.face_encodings(rgb_img, face_locations)[0]
        
        emp_id = recognize_face(face_encoding)
        
        if not emp_id:
            return jsonify({'success': False, 'message': 'Face not recognized'})
        
        employee = Employee.query.filter_by(emp_id=emp_id).first()
        
        if not employee:
            return jsonify({'success': False, 'message': 'Employee not found'})
        
        today = datetime.now().date()
        attendance = Attendance.query.filter_by(emp_id=emp_id, date=today).first()
        
        response = {
            'success': True,
            'employee': {
                'id': employee.emp_id,
                'name': employee.name
            },
            'attendance_status': 'new'
        }
        
        if attendance:
            if attendance.check_in and not attendance.check_out:
                response['attendance_status'] = 'checked_in'
            elif attendance.check_in and attendance.check_out:
                response['attendance_status'] = 'completed'
        
        return jsonify(response)

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    emp_id = request.form.get('emp_id')
    action = request.form.get('action')
    
    if not emp_id or not action:
        return jsonify({'success': False, 'message': 'Invalid request'})
    
    employee = Employee.query.filter_by(emp_id=emp_id).first()
    if not employee:
        return jsonify({'success': False, 'message': 'Employee not found'})
    
    now = datetime.now()
    today = now.date()
    
    attendance = Attendance.query.filter_by(emp_id=emp_id, date=today).first()
    
    if action == 'check_in':
        if attendance and attendance.check_in:
            return jsonify({'success': False, 'message': 'Already checked in today'})
        
        if not attendance:
            attendance = Attendance(emp_id=emp_id, date=today, check_in=now)
            db.session.add(attendance)
        else:
            attendance.check_in = now
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Check-in successful'})
    
    elif action == 'check_out':
        if not attendance or not attendance.check_in:
            return jsonify({'success': False, 'message': 'Need to check-in first'})
        
        attendance.check_out = now
        db.session.commit()
        
        update_attendance_status(attendance.id)
        
        return jsonify({'success': True, 'message': 'Check-out successful'})
    
    return jsonify({'success': False, 'message': 'Invalid action'})

@app.route('/api/admin_registration', methods=['POST'])
def admin_registration():
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password are required'}), 400
    
    existing_admin = Admin.query.filter_by(username=username).first()
    if existing_admin:
        return jsonify({'success': False, 'message': 'Username already exists'}), 409
    
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    new_admin = Admin(username=username, password=hashed_password.decode('utf-8'))
    
    try:
        db.session.add(new_admin)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Admin registered successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Registration failed: {str(e)}'}), 500

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and bcrypt.checkpw(password.encode('utf-8'), admin.password.encode('utf-8')):
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid login credentials', 'danger')
    
    return render_template('admin_login.html', form=form)

@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html')

@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/manage_employees')
def manage_employees():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    employees = Employee.query.all()
    return render_template('manage_employees.html', employees=employees)

# @app.route('/add_employee', methods=['GET', 'POST'])
# def add_employee():
#     if not session.get('admin_logged_in'):
#         return redirect(url_for('admin_login'))
    
#     form = EmployeeForm()
#     if form.validate_on_submit():
#         emp_id = form.employee_id.data
#         name = form.name.data
#         face_image = form.face_image.data
        
#         existing_employee = Employee.query.filter_by(emp_id=emp_id).first()
#         if existing_employee:
#             flash('Employee ID already exists', 'danger')
#             return render_template('add_employee.html', form=form)
        
#         filename = secure_filename(f"{emp_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg")
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         face_image.save(file_path)
        
#         face_encoding = encode_face(file_path)
#         if not face_encoding:
#             flash('No face detected in the uploaded image', 'danger')
#             os.remove(file_path)
#             return render_template('add_employee.html', form=form)
        
#         new_employee = Employee(
#             emp_id=emp_id,
#             name=name,
#             face_encoding=face_encoding,
#             face_image_path=os.path.join('faces', filename)
#         )
#         db.session.add(new_employee)
#         db.session.commit()
        
#         flash('Employee added successfully', 'success')
#         return redirect(url_for('manage_employees'))
    
#     return render_template('add_employee.html', form=form)

import os
import base64
import re
import numpy as np
import cv2
from datetime import datetime
from flask import render_template, redirect, url_for, flash, session, request
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from io import BytesIO

@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    form = EmployeeForm()
    # Remove the face_image field validation since we're capturing it directly
    form.face_image = None
    
    if request.method == 'POST':
        if form.validate():
            emp_id = form.employee_id.data
            name = form.name.data
            captured_image_data = request.form.get('captured_image')
            
            # Check if image data exists
            if not captured_image_data or captured_image_data == '':
                flash('No image captured. Please capture an employee face image.', 'danger')
                return render_template('add_employee.html', form=form)
            
            # Check if employee ID already exists
            existing_employee = Employee.query.filter_by(emp_id=emp_id).first()
            if existing_employee:
                flash('Employee ID already exists', 'danger')
                return render_template('add_employee.html', form=form)
            
            try:
                # Extract the base64 data
                image_data = re.sub('^data:image/.+;base64,', '', captured_image_data)
                image_bytes = base64.b64decode(image_data)
                
                # Create a file-like object
                image_file = BytesIO(image_bytes)
                
                # Generate unique filename
                filename = secure_filename(f"{emp_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg")
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # Save the image to file
                with open(file_path, 'wb') as f:
                    f.write(image_bytes)
                
                # Verify face detection in the saved image
                face_encoding = encode_face(file_path)
                if not face_encoding:
                    flash('No face detected in the captured image', 'danger')
                    os.remove(file_path)
                    return render_template('add_employee.html', form=form)
                
                # Save employee to database
                new_employee = Employee(
                    emp_id=emp_id,
                    name=name,
                    face_encoding=face_encoding,
                    face_image_path=os.path.join('faces', filename)
                )
                db.session.add(new_employee)
                db.session.commit()
                
                flash('Employee added successfully', 'success')
                return redirect(url_for('manage_employees'))
                
            except Exception as e:
                flash(f'Error processing image: {str(e)}', 'danger')
                return render_template('add_employee.html', form=form)
        else:
            # Form validation failed
            return render_template('add_employee.html', form=form)
    
    return render_template('add_employee.html', form=form)

@app.route('/capture_face/<emp_id>')
def capture_face(emp_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    employee = Employee.query.filter_by(emp_id=emp_id).first()
    if not employee:
        flash('Employee not found', 'danger')
        return redirect(url_for('manage_employees'))
    
    return render_template('capture_face.html', employee=employee)

@app.route('/save_face', methods=['POST'])
def save_face():
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Not authorized'})
    
    emp_id = request.form.get('emp_id')
    face_data = request.form.get('face_data')
    
    if not emp_id or not face_data:
        return jsonify({'success': False, 'message': 'Missing data'})
    
    employee = Employee.query.filter_by(emp_id=emp_id).first()
    if not employee:
        return jsonify({'success': False, 'message': 'Employee not found'})
    
    encoded_data = face_data.split(',')[1]
    nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_img)
    
    if not face_locations:
        return jsonify({'success': False, 'message': 'No face detected'})
    
    filename = f"{emp_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    cv2.imwrite(file_path, img)
    
    face_encoding = face_recognition.face_encodings(rgb_img, face_locations)[0]
    encoded_face = base64.b64encode(face_encoding.tobytes()).decode('utf-8')
    
    employee.face_encoding = encoded_face
    employee.face_image_path = os.path.join('faces', filename)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Face captured successfully'})

@app.route('/view_attendance')
def view_attendance():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    month = request.args.get('month', datetime.now().month)
    year = request.args.get('year', datetime.now().year)
    
    try:
        month = int(month)
        year = int(year)
    except ValueError:
        month = datetime.now().month
        year = datetime.now().year
    
    employees = Employee.query.all()
    
    attendance_data = {}
    for employee in employees:
        emp_id = employee.emp_id
        attendance_data[emp_id] = {
            'name': employee.name,
            'days': {}
        }
        
        start_date = datetime(year, month, 1).date()
        if month == 12:
            end_date = datetime(year + 1, 1, 1).date()
        else:
            end_date = datetime(year, month + 1, 1).date()
        
        records = Attendance.query.filter(
            Attendance.emp_id == emp_id,
            Attendance.date >= start_date,
            Attendance.date < end_date
        ).all()
        
        for record in records:
            day = record.date.day
            attendance_data[emp_id]['days'][day] = {
                'check_in': record.check_in.strftime('%H:%M') if record.check_in else None,
                'check_out': record.check_out.strftime('%H:%M') if record.check_out else None,
                'status': record.status,
                'working_hours': record.working_hours
            }
    
    first_day = datetime(year, month, 1)
    last_day = (datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)) - timedelta(days=1)
    days_in_month = last_day.day
    first_weekday = first_day.weekday()
    first_weekday = (first_weekday + 1) % 7
    
    calendar_weeks = []
    day = 1
    for week in range(6):
        week_days = [None] * 7
        for weekday in range(7):
            if (week == 0 and weekday < first_weekday) or day > days_in_month:
                week_days[weekday] = None
            else:
                week_days[weekday] = day
                day += 1
        calendar_weeks.append(week_days)
        if day > days_in_month:
            break
    
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year
    
    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year
    
    month_name = datetime(year, month, 1).strftime('%B')
    
    return render_template(
        'view_attendance.html',
        employees=employees,
        attendance_data=attendance_data,
        calendar_weeks=calendar_weeks,
        month=month,
        year=year,
        month_name=month_name,
        prev_month=prev_month,
        prev_year=prev_year,
        next_month=next_month,
        next_year=next_year
    )

@app.route('/employee_attendance/<emp_id>')
def employee_attendance(emp_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    employee = Employee.query.filter_by(emp_id=emp_id).first()
    if not employee:
        flash('Employee not found', 'danger')
        return redirect(url_for('view_attendance'))
    
    month = request.args.get('month', datetime.now().month)
    year = request.args.get('year', datetime.now().year)
    
    try:
        month = int(month)
        year = int(year)
    except ValueError:
        month = datetime.now().month
        year = datetime.now().year
    
    start_date = datetime(year, month, 1).date()
    if month == 12:
        end_date = datetime(year + 1, 1, 1).date()
    else:
        end_date = datetime(year, month + 1, 1).date()
    
    attendance_records = Attendance.query.filter(
        Attendance.emp_id == emp_id,
        Attendance.date >= start_date,
        Attendance.date < end_date
    ).order_by(Attendance.date).all()
    
    month_name = datetime(year, month, 1).strftime('%B')
    
    total_days = len(attendance_records)
    full_days = sum(1 for record in attendance_records if record.status == 'Full Day')
    half_days = sum(1 for record in attendance_records if record.status == 'Half Day')
    absent_days = sum(1 for record in attendance_records if record.status == 'Absent')
    
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year
    
    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year
    
    return render_template(
        'employee_attendance.html',
        employee=employee,
        attendance_records=attendance_records,
        month=month,
        year=year,
        month_name=month_name,
        prev_month=prev_month,
        prev_year=prev_year,
        next_month=next_month,
        next_year=next_year,
        stats={
            'total_days': total_days,
            'full_days': full_days,
            'half_days': half_days,
            'absent_days': absent_days
        }
    )

if __name__ == '__main__':
    app.run(debug=True)