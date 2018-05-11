#!/usr/bin/env python
#coding=utf-8
import sys
import json
from pymongo import MongoClient
from mitmproxy import flowfilter

Question = '';
Option = '';

class M:
    def __init__(self):
        self.conn = MongoClient('mongodb://192.168.99.100:27017/')
        self.db = self.conn.testdb

class Dev:
    def __init__(self, m):
        self.m = m
    def request(self, flow):
        if flowfilter.match(flowfilter.parse('~u https://qf.56.com/wxexam/v2/singleMode/getQuestion.do'), flow):
            print('findQuiz')
    def response(self, flow):
        try:
            data = flow.response.content
            data = json.loads(data)
            if flowfilter.match(flowfilter.parse('~u https://qf.56.com/wxexam/v2/singleMode/getQuestion.do'), flow):
                global Question, Option
                Question = question = data['data']['title']
                answer = self.m.db.col.find_one({"question":question})
                Option = option = [data['data']['answera'], data['data']['answerb'], data['data']['answerc']]
                if answer is None:
                    print(question)
                else:
                    trueAnsewer = '';
                    strindex = '';
                    print('have answer')
                    c = flow.response.content
                    for index in range(len(Option)):
                        if(Option[index] == answer['answer']):
                            if index == 1 :
                                strindex = 'answera'
                            elif index == 2 :
                                strindex = 'answerb'
                            else :
                                strindex = 'answerc'
                            trueAnsewer = data['data'][strindex] + '[标准答案]'
                            flow.response.content = flow.response.content.replace(bytes(data['data'][strindex],encoding='utf8'), bytes(trueAnsewer, encoding='utf8'))
                    # print(flow.response.content)
                    return;
            if flowfilter.match(flowfilter.parse('~u https://qf.56.com/wxexam/v2/singleMode/answer.do'), flow):
                answer = data['data']['rightAnswer']
                _answer = self.m.db.col.find_one({"question":Question})
                if _answer is None:
                    print('插入' + {"question": Question, "answer": Option[answer - 1]})
                    self.m.db.col.insert({"question": Question, "answer": Option[answer - 1]})
                else:
                    print('更新')
                    self.m.db.col.update({"question": Question}, {"answer": Option[answer - 1]})
                return;
        except Exception:
            pass

addons = [
    Dev(M())
]