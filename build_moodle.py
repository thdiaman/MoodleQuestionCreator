import os
import re
import sys
import base64
import codecs
import shutil
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

def codefile_to_monospace_html(codefile):
	"""
	Helper function that converts a file of code to monospace html
	"""
	with open(codefile, "r") as infile:
		code = infile.read()
	return '<pre style="border: 0; background-color: transparent;">' + code + "</pre>"

if __name__ == '__main__':
	# Create file paths
	dirpath = os.path.dirname(sys.argv[1])
	texfile = os.path.basename(sys.argv[1])
	moodlefile = texfile[:-4] + '-moodle.xml'
	newmoodlefile = texfile[:-4] + '-moodle-new.xml'

	# Compile file using xelatex
	cwd = os.getcwd()
	if not os.path.exists(os.path.join(dirpath, 'moodle.sty')):
		shutil.copyfile('moodle.sty', os.path.join(dirpath, 'moodle.sty'))
	os.chdir(dirpath)
	os.system('xelatex ' + texfile)

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
				if 'type="description"' in line:
					startdesc = True
				elif startdesc:
					if '</question>' in line:
						startdesc = False
					elif '<defaultgrade>' in line:
						line = line.replace('1.0', '0.0000000')
					elif '<penalty>' in line:
						line = line.replace('0.1000000', '0.0000000')
				# Replace images and equations
				if '<IMG ' in line or '\(' in line:
					if '<IMG ' in line:
						line = line.split(' SRC="')[0] + ' SRC="' + image_to_png_base64(next(imagepaths)) + '">' + line.split(' SRC="')[1].split('">')[1]
					if '\({' in line:
						for eq in re.findall('\\\\\(\{(.+?)\}\\\\\)', line):
							line = line.replace(r'\({' + eq + r'}\)', '<IMG  SRC="' + latex_equation_to_png_base64(next(equations)) + '">', 1)
				# Replace code
				if r'\texttt' in line:
					for eq in re.findall('\\\\texttt \{(.+?)\}', line):
						line = line.replace(r'\texttt {' + eq + r'}', \
								'<span style="font-family: Monaco,Menlo,Consolas,\'Courier New\',monospace;">' + eq + '</span>')
				# Replace multiline code
				if r'\lstinputlisting' in line:
					for eq in re.findall('\\\\lstinputlisting \{(.+?)\}', line):
						line = line.replace(r'\lstinputlisting {' + eq + r'}', codefile_to_monospace_html(eq))
				# Replace text manipulations
				if r'<SPAN STYLE=&rdquo;text-decoration: underline;&rdquo;>' in line:
					for eq in re.findall('<SPAN STYLE=&rdquo;text-decoration: underline;&rdquo;>(.+?)</SPAN>', line):
						line = line.replace(r'<SPAN STYLE=&rdquo;text-decoration: underline;&rdquo;>' + eq + r'</SPAN>', '<u>' + eq + '</u>')
				if r'\textit' in line:
					for eq in re.findall('\\\\textit \{(.+?)\}', line):
						line = line.replace(r'\textit {' + eq + r'}', '<i>' + eq + '</i>')
				# Replace attachments
				if r'({{' in line:
					for eq in re.findall('\({{(.+?)}}\)', line):
						filename = eq.split(',')[0].strip()
						linktext = eq.split(',')[1].strip()
						line = line.replace(r'({{' + eq + r'}})', \
								'<a href="' + zipfile_to_zip_base64(filename) + '" download="' + filename.split('/')[-1].split('\\')[-1] + '">' + linktext + '</a>')
				outfile.write(line)

	# Clean up by removing temporary files
	shutil.copyfile(newmoodlefile, moodlefile)
	os.remove(newmoodlefile)
	os.chdir(cwd)
