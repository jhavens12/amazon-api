
old_number = 49.99
new_number = 47.49


print(str("{0:.0f}%".format(new_number - old_number)))
print(((new_number - old_number)/old_number)*100)
floater = ((new_number - old_number)/old_number)*100


print(str("{0:.0f}%".format(floater)))


# 2017 Q1
q_list = ['Q1','Q2','Q3','Q4']
y_list = list(range(2010,2030))
f_list = []

for y in y_list:
    for q in q_list:
        f_list.append(str(y)+" "+str(q))

print(f_list)
