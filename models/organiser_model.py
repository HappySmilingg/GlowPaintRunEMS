from MySQLdb.cursors import DictCursor


class OrganiserModel:
    def __init__(self, db):
        self.db = db

# Homepage
    def update_event_details(self, form_data):
        db = self.db.cursor()
        if form_data['description'] or form_data['remark1'] or form_data['remark2'] or form_data['remark3']:
            db.execute(
                """
                UPDATE EventDetails
                SET detailDescription = JSON_SET(
                    detailDescription, 
                    '$.titleDesc', COALESCE(%s, ''),
                    '$.remark1', COALESCE(%s, ''),
                    '$.remark2', COALESCE(%s, ''),
                    '$.remark3', COALESCE(%s, '')
                )
                WHERE eventDetailId = 21 AND detailName = 'Event Info';
                """,
                (form_data['description'], form_data['remark1'], form_data['remark2'], form_data['remark3'])
            )

        if form_data['title'] or form_data['date'] or form_data['time1'] or form_data['time2'] or form_data['venue'] or form_data['distance']:
            time_start = f"{form_data['date']} {form_data['time1']}" 
            time_end = f"{form_data['date']} {form_data['time2']}"

            db.execute(
                """
                UPDATE Event
                SET eventName = %s,
                    eventDate = %s, 
                    eventStartTime = %s, 
                    eventEndTime = %s,
                    eventLocation = %s,
                    routeDistance = %s;
                """,
                (form_data['title'], form_data['date'], time_start, time_end, form_data['venue'], form_data['distance'])
            )
        self.db.commit()

    def update_event_image(self, event_detail_id, img_data):
        db = self.db.cursor()
        db.execute(
            """
            UPDATE EventDetails
            SET detailPicture = %s
            WHERE eventDetailId = %s
            """,
            (img_data, event_detail_id)
        )
        self.db.commit()

    def get_main_event_details(self):
        db = self.db.cursor()
        db.execute("""
            SELECT eventName, 
                   DATE(eventDate),
                   TIME(eventStartTime),
                   TIME(eventEndTime), 
                   eventLocation, 
                   routeDistance 
            FROM Event;
        """)
        result = db.fetchone()
        return {
            'name': result[0],
            'date': result[1],
            'time1': result[2],
            'time2': result[3],
            'venue': result[4],
            'distance': result[5],
        } if result else None

    def get_sub_event_details(self):
        db = self.db.cursor()
        db.execute("""
            SELECT JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.titleDesc')), 
                   JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.remark1')),
                   JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.remark2')),
                   JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.remark3')) 
            FROM eventDetails
            WHERE eventDetailId = 21 AND detailName = 'Event Info';
        """)
        result = db.fetchone()
        return {
            'description': result[0] or '',
            'info1': result[1] or '',
            'info2': result[2] or '',
            'info3': result[3] or ''
        } if result else None

    def get_past_event_images(self):
        db = self.db.cursor()
        db.execute("""
            SELECT eventDetailID, detailPicture 
            FROM EventDetails 
            WHERE eventDetailID BETWEEN 1 AND 5 AND detailName = 'Past Event Images';
        """)
        return db.fetchall()

