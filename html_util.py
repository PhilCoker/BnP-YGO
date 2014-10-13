def get_about_html():
	return_html = """<!DOCTYPE html>
<html>
<head>
<title>About</title>
<link rel="stylesheet" type="text/css" href="static/site.css">
<link rel="icon" type="image/png" href="static/favicon.png" />
</head>
<body>
Created by Phillip Coker, with help from his twin brother, Brad.<br><img src="http://img1.wikia.nocookie.net/__cb20120621213210/yugioh/images/d/d8/IllusionistFacelessMage-TF04-JP-VG.jpg">
<br>
<br>
<a href="/">Back</a>
</body>
</html>"""
	return return_html
	
#Returns the html stub that allows selection between elements of a list
def get_select_html( list, name ):
	return_html = '<select name="{}">\n'.format(name)
	for l in list:
		return_html += '<option value="{0}">{0}</option>\n'.format( l )
	return_html += '</select>\n'
	return return_html