from flask import Flask, render_template, request, redirect, url_for, flash
from flaskext.mysql import MySQL
import pymysql, os, re
import time
from datetime import datetime
from werkzeug.utils import secure_filename

#UPLOAD_FOLDER = 'F:\IDE\Xamp\htdocs\Blood Aid Bank Jashore\images'
UPLOAD_FOLDER = os.path.join('images', 'profile')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
 
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.urandom(24)
  
mysql = MySQL()
   
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'bloodaidbankjashore'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)

@app.route('/')
@app.route('/index')
def index():
    conn = mysql.connect()
    mycur = conn.cursor(pymysql.cursors.DictCursor)
    mycur.execute('SELECT * FROM notice ORDER BY id DESC LIMIT 10')
    link = mycur.fetchall()
    mycur.close()
    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'shovon.jpg')
    print(full_filename)
    return render_template('index.html', fblink = link, user_image = full_filename)
    #return render_template('index.html')

#Collect Donor
@app.route('/donorform', methods=['GET', 'POST'])
def add_donor():
    conn = mysql.connect()
    mycur = conn.cursor(pymysql.cursors.DictCursor)
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        blood = request.form['blood']
        institute = request.form['institute']
        upazila = request.form['location']
        zilla = request.form['zilla']
        mycur.execute("INSERT INTO donor(name, phone, bloodgroup, institute, upazila, district, donationDate) VALUES (%s,%s,%s,%s,%s,%s,%s)", (name, phone, blood, institute, upazila, zilla,'19000101'))
        conn.commit()
        mycur.close()
    return render_template('donorform.html')

#Show Donor
@app.route('/donorlist', methods=['GET', 'POST'])
def show_donor():
    conn = mysql.connect()
    mycur = conn.cursor(pymysql.cursors.DictCursor)
    mycur.execute("SELECT * FROM donor ORDER BY bloodgroup ASC")
    data = mycur.fetchall()
    mycur.close()
    return render_template('donorlist.html', donorlist = data)

#Search Donor
@app.route('/searched', methods=['GET', 'POST'])
def search_donor():
    if request.method == 'POST':
        conn = mysql.connect()
        mycur = conn.cursor(pymysql.cursors.DictCursor)
        group = request.form['blood']
        mycur.execute("SELECT * FROM donor")
        data = mycur.fetchall()
        blood = []
        for x in range(len(data)):
            if data[x]['bloodgroup']==group:
                blood.append(data[x])
        mycur.close()
        return render_template('donorlist.html', donorlist = blood)

#Blood Booking for Future
@app.route('/booking', methods=['GET', 'POST'])
def add_booking():
    conn = mysql.connect()
    mycur = conn.cursor(pymysql.cursors.DictCursor)
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        month = request.form['time']
        blood = request.form['blood']
        city = request.form['city']
        mycur.execute("INSERT INTO booking(name, phone, month, bloodgroup, city, requestStatus) VALUES (%s,%s,%s,%s,%s,%s)", (name, phone, month, blood, city, 'Pending'))
        conn.commit()
        mycur.close()
    return render_template('booking.html')


#Show Blood Booking List
@app.route('/bookinglist', methods=['GET', 'POST'])
def show_bookinglist():
    conn = mysql.connect()
    mycur = conn.cursor(pymysql.cursors.DictCursor)
    mycur.execute('SELECT * FROM booking ORDER BY month ASC')
    data = mycur.fetchall()
    mycur.close()
    return render_template('bookinglist.html', bookinglist = data)

#Update Blood Booking List
@app.route('/updated', methods=['GET', 'POST'])
def update_status():
    if request.method == 'POST':
        change_id = request.form['id']
        conn = mysql.connect()
        mycur = conn.cursor(pymysql.cursors.DictCursor)
        mycur.execute("UPDATE booking SET requestStatus = 'Available' WHERE id = {0}".format(change_id))
        conn.commit()
        mycur.execute('SELECT*FROM booking ORDER BY month ASC')
        data = mycur.fetchall()
        mycur.close()
        return render_template('bookinglist.html', bookinglist = data)
    return render_template('bookinglist.html', bookinglist = data)
#Dashboard
#Create Admin
@app.route("/adminCreation", methods=['GET','POST'])
def create_admin():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        conn = mysql.connect()
        mycur = conn.cursor(pymysql.cursors.DictCursor)
        mycur.execute("INSERT INTO admin(email, name, pass) VALUES(%s, %s, %s)",(email,name,password))
        conn.commit()
        mycur.close()
        return render_template('admin_dashboard.html')