# Student And Public Participant Page
    def get_student_participants(self):
        db = self.db.cursor()
        query = '''
            SELECT 
                U.userName,
                U.userEmail,
                U.userPhone,
                JSON_UNQUOTE(JSON_EXTRACT(U.userDescription, '$.matricNumber')) AS matricNumber,
                JSON_UNQUOTE(JSON_EXTRACT(U.userDescription, '$.package')) AS package,
                JSON_UNQUOTE(JSON_EXTRACT(U.userDescription, '$.tShirtSize')) AS tShirtSize,
                JSON_UNQUOTE(JSON_EXTRACT(U.userDescription, '$.campus')) AS campus,
                JSON_UNQUOTE(JSON_EXTRACT(U.userDescription, '$.school')) AS school,
                U.userStatus,
                T.totalAmount, 
                T.fileUploaded,
                T.fileName,
                JSON_UNQUOTE(JSON_EXTRACT(U.userDescription, '$.transport')) AS transport
            FROM Users U
            LEFT JOIN payment T ON T.userNumber = JSON_UNQUOTE(JSON_EXTRACT(U.userDescription, '$.matricNumber'))
            WHERE U.userType = 'student' AND T.fileName IS NOT NULL;
        '''
        db.execute(query)
        students = db.fetchall()
        db.close()
        return students


    def update_student_status(self, matricNumber, status):
        db = self.db.cursor()
        db.execute(
            'UPDATE users SET userStatus = %s WHERE JSON_UNQUOTE(JSON_EXTRACT(userDescription, "$.matricNumber")) = %s',
            (status, matricNumber)
        )
        self.db.commit()
        return db.rowcount > 0
    
    def get_public_participants(self):
        db = self.db.cursor()
        query = '''
            SELECT 
                userName,
                userEmail,
                userPhone,
                JSON_UNQUOTE(JSON_EXTRACT(userDescription, '$.ICNumber')) AS ICNumber,
                JSON_UNQUOTE(JSON_EXTRACT(userDescription, '$.package')) AS package,
                JSON_UNQUOTE(JSON_EXTRACT(userDescription, '$.tShirtSize')) AS tShirtSize,
                userStatus,
                T.totalAmount, 
                T.fileUploaded,
                T.fileName
            FROM Users U
            LEFT JOIN payment T ON T.userNumber = JSON_UNQUOTE(JSON_EXTRACT(U.userDescription, '$.ICNumber'))
            WHERE U.userType = 'public' AND T.fileName IS NOT NULL; 
        '''
        db.execute(query)
        publics = db.fetchall()
        db.close()
        return publics


    def update_public_status(self, ICNumber, status):
        db = self.db.cursor()
        db.execute(
            'UPDATE users SET userStatus = %s WHERE JSON_UNQUOTE(JSON_EXTRACT(userDescription, "$.ICNumber")) = %s',
            (status, ICNumber)
        )
        self.db.commit()
        return db.rowcount > 0
    
    def get_file(self, user_number):
        db = self.db.cursor()
        query = '''
            SELECT T.fileUploaded, T.fileName 
            FROM payment T
            WHERE T.userNumber = %s
        '''
        db.execute(query, (user_number,))
        result = db.fetchone()
        db.close()
        return result
    
# Event Route Page
    def update_route_detail_with_image(self, event_id, img_data, img_name):
            db = self.db.cursor()
            query = """
                UPDATE EventDetails
                SET 
                    detailPicture = %s,
                    detailDescription = CASE
                        WHEN JSON_CONTAINS_PATH(detailDescription, 'one', '$.imgName') THEN
                            JSON_SET(detailDescription, '$.imgName', %s)
                        ELSE
                            JSON_SET(detailDescription, '$.imgName', %s)  
                    END
                WHERE eventDetailId = %s
            """
            db.execute(query, (img_data, img_name, img_name, event_id))
            self.db.commit()

    def update_route_name(self, event_id, img_name):
        db = self.db.cursor()
        query = """
            UPDATE EventDetails
            SET detailDescription = CASE
                WHEN JSON_CONTAINS_PATH(detailDescription, 'one', '$.imgName') THEN
                    JSON_SET(detailDescription, '$.imgName', %s)
                ELSE
                    JSON_SET(detailDescription, '$.imgName', %s)  
            END
            WHERE eventDetailId = %s
        """
        db.execute(query, (img_name, img_name, event_id))
        self.db.commit()

    def get_route_details(self):
        db = self.db.cursor()
        query = """
            SELECT eventDetailId, detailPicture, JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.imgName')) AS detailDescription
            FROM EventDetails
            WHERE eventDetailId BETWEEN 6 AND 14 AND detailName = 'Route Images'
        """
        db.execute(query)
        results = db.fetchall()
        db.close()
        return results

    def rollback_transaction(self):
        self.db.rollback()

