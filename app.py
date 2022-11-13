import flask
from flask_sqlalchemy import SQLAlchemy
from operator import itemgetter
from requests import get

app = flask.Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["SECRET_KEY"] = "sqhs-eage-3gqw"

db = SQLAlchemy(app)


class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    skills = db.Column(db.String, default="")
    primary_skill = db.Column(db.String, default="")
    name = db.Column(db.String)
    path_to_resume = db.Column(db.String)
    resume_point = db.Column(db.Integer)


class Searches(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    search_term = db.Column(db.String)


def get_matching_score_one(arr1, arr2):
    matching_score = 0

    for i in arr1:
        if i.replace(" ", "").lower() in [c.lower().replace(" ", "") for c in arr2]:
            matching_score += 2

    return matching_score


def remove_low_matching_scores(arr, minimum=6):
    for i in arr:
        if i.get("matching_score") < minimum:
            arr.remove(i)
    if len(arr) == 0 and minimum > 1:
        remove_low_matching_scores(arr, minimum=minimum-1)

    return arr


@app.route("/search/<skills>")
def search(skills):
    new_search = Searches(search_term=skills)

    db.session.add(new_search)
    db.session.commit()

    contains_js = "js" in skills
    skills = skills.split(",")

    if "javascript" not in [i.lower() for i in skills] and contains_js:
        skills.append("javascript")

    results = []
    for i in Candidate.query.all():
        if i.primary_skill.lower() in [c.lower() for c in skills]:
            if get_matching_score_one(arr1=skills, arr2=i.skills.split("/")) > 1:
                results.append({
                    "candidate": i,
                    "matching_score": get_matching_score_one(arr1=skills, arr2=i.skills.split("/")) + 5 + i.resume_point
                })
        else:
            if get_matching_score_one(arr1=skills, arr2=i.skills.split("/")) > 1:
                results.append({
                    "candidate": i,
                    "matching_score": get_matching_score_one(arr1=skills, arr2=i.skills.split("/")) + i.resume_point
                })

    results = remove_low_matching_scores(results)
    results = sorted(results, key=itemgetter('matching_score'), reverse=True)

    return flask.render_template("search_results.html", results=results)


@app.route("/get-candidate/<candidate_id>")
def get_candidate(candidate_id):
    return flask.send_file(Candidate.query.get(candidate_id).path_to_resume)


@app.route("/", methods=["POST", "GET"])
def search_index():
    if flask.request.method == "POST":
        path = flask.request.values["url_to_listing"]
        data_from_page = get(path).text.lower().split(" ")

        required_skills = []
        all_skills = []

        for i in Candidate.query.all():
            for c in i.skills.split("/"):
                all_skills.append(c.lower())

        all_skills = set(all_skills)

        for i in data_from_page:
            if i in all_skills:
                required_skills.append(i.replace("#", "sharp"))

        required_skills = set(required_skills)

        return flask.redirect("/search/" + ",".join(required_skills))

    return flask.render_template("search.html")