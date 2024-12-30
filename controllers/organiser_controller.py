from datetime import datetime
import base64
import mimetypes
from flask import render_template, flash, request, jsonify, Response
from models.organiser_model import OrganiserModel

class OrganiserController:
    def __init__(self, db):
        self.db = db
        self.organiser_model = OrganiserModel(db)

# Homepage
    def handle_homepage(self, request):
        if request.method == 'POST':
            try:
                # Handle form data
                form_data = {
                    'title': request.form.get('text-title'),
                    'description': request.form.get('text-desc'),
                    'date': request.form.get('text-date'),
                    'time1': request.form.get('text-time1'),
                    'time2': request.form.get('text-time2'),
                    'venue': request.form.get('text-venue'),
                    'distance': request.form.get('text-distance'),
                    'remark1': request.form.get('text-info1'),
                    'remark2': request.form.get('text-info2'),
                    'remark3': request.form.get('text-info3'),
                }
                self.organiser_model.update_event_details(form_data)

                # Handle file uploads
                for i in range(1, 6):
                    img_file = request.files.get(f'upload-image-{i}')
                    if img_file:
                        self.organiser_model.update_event_image(i, img_file.read())

                flash('Your changes have been saved!', 'success')
            except Exception as e:
                self.db.rollback()
                flash('Failed to save changes. Please try again.', 'error')

        # Retrieve data for rendering
        mains = self.organiser_model.get_main_event_details()
        sub_details = self.organiser_model.get_sub_event_details()
        past_event_images = self.organiser_model.get_past_event_images()

        # Format time and images
        if mains:
            mains['time1'] = datetime.strptime(str(mains['time1']), "%H:%M:%S").strftime("%H:%M")
            mains['time2'] = datetime.strptime(str(mains['time2']), "%H:%M:%S").strftime("%H:%M")

        images = {
            img[0]: {
                "picture": base64.b64encode(img[1]).decode('utf-8') if img[1] else None
            }
            for img in past_event_images
        }

        return render_template('Organiser/homepage.html', mains=mains, sub_details=sub_details, images=images)

# Student And Public Participant
    def student_participant_list(self):
        students = self.organiser_model.get_student_participants()
        students_data = [
            {
                'name': student[0],
                'email': student[1],
                'phone': student[2],
                'matricNumber': student[3],
                'package': student[4],
                'tShirtSize': student[5],
                'campus': student[6],
                'school': student[7],
                'status': student[8],
                'totalAmount': student[9],
                'fileUploaded': student[10],
                'fileName': student[11],
                'transport': student[12]
            }
            for student in students
        ]
        return render_template('Organiser/student_participant_list.html', students=students_data)

    def update_status(self, matricNumber):
        data = request.get_json()
        status = data.get('status')
        success = self.organiser_model.update_student_status(matricNumber, status)
        return jsonify({'success': success})
    
    def public_participant_list(self):
        publics = self.organiser_model.get_public_participants()
        publics_data = [
            {
                'name': public[0],
                'email': public[1],
                'phone': public[2],
                'ICNumber': public[3],
                'package': public[4],
                'tShirtSize': public[5],
                'status': public[6],
                'totalAmount': public[7],
                'fileUploaded': public[8],
                'fileName': public[9]
            }
            for public in publics
        ]
        return render_template('Organiser/public_participant_list.html', publics=publics_data)

    def update_status2(self, ICNumber):
        data = request.get_json()
        status = data.get('status')
        success = self.organiser_model.update_public_status(ICNumber, status)
        return jsonify({'success': success})
    
    def download_file(self, user_number):
        file_data = self.organiser_model.get_file(user_number)

        if file_data:
            file_uploaded, file_name = file_data

            # Determine MIME type based on the file name extension
            mime_type, _ = mimetypes.guess_type(file_name)
            if not mime_type:
                mime_type = 'application/octet-stream'  # Fallback for unknown file types

            # Return the file as a downloadable response
            return Response(
                file_uploaded,
                mimetype=mime_type,
                headers={"Content-Disposition": f"attachment;filename={file_name}"}
            )
        else:
            return "File not found", 404