# Packages Page
    # Function to handle T-shirt size updates and inserts
    def update_tshirt_sizes(self, form_data):
        db = self.db.cursor(DictCursor)
        tshirt_sizes = []

        for key in form_data:
            if key.startswith('sizes['):
                if '[new]' in key:
                    field_name = key.split('[')[3].split(']')[0]
                    index = int(key.split('[')[2].split(']')[0])

                    while len(tshirt_sizes) <= index:
                        tshirt_sizes.append({"is_new": True})

                    tshirt_sizes[index][field_name] = form_data[key]
                else:
                    size_id = key.split('[')[1].split(']')[0]
                    field_name = key.split('[')[2].split(']')[0]

                    while len(tshirt_sizes) <= int(size_id):
                        tshirt_sizes.append({"sizeID": size_id})

                    tshirt_sizes[int(size_id)][field_name] = form_data[key]

        for size in tshirt_sizes:
            size_id = size.get('sizeID')
            size_name = size.get('sizeName')
            size_price = size.get('sizePrice')
            delete_flag = size.get('delete', '0')

            if delete_flag == '1' and size_id:
                db.execute("DELETE FROM Tshirt_size WHERE sizeID = %s", (size_id,))
                continue
            if size_id:
                db.execute("UPDATE Tshirt_size SET sizeName = %s, sizePrice = %s WHERE sizeID = %s",
                        (size_name, size_price, size_id))
            elif size.get("is_new"):
                db.execute("INSERT INTO Tshirt_size (sizeName, sizePrice) VALUES (%s, %s)",
                        (size_name, size_price))

        self.db.commit()


    # Function to handle item updates and inserts
    def update_items(self, form_data):
        db = self.db.cursor(DictCursor)
        items = []

        for key in form_data:
            if key.startswith('items['):
                if '[new]' in key:
                    field_name = key.split('[')[3].split(']')[0]
                    index = int(key.split('[')[2].split(']')[0])

                    while len(items) <= index:
                        items.append({"is_new": True})

                    items[index][field_name] = form_data[key]
                else:
                    item_id = key.split('[')[1].split(']')[0]
                    field_name = key.split('[')[2].split(']')[0]

                    while len(items) <= int(item_id):
                        items.append({"itemID": item_id})

                    items[int(item_id)][field_name] = form_data[key]

        for item in items:
            item_id = item.get('itemID')
            item_name = item.get('itemName')
            delete_flag = item.get('delete')

            if delete_flag == '1' and item_id:
                db.execute("UPDATE Items SET itemStatus = 'deleted' WHERE itemID = %s", (item_id,))
                continue
            if item_id:
                db.execute("UPDATE Items SET itemName = %s WHERE itemID = %s", (item_name, item_id))
            elif item.get("is_new"):
                db.execute("INSERT INTO Items (itemName, itemStatus) VALUES (%s, 'active')", (item_name,))

        self.db.commit()


    # Function to handle package updates and inserts
    def update_packages(self, form_data):
        db = self.db.cursor(DictCursor)
        packages = []

        for key in form_data:
            if key.startswith('packages['):
                if '[new]' in key:
                    index = int(key.split('[')[2].split(']')[0])

                    while len(packages) <= index:
                        packages.append({"is_new": True, "items": []})

                    if '[items]' in key:
                        item_id = key.split('[')[4].split(']')[0]
                        item_name = form_data[key]
                        packages[index]["items"].append({"itemID": item_id, "itemName": item_name})
                    else:
                        field_name = key.split('[')[3].split(']')[0]
                        packages[index][field_name] = form_data[key]
                else:
                    package_id = key.split('[')[1].split(']')[0]

                    if len(packages) <= int(package_id):
                        packages.append({
                            "packageID": form_data.get(f"packages[{package_id}][packageID]"),
                            "packageName": form_data.get(f"packages[{package_id}][packageName]"),
                            "price": form_data.get(f"packages[{package_id}][price]"),
                            "items": []
                        })

                    if 'items' in key:
                        item_index = int(key.split('[')[3].split(']')[0])
                        item_name = form_data[key]

                        if item_name:
                            packages[int(package_id)]["items"].append({
                                "itemID": item_index,
                                "itemName": item_name
                            })

        for package in packages:
            package_id = package.get('packageID')
            package_name = package.get('packageName')
            price = package.get('price')
            items_in_package = package.get('items', [])
            has_tshirt = any(item['itemName'].lower() == "t-shirt" for item in items_in_package)

            if package_id:
                db.execute("UPDATE Packages SET packageName = %s, price = %s WHERE packageID = %s",
                        (package_name, price, package_id))

                db.execute("SELECT itemID FROM Packages WHERE packageID = %s", (package_id,))
                current_items = {row['itemID'] for row in db.fetchall()}

                items_to_delete = current_items - {item['itemID'] for item in items_in_package}
                for item_id in items_to_delete:
                    db.execute("DELETE FROM Packages WHERE packageID = %s AND itemID = %s",
                            (package_id, item_id))

                items_to_add = {item['itemID'] for item in items_in_package} - current_items
                for item_id in items_to_add:
                    db.execute("INSERT INTO Packages (packageID, packageName, price, hasTShirt, itemID) VALUES (%s, %s, %s, %s, %s)",
                            (package_id, package_name, price, has_tshirt, item_id))
            elif package.get("is_new"):
                db.execute("SELECT MAX(packageID) + 1 AS new_package_id FROM Packages")
                new_package_id = db.fetchone()["new_package_id"]

                for item in package["items"]:
                    db.execute("INSERT INTO Packages (packageID, packageName, price, hasTShirt, itemID) VALUES (%s, %s, %s, %s, %s)",
                            (new_package_id, package["packageName"], package["price"], has_tshirt, item["itemID"]))

        self.db.commit()

    # Function to fetch T-shirt sizes
    def get_tshirt_sizes(self):
        db = self.db.cursor(DictCursor)
        db.execute("SELECT sizeID, sizeName, sizePrice FROM Tshirt_size ORDER BY sizeID")
        return db.fetchall()

    # Function to fetch active items
    def get_items(self):
        db = self.db.cursor(DictCursor)
        db.execute("SELECT itemID, itemName FROM Items WHERE itemStatus = 'active' ORDER BY itemID")
        return db.fetchall()

    # Function to fetch active packages and their items
    def get_packages(self):
        db = self.db.cursor(DictCursor)
        db.execute("""
            SELECT p.packageID, p.packageName, p.price, i.itemID, i.itemName
            FROM Packages p
            LEFT JOIN Items i ON i.itemID = p.itemID
            WHERE p.packageStatus = 'active' AND i.itemStatus = 'active'
            ORDER BY p.packageID, p.itemID;
        """)
        raw_packages = db.fetchall()

        packages = {}
        for row in raw_packages:
            package_id = row['packageID']
            if package_id not in packages:
                packages[package_id] = {
                    'packageID': package_id,
                    'packageName': row['packageName'],
                    'price': row['price'],
                    'items': []
                }
            if row['itemID']:
                packages[package_id]['items'].append({
                    'itemID': row['itemID'],
                    'itemName': row['itemName']
                })

        return list(packages.values())
    
