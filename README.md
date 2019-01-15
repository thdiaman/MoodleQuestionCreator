# MoodleQuestionCreator
Tool for creating moodle questions in latex.
Based on the CTAN package [moodle](https://ctan.org/pkg/moodle).

# Instructions
Perform the following steps:
- Create a file named questions.tex like the one given in folder test
- Make sure that files moodle.sty and build_moodle.py are in the same directory
- Compile the file using xelatex
- Run the script build_moodle.py
- Upload the file questions-moodle-new.xml to moodle

# Limitations
There are the following limitations:
- Only png images are supported
- Math must be inside ${ and }$
- Four types of questions are supported: essay, single answer, multiple answers, numerical
- No verbatim environments, listings, etc.; it's generally best to avoid fancy latex commands
- File attachment support (using the format ({{filename, text_of_link)}} for defining it) is very experimental; it supports only zip files and has not been tested with different browsers
