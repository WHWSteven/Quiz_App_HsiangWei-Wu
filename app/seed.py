from app import create_app, db
from app.models import Category, Question, Choice

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    math = Category(name="Math")
    science = Category(name="Science")
    geography = Category(name="Geography")

    db.session.add_all([math, science, geography])
    db.session.commit()

    math_id = math.id
    science_id = science.id
    geography_id = geography.id

# ================= MATH =================

    q = Question(text="What is 3/4 + 1/4?", correct_choice="B", category_id=math_id)
    db.session.add(q); db.session.commit()
    db.session.add_all([
        Choice(text="1/2", question_id=q.id),
        Choice(text="1", question_id=q.id),
        Choice(text="3/4", question_id=q.id),
        Choice(text="2", question_id=q.id),
    ]); db.session.commit()

    q = Question(text="What is 18 ÷ 3?", correct_choice="C", category_id=math_id)
    db.session.add(q); db.session.commit()
    db.session.add_all([
        Choice(text="4", question_id=q.id),
        Choice(text="5", question_id=q.id),
        Choice(text="6", question_id=q.id),
        Choice(text="9", question_id=q.id),
    ]); db.session.commit()

    q = Question(text="If x + 5 = 12, what is x?", correct_choice="A", category_id=math_id)
    db.session.add(q); db.session.commit()
    db.session.add_all([
        Choice(text="7", question_id=q.id),
        Choice(text="5", question_id=q.id),
        Choice(text="6", question_id=q.id),
        Choice(text="8", question_id=q.id),
    ]); db.session.commit()

    q = Question(text="What is the area of a rectangle with length 6 and width 4?", correct_choice="D", category_id=math_id)
    db.session.add(q); db.session.commit()
    db.session.add_all([
        Choice(text="10", question_id=q.id),
        Choice(text="20", question_id=q.id),
        Choice(text="12", question_id=q.id),
        Choice(text="24", question_id=q.id),
    ]); db.session.commit()

    q = Question(text="Which number is a multiple of both 2 and 3?", correct_choice="C", category_id=math_id)
    db.session.add(q); db.session.commit()
    db.session.add_all([
        Choice(text="8", question_id=q.id),
        Choice(text="9", question_id=q.id),
        Choice(text="12", question_id=q.id),
        Choice(text="15", question_id=q.id),
    ]); db.session.commit()

    q = Question(text="What is 0.5 written as a fraction?", correct_choice="B", category_id=math_id)
    db.session.add(q); db.session.commit()
    db.session.add_all([
        Choice(text="1/4", question_id=q.id),
        Choice(text="1/2", question_id=q.id),
        Choice(text="2/5", question_id=q.id),
        Choice(text="5/10", question_id=q.id),
    ]); db.session.commit()

    q = Question(text="What is the perimeter of a square with side length 7?", correct_choice="A", category_id=math_id)
    db.session.add(q); db.session.commit()
    db.session.add_all([
        Choice(text="28", question_id=q.id),
        Choice(text="21", question_id=q.id),
        Choice(text="14", question_id=q.id),
        Choice(text="49", question_id=q.id),
    ]); db.session.commit()

    q = Question(text="Which number is prime?", correct_choice="D", category_id=math_id)
    db.session.add(q); db.session.commit()
    db.session.add_all([
        Choice(text="9", question_id=q.id),
        Choice(text="15", question_id=q.id),
        Choice(text="21", question_id=q.id),
        Choice(text="13", question_id=q.id),
    ]); db.session.commit()

    q = Question(text="What is 2³ (2 to the power of 3)?", correct_choice="C", category_id=math_id)
    db.session.add(q); db.session.commit()
    db.session.add_all([
        Choice(text="6", question_id=q.id),
        Choice(text="4", question_id=q.id),
        Choice(text="8", question_id=q.id),
        Choice(text="9", question_id=q.id),
    ]); db.session.commit()

    q = Question(text="What is the value of x in 2x = 10?", correct_choice="B", category_id=math_id)
    db.session.add(q); db.session.commit()
    db.session.add_all([
        Choice(text="10", question_id=q.id),
        Choice(text="5", question_id=q.id),
        Choice(text="2", question_id=q.id),
        Choice(text="20", question_id=q.id),
    ]); db.session.commit()


    q = Question(
        text="What is 7 + 5?",
        correct_choice="A",
        category_id=math_id
    )
    db.session.add(q)
    db.session.commit()

    choices = [
        Choice(text="12", question_id=q.id),
        Choice(text="10", question_id=q.id),
        Choice(text="13", question_id=q.id),
        Choice(text="11", question_id=q.id),
    ]
    db.session.add_all(choices)
    db.session.commit()

    q = Question(
        text="What is 15 - 9?",
        correct_choice="B",
        category_id=math_id
    )
    db.session.add(q)
    db.session.commit()

    choices = [
        Choice(text="5", question_id=q.id),
        Choice(text="6", question_id=q.id),
        Choice(text="7", question_id=q.id),
        Choice(text="4", question_id=q.id),
    ]
    db.session.add_all(choices)
    db.session.commit()

    q = Question(
        text="What is 6 × 4?",
        correct_choice="C",
        category_id=math_id
    )
    db.session.add(q)
    db.session.commit()

    choices = [
        Choice(text="20", question_id=q.id),
        Choice(text="18", question_id=q.id),
        Choice(text="24", question_id=q.id),
        Choice(text="26", question_id=q.id),
    ]
    db.session.add_all(choices)
    db.session.commit()

    q = Question(
        text="What is 20 ÷ 5?",
        correct_choice="C",
        category_id=math_id
    )
    db.session.add(q)
    db.session.commit()

    choices = [
        Choice(text="2", question_id=q.id),
        Choice(text="3", question_id=q.id),
        Choice(text="4", question_id=q.id),
        Choice(text="5", question_id=q.id),
    ]
    db.session.add_all(choices)
    db.session.commit()

    q = Question(
        text="What is 9 squared?",
        correct_choice="B",
        category_id=math_id
    )
    db.session.add(q)
    db.session.commit()

    choices = [
        Choice(text="18", question_id=q.id),
        Choice(text="81", question_id=q.id),
        Choice(text="27", question_id=q.id),
        Choice(text="72", question_id=q.id),
    ]
    db.session.add_all(choices)
    db.session.commit()

    q = Question(
        text="Which number is even?",
        correct_choice="C",
        category_id=math_id
    )
    db.session.add(q)
    db.session.commit()

    choices = [
        Choice(text="11", question_id=q.id),
        Choice(text="15", question_id=q.id),
        Choice(text="18", question_id=q.id),
        Choice(text="21", question_id=q.id),
    ]
    db.session.add_all(choices)
    db.session.commit()

    q = Question(
        text="What is the value of x if x + 3 = 10?",
        correct_choice="C",
        category_id=math_id
    )
    db.session.add(q)
    db.session.commit()

    choices = [
        Choice(text="5", question_id=q.id),
        Choice(text="6", question_id=q.id),
        Choice(text="7", question_id=q.id),
        Choice(text="8", question_id=q.id),
    ]
    db.session.add_all(choices)
    db.session.commit()

    q = Question(
        text="What is 3/4 written as a decimal?",
        correct_choice="C",
        category_id=math_id
    )
    db.session.add(q)
    db.session.commit()

    choices = [
        Choice(text="0.25", question_id=q.id),
        Choice(text="0.5", question_id=q.id),
        Choice(text="0.75", question_id=q.id),
        Choice(text="1.25", question_id=q.id),
    ]
    db.session.add_all(choices)
    db.session.commit()

    q = Question(
        text="What is the perimeter of a square with side length 5?",
        correct_choice="C",
        category_id=math_id
    )
    db.session.add(q)
    db.session.commit()

    choices = [
        Choice(text="10", question_id=q.id),
        Choice(text="15", question_id=q.id),
        Choice(text="20", question_id=q.id),
        Choice(text="25", question_id=q.id),
    ]
    db.session.add_all(choices)
    db.session.commit()

    q = Question(
        text="Which number is a prime number?",
        correct_choice="D",
        category_id=math_id
    )
    db.session.add(q)
    db.session.commit()

    choices = [
        Choice(text="9", question_id=q.id),
        Choice(text="15", question_id=q.id),
        Choice(text="21", question_id=q.id),
        Choice(text="17", question_id=q.id),
    ]
    db.session.add_all(choices)
    db.session.commit()