# About Us Page
    def update_event_details(self, request):
        db = self.db.cursor()
        profile_name1 = request.form.get('name1')  
        profile_name2 = request.form.get('name2')  
        profile_file = request.files.get('profile') 

        if profile_file:
            img_data = profile_file.read()
            db.execute(
                """
                UPDATE EventDetails
                SET 
                    detailPicture = %s,
                    detailDescription = JSON_SET(detailDescription, '$.name1', %s),
                    detailDescription = JSON_SET(detailDescription, '$.name2', %s)
                WHERE detailName = 'Organiser Profile'
                """,
                (img_data, profile_name1, profile_name2)
            )
        else:
            db.execute(
                """
                UPDATE EventDetails
                SET 
                    detailDescription = JSON_SET(detailDescription, '$.name1', %s),
                    detailDescription = JSON_SET(detailDescription, '$.name2', %s)
                WHERE detailName = 'Organiser Profile'
                """,
                (profile_name1, profile_name2)
            )

        self.db.commit()

    def update_social_links(self, request):
        sociallink1 = request.form.get('link1')
        sociallink2 = request.form.get('link2')
        sociallink3 = request.form.get('link3')
        sociallink4 = request.form.get('link4')
        sociallink5 = request.form.get('link5')
        db = self.db.cursor()
        db.execute(
            """
            UPDATE EventDetails
            SET 
                detailDescription = JSON_SET(detailDescription, '$.linkName1', %s),
                detailDescription = JSON_SET(detailDescription, '$.linkName2', %s),
                detailDescription = JSON_SET(detailDescription, '$.linkName3', %s),
                detailDescription = JSON_SET(detailDescription, '$.linkName4', %s),
                detailDescription = JSON_SET(detailDescription, '$.linkName5', %s)
            WHERE detailName = 'Social Link'
            """,
            (sociallink1, sociallink2, sociallink3, sociallink4, sociallink5)
        )

        self.db.commit()

    def update_other_link(self, request):
        other_social_data = {}
        for i in range(1, 13):
            other_social_data[f'eventname{i}'] = request.form.get(f'text{i * 2 - 1}')
            other_social_data[f'eventlink{i}'] = request.form.get(f'text{i * 2}')

        # Updating events in database
        db = self.db.cursor()
        db.execute(
            """
            UPDATE EventDetails
            SET 
                detailDescription = JSON_SET(detailDescription, '$.eventName1', %s),
                detailDescription = JSON_SET(detailDescription, '$.linkName1', %s),
                detailDescription = JSON_SET(detailDescription, '$.eventName2', %s),
                detailDescription = JSON_SET(detailDescription, '$.linkName2', %s),
                detailDescription = JSON_SET(detailDescription, '$.eventName3', %s),
                detailDescription = JSON_SET(detailDescription, '$.linkName3', %s),
                detailDescription = JSON_SET(detailDescription, '$.eventName4', %s),
                detailDescription = JSON_SET(detailDescription, '$.linkName4', %s),
                detailDescription = JSON_SET(detailDescription, '$.eventName5', %s),
                detailDescription = JSON_SET(detailDescription, '$.linkName5', %s),
                detailDescription = JSON_SET(detailDescription, '$.eventName6', %s),
                detailDescription = JSON_SET(detailDescription, '$.linkName6', %s),
                detailDescription = JSON_SET(detailDescription, '$.eventName7', %s),
                detailDescription = JSON_SET(detailDescription, '$.linkName7', %s),
                detailDescription = JSON_SET(detailDescription, '$.eventName8', %s),
                detailDescription = JSON_SET(detailDescription, '$.linkName8', %s),
                detailDescription = JSON_SET(detailDescription, '$.eventName9', %s),
                detailDescription = JSON_SET(detailDescription, '$.linkName9', %s),
                detailDescription = JSON_SET(detailDescription, '$.eventName10', %s),
                detailDescription = JSON_SET(detailDescription, '$.linkName10', %s),
                detailDescription = JSON_SET(detailDescription, '$.eventName11', %s),
                detailDescription = JSON_SET(detailDescription, '$.linkName11', %s),
                detailDescription = JSON_SET(detailDescription, '$.eventName12', %s),
                detailDescription = JSON_SET(detailDescription, '$.linkName12', %s)
            WHERE detailName = 'Other Social Link'
            """,
            tuple(other_social_data.values())
        )

        self.db.commit()

    def get_profile_data(self):
        db = self.db.cursor()
        db.execute("""
            SELECT detailPicture AS picture, 
                   JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.name1')) AS name1,
                   JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.name2')) AS name2
            FROM EventDetails
            WHERE detailName = 'Organiser Profile'
        """)
        return db.fetchall()
        
    def get_social_links(self):
        db = self.db.cursor()
        db.execute("""
            SELECT 
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.linkName1')) AS linkName1,
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.linkName2')) AS linkName2,
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.linkName3')) AS linkName3,
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.linkName4')) AS linkName4,
                JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.linkName5')) AS linkName5
            FROM EventDetails
            WHERE detailName = 'Social Link'
        """)
        return db.fetchall()

    def get_other_social_links(self):
        db = self.db.cursor()
        db.execute("""
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
            FROM EventDetails
            WHERE detailName = 'Other Social Link'
        """)
        return db.fetchall()

