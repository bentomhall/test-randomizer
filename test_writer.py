#! /Library/Frameworks/Python.framework/Versions/3.6/bin/python3
import re
import assignmentparser
import sys, os

class TestWriter(object):
    def __init__(self, assessment, condense_MC, show_answerblank=False):
        self.assessment = assessment
        self.total_questions = assessment.total
        self.sections = len(assessment._sections)
        self.show_blank = show_answerblank
        if condense_MC:
            self.question_environment = "oneparchoices"
        else:
            self.question_environment = "choices"
        return

    def format_mc_question(self, question, value):
        text, answers = question.data()
        #text[-1] += "\\\\" #insert linebreak after last part of question
        output = ["\\question"]
        if self.show_blank:
            text.insert(0, "\\answerblank ")
        output.extend(text)
        output.append("\\begin{{{0}}}".format(self.question_environment))
        output.extend([self.format_answer(answer) for answer in answers])
        output.append("\\end{{{0}}}".format(self.question_environment))
        return "\n".join(output)+"\n"

    def format_multipart_question(self, question):
        text = question.data()[0]
        output = ["\\question"]
        output.append(text[0])
        output.append("\\begin{parts}")
        output.extend([self.format_question_part(q_text) for  q_text in text[1:]])
        output.append("\\end{parts}")
        return "\n".join(output)+"\n"

    def format_single_question(self, question, value):
        text = question.data()[0]
        if self.show_blank:
            text.insert(0, "\\answerblank")
        return "\\question {0}\n".format("\n".join(text))
    
    def format_question_part(self, text):
        output = ["\\part"]
        output.append(text)
        #output.append("\\vspace*{1in}")
        return "\n".join(output)+"\n"

    def format_answer(self, answer):
        if answer.is_correct:
            return "\\correctchoice {0}".format(answer.text)+"\n"
        else:
            return "\\choice {0}".format(answer.text)+"\n"

    def format_answer_group(self, group):
        output = ["\\begin{multicols}{2}"]
        output.append("\\begin{enumerate}")
        output.extend(["\\item {0}".format(i.text) for i in group])
        output.append("\\end{enumerate}")
        output.append("\\end{multicols}")
        return output


    def format_section(self, section, restart_numbering=False):
        output = []
        questions = section.shuffle()
        if restart_numbering:
            output.append("\\end{questions}")
            output.append(self.format_section_label(section.title))
            output.append("\\begin{questions}")
        else:
            output.append(self.format_section_label(section.title))
        for q in questions:
            if q.is_multiple_choice():
                output.append(self.format_mc_question(q, 2))
            elif q.is_multipart():
                output.append(self.format_multipart_question(q))
            else:
                output.append(self.format_single_question(q, 1))
        if len(section.answer_groups) > 0:
            output.extend(self.format_answer_group(section.answer_groups))
        return "\n".join(output)

    def format_section_label(self, title):
        if title == "":
            return "\n"
        else:
            t, info = title.split('\\',1)
            if info:
                return "\\fullwidth{{\Large {{\\textbf{{{0}}}}} \\\\ \\textit{{{1}}}}}".format(t, info)
            return "\\fullwidth{{\\Large \\textbf{{{0}}}}}".format(title)

    def marshal(self):
        output = []
        for s in self.assessment._sections:
            output.append(self.format_section(s))
        return output

def write(filename, text):
    with open(filename, 'w') as ofile:
        ofile.write(text)
    return

def main(input_file, subject, exam_name, date, index=0, condensed=False, verbose=False, includeFile=None, showBlank=False):
    template = load_template("assessment.template.tex", subject, exam_name, date, index)
    fname = format_filename(input_file, index)
    parser = assignmentparser.Parser(verbose)
    with open(input_file, 'r') as ifile:
        text = ifile.readlines()
        parser.parse(text)
    writer = TestWriter(parser, condensed, show_answerblank=showBlank)
    output = write_test(fname, index, writer, template, includeFile)
    key_name = make_key(fname, index, output)
    return fname, key_name

def include_file(file, index):
    pass

def make_key(fname, index, data):
    name = "{0}.key.tex".format(fname[:-4])
    data[0] = data[0].replace(r"\documentclass{exam}",r"\documentclass[answers]{exam}")
    write(name, '\n'.join(data))
    return name

def write_test(fname, index, parser, template, include=None):
    output = [template]
    output.extend(parser.marshal())
    output.append('\\end{questions}')
    if include:
        output.append(include_file(include, index))
    output.append('\\end{document}')
    write(fname, '\n'.join(output) )
    return output

def format_filename(base, index):
    return "{0}.{1}.tex".format(base[:-4], index)

def load_template(filename, subject, examname, date, index):
    with open(filename, 'r') as template_file:
        text = template_file.read()
        text = text.replace('CODE', str(index+1))
        text = text.replace('CLASSNAME', "\\large \\bfseries {0}\\\\".format(subject) if subject else "")
        text = text.replace('EXAMNAME', examname)
        text = text.replace(' DATE', ", {}".format(date) if date else "")
    return text

if __name__ == "__main__":
    pass

        
        


