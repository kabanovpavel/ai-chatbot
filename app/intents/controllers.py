import os
from bson.json_util import dumps
from bson.json_util import loads
from bson.objectid import ObjectId
from flask import Blueprint, request, Response, jsonify
from flask import abort
from flask import current_app as app
from app.commons.utils import update_document
from app.intents.models import ApiDetails
from app.intents.models import Intent
from app.intents.models import Parameter
from app.nlu.training import train_models

intents = Blueprint('intents_blueprint', __name__,
                    url_prefix='/intents')


@intents.route('/', methods=['POST'])
def create_intent():
    """
    Create a story from the provided json
    :return:
    """
    content = request.get_json(silent=True)

    intent = Intent()
    intent.name = content.get("name")
    intent.intentId = content.get("intentId")
    intent.speechResponse = content.get("speechResponse")
    intent.trainingData = []

    if content.get("apiTrigger") is True:
        intent.apiTrigger = True
        api_details = ApiDetails()
        isJson = content.get("apiDetails").get("isJson")
        api_details.isJson = isJson
        if isJson:
            api_details.jsonData = content.get("apiDetails").get("jsonData")

        api_details.url = content.get("apiDetails").get("url")
        api_details.headers = content.get("apiDetails").get("headers")
        api_details.requestType = content.get("apiDetails").get("requestType")
        intent.apiDetails = api_details
    else:
        intent.apiTrigger = False

    if content.get("parameters"):
        for param in content.get("parameters"):
            parameter = Parameter()
            update_document(parameter, param)
            intent.parameters.append(parameter)
    try:
        story_id = intent.save()
    except Exception as e:
        return jsonify({"error": str(e)})

    return jsonify({
        "_id": str(story_id.id)
    })


@intents.route('/')
def read_intents():
    """
    find list of intents for the agent
    :return:
    """
    all_intents = Intent.objects
    return Response(all_intents.to_json(), mimetype='application/json', status=200)


@intents.route('/<id>')
def read_intent(id):
    """
    Find details for the given intent id
    :param id:
    :return:
    """
    return Response(response=dumps(
        Intent.objects.get(
            id=ObjectId(id)).to_mongo().to_dict()),
        status=200,
        mimetype="application/json")


@intents.route('/<id>', methods=['PUT'])
def update_intent(id):
    """
    Update a story from the provided json
    :return:
    """
    json_data = loads(request.get_data())
    intent = Intent.objects.get(id=ObjectId(id))
    intent = update_document(intent, json_data)
    intent.save()
    return jsonify({"status": "success"})


@intents.route('/<id>', methods=['DELETE'])
def delete_intent(id):
    """
    Delete a intent
    :param id:
    :return:
    """
    Intent.objects.get(id=ObjectId(id)).delete()

    try:
        train_models()
    except BaseException:
        pass

    # remove NER model for the deleted story
    try:
        os.remove("{}/{}.model".format(app.config["MODELS_DIR"], id))
    except OSError:
        pass
    return jsonify({"result": True})
