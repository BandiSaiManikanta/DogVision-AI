from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
import os, random, datetime, pandas as pd
from werkzeug.utils import secure_filename
from collections import Counter

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///predictions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(200))
    breed = db.Column(db.String(100))
    confidence = db.Column(db.Float)
    date = db.Column(db.String(100))

with app.app_context():
    db.create_all()

dog_breeds=["Labrador","German Shepherd","Golden Retriever","Pug","Beagle","Rottweiler","Husky","Boxer"]

@app.route("/")
def home(): return render_template("index.html")

@app.route("/predict")
def predict(): return render_template("predict.html")

@app.route("/result", methods=["POST"])
def result():
    file=request.files["file"]
    filename=secure_filename(file.filename)
    path=os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(path)

    prediction=random.choice(dog_breeds)
    confidence=round(random.uniform(85,98),2)

    new=Prediction(image_name=filename,breed=prediction,
                   confidence=confidence,date=str(datetime.datetime.now()))
    db.session.add(new)
    db.session.commit()

    return render_template("output.html",
        prediction=prediction,confidence=confidence,img_path=path)

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/analytics-data")
def analytics_data():
    data = Prediction.query.all()
    dates=[p.date[:10] for p in data]
    breeds=[p.breed for p in data]
    return {
        "dates":list(Counter(dates).keys()),
        "date_values":list(Counter(dates).values()),
        "breeds":list(Counter(breeds).keys()),
        "breed_values":list(Counter(breeds).values())
    }

# EXPORT REPORT
@app.route("/export")
def export():
    data=Prediction.query.all()
    df=pd.DataFrame([(d.image_name,d.breed,d.confidence,d.date)
                    for d in data],
                    columns=["Image","Breed","Confidence","Date"])
    file="report.csv"
    df.to_csv(file,index=False)
    return send_file(file,as_attachment=True)
app.run(host="0.0.0.0", port=5000, debug=True)