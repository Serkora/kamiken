# kamiken 0.1.1
- pyglet GUI
- Раздельные сервер, клиент, игра и ланчер.
- Сервер запускается только отдельно.
- Выбор игрока по аргументу при запуске.
- Выбор размера доски по аргументу при запуске.
- Обновляющиеся лейблы
- Импортируется только то, что нужно. Вероятно, можно немного меньше из pyglet'а
импортировать, оставив только window, но понадобится переписывать почти весь код
из-за смены названий методов. Да и не завершена ещё, наверна, сама игра.
- 0.1.1 — стейбл, типа. Изменения в 0.1.2 вносить.

#### TODO:
- Автоизменение размера доски/окна, нужно менять проверки в on_mouse_press 
	и on_mouse_motion
- Переделать ланчер и убрать PLAYER из списка аргументов класса. (?)
- Добавить шрифты используемые в проекте в /Font чтобы они работали на любой платформе
- Добавить функцию подсчета очков
- Подключение к серверу любого количества игроков, выбор с кем играть, переделать функцию 
выбора параметров (исходя из того, кто послал реквест к игре)
- Векторные (?хайрезные?) тайлы
- Добавить историю ходов и возможность ее сохранения в файл, а также восстановление игр из него
- Индикатор последнего хода (графически)
- Добавить координаты (?если история ходов будет отображаться в игровом окне (?), 
стоит добавить координаты, так как иначе смысла в такой истории никакого)
- Сделать задержку повторного отправления сообщений.
- См. предидущий пункт. Проблемы с потерей хода (клиент на одной стороне отправляет, но сервер не получает, 
или сервер получает, но второй клиент не получает) связаны с проблемами сети? Исправит ли 
эту проблему отправка хода несколько раз с задержкой? Какой должна быть задержка - очевидно, 
1 с, например, слишком много. Если речь идет о пяти сообщениях, то задержку, вероятно, 
нецелесообразно устанавливать более 0.2 с (хотя теоретичсеки в пошаговой игре игроки могут 
подождать и более существенное время и не заметить разницы). Вообще, в подобных проектах, 
как мне кажется, применяется плавающая задержка, зависящая от качества соединения. В нашем 
случае: создать отдельную функцию, отправляющую 100 минимальных сообщений с задержкой, 
например, 0.05 секунд (от сервера к клиентам). Каждый клиент считает, сколько сообщений 
получил (n) а затем: const = n/m, где m = 100 Общее число сообщений. Если t - базовое время 
задержки, то для конкретного подключения использовать tc = t/const(^x) увеличивающееся в 
зависимости от потери пакетов, где x - переменная, регулирующая линейность выражения. 

Есть и другой вариант, и он проще. Он заключается в том, что в качестве сообщения 
передается не ход (один раз, 5 раз, n раз...), а матрица ALL_STONES. При этом происходит следующее: 
А - клиент-отправитель, С - сервер, В - клиент-получатель. A совершает ход и начинает 
отправлять ALL_STONES на сервер каждые t секунд. При этом на сервере в качестве 
переменной уже хранится ALL_STONES (если ход первый, то это нулевая матрица). 
При получении ALL_STONES сервер С сравнивает его с тем, что у него хранится, 
и если матрица отличается на один элемент отправляет ее В (ну и заменяет свой 
ALL_STONES на новый). При получении ALL_STONES B сравнивает его со своей ALL_STONES 
на предмет нового элемента и если true принимает ход. При этом А может продолжать 
высылать ALL_STONES но сервер игнорирует их, так как они совпадают с хранящейся на 
нем ALL_STONES. Когда В совершает ход он точно так же начинает отправлять новую 
ALL_STONES на сервер и сервер принимает ее, так как она отличается от хранящейся 
на нем матрицы и пересылает его А, который все еще послыает предидущий ход. Получив 
новую ALL_STONES А проверяет есть ли в ней ход, который он пытается отправить, и 
если есть - перестает отправлять старый ALL_STONES и принимает ход. Все, будет 
работать. Может быть это не оптимально, так как сообщения будт сыпаться на сервер 
постоянно, но это ТОЧНО будет работать. 
		
		
#### Update log
##### V 0.1.1
- Пришлось размеры окна/доски в self.x переместить, иначе on_draw() использует не те
значения, которые были переданы в аргументах при создании объекта, а те, что находятся
в файле с самим камикеном. Из-за этого размер доски изменять нельзя было.

- Почистил client/server, теперь там только нужное и умещается на 1-2 страницы кода.

- Клиент высылает сообещение 5 раз, сервер пересылает каждое из этих сообщений по разу.
Высылается клиентом 5 раз почти мгновенно, а задержку поставить нельзя — будет гуи 
зависать. Либо и функцию отправки в отдельном процессе делать тогда. На сервере 
ставить отправку нескольких сообщений проблематично, так как на каждое клиентское будет
5 серверных, итого очень много. Но там можно задержку хотя бы полсекунды ставить
без особых проблем. Но если клиент посылает лишь один раз, то проблема та же — ведь у нас
как от сервера не доходило, так и от клиента.

- Получение этих 5 сообщений очень сильно загрязняет консоль.

- Добавил аргумент размера доски при запуске.

- добавил lnch — симлинк на LAUNCHER_0_0_2.py, для более удобного запуска.

- Убрал ALL_STONES из аргументов Доски.

- self.lbltext — костыль для изменения текст лейбла по вызываемому клиентом событию.

- Координаты мышки преобразуются в "правильные" — начинающиеся с (0,0)

##### V 0.1.2
- Добавлен config.ini с параметрами размера доски и путями к картинками.

- Немного подправлен процесс обновления текста лейбла, чтобы избавиться от лишних переменных


##### V 0.1.3
- Стартовое меню. Выбор размера доски и игрока. Пока что на сервер всё равно отправляется
только сообщение о подключении.

- Лейблы нормально перерисовываются при переключении в фуллскрин или начале игры 
с другим разрмером доски.

- Сама доска, впрочем, всё ещё в левом углу рисуется.

- PLAYER среди аргументов класса ещё присутствует для совместимости с созданием 
объекта в ланчере, но в принципе не используется. Как будут более серьёзные 
изменения ланчера — обновлю.

##### V 0.1.4, Server 0.0.3, Client 0.0.3, Launcher 0.0.4
- Избавился от аргументов
PLAYER  - нинужен, игрок выбирается внутри игры
WINDOW_H/WINDOW_W - нинужны, размер окна, во-первых, всё равно выставляется
в зависимости от размера доски, во-вторых, передаётся в переменные внутри класса.
Ни к чему высчитывать размер вне класса а потом передавать в качестве аргумента.
- Вызов 5 событий на передачё сообщения с интервалом в 100 мс

- Сервер:
1. Бесконечный луп, пока self.shutdown != True.
2. Как только игра заканчивается, сервер выходит из self.running() и начинает
всё с начала (подключение игроков)
3. При получении команды "disconnect" от клиента, удаляет его адрес из списка и уменьшает
количество игроков на 1
4. Изменена функция подключения игроков, теперь используется manage_connections

- Клиент:
1. Убрана передача пяти сообщений, так как игра будет 5 событий вызывать с задержкой
2. Сокет биндится на 0.0.0.0 и рандомный порт для прослушивания на всех интерфейсах.
Серверный айпи был изменён по техническим причинам.

- Ланчер:
1. Убраны ненужные классы
2. Добавлена отправка "disconnect" при выходе из игры.


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
