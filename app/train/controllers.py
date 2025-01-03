from bson.objectid import ObjectId
from flask import Blueprint, request, jsonify
from app.intents.models import Intent

train = Blueprint('train_blueprint', __name__,
                  url_prefix='/train')


@train.route('/<story_id>/data', methods=['POST'])
def save_training_data(story_id):
    """
    Save training data for given story
    :param story_id:
    :return:
    """
    story = Intent.objects.get(id=ObjectId(story_id))
    story.trainingData = request.json
    story.save()
    return jsonify({"result": True})


@train.route('/<story_id>/data', methods=['GET'])
def get_training_data(story_id):
    """
    retrieve training data for a given story
    :param story_id:
    :return:
    """
    story = Intent.objects.get(id=ObjectId(story_id))
    return jsonify(story.trainingData)
