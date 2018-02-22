
import os
import sys
import pyDes
import swiftclient.client as swiftclient
import flask
import datetime
import os

import keystoneclient.v3 as keystoneclient


PORT = int(os.getenv('PORT', 80))
app = flask.Flask(__name__)
app.debug=True

password = ''
authurl = ''
projectId = ''
userId = ''
region = ''


conn = swiftclient.Connection(
        key=password,
        authurl=authurl+'/v3',
        auth_version='3',
        os_options={"project_id": projectId,
                             "user_id": userId,
                             "region_name": region})



@app.route('/',methods=['GET','POST'])
def root():
    return flask.render_template("index.html")


@app.route('/createnewcont',methods=['GET','POST'])
def createnewcont():
    container_name =flask.request.form['contname']
    conn.put_container(container_name)
    return flask.render_template("index.html",msgcon="container" +" " +container_name +" created successfully")

@app.route('/displaycons',methods=["GET",'POST'])
def displaycons():
    list=[]
    for container in conn.get_account()[1]:
        list.append(container['name'])
    return flask.render_template("index.html", lists=list)


@app.route('/deletecont',methods=["GET",'POST'])
def deletecont():
    name=flask.request.form['delcont']
    conn.delete_container(name)
    return flask.render_template("index.html",msgdelete = "Container "+name+" deleted successfully")

@app.route('/fileupload',methods=['GET','POST'])
def file_upload():

    if flask.request.method== 'POST':
        container_name=flask.request.form['uploadnamecont']
        f=flask.request.files['file']

        blob = flask.request.files['file'].read()
        size = len(blob)


        data = f.stream.read()


        if size >10 :
            container_name ="big"
        if size <=10:
            container_name = "small"

        conn.put_object(container_name,
                        f.filename,
                        contents=encod(data,'qweasdzx'),
                        content_type='text/plain')



        totalfilesize = 0
        for data in conn.get_container(container_name)[1]:
                totalfilesize  += data['bytes']

        return flask.render_template("index.html",msg="File uploaded suceesfully , Total size on cloud is " + str(totalfilesize))


def encod(data, password):
    k = pyDes.des(password, pyDes.CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
    d = k.encrypt(data)
    return d

def decod(data, password):
    password = password.encode('ascii')
    k = pyDes.des(password, pyDes.CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
    d = k.decrypt(data)
    return d



@app.route('/filedownload',methods=['GET','POST'])
def file_download():
        container_name=flask.request.form['paramcname']
        filenme=flask.request.form['paramfile']
        obj = conn.get_object(container_name, filenme)
        file_contents = obj[1]
        actual_file=decod(file_contents,'qweasdzx')

        if flask.request.method == 'POST' :
            response = flask.make_response(actual_file)
            response.headers["Content-Disposition"] = "attachment; filename=%s"%filenme
            return response


@app.route('/displayfiledata',methods=['GET','POST'])
def displayfiledata():
    container_name = flask.request.form['cname']
    object_name=flask.request.form['fname']
    flag = None

    if container_name == '':
        return flask.render_template("index.html", contents="enter a container name")


    if object_name == '':
        return flask.render_template("index.html", contents="enter a file name")

    for data in conn.get_container(container_name)[1]:
        if data['name'] ==object_name:
            flag =True
            break;


    if flag is None:
        return flask.render_template("index.html", contents="file not on cloud")

    data = conn.get_object(container_name, object_name)
    file_contents = data[1]
    actual_file = decod(file_contents, 'qweasdzx')
    return flask.render_template("index.html", contents=actual_file)


@app.route('/displayfilesincontainer',methods=['GET','POST'])
def displaycontainerfiles():
    container_name=flask.request.form['containername']
    list=[]
    for data in conn.get_container(container_name)[1]:
        list.append(data['name'])
        list.append(data['bytes'])
        list.append(data['last_modified'])
    return flask.render_template("index.html", files_list=list)

@app.route("/deleteobjectsofcontainer",methods=['GET','POST'])
def deleteobjectsofcontainer():
    container_name=flask.request.form['deleteconatername']
    obj_name=flask.request.form['objectname']
    conn.delete_object(container_name, obj_name)
    return flask.render_template("index.html")



@app.route('/deletefiles',methods=['GET','POST'])
def deletefilesofcontainer():
    container_name=flask.request.form['deltefilecon']
    filedate = datetime.datetime.strptime(flask.request.form['filedate'], "%Y-%m-%dT%H:%M:%S.%f")

    list = []

    for data in conn.get_container(container_name)[1]:
        if datetime.datetime.strptime(data['last_modified'],"%Y-%m-%dT%H:%M:%S.%f") < filedate:
            list.append(data['name'])
            conn.delete_object(container_name, data['name'])

    return flask.render_template("index.html", deletedfiles=list)




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(PORT), threaded=True, debug=False)