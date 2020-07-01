from app import api, mongo
from flask_restful import Resource, reqparse
from flask import request, make_response, jsonify
import os
from functools import wraps

drugs = mongo.db.drugs


def require_key(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if request.args.get('x-drug-key') and request.args.get('x-drug-key') == "drug-key-key":
            return view_function(*args, **kwargs)
        else:
            return make_response(jsonify({"message": "Unauthorized access at " + request.url, "status": False}), 403)
    return decorated_function


class AddDrugs(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, help="This field cannot be left blank")
    parser.add_argument('price', type=str, required=True, help="This field cannot be left blank")

    @require_key
    def post(self):
        data = AddDrugs.parser.parse_args()
        if ' '.join(data['name'].split()) == '':
            return {"message": "stakeholder field cannot be empty", "status": False}, 404
        elif ' '.join(data['price'].split()) == '':
            return {"message": "stakeholder field cannot be empty", "status": False}, 404
        else:
            if drugs.find_one({"name": data['name'].lower()}):
                return {"message": "drug name {} already exists".format(data['name']), "status": False}, 404
            else:
                all_drugs = {"name": data['name'].lower(), "price": data['price']}
                drugs.insert(all_drugs)
                return {"message": "NGN{} {} added successfully".format(data['price'], data['name'].title()), "status": True}, 200


api.add_resource(AddDrugs, '/adddrug')


class GetADrug(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, help="This field cannot be left blank")

    @require_key
    def get(self):
        data = GetADrug.parser.parse_args()
        if ' '.join(data['name'].split()) == '':
            return {"message": "name field cannot be empty", "status": False}, 404
        else:
            d = drugs.find_one({"name": data['name'].lower()})
            if not d:
                return {"message": " {} does not exists".format(data['name']), "status": False}, 404
            else:
                return {
                    "name": d['name'].title(),
                    "price": "NGN"+d['price'],
                    "status": True
                }, 200


api.add_resource(GetADrug, '/getadrug')


class GetAllDrugs(Resource):

    @require_key
    def get(self):
        out = []
        for q in drugs.find():
            out.append({"name": q['name'].title(), "price": "NGN"+q['price']})
        return {
            "total": drugs.count(),
            "drugs": out,
            "status": True
        }, 200


api.add_resource(GetAllDrugs, '/getalldrugs')


class UpdateDrug(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, help="This field cannot be left blank")
    parser.add_argument('price', type=str, required=True, help="This field cannot be left blank")

    @require_key
    def put(self):
        data = UpdateDrug.parser.parse_args()
        if ' '.join(data['name'].split()) == '':
            return {"message": "name field cannot be empty", "status": False}, 404
        elif ' '.join(data['price'].split()) == '':
            return {"message": "price already the same", "status": False}, 404
        elif int(data['price']) < 1:
            return {"message": "invalid price", "status": False}, 404
        else:
            d = drugs.find_one({"name": data['name'].lower()})
            if not d:
                return {"message": "{} does not exist".format(data['name']), "status": False}, 404
            elif d['price'] == data['price']:
                return {"message": "cannot update same price", "status": False}, 404
            else:
                drugs.update_one({"name": data['name']}, {"$set": {"price": data['price']}})
                return {"message": "{} price successfully updated to NGN{}".format(data['name'], data['price']), "status": True}, 200


api.add_resource(UpdateDrug, '/updatedrugs')


class DeleteDrug(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, help="This field cannot be left blank")

    @require_key
    def delete(self):
        data = DeleteDrug.parser.parse_args()
        if ' '.join(data['name'].split()) == '':
            return {"message": "name field cannot be empty", "status": False}, 404
        else:
            if not drugs.find_one({"name": data['name'].lower()}):
                return {"message": "{} does not exist".format(data['name']), "status": False}, 404
            else:
                d = drugs.find_one({"name": data['name']})
                drugs.remove(d)
                return {"message": "{} successfully deleted".format(data['name']), "status": True}, 200


api.add_resource(DeleteDrug, '/deletedrug')

