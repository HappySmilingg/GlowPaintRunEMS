class EventModel:
    def __init__(self, db):
        self.db = db

    def get_events(self):
        """Fetch event details."""
        self.db.execute("""
            SELECT eventName, eventDate, eventStartTime, eventEndTime, eventLocation, routeDistance 
            FROM Event
        """)
        return self.db.fetchall()
    
    def get_event_details(self):
        self.db.execute("""
            SELECT JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.titleDesc')), 
               JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.remark1')),
               JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.remark2')),
               JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.remark3')) 
        FROM eventDetails
        WHERE eventDetailId = 21 AND detailName = 'Event Info';
        """)
        return self.db.fetchall()

    def get_past_event_images(self):
        """Fetch past event images."""
        self.db.execute("""
            SELECT detailPicture 
            FROM EventDetails 
            WHERE eventID = 1 AND detailName = 'Past Event Images'
        """)
        return self.db.fetchall()
