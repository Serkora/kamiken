# kamiken 0.3.0
- pyglet GUI.
- Раздельные сервер, клиент, игра и ланчер.
- Сервер запускается только отдельно.
- Выбор игрока и размера поля внутри игры.
- Подключение/отключение от сервера без необходимости перезапуска последнего.
- Работающий фуллскрин
- Хайрез спрайты
- Анимация!
- Меню игры!
- Оптимизация!

#### TODO:
- Добавить шрифты используемые в проекте в /Font чтобы они работали на любой платформе
А имеем ли мы право этот comic sans распространять?
- Добавить функцию подсчета очков (осталось решить с концом игры)
- Подключение к серверу любого количества игроков, выбор с кем играть, переделать функцию 
выбора параметров (исходя из того, кто послал реквест к игре)
- Добавить историю ходов и возможность ее сохранения в файл, а также восстановление игр из него
- Добавить координаты (?если история ходов будет отображаться в игровом окне (?), 
стоит добавить координаты, так как иначе смысла в такой истории никакого)
- Пора бы АИ прикрутить.	
- В фуллскрине леблы доски/типа игры смотрятся очень плохо, находясь впритык к 
просто огроменным тайлам.
- Подумать над дефолтным размером камня выбора игрока.
- Добавить выбор размера окна/фуллскрина в стартовое меню.
- Вынести стартовое меню тоже в отдельный класс?
- Добавить функцию удаления всех кнопок в меню.(button.batch = None выдаёт несколько 
ошибок и потом убирает кнопку, но ломает меню. button.delete() убирает кнопку, но
после движения мышки снова её рисует. button.delete() и buttons.remove(button),
вроде как, делает то, что нужно.) МОЖНО ПРОСТО НЕ РИСОВАТЬ, КОГДА НЕ НАДО!
- Добавить какую-то проверку на конфликт номеров игроков.
- Добавить периодический пинг игроков
		
#### Update log
##### V 0.3.0
- UP TO 2000%+ FASTER
- Собственно, переделана функция прорисовки поля. Список спрайтов пересоздаётся
только тогда, когда поле изенилось, иначе просто рисуется предыдущий игровой batch.
- На больших полях (>25x25) в момент момент хода всё равно заметен провал фпс,
так что место для дальнейшей оптимизации (изменение лишь нужных спрайтов) ещё есть.
- Двойна защита от KeyError: используется локальная переменная и клиент теперь
не просто отправляет событие, а добавляет его в стек событий часов, так что
изменение элементов матрицы просто _обязано_ быть синхронизированным с другими
функциями.
- 0.0.5 Версии сетевых модулей (клиент описан, в ланчере нужные цифры проставлены,
а сервер за компанию.)

##### Launcher 0.0.4, Client 0.0.4, Server 0.0.4
- Подправлены сетевые команды клиента и сервер.
- Клиент теперь не выполняет никаких операций, если полученная команда уже была
ранее получена (пока что два подряд идентичных сообщений быть не может, только 
как "запасные")
- В консоль идёт только по одному принту от 5 повторяющихся сообещний
- Ланчер просто чуть переписан для работы с новыми версиями и переименован для 
красоты (как бы все "сетевые" модули одной версии).

##### V 0.2.2s
- Добавленю меню игры с возможностью скипа, конца игры, настроек и отключения.
Пока что ничего из этого не работает, конечно. Кроме выхода, из игры, это просто было.
- Обработчики событий мыши теперь просто вызываются соответствующие функции согласно
состоянию игры.
- Меню игры хорошо проработано, довольно функционально и универсально, что-либо
изменить в нём не составит труда.
- Передвинуты многи функции в коде, чтобы быть как-то логически быть связанными.
- В config.ini теперь пункт resolution = 0000x0000, который читается при запуске,
и куда (вместе с fullscreen) записывается при выходе последнее состояние
- Комменты, много их. Треть кода, наверное, в них.

