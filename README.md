# kamiken 0.1.0
- pyglet GUI
- Раздельные сервер, клиент, игра и ланчер.
- Сервер запускается только отдельно.
- Выбор игрока по аргументу при запуске.
- Выбор размера доски по аргументу при запуске.
- Обновляющиеся лейблы
- Импортируется только то, что нужно. Вероятно, можно немного меньше из pyglet'а
импортировать, оставив только window, но понадобится переписывать почти весь код
из-за смены названий методов. Да и не завершена ещё, наверна, сама игра.

#### TODO:
СДЕЛАНО	1. После ход полупрозрачный камень рисуется поверх уже поставленного
СДЕЛАНО	2. Переделать обратно прорисовку fade_stone'а, чтобы оно рисовало в зависимости
			от игрока, а не хода.				
СДЕЛАНО	3. Из сетевых функций client/server не используется практически ничего, так как
			функциональности там вагон, а в данном исполнении игры посылается лишь "с"
			и потом ходы в виде "(x,y)". Нужно очищать/переписывать с нуля.
		4. Сделать возможность изменять размер поля.
		5. Сделать хотя бы примитивное меню при запуске.
СДЕЛАНО	6. Индикатор хода.
		7. config.ini.
СДЕЛАНО	8. Аргумент размера доски.
СДЕЛАНО	9. Отправка 5 сообщений доски.
СДЕЛАНО	10. Соответственно, изменения формата высылаемого сообщения.
		11. Автоизменение размера доски/окна, нужно менять проверки в on_mouse_press 
			и on_mouse_motion
		
#### MISC:
В скомпилированном виде весит ~40 мегабайт. Скомпилированный один только CLIENT.py весит 18,
хотя там импортируются лишь 3 модуля, никакой графики. Как уменьшить размер программы-то?


С цветами в pyglet бида. Фоновый цвет хороши работает только если значение
голубого (третье число) 0 или 255, в противном случае рисует белым. Однако,
если использовать дробные значение (0-125 / 255 = 0.х), то все работает. ОДНАКО,
это распространяется на ФОН (pyglet.gl.glClearColor(*colors['board']) -т.е.
когда работаем непосредственно через OpenGL), а вот цвет label'а, например,
требует параметры в int. ЧСХ label нормально работает с любыми цветами, если
значения RGB целочисленные. И еще- в label так же работает и прозрачность (4-ое
число, альфа-канал), в то время как в фоне он ничего не делает. Т.о. цвет фона
окна нужно указывать с осторожностью и не путать переменные.

#### Update log
##### V 0.1.1
-- Пришлось размеры окна/доски в self.x переместить, иначе on_draw() использует не те
значения, которые были переданы в аргументах при создании объекта, а те, что находятся
в файле с самим камикеном. Из-за этого размер доски изменять нельзя было.

-- Почистил client/server, теперь там только нужное и умещается на 1-2 страницы кода.

-- Клиент высылает сообещение 5 раз, сервер пересылает каждое из этих сообщений по разу.
Высылается клиентом 5 раз почти мгновенно, а задержку поставить нельзя — будет гуи 
зависать. Либо и функцию отправки в отдельном процессе делать тогда. На сервере 
ставить отправку нескольких сообщений проблематично, так как на каждое клиентское будет
5 серверных, итого очень много. Но там можно задержку хотя бы полсекунды ставить
без особых проблем. Но если клиент посылает лишь один раз, то проблема та же — ведь у нас
как от сервера не доходило, так и от клиента.

-- Получение этих 5 сообщений очень сильно загрязняет консоль.

-- Добавил аргумент размера доски при запуске.

-- добавил lnch — симлинк на LAUNCHER_0_0_2.py, для более удобного запуска.

-- Убрал ALL_STONES из аргументов Доски.

-- self.lbltext — костыль для изменения текст лейбла по вызываемому клиентом событию.