# Event Route Page
    def handle_route(self, request):
        try:
            for i in range(6, 15):  # Loop for eventDetailId 6-14
                img_name = request.form.get(f'point-{i}')
                img_file = request.files.get(f'upload-image-{i}')
                if img_file:
                    img_data = img_file.read()
                    self.organiser_model.update_route_detail_with_image(i, img_data, img_name)
                else:
                    self.organiser_model.update_route_name(i, img_name)

            flash('Your changes have been saved!', 'success')

        except Exception as e:
            self.organiser_model.rollback_transaction()
            flash('Failed to save changes. Please try again.', 'error')

    def get_route_details(self):
        event_details = self.organiser_model.get_route_details()
        locations = {}
        for detail in event_details:
            locations[detail[0]] = {
                "picture": base64.b64encode(detail[1]).decode('utf-8') if detail[1] else None,
                "img_name": detail[2]
            }
        return {f'location_{i}': locations.get(i) for i in range(6, 15)}

# Packages Page
    def process_packages_and_items(self, form_data, is_get=False):
        if is_get:
            # Fetch the data to display in the template
            tshirt_sizes = self.organiser_model.get_tshirt_sizes()
            items = self.organiser_model.get_items()
            packages = self.organiser_model.get_packages()
            return {
                'tshirt_sizes': tshirt_sizes,
                'items': items,
                'packages': packages
            }

        # Handle POST data for tshirt sizes, items, and packages
        self.organiser_model.update_tshirt_sizes(form_data)
        self.organiser_model.update_items(form_data)
        self.organiser_model.update_packages(form_data)

# About Us Page
    def handle_about_us(self, request):
        # Handle POST request
        if request.method == 'POST':
            self.organiser_model.update_event_details(request)
            self.organiser_model.update_social_links(request)
            self.organiser_model.update_other_link(request)
            flash('Your changes have been saved!', 'success')
        
        # Fetch the current data to be displayed
        profile_data = self.organiser_model.get_profile_data()
        social_data = self.organiser_model.get_social_links()
        other_social_data = self.organiser_model.get_other_social_links()

        profile = None
        if profile_data:
            profile = {
            'picture': base64.b64encode(profile_data[0][0]).decode('utf-8') if profile_data[0][0] else None,
            'name1': profile_data[1][1],     
            'name2': profile_data[1][2]      
            }
        
        social = None
        if social_data:
            social = {
                'linkName1': social_data[0][0],
                'linkName2': social_data[0][1],
                'linkName3': social_data[0][2],
                'linkName4': social_data[0][3],
                'linkName5': social_data[0][4]
            }
        
        event = None
        if other_social_data:
            event = {}
            for i in range(1, 25):
                event[f'eventName{i}'] = other_social_data[0][2 * (i - 1)]  
                event[f'eventLink{i}'] = other_social_data[0][2 * (i - 1) + 1] 

        return render_template('Organiser/about_us.html', profile=profile, social=social, event=event)

# Contact Us Page
    def handle_contact_us(self, request):
        if request.method == 'POST':
            try:
                # Get form data
                form_data = {
                    'message': request.form.get('desc'),
                    'title': request.form.get('desc2'),
                    'position': request.form.get('desc3'),
                    'name': request.form.get('desc4'),
                    'contact': request.form.get('desc5'),
                    'img_file': request.files.get('profile'),
                    'title2': request.form.get('desc6'),
                    'position2': request.form.get('desc7'),
                    'name2': request.form.get('desc8'),
                    'contact2': request.form.get('desc9'),
                    'img_file2': request.files.get('profile2')
                }

                self.organiser_model.update_contact_us(form_data)

                flash('Your changes have been saved!', 'success')

            except Exception as e:
                print(f"Error!!!: {str(e)}")
                flash('Failed to save changes. Please try again.', 'error')

    def get_contact_us_data(self):
        contact_data = self.organiser_model.get_contact_us_data() 
        contact_data2 = self.organiser_model.get_contact_us_data2()  
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
        return contact, contact2