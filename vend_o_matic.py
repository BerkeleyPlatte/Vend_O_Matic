from flask import Flask, request, jsonify

vend_o_matic = Flask(__name__)

class VendingMachine:
    def __init__(self):
        # I know the requirements didn't call for a repository for the coins that 
        # actually purchase the drinks, but I like that the coins don't just disappear 
        # once the transaction is complete
        self.bank = 0
        self.price = 2
        self.coins_in = 0
        # 'your drink' is an attempt to make the number of items vended dynamic
        self.your_drink = 0
        self.change = 0
        self.inventory = {'1': 5,
                          '2': 5,
                          '3': 5}
    
    # this method handles the transaction    
    def purchase(self, drink):
        self.bank += 2
        self.change = self.coins_in - self.price
        self.inventory[drink] -= 1
        self.coins_in = 0
        self.your_drink += 1
        
m = VendingMachine()

@vend_o_matic.route('/inventory', methods = ['GET'])
def get_drink_quantites():

    # returns the undifferentiated quantities per the exercise requirements
    data = [int(each) for each in m.inventory.values()]
    response = jsonify(data)
    response.status_code = 200

    return response

@vend_o_matic.route('/inventory/<int:id>', methods = ['GET'])
def get_quantity_for_single_drink(id):
    
    data = int(m.inventory[str(id)])
    response = jsonify(data)
    response.status_code = 200
    
    return response

@vend_o_matic.route('/', methods = ['PUT'])
def insert_coins():
        
    data = request.get_json(force=True)
    response = jsonify(data)
    # puts a coin in the slot
    m.coins_in += int(data['coin'])
    response.headers['X-Coins'] = m.coins_in
    response.status_code = 204

    return response

@vend_o_matic.route('/inventory/<int:id>', methods = ['PUT'])
def sale(id):
    # this turns the id into a string so it can be matched to a key in the 
    # VendingMachine's inventory dictionary
    drink = str(id)

    if m.inventory[drink] > 0:
        if m.coins_in >= m.price:
            # here's where the transaction finally actually happens
            m.purchase(drink)
            data = {'quantity': m.your_drink}
            # while the amount of coins inserted can be safely reset at the time 
            # of purchase, that which is returned to the user (their drink and
            # their change) can only be reset after their values are appropriately
            # allocated
            m.your_drink = 0
            response = jsonify(data)
            response.headers['X-Coins'] = m.change
            m.change = 0
            response.headers['X-Inventory-Remaining'] = m.inventory[drink]
            response.status_code = 200
        else:
            response = jsonify()
            response.headers['X-Coins'] = m.coins_in
            response.status_code = 403
    else:
        response = jsonify()
        response.headers['X-Coins'] = m.coins_in
        response.status_code = 404

    return response

# for when the user decides they'd rather save their money (cancels the transaction)
@vend_o_matic.route('/', methods = ['DELETE'])
def cancel_sale():

    response = jsonify()
    response.headers['X-Coins'] = m.coins_in
    # because the coins are returned, they're no longer in the machine
    m.coins_in = 0
    response.status_code = 204

    return response

if __name__ == '__main__':
    vend_o_matic.run()