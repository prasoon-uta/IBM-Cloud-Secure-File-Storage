
import os
import json
import pyDes

from flask import Flask, render_template, request, make_response
import swiftclient.client as swiftclient


import keystoneclient.v3 as keystoneclient



PORT = int(os.getenv('PORT', 80))
app = Flask(__name__)
app.debug=True

"""
if 'VCAP_SERVICES' in os.environ:
    cred = json.loads(os.environ['VCAP_SERVICES'])['Object-Storage'][0]
    credinfo=cred['credentials']
    authurl = credinfo['https://identity.open.softlayer.com'] + '/v3'
    projectId = credinfo['8929e7a3ba4847c0adbd4c134349f1a5']
    region = credinfo['dallas']
    userId = credinfo['19654912304a4110a0cf487a3acb47bd']
    password = credinfo['Zf*7PTJY.!_7KkC=']
    projectname = credinfo['object_storage_de149da8_17ae_417a_b6ea_f6ac635ad442']
    domainName = credinfo['b2f10d5c0a624363ae567ba18493b408']
    conn = swiftclient.Connection(key=password, authurl=authurl, auth_version='3',
                                  os_options={"project_id": projectId, "user_id": userId, "region_name": region})

"""

password = 'Zf*7PTJY.!_7KkC='
authurl = 'https://identity.open.softlayer.com'
projectId = '8929e7a3ba4847c0adbd4c134349f1a5'
userId = '19654912304a4110a0cf487a3acb47bd'
region = 'dallas'


conn = swiftclient.Connection(
        key=password,
        authurl=authurl+'/v3',
        auth_version='3',
        os_options={"project_id": projectId,
                             "user_id": userId,
                             "region_name": region})



@app.route('/',methods=['GET','POST'])
def root():
    return render_template("index.html")


@app.route('/createcontiner',methods=['GET','POST'])
def createcontainer():
    container_name =request.form['containername']
    conn.put_container(container_name)
    return render_template("index.html")

@app.route('/displaycontainers',methods=["GET",'POST'])
def displaycontainers():
    container_list=[]
    for container in conn.get_account()[1]:
        container_list.append(container['name'])
    return render_template("index.html",container_list=container_list)

@app.route('/deletecontainer',methods=["GET",'POST'])
def deletecontainers():
    container_name=request.form['getdeletecontainer']
    conn.delete_container(container_name)
    return render_template("index.html")

@app.route('/upload_file',methods=['GET','POST'])
def upload():

    if request.method== 'POST':
        container_name=request.form['uploadcontainername']
        f=request.files['file']
        data = f.stream.read()
        conn.put_object(container_name,
                        f.filename,
                        contents=encod(data,'qweasdzx'),
                        content_type='text/plain')

        return render_template("index.html",msg="File uploaded suceesfully")

def encod(data, password):
    k = pyDes.des(password, pyDes.CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
    d = k.encrypt(data)
    return d

def decod(data, password):
    password = password.encode('ascii')
    k = pyDes.des(password, pyDes.CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
    d = k.decrypt(data)
    return d



@app.route('/download_file',methods=['GET','POST'])
def download():
        container_name=request.form['downloadcontainername']
        filenme=request.form['downloadingfile']
        obj = conn.get_object(container_name, filenme)
        file_contents = obj[1]
        actual_file=decod(file_contents,'qweasdzx')

        if request.method == 'POST' :
            response = make_response(actual_file)
            response.headers["Content-Disposition"] = "attachment; filename=%s"%filenme
            return response


@app.route('/displaydata',methods=['GET','POST'])
def displayingdata():
    container_name = request.form['containnmae']
    object_name=request.form['objecname']
    data=conn.get_object(container_name,object_name)
    file_contents=data[1]
    return render_template("index.html",file_contents=file_contents)


@app.route('/listfiles',methods=['GET','POST'])
def displayfilesfromcontainer():
    container_name=request.form['conname']
    object_list=[]
    for data in conn.get_container(container_name)[1]:
        object_list.append(data['name'])
        object_list.append(data['bytes'])
        object_list.append(data['last_modified'])
    return render_template("index.html",object_list=object_list)

@app.route("/deleteobjects",methods=['GET','POST'])
def deleteobjects():
    container_name=request.form['deleteconater']
    obj_name=request.form['objname']
    conn.delete_object(container_name, obj_name)
    return render_template("index.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(PORT), threaded=True, debug=False)