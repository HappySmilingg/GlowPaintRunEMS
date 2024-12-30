import base64
from flask import render_template, request, jsonify
from models.event_model import EventModel

class EventController:
    def __init__(self, db):
        self.db = db
        self.event_model = EventModel(db)

    def get_event_details(self):
        """Fetch and process data for the homepage."""
        # Fetch events
        events = self.event_model.get_events()

        # Fetch event details
        sub_detail = self.event_model.get_event_details()
        sub_details = None
        if sub_detail:
            sub_details = {
                'description': sub_detail[0][0] or '',
                'info1': sub_detail[0][1] or '',
                'info2': sub_detail[0][2] or '',
                'info3': sub_detail[0][3] or ''
            }

        # Fetch past event images
        past_event_images = self.event_model.get_past_event_images()

        # Process images (convert binary to base64)
        past_images = [
            base64.b64encode(image[0]).decode('utf-8') for image in past_event_images
        ]

        # Extract event date
        event_date = events[0][1] if events else None

        return {"events": events, "event_date": event_date, 'sub_details': sub_details, "past_images": past_images}

    def route(self):
        return render_template('Public/route.html')

    def get_route_image(self, selected_option):
        index = {
            'cafe': 0,      # Bumbledees Cafe
            'muzium': 1,    # Muzium
            'bukit': 2,     # Bukit Cinta
            'hbp': 3,       # HBP
            'fajar': 4,     # Fajar
            'bhepa': 5,     # BHEPA
            'kok': 6,       # Rancangan KOK
            'start': 7,     # Start/Finish
        }

        if selected_option in index:
            route_images = self.event_model.get_route_images()

            # Map selected_option to the corresponding index
            image_index = index[selected_option]
            try:
                route_image = route_images[image_index][0]
                base64_encoded_image = base64.b64encode(route_image).decode('utf-8')
                return jsonify({'image': base64_encoded_image})
            except IndexError:
                return jsonify({'error': 'Image not found'}), 404
        else:
            return jsonify({'error': 'Invalid selection'}), 400
    
    def packages(self):
        results = self.event_model.get_packages()

        # Group items by package
        packages = {}
        for row in results:
            package_name = row['packageName']
            price = row['price']
            item_name = row['itemName']
            if package_name not in packages:
                packages[package_name] = {
                    'price': price,
                    'items': []
                }
            packages[package_name]['items'].append(item_name)

        # Add a note for specific packages (example: "Only for USM Student")
        for package in packages:
            if package.lower().endswith('lite') or package.lower().endswith('starter'):
                packages[package]['note'] = '#Only for USM Student'
            else:
                packages[package]['note'] = '#Available for USM Student & Public Participant'

        return render_template('Public/packages.html', packages=packages)