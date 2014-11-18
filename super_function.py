# -*- coding: UTF-8 -*-

I = 1
J = 1

def super_function(I, J): #координаты тайла
    coordinates = []
    for i in range(I - 1, I + 2):
        for j in range(J - 1, J + 2):
            if i != j and abs(i - j) < 2:
               # print('True ', i, j)
                coordinates.append((i, j)) #возвращает четыре пары координат
    return(coordinates)            

print(super_function(I, J))
