from controllers import home, event, fighter

def routes(app):
    '''All Routes / Url
    This app uses an MVC pattern, hence all the url are routed here
    Just import your logics from the controllers package and route
    using the add_url_rule function

    :param app: Flask app instance
    :return: None
    '''
    #----------------------------------------------------------------------------#
    # Home Routes
    #----------------------------------------------------------------------------#

    app.add_url_rule('/', view_func=home)
    app.add_url_rule('/event/<string:id>', view_func=event)
    app.add_url_rule('/fighter/<string:fighter_name>', view_func=fighter)