# ================= SCIENCE  =================

    q = Question(text="Which planet is closest to the Sun?", correct_choice="A", category_id=science_id)
    db.session.add(q); db.session.commit()
    db.session.add_all([
        Choice(text="Mercury", question_id=q.id),
        Choice(text="Venus", question_id=q.id),
        Choice(text="Earth", question_id=q.id),
        Choice(text="Mars", question_id=q.id),
    ]); db.session.commit()

    q = Question(text="What process do plants use to make food?", correct_choice="C", category_id=science_id)
    db.session.add(q); db.session.commit()
    db.session.add_all([
        Choice(text="Respiration", question_id=q.id),
        Choice(text="Digestion", question_id=q.id),
        Choice(text="Photosynthesis", question_id=q.id),
        Choice(text="Evaporation", question_id=q.id),
    ]); db.session.commit()

    q = Question(text="Which gas is most abundant in Earth's atmosphere?", correct_choice="B", category_id=science_id)
    db.session.add(q); db.session.commit()
    db.session.add_all([
        Choice(text="Oxygen", question_id=q.id),
        Choice(text="Nitrogen", question_id=q.id),
        Choice(text="Carbon dioxide", question_id=q.id),
        Choice(text="Hydrogen", question_id=q.id),
    ]); db.session.commit()

    q = Question(text="What part of the cell controls its activities?", correct_choice="D", category_id=science_id)
    db.session.add(q); db.session.commit()
    db.session.add_all([
        Choice(text="Cell wall", question_id=q.id),
        Choice(text="Mitochondria", question_id=q.id),
        Choice(text="Cytoplasm", question_id=q.id),
        Choice(text="Nucleus", question_id=q.id),
    ]); db.session.commit()

    q = Question(text="Which type of energy is stored in food?", correct_choice="A", category_id=science_id)
    db.session.add(q); db.session.commit()
    db.session.add_all([
        Choice(text="Chemical energy", question_id=q.id),
        Choice(text="Thermal energy", question_id=q.id),
        Choice(text="Electrical energy", question_id=q.id),
        Choice(text="Light energy", question_id=q.id),
    ]); db.session.commit()

    q = Question(text="What force causes objects to fall to the ground?", correct_choice="C", category_id=science_id)
    db.session.add(q); db.session.commit()
    db.session.add_all([
        Choice(text="Magnetism", question_id=q.id),
        Choice(text="Friction", question_id=q.id),
        Choice(text="Gravity", question_id=q.id),
        Choice(text="Electricity", question_id=q.id),
    ]); db.session.commit()

    q = Question(text="Which organ helps humans breathe?", correct_choice="B", category_id=science_id)
    db.session.add(q); db.session.commit()
    db.session.add_all([
        Choice(text="Heart", question_id=q.id),
        Choice(text="Lungs", question_id=q.id),
        Choice(text="Brain", question_id=q.id),
        Choice(text="Stomach", question_id=q.id),
    ]); db.session.commit()

    q = Question(text="Water freezes at what temperature (°C)?", correct_choice="D", category_id=science_id)
    db.session.add(q); db.session.commit()
    db.session.add_all([
        Choice(text="100", question_id=q.id),
        Choice(text="50", question_id=q.id),
        Choice(text="32", question_id=q.id),
        Choice(text="0", question_id=q.id),
    ]); db.session.commit()

    q = Question(text="Which body system carries blood through the body?", correct_choice="A", category_id=science_id)
    db.session.add(q); db.session.commit()
    db.session.add_all([
        Choice(text="Circulatory system", question_id=q.id),
        Choice(text="Respiratory system", question_id=q.id),
        Choice(text="Digestive system", question_id=q.id),
        Choice(text="Skeletal system", question_id=q.id),
    ]); db.session.commit()

    q = Question(text="What simple machine is a ramp?", correct_choice="C", category_id=science_id)
    db.session.add(q); db.session.commit()
    db.session.add_all([
        Choice(text="Lever", question_id=q.id),
        Choice(text="Pulley", question_id=q.id),
        Choice(text="Inclined plane", question_id=q.id),
        Choice(text="Wheel and axle", question_id=q.id),
    ]); db.session.commit()


    q = Question(
        text="What planet is known as the Red Planet?",
        correct_choice="B",
        category_id=science_id
    )
    db.session.add(q)
    db.session.commit()

    choices = [
        Choice(text="Earth", question_id=q.id),
        Choice(text="Mars", question_id=q.id),
        Choice(text="Jupiter", question_id=q.id),
        Choice(text="Venus", question_id=q.id),
    ]
    db.session.add_all(choices)
    db.session.commit()

    q = Question(
        text="What gas do plants absorb from the air?",
        correct_choice="A",
        category_id=science_id
    )
    db.session.add(q)
    db.session.commit()

    choices = [
        Choice(text="Carbon dioxide", question_id=q.id),
        Choice(text="Oxygen", question_id=q.id),
        Choice(text="Nitrogen", question_id=q.id),
        Choice(text="Hydrogen", question_id=q.id),
    ]
    db.session.add_all(choices)
    db.session.commit()

    q = Question(
        text="What part of the plant makes food using sunlight?",
        correct_choice="C",
        category_id=science_id
    )
    db.session.add(q)
    db.session.commit()

    choices = [
        Choice(text="Roots", question_id=q.id),
        Choice(text="Stem", question_id=q.id),
        Choice(text="Leaves", question_id=q.id),
        Choice(text="Flowers", question_id=q.id),
    ]
    db.session.add_all(choices)
    db.session.commit()

    q = Question(
        text="How many states of matter are commonly taught?",
        correct_choice="D",
        category_id=science_id
    )
    db.session.add(q)
    db.session.commit()

    choices = [
        Choice(text="Two", question_id=q.id),
        Choice(text="Three", question_id=q.id),
        Choice(text="Four", question_id=q.id),
        Choice(text="Five", question_id=q.id),
    ]
    db.session.add_all(choices)
    db.session.commit()

    q = Question(
        text="What force pulls objects toward Earth?",
        correct_choice="A",
        category_id=science_id
    )
    db.session.add(q)
    db.session.commit()

    choices = [
        Choice(text="Gravity", question_id=q.id),
        Choice(text="Magnetism", question_id=q.id),
        Choice(text="Friction", question_id=q.id),
        Choice(text="Electricity", question_id=q.id),
    ]
    db.session.add_all(choices)
    db.session.commit()

    q = Question(
        text="Which organ pumps blood through the body?",
        correct_choice="B",
        category_id=science_id
    )
    db.session.add(q)
    db.session.commit()

    choices = [
        Choice(text="Lungs", question_id=q.id),
        Choice(text="Heart", question_id=q.id),
        Choice(text="Brain", question_id=q.id),
        Choice(text="Kidneys", question_id=q.id),
    ]
    db.session.add_all(choices)
    db.session.commit()

    q = Question(
        text="What is H2O commonly known as?",
        correct_choice="C",
        category_id=science_id
    )
    db.session.add(q)
    db.session.commit()

    choices = [
        Choice(text="Salt", question_id=q.id),
        Choice(text="Oxygen", question_id=q.id),
        Choice(text="Water", question_id=q.id),
        Choice(text="Hydrogen", question_id=q.id),
    ]
    db.session.add_all(choices)
    db.session.commit()

    q = Question(
        text="What gas do humans need to breathe?",
        correct_choice="D",
        category_id=science_id
    )
    db.session.add(q)
    db.session.commit()

    choices = [
        Choice(text="Carbon dioxide", question_id=q.id),
        Choice(text="Nitrogen", question_id=q.id),
        Choice(text="Helium", question_id=q.id),
        Choice(text="Oxygen", question_id=q.id),
    ]
    db.session.add_all(choices)
    db.session.commit()

    q = Question(
        text="Which part of the body helps you think?",
        correct_choice="A",
        category_id=science_id
    )
    db.session.add(q)
    db.session.commit()

    choices = [
        Choice(text="Brain", question_id=q.id),
        Choice(text="Heart", question_id=q.id),
        Choice(text="Liver", question_id=q.id),
        Choice(text="Muscles", question_id=q.id),
    ]
    db.session.add_all(choices)
    db.session.commit()

    q = Question(
        text="What star is at the center of our solar system?",
        correct_choice="B",
        category_id=science_id
    )
    db.session.add(q)
    db.session.commit()

    choices = [
        Choice(text="Polaris", question_id=q.id),
        Choice(text="The Sun", question_id=q.id),
        Choice(text="The Moon", question_id=q.id),
        Choice(text="Alpha Centauri", question_id=q.id),
    ]
    db.session.add_all(choices)
    db.session.commit()