# Contact Us Page
    def update_contact_us(self, form_data):
        # Extract data from form
        message = form_data['message']
        title = form_data['title']
        position = form_data['position']
        name = form_data['name']
        contact = form_data['contact']
        img_file = form_data['img_file']

        db = self.db.cursor()
        
        # Handle profile picture and update database
        if img_file:
            img_data = img_file.read()
            db.execute(
                """
                UPDATE EventDetails
                SET 
                    detailPicture = %s,
                    detailDescription = JSON_SET(detailDescription, '$.message', %s),
                    detailDescription = JSON_SET(detailDescription, '$.title', %s),
                    detailDescription = JSON_SET(detailDescription, '$.position', %s),
                    detailDescription = JSON_SET(detailDescription, '$.name', %s),
                    detailDescription = JSON_SET(detailDescription, '$.contact', %s)
                WHERE eventDetailId = 19
                """,
                (img_data, message, title, position, name, contact)
            )
        else:
            db.execute(
                """
                UPDATE EventDetails
                SET 
                    detailDescription = JSON_SET(detailDescription, '$.message', %s),
                    detailDescription = JSON_SET(detailDescription, '$.title', %s),
                    detailDescription = JSON_SET(detailDescription, '$.position', %s),
                    detailDescription = JSON_SET(detailDescription, '$.name', %s),
                    detailDescription = JSON_SET(detailDescription, '$.contact', %s)
                WHERE eventDetailId = 19
                """,
                (message, title, position, name, contact)
            )

        # For second set of data (eventDetailId = 20)
        title2 = form_data['title2']
        position2 = form_data['position2']
        name2 = form_data['name2']
        contact2 = form_data['contact2']
        img_file2 = form_data['img_file2']
        
        if img_file2:
            img_data2 = img_file2.read()
            db.execute(
                """
                UPDATE EventDetails
                SET 
                    detailPicture = %s,
                    detailDescription = JSON_SET(detailDescription, '$.title', %s),
                    detailDescription = JSON_SET(detailDescription, '$.position', %s),
                    detailDescription = JSON_SET(detailDescription, '$.name', %s),
                    detailDescription = JSON_SET(detailDescription, '$.contact', %s)
                WHERE eventDetailId = 20
                """,
                (img_data2, title2, position2, name2, contact2)
            )
        else:
            db.execute(
                """
                UPDATE EventDetails
                SET 
                    detailDescription = JSON_SET(detailDescription, '$.title', %s),
                    detailDescription = JSON_SET(detailDescription, '$.position', %s),
                    detailDescription = JSON_SET(detailDescription, '$.name', %s),
                    detailDescription = JSON_SET(detailDescription, '$.contact', %s)
                WHERE eventDetailId = 20
                """,
                (title2, position2, name2, contact2)
            )

        self.db.commit()

    def get_contact_us_data(self):
        db = self.db.cursor()
        # Retrieve data for eventDetailId = 19
        db.execute("""
            SELECT detailPicture, 
                   JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.message')),
                   JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.title')),
                   JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.position')),
                   JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.name')),
                   JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.contact'))
            FROM EventDetails
            WHERE eventDetailId = 19 AND detailName = 'Contact Us'
        """)
        return db.fetchall()
    
    def get_contact_us_data2(self):
        try:
            db = self.db.cursor()
            db.execute("""
                SELECT detailPicture, 
                    JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.title')),
                    JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.position')),
                    JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.name')),
                    JSON_UNQUOTE(JSON_EXTRACT(detailDescription, '$.contact'))
                FROM EventDetails
                WHERE eventDetailId = 20 AND detailName = 'Contact Us'
            """)
            return db.fetchall()
        except Exception as e:
            print(f"Error in get_contact_us_data2: {str(e)}")
            return None