#Login as Admin
@app.route('/dashboard', methods=['POST','GET'])
def login_admin():
    if request.method == 'POST':
        email = request.form['email']
        conn = mysql.connect()
        mycur = conn.cursor(pymysql.cursors.DictCursor)
        mycur.execute('SELECT * FROM admin')
        admin_email = mycur.fetchall()
        check = False
        for x in range(len(admin_email)):
            if admin_email[x]['email'] == email:
                check = True
                return render_template('layout2.html')
        if not check:
            index()

    return render_template('layout2.html')

#Add notice from facebook
@app.route("/noitce", methods=['GET','POST'])
def add_notice():
    conn = mysql.connect()
    mycur = conn.cursor(pymysql.cursors.DictCursor)
    if request.method == 'POST':
        link = request.form['fblink']
        date = request.form['date']
        mycur.execute("INSERT INTO notice(fblink, date) VALUES(%s, %s)",(link, date))
        conn.commit()
        mycur.execute('SELECT * FROM notice ORDER BY id DESC LIMIT 10')
        link = mycur.fetchall()
        return render_template('index.html', fblink = link)

#Show booking blood information in admin panel
@app.route("/bookinglist_dashboard", methods=['GET','POST'])
def show_bookinglist_dashboard():
    conn = mysql.connect()
    mycur = conn.cursor(pymysql.cursors.DictCursor)
    mycur.execute('SELECT * FROM booking ORDER BY month ASC')
    data = mycur.fetchall()
    mycur.close()
    return render_template('bookinglistAdmin.html', bookinglist = data)

#Show donorlist information in admin panel
@app.route('/donorlist_dashboard', methods=['GET', 'POST'])
def show_donor_dashboard():
    conn = mysql.connect()
    mycur = conn.cursor(pymysql.cursors.DictCursor)
    mycur.execute("SELECT * FROM donor ORDER BY donationDate ASC")
    data = mycur.fetchall()
    for x in range(len(data)):
        data[x]['donationDate'] = data[x]['donationDate'][:4]+'-'+data[x]['donationDate'][4:6]+'-'+data[x]['donationDate'][6:]
    mycur.close()
    return render_template('donorlistAdmin.html', donorlist = data)

#Search donor information in admin panel
@app.route('/searched_donor_dashboard', methods=['GET', 'POST'])
def search_donor_dashboard():
    if request.method == 'POST':
        conn = mysql.connect()
        mycur = conn.cursor(pymysql.cursors.DictCursor)
        group = request.form['blood']
        location = request.form['location']
        mycur.execute("SELECT * FROM donor")
        data = mycur.fetchall()
        blood = []
        for x in range(len(data)):
            if data[x]['bloodgroup']==group and data[x]['district']==location:
                blood.append(data[x])
        for x in range(len(blood)):
            blood[x]['donationDate'] = blood[x]['donationDate'][:4]+'-'+blood[x]['donationDate'][4:6]+'-'+blood[x]['donationDate'][6:]
        mycur.close()
        return render_template('donorlistAdmin.html', donorlist = blood)

#Delete booking in admin panel
@app.route('/delete', methods=['POST'])
def delete_entry():
    conn = mysql.connect()
    mycur = conn.cursor(pymysql.cursors.DictCursor)
    if request.method == 'POST':
        #print([request.form['entry_id']])
        id = request.form['entry_id']
        mycur.execute("DELETE FROM booking WHERE id = {0}".format(id))
        conn.commit()
        mycur.execute("SELECT * FROM booking")
        data = mycur.fetchall()
        #print(data)
        mycur.close()
        return render_template('bookinglistAdmin.html', bookinglist = data)

#Edit donation date in admin panel
@app.route('/edit', methods=['POST'])
def edit_entry():
    conn = mysql.connect()
    mycur = conn.cursor(pymysql.cursors.DictCursor)
    if request.method == 'POST':
        id = request.form['edit_id']
        month = request.form['month']
        month = re.split("\-", month)
        month = ''.join(month)
        mycur.execute("UPDATE donor SET donationDate = {0} WHERE id = {1}".format(month, id))
        conn.commit()
        mycur.execute("SELECT * FROM donor ORDER BY donationDate ASC")
        data = mycur.fetchall()
        for x in range(len(data)):
            data[x]['donationDate'] = data[x]['donationDate'][:4]+'-'+data[x]['donationDate'][4:6]+'-'+data[x]['donationDate'][6:]
        mycur.close()
        return render_template('donorlistAdmin.html', donorlist = data)


