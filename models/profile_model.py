class ProfileModel:
    def __init__(self, db):
        self.db = db
    
    def get_organiser_profile(self):
        query = """
            SELECT detailPicture AS picture, 
                   JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.name1')) AS name1,
                   JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.name2')) AS name2
            FROM eventdetails
            WHERE detailName = 'Organiser Profile'
        """
        db = self.db.cursor()
        db.execute(query)
        return db.fetchall()

    def get_social_links(self):
        query = """
            SELECT 
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.linkName1')) AS linkName1,
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.linkName2')) AS linkName2,
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.linkName3')) AS linkName3,
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.linkName4')) AS linkName4,
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.linkName5')) AS linkName5
            FROM eventdetails
            WHERE detailName = 'Social Link'
        """
        db = self.db.cursor()
        db.execute(query)
        return db.fetchall()

    def get_other_social_links(self):
        query = """
            SELECT 
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName1')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink1')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName2')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink2')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName3')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink3')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName4')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink4')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName5')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink5')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName6')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink6')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName7')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink7')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName8')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink8')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName9')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink9')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName10')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink10')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName11')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink11')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName12')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink12')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName13')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink13')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName14')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink14')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName15')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink15')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName16')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink16')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName17')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink17')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName18')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink18')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName19')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink19')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName20')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink20')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName21')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink21')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName22')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink22')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName23')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink23')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventName24')),
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.eventLink24'))
            FROM eventdetails
            WHERE detailName = 'Other Social Link'
        """
        db = self.db.cursor()
        db.execute(query)
        return db.fetchall()

    def get_contact_data(self, event_detail_id):
        query = f"""
            SELECT detailPicture, 
                   JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.message')),
                   JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.title')),
                   JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.position')),
                   JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.name')),
                   JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.contact'))
            FROM eventdetails
            WHERE eventDetailId = {event_detail_id} AND detailName = 'Contact Us'
        """
        db = self.db.cursor()
        db.execute(query)
        return db.fetchall()