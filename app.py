from flask import Flask,render_template,redirect,url_for,flash,request,session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "shreyansh__"

db = SQLAlchemy(app)

class Admin(db.Model):

    id = db.Column("id",db.Integer,primary_key=True)
    user_name = db.Column("name",db.String(100))
    password = db.Column("password",db.String(100))

    def __init__(self,user_name,password):
        self.user_name = user_name
        self.password = password

class Venue(db.Model):
    id = db.Column("id",db.Integer,primary_key=True)
    venue_name = db.Column("venue_name",db.String(100))
    venue_location = db.Column("venue_location",db.String(100))
    venue_capacity = db.Column("venue_capacity",db.Integer)
    shows = db.relationship("Show",backref="venue")

    def __init__(self,venue_name,venue_location,venue_capacity):
        self.venue_name = venue_name
        self.venue_location = venue_location
        self.venue_capacity = venue_capacity

class Show(db.Model):

    id = db.Column("id",db.Integer,primary_key=True)
    show_name = db.Column("show_name",db.String(100))
    show_timing = db.Column("show_timing",db.String(100))
    show_id = db.Column(db.Integer,db.ForeignKey("venue.id"))

'''
    def __init__(self,show_name,show_timing):
        self.show_name = show_name
        self.show_timing = show_timing  '''

@app.route("/admin_login",methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        user_name = request.form["user_name"]
        password = request.form["password"]
        session["user_name"] = user_name
        session["password"] = password

        '''
        admin = Admin(user_name=user_name,password=password)
        db.session.add(admin)
        db.session.commit()
        '''

        admin = Admin.query.filter_by(user_name=user_name).first()
        if admin.user_name == user_name and password == admin.password:
            flash("Admin login is successful!","info")
            venues = Venue.query.all()
            return render_template("admin_view.html",user_name=user_name,venues=venues)
        else:
            flash("Incorrect username or password!")
            return render_template("admin_login.html")

    else:
        if "user_name" in session:
            venues = Venue.query.all()
            return render_template("admin_view.html",user_name=session["user_name"],venues=venues)
        else:
            return render_template("admin_login.html")

@app.route("/create_venue",methods=["GET","POST"])
def create_venue():
    if request.method == "POST":
        venue_name = request.form["venue_name"]
        venue_location = request.form["venue_location"]
        venue_capacity = request.form["venue_capacity"]
        session["venue_name"] = venue_name
        session["venue_location"] = venue_location
        session["venue_capacity"] = venue_capacity
        venue = Venue(venue_name=venue_name,venue_location=venue_location,venue_capacity=venue_capacity)
        db.session.add(venue)
        db.session.commit()
        flash("Venue created successfully","info")
        venues = Venue.query.all()
        admin = Admin.query.filter_by(user_name=session["user_name"]).first()
        return redirect(url_for("admin_login",user_name=admin.user_name))
    else:

        return render_template("venues.html")

@app.route("/create_show/<venue_id>",methods=["GET","POST"])
def create_show(venue_id):
    if request.method == "POST":
        show_name = request.form["show_name"]
        show_timing = request.form["show_timing"]
        venue = Venue.query.filter_by(id=venue_id).first()
        show = Show(show_name=show_name,show_timing=show_timing,venue=venue)
        db.session.add(show)
        db.session.commit()
        flash("Show created successfully","info")
        return redirect(url_for("admin_login"))
    else:
        return render_template("create_show.html")

@app.route("/edit_show/<venue_id>/<show_name>/<show_timing>",methods=["GET","POST"])
def edit_show(venue_id,show_name,show_timing):
    if request.method == "POST":
        new_name = request.form["show_name"]
        new_timing = request.form["show_timing"]
        venue = Venue.query.filter_by(id=venue_id).first()
        show = Show.query.filter_by(show_name=show_name,show_timing=show_timing,venue=venue).first()
        show.show_name = new_name
        show.show_timing = new_timing
        db.session.commit()
        flash("Show edited successfully","info")
        return redirect(url_for("admin_login"))
    else:
        return render_template("edit_show.html")

@app.route("/delete_show/<venue_id>/<show_name>/<show_timing>",methods=["GET","POST"])
def delete_show(venue_id,show_name,show_timing):
    if request.method == "POST":
        venue = Venue.query.filter_by(id=venue_id).first()
        show = Show.query.filter_by(show_name=show_name,show_timing=show_timing,venue=venue).first()
        db.session.delete(show)
        db.session.commit()

        return redirect(url_for("admin_login"))
    else:
        return render_template("delete_show.html")

@app.route("/logout",methods=["GET","POST"])
def logout():
    if "user_name" in session:
        session.pop("user_name",None)
        flash("Logged out successfully!","info")
        return redirect(url_for("admin_login"))
    else:
        return redirect(url_for("admin_login"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(port=5001,debug=True)
