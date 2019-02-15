from server import  db

class CollegeModel(db.Model):
    __tablename__ = 'college'
    name = db.Column(db.TEXT, primary_key=True)
    private = db.Column(db.TEXT)
    apps = db.Column(db.TEXT)
    acc = db.Column(db.Integer)
    enroll = db.Column(db.Integer)
    top10perc = db.Column(db.Integer)
    top25perc = db.Column(db.Integer)
    fundergrad = db.Column(db.Integer)
    pundergrad = db.Column(db.Integer)
    outstate = db.Column(db.Integer)
    roomboard = db.Column(db.Integer)
    books = db.Column(db.Integer)
    personal = db.Column(db.Integer)
    phd = db.Column(db.Integer)
    terminal = db.Column(db.Integer)
    ratio = db.Column(db.Float)
    percalum = db.Column(db.Integer)
    expend = db.Column(db.Integer)
    gradrate = db.Column(db.Float)

    def __init__(self, school_name):
        self.name = school_name

    @classmethod
    def find_by_school_name(cls, school):
        return cls.query.filter_by(name=school).first()

    def json(self):
        return {
            'school name': self.name,
            'private': self.private,
            'number of application': self.apps,
            'number of enrollment': self.enroll,
            'top10perc': self.top10perc,
            'top25perc': self.top25perc,
            'F undergrad': self.fundergrad,
            'P undergrad': self.pundergrad,
            'number of out of state students': self.outstate,
            'room n board cost': self.roomboard
        }