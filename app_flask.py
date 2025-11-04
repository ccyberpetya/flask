from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:123@localhost:5432/ads_db?client_encoding=utf8"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['JSON_AS_ASCII'] = False

db = SQLAlchemy(app)


class Advertisement(db.Model):
    __tablename__ = "advertisements"

    id = db.Column(db.Integer, primary_key=True)
    headline = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    owner = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "headline": self.headline,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "owner": self.owner
        }


@app.route("/ads", methods=["POST"])
def create_ad():
    data = request.get_json()

    # Проверка кодировки
    print("Received data:", data)

    ad = Advertisement(
        headline=data.get("headline"),
        description=data.get("description"),
        owner=data.get("owner")
    )
    db.session.add(ad)
    db.session.commit()
    return jsonify(ad.to_dict()), 201


@app.route("/ads/<int:ad_id>", methods=["GET"])
def get_ad(ad_id):
    ad = Advertisement.query.get_or_404(ad_id)
    return jsonify(ad.to_dict())


@app.route("/ads/<int:ad_id>", methods=["PATCH"])
def update_ad(ad_id):
    ad = Advertisement.query.get_or_404(ad_id)
    data = request.get_json()

    if "headline" in data:
        ad.headline = data["headline"]
    if "description" in data:
        ad.description = data["description"]
    if "owner" in data:
        ad.owner = data["owner"]

    db.session.commit()
    return jsonify(ad.to_dict())


@app.route("/ads/<int:ad_id>", methods=["DELETE"])
def delete_ad(ad_id):
    ad = Advertisement.query.get_or_404(ad_id)
    db.session.delete(ad)
    db.session.commit()
    return jsonify({"status": f"Ad {ad_id} deleted"})


@app.route("/ads", methods=["GET"])
def get_all_ads():
    ads = Advertisement.query.all()
    return jsonify([ad.to_dict() for ad in ads])


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
