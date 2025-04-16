from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class DetectionResult(db.Model):
    """
    Model for storing license plate detection results
    """
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    detection_type = db.Column(db.String(50), nullable=False)  # 'license_plate' or 'lane_intrusion'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # For storage of the result image
    result_path = db.Column(db.String(255))

    # Relationship with detection items (license plates or intrusions)
    items = db.relationship('DetectionItem', backref='detection', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<DetectionResult {self.id} - {self.detection_type}>'

class DetectionItem(db.Model):
    """
    Model for storing individual detected items (license plates or intrusion events)
    """
    id = db.Column(db.Integer, primary_key=True)
    detection_id = db.Column(db.Integer, db.ForeignKey('detection_result.id'), nullable=False)

    # For license plates
    license_plate = db.Column(db.String(20), nullable=True)
    confidence = db.Column(db.Float, nullable=True)

    # For lane intrusions
    vehicle_id = db.Column(db.Integer, nullable=True)
    from_lane = db.Column(db.Integer, nullable=True)
    to_lane = db.Column(db.Integer, nullable=True)

    # Bounding box coordinates (x1, y1, x2, y2)
    bbox_x1 = db.Column(db.Integer, nullable=True)
    bbox_y1 = db.Column(db.Integer, nullable=True)
    bbox_x2 = db.Column(db.Integer, nullable=True)
    bbox_y2 = db.Column(db.Integer, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        if self.license_plate:
            return f'<DetectionItem {self.id} - Plate: {self.license_plate}>'
        else:
            return f'<DetectionItem {self.id} - Intrusion: Lane {self.from_lane} to {self.to_lane}>'