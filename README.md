# MoodleQuestionCreator
Tool for creating moodle questions in latex.
Based on the CTAN package [moodle](https://ctan.org/pkg/moodle).

# Instructions
Perform the following steps:
- Create a file named questions.tex like the one given in folder test
- Make sure that file moodle.sty is in the same directory
- Compile the tex file using xelatex
- Run the script build_moodle.py
- Upload the file questions-moodle.xml to moodle

# Limitations
There are the following limitations:
- The last answer in a question should be `\item{}` instead of `\item` so that all text formattings are parsed correctly
- Only png images are supported
- Math must be inside `${` and `}$`
- Verbatim text is either single-line using `\texttt{}` or multi-line reading from file using `\lstinputlisting{}`
- Four types of questions are supported: essay, single answer, multiple answers, numerical
- No verbatim environments, etc.; it's generally best to avoid fancy latex commands
- File attachment support (using the format `({{filename, text_of_link}})` for defining it) is very experimental; it supports only zip files and has not been tested with different browsers