@app.route("/admin")
def enter_admin():
    return render_template('admin.html')

#Admin dashboard
@app.route("/admin_dashboard")
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route("/moderatorForm", methods=['GET','POST'])
def add_moderator():
    conn = mysql.connect()
    mycur = conn.cursor(pymysql.cursors.DictCursor)
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        group = request.form['blood']
        institute = request.form['institute']
        location = request.form['location']
        zilla = request.form['zilla']
        mycur.execute("INSERT INTO Moderator(name, phone, email, blood, institute, location, district) VALUES (%s,%s,%s,%s,%s,%s, %s)", (name, phone, email, group,institute, location, zilla))
        conn.commit()
        mycur.close()
    return render_template('moderatorForm.html')

@app.route("/moderatorList", methods=['GET', 'POST'])
def show_moderator():
    conn = mysql.connect()
    mycur = conn.cursor(pymysql.cursors.DictCursor)
    mycur.execute("SELECT * FROM moderator LEFT JOIN user_designation ON moderator.designation_id = user_designation.designation_id")
    data = mycur.fetchall()
    mycur.close()
    return render_template('moderatorListEdit.html', moderator = data)

@app.route("/editModeratorList", methods=['GET','POST'])
def edit_moderator():
    if request.method == 'POST':
        conn = mysql.connect()
        mycur = conn.cursor(pymysql.cursors.DictCursor)
        #print([request.form['entry_id']])
        id = request.form['edit_moderator']
        designation_id = request.form['designation']
        #print(designation)
        mycur.execute("UPDATE moderator SET designation_id = {0} WHERE id = {1}".format(designation_id, id))
        conn.commit()
        mycur.execute("SELECT * FROM moderator LEFT JOIN user_designation ON moderator.designation_id = user_designation.designation_id")
        data = mycur.fetchall()
        #print(data)
        mycur.close()
        return render_template('moderatorListEdit.html', moderator = data)

@app.route("/moderatorListDelete", methods=['GET','POST'])
def delete_moderator():
    if request.method == 'POST':
        conn = mysql.connect()
        mycur = conn.cursor(pymysql.cursors.DictCursor)
        #print([request.form['entry_id']])
        id = request.form['delete_id']
        mycur.execute("DELETE FROM moderator WHERE id = {0}".format(id))
        conn.commit()
        mycur.execute("SELECT * FROM moderator")
        data = mycur.fetchall()
        print(data)
        mycur.close()
        return render_template('moderatorListEdit.html', moderator = data)

@app.route("/moderator")
def enter_moderator():
    return render_template('moderator.html')

@app.route("/designation", methods=['POST','GET'])
def create_designation():
    conn = mysql.connect()
    mycur = conn.cursor(pymysql.cursors.DictCursor)

    if request.method == 'POST':
        designation = request.form['designation']
        mycur.execute("INSERT INTO user_designation(designation_name) VALUES(%s)",(designation))
        conn.commit()
        mycur.execute("SELECT * FROM user_designation")
        x = mycur.fetchall()
        mycur.close()
        return render_template('designation.html', designation = x)
    mycur.execute("SELECT * FROM user_designation")
    data = mycur.fetchall()
    return render_template('designation.html', designation = data)

    
@app.route('/text', methods=['POST', 'GET'])
def show_text():
    if request.method == 'POST':
        data = request.form['textpost']
        return render_template('admin.html', post = data)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploader', methods = ['GET', 'POST'])
def file_upload():
    if request.method == 'POST':
        f = request.files['file']
        filename = secure_filename(f.filename)
         #f.save(secure_filename(f.filename))
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return 'file uploaded successfully'

@app.route("/uploadImage", methods=['GET','POST'])
def add_image():
    if request.method == 'POST':
        conn = mysql.connect()
        mycur = conn.cursor(pymysql.cursors.DictCursor)
        print(1)
        f = request.files['photo']
        print(f)
        f.save(secure_filename(f.filename))
        photo_url = f.filename
        print(photo_url)
        mycur.execute('INSERT INTO images(image_name)VALUES(%s)',(photo_url))
        conn.commit()
        mycur.execute('SELECT*FROM images')
        data = mycur.fetchall()
        mycur.close()
        return render_template('admin_dashboard.html', image = data)
     
if __name__ == "__main__":
    app.run(debug=False)