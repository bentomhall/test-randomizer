import copy
import pdb
import random
import sys

class Assessment(object):
    pass

class Section(object):
    def __init__(self, title):
        self.title = title if title is not None else ""
        self._questions = []
        self._groups = []
        self.answer_groups = []
    
    def addQuestion(self, q):
        self._questions.append(copy.deepcopy(q))
        return

    def addVariant(self, v):
        self._groups.append(copy.deepcopy(v))
        return

    def addAnswer(self, a):
        self.answer_groups.append(a)
        return

    def shuffle(self):
        questions = self._questions.copy()
        questions.extend([vq.choice() for vq in self._groups ])
        random.shuffle(questions)
        return questions

class VariantGroup(object):
    def __init__(self):
        self._questions = []

    def addQuestion(self, q):
        self._questions.append(copy.deepcopy(q))
        return

    def choice(self):
        return random.choice(self._questions)

class Question(object):
    ANSWER = "[answers]"
    def __init__(self, shouldShuffle=True, isVerbatim=False):
        self._shuffle = shouldShuffle
        self._question = []
        self._answers = []
        self._addAnswer = False
        self._verbatim = isVerbatim
        return

    def addLine(self, line):
        if line.lower() == self.ANSWER:
            self._addAnswer = True
            return
        if self._addAnswer:
            if len(self._answers) == 0:
                self._answers.append(Answer(line, True))
            else:
                self._answers.append(Answer(line, False))
        elif self._verbatim:
            if len(self._question) == 0:
                self._question.append(line)
            else:
                self._question[0] += line
        else:
            self._question.append(line)
        return

    def data(self):
        return (self._question, self.shuffle())

    def shuffle(self):
        if len(self._answers) == 0:
            return None
        if self._shuffle:
            random.shuffle(self._answers)
        return self._answers

    def is_multiple_choice(self):
        return len(self._answers) != 0

    def is_multipart(self):
        return not self.is_multiple_choice() and len(self._question) > 1 and not self._verbatim


class Answer(object):
    def __init__(self, text, is_correct):
        self.text = text
        self.is_correct = is_correct
        return

class InputError(Exception):
    pass

class Parser(object):
    SECTION_START = "[section]"
    SECTION_END = "[/section]"
    STATIC = "[static]"
    VARIANT_START = "[variant]"
    VARIANT_END = "[/variant]"
    ANSWER_GROUP = "[answer_group]"
    VERBATIM = ["verbatim"]

    def __init__(self, verbose=False):
        self.total = 0
        self._section = None
        self._variantGroup = None
        self._question = None
        self._sections = []
        self.assessment = Assessment()
        self.verbose = verbose
        return

    def _startSection(self, title):
        if self._section and not self._section.title:
            self._endSection()
        elif self._section:
            raise InputError("Cannot nest non-anonymous sections")
        self._section = Section(title)
        return

    def _endSection(self):
        if self._section:
            if self._variantGroup: #close active questions, then close the variant group
                if self._question:
                    self._variantGroup.addQuestion(self._question)
                    self._question = None
                self._section.addVariant(self._variantGroup)
                self._variantGroup = None
            elif self._question: #close active questions
                self._section.addQuestion(self._question)
                self._question = None
            self._sections.append(copy.deepcopy(self._section))
            self._section = None
        return

    def _isAnswerGroupStart(self, line):
        return line.lower() == self.ANSWER_GROUP

    def _isSectionStart(self, line):
        l = line.split(":", 1)[0].rstrip()
        return l.lower() == self.SECTION_START

    def _isSectionEnd(self, line):
        return line.lower() == self.SECTION_END
    
    def _parseSectionTitle(self, line):
        try:
            return line.split(':', 1)[1].strip()
        except IndexError:
            return None

    def _isStatic(self, line):
        return line.lower() == self.STATIC

    def _isVerbatim(self, line):
        return line.lower() == self.VERBATIM

    def _isVariantStart(self, line):
        return line.lower() == self.VARIANT_START

    def _isVariantEnd(self, line):
        return line.lower() == self.VARIANT_END

    def parse(self, text):
        multi_part = 0
        is_answer_group = False
        for i, line in enumerate(text):
            line = line.rstrip()
            if self._isSectionStart(line):
                if self.verbose: 
                    print("starting section")
                title = self._parseSectionTitle(line)
                self._startSection(title)
                continue
            elif self._isSectionEnd(line):
                if self.verbose: 
                    print("ending section")
                self._endSection()
                is_answer_group = False
                continue
            elif self._isVariantStart(line):
                if self.verbose: 
                    print("beginning variant group")
                self._variantGroup = VariantGroup()
                continue
            elif self._isVariantEnd(line):
                if self.verbose:
                    print("ending variant group")
                self._section.addVariant(self._variantGroup)
                self._variantGroup = None
                continue
            elif self._isAnswerGroupStart(line):
                if self.verbose:
                    print("beginning answer group")
                is_answer_group = True
            else:
                if i == 0:
                    self._startSection(None) #insert an anonymous section if the first line isn't a section start tag
                if (not line or line.isspace()) and is_answer_group:
                    if self.verbose:
                        print("ending answer group")
                    is_answer_group = False
                elif (not line or line.isspace()) and self._question:
                    if self._variantGroup:
                        if self.verbose:
                            print("adding question to variant group")
                        self._variantGroup.addQuestion(self._question)
                    else:
                        if self.verbose:
                            print("adding normal question")
                        self._section.addQuestion(self._question)
                    multi_part += 1 if self._question.is_multipart() else 0
                    self._question = None
                    continue
                if not self._question and not is_answer_group:
                    if self._isStatic(line):
                        if self.verbose:
                            print("Beginning static question")
                        self._question = Question(False)
                        continue
                    else:
                        if self.verbose:
                            print("Beginning movable question")
                        self._question = Question(True)
                
                if is_answer_group:
                    if self.verbose:
                        print("adding answer to group")
                        print(line)
                    self._section.addAnswer(Answer(line, False))
                else:
                    if self.verbose:
                        print("adding line to question")
                        print(line if not line.isspace() else 'BLANK')
                    self._question.addLine(line)
                    self.total += 1
        self._endSection()
        if self.verbose:
            print("--------------REPORT---------------")
            print("Total questions: {}".format(self.total))
            print("multi-part questions: {}".format(multi_part))
            sys.exit()
        return
        
if __name__ == "__main__":
    parser = Parser()
    with open('test_input.txt','r') as ifile:
        text = ifile.readlines()
        parser.parse(text)
        for s in parser._sections:
            for q in s._questions:
                print(q._question,q._answers)







