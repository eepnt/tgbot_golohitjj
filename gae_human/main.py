import flask, logging

import google.cloud.logging
google.cloud.logging.Client().setup_logging()

# get cloud debugger
try:
  import googleclouddebugger
  googleclouddebugger.enable(
    breakpoint_enable_canary=False
  )
except ImportError:
  print('cannot load cloud debugger')

import has_girl

app = flask.Flask(__name__)

@app.route('/', methods=["POST"])
def recv_request():
    try:
        data = flask.request.get_json()

        rt = has_girl.has_girl(data["link"])
        
        logging.info({
          "req": data,
          "resp": rt,
        })

        if rt < 0:
            return "TRUE"
        else:
            return "FALSE"

    except Exception as e:
        import traceback
        logging.error(''.join(traceback.format_exception(type(e), e, e.__traceback__)))
        return ""

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
