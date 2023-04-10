from flask import Flask,render_template,redirect,url_for,flash,request,session
from flask_sqlalchemy import SQLAlchemy
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

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
    seats_remaining = db.Column("seats_remaining",db.Integer)
    recliner_row_price = db.Column("recliner_seat_price",db.Integer)
    middle_row_price = db.Column("middle_row_price",db.Integer)
    front_row_price = db.Column("front_row_price",db.Integer)
    shows = db.relationship("Show",backref="venue")


    def __init__(self,venue_name,venue_location,seats_remaining,recliner_row_price,middle_row_price,front_row_price):
        self.venue_name = venue_name
        self.venue_location = venue_location
        self.seats_remaining = seats_remaining
        self.recliner_row_price = recliner_row_price
        self.middle_row_price = middle_row_price
        self.front_row_price = front_row_price

class Show(db.Model):

    id = db.Column("id",db.Integer,primary_key=True)
    show_name = db.Column("show_name",db.String(100))
    show_timing = db.Column("show_timing",db.String(100))
    show_price = db.Column("show",db.Integer)
    show_id = db.Column(db.Integer,db.ForeignKey("venue.id"))
    users = db.relationship("User",secondary="user_show")
    average_rating = db.Column(db.Float, default=None)

    def update_average_rating(self):
        ratings = [user_show.rating for user_show in self.show_users if user_show.rating is not None]
        if len(ratings) == 0:
            self.average_rating = None
        else:
            self.average_rating = sum(ratings) / len(ratings)



'''
    def __init__(self,show_name,show_timing):
        self.show_name = show_name
        self.show_timing = show_timing  '''

class User(db.Model):

    id = db.Column("id",db.Integer,primary_key=True)
    username = db.Column("username",db.String(100))
    user_password = db.Column("user_password",db.String(100))
    booked_id = db.relationship("Show",secondary="user_show")
'''
    def __init__(self,username,user_password,booked_shows=0):

        self.username = username
        self.user_password = user_password
        self.booked_shows= 0 '''

class User_show(db.Model):
    id = db.Column("id",db.Integer,primary_key = True)
    user_id = db.Column(db.Integer,db.ForeignKey("user.id"))
    show_id = db.Column(db.Integer,db.ForeignKey("show.id"))

    rating = db.Column(db.Integer)

    user = db.relationship("User", backref=db.backref("user_shows", cascade="all, delete-orphan"))
    show = db.relationship("Show", backref=db.backref("show_users", cascade="all, delete-orphan"))

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
        if admin:
            if admin.user_name == user_name and password == admin.password:
                flash("Admin login is successful!","info")
                venues = Venue.query.all()
                return render_template("admin_view.html",user_name=user_name,venues=venues)
            else:
                flash("Incorrect username or password!")
                return render_template("admin_login.html")
        else:
            flash("Wrong username or password","info")
            return render_template("admin_login.html")

    else:
        if "user_name" in session:
            admin = Admin.query.first()
            venues = Venue.query.all()
            return render_template("admin_view.html",user_name=admin.user_name,venues=venues)
        else:
            return render_template("admin_login.html")

@app.route("/create_venue",methods=["GET","POST"])
def create_venue():
    if request.method == "POST":
        venue_name = request.form["venue_name"]
        venue_location = request.form["venue_location"]
        seats_remaining = request.form["venue_capacity"]
        recliner_row_price = request.form["recliner_row_price"]
        middle_row_price = request.form["middle_row_price"]
        front_row_price = request.form["front_row_price"]
        session["venue_name"] = venue_name
        session["venue_location"] = venue_location
        session["venue_capacity"] = seats_remaining
        venue = Venue(venue_name=venue_name,venue_location=venue_location,seats_remaining=seats_remaining,recliner_row_price=recliner_row_price, middle_row_price=middle_row_price ,front_row_price=front_row_price)
        db.session.add(venue)
        db.session.commit()
        flash("Venue created successfully","info")
        venues = Venue.query.all()
        admin = Admin.query.first()
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
        venue = Venue.query.filter_by(id=venue_id).first()
        return render_template("create_show.html",venue=venue)

@app.route("/edit_venue/<venue_id>",methods=["GET","POST"])
def edit_venue(venue_id):
    if request.method == "POST":
        new_name = request.form["venue_name"]
        new_location = request.form["venue_location"]
        new_seats_remaining = request.form["venue_capacity"]
        new_recliner_row_price = request.form["recliner_row_price"]
        new_middle_row_price = request.form["middle_row_price"]
        new_front_row_price = request.form["front_row_price"]
        venue = Venue.query.filter_by(id=venue_id).first()
        venue.venue_name = new_name
        venue.venue_location = new_location
        venue.seats_remaining = new_seats_remaining
        venue.recliner_row_price = new_recliner_row_price
        venue.middle_row_price = new_middle_row_price
        venue.front_row_price = new_front_row_price
        db.session.commit()
        flash("Venue edited Successfully","info")
        return redirect(url_for("admin_login"))
    else:
        venue = Venue.query.filter_by(id=venue_id).first()
        return render_template("edit_venue.html",venue=venue)

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
        venue = Venue.query.filter_by(id=venue_id).first()
        return render_template("edit_show.html",venue=venue)

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

