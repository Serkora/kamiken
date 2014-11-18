# -*- coding: UTF-8 -*-

I = 33
J = 3

def super_function(I, J): #координаты тайла
    coordinates = []
    for i in range(I - 1, I + 2):
        for j in range(J - 1, J + 2):
            print(i , j )
            if (i - j) % 2 == 1:
                coordinates.append((i, j)) #возвращает четыре пары координат
           
    return(coordinates)            

print(super_function(I, J))
