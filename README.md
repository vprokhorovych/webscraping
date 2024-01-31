### Коментарі
Задачу я розв'язував за допомогою `Selenium` та пітонівської бібліотеки `schedule`. `Selenium` я взяв через наявність динамічного вмісту в сторінках- а саме, показу номера телефону. Номер прихований, причому досить надійно: якщо тицьнути кнопку "показати", то можна простежити, наприклад, обмін даними з facebook. Іншими словами, номер витягується із БД autoria. `Selenium` дозволяє вичепити цей номер (це не дуже скалдно, насправді), але `Selenium` доволі жадібний, а відмовитися від нього не можна (точніше, можна було спробувати `Scrapy`, але ця бібліотека сама по собі не вміє витягувати динамічний вміст, треба використовувати інші бібліотеки, тому я вирішив піти надійнішим шляхом), тому класичні бібліотеки (приміром, `BeautifulSoap`) не годяться. Але все одно є серйозна проблема: на 1 запис іде десь 2 секунди, а записів всього близько 290 000. Більшість цього часу іде просто на завантаження сторінок машин. Тому варто використати асинхронність/багатопоточність, аби цей час даремно не гаявся. Знову ж таки, для статичних сторінок це вже певною мірою навіть звична технологія. Однак і `Selenium` можна вживити в асинхронну обробку - проте такі експерименти потребують часу (бо, чесно скажу, я конкурентне програмування знаю лише на рівні найпростішої теорії, а практики взагалі майже нема).

Для створення дампів БД я послуговувався стандартною Postgres-утилітою `pg_dump`, яку запускав за допомогою `subprocess`.

### Структура програми...
... доволі проста, вона оформлена у вигляді пакета, який можна запускати.  `__init__.py` порожній, він лише вказує пітону, що це пакет. `__main__.py` містить запуск програми за графіком (цей же файл дозволяє виконувати пакет за допомогою `python ...`). `model.py` містить об'єкт таблиці та її метадані, там же створюється єдиний глобальний об'єкт сесії (все це робиться за допомогою `SQLAlchemy`). `scrape.py` - найбільший модуль, який містить функції, що, власне, і виконують скрейпінг. `backup.py` - модуль із функцією, яка створює дамп бази даних.
### Як запустити програму
Я вважатиму, що ви працюєте на Windows 10 та маєте встановлений Python 3.11, PostgreSQL (зокрема, `psql`, `pg_dump`) і Git Bash на вашій машині.
1. Створити теку (наприклад, `D:\Projects\ws`) та перейти в неї у File Explorer
2. Запустити Git Bash із цієї теки та ввести команду `git clone <http path>`, де `<http path>` - https-посилання на репозиторій із кодом
3. Заповнити `D:\Projects\ws\webscraping\.env` власними значеннями
4. Відкрити звичайний термінал та перейти у `ws` (приміром, за допомогою команди `pushd D:\Projects\ws`) 
5. Виконати команди `python -m venv .venv` (створити віртуальне середовище) та `.venv\Scripts\activate` (активувати його)
6. Встановити необхідні бібліотеки командою `pip install -r webscraping\requirements.txt`
7. Виконати в терміналі команду `python webscraping`

   
