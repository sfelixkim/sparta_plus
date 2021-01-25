from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import requests
import html

app = Flask(__name__)

client = MongoClient("localhost", 27017)
db = client.dbsparta_plus


@app.route('/')
def main():
    return render_template("index.html")


@app.route('/detail/<keyword>')
def detail(keyword):
    status_receive=request.args.get("status_give")
    if status_receive is None: status_receive="new"
    r = requests.get(f"https://owlbot.info/api/v4/dictionary/{keyword}", headers={"Authorization": "Token 990c8653785cd4bf04ba012237c7f0ba3d49b50f"})
    if r.status_code != 200:
        return redirect(url_for("main"))
    result = r.json()
    for definition in result["definitions"]:
        # print(type(definition["example"]))
        # if definition["definition"] is not None:
        definition["definition"] = definition["definition"].encode('ascii', 'ignore').decode('utf-8')
        if definition["example"] is not None:
            # definition["example"] = html.unescape(definition["example"].encode('ascii', 'xmlcharrefreplace').decode('utf-8'))
            definition["example"] = definition["example"].encode('ascii', 'ignore').decode('utf-8')
    return render_template("detail2.html", word=keyword, status=status_receive, result=result)


@app.route('/api/get_list', methods=['GET'])
def get_list():
    result = list(db.words.find({}, {'_id': 0}))
    return jsonify({'result': 'success', 'words': result})


@app.route('/api/save_word', methods=['POST'])
def save_word():
    word_receive = request.form['word_give']
    definition_receive = request.form['definition_give']
    doc = {"word": word_receive, "definition": definition_receive}
    db.words.insert_one(doc)
    return jsonify({'result': 'success', 'msg': f'word "{word_receive}" saved'})


@app.route('/api/delete_word', methods=['POST'])
def delete_word():
    word_receive = request.form['word_give']
    db.words.delete_one({"word":word_receive})
    return jsonify({'result': 'success', 'msg': f'word "{word_receive}" deleted'})


@app.route('/api/get_examples', methods=['GET'])
def get_exs():
    word_receive = request.args.get("word_give")
    result = list(db.examples.find({"word": word_receive}, {'_id': 0}))
    print(word_receive, len(result))

    return jsonify({'result': 'success', 'examples': result})

@app.route('/api/save_ex', methods=['POST'])
def save_ex():
    word_receive = request.form['word_give']
    example_receive = request.form['example_give']
    doc = {"word": word_receive,
           "example": example_receive}
    db.examples.insert_one(doc)
    return jsonify({'result': 'success', 'msg': f'example "{example_receive}" saved'})


@app.route('/api/delete_ex', methods=['POST'])
def delete_ex():
    word_receive = request.form['word_give']
    number_receive = int(request.form["number_give"])
    example = list(db.examples.find({"word":word_receive}))[number_receive]["example"]
    print(word_receive, example)
    db.examples.delete_one({"word":word_receive, "example":example})
    return jsonify({'result': 'success', 'msg': f'example #{number_receive} of "{word_receive}" deleted'})


# @app.route('/api/get_one', methods=['GET'])
# def get_one():
#     word_receive = request.args.get('word_give')
#     result = db.words.find_one({"word": word_receive}, {'_id': 0})
#     if result is None:
#         r = requests.get(f"https://owlbot.info/api/v4/dictionary/{word_receive}", headers={"Authorization": "Token 990c8653785cd4bf04ba012237c7f0ba3d49b50f"})
#         if r.status_code != 200:
#             return redirect(url_for("main"))
#         result = r.json()
#     return jsonify({'result': 'success', 'word': result})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