##### V 0.2.1
- 150х150 хайрез тайлы
- Автоматическое изменение размера тайлов в зависимости от размера окна. Оставляет
по 30 пикселей (константа не очень хорошо, надо бы убрать, но нужно решить, 
на что заменить) сверху и снизу экрана, а остальное место равномерно делит между
всеми клетками доски. Выбрана вертикаль, чтобы заполнить целиком заполнить наименьшый
размер экрана. Под узкоформатные мониторы не пойдёт. Размер тайла — 0.8 * размер клетки,
то есть 0.2 — это пробел между соседними тайлами. Наведение курсора на этот пробел, 
впрочем, всё равно отображает полупрозрачный камень.
- Анимация последнего хода (в misc немного инфы)
- Для "корректной" работы анимации пришлось добавить вызываемую постоянно нулевую
функцию для обновления окна так часто, как только компьютер может.
- Добавлен выбор сингл/мультиплеера. Пока что ни на что не влияет, правда.

##### V 0.2.0
- Переработана графика: тайлы более не имею прозрачных полей, вместо этого
при рисовке создаются интервалы между ними.
- Соответственно, теперь есть TILE\_SIZE — размер тайла, и SQUARE\_SIZE — размер клетки.
- Anchor point у тайлов теперь в центре, а не в левом нижнем углу.
- Добавлены переменны margin\_v, margin\_h, отвечающие за необходимые отступы от 
краёв окна для выведения поля в центр экрана независимо от размера окна.
- Соответственно, доска рисуется всегда в центре, как в оконном, так и в полноэкранном
режимах.
- Добавлен автоматический подсчёт очков, но пока лишь в виде изменения главного 
лейбла по нажатию сочетания клавиш — !Заканчивает игру!
- Необходимо добавить (вернуть...) идентификатор сообщений по префиксам, чтобы 
игра могла обрабатывать различные запросы, а не только получать и передавать две 
цифры (даже приём сообщения о подключении второго игра сделать кустарно).

##### V 0.1.4, Server 0.0.3, Client 0.0.3, Launcher 0.0.3
- Добавлена функция преобразования изображений в текстуры OpenGL, вызывается 
из draw\_setup() для отображения увеличенных r\_stone и b\_stone без "блюра" 
- Вызов 5 событий на передачe сообщения с интервалом в 100 мс.
- Избавился от аргументов:
1. PLAYER  - нинужен, игрок выбирается внутри игры
WINDOW\_H/WINDOW\_W - нинужны, размер окна, во-первых, всё равно выставляется.
в зависимости от размера доски, во-вторых, передаётся в переменные внутри класса.
2. Ни к чему высчитывать размер вне класса, а потом передавать в качестве аргумента.

- Сервер:
1. Бесконечный луп, пока self.shutdown != True.
2. Как только игра заканчивается, сервер выходит из self.running() и начинает
всё с начала (подключение игроков).
3. При получении команды "disconnect" от клиента, удаляет его адрес из списка и уменьшает
количество игроков на 1.
4. Изменена функция подключения игроков, теперь используется manage_connections.

- Клиент:
1. Убрана передача пяти сообщений, так как игра будет 5 событий вызывать с задержкой.
2. Сокет биндится на 0.0.0.0 и рандомный порт для прослушивания на всех интерфейсах.
Серверный айпи/порт был изменён по техническим причинам.

- Ланчер:
1. Убраны ненужные классы.
2. Убран запуск с аргументами.
3. Добавлена отправка "disconnect" при выходе из игры.

##### V 0.1.3
- Стартовое меню. Выбор размера доски и игрока. Пока что на сервер всё равно отправляется
только сообщение о подключении.

- Лейблы нормально перерисовываются при переключении в фуллскрин или начале игры 
с другим разрмером доски.

- Сама доска, впрочем, всё ещё в левом углу рисуется.

- PLAYER среди аргументов класса ещё присутствует для совместимости с созданием 
объекта в ланчере, но в принципе не используется. Как будут более серьёзные 
изменения ланчера — обновлю.

##### V 0.1.2
- Добавлен config.ini с параметрами размера доски и путями к картинками.

- Немного подправлен процесс обновления текста лейбла, чтобы избавиться от лишних переменных

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

- добавил lnch — симлинк на LAUNCHER\_0\_0\_2.py, для более удобного запуска.

- Убрал ALL_STONES из аргументов Доски.

- self.lbltext — костыль для изменения текст лейбла по вызываемому клиентом событию.

- Координаты мышки преобразуются в "правильные" — начинающиеся с (0,0)

