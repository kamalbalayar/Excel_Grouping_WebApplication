from flask import Blueprint, render_template, request, flash, send_file, session, redirect, url_for
from flask_login import login_required, current_user
import pandas
from fileinput import filename
import os
import csv
import xlrd

views = Blueprint('views', __name__)

user = current_user

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    email = current_user.email
    upload_folder = 'uploads'
    files = os.listdir(upload_folder)
    
    if request.path == '/':
        session.clear()
        session.modified = True
        for filename in os.listdir('./flask_session'):
            file_path = os.path.join('./flask_session', filename)
            try:
                os.remove(file_path)
            except Exception as e:
                print(f'Error deleting file {file_path}: {e}')
    
    return render_template("home.html", email=email, user=current_user, files=files, upload_folder=upload_folder)
def index():
    if 'count' not in session:
        session['count'] = 0
    session['count'] += 1
    return f'Count: {session["count"]}'

@views.route('/upload', methods=['GET', 'POST'])
def upload():
    user = request.args.get('user')
    filename = request.args.get('filename')
    
    if filename:
        data = []
        if filename.endswith('.csv'):
            with open(os.path.join('uploads', filename), 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                print(csv_reader)
                headers = next(csv_reader)
                for row in csv_reader:
                    data.append(row)
        elif filename.endswith('.xls'):
            book = xlrd.open_workbook(os.path.join('uploads', filename))
            sheet = book.sheet_by_index(0)
            headers = sheet.row_values(0)
            for row in range(1, sheet.nrows):
                data.append(sheet.row_values(row))
        elif filename.endswith('.xlsx'):
            df = pandas.read_excel(os.path.join('uploads', filename))
            headers = df.columns.tolist()
            data = df.values.tolist()
        else:
            return redirect((url_for('views.home')))
        
        session['filename'] = filename
        session['headers'] = headers
        session['data'] = data

        table_data = []
        for row in data:
            table_data.append(list(row))

        return redirect(url_for('views.upload_page', filename=filename))
    
    headers=[]
    if request.method == 'POST':
        file = request.files.get('file')
        saved_file = request.form.get('saved_file')
        
        if not file and not saved_file:
            return redirect((url_for('views.home')))


        if file:
            filename = file.filename
            file.save(os.path.join('uploads', filename))
        else:
            filename = saved_file

        data = []
        if filename.endswith('.csv'):
            with open(os.path.join('uploads', filename), 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                headers = next(csv_reader)
                for row in csv_reader:
                    data.append(row)
        elif filename.endswith('.xls'):
            book = xlrd.open_workbook(os.path.join('uploads', filename))
            sheet = book.sheet_by_index(0)
            headers = sheet.row_values(0)
            for row in range(1, sheet.nrows):
                data.append(sheet.row_values(row))
        elif filename.endswith('.xlsx'):
            df = pandas.read_excel(os.path.join('uploads', filename))
            headers = df.columns.tolist()
            data = df.values.tolist()
        else:
            flash('Reset Filter!', category='error')

        session['filename'] = filename
        session['headers'] = headers
        session['data'] = data

        table_data = []
        for row in data:
            table_data.append(list(row))

        return redirect(url_for('views.upload_page', filename=filename))
    
    num_rows = len(headers)
    upload_folder = 'uploads'
    files = os.listdir(upload_folder)
    return render_template("upload_form.html", files=files, user=current_user, upload_folder=upload_folder, num_rows=num_rows)

@views.route('/upload/<filename>', methods=['GET'])
def upload_page(filename):
    headers = session.get('headers')
    data = session.get('data')
    table_data = []
    for row in data:
        row_without_quotes = [str(cell).replace("'", "`") for cell in row]
        table_data.append(row_without_quotes)
    return render_template('upload.html', headers=headers, data=table_data, user=current_user, filename=filename)


@views.route('/filter', methods=['POST'])
def filter():
    filename = request.form.get('filename')
    if request.method == 'POST':
        try:
            selected_headers = request.form.getlist('filter')
        except KeyError:
            selected_headers = []

        table_data = session['data']
        headers = selected_headers

        filtered_data = []
        for row in table_data:
            filtered_row = []
            for i, value in enumerate(row):
                if session['headers'][i] in selected_headers:
                    value_without_quotes = str(value).replace("'", "`")
                    filtered_row.append(value_without_quotes)
            if filtered_row:
                filtered_data.append(filtered_row)

        session['filtered_data'] = filtered_data
        session['headers'] = headers
        
        return redirect(url_for('views.filter_page', filename=filename))


@views.route('/filter_page/<filename>', methods=['GET'])
def filter_page(filename):
    headers = session.get('headers')
    filtered_data = session.get('filtered_data')
    table_data = []
    for row in filtered_data:
        row_without_quotes = [str(cell).replace("'", "`") for cell in row]
        table_data.append(row_without_quotes)
    num_rows = len(headers)
    return render_template('upload.html', headers=headers, data=table_data, user=current_user, filename=filename, num_rows=num_rows)