@app.route("/user_register",methods=["GET","POST"])
def user_register():
    if request.method == "POST":
        username = request.form["username"]
        user_password = request.form["user_password"]
        session["username"] = username
        session["user_password"] = user_password
        dummy = User.query.filter_by(username=username).first()
        if not dummy:
            user = User(username = username,user_password=user_password)
            db.session.add(user)
            db.session.commit()
            flash("User registered successfully","info")
            return redirect(url_for("user_login"))
        else:
            flash("Username already exists",'info')
            return render_template("user_registration.html")
    else:
        return render_template("user_registration.html")


@app.route("/user_login",methods=["GET","POST"])
def user_login():
    if request.method == "POST":
        username = request.form["username"]
        user_password = request.form["user_password"]
        user = User.query.filter_by(username=username,user_password=user_password).first()
        if user:
            session["username"] = username
            session["user_password"] = user_password
            flash("User logged in successfully","info")
            venues = Venue.query.all()
            shows = Show.query.all()
            return render_template("home.html",user=user,venues=venues,shows=shows)
        else:
            flash("Incorrect Username or Password")
            return render_template("user_login.html")
    else:

        return render_template("user_login.html")

@app.route("/user_logout",methods=["GET","POST"])
def user_logout():
    if "username" in session:
        session.pop("username",None)
        flash("User logged out Successfully")
        return redirect(url_for("user_login"))
    else:
        return redirect(url_for("user_login"))



@app.route("/book_show/<user_id>/<venue_id>/<show_pid>",methods=["GET","POST"])
def book_show(user_id,venue_id,show_pid):
    if request.method == "POST":
        user = User.query.filter_by(id=user_id).first()
        show = Show.query.filter_by(id=show_pid).first()
        user.booked_id.append(show)
        db.session.commit()
        shows = user.booked_id
        ticket_price = request.form['show_price']
        no_of_tickets = request.form["number_of_tickets"]
        venue = Venue.query.filter_by(id=venue_id).first()
        if int(venue.seats_remaining) >= int(no_of_tickets):
            flash(str(no_of_tickets)+"have been booked for the show" +str(show.show_name),"info")
            venue.seats_remaining -= int(no_of_tickets)
            db.session.commit()
            return render_template("user_shows.html", user=user, shows=shows)
        else:
            flash(str(no_of_tickets)+ "are not available","info")
            venue = Venue.query.filter_by(id=venue_id).first()
            return render_template("booked_shows.html",venue=venue)

    else:
        venue = Venue.query.filter_by(id=venue_id).first()
        return render_template("booked_shows.html",venue=venue)

@app.route("/my_bookings/<id>",methods=["GET","POST"])
def my_bookings(id):
    user = User.query.filter_by(id=id).first()
    shows = user.booked_id
    return render_template("user_shows.html",user=user,shows=shows)

@app.route("/rate_show/<user_id>/<show_id>",methods=["GET","POST"])
def rate_show(user_id,show_id):
    if request.method == "POST":
        rating = int(request.form["rating"])
        user_show = User_show.query.filter_by(user_id=user_id, show_id=show_id).first()
        user_show.rating = rating
        db.session.commit()

        show = Show.query.get(show_id)
        show.update_average_rating()
        db.session.commit()

        user = User.query.filter_by(id=user_id).first()
        shows = user.booked_id
        venues = Venue.query.all()
        return render_template("user_shows.html",user=user,shows=shows,venues=venues)

    else:
        show = Show.query.get(show_id)
        return render_template("rate_show.html",show=show)

@app.route("/delete_venue/<venue_id>",methods=["GET","POST"])
def delete_venue(venue_id):

    if request.method == "POST":
        venue = Venue.query.filter_by(id=venue_id).first()
        db.session.delete(venue)
        db.session.commit()
        flash("Venue deleted successfully","info")
        return redirect(url_for("admin_login"))
    else:
        return render_template("delete_venue.html")


@app.route('/search')
def search():
    venue_id = request.args.get('venue')
    rating = request.args.get('rating')
    timing = request.args.get('timing')

    shows = Show.query
    if venue_id:
        shows = shows.filter_by(show_id=venue_id)
    if rating:
        shows = shows.filter(Show.average_rating >= rating)
    if timing:
        shows = shows.filter_by(show_timing=timing)

    venues = Venue.query.all()
    return render_template('search_results.html', shows=shows,venues=venues)

@app.route('/data_visualisation')
def data():
    venues = Venue.query.all()
    venue_names = [venue.venue_name for venue in venues]
    seats_remaining = [venue.seats_remaining for venue in venues]

    plt.bar(venue_names, seats_remaining)
    plt.title('Seats Remaining by Venue')
    plt.xlabel('Venue')
    plt.ylabel('Seats Remaining')
    plt.xticks(rotation=45)

    chart = plt.gcf()
    chart.savefig('static/images/venues.png')

    return render_template('data.html')

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(port=5001,debug=True)
