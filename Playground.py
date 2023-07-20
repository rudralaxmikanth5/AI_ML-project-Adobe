import q_and_a as qna
import datetime

from flask import Flask, request, render_template



from pygments import highlight
from pygments.lexers import PythonLexer, get_lexer_by_name
from pygments.formatters import HtmlFormatter

app = Flask(__name__)
# https://pygments.org/styles/
style = 'friendly'


firefly = qna.QuestionAnswering()

@app.route("/", methods=["GET"])
def show_panel():
    return render_template("./index.html")

@app.route("/", methods=["POST"])
def completion():
    highighter_style = HtmlFormatter(style=style).get_style_defs('.highlight')
    prompt = request.form["prompt"]
    response = firefly.run_question_answering(prompt)
    response = format(response)
    return render_template("./index.html", response=response, highighter_style=highighter_style)

@app.route("/submit_feedback", methods=["POST"])
def submit_feedback():
    feedback = request.form["prompt"]

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"feedbacks/feedback_{timestamp}.txt"

    with open(filename, "w") as f:
        f.write(feedback)
    return render_template("./index.html")

@app.template_filter('javascript')
def pygments_filter(code):
    lexer = get_lexer_by_name('javascript', stripall=True)
    formatter = HtmlFormatter(style=style)
    return highlight(code, lexer, formatter)

def format(response):
    # split the text into a list of sentences separator ```
    response = response.split("```")
    out = []
    for i,text in enumerate(response):
        if (i%2 == 1):
            out.append({"text": text, "code": True})
        else:
            # push to out
            out.append({"text": text, "code": False})
    return out

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)




