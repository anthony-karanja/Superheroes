from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from models import db, Hero, Power, HeroPower

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///superheroes.db"
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False

migrate = Migrate(app,db)

db.init_app(app)

@app.route('/heros')
def get_heroes():
    heros = Hero.query.all()
    return jsonify([{
        'id':hero.id,
        'name': hero.name,
        'super_name': hero.super_name
    }
        for hero in heros
                    ])
    
@app.route('/heros/<int:id>')
def heroes_by_id(id):
    hero = Hero.query.get(id)
    if not hero:
        return jsonify({'error': 'Hero not found'}), 404

    hero_details = hero.to_dict(only=('id', 'name', 'super_name'))
    hero_details['hero_powers'] = [
        {
            'hero_id': hero_power.hero_id,
            'id': hero_power.id,
            'power': hero_power.power.to_dict(only=('description', 'id', 'name')),
            'power_id': hero_power.power_id,
            'strength': hero_power.strength
        }
        for hero_power in hero.hero_powers
    ]
    return jsonify(hero_details), 200

@app.route('/power')
def get_power():
    powers = Power.query.all()
    return jsonify([{
        'id':power.id,
        'name': power.name,
        'super_name': power.super_name
    }
        for power in powers
                    ])
    
@app.route('/powers/<int:id>')
def powers_by_id(id):
    try:
        power = Power.query.get(id)
        return jsonify([{
            'description': Power.description,        
            'id': Power.id, 
            'name': Power.name        
            }])
    except Exception :
        return jsonify({'error: Power not found'}), 404
    
    
@app.route('/powers/<int:id>', methods=['PATCH'])    
def update_power_by_id(id):
    try:
        power = Power.query.get(id)
        if not power:
            return jsonify({"error": "Power not found"}), 404

        data = request.get_json()
        new_description = data.get('description')
        if new_description:
            power.description = new_description
            db.session.commit()

        return jsonify({
            "id": power.id,
            "name": power.name,
            "description": power.description
        })

    except Exception as e:
        print(f" {e}")
        return make_response(jsonify({"error": "Power not found"}), 500)
    

@app.route('/hero_powers', methods=['POST'])
def add_hero_power():
    data = request.get_json()
 
    if 'strength' not in data:
        return jsonify({'error': ['Strength is required']}), 400

    hero = Hero.query.get(data['hero_id'])
    power = Power.query.get(data['power_id'])

    if not hero:
        return jsonify({'error': 'Hero not found'}), 404
    
    if not power:
        return jsonify({'error': 'Power not found'}), 404

    try:
        hero_power = HeroPower(
            strength=data["strength"],
            hero_id=data["hero_id"],
            power_id=data["power_id"]
        )
        db.session.add(hero_power)
        db.session.commit()

        hero_power_details = hero_power.to_dict(only=('id', 'hero_id', 'power_id', 'strength'))
        hero_power_details['hero'] = hero_power.hero.to_dict(only=('id', 'name', 'super_name'))
        hero_power_details['power'] = hero_power.power.to_dict(only=('id', 'name', 'description'))

        return jsonify(hero_power_details), 201

    except ValueError as exc:
        db.session.rollback()
        return jsonify({'errors': str(exc)}), 400
    

if __name__ == '__main__':
    app.run(port=5555, debug=True)