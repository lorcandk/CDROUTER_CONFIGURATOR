from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def dropdown():
    options = ['Option 1', 'Option 2', 'Option 3']
    if request.method == 'POST':
        selected_option = request.form.get('options')
        return f"You selected: {selected_option}"
    return render_template('cdrouter_configurator.html', options=options)

if __name__ == '__main__':
#    app.run(debug=True)
    app.run(debug=True, port=5000, host='0.0.0.0')

