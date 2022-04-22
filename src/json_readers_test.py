'''This file has to be external to test if some pocs of importing from json_reader'''
'''test to delete'''

from random import randint
from json_readers import TestJson, TestJsonContainer

test_obj = { 'a': randint(0, 100) }
TestJson.write(test_obj)
assert(TestJsonContainer == [test_obj])

test_obj2 = { 'b': randint(101, 200) }
TestJson.write(test_obj2)
assert(TestJsonContainer == [test_obj2])