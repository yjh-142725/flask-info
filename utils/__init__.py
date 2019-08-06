class Pre(object):
    a = 1
class B(Pre):
    pass
class C(Pre):
    pass


print(Pre.a, B.a, C.a)

B.a = 2
print(Pre.a, B.a, C.a)

Pre.a = 3
print(Pre.a, B.a, C.a)

B.a = 2.5
print(Pre.a, B.a, C.a)

Pre.a = 4
print(Pre.a, B.a, C.a)
