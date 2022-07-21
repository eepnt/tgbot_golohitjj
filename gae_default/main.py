import flask, logging, requests, os

import google.cloud.logging
google.cloud.logging.Client().setup_logging()

# gcp cloud storage
from google.cloud import storage
storage_client = storage.Client()

# get cloud debugger
try:
  import googleclouddebugger
  googleclouddebugger.enable(
    breakpoint_enable_canary=False
  )
except ImportError:
  print('cannot load cloud debugger')

# get secret
from google.cloud import secretmanager
tgbot_token = secretmanager.SecretManagerServiceClient().access_secret_version(
    request=secretmanager.AccessSecretVersionRequest({
        "name": "projects/{}/secrets/tgbot_secret/versions/1".format(os.environ['USER_GAE_PROJECT_ID'])
    })
).payload.data.decode("UTF-8")

app = flask.Flask(__name__)

@app.route('/', methods=["POST"])
def recv_tgmsg():
    file_link = None
    try:
        data = flask.request.get_json()
        if "message" not in data or "photo" not in data["message"]:
            return ""
        logging.info(data)
        get_file = requests.get('https://api.telegram.org/bot{}/getFile?file_id={}'.format(
            tgbot_token, data["message"]["photo"][-1]["file_id"],
        )).json()
        logging.info(get_file)

        file_link = 'https://api.telegram.org/file/bot{}/{}'.format(tgbot_token, get_file["result"]["file_path"]) 

        result = requests.post('https://human-dot-goloscorerbot.dt.r.appspot.com', json={'link':file_link})

        if result.text == 'TRUE':
            return ""
        elif result.text == 'FALSE':
            return {
                "method": "sendMessage",
                "chat_id": data["message"]["chat"]["id"],
                'text': "nothing to j...",
                "reply_to_message_id": data["message"]["message_id"],
            }
        else:
            logging.error(result)
            return ""

        # storage:

    except Exception as e:
        import traceback
        logging.error(''.join(traceback.format_exception(type(e), e, e.__traceback__)))
        return ""
    finally:
        if file_link is not None:
            file = requests.get(file_link).content
            storage_client.bucket('golo_bucket').blob(
                '{}.{}'.format(data["message"]["photo"][-1]["file_id"], get_file["result"]["file_path"].split('.')[-1])
            ).upload_from_string(file, content_type="image/jpeg")
        

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
