import base64
from flask import render_template, request, jsonify
from models.profile_model import ProfileModel

class ProfileController:
    def __init__(self, db):
        self.db = db
        self.profile_model = ProfileModel(db)

    def about_us(self):
        # Get data from the model
        profile_data = self.profile_model.get_organiser_profile()
        social_data = self.profile_model.get_social_links()
        other_social_data = self.profile_model.get_other_social_links()

        # Process profile data (base64 encoding the image)
        profile = None
        if profile_data:
            profile = {
                'picture': base64.b64encode(profile_data[0][0]).decode('utf-8') if profile_data[0][0] else None,
                'name1': profile_data[1][1],     
                'name2': profile_data[1][2]   
            }

        # Process social links
        social = None
        if social_data:
            social = {
                'linkName1': social_data[0][0],
                'linkName2': social_data[0][1],
                'linkName3': social_data[0][2],
                'linkName4': social_data[0][3],
                'linkName5': social_data[0][4]
            }

        # Process other social links (loop through all events)
        event = None
        if other_social_data:
            event = {}
            for i in range(1, 25):
                event[f'eventName{i}'] = other_social_data[0][2 * (i - 1)]  
                event[f'eventLink{i}'] = other_social_data[0][2 * (i - 1) + 1] 

        return render_template('Public/about_us.html', profile=profile, social=social, event=event)
    
    def contact_us(self):
        contact_data = self.profile_model.get_contact_data(19)
        contact_data2 = self.profile_model.get_contact_data(20)

        contact = None
        contact2 = None

        if contact_data:
            contact = {
                    'profile': base64.b64encode(contact_data[0][0]).decode('utf-8') if contact_data[0][0] else None,
                    'message': contact_data[0][1],
                    'title': contact_data[0][2],
                    'position': contact_data[0][3],
                    'name': contact_data[0][4],
                    'contact': contact_data[0][5],
                }

        if contact_data2:
            contact2 = {
                    'profile': base64.b64encode(contact_data2[0][0]).decode('utf-8') if contact_data2[0][0] else None,
                    'title': contact_data2[0][1],
                    'position': contact_data2[0][2],
                    'name': contact_data2[0][3],
                    'contact': contact_data2[0][4],
                }

        return render_template('Public/contact_us.html', contact=contact, contact2=contact2)