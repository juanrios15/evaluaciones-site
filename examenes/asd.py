def I():
    s = 'abcdef'
    for c in s[::2]:
        yield c


for x in I():
    print(x,end="")
    
print("#"*30)

def f(x):
    try:
        x = x/x
    except:
        print("a",end="")
    else:
        print("b",end="")
    finally:
        print("c",end="")

f(1)
f(0)


class A:
    v=2
class B(A):
    v = 1

class C(B):
    pass
o = C()
print(o.v)

class A:
    A = 1
    
print(hasattr(A,'A'))

def fun(n):
    s = '+'
    for i in range(n):
        s += s
        yield s
        
for x in fun(2):
    print(x, end="")
    
class A:
    X = 0
    def __init__(self,v = 0):
        self.Y = v
        A.X += v

a = A()
b = A(1)
c = A(2)

print(c.X)


class A:
    def __str__(self):
        return 'a'

class B(A):
    def __str__(self):
        return 'b'
    
    
class C(B):
    pass

o = C()
print(o)



class I:
    def __init__(self):
        self.s = 'abc'
        self.i = 0
    
    def __iter__(self):
        return self
    def __next__(self):
        if self.i == len(self.s):
            raise StopIteration
        v = self.s[self.i]
        self.i += 1
        return v

for x in I():
    print(x,end="")

print()
print("#"*20)

class A:
    def __str__(self):
        return 'a'

class B:
    def __str__(self):
        return 'b'
    
    
class C(A,B):
    pass

o = C()
print(o)


def o(p):
    def q():
        return '*' * p
    
    return q

r = o(1)
s = o(2)
print(r() + s())


# class A:
#     def __init__(self,v):
#         self.__a = v + 1
        
# a = A(0)

# print(a.__a)


try:
    raise Exception(1,2,3)
except Exception as e:
    print(len(e.args))
    
    

class A:
    pass

class B(A):
    pass
    
    
class C(B):
    pass

print(issubclass(C,A))


class A:
    def a(self):
        print('a')

class B:
    def __str__(self):
        print('b')
    
    
class C(B,A):
    def c(self):
        self.a()

o = C()
o.c()


class A:
    def __init__(self,v=1):
        self.v = v
    
    def set(self,v):
        self.v = v
        return v

a = A()
print(a.set(a.v + 1))



