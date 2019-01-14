import os
import re
import base64
import codecs
import matplotlib.pyplot as plt
try:
	from StringIO import StringIO as SIO # for python 2
except ImportError:
	from io import BytesIO as SIO # for python 3

def render_latex(formula, fontsize=5, dpi=200, format_='png'):
	"""
	Helper function that converts a latex equation to an image
	"""
	fig = plt.figure(figsize=(0.01, 0.01))
	fig.text(0, 0, u'${}$'.format(formula), fontsize=fontsize)
	buffer_ = SIO()
	fig.savefig(buffer_, dpi=dpi, transparent=True, format=format_, bbox_inches='tight', pad_inches=0.0)
	plt.close(fig)
	return buffer_.getvalue()

def write_image_to_file(image_bytes, filename):
	"""
	Helper function that writes an image to file
	"""
	with open(filename, 'wb') as image_file:
		image_file.write(image_bytes)

def latex_equation_to_png_base64(formula):
	"""
	Helper function that converts a latex equation to a png image that is returned in base64 format
	"""
	image_bytes = render_latex(formula)
	encoded_string = base64.b64encode(image_bytes)
	return "data:image/png;base64," + encoded_string.decode('utf-8')

def image_to_png_base64(image_path):
	"""
	Helper function that reads a png image file and converts it to base64 format
	"""
	with open(image_path, "rb") as image_file:
		encoded_string = base64.b64encode(image_file.read())
	return "data:image/png;base64," + encoded_string.decode('utf-8')

def zipfile_to_zip_base64(zip_path):
	"""
	Helper function that reads a zip file and converts it to base64 format
	"""
	with open(zip_path, "rb") as zip_file:
		encoded_string = base64.b64encode(zip_file.read())
	return "data:application/zip;base64," + encoded_string.decode('utf-8')

if __name__ == '__main__':
	texfile = 'questions.tex'#sys.argv[1]
	moodlefile = texfile[:-4] + '-moodle.xml'
	newmoodlefile = texfile[:-4] + '-moodle-new.xml'
#	os.system('xelatex ' + texfile)

	# Find all images in tex
	imagepaths = []
	with codecs.open(texfile, encoding='utf-8') as infile:
		for line in infile:
			if '\\includegraphics' in line:
				impath = line.split('{')[-1].split('}')[0]
				imagepaths.append(impath if impath.endswith('.png') else impath + '.png')
	imagepaths = (imagepath for imagepath in imagepaths)

	# Find all equations in tex
	equations = []
	with codecs.open(texfile, encoding='utf-8') as infile:
		for line in infile:
			if '${' in line:
				for eq in re.findall('\$\{(.+?)\}\$', line):
					equations.append(eq)
	equations = (equation for equation in equations)

	# Iterate the file line by line
	with codecs.open(newmoodlefile, 'w', encoding='utf-8') as outfile:
		with codecs.open(moodlefile, encoding='utf-8') as infile:
			startdesc = False
			for line in infile:
				# Replace short answers with description questions
				if 'type="shortanswer"' in line:
					line = line.split('type="shortanswer"')[0] + 'type="description"' + line.split('type="shortanswer"')[1]
					startdesc = True
				elif startdesc:
					if r'\color {white}' in line:
						line = line.replace(r'\color {white}', '')
					elif '</question>' in line:
						startdesc = False
					elif not ('name>' in line or ('<text>' in line and 'descriptionquestion' not in line) or 'questiontext' in line or \
						 '<defaultgrade>' in line or '<generalfeedback' in line or '<penalty>' in line or '<hidden>' in line):
						continue
				# Replace images and equations
				if '<IMG ' in line or '\(' in line:
					if '<IMG ' in line:
						line = line.split(' SRC="')[0] + ' SRC="' + image_to_png_base64(next(imagepaths)) + '">' + line.split(' SRC="')[1].split('">')[1]
					if '\({' in line:
						for eq in re.findall('\\\\\(\{(.+?)\}\\\\\)', line):
							line = line.replace(r'\({' + eq + r'}\)', '<IMG  SRC="' + latex_equation_to_png_base64(next(equations)) + '">', 1)
				# Replace attachments
				if 'STARTEMBEDDATA' in line:
					for eq in re.findall('STARTEMBEDDATA-(.+?)-ENDEMBEDDATA', line):
						filename = eq.split(',')[0].strip()
						linktext = eq.split(',')[1].strip()
						line = line.replace('STARTEMBEDDATA-' + eq + '-ENDEMBEDDATA', \
								'<a href="' + zipfile_to_zip_base64(filename) + '" download="' + filename.split('/')[-1].split('\\')[-1] + '">' + linktext + '</a>')
				outfile.write(line)
