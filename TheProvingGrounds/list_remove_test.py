



list = list()

if(list):
    print(list)

for i in range(10):
    list.append(i)
    
print(list)
print(list[0], list[1])

list.remove(1)
print(list[0], list[1])

list.remove(0)
print(list[0], list[1])