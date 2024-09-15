a = '{a}, {b}'
str1 = a.format_map({'a': 2})
str2 = str1.format(b=3)
print(str2)
