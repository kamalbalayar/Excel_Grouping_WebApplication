from website import create_app

app = create_app()
#this is our main page
if __name__ == '__main__':
    app.run(debug=True)