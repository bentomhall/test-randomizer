#! /Library/Frameworks/Python.framework/Versions/3.6/bin/python3
import re
import assignmentparser
import sys

class TestWriter(object):
    def __init__(self, assessment, condense_MC):
        self.assessment = assessment
        self.total_questions = assessment.total
        self.sections = len(assessment._sections)
        if condense_MC:
            self.question_environment = "oneparchoices"
        else:
            self.question_environment = "choices"
        return

    def format_mc_question(self, question, value):
        text, answers = question.data()
        text[-1] += "\\\\" #insert linebreak after last part of question
        output = ["\\question[{0}]".format(value)]
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
        return "\\question {0}\n".format("\n".join(text))
    
    def format_question_part(self, text):
        output = ["\\part"]
        output.append(text)
        output.append("\\vspace*{1in}")
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

def main(input_file, subject, exam_name, date, index=0, condensed=False, verbose=False):
    template = load_template("assessment.template.tex", subject, exam_name, date)
    parser = assignmentparser.Parser(verbose)
    with open(input_file, 'r') as ifile:
        text = ifile.readlines()
        parser.parse(text)
    writer = TestWriter(parser, condensed)
    output = [template]
    output.extend(writer.marshal())
    output.append('\\end{questions}')
    output.append('\\end{document}')
    fname = format_filename(input_file, index)
    write(fname, '\n'.join(output) )
    return fname

def format_filename(base, index):
    return "{0}.{1}.tex".format(base[:-4], index)

def load_template(filename, subject, examname, date):
    with open(filename, 'r') as template_file:
        text = template_file.read()
        text = text.replace('CLASSNAME', "\\large \\bfseries {0}\\\\".format(subject) if subject else "")
        text = text.replace('EXAMNAME', examname)
        text = text.replace(' DATE', ", {}".format(date) if date else "")
    return text

if __name__ == "__main__":
    pass

        
        


