from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, redirect, url_for, flash
import os

from supabase import create_client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

app = Flask(__name__)
app.secret_key = "obaoufbaobfoaboba"


@app.route("/")
def mainPage():
    response = supabase.table("Events").select("*").execute()
    data = response.data
    return render_template("main_page.html", data=data)


@app.route("/profile")
def profile():
    response = supabase.auth.get_session()
    if response:
        organizer_id = response.user.id
        response = supabase.table("Events").select("*").eq("organizers_id", organizer_id).execute()
        data = response.data
        return render_template("profile.html", data=data)
    else:
        return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        try:
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if response:
                return redirect(url_for("mainPage"))
        except Exception as e:
            flash(str(e), "error")
            return redirect(url_for("login"))
    return render_template("login.html")



@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        name = request.form["name"]
        age = request.form["age"]

        try:
            response1 = supabase.auth.sign_up({
                "email": email,
                "password": password
            })

            if response1.user and response1.user.identities != []:
                user_id = response1.user.id
                supabase.table("users_custom").insert({
                    "id": user_id,
                    "name": name,
                    "age": age
                }).execute()

                flash("Account Created, a confirmation link has been sent to your email", "success")
                return redirect(url_for("login"))

        except Exception:
            if len(password) >= 6:
                flash("Email already exists", "error")
            else:
                flash("Password length should be minimum 6 characters", "error")
            return redirect(url_for("signup"))

    return render_template("signup.html")


@app.route("/logout", methods=["GET","POST"])
def logout():
    if request.method == "GET":
        return redirect(url_for("profile"))
    else:
        response = supabase.auth.sign_out()
        return redirect(url_for("mainPage"))


@app.route("/organize", methods=["GET", "POST"])
def organize():
    response = supabase.auth.get_session()
    if response:
        return render_template("organize.html")
    else:
        return redirect(url_for("login"))


@app.route("/submitEvent", methods=["GET", "POST"])
def submitEvent():
    if request.method == "GET":
        return redirect(url_for("organize"))
    name = request.form["eventName"]
    venue = request.form["eventVenue"]
    time = request.form["eventTime"]
    date = request.form["eventDate"]
    duration = request.form["duration"]
    genre = request.form["genre"]
    response = supabase.auth.get_session()
    organizer_id = response.user.id
    response = supabase.table("Events").insert({"date": date, "time": time, "duration": duration, "genre": genre, "event_name": name, "venue": venue, "organizers_id": organizer_id}).execute()
    return redirect(url_for("mainPage"))



@app.route("/enroll", methods=["GET","POST"])
def enroll():
    if request.method == "POST":
        response = supabase.auth.get_session()
        if response:
            event_id = request.form["event_id"]
            user_id = response.user.id
            check = supabase.table("Attendees").select("id").eq("user_id", user_id).eq("event_id", event_id).execute()
            checkdata = check.data
            if checkdata != []:
                flash("Already Enrolled")
                return redirect(url_for("registered"))
            else:
                response = supabase.table("Attendees").insert({"event_id": event_id, "user_id": user_id}).execute()
                return redirect(url_for("registered")) # edit this to registered / enrolled event page
        else:
            return redirect(url_for("login"))
    else:
        return redirect(url_for("mainPage"))

@app.route("/attendee", methods=["GET", "POST"])
def attendee():
    if request.method == "POST":
        event_id = request.form["event_id"]
        response = supabase.table("Attendees").select("user_id, users_custom(id, name, age)").eq("event_id", event_id).execute()
        data = response.data
        return render_template("attendees.html", data=data)
    else:
        return redirect(url_for("profile"))

@app.route("/registered")
def registered():
    response = supabase.auth.get_session()
    if response:
         id = response.user.id
         response = supabase.table("Attendees").select("event_id, Events(event_name, venue, genre, date, time, duration)").eq("user_id", id).execute()
         data = response.data
         return render_template("registered.html", data=data)      
    else:
        return(redirect("login"))


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )
