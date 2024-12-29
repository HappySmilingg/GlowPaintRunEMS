import base64
from models.event_model import EventModel

class EventController:
    def __init__(self, mysql):
        self.mysql = mysql

    def homepage_data(self):
        """Fetch and process data for the homepage."""
        db = self.mysql.connection.cursor()
        event_model = EventModel(db)

        # Fetch events
        events = event_model.get_events()

        # Fetch event details
        sub_detail = event_model.get_event_details()
        sub_details = None
        if sub_detail:
            sub_details = {
                'description': sub_detail[0][0] or '',
                'info1': sub_detail[0][1] or '',
                'info2': sub_detail[0][2] or '',
                'info3': sub_detail[0][3] or ''
            }

        # Fetch past event images
        past_event_images = event_model.get_past_event_images()

        # Process images (convert binary to base64)
        past_images = [
            base64.b64encode(image[0]).decode('utf-8') for image in past_event_images
        ]

        # Extract event date
        event_date = events[0][1] if events else None

        db.close()
        return {"events": events, "event_date": event_date, 'sub_details': sub_details, "past_images": past_images}
