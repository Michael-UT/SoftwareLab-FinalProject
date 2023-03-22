from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)
app.config['MONGO_URI'] ="mongodb+srv://goblin:Password1234@database.kbcy6ct.mongodb.net/?retryWrites=true&w=majority"
mongo = PyMongo(app)

'''
Structure of User entry so far:
User = {
    "Username": username,
    "UserID": userid,
    "Password": password,
    "Items": {item1:qty1, item2:qty2, ....}
}
'''

# Function tries to login a user with their provided Username and Password
# Returns json specfiying if the user login attempt was successful or not
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('Username') # username, password are taken in from the webpage html
    password = request.json.get('Password')

    user = mongo.HardwareCheckout.Users.find_one({'Username': username})    # access the hardware checkout database -> users collection

    if user and user['Password'] == password:
        return jsonify({'success': True, 'message': 'Login successful!'})
    else:
        return jsonify({'success': False, 'message': 'Invalid username or password.'})


# Function tries to create a user with their provided Username and Password
# Returns json specfiying if the user creation was successful or not
@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.json.get('Username')
    password = request.json.get('Password')

    # Check if the user already exists in the database
    existing_user = mongo.HardwareCheckout.Users.find_one({'Username': username})
    if existing_user:
        return jsonify({'success': False, 'message': 'User already exists.'})

    # If the user doesn't exist already, add them to the database
    new_user = {'Username': username, 'Password': password}
    result = mongo.HardwareCheckout.Users.insert_one(new_user)

    return jsonify({'success': True, 'message': 'User added successfully.'})

'''
Structure of Project entry so far:
Project = {
    "Name": projectName,
    "ProjectID": projectID,
    "Description": description
    "HardwareSets": [HW1_ID, HW2_ID, ...]
    # Should probably be a map with HWSetName and amount used by this project
}
'''
@app.route('/add_project', methods=['POST'])
def add_project():
    projectName = request.json.get('Name')
    projectID = request.json.get('ProjectID')
    description = request.json.get('Description')

    db = mongo.HardwareCheckout
    projects = db.Projects
    success = False
    
    # Keep track of HW sets for this project
    if projects.find({"Name": projectName, "ProjectID": projectID}).count() == 0:
        doc = {
            "Name": projectName,
            "ProjectID": projectID,
            "Description": description
        }
        projects.insert_one(doc)
        return jsonify({'success': True, 'message': 'Project added successfully.'})

    return jsonify({'success': False, 'message': 'Project already exists.'})


'''
Structure of Hardware Set entry so far:
HardwareSet = {
    "Name": hwSetName,
    "Capacity": initialCapacity,
    "Availability": initialCapacity
}
'''

@app.route('/add_project', methods=['POST'])
def add_hardware_set():
    hwSetName = request.json.get('Name')
    initCapacity = request.json.get('initCapacity')

    db = mongo.HardwareCheckout
    hwsets = db.HardwareSets
    
    doc = {
        "Name": hwSetName,
        "Capacity": str(initCapacity),
        "Availability": str(initCapacity)
    }

    hwsets.insert_one(doc)

# Function tries to create a user with their provided Username and Password
# Returns json specfiying if the user creation was successful or not
@app.route('/check_in', methods=['POST'])
def check_in():
    username = request.json.get('Username')
    hardwareItem = request.json.get('HardwareItem')
    quantity = request.json.get('Quantity')
    
    # Check if the user exists in the database
    user = mongo.HardwareCheckout.Users.find_one({'Username': username})
    if not user:
        return jsonify({'success': False, 'message': 'Username invalid. Unable to check in item'})

    # Update the inventory of the checked in item
    item = mongo.HardwareCheckout.HardwareSets.find_one({'Name': hardwareItem})
    # If item doesn't already exist in inventory, create it and intialize capacity and available values to quantity provided
    if not item:
        item = {'Name': hardwareItem, 'Available': quantity, 'Capacity': quantity}
        mongo.HardwareCheckout.HardwareSets.insert_one(item)
    # Item exists; update availability
    else:
        item['Available'] += quantity
        mongo.HardwareCheckout.HardwareSets.update_one({'_id': item['_id']}, {'$set': {'Available': item['Available']}})

    # Update the user's data
    if hardwareItem not in user['Items']:
        user['Items'][item_name] = quantity
    else:
        user['Items'][item_name] += quantity
    mongo.HardwareCheckout.Users.update_one({'_id': user['_id']}, {'$set': {'Items': user['Items']}})

    # return json success message
    return jsonify({'success': True, 'message': f'Item {hardwareItem} checked in successfully.'})


@app.route('/check_out', methods=['POST'])
def check_out():
    username = request.json.get('Username')
    hardwareItem = request.json.get('HardwareItem')
    quantity = request.json.get('Quantity')

    # Check if the user exists in the database
    user = mongo.HardwareCheckout.Users.find_one({'Username': username})
    if not user:
        return jsonify({'success': False, 'message': 'Username invalid. Unable to check in item'})

    # Check if the item exists in the inventory
    item = mongo.HardwareCheckout.HardwareSets.find_one({'Name': hardwareItem})
    if not item:
        return jsonify({'success': False, 'message': 'Item not found.'})

    # Check if enough of the item is available
    if quantity > user['Available']:
        return jsonify({'success': False, 'message': f'Not enough quantity of {hardwareItem} available'})

    # Checkout the item and update the inventory
    item['Quantity'] -= quantity

    # Add the quantity of hardwareItem to the user's profile
    if hardwareItem in user['Items']:
        user['Items'][hardwareItem]+= quantity
    else:
        user['Items'][hardwareItem]= quantity # if the tool isn't in the user's profile, add it to the dictionary
    
    mongo.db.inventory.update_one({'_id': item['_id']}, {'$set': {'quantity': item['quantity']}})

    # Update the user's data
    user['Items'][hardwareItem] -= quantity

    # mongo.HardwareCheckout.HardwareSets refers to the HardwareSets collection in the mongoDB
    mongo.HardwareCheckout.HardwareSets.update_one({'_id': item['_id']}, {'$set': {'Available': item['Available']}})
    mongo.HardwareCheckout.Users.update_one({'_id': user['_id']}, {'$set': {'Items': user['Items']}})

    return jsonify({'success': True, 'message': 'Item checked out successfully.'})

if __name__ == '__main__':
    app.run(debug=True)