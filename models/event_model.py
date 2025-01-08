from MySQLdb.cursors import DictCursor

class EventModel:
    def __init__(self, db):
        self.db = db

    def get_events(self):
        """Fetch event details."""
        db = self.db.cursor()
        db.execute("""
            SELECT eventName, eventDate, eventStartTime, eventEndTime, eventLocation, routeDistance 
            FROM Event
        """)
        return db.fetchall()
    
    def get_event_details(self):
        db = self.db.cursor()
        db.execute("""
            SELECT JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.titleDesc')), 
               JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.remark1')),
               JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.remark2')),
               JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.remark3')) 
        FROM eventDetails
        WHERE eventDetailId = 211 AND detailName = 'Event Info';
        """)
        return db.fetchall()

    def get_past_event_images(self):
        """Fetch past event images."""
        db = self.db.cursor()
        db.execute("""
            SELECT detailPicture 
            FROM EventDetails 
            WHERE eventID = 1 AND detailName = 'Past Event Images'
        """)
        return db.fetchall()

    def get_route_images(self):
        """ Retrieve route images for the event."""
        query = "SELECT detailPicture FROM EventDetails WHERE eventID = 1 AND detailName = 'Route Images'"
        db = self.db.cursor()
        db.execute(query)
        route_images = db.fetchall()
        return route_images
    
    def get_packages(self):
        """ Retrieve all active packages and their items. """
        query = """
            SELECT P.packageName, P.price, I.itemName
            FROM packages P
            LEFT JOIN items I ON I.itemID = P.itemID
            WHERE P.packageStatus = 'active';
        """
        db = self.db.cursor(DictCursor)
        db.execute(query)
        results = db.fetchall()
        return results
