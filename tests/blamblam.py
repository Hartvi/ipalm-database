
a = [1, 2]
print(eval("a"))

def blamblam(yay):
    print(yay)

blamblam.lol = a

a += [3, ]
print(blamblam.lol)
print(type(blamblam(blamblam.lol)))
print(type(blamblam))

print("blamblam.lol:",eval("blamblam").lol)
print("blamblam.__dict__:",eval("blamblam").__dict__)
exec("a = 1")
a,b,c = 1,2,3
print(a)

print(type(eval))



