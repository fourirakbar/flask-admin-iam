import flask
from flask import Flask, render_template, jsonify, send_file
from flask_bootstrap import Bootstrap
import mysql.connector
import json
from shelljob import proc
import subprocess
from gevent.select import select
from gevent.wsgi import WSGIServer
import eventlet
import time, datetime, os, getpass
import urllib

eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretboi!'
db = mysql.connector.connect(user='taoing', password='fourir96akbar', host='127.0.0.1', database='ta_container')
cursor = db.cursor(buffered=True)
bootstrap = Bootstrap(app)

@app.route('/')
def index():
	# Movie Titles - Stored as an array
	movie_names = ['Avatar', 
		           'Pirates of the Caribbean',
		           'Spectre',
		           'The Dark Knight Rises',
		           'John Carter',
		           'Spider-Man 3',
		           'Tangled' ]

	# Movie Titles with Attributes - Stored in a Dictionary
	movies = {
		'Avatar': { 'critical_reviews': 723, 'duration': 178, 'imdb_score': 7.9 },
		'Pirates of the Caribbean': { 'critical_reviews': 302, 'duration': 169, 'imdb_score': 7.1 },
		'Spectre': { 'critical_reviews': 602, 'duration': 148, 'imdb_score': 6.8 },
		'The Dark Knight Rises': { 'critical_reviews': 813, 'duration': 164, 'imdb_score': 8.5 },
		'John Carter': { 'critical_reviews': 462, 'duration': 132, 'imdb_score': 6.6 },
		'Spider-Man 3': { 'critical_reviews': 392, 'duration': 156, 'imdb_score': 6.2 },
		'Tangled': { 'critical_reviews': 324, 'duration': 100, 'imdb_score': 7.8 },
	}
	
	return render_template('index.html', movies=movies, movie_names=movie_names)

# dynamic route
@app.route('/channel/<username>')
def channel(username):
	return render_template('username.html', username=username)

@app.route('/dashboard')
def dashboard():
	return render_template('dashboard.html')

@app.route('/table', methods=['GET'])
def table():
	query = "select * from kontainer where date(created_at) = curdate()"
	query = "SELECT * FROM kontainer WHERE created_at "
	cursor.execute(query)
	hasil = cursor.fetchall()
	# print hasil

	# array_hasil = []
	# for data in hasil:
	# 	print data
	# 	dict_hasil = {
	# 		'id': data[0],
	# 		'nrp': data[1],
	# 		'ip': data[2],
	# 		'port': data[3]
	# 	}
	# 	array_hasil.append(dict_hasil)
	
	# dumps = json.dumps(array_hasil)
	# return dumps
	# results = BaseDataTables(request, columns, collection).output_result()
	# return dumps
	# return jsonify(results)


	return render_template('table.html', hasil=hasil)

@app.route( '/stream/<ip>/<user>/<port>', methods=['GET'] )
def stream(ip, user, port):
	# print "jancok a"
	now = datetime.datetime.now()
	newDirName = now.strftime("%Y_%m_%d")
	proc = subprocess.Popen(
    	# /container-data/2018_05_26/192.168.99.100_5114100003_49178
    	# ['tail -f -c +0 /home/fourirakbar/container-data/2018_05_26/192.168.99.100_5114100003_49178/output_file | mitmdump -nr - --set flow_detail=1 --showhost'],
        ['tail -f -c +0 /home/fourirakbar/container-data/'+newDirName+'/'+ip+'_'+user+'_'+port+'/output_file | mitmdump -nr - --set flow_detail=1 --showhost'],
        # ['ping 1.1.1.1'],
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
        )

	def read_process():
		awaiting = [proc.stdout, proc.stderr]
		while awaiting:
			ready, _, _ = select(awaiting, [], [])
			for pipe in ready:
				line = pipe.readline()
				yield ("data:" + line.decode('utf-8') + '\n\n')


        # try:
        #     awaiting = [proc.stdout, proc.stderr]
        #     while awaiting:
        #         ready, _, _ = select(awaiting, [], [])
        #         for pipe in ready:
        #             line = pipe.readline()
        #             if line:
        #                 print "sending line", line.replace('\n', '\\n')
        #                 yield line.rstrip() + '<br/>\n'
        #             else:
        #                 awaiting.remove(pipe)
        #     if proc.poll() is None:
        #         print "process closed stdout and stderr but didn't terminate; terminating now."
        #         proc.terminate()

        # except GeneratorExit:
        #     print "client disconnected, killing process"
        #     proc.terminate()

        # ret_code = proc.wait()
        # print "process return code: ", ret_code

	return flask.Response( read_process(), mimetype= 'text/event-stream' )

    # return render_template('stream.html', ip=ip, user=user, port=port)

# @app.route('/page')
# def get_page():
#     return flask.send_file('page.html')

# @app.route('/stream/<ip>/<user>/<port>', methods=['GET'])
# def stream(ip, user, port):
# 	proc = subprocess.Popen(
#         ['tail -f -c +0 /home/fourirakbar/container-data/192.168.99.100_5114100001_49173/output_file | mitmdump -nr - --set flow_detail=1 --showhost'],
#         # ['ping 1.1.1.1'],
#         shell=True,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE
#         )

# 	def read_process():
#         try:
#             awaiting = [proc.stdout, proc.stderr]
#             while awaiting:
#                 ready, _, _ = select(awaiting, [], [])
#                 for pipe in ready:
#                     line = pipe.readline()
#                     if line:
#                         print "sending line", line.replace('\n', '\\n')
#                         yield line.rstrip() + '<br/>\n'
#                     else:
#                         awaiting.remove(pipe)
#             if proc.poll() is None:
#                 print "process closed stdout and stderr but didn't terminate; terminating now."
#                 proc.terminate()

#         except GeneratorExit:
#             print "client disconnected, killing process"
#             proc.terminate()

#         ret_code = proc.wait()
#         print "process return code: ", ret_code




	# return render_template('stream.html', ip=ip, user=user, port=port)

@app.route('/lihat/<id>/<ip>/<user>/<port>', methods=['GET'])
def lihat(id, ip, user, port):
	query = "SELECT * FROM kontainer WHERE id = '%s'" % (id)
	cursor.execute(query)
	hasil = cursor.fetchall()
	split1 = str(hasil).split("datetime.datetime")[-1]
	split2 = str(split1).split(")]")[0]
	split3 = str(split2).split(",")[0]
	tahun = str(split3).split("(")[1]
	bulan = str(split2).split(",")[1]
	hari = str(split2).split(",")[2]

	if int(bulan) < 10:
		curdate = (tahun+'_0'+bulan+'_'+hari).replace(" ","")
	else:
		curdate = (tahun+'_'+bulan+'_'+hari).replace(" ","")	

	username = getpass.getuser()
	location = '/home/fourirakbar/container-data/'+curdate+'/'+ip+'_'+user+'_'+port
	os.chdir(location)

	#reploace file sebelumnya
	# os.system("sh read_file.sh")

	file = ('log_'+ip+'_'+user+'_'+port+'.txt')
	# urllib.urlretrieve("http://www.google.com", fullfilename)
	# urllib.urlretrieve(file)

	return send_file(location+'/'+file, attachment_filename=file)
	# return send_file(location+'/'+file, attachment_filename=file)

@app.route('/testing')
def testing():
	return render_template('testing.html')

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

if __name__ == '__main__':
	app.run(debug=True, port=5001)