# ================= GEOGRAPHY  =================

    q = Question(
        text="What is the largest continent on Earth?",
        correct_choice="C",
        category_id=geography_id
    )
    db.session.add(q)
    db.session.commit()

    choices = [
        Choice(text="Africa", question_id=q.id),
        Choice(text="Europe", question_id=q.id),
        Choice(text="Asia", question_id=q.id),
        Choice(text="Antarctica", question_id=q.id),
    ]
    db.session.add_all(choices)
    db.session.commit()

    q = Question(
        text="Which ocean is the largest?",
        correct_choice="A",
        category_id=geography_id
    )
    db.session.add(q)
    db.session.commit()

    choices = [
        Choice(text="Pacific Ocean", question_id=q.id),
        Choice(text="Atlantic Ocean", question_id=q.id),
        Choice(text="Indian Ocean", question_id=q.id),
        Choice(text="Arctic Ocean", question_id=q.id),
    ]
    db.session.add_all(choices)
    db.session.commit()

    q = Question(
        text="What country has the largest population?",
        correct_choice="D",
        category_id=geography_id
    )
    db.session.add(q)
    db.session.commit()

    choices = [
        Choice(text="United States", question_id=q.id),
        Choice(text="India", question_id=q.id),
        Choice(text="Russia", question_id=q.id),
        Choice(text="China", question_id=q.id),
    ]
    db.session.add_all(choices)
    db.session.commit()

    q = Question(
        text="What is the capital of France?",
        correct_choice="B",
        category_id=geography_id
    )
    db.session.add(q)
    db.session.commit()

    choices = [
        Choice(text="London", question_id=q.id),
        Choice(text="Paris", question_id=q.id),
        Choice(text="Rome", question_id=q.id),
        Choice(text="Berlin", question_id=q.id),
    ]
    db.session.add_all(choices)
    db.session.commit()

    q = Question(
        text="Which desert is the largest hot desert in the world?",
        correct_choice="C",
        category_id=geography_id
    )
    db.session.add(q)
    db.session.commit()

    choices = [
        Choice(text="Gobi Desert", question_id=q.id),
        Choice(text="Kalahari Desert", question_id=q.id),
        Choice(text="Sahara Desert", question_id=q.id),
        Choice(text="Mojave Desert", question_id=q.id),
    ]
    db.session.add_all(choices)
    db.session.commit()

    q = Question(
        text="Which country is known as the Land of the Rising Sun?",
        correct_choice="A",
        category_id=geography_id
    )
    db.session.add(q)
    db.session.commit()

    choices = [
        Choice(text="Japan", question_id=q.id),
        Choice(text="China", question_id=q.id),
        Choice(text="Thailand", question_id=q.id),
        Choice(text="South Korea", question_id=q.id),
    ]
    db.session.add_all(choices)
    db.session.commit()

    q = Question(
        text="Which continent is the smallest by land area?",
        correct_choice="D",
        category_id=geography_id
    )
    db.session.add(q)
    db.session.commit()

    choices = [
        Choice(text="Europe", question_id=q.id),
        Choice(text="South America", question_id=q.id),
        Choice(text="Antarctica", question_id=q.id),
        Choice(text="Australia", question_id=q.id),
    ]
    db.session.add_all(choices)
    db.session.commit()

    q = Question(
        text="Which river is the longest in the world?",
        correct_choice="B",
        category_id=geography_id
    )
    db.session.add(q)
    db.session.commit()

    choices = [
        Choice(text="Amazon River", question_id=q.id),
        Choice(text="Nile River", question_id=q.id),
        Choice(text="Yangtze River", question_id=q.id),
        Choice(text="Mississippi River", question_id=q.id),
    ]
    db.session.add_all(choices)
    db.session.commit()

    q = Question(
        text="Mount Everest is located in which mountain range?",
        correct_choice="C",
        category_id=geography_id
    )
    db.session.add(q)
    db.session.commit()

    choices = [
        Choice(text="Andes", question_id=q.id),
        Choice(text="Rocky Mountains", question_id=q.id),
        Choice(text="Himalayas", question_id=q.id),
        Choice(text="Alps", question_id=q.id),
    ]
    db.session.add_all(choices)
    db.session.commit()

    q = Question(
        text="Which country has the most time zones?",
        correct_choice="A",
        category_id=geography_id
    )
    db.session.add(q)
    db.session.commit()

    choices = [
        Choice(text="France", question_id=q.id),
        Choice(text="United States", question_id=q.id),
        Choice(text="Russia", question_id=q.id),
        Choice(text="China", question_id=q.id),
    ]
    db.session.add_all(choices)
    db.session.commit()

    q = Question(text="Which continent is India in?", correct_choice="C", category_id=geography_id)
    db.session.add(q); db.session.commit()
    db.session.add_all([
        Choice(text="North America", question_id=q.id),
        Choice(text="Europe", question_id=q.id),
        Choice(text="Asia", question_id=q.id),
        Choice(text="Africa", question_id=q.id),
    ]); db.session.commit()

    q = Question(text="Which ocean is on the west coast of the USA?", correct_choice="C", category_id=geography_id)
    db.session.add(q); db.session.commit()
    db.session.add_all([
        Choice(text="Atlantic", question_id=q.id),
        Choice(text="Indian", question_id=q.id),
        Choice(text="Pacific", question_id=q.id),
        Choice(text="Arctic", question_id=q.id),
    ]); db.session.commit()

    q = Question(text="What country is Madrid in?", correct_choice="A", category_id=geography_id)
    db.session.add(q); db.session.commit()
    db.session.add_all([
        Choice(text="Italy", question_id=q.id),
        Choice(text="France", question_id=q.id),
        Choice(text="Germany", question_id=q.id),
        Choice(text="Spain", question_id=q.id),
    ]); db.session.commit()

    q = Question(text="Which is the largest ocean?", correct_choice="A", category_id=geography_id)
    db.session.add(q); db.session.commit()
    db.session.add_all([
        Choice(text="Pacific", question_id=q.id),
        Choice(text="Atlantic", question_id=q.id),
        Choice(text="Indian", question_id=q.id),
        Choice(text="Arctic", question_id=q.id),
    ]); db.session.commit()

    q = Question(text="What country is south of the USA?", correct_choice="D", category_id=geography_id)
    db.session.add(q); db.session.commit()
    db.session.add_all([
        Choice(text="Canada", question_id=q.id),
        Choice(text="Brazil", question_id=q.id),
        Choice(text="Spain", question_id=q.id),
        Choice(text="Mexico", question_id=q.id),
    ]); db.session.commit()

    q = Question(text="Which continent is Australia in?", correct_choice="C", category_id=geography_id)
    db.session.add(q); db.session.commit()
    db.session.add_all([
        Choice(text="Europe", question_id=q.id),
        Choice(text="Asia", question_id=q.id),
        Choice(text="Australia", question_id=q.id),
        Choice(text="Africa", question_id=q.id),
    ]); db.session.commit()

    q = Question(text="What is the capital of Korea?", correct_choice="C", category_id=geography_id)
    db.session.add(q); db.session.commit()
    db.session.add_all([
        Choice(text="Beijing", question_id=q.id),
        Choice(text="Tokyo", question_id=q.id),
        Choice(text="Seoul", question_id=q.id),
        Choice(text="Kyoto", question_id=q.id),
    ]); db.session.commit()

    q = Question(text="Which continent is the coldest?", correct_choice="D", category_id=geography_id)
    db.session.add(q); db.session.commit()
    db.session.add_all([
        Choice(text="Asia", question_id=q.id),
        Choice(text="Europe", question_id=q.id),
        Choice(text="Africa", question_id=q.id),
        Choice(text="Antarctica", question_id=q.id),
    ]); db.session.commit()

    q = Question(text="Which country has the Great Wall?", correct_choice="A", category_id=geography_id)
    db.session.add(q); db.session.commit()
    db.session.add_all([
        Choice(text="China", question_id=q.id),
        Choice(text="Japan", question_id=q.id),
        Choice(text="India", question_id=q.id),
        Choice(text="Korea", question_id=q.id),
    ]); db.session.commit()

    q = Question(text="What direction does the sun rise from?", correct_choice="C", category_id=geography_id)
    db.session.add(q); db.session.commit()
    db.session.add_all([
        Choice(text="North", question_id=q.id),
        Choice(text="South", question_id=q.id),
        Choice(text="East", question_id=q.id),
        Choice(text="West", question_id=q.id),
    ]); db.session.commit()

