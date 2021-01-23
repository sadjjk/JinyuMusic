from Music import create_app

# app = create_app('develop')
app = create_app('product')

if __name__ == '__main__':
    app.run()