#### MISC:
В скомпилированном виде весит ~40 мегабайт. Скомпилированный один только CLIENT.py весит 18,
хотя там импортируются лишь 3 модуля, никакой графики. Как уменьшить размер программы-то?
18 мегабайт, как выяснилось, это просто голвый питон. Хоть одну, хоть тысячу и одну строку
кода туда пиши.

С цветами в pyglet бида. Фоновый цвет хороши работает только если значение
голубого (третье число) 0 или 255, в противном случае рисует белым. Однако,
если использовать дробные значение (0-125 / 255 = 0.х), то все работает. ОДНАКО,
это распространяется на ФОН (pyglet.gl.glClearColor(*colors['board']) -т.е.
когда работаем непосредственно через OpenGL), а вот цвет label'а, например,
требует параметры в int. ЧСХ label нормально работает с любыми цветами, если
значения RGB целочисленные. И еще- в label так же работает и прозрачность (4-ое
число, альфа-канал), в то время как в фоне он ничего не делает. Т.о. цвет фона
окна нужно указывать с осторожностью и не путать переменные.


См. предыдущий пункт. Проблемы с потерей хода (клиент на одной стороне отправляет, но сервер не получает, 
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
передается не ход (один раз, 5 раз, n раз...), а матрица ALL\_STONES. При этом происходит следующее: 
А - клиент-отправитель, С - сервер, В - клиент-получатель. A совершает ход и начинает 
отправлять ALL\_STONES на сервер каждые t секунд. При этом на сервере в качестве 
переменной уже хранится ALL\_STONES (если ход первый, то это нулевая матрица). 
При получении ALL\_STONES сервер С сравнивает его с тем, что у него хранится, 
и если матрица отличается на один элемент отправляет ее В (ну и заменяет свой 
ALL\_STONES на новый). При получении ALL\_STONES B сравнивает его со своей ALL\_STONES 
на предмет нового элемента и если true принимает ход. При этом А может продолжать 
высылать ALL\_STONES но сервер игнорирует их, так как они совпадают с хранящейся на 
нем ALL\_STONES. Когда В совершает ход он точно так же начинает отправлять новую 
ALL\_STONES на сервер и сервер принимает ее, так как она отличается от хранящейся 
на нем матрицы и пересылает его А, который все еще послыает предидущий ход. Получив 
новую ALL\_STONES А проверяет есть ли в ней ход, который он пытается отправить, и 
если есть - перестает отправлять старый ALL\_STONES и принимает ход. Все, будет 
работать. Может быть это не оптимально, так как сообщения будт сыпаться на сервер 
постоянно, но это ТОЧНО будет работать. 

Короче, я пытался, как всегда, сделать однострочную функицю. Проблема в том, что нужно, 
чтобы прозрачность плавно двигалась между 128, 256 и обратно 128, а с остатком 
от деления получается 128->255, 128->255, со скачком между 255 и 128. Разумно, 
что для такой пульсации сгодится косинус. Вот только кто и как будет 
инкрементировать аргумент этого косинуса? Ведь вся идея в том, что уравнение
вида x = c + f(x) сделает нужную работу, так как расслабившись и дав себе
две-три строки задача становится тривиальной (пока что так и сделал, к сожалению).
Пришла идея с рекурсивным косинусом: x = cos(arccos(x)+1). То есть, при каждом проходе
по этой функции x становится чуть больше/меньше. К сожалению, arccos возвращает значения
только от 0 до π, следовательно на -1 он застревает, ведь cos(pi+0.1) = cos(pi-0.1), 
и колеблется лишь между этими двумя значениями. Каким-то образом нужно поменять знак
при доходе до π. Казалось бы, сравны x и cos(arccos(x)+0.1), и узнай, в какую сторону 
сейчас подвинется — но теперь нужно поменять знак и в этом этапе сравнения. В общем,
само в себя упирается и до бесконечности можно писать. В общем, есть ещё пара идей
со сравнением значений arrcos, увеличением диапазона этого arccos до 2π, или 
остатком от деления на отрицательное число, но фиг его знает, как это сделать. Вероятно,
придётся остановится на этом уродливом костыле в виде self.pulseiter.
часа 4 на это потратил, а в итоге безрезультатно.