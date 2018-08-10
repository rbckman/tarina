import web
import os

os.system("ln -s /home/pi/Videos static/Videos")

films = []

urls = (
    '/', 'index'
)

render = web.template.render('templates/')

class index:
    def GET(self):
        films = os.walk('static/Videos/').next()[1]
        renderedfilms = []
        unrenderedfilms = []
        for i in films:
            if os.path.isfile('static/Videos/' + i + '/' + i + '.mp4') == True:
                renderedfilms.append(i)
            else:
                unrenderedfilms.append(i)
        return render.index(renderedfilms, unrenderedfilms)

if __name__== "__main__":
    app = web.application(urls, globals())
    app